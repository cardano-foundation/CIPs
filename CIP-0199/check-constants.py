#!/usr/bin/env python3
"""Verify the Poseidon constants and test vectors shipped with this CIP.

Two independent kinds of checks, both runnable with a bare python3 (no
dependencies):

1. Constant properties required by the Poseidon paper [GKRRS21]
   (https://eprint.iacr.org/2019/458), the same properties cardano-base's
   test suite asserts over its registered constants:
     - every constant is a canonical field element in [0, r);
     - the round constants are pairwise distinct and nonzero;
     - gcd(alpha, r-1) = 1, so x -> x^alpha is a bijection;
     - the matrix is genuinely MDS: every square minor is nonzero
       ([GKRRS21] footnote 7) — which also implies invertibility;
     - no infinitely long subspace trail can keep the partial-round S-box
       inactive ([GKRRS21] section 2.3; Grassi/Rechberger/Schofnegger,
       eprint 2020/500): the largest M-invariant subspace contained in the
       hyperplane { x : x_sboxlane = 0 } must be trivial, which holds iff
       the matrix with rows e_l M^j (j = 0..t-1, l the S-box lane) has full
       rank t.

   The stronger condition sometimes checked instead — no power M^i has any
   eigenvalue in F_r at all — is sufficient but NOT necessary, and it does
   not hold for deployed t = 3 instances (the midnight-zk and circom
   BLS12-381 MDS matrices both have eigenvalues in F_r); the eigenvalue
   scan below is therefore reported as information, not as a failure.

2. Known-answer vectors, one file per instance, all re-derived here:
     - the NORMATIVE 'permutation' vectors — one call of the built-in,
       (input state -> full output state) — computed from each instance
       file's constants under its declared partial_sbox_lane, mds
       orientation and round order: these pin the built-in exactly;
     - the secondary 'hash' vectors — the instance ecosystem's hash —
       re-derived by a generic pure-integer sponge driven ENTIRELY by the
       "framing" block encoded in the constants file (rate, capacity lane,
       capacity initialization, accepted arities, digest lane), proving
       the encoded framing is complete enough to define the hash;
     - where an instance ships a conjugated_form (for permutation cores
       hard-coding the partial S-box on the last lane), the exact
       state-reversal conjugation identity is asserted;
     - the midnight permutation vector is additionally checked through
       both the classic ARC->S-box->Mix schedule and midnight's shifted
       schedule, asserting their observational equivalence.

Exit status 0 and a final ALL CHECKS PASSED line on success.
"""
import json
import os
import sys
from itertools import combinations
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 5

failures = []


def check(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        failures.append(name)


# ----------------------------------------------------------------------
# Field / matrix helpers (all arithmetic mod r)
# ----------------------------------------------------------------------

def minor_det(M, rows, cols, r):
    """Determinant of the submatrix M[rows][cols] via Laplace expansion
    (matrices here are at most 4x4)."""
    if len(rows) == 1:
        return M[rows[0]][cols[0]] % r
    total = 0
    for k, row in enumerate(rows):
        d = minor_det(M, rows[:k] + rows[k + 1:], cols[1:], r)
        total += (-1) ** k * M[row][cols[0]] * d
    return total % r


def is_mds(M, r):
    """Every square minor nonzero ([GKRRS21] footnote 7)."""
    t = len(M)
    for k in range(1, t + 1):
        for rows in combinations(range(t), k):
            for cols in combinations(range(t), k):
                if minor_det(M, list(rows), list(cols), r) == 0:
                    return False
    return True


def mat_mul(A, B, r):
    t = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(t)) % r for j in range(t)]
            for i in range(t)]


def char_poly(M, r):
    """Characteristic polynomial coefficients (monic, ascending order) via
    the Faddeev–LeVerrier algorithm mod the prime r."""
    t = len(M)
    I = [[1 if i == j else 0 for j in range(t)] for i in range(t)]
    coeffs = [0] * t + [1]  # x^t coefficient
    N = [row[:] for row in I]
    MN = M
    for k in range(1, t + 1):
        MN = mat_mul(M, N, r)
        trace = sum(MN[i][i] for i in range(t)) % r
        c = (-trace * pow(k, r - 2, r)) % r
        coeffs[t - k] = c
        N = [[(MN[i][j] + (c if i == j else 0)) % r for j in range(t)]
             for i in range(t)]
    return coeffs


def poly_mod(a, f, r):
    """a mod f over F_r[x]; f monic. Coefficients ascending."""
    a = a[:]
    df = len(f) - 1
    for i in range(len(a) - 1, df - 1, -1):
        c = a[i] % r
        if c:
            for j in range(df + 1):
                a[i - df + j] = (a[i - df + j] - c * f[j]) % r
        a[i] = 0
    return a[:df]


def poly_mul_mod(a, b, f, r):
    prod = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                prod[i + j] = (prod[i + j] + x * y) % r
    return poly_mod(prod, f, r)


def has_root_in_field(f, r):
    """f (monic, ascending coeffs) has a root in F_r iff
    gcd(x^r - x, f) is non-constant."""
    # x^r mod f by square-and-multiply
    result = [1] + [0] * (len(f) - 2)          # 1
    base = poly_mod([0, 1] + [0] * len(f), f, r)  # x mod f
    e = r
    while e:
        if e & 1:
            result = poly_mul_mod(result, base, f, r)
        base = poly_mul_mod(base, base, f, r)
        e >>= 1
    # x^r - x mod f
    g = result[:]
    if len(g) < 2:
        g += [0] * (2 - len(g))
    g[1] = (g[1] - 1) % r
    # gcd(g, f) over F_r[x]
    a, b = f[:], g
    while any(c % r for c in b):
        while b and b[-1] % r == 0:
            b.pop()
        lead_inv = pow(b[-1], r - 2, r)
        bm = [(c * lead_inv) % r for c in b]
        a = poly_mod(a + [0], bm, r) if len(a) >= len(bm) else a
        a, b = b, [c % r for c in a]
        while a and a[-1] % r == 0:
            a.pop()
        if not b or all(c % r == 0 for c in b):
            break
    while a and a[-1] % r == 0:
        a.pop()
    return len(a) > 1  # non-constant gcd => a root exists


def eigenvalue_powers(M, r, max_power):
    """Which powers M^i (1 <= i <= max_power) have an eigenvalue in F_r.
    Informational: an eigenvalue alone is not a defect (see module docs)."""
    hits = []
    P = M
    for i in range(1, max_power + 1):
        if i > 1:
            P = mat_mul(P, M, r)
        if has_root_in_field(char_poly(P, r), r):
            hits.append(i)
    return hits


def rank(M, r):
    """Rank of a matrix over F_r by Gaussian elimination."""
    A = [row[:] for row in M]
    rows, cols = len(A), len(A[0])
    rk = 0
    for c in range(cols):
        pivot = next((i for i in range(rk, rows) if A[i][c] % r), None)
        if pivot is None:
            continue
        A[rk], A[pivot] = A[pivot], A[rk]
        inv = pow(A[rk][c], r - 2, r)
        A[rk] = [(x * inv) % r for x in A[rk]]
        for i in range(rows):
            if i != rk and A[i][c] % r:
                f = A[i][c]
                A[i] = [(x - f * y) % r for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk


def sbox_lane_secure(M, r, lane):
    """True iff the only M-invariant subspace contained in
    { x : x_lane = 0 } is trivial — i.e. no infinitely long subspace trail
    keeps the partial-round S-box inactive. Holds iff the observability
    matrix with rows e_lane M^j (j = 0..t-1) has full rank t."""
    t = len(M)
    row = [1 if j == lane else 0 for j in range(t)]
    obs = []
    for _ in range(t):
        obs.append(row)
        row = [sum(row[k] * M[k][j] for k in range(t)) % r for j in range(t)]
    return rank(obs, r) == t


def check_instance(label, r, width, ark, mds, n_rounds, sbox_lane):
    check(f"{label}: round-constant count == (R_F+R_P)*t == {n_rounds * width}",
          len(ark) == n_rounds * width)
    check(f"{label}: MDS shape {width}x{width}",
          len(mds) == width and all(len(row) == width for row in mds))
    flat = ark + [x for row in mds for x in row]
    check(f"{label}: all constants canonical in [0, r)",
          all(0 <= x < r for x in flat))
    check(f"{label}: round constants pairwise distinct and nonzero",
          len(set(ark)) == len(ark) and 0 not in ark)
    check(f"{label}: matrix is MDS (every square minor nonzero)",
          is_mds(mds, r))
    lane = 0 if sbox_lane == "first" else width - 1
    check(f"{label}: no M-invariant subspace avoids the S-box lane "
          f"({sbox_lane})", sbox_lane_secure(mds, r, lane))
    hits = eigenvalue_powers(mds, r, 4 * width)
    print(f"info  {label}: powers M^i (i <= {4 * width}) with an eigenvalue "
          f"in F_r: {hits if hits else 'none'}")


# ----------------------------------------------------------------------
# Permutations, in each instance's own convention
# ----------------------------------------------------------------------

def midnight_permutation(state, ark, mds, rf, rp, r):
    """Shifted-round form used by midnight-zk (and cardano-base): initial
    ARC, then each round = S-box -> MDS -> add next round's constants (the
    final round adds nothing). Partial-round S-box on the LAST lane.
    Observationally identical to the ARC -> S-box -> Mix definition."""
    w = len(state)
    st = [(s + c) % r for s, c in zip(state, ark[0:w])]
    chunks = [ark[i * w:(i + 1) * w] for i in range(len(ark) // w)]
    later = chunks[1:] + [None]
    kinds = ["F"] * (rf // 2) + ["P"] * rp + ["F"] * (rf // 2)
    for kind, cs in zip(kinds, later):
        if kind == "F":
            st = [pow(x, ALPHA, r) for x in st]
        else:
            st = st[:-1] + [pow(st[-1], ALPHA, r)]
        st = [sum(mds[i][j] * st[j] for j in range(w)) % r for i in range(w)]
        if cs is not None:
            st = [(x + c) % r for x, c in zip(st, cs)]
    return st


def classic_permutation(state, C, M, rf, rp, r, sbox_lane):
    """Textbook round order: ARC -> S-box -> Mix, every round."""
    t = len(state)
    st = list(state)
    for rd in range(rf + rp):
        st = [(x + c) % r for x, c in zip(st, C[rd * t:(rd + 1) * t])]
        if rf // 2 <= rd < rf // 2 + rp:
            i = 0 if sbox_lane == "first" else t - 1
            st[i] = pow(st[i], ALPHA, r)
        else:
            st = [pow(x, ALPHA, r) for x in st]
        st = [sum(M[i][j] * st[j] for j in range(t)) % r for i in range(t)]
    return st


def entry_hash(message, width, C, M, rf, rp, r, sbox_lane, framing):
    """The ecosystem hash, driven entirely by the encoded framing block:
    initialize the capacity, absorb the message in rate-sized chunks (one
    permutation per chunk). Returns (digest, trace), where trace is the
    list of (permutation input state, permutation output state) pairs —
    i.e. exactly the sequence of built-in calls a script-level hash makes.
    The hash/permutation separation is deliberate: the permutation is the
    built-in, the hash is this construction around it."""
    t = width
    cap = 0 if framing["capacity_lane"] == "first" else t - 1
    rate_lanes = [i for i in range(t) if i != cap]
    if framing["rate"] != len(rate_lanes):
        raise ValueError("framing rate inconsistent with capacity size")
    n = len(message)
    aa = framing["accepted_arities"]
    if not (("min" in aa and n >= aa["min"]) or
            ("exact" in aa and n == aa["exact"])):
        raise ValueError(f"arity {n} not accepted by framing")
    init = n if framing["capacity_init"] == "arity" else framing["capacity_init"]
    st = [0] * t
    st[cap] = init % r
    trace = []
    for i in range(0, n, framing["rate"]):
        for lane, x in zip(rate_lanes, message[i:i + framing["rate"]]):
            st[lane] = (st[lane] + x) % r
        inp = list(st)
        st = classic_permutation(st, C, M, rf, rp, r, sbox_lane)
        trace.append((inp, list(st)))
    return st[framing["digest_lane"]], trace


INSTANCES = [
    ("midnight width-3", "midnight-poseidon-constants.json", "midnight_width3"),
    ("circom-bls t=3", "circom-bls-t3-poseidon-constants.json", "circom_bls_t3"),
    ("circom-bls t=4", "circom-bls-t4-poseidon-constants.json", "circom_bls_t4"),
]


def main():
    vec = json.load(open(os.path.join(HERE, "test-vectors.json")))
    insts = [(label, json.load(open(os.path.join(HERE, fn))), vec[vkey])
             for label, fn, vkey in INSTANCES]

    r = insts[0][1]["field_modulus_r"]
    check("field moduli agree across constants files",
          all(d["field_modulus_r"] == r for _, d, _ in insts))
    check(f"gcd(alpha={ALPHA}, r-1) == 1 (S-box is a bijection)",
          gcd(ALPHA, r - 1) == 1)

    for label, d, v in insts:
        rf, rp = d["nbFullRounds"], d["nbPartialRounds"]

        # --- constant properties ---------------------------------------
        check_instance(label, r, d["width"], d["ark"], d["mds"], rf + rp,
                       d["partial_sbox_lane"])
        conj = d.get("conjugated_form")
        if conj:
            check_instance(f"{label} (conjugated form)", r, d["width"],
                           conj["ark"], conj["mds"], rf + rp,
                           conj["partial_sbox_lane"])

        # --- normative built-in vector: one permutation call ------------
        perm_in = v["permutation"]["input_state"]
        out = classic_permutation(perm_in, d["ark"], d["mds"], rf, rp, r,
                                  d["partial_sbox_lane"])
        check(f"{label}: permutation({perm_in}) matches test vector",
              out == v["permutation"]["output_state"])
        if conj:
            out2 = classic_permutation(list(reversed(perm_in)),
                                       conj["ark"], conj["mds"], rf, rp, r,
                                       conj["partial_sbox_lane"])
            check(f"{label}: conjugated form is the exact state reversal",
                  out2 == list(reversed(out)))

        # --- secondary vectors: the ecosystem hash, from the framing ----
        # (each vector carries the full permutation-call trace, so the
        # hash construction — not just the digest — is pinned)
        for hv in v["hashes"]["vectors"]:
            digest, trace = entry_hash(hv["message"], d["width"], d["ark"],
                                       d["mds"], rf, rp, r,
                                       d["partial_sbox_lane"], d["framing"])
            expected = [(s["permutation_input_state"],
                         s["permutation_output_state"]) for s in hv["trace"]]
            check(f"{label}: hash{hv['message']} full permutation-call trace"
                  f" re-derived from encoded framing",
                  trace == expected and digest == hv["digest"])

    # the midnight constants are consumed by a shifted-schedule
    # implementation upstream; assert schedule equivalence on its vector
    label, mid, mv = insts[0]
    perm_in = mv["permutation"]["input_state"]
    check("midnight: shifted and classic round schedules agree",
          midnight_permutation(perm_in, mid["ark"], mid["mds"],
                               mid["nbFullRounds"], mid["nbPartialRounds"], r)
          == classic_permutation(perm_in, mid["ark"], mid["mds"],
                                 mid["nbFullRounds"], mid["nbPartialRounds"],
                                 r, mid["partial_sbox_lane"]))

    print()
    if failures:
        print(f"{len(failures)} CHECK(S) FAILED")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
