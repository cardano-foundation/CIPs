---
CIP: ?
Title: Variable Deposits as Pledge
Category: Ledger
Status: Proposed
Authors:
    - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1204
Created: 2026-05-31
License: CC-BY-4.0
---

## Abstract

Cardano currently treats stake pool pledge as a declared value rather than ADA that is directly locked as pledge. This creates operational confusion between "declared pledge" and "live pledge", requires a separate owner-stake satisfaction check, and allows mangled-address constructions where apparent pledge can be inflated through stake credential "frankenwallets". Meanwhile, dReps have only a flat registration deposit and no equivalent pledge primitive, limiting future designs that may want dReps to have visible skin in the game.

This CIP replaces declared stake pool pledge with actual locked ADA by making the pool pledge deposit variable and using that deposit as the pool's pledge. Instead of declaring pledge in pool parameters and then checking whether owner stake credentials collectively control enough delegated stake, a pool operator locks the intended pledge amount in the ledger deposit pot. The existing pool deposit parameter is renamed to `minPoolDeposit` and becomes the minimum allowed pool pledge deposit.

The same mechanism is introduced for dReps. The existing dRep deposit parameter is renamed to `minDrepDeposit` and becomes the minimum allowed dRep pledge deposit. A dRep may lock any amount at or above that minimum as dRep pledge. This CIP does not change dRep voting power formulas or define a dRep compensation scheme. It creates a simple, queryable, on-chain pledge primitive that future CIPs may use for dRep incentives, compensation eligibility, concentration mitigation, etc.

Pledged stake remains economically active. Pool pledge deposits continue to earn staking rewards through the pool they pledge to and continue to count toward the dRep chosen by the pool operator's voting delegation. dRep pledge deposits continue to count toward that dRep's voting power and continue to earn staking rewards through the stake pool chosen by the dRep.

## Motivation: why is this CIP necessary?

### Current pool pledge is declared, not locked

Stake pool pledge is currently a value declared in pool registration parameters. At reward calculation time, the ledger checks whether the pool owners collectively control enough stake to satisfy the declared pledge. If the pledge is met, the declared pledge value is used in the reward calculation. If it is not met, the pool receives no rewards for that epoch.

This mechanism has two drawbacks.

First, pledge is operationally more complex than it needs to be. A pool operator declares a value, ensures enough stake is delegated through pool owner stake credentials, and relies on ledger accounting to classify that stake as owner stake. The deposit required to register the pool is a separate fixed value and does not itself represent the pool's pledge. This also creates common confusion between declared pledge and live pledge.

Second, declared pledge is vulnerable to confusing address constructions. CIP-0019 describes Shelley addresses as having a payment part and a delegation part. These parts are usually controlled by the same party, but can be controlled separately in "mangled addresses" or "hybrid addresses". Since current pledge satisfaction follows stake credentials, not payment credentials, ADA controlled by one party's payment credential may still count as another party's pool owner stake if the address uses that pool owner's stake credential. This does not create stake from nowhere and does not double-count stake, but it can inflate apparent pledge without requiring the pool operator to actually lock the claimed amount.

### Deposits already express locked ADA

The ledger already tracks deposits for stake credentials, stake pools, dReps, and governance actions. Deposits are returned only through the relevant deregistration, retirement, or finalization path. This CIP uses that existing accounting concept for pledge: a pool's pledge is the ADA locked under its pool pledge deposit, and a dRep's pledge is the ADA locked under its dRep pledge deposit.

This makes pledge easier to explain and reason about:

- A pool pledges 100,000 ADA by locking 100,000 ADA as its pool pledge deposit.
- A dRep pledges 10,000 ADA by locking 10,000 ADA as its dRep pledge deposit.
- The `minPoolDeposit` and `minDrepDeposit` protocol parameters define the minimum allowed pledge for each role.
- Reducing a pledge below the applicable minimum is rejected. Retrieving the final minimum deposit requires pool retirement or dRep deregistration.

## Specification

### Terminology

- `minPoolDeposit`: the renamed protocol parameter replacing `poolDeposit`. It defines the minimum allowed pool pledge deposit.
- `minDrepDeposit`: the renamed protocol parameter replacing `drepDeposit`. It defines the minimum allowed dRep pledge deposit.
- `poolPledgeDeposit`: the amount of ADA locked for a particular stake pool.
- `drepPledgeDeposit`: the amount of ADA locked for a particular dRep.
- `pledged stake`: ADA locked as a pool or dRep pledge deposit and included in stake and governance accounting according to the rules in this CIP.
- `pledge owner credential`: the stake credential or reward account associated with a pledge deposit for reward and voting-power accounting.

### Protocol parameter migration

This CIP renames the existing deposit protocol parameters:

- `poolDeposit` becomes `minPoolDeposit`.
- `drepDeposit` becomes `minDrepDeposit`.

Their meanings change as follows:

- `minPoolDeposit`: minimum allowed `poolPledgeDeposit`.
- `minDrepDeposit`: minimum allowed `drepPledgeDeposit`.

These parameters no longer define fixed registration deposits. They define the minimum amount of ADA that must remain locked for the corresponding role while that role is registered.

Changing either parameter by governance changes the minimum required pledge for future registration and update certificates. Existing registered pools and dReps with deposits below a newly increased minimum SHOULD remain valid until their next registration update, unless a future hard fork explicitly defines a migration rule that requires top-ups.

### Stake pool registration and updates

Stake pool registration and update certificates MUST include an explicit `poolPledgeDeposit` amount and a pledge owner credential.

For a newly registered pool:

- The transaction MUST lock a `poolPledgeDeposit` for the pool.
- `poolPledgeDeposit` MUST be greater than or equal to `pp.minPoolDeposit`.
- `poolPledgeDeposit` is recorded in the ledger's deposit accounting under the pool's `PoolDeposit` deposit purpose.
- `poolPledgeDeposit` is the pool's pledge.
- The pledge owner credential identifies the reward account that receives staking rewards attributable to this pledged ADA and whose voting delegation determines the dRep voting power for this pledged ADA.

For an already registered pool:

- Submitting a pool update certificate MUST NOT require pool retirement or deregistration.
- The update certificate MAY change `poolPledgeDeposit`.
- If the new `poolPledgeDeposit` is greater than the existing `poolPledgeDeposit`, the transaction MUST pay and lock the difference.
- If the new `poolPledgeDeposit` is less than the existing `poolPledgeDeposit`, the transaction MUST refund the difference.
- An update that sets `poolPledgeDeposit` below `pp.minPoolDeposit` MUST be rejected.

The pool parameter field for declared pledge is removed. Pledge is no longer read from pool parameters. The sole source of pool pledge is `poolPledgeDeposit` recorded in ledger deposit accounting.

For transition compatibility, an implementation era MAY retain, deprecate, or ignore the existing serialized declared pledge field before removing it completely. Regardless of the transition encoding, ledger semantics after activation MUST treat `poolPledgeDeposit` as the sole source of pool pledge.

### Pool pledge rewards and voting power

A `poolPledgeDeposit` is pledged stake.

For stake-pool accounting:

- `poolPledgeDeposit` MUST count as stake delegated to the pool that the pledge deposit applies to.
- This pledged stake therefore contributes to the pool's active stake and staking rewards.
- Staking rewards attributable to the deposit are credited to the pledge owner credential's reward account.

For governance accounting:

- `poolPledgeDeposit` MUST count toward the dRep voting delegation chosen by the pledge owner credential.
- A pool operator may therefore pledge ADA to a pool while still delegating the governance voting power of that pledged ADA to the dRep they choose.

The stake pool reward calculation continues to use a pledge value, but the pledge value MUST be read from the pool's effective `poolPledgeDeposit`.

The current owner-stake pledge satisfaction check is removed. In the current ledger, pool rewards depend on checking whether declared pledge is less than or equal to owner stake. Under this CIP, that check is no longer necessary because the pledge amount has already been locked. A pool's pledge is met by construction.

Any reward formula that currently takes pool pledge as an input, including future formulas such as pledge leverage-based reward schemes, SHOULD treat the effective `poolPledgeDeposit` as the pledge input.

### dRep registration and updates

dRep registration and update certificates MUST include an explicit `drepPledgeDeposit` amount and a pledge owner credential.

For a newly registered dRep:

- The transaction MUST lock a `drepPledgeDeposit` for the dRep.
- `drepPledgeDeposit` MUST be greater than or equal to `pp.minDrepDeposit`.
- `drepPledgeDeposit` is recorded in the ledger's deposit accounting under the dRep pledge deposit purpose.
- `drepPledgeDeposit` is the dRep's pledge.
- The pledge owner credential identifies the reward account whose stake-pool delegation determines staking rewards for this pledged ADA.

For an already registered dRep:

- Submitting a dRep update certificate MUST NOT require dRep deregistration.
- The update certificate MAY change `drepPledgeDeposit`.
- If the new `drepPledgeDeposit` is greater than the existing `drepPledgeDeposit`, the transaction MUST pay and lock the difference.
- If the new `drepPledgeDeposit` is less than the existing `drepPledgeDeposit`, the transaction MUST refund the difference.
- An update that sets `drepPledgeDeposit` below `pp.minDrepDeposit` MUST be rejected.

Implementations MAY satisfy this requirement by extending the existing dRep update certificate to carry pledge changes, or by adding a dedicated dRep pledge update certificate with equivalent ledger semantics.

This CIP does not change the formula for dRep voting power. dRep voting power remains based on the stake delegated to the dRep according to CIP-1694. The dRep pledge is included in that distribution as stake delegated to the dRep for whom the pledge is locked.

### dRep pledge rewards and voting power

A `drepPledgeDeposit` is pledged stake.

For governance accounting:

- `drepPledgeDeposit` MUST count as voting power delegated to the dRep that the pledge deposit applies to.
- This pledged stake therefore contributes to that dRep's voting power under the existing delegated-stake voting model.

For stake-pool accounting:

- `drepPledgeDeposit` MUST count toward the stake pool delegation chosen by the pledge owner credential.
- Staking rewards attributable to the deposit are credited to the pledge owner credential's reward account.

This allows a dRep to pledge ADA to their dRep role while still choosing which stake pool receives the staking weight of that ADA.

### Snapshot behavior for pledge updates

Raising or lowering a pool or dRep pledge deposit MUST be possible without retiring the pool or deregistering the dRep.

Deposit deltas are applied to the transaction that updates the registration:

- Increases lock additional ADA when the update transaction is accepted.
- Decreases refund ADA when the update transaction is accepted.

However, the effective pledge used for reward and governance calculations MUST change only at the normal snapshot boundary relevant to that calculation.

For stake pools:

- Reward calculation uses the effective `poolPledgeDeposit` from the relevant stake snapshot.
- A deposit update accepted after a snapshot MUST NOT change rewards calculated from that snapshot.

For dReps:

- Governance calculations use the effective `drepPledgeDeposit` from the relevant dRep stake distribution snapshot.
- A deposit update accepted after a snapshot MUST NOT change votes or ratification calculations based on that snapshot.

This preserves liquidity while preventing a pledge update from changing calculations that are already fixed by a prior snapshot.

### Retirement and deregistration

When a stake pool is retired, the remaining `poolPledgeDeposit` is returned through the normal pool retirement mechanism.

When a dRep is deregistered, the remaining `drepPledgeDeposit` is returned through the normal dRep deregistration mechanism.

The final remainder at or above the applicable minimum deposit cannot be retrieved through an ordinary pledge update. An update that would reduce the deposit below `pp.minPoolDeposit` or `pp.minDrepDeposit` MUST be rejected. Retrieving that final deposit requires pool retirement or dRep deregistration.

### Ledger queries and ecosystem visibility

Ledger state queries SHOULD expose:

- `poolPledgeDeposit` for each registered pool,
- effective pool pledge for the current and relevant future reward snapshots,
- pledge owner credential for each registered pool pledge deposit,
- `drepPledgeDeposit` for each registered dRep,
- effective dRep pledge for the current and relevant future governance snapshots,
- pledge owner credential for each registered dRep pledge deposit.

Wallets, CLIs, explorers, and governance tools SHOULD display pool pledge and dRep pledge as locked ADA. Tools SHOULD distinguish:

- pledge deposit currently locked,
- pledge effective for the current reward or governance snapshot,
- pending change that will become effective at a future snapshot, if applicable.

Tools SHOULD stop presenting pool pledge as both "declared pledge" and "live pledge". Under this CIP, the pledge deposit is the pledge.

## Rationale: how does this CIP achieve its goals?

### Pledge becomes real locked ADA

The central change is conceptual: pledge is no longer a declaration backed by a stake-credential check. It is ADA locked in the deposit pot.

This simplifies the operator model. A pool operator no longer needs to reason about whether the correct stake credentials hold enough ADA to satisfy a declared pledge. The pool pledge deposit itself is the pledge. A dRep likewise does not merely pay a fixed admission deposit. The dRep chooses how much ADA to lock as pledge, subject to the protocol minimum.

This also removes the confusing split between declared pledge and live pledge. If 100,000 ADA is locked as `poolPledgeDeposit`, the pool has 100,000 ADA of pledge.

### Pledged ADA remains economically active

This CIP does not remove pledged ADA from staking rewards or governance voting power. It changes how the ADA is locked and attributed as pledged stake.

Pool pledge deposits are required to support the pool they pledge to for stake-pool accounting, but their governance voting power follows the pledge owner credential's dRep delegation. dRep pledge deposits are required to support the dRep they pledge to for governance accounting, but their staking rewards and stake-pool weight follow the pledge owner credential's stake-pool delegation.

This preserves the expected behavior that locked pledge is still ADA participating in the protocol. Because pledged ADA is held in ledger deposit accounting rather than ordinary UTxOs, the ledger MUST include pledged stake in the relevant stake-pool and governance distributions by explicit deterministic rule.

### The frankenwallet path is removed

CIP-0019 explicitly allows the payment and delegation parts of a Shelley address to be controlled by different entities. This is useful and valid, but it means current pledge satisfaction follows delegation rights rather than payment ownership.

Under this CIP, a pool's pledge is not inferred from payment credentials, stake credentials, or address composition. It is the ADA locked under that pool's `PoolDeposit` purpose. A hybrid address can still exist, and stake can still be delegated normally, but it cannot inflate a pool's pledge unless ADA is actually locked as that pool's pledge deposit.

### CEX and custody risk is reduced, not eliminated

This proposal does not claim to distinguish an operator's own ADA from ADA held in custody for customers. A centralized exchange or custodian that controls a large amount of ADA may still be able to lock that ADA as pledge if its legal and operational model permits doing so.

The improvement is narrower but still important: non-custodial actors cannot use address composition to make another party's stake credential appear as pool pledge without locking the ADA. If the community later chooses to make pledge more important through a reward, voting, or compensation mechanism, this CIP gives that mechanism a cleaner and more auditable pledge input.

### Existing parameters are renamed and repurposed

Keeping the old names `poolDeposit` and `drepDeposit` would preserve historical continuity, but it would also obscure the new meaning of those parameters. Under this CIP they are no longer fixed deposit amounts. They are minimum pledge deposits.

Renaming them to `minPoolDeposit` and `minDrepDeposit` makes that meaning explicit while preserving the conceptual role of the existing parameters:

- there is one minimum pool pledge deposit,
- there is one minimum dRep pledge deposit,
- each registered pool or dRep has one actual locked pledge deposit.

This requires documentation, tooling, and constitutional guardrails to be updated so that the renamed parameters are understood as minimums rather than fixed amounts.

### dRep pledge is deliberately limited in this CIP

dRep compensation and dRep voting-power concentration are important topics, but they are not settled by this proposal. This CIP introduces dRep pledge as an on-chain primitive and includes it in ordinary delegated stake accounting, but does not add a special dRep compensation or voting-weight formula.

Future CIPs can use dRep pledge as one input while preserving backward compatibility with the primitive introduced here.

### Relationship to CIP-50 and other pledge proposals

CIP-50 and related reward-sharing proposals change how pledge affects rewards. This CIP changes what pledge is.

The two ideas are complementary. A reward formula can still include pledge influence, leverage caps, or other pledge-based behavior. Under this CIP, those formulas read pledge from locked pool deposits rather than from declared pool parameters and owner stake checks.

## Path to Active

### Acceptance Criteria

- [ ] CIP editors confirm that the ledger semantics are complete, unambiguous, and consistent with the CIP process.
- [ ] Ledger maintainers confirm that pool and dRep deposits can be exposed to the reward calculation, registration rules, and state query interfaces required by this CIP.
- [ ] Wallet, CLI, explorer, and governance-tool maintainers confirm that pledge deposits, effective pledge, pledge owner credentials, and deposit deltas can be displayed clearly.
- [ ] Any required updates to constitutional guardrails for `minPoolDeposit` and `minDrepDeposit` are identified.
- [ ] Implementation is present within block-producing nodes used by 80% or more of stake before the proposal is considered Active.

### Implementation Plan

1. Community deliberation
   - Publish the draft CIP and collect feedback from SPOs, dReps, wallet teams, explorers, ledger maintainers, the Parameter Committee, the Technical Steering Committee, and CIP editors.
   - Collect data on current pool pledge distribution, current dRep registrations, known CEX and multipool stake concentration, and Mike Hornan's proposed CEX influence ratio.

2. Ledger specification updates
   - Rename `poolDeposit` to `minPoolDeposit` and `drepDeposit` to `minDrepDeposit`.
   - Update pool registration and update certificates to carry an explicit `poolPledgeDeposit` and pledge owner credential.
   - Update dRep registration and update certificates to carry an explicit `drepPledgeDeposit` and pledge owner credential.
   - Update pool registration transition rules to support pledge deposit deltas, since existing ledger behavior assumes pool deposits do not change during pool re-registration.
   - Extend dRep update certificates, or add a dedicated dRep pledge update certificate, so dRep pledge deposits can be raised or lowered without deregistration.
   - Remove, deprecate, or ignore the declared pledge field from pool parameters so `poolPledgeDeposit` becomes the sole pledge source.
   - Update transition rules so pool and dRep registration updates pay or refund deposit deltas, while rejecting reductions below the applicable minimum.
   - Update reward calculation to read pool pledge from the effective `poolPledgeDeposit`.
   - Remove the owner-stake pledge satisfaction check from pool reward calculation.
   - Update stake and governance distribution calculations so pledged stake remains active for staking rewards and dRep voting power as specified above.

3. Node, CLI, wallet, and query support
   - Implement the ledger changes in cardano-ledger and cardano-node.
   - Add CLI support for registering and updating pools and dReps with explicit pledge deposit values and pledge owner credentials.
   - Add state queries for actual and effective pool/dRep pledge deposits.
   - Update wallet and explorer APIs to display locked pledge, snapshot-effective pledge, and the staking/governance delegations attached to pledge deposits.

4. Testing and rollout
   - Add ledger unit and property tests for registration, updates, refunds, minimum deposit enforcement, reward snapshots, governance snapshots, retirement, and deregistration.
   - Run a dedicated testnet or preview-era test deployment with mainnet-like parameters.
   - File any necessary constitutional or governance actions for parameter guardrail changes.
   - Activate through a hard-fork governance action after ecosystem readiness is confirmed.

## Open questions

- Should we allow the same locked pledge to support multiple roles, such as SPO and dRep, simultaneously?

## References

- CIP-0019: Cardano Addresses. https://github.com/cardano-foundation/CIPs/tree/master/CIP-0019
- CIP-0050: Pledge Leverage-Based Staking Rewards. https://github.com/cardano-foundation/CIPs/tree/master/CIP-0050
- CIP-0149: Optional dRep Compensation. https://github.com/cardano-foundation/CIPs/tree/master/CIP-0149
- CIP-1694: A First Step Towards On-Chain Decentralized Governance. https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694
- Pledging and rewards, Cardano Docs. https://docs.cardano.org/about-cardano/learn/pledging-rewards/
- Stake pool registration, Cardano Developer Docs. https://developers.cardano.org/docs/operate-a-stake-pool/register-stake-pool/
- Registering a dRep, Cardano Developer Docs. https://developers.cardano.org/docs/get-started/infrastructure/cardano-cli/governance/register%20drep/
- A Formal Specification of the Cardano Ledger. https://intersectmbo.github.io/formal-ledger-specifications/cardano-ledger.pdf
- The Cardano Constitution. https://cardano.org/constitution/

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
