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
Created: 2023-12-20
License: CC-BY-4.0
---

# CIP-?: Plutus v1

## Abstract

Despite making up less than half the transactions on Cardano, Plutus v1 scripts occupy over 90% of the block space. Increasing the space available to blocks is risky, as it impacts the block propagation time. This proposal puts forth a simple way to reduce this strain.

## Motivation: why is this CIP necessary?

Plutus v2 introduced a way to publish scripts on-chain, and *reference* those scripts to satisfy the witness requirement. However, because this was done via a new field on the transaction (i.e. "Reference Inputs"), which shows up in the script context, this feature is not backwards compatible with Plutus v1.

However, despite consisting of less than half of the transactions being posted to the blockchain in late 2023, the bytes taken up by constantly re-publishing the same Plutus v1 scripts is nearly 90% of each block. Put another way, of the 151gb it takes to represent the 6 year history of the chain, roughly 93 gb of that (nearly 61%) can be attributed to the wasted space from repeating the same scripts in the last 2 years.

This problem isn't going away: while protocols may migrate to new Plutus v2 or v3 scripts, these old protocols will exist forever. Liquidity locked in these scripts, sometimes permanently, will mean that there is always an arbitrage opportunity that incentivizes a large portion of the block to be occupied by continually republishing these v1 scripts.

Additionally, raising the block size is considered incredibly sensitive, as it impacts block propagation times.

A simple, backwards compatible mechanism for plutus v1 protocols to satisfy the script witness requirement, without changing the script context and causing breaking changes for Plutus v1 scripts, would alleviate quite literally millions of dollars worth of storage requirements, user pain, and developer frustration.

## Specification

Currently, the relevant parts of the transaction body CDDL are produced below:

```
transaction =
  [ transaction_body
  , transaction_witness_set
  ...
  ]

transaction_body =
  { 0 : set<transaction_input>             ; inputs
  ...
  , ? 7 : auxiliary_data_hash
  ...
  , ? 11 : script_data_hash
  ...
  , ? 13 : nonempty_set<transaction_input> ; collateral inputs
  ...
  , ? 18 : nonempty_set<transaction_input> ; reference inputs
  }

post_alonzo_transaction_output =
  {
  ...
  , ? 3 : script_ref   ; script reference
  }

transaction_witness_set =
  {
  , ? 3: [* plutus_v1_script ]
  ...
  , ? 6: [* plutus_v2_script ]
  , ? 7: [* plutus_v3_script ]
  }
```

In order to satisfy the script witness requirement for some input locked by script hash H, you must either:
 - Include a script that hashes to H in the `transaction_witness_set`, in fields 3, 6, or 7
 - Include an input in field 18 of the transaction body (reference inputs), which refers to an input with `script_ref` set to a script that hashes to H

Because of the use of the reference inputs, this will cause the construction of the plutus v1 script context to fail, as it has no backwards compatible way to expose these reference inputs to the script context.

However, the `transaction_witness_set` is not exposed directly to the script context.

So, we propose adding a new field for script references, as follows:

```
transaction_witness_set =
  {
  , ? 3: [* plutus_v1_script ]
  ...
  , ? 6: [* plutus_v2_script ]
  , ? 7: [* plutus_v3_script ]
  , ? 8: [* transaction_input ]
  }
```

These inputs are not visible as reference inputs to the script context, and are *only* used to satisfy the script witness criteria. The node will look up each input referenced in `transaction_input`, and use any scripts found in the `script_ref` field, hash them, and use those scripts when it comes to evaluating whether each input can be spent.

## Rationale: how does this CIP achieve its goals?

This approach would immediately allow all major plutus v1 dApps to reduce their transaction sizes dramatically. Some napkin math for both Sundae and Minswap shows that this would cut around 85% of the transaction size for each transaction; Considering 90% of the space taken by by blocks is taken up by Plutus v1 scripts, this would have a massive impact on chain load.

This may initially receive push-back because it admittedly has a "hacky" aesthetic; It feels like introducing multiple ways to accomplish the same thing, and adds a wrinkle to the specification of the transaction body.

However, it is hard to overstate the long-term positive impact that this change could have for real users of the Cardano blockchain. Unless there is a very material drawback or attack vector for this change, I believe that many would agree that the aesthetic awkwardness is vastly outweighed by this real world impact.

## Path to Active

### Acceptance Criteria

- [ ] Review of this proposal by the relevant subject matter experts
- [ ] Implement the change in the cardano-ledger and cardano-node repositories
- [ ] Include this change in a relevant hard fork

### Implementation Plan

- [ ] 

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
