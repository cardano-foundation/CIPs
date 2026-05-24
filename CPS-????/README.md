---
CPS: "????"
Title: Private Voting for DReps
Category: Ledger
Status: Open
Authors:
  - Thomas Lindseth <thomas.lindseth@intersectmbo.org>
Proposed Solutions: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1201
Created: 2026-05-23
License: CC-BY-4.0
---

## Abstract

CIP-1694 introduced on-chain governance for Cardano, including a system of Delegated
Representatives (DReps) who vote on governance actions on behalf of ADA holders. Under
the current design, all DRep votes are recorded in plaintext on the public ledger the
moment the voting transaction is confirmed. While transparency is a legitimate governance
value, unrestricted real-time public visibility of individual vote directions creates
concrete vectors for coercion, herding, and cartel coordination that undermine the
quality and independence of governance decisions. This CPS defines the problem,
identifies the parties affected, describes the trade-offs that any solution must navigate,
and lists the open questions that a satisfactory proposal must answer.

---

## Problem

### All DRep votes are immediately and permanently public

When a DRep submits a `VotingProcedure`, the ledger records their credential alongside
a plaintext `Yes`, `No`, or `Abstain` for each governance action. This is visible to
every node within seconds of the block being forged, and remains permanently queryable
on-chain and through governance explorers.

This design choice was intentional: voters should be accountable to their delegators.
However, full real-time transparency also means anyone — including large ADA holders,
organised blocs, or media — can observe, react to, and condition behaviour on any
DRep's vote while the voting period is still open.

### 2. Concrete failure modes that result

**Vote-buying and coercion.** An adversary can credibly offer a reward or threat
conditional on an observable on-chain outcome. Because the vote is immediately public
and the voting period can last several days, there is a large window during which a
DRep who has already voted can be identified, targeted, and pressured to submit a
cancellation and replacement vote. The current protocol explicitly allows vote revisions
within the voting window.

**Herding and last-mover advantage.** DReps who cast their votes late can trivially
observe how the vote is trending and vote with the apparent majority, regardless of
their independent assessment. This suppresses genuine deliberation and inflates the
appearance of consensus. The problem is especially acute for large DReps whose vote
is likely to be decisive.

**Cartel signalling.** A coalition of large DReps can publish their votes early as a
coordination signal, implicitly pressuring smaller DReps to follow. Deviating from
the coalition is observable and may carry reputational or financial cost.

**Chilling effect on minority positions.** DReps who hold well-reasoned but unpopular
views may self-censor in anticipation of retaliation, whether financial (redelegation)
or social (public criticism). The result is that the visible outcome of governance
may not reflect the true distribution of informed opinion in the DRep community.

### 3. The accountability tension

Solving the above problems by making votes fully private conflicts with a legitimate
governance requirement: delegators must be able to evaluate whether their DRep is
voting in ways they endorse, in order to make informed redelegation decisions. A DRep
whose individual vote is permanently hidden cannot be held accountable by the people
who delegated to them.

Any solution must navigate the tension between:
- **Vote secrecy** — hiding the vote direction from potential adversaries, and
- **Delegator accountability** — giving delegators verifiable information about how
  their representative voted.

These goals are not binary. A spectrum of designs exists between full public
transparency and full anonymity, and the right point on that spectrum is itself an
open question.

### 4. Constraint: the ledger records plaintext votes today

The Conway-era ledger encodes vote direction directly in the `VotingProcedure`
structure. Hiding the vote direction on-chain requires at minimum adding a new
optional field to that structure, which constitutes a hard fork. Solutions that do
not require any ledger change can only address a subset of the problem (e.g.
commitment-based anti-coercion proofs, or off-chain attestation standards) but
cannot achieve true on-chain vote secrecy. This trade-off must be acknowledged
and the scope of any proposal made explicit.

---

## Use Cases

### DRep votes independently under social pressure

A DRep has formed a view on a contentious treasury withdrawal proposal. A large ADA
holder who disagrees publicly announces they will immediately redelegate away from any
DRep who votes against the proposal. The DRep wishes to vote their conscience without
that vote being visible until a point at which redelegation can no longer affect the
outcome.

### UC-2: Delegator verifies how their DRep voted

An ADA holder has delegated to a DRep who promised to vote against increases to the
protocol treasury tax. After a governance action passes, the holder wants to verify
that their DRep voted as promised and, if not, to have evidence to support public
criticism or immediate redelegation.

### UC-3: DRep proves vote was not changed under pressure

A DRep faces accusations of changing their vote after being pressured by a large
whale. The DRep wants to demonstrate that their on-chain vote matches a commitment
they published before the whale's public statement.

### UC-4: Governance researcher analyses voting patterns

A researcher studying DRep voting coalitions wants to understand whether certain DReps
always vote together. Under full transparency, coalitions are trivially observable and
may become self-reinforcing. Under a privacy-preserving scheme, post-hoc statistical
analysis might still be possible from aggregate data, but real-time coalition
signalling would be disrupted.

### UC-5: Small DRep votes on a decisive action

A DRep holds just enough delegated stake that their vote is pivotal. Voting early
publicly may attract targeted pressure; voting late publicly enables strategic
free-riding. The DRep wants to cast a vote that takes effect at the close of the
voting window without revealing its direction beforehand.

---

## Goals

Goals are ranked by importance. Non-goals are explicitly listed to bound scope.

### G1 — Prevent coercion and vote-buying during the voting window (highest priority)

A solution should make it infeasible for an adversary to observe, and condition
behaviour on, an individual DRep's vote while the voting period remains open.

### G2 — Preserve delegator accountability

Delegators should have access to verifiable information about how their DRep voted.
The mechanism may be direct (automatic disclosure) or voluntary (DRep-controlled
disclosure), but some credible accountability path must exist.

### G3 — Produce a publicly verifiable aggregate tally

The final outcome of a governance vote — the total Yes, No, and Abstain weight — must
be unambiguously verifiable by any observer. It must not be possible for a tally to
be fabricated or suppressed.

### G4 — Minimise implementation complexity and deployment risk

A solution should be achievable with the smallest feasible ledger or protocol change.
It should not introduce new trusted parties, new long-lived cryptographic key material,
or new failure modes that could block governance entirely (e.g. if a decryption
committee is unavailable).

### G5 — Be backward-compatible with existing DRep tooling

Existing wallets, governance explorers, and DRep registration tooling should continue
to function. A solution that requires every DRep to migrate to new credentials or
re-register would impose unjustified friction.

### Non-goals

- **Full anonymity of DRep identity.** It is acceptable and expected that the ledger
  records which DRep credential submitted a vote. Only the vote direction needs to
  be private.
- **Privacy for SPO or Constitutional Committee votes.** This CPS is scoped to DRep
  votes only. The same techniques may apply to other voter classes but that is outside
  this scope.
- **Preventing post-hoc aggregate analysis.** Once the tally is public, statistical
  inference about voting blocs is possible. This is acceptable.
- **Protecting DReps from all forms of social pressure.** Off-chain pressure (e.g.
  public lobbying, published statements) is outside the scope of any on-chain
  privacy mechanism.

---

## Open Questions

Solutions to this problem must address the following questions. Where trade-offs exist,
the proposal should state which side it favours and why.

**OQ-1: At what point does the vote direction become public (if ever)?**
Options include: never (only the tally is revealed); after the voting period closes;
immediately (no change from today). Each choice has different accountability and
coercion-resistance properties.

**OQ-2: Who or what performs decryption or tally aggregation?**
If votes are encrypted, something must decrypt or aggregate them. Candidates include:
the existing Constitutional Committee; a purpose-built threshold committee; a
Plutus script enforcing a commit-reveal rule; or the DReps themselves in a
coordinated reveal. Each option has different liveness and trust assumptions.

**OQ-3: What is the minimum ledger change required?**
Can a useful subset of the problem be solved with zero ledger changes (e.g. an
off-chain metadata standard)? What additional value is unlocked by adding a single
field to `VotingProcedure`? What is the full cost of a more invasive change?

**OQ-4: How does selective disclosure work for delegators?**
Should disclosure be automatic (all delegators see the vote, the public does not),
opt-in by delegators (they register a key), or opt-out by DReps (they choose not to
disclose)? How is a delegator's right to information balanced against the DRep's
need for coercion resistance?

**OQ-5: How is the validity of an encrypted or committed vote verified on-chain?**
Without knowing the vote direction, how can a validator confirm the submission is
well-formed (e.g. that the DRep did not encrypt an invalid value, or that the
commitment is binding)? Zero-knowledge proofs address this but add complexity;
trusted verification delegates the check to a committee.

**OQ-6: What happens if a decryption committee member is offline or malicious?**
Threshold schemes tolerate up to `n - t` failures. What is the liveness guarantee
under partial committee failure, and what is the fallback if quorum cannot be
reached before the governance deadline?

**OQ-7: Can a DRep prove coercion resistance without revealing their vote?**
Is it possible to prove that a vote was committed to before a specific event (e.g.
a public threat) without revealing the vote direction? A hash commitment achieves
this if the reveal is voluntary, but the DRep must later choose to open it.

**OQ-8: Is a purely off-chain standard sufficient for the core use case?**
A metadata-based commitment and attestation standard can provide anti-coercion
properties and delegator accountability without any ledger change. Is this sufficient
for the community's needs, or is true on-chain vote secrecy necessary?

---

## References

- [CIP-1694](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694) — A First Step Towards On-Chain Decentralized Governance
- [CIP-0119](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0119) — Governance Metadata - DReps
- [CIP-0100](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100) — Governance Metadata
- [CIP-9999](https://github.com/cardano-foundation/CIPs/tree/master/CIP-9999) — Cardano Problem Statement format
- Adida, B., et al. (2008). *Helios: Web-based Open-Audit Voting*. USENIX Security.
- Cortier, V., et al. (2021). *SoK: Verifiability Notions for E-Voting Protocols*. IEEE S&P.

---

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
