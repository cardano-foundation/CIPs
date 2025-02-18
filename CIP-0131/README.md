---
CIP: 131
Title: Transaction swaps
Category: Ledger
Status: Proposed
Authors:
    - Alexey Kuleshevich <alexey.kulehsevich@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/880
Created: 2024-08-08
License: [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0)
---

## Abstract

Transaction swaps are miniature unbalanced transactions that are individually signed by the spender, but must be included in a regular transaction in order to be accepted on chain. Inclusion of such swaps would effectively implement Babel fees, as well as allow for a third party service to construct a settlement system on the Cardano blockchain.

## Motivation: why is this CIP necessary?

Desire to have this functionality has already been described in [Transaction pieces - CIP-0130](https://github.com/cardano-foundation/CIPs/pull/873/files) as well as [Validation Zones](https://github.com/cardano-foundation/CIPs/pull/862). Therefore I will not dwell on motivation too much at this point, but we will expand this section at a later point.

## Specification

Both  [Transaction pieces - CIP-0130](https://github.com/cardano-foundation/CIPs/pull/873/files) and [Validation Zones](https://github.com/cardano-foundation/CIPs/pull/862) have some great ideas, but both of them are overly invasive from implementation perspective. They also have severe drawbacks like backwards incompatibility issues on the binary level or requiring special support from consensus and network layers. Therefore here I will describe an alternative approach that would solve all the problems that I was able to identify.

First and foremost, the problem that we are trying to solve concerns the monetary part of the transaction. Therefore there is no need to involve all of the advanced features of the Ledger like submitting proposals and votes, registering entities like DReps, Constitutional Committee Members and Stake Pools, etc. We really want to keep the original architecture of a transaction intact. In other words we want to add new pieces to the existing transaction specification, instead of introducing new relations between transactions.

Each transaction will have to be balanced as a whole, just as before. Prior to describing changes to transaction itself, I need to introduce new concepts:

### Transaction Swaps

Transaction swaps will be like mini transactions, that only have a subset of features of a regular transaction that are relevant for solving the problems at hand. Here is a new cddl for a transaction swap:

```cddl
swap_body = { 0 : oset<transaction_input> ;; Regular inputs
            , 1 : [+ transaction_output]  ;; Outputs, that will have to be satisfied
            , ? 3 : slot_no               ;; Validity interval start slot number
            , ? 5 : withdrawals           ;; Regular withdrawals
            , ? 8 : slot_no               ;; Validity interval end slot number
            , ? 9 : mint                  ;; Mint field
            , ? 14 : required_signers     ;; Required signers
            , ? 15 : network_id           ;; Network Id
            , ? 22 : positive_coin        ;; Treasury donation
            }
```

If you compare this specification to the regular transaction body then you will see that all fields that are not relevant to monetary exchanges are missing. At the same time there is not a single new field that was added, which means transaction swap body will be compatible at a binary level with all of the existing tools and hardware wallets. This will also prove to be benefitial for their implementation in the Ledger codebase.

Next we define the witnesses required for a transaction swap to be valid. Unlike regular transactions we will not require Plutus scripts or spending datums to be provided in the swap witness set. That burden will be placed on the transaction builder. Using this approach will allow us to avoid duplication of providing the same scripts and spending datums, when they are used multiple times across many swaps. We also cannot require swap builders to provide execution units for any of the Plutus scripts used by it, because the script execution will depend on the full transaction, instead of just individual swaps. Auxiliary data is also not a feature that we will be adding to the swaps in order to reduce complexity. There are only two requirements for the swap witnesses:

1. Cryptographic signatures of the transaction swap with corresponding public keys
2. Datums which need to be supplied to all of the Plutus scripts in the swap

```cddl
swap_witness_set = { ? 0 : nonempty_set<vkeywitness>
                   , ? 1 : nonempty_set<native_script>
                   , ? 2 : nonempty_set<bootstrap_witness>
                   , ? 5 : swap_redeemers
                   }
swap_redeemers = { + [ tag   : swap_redeemer_tag
                     , index : uint .size 4
                     ] => plutus_data
                 }
swap_redeemer_tag =
    0 ; inputTag "Spend"
  / 1 ; mintTag  "Mint"
  / 3 ; wdrlTag  "Reward"
```

Transaction swap is minimal, only the body and the witnesses:
```cddl
transaction_swap =
  [ swap_body
  , swap_witness_set
  ]
```

Important part of the transaction swap is that it does not specify any fees, does not provide the collateral nor it specifies the phase-2 validity. All this responsibility goes on the transaction builder.

All that being said, we could potentially allow for transaction swap creators to optionally specify Plutus scripts and spending datums. There is no inherent reason why we should forbid users from supplying this information, but it could be cheaper for everyone if they supplied it off chain together with the transaction swap and let the transaction builder decide how to supply this information in the transaction.

### Transaction

There are two new changes that we will need to add to a transaction body.

Naturally, the first change is a new field with the list of all transaction swaps:

```cddl
transaction_body =
  { ....
  , 23 : [* transaction_swap]
  }
```

The second change is to the transaction outputs. Important part of this proposal is that it can preserve our current mechanism of identifying unspent outputs: `transaction_body_hash + output_index`. There is an easy way to achieve this, namely we can require the transaction builder to list all of the same outputs that are present in all of the swaps as regular outputs. However, this would result in a lot of duplication, which would negatively affect the size of the transaction and thus the fees. We can do one better. Instead we can add a new case to a transaction output:

```cddl
new_transaction_output = transaction_output
                       / swap_output_index

swap_output_index = [ swap_index   : uint .size 2
                    , output_index : uint .size 2
                    ]
```

`swap_index` would refer to the location of the swap in the list of `transaction_swap`s, while the `output_index` would identify the location of output the list of swap's outputs. The interesting part of this change is that it will only look like this at the serialization level, while Ledger can perform a transformation and resolve the `swap_index` into the same `TxOut` that we all know and love. This would allow for transaction swap outputs to travel into the same `UTxO`. In other words there are no changes necessary in the ledger state to accomodate this approach.

Unfortunately there is a slight problem with the above CDDL definition of `swap_output_index`, because it is defined as an array it could conflict with definition of `pre_babbage_transaction_output`, which is also defined as an array of 2 or 3 items. One way to solve this would be to define `swap_output_index` as a single 32bit unsigned integer, instead of two 16bit unsigned integers. Where topmost 16bits would refer to `swap_index`, while the bottom bits would refer to `output_index`:

```cddl
swap_output_index = uint .size 4
```

That would be the most efficient representation, but there are others. We could decide on the most suitable binary representation for this index at a later point.

Transaction witnesses will receive a new field with a specialized type of redeemer, since they will have to supply execution units for all of the scripts in the swaps and they will require slightly different redeemer pointers:

```cddl
transaction_swap_redeemers = { + [ swap_index : uint .size 2
                             , tag        : swap_redeemer_tag
                             , index      : uint .size 4
                             ] => ex_units
                             }

transaction_witness_set = { ....
                          , ? 8 : nonempty_set<plutus_v4_script>
                          , ? 9 : transaction_swap_redeemers
                          }
```

## Rationale: how does this CIP achieve its goals?

With the introduction of unbalanced transaction swaps, that need to be signed by the owner, we allow users to describe what they would like to receive and to which Cardano address the desired value should be sent to. They can also use all of the regular mechanisms of spending their assets: be it spending outputs, withdrawing rewards or minting new assets. When creating transaction swaps users will not pay directly for the transaction fees, but they will have to estimate how much would it cost to include their swap on chain and spend just that much more value. The beauty of this is that it does not have to be ADA, this extra money for the fee could be paid by any asset. It will be up to the transaction builder to decide if the extra included amount is enough to pay for the associated fees. In my understanding this is exactly the definition of "Babel Fees".

One crucial aspect that I haven't talked about is how this approach interacts with execution of Plutus scripts and their context. The only and the most sensible interaction comes from the definition of a transaction, it will be supplied as a whole to every Plutus script starting with `PlutusV4` version onwards. This is the only sensible approach and it is the one that allows for all scripts in the transaction to have access to all of the transaction swaps. One great benefit we get from this is that Plutus scripts will never see such a thing as an unbalanced transaction.

The major advantage of the approach described in this proposal is in what it takes to implement it. Because of the incredible similarities of transaction swaps with regular transactions we, in ledger, will be able to reuse a lot of the existing functionality. There is no need to change serialization of a block. Binary specification of a transaction retains backwards compatibility. Another extremely important aspect of this approach is that there is no effect on consensus and network components. In other words we do not need to change the architecture of how Ledger interacts with the rest of the system, we just need to implement some new ledger rules that deal with these new features.

Exclusion of all of the irrelevant features of a regular transaction from the swaps will reduce the complexity of implementation and decrease the chance of introducing bugs into the system. This proposal is designed in the type safe spirit of Haskell, because it specifies the feature explicitly, instead of trying to abuse existing ledger rules in order to accommodate desired features. Most importantly, all transactions will continue to be balanced, as crypto gods intended them to be.

### Comparison to `Validation zones`

The CIP [Validation Zones](https://github.com/cardano-foundation/CIPs/pull/862) also solves some of the same problems, but in a very different way. It makes sense to compare properties of these two approaches, so that the community members could make an an educated decision on which approach is better for them.

Technically speaking these two approaches do not conflict with each other and could be implemented together. However, since both of them solve some of the same problems, in my opinion we should avoid going that route.

Both proposals allow for unbalanced transactions to be submited by separate parties that do not have mutual trust, which is the main problem we've set out to solve.

These two proposals have different levels of complexity in respect of implementation, which we are not going to discuss here, since the point of this section is to figure out the difference in features that users of Cardano could evaluate.


#### Plutus Context

This proposal has one huge difference from the Validation Zones proposal, namely all of the scripts in a transaction, uncluding the ones in the swaps will see all of the transaction swaps in their context, because they get access to the full transaction. This comes with a benefit of allowing plutus scripts to make decisions on all of the individually unbalanced pieces. That being said it would come at a higher cost for scripts, unless we would also implement [cardano-ledger#3124](https://github.com/IntersectMBO/cardano-ledger/issues/3124), which we have plans on doing anyways. The biggest cost is extra complexity for script writers, since now inputs and withdrawals and minting scritps could now appear in two different places: in regular transactions and in swaps.

#### Dependencies of transactions and collateral

Another major difference is that swaps are constructed completely independently and it is only the top level transaction that combines them all together. This allows for an unlimited number of swaps to be constructed concurrently, while Validation zones have inherent dependency in their design: every transaction depends on all of the preceding transactions in the zone. From my understanding this dependency comes from the design of how colateral is specified in the zones.

Here is a dependency graph of three swaps in a transaction:
```
    tx
   / | \
  /  |  \
s1   s2  s3
```
while this is the dependency of equivalent setup of four transactions in a zone:

```
tx1 <- tx2 <- tx3 <- tx4
```

The decision of who pays for the collateral in Validation Zones comes with a natural benefit of deterring users from constructing transactions with phase2 validation, since the first transaction that fails phase2 validation is the one that pays for all scripts in all of the preceding transactions in the zone.

In case of swaps it is up to the transaction builder to figure out which swaps together make up a phase2 valid transaction, because ultimately they will be paying for the collateral if any of the scripts do not succeed. In my personal opinion it is totally reasonable to put this responsibilty on the transaction builder, since ultimately that is the entity that will be making the money in this process.

#### Full transaction vs a subset of features

Validation Zones allow for full blown transactions that allow usage of features that are not relevant for the goal of solving unbalanced transactions and the feature of Babel Fees, for example voting, proposing, certificates etc. It makes no sense to include them in the swaps, since that would unnecessarily complicate the logic, while in Validation zones it would not make sense to exclude any of them for the same reason. This could be viewed as a benefit or a drawback, depending on one's point of view. One imporant thing to remember when concidering this point is that both of the approaches respet the same transaction size limit.

## Path to Active

### Acceptance Criteria

- [ ] It is approved by the community and the plutus teams.
- [ ] It is approved by the formal methods team that is working on Babel Fees

### Implementation Plan

- [ ] Implement it in Ledger in the new era: create new types, create one or two new ledger rules, slightly change some existing ones.
- [ ] Implement support in `cardano-api` and tooling in `cardano-cli` to support transaction swaps

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
