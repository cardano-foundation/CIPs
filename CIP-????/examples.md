# Light client intents — worked examples

Three use cases traced end to end: what the client writes, the constraint it
compiles to, the filter keys it routes under, the sub-transaction a service
returns, and the batch that carries it. Sizes and key sets are **measured**,
not estimated — `cargo test -p babel-intent --test examples -- --nocapture`
prints them, and that test is the source for every figure below.

Throughout, the client is a **C0** wallet: it holds keys and nothing else. No
node, no indexer, no account with a provider.

---

## 1. Babel fee — send a token, hold no ADA

Alice holds USDM and no ADA. She wants Bob to have 100 USDM.

### What she writes

```rust
IntentRequest::new(my_credentials, my_address, now)
    .paying(bob, usdm, 100_000_000)
    .spending_at_most(usdm, 120_000_000)   // 100 to Bob, at most 20 in fees
    .receiving_at_most_lovelace(3_000_000) // change is ADA she pays for
    .build()
```

Four lines. Everything else — the validity window, the output structure, and
the four allowlists that forbid certificates, withdrawals, minting and
voting — is applied by default and needs no mention.

### The constraint

**249 bytes, 6 bound entries, no gaps.**

| | |
|---|---|
| requirement | `PayTo { Address(bob), USDM, 100_000_000 }` |
| `net_change` | USDM `max 120_000_000`; lovelace `min −3_000_000` |
| `valid_within` | `[now, now + 10 min]` |
| `output_structure` | one output for Bob, exactly one carrying her change, and no others |
| restrictions | `CertificatesOnly {}`, `WithdrawalsOnly {}`, `MintOnly {}`, `VotesOnly {}` |

The USDM ceiling is the price protection: the sub-transaction may be out of
balance by at most 120 million USDM, which covers the 100 to Bob and caps the
service's cut at 20. The service takes no output here — it is paid by that
imbalance, out of its own sub-transaction. The lovelace floor is there because ADA
arriving in her change is ADA she is charged for in USDM — and
`output_structure` closes the set, so that change arrives as exactly one
output rather than six dust UTxOs with six min-UTxO floors she pays for.

### Filter keys

```
subtx/v1/mainnet/offered/<usdm policy>
subtx/v1/mainnet/dialect/<interpreter>
```

Two. A market maker in USDM subscribes to the first; every service subscribes
to the dialects it speaks.

### The sub-transaction a service returns

| | |
|---|---|
| spends | 2 of Alice's USDM UTxOs; 1 of the service's ADA UTxOs |
| outputs | exactly two: 100 USDM → Bob; 380 USDM + min-UTxO ADA → Alice |
| withdrawal | 0 from the interpreter's stake credential, redeemer = the constraint |
| validity | inside Alice's window |

Alice checks one thing: that the withdrawal runs an interpreter she knows,
over a datum byte-identical to the one she sent. She signs; the service
countersigns and returns the result.

### The batch

An ordinary CIP-0198 top-level transaction. Alice's sub-transaction goes into
field 23 verbatim, alongside whatever else the service is carrying. The guard
runs once, against her sub-transaction, when the batch validates.

---

## 2. DEX swap — pool identified by a beacon NFT

Alice swaps 100 USDM for at least 40 ADA, at a pool whose live state is marked
by a beacon token. The pool's script address holds many UTxOs; only the one
carrying the beacon is the pool.

### What she writes

```rust
// "I must net RECEIVE at least 40 ADA" is a NEGATIVE ceiling.
net_change { lovelace, min: -45_000_000, max: -40_000_000 }
net_change { usdm,     max: 100_000_000 }

requirement: All([
    Spends(Holding { asset: beacon, datum: None }),
    PayTo { to: pool_address, asset: usdm, amount: 100_000_000, datum },
])
```

### The constraint

**312 bytes, 6 bound entries, no gaps.** Two outputs: the pool, and her
change — the pool target read off the requirement tree.

The sign convention is the one thing here that needs care. Net change is the
sub-transaction's imbalance over every field that moves value —
`inputs + mint + withdrawals + refunds − outputs − deposits − donation` —
so:

| Written | Means |
|---|---|
| `max: 100_000_000` | part with at most 100 USDM |
| `max: −40_000_000` | **net receive at least 40 ADA** |
| `min: −45_000_000` | receive no more than 45 ADA — a cost ceiling, since supplied ADA is charged for |

Only the ceiling states a requirement. The floor permits, and that asymmetry
is what the filter keys read.

### Filter keys

```
subtx/v1/mainnet/offered/<usdm policy>
subtx/v1/mainnet/pays/<pool script>
subtx/v1/mainnet/holds/<beacon policy>
subtx/v1/mainnet/dialect/<interpreter>
```

Four. The pool's operator subscribes to `pays/` and `holds/` for its own
validator and beacon, which is the DApp-subsidy condition in full.

**Note what is absent**: no `needed/ada`. Lovelace yields no asset key by
design, since every intent moves it and a key on it would separate nothing. A
market maker buying USDM finds this intent on the `offered/` side instead.

### The sub-transaction

| | |
|---|---|
| spends | Alice's USDM UTxOs; **the pool UTxO holding the beacon**; the service's ADA |
| outputs | two: 100 USDM + the pool's datum → the pool, carrying the beacon back; ≥ 40 ADA → Alice |
| withdrawal | the interpreter, over Alice's constraint |

`Spends(Holding(beacon))` is the clause that makes this a pool interaction
rather than a payment that happens to land at a script address. It is also
the clause a batcher **cannot build toward** — adding an input needs that
input's witness — so a service either already has the pool in the batch or
the intent is unsatisfiable.

### The batch

The pool's own sub-transaction and Alice's are both in field 23. Her guard
sees only hers; the pool's validator sees the whole spend of its UTxO, as
usual.

---

## 3. DApp-sponsored mint — the client pays nothing

Acme runs a DApp and mints a membership NFT for new users, free. Alice holds
no ADA and no tokens at all.

### What she writes

```rust
IntentRequest::new(my_credentials, my_address, now)
    .spending_at_most(lovelace, 0)        // I part with nothing
    .minting({ pass_nft: 1 })             // exactly this, and nothing else
    .build()
// requirement: Spends(At { place: Credential(acme_script), holding: None })
```

### The constraint

**200 bytes, 5 bound entries, one gap.** The smallest of the three, because a
client that parts with nothing needs only one net-change bound. One output:
her change, carrying the NFT.

`spending_at_most(lovelace, 0)` is the sponsorship statement: the
sub-transaction's ADA imbalance must be at most zero, so it cannot take ADA
out of her — any ADA it needs, Acme supplies. `MintOnly` names the one NFT
and its quantity exactly, so no second token rides along; had she not called
`minting`, minting would have been forbidden entirely, which is the default.

`audit` reports one gap here, `ServiceUnpaid`: no asset's `net_change`
ceiling is above zero and nothing is paid to anyone, so there is no money in
this intent for a service. That is correct and expected — Acme fills it
under the [DApp subsidy](./README.md#other-payment-options), for a reason
that is nowhere in the constraint. Worth surfacing all the same, because the
same report on example 1 would mean nobody will ever answer.

### Filter keys

```
subtx/v1/mainnet/invokes/<acme validator>
subtx/v1/mainnet/dialect/<interpreter>
```

Two, and the first is exactly what Acme subscribes to. `invokes/` rather than
`pays/` because spending from a script runs it — and the key comes off the
credential selector directly, with no address in between to go stale.

### The sub-transaction

Acme supplies every input, pays the fee, mints the NFT to Alice, and takes
nothing. Alice signs because her credentials appear nowhere — which is worth
noticing: she signs an empty authorisation, and the guard still protects her,
because the constraint forbids everything she did not ask for.

---

## 4. The same babel fee, as a top-level transaction

Alice's intent from example 1, unchanged, with `top_level` set on the
message. Nothing about the constraint differs — what differs is that none
of it goes on-chain.

### What she writes

Identical to example 1, plus one field on the intent message:

```rust
Intent { top_level: true, .. }
```

### The constraint

**249 bytes, 6 bound entries, no gaps** — and **0 bytes on-chain.** The
service builds a complete transaction, Alice checks it herself, and no
interpreter runs: the guard exists to bind what a batcher adds, and there
is no batch.

| | |
|---|---|
| on-chain datum | none |
| interpreter | none runs |
| what Alice checks | the whole transaction, against the 249-byte constraint she kept |
| what she still cannot resolve | the inputs — the service's word, as ever |

### What it costs

The batch. A top-level transaction pays its whole fee rather than a share
of one, and cannot be combined with other clients' work, so it is worth
less to a service and will be priced accordingly. For a client making one
payment and holding no ada, that may still be the better trade: it pays
one fee instead of a fee share plus ~249 B of datum plus the interpreter's
execution units, and it gets a transaction it can read end to end.

The comparison is not datum-against-datum but **fee-share-plus-guard
against whole-fee**, and which wins depends on how full the batch would
have been.

## Do these look OK?

### Size — and what the guard datum costs

Each figure below is the constraint as it would ride on-chain, measured.

| Example | Datum | Bound entries | Outputs |
|---|---|---|---|
| 1. Babel fee | 249 B | 6 | 2 |
| 2. DEX swap | 312 B | 6 | 2 |
| 3. Sponsored mint | 200 B | 5 | 1 |

Against a 16 KB `maxTxSize`, one intent's datum is **2–2.5%**. At
`minFeeA = 44` lovelace/byte that is roughly **0.018 ADA** of fee per intent,
which nobody will notice.

The batch is where it adds up. **Ten intents in one batch is ~2.5 KB of guard
datums — about a seventh of the transaction**, before any sub-transaction
bodies.

#### With and without the guard datum

In the plaintext exchange the guard is
[optional](./README.md#constraint-language-extensions): the
client has already checked the body it is about to sign. Dropping it removes
the datum, the zero-withdrawal that invokes the interpreter, its redeemer,
and the interpreter's execution units.

Four options, not two. The middle two publish only the [chain
checks](./README.md#the-chain-checks-dialect) — the clauses the client
could not settle from the body — either in the full language, or in the
chain-checks dialect under its own smaller interpreter.

| | Whole constraint | Chain checks, full language | Chain-checks dialect | No guard |
|---|---|---|---|---|
| 1. Babel fee | 249 B | 92 B | **74 B** | 0 |
| 2. DEX swap | 312 B | 141 B | **123 B** | 0 |
| 3. Sponsored mint | 200 B | 81 B | **63 B** | 0 |
| Ten mixed intents | ~2.5 KB | ~1.0 KB | ~0.9 KB | 0 |
| Plus, per intent | ~35 B of withdrawal and redeemer | the same | the same | none |
| Interpreter | 453 lines, 6 bound entries | the same script | **116 lines, 3 flat lists** | none |

Two different savings, and it is worth not confusing them. **Dropping to the
chain checks saves datum**: about two-thirds, measured. **Dropping to the
dialect saves execution**: another 17 bytes, which is minor, but it runs a
script a quarter the size with no recursion at all — three folds over three
flat lists, instead of a walk of the outputs plus the certificate list, the
mint map, the withdrawals, the votes, an interval comparison and a
requirement tree.

Per-intent execution units are what decide how many intents fit in a batch,
so for a service that is the column that matters. The datum columns are
measured and the line counts are real; the ~35 B is the withdrawal entry (a
29-byte reward account and a coin) plus its redeemer pointer, and the actual
ExUnits need the Aiken compiled.

What stays on-chain in either middle column is exactly the part a C0 client
would otherwise be taking on the service's word: the value ceiling and any
named input.

What each option costs a C0 client in trust is set out under [the checker's
limits](#what-local-checking-cannot-decide) below.

Carrying the whole constraint, a service batching light-client work hits the
size ceiling on datums well before it runs out of room for transactions.
One thing would help if that bites: the four restrictions are empty lists
that could be one bitmask. Neither is worth optimising until
there is a real batch to measure — and publishing the chain checks instead
saves more than either.

### Complexity — good, and the defaults carry it

Three or four builder calls per example. The client states what it wants and
what it will pay; the protective bounds arrive without being asked for, and
`audit` reports nothing on the two intents that pay for themselves.

That is the part that matters, because the alternative was a client
remembering six clauses. The one thing it still has to get right is the
**sign convention on `net_change`**, and example 2 shows why: "receive at
least 40 ADA" is a negative *ceiling*, not a floor. I got that backwards when
writing this file, and the same error was in the filter-key derivation until
these examples caught it. If anything here needs a better interface, it is
that — `receiving_at_least(asset, n)` as a builder method would remove the
only genuine footgun left.

A second, smaller one: `.paying()` takes no datum, so example 2's payment
into the pool — which must carry the pool's new state — is written by hand.
`.paying(address, asset, amount).with_datum(d)` would close it. Not a
selector: a payment CREATES an output, and an output needs a full address,
payment and staking parts both, which a credential does not supply. That
asymmetry with `Spends` is deliberate.

### Coverage — what a signature can authorise, and what bounds it

Worth stating plainly, since the client's whole protection is that the list
is complete:

| A sub-tx may | Bounded by |
|---|---|
| spend the client's UTxOs | `net_change` — the value is capped, and consolidating dust is not harm |
| create outputs | `output_structure`: one per `PayTo`, exactly one change, no others |
| mint or burn | `MintOnly`, exactly |
| post certificates | `CertificatesOnly`, exactly |
| withdraw rewards | `WithdrawalsOnly`, and the amount is in `net_change` |
| donate to the treasury | `net_change` |
| lock a deposit | `net_change` |
| land whenever | `valid_within` |
| move the client's stake | `output_structure` — every output sits at an address the client wrote whole |
| cast a governance vote | `VotesOnly` — the only one no value bound can see |

Inputs are the one field left open, deliberately: adding one needs its
witness, and whatever it brings in is already counted by `net_change`.

### Expressiveness — covers these three with nothing missing

All three compile with no gaps and no clause left unexpressible. The
selector earns its place twice over: `Holding(beacon)` in example 2 names a
UTxO no address could — the pool's script address holds many, and only the
one carrying the beacon is the pool — and `At(Credential(acme))` in example
3 names a DApp across every address it uses, which an exact address cannot.
Neither example needs it, but the two compose: `At { Credential(pool),
holding: beacon }` is "that pool's UTxO holding its beacon", which matters
once the token is fungible and so sits in more than one place.

Two limits worth stating, neither hit here:

- **`Spends` cannot be built toward.** A service either already has the named
  UTxO in the batch or declines. That is correct, but it means a client
  naming a busy pool competes for it, and the failure looks the same as
  disinterest.
- **No `needed/` key for ADA.** A market maker in ADA cannot subscribe to the
  buy side of an ADA swap. Example 2 routes on `offered/USDM` instead, which
  works, but a service that only ever buys ADA for tokens has nothing to
  subscribe to.

### What local checking cannot decide

A client checking the body itself replaces the guard only as far as it can
actually decide the clauses. Two things do not come out of the body:

| | Needs | A C0 client |
|---|---|---|
| `net_change` | the value of every input | must take them from the service — and a service that understates one makes the check pass when it should fail |
| `Spends` | the address of every input | the same |
| `Guards` | the finished witness set | does not exist yet when the client checks |
| `valid_within` | slot-to-time conversion | has it: two network constants and a clock |
| `CertificatesOnly`, `WithdrawalsOnly`, `VotesOnly` | the accounts, certificates and voters named | provable when the field is ABSENT, which is the default case; otherwise reported unchecked |
| everything else | the body alone | decidable |

So the honest rule is: **the guard may be dropped in plaintext by a client
that can resolve the sub-transaction's inputs** — C2 always, C1 for its own —
**or by one willing to take the service's word for their values.** For a C0
client that trusts nothing, the guard is what resolves inputs on its behalf,
and it stays.

Which is why a middle option usually wins: a C0 client publishes the [chain
checks](./README.md#the-chain-checks-dialect) — exactly these three
clauses — checks the rest itself, and pays a third of the bytes without
trusting the service for anything.

`babel_intent::verify` reports a clause it cannot decide in `unchecked`
rather than passing it, and `is_satisfied()` demands that list be empty.
That is deliberate: a clause nobody checked is not a clause that held, and
reporting protection the client does not have is the one failure it cannot
detect for itself.

### What these examples do not test

ExUnits. Every figure above is bytes, and the cost that will actually decide
whether a batch is viable is what the interpreter costs to run per intent —
six bound entries, each a pass over inputs, outputs or another body
field. That needs the Aiken compiled, which it is not. Until then the `MAX_BOUND_ENTRIES = 64` and
`MAX_BOUND_LIST_LENGTH = 32` caps are guesses sized for off-chain DoS,
not for an execution budget, and I would expect both to come down.
