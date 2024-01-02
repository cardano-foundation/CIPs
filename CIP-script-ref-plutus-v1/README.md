---
CIP: ?
Title: Plutus v1 Script References
Status: Active
Category: Plutus
Authors:
    - Pi Lanningham <pi@sundaeswap.finance>
Implementors: N/A
Discussions:
 - https://twitter.com/SmaugPool/status/1737454984147390905
 - https://twitter.com/Quantumplation/status/1737704936089985339
 - https://twitter.com/SmaugPool/status/1737814894710231161
Created: 2023-12-20
License: CC-BY-4.0
---

# CIP-?: Plutus v1

## Abstract

Despite making up less than half the transactions on Cardano, Plutus v1 scripts make up 90% of the space dedicated to scripts (around 60% of the total block space). Increasing the space available to blocks is risky, as it impacts the block propagation time. This proposal puts forth a simple way to reduce this strain.

## Motivation: why is this CIP necessary?

Plutus v2 introduced a way to publish scripts on-chain, and *reference* those scripts to satisfy the witness requirement. However, because this was done via a new field on the transaction (i.e. "Reference Inputs"), which shows up in the script context, this feature is not backwards compatible with Plutus v1.

However, despite consisting of less than half of the transactions being posted to the blockchain in late 2023, the bytes taken up by constantly re-publishing the same Plutus v1 scripts is nearly 60% of each block. Put another way, of the 151gb it takes to represent the 6 year history of the chain, roughly 60 gb of that (nearly 40%) can be attributed to the wasted space from repeating the same scripts in the last 2 years.

This problem isn't going away: while protocols may migrate to new Plutus v2 or v3 scripts, these old protocols will exist forever. Liquidity locked in these scripts, sometimes permanently, will mean that there is always an arbitrage opportunity that incentivizes a large portion of the block to be occupied by continually republishing these v1 scripts.

> Historical Note: At the time that the babbage hardfork happened, the belief was that Plutus v2 would be attractive enough to encourage migration of that traffic. In practice, this simply isn't true, and circumstances like locked liquidity were unforseen.

Additionally, raising the block size is considered incredibly sensitive, as it impacts block propagation times.

A simple, backwards compatible mechanism for plutus v1 protocols to satisfy the script witness requirement, without changing the script context and causing breaking changes for Plutus v1 scripts, would alleviate quite literally millions of dollars worth of storage requirements, user pain, and developer frustration.

## Specification

We propose relaxing the ledger rule that fails Plutus v1 scripts in transactions that have reference inputs, and to construct a script context that excludes reference inputs.

The ledger rule shouldn't change in other ways: for example, Plutus v1 scripts should still fail in the presence of inline datums or reference scripts on spent transaction inputs.

## Rationale: how does this CIP achieve its goals?

The main concern with this relates to backwards compatibility. The ledger makes very strong commitments regarding the behavior of scripts: any observable change represents a risk that there is some script out there that will either be unspendable when it should be, or spendable when it should not be.

Because of this, any such change which violates this must satisfy a burden of proof with regards to both the benefits and the risks. This was in fact considered [in the original CIP](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031#how-should-we-present-the-information-to-scripts), and at the time, it was decided that the justification would likely not meet that high bar.

Thus, as a rationale for this CIP, we repeat that analysis, hopefully with a different conclusion.

In terms of benefit, this approach would immediately allow all major plutus v1 dApps to reduce their transaction sizes dramatically. Some napkin math for both Sundae and Minswap shows that this would cut around 85% of the transaction size for each transaction; Considering the portion of block space currently taken up by Plutus v1 scripts, this represents a significant savings.

It is hard to overstate the long-term positive impact that this change could have for real users of the Cardano blockchain.

In terms of the risks, there are four main risks to consider:

 - Funds that should be spendable are suddenly not spendable;
 
   In this case, a user could simply continue to use the existing witness mechanism to provide the scripts, and those funds become spendable again.

 - Funds that should not be spendable are suddenly spendable;
 
   In this case, it is very hard to imagine a scenario where this would be true that isn't crafted intentionally. It would have to be some script that was dependent on the transaction fee being above a certain threshold, which is already a dangerous assumption to make given the updatable protocol parameters. In other instances (such as the change to how the minimum UTXO output is calculated) this kind of risk hasn't been an obstacle.

 - The execution units change, without changing the outcome, resulting in a different cost for the user;

   In this case, the cost would only go down, and it is again hard to imagine a scenario where this is at material risk of violating some protocols integrity in a way that is not already compromised.

## Path to Active

### Acceptance Criteria

- [ ] Review of this proposal by the relevant subject matter experts
- [ ] Implement the change in the cardano-ledger and cardano-node repositories
- [ ] Include this change in a relevant hard fork

### Implementation Plan

- [ ] 

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
