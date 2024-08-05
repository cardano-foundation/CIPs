---
CIP: ????
Title: Transaction Pieces
Status: Proposed
Category: Ledger
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/862#discussion_r1700138228
    - https://github.com/cardano-foundation/CIPs/pull/862#issuecomment-2266689423
Solution-To: 
    - CPS-0015? | Intents For Cardano
Created: 2024-08-05
License: CC-BY-4.0
---

## Abstract

Cardano currently requires cryptographic keys to sign the entire transaction. As a result,
coordination is required whenever there are UTxOs being spent from pubkey addresses that belong to
different parties. However, this is unnecessary since parties really only need to approve the parts
of the transaction that are relevant to them. This CIP looks to enable users to create **pieces** of
transactions that can then be signed by the user(s) relevant to that piece. Users that have nothing
to do with a specific transaction piece *do not need to sign that piece*. These signed pieces can
then be aggregated off-chain and submitted together as a single complete transaction, without
requiring coordination or any other action from the respective users. By eliminating the need for
users to coordinate signing transactions, combined with the fact that transaction pieces can be
individually unbalanced, the basic Cardano transaction would become a natural intent settlement
system. This would open up the possibility for use cases such as Babel Fees and high frequency
off-chain trading. Furthermore, thanks to the eUTxO model, transaction pieces have the same level of
determinism as whole transactions.

## Motivation: why is this CIP necessary?

A key assertion underlying this CIP is **a batch of properly signed transaction pieces is
functionally equivalent to a single transaction signed by all parties**. To highlight the truth of
this assertion, consider two complementary atomic swap transaction pieces:

- Alice wants to swap 10 ADA for 10 DJED so she creates a transaction piece with:
    - 1 input from her address with 10 ADA
    - 1 output to her address with 10 DJED
- Bob wants to swap 10 DJED for 10 ADA so he creates a transaction piece with:
    - 1 input from his address with 10 DJED
    - 1 output to his address with 10 ADA

Individually, neither of these transaction pieces are balanced transactions which means they can't
be submitted to the blockchain. But if they are put together, the combination *is* a balanced
transaction. Transaction pieces must be included all-or-nothing which means Alice's input can only
be spent if the transaction actually includes her required output. 

Given the all-or-nothing requirement, does it matter that Alice did not sign Bob's piece or the
overall transaction? No, it doesn't because spending Bob's input doesn't require a signature from
Alice, and she was guaranteed to get the output she wanted. The same is true for Bob's signature.
There is no reason why the batching of these two transaction pieces should invalidate the
signatures. Requiring Bob to also sign Alice's transaction piece is like requiring a smart contract
to validate the spending of all UTxOs in a transaction, even those that aren't protected by that
smart contract.

Transaction pieces are the perfect model of an intent since *they are inherently flexible* (ie, a
single piece can encompass multiple inputs, outputs, mints, etc) and *they can be unbalanced*. Being
able to create unbalanced intents is critical to a healthy intent ecosystem because most intents are
fundamentally only pieces of a transaction. Look back at Alice's and Bob's pieces above. The atomic
swap intents don't say anything about the counter-party to the swap, and they shouldn't need to.
Requiring users to specify who the counter-party should be fundamentally limits who can actually
fulfill the intent. Without being able to create unbalanced transaction pieces, users would be
forced to specify inputs and outputs for the potential counter-party just to finish balancing the
transaction. 

Another benefit of not having to specify counter-party information is that these transaction pieces
can be trivially batched together without requiring coordination. As a result, a single transaction
can trivially satisfy the intents of many complete strangers. In short, being able to properly model
unbalanced intents makes transaction pieces a very natural and efficient intent settlement system.

> [!IMPORTANT]
> Transaction pieces effectively give another entity the right to spend your UTxOs as long as
> certain conditions are satisfied in the same transaction. The key thing that sets this proposal
> apart from other similar proposals is the fact that **the rest of the transaction is irrelevant**.
> Smart contracts can already operate this way which is why it is so easy to batch DeFi orders (aka
> intents) of complete strangers; this CIP extends this functionality to cryptographic keys.

### Babel Fees

Imagine if Alice wants to buy a sword NFT worth 25 GEMS and she expects the transaction fee to be
about 1.4 GEMS. Let's say she has a UTxO available with 30 GEMS. She can create a single transaction
piece with:

- 1 input from her address with 30 GEMS
- 1 output to her address with 3.4 GEMS + the sword NFT

Alice can sign this piece and send it off-chain to the store selling the NFT.

> [!IMPORTANT] 
> Alice does not actually know how much the transaction fee will be when she creates her transaction
> piece since the fee depends on the ultimate batch of transaction pieces. However, this is not a
> problem because Alice is effectively setting the fee she is willing to pay. The more she is
> willing to pay, the faster the store will fulfill her intent since it means her intent is more
> flexible in how it can be profitably batched with other intents. In other words, transaction
> pieces enable Babel Fees to naturally support its own intrinsic fee market.

The store can create its own complementary transaction piece to finish balancing Alice's piece. For
example, its piece could be:

- 1 input with the sword NFT + the amount of ADA actually required for the fee
- 1 output with 26.4 GEMS

The store can batch its transaction piece with Alice's to create a full transaction that can now be
submitted to the blockchain. Since Alice already signed her piece, the store does not need Alice's
permission to submit the batch. The store can even include transaction pieces from other users and
adjust its own piece to finish balancing the batch.

> [!IMPORTANT] 
> Since the store actually has all of the pieces that will be submitted in the batch, it has all of
> the information it needs to deterministically calculate the transaction fee (and collateral)
> required for the batch. This means this CIP does not sacrifice the ability for submitters to know
> how much a transaction will cost before actually submitting it. The store can use this information
> to figure out the best batch of pieces to make a profit while still satisfying the users' intents.

### High Frequency Off-Chain Trading

Day-trading is a common occurrence on exchanges, and it involves users creating and updating asking
prices with relatively high frequency. However, if these price updates were to happen on-chain,
each update would incur a transaction fee and would also take up block space that would otherwise go
to more critical activities. Using transaction pieces, it is trivial to support high frequency
off-chain price updates followed by efficiently batched settlement on-chain.

Consider Alice's atomic swap transaction piece again, this was effectively a limit order with an asking
price of 1 ADA/DJED. Off-chain aggregators can enable users to submit new transaction pieces for a
trade, and the aggregator can use the most recent transaction piece for that trade. For example, if
Alice created a new transaction piece with:

- 1 input from her address with 10 ADA (the same input from the prior transaction piece)
- 1 output to her address with 20 DJED

She can submit this new piece off-chain to effectively update her asking price to 0.5 ADA/DJED.

Using the off-chain aggregator like this requires a level of trust since the aggregator can always
choose to still use the older transaction piece. However, users can add "kill-switches" to their
transaction pieces to securely and trustlessly cancel all prior pieces. There are two main ways to
do this:

- Have the transaction piece reference a particular input that can be spent by the user.
- Have the transaction piece spend a particular input that can also be directly spent by the user.

With either of the above choices, spending the input in question will invalidate all transaction
pieces with this input since the UTxO would no longer exist. Both types of kill-switches can even be
used within the same transaction piece. Using both would give users the flexibility of either
canceling a particular limit order or a batch of limit orders (eg, all limit orders for a particular
trading pair).

The aggregator can take all (still valid) transaction pieces from users and batch them together,
possibly with on-chain liquidity sources, to submit them in a single transaction. Since the
transaction pieces did not need to specify a counter-party, these trades can be matched against
**any** counter-party, no matter its form. It is even trivially possible to match a single large
order against several smaller orders.

With this approach, all high frequency activity can happen off-chain while settling the actual
trades on-chain in the most efficient way possible.

This approach can even be combined with Babel Fees to enable day-traders to pay the transaction fee
in a native asset specified by the aggregator.

## Specification

Transaction pieces **must** be included all-or-nothing, and a transaction would become
**exclusively** a list of signed pieces (ie, an output cannot be specified outside of a transaction
piece). The current one-party style transaction can still be represented by a transaction with only
one piece where that piece is a fully balanced transaction body.

### CDDL

#### Transaction

Below is the current cddl representation of a transaction:

```cddl
transaction =
  [ transaction_body
  , transaction_witness_set
  , bool
  , auxiliary_data / null
  ]
```

It contains a single transaction body and a single witness set. This will be changed to contain a
list of transaction bodies, each paired with their own witness set.

The transaction witness set is currently:

```cddl
transaction_witness_set =
  { ? 0: [* vkeywitness ]
  , ? 1: [* native_script ]
  , ? 2: [* bootstrap_witness ]
  , ? 3: [* plutus_v1_script ]
  , ? 4: [* plutus_data ]
  , ? 5: [* redeemer ]
  , ? 6: [* plutus_v2_script ] ; New
  }
```

Smart contracts will still be executed against the full transaction (this will be discussed in a
later section), but all of the required information for an execution (eg, script, datum, and
redeemer) can be found within the corresponding transaction piece. This enables the witness set to
remain unchanged.

The new transaction would then be:

```cddl
transaction_piece =
  { 0: transaction_body
  , 1: transaction_witness_set ; The witness set for this transaction body.
  }

transaction =
  [ transaction_pieces    : [* transaction_piece]
  , bool
  , auxiliary_data / null
  ]
```

The order of the transaction pieces list is significant since it represents the order in which the
pieces must be combined, and ultimately determines the order of the inputs and outputs. How to
combine the pieces will be discussed later in the spec. 

#### Block

The cddl for a block is currently:

```cddl
block =
  [ header
  , transaction_bodies         : [* transaction_body]
  , transaction_witness_sets   : [* transaction_witness_set]
  , auxiliary_data_set         : {* transaction_index => auxiliary_data }
  , invalid_transactions       : [* transaction_index ]
  ]; Valid blocks must also satisfy the following two constraints:
   ; 1) the length of transaction_bodies and transaction_witness_sets
   ;    must be the same
   ; 2) every transaction_index must be strictly smaller than the
   ;    length of transaction_bodies
```

Just like with the transaction cddl, the block's transaction bodies and the transaction witness sets
will be merged, and the constraints must be updated accordingly:

```cddl
; This is re-posted here for reference.
transaction_piece =
  { 0: transaction_body
  , 1: transaction_witness_set ; The witness set for this transaction body.
  }

; A specific transaction in the block is a specific batch of transaction pieces. 
block_transaction = [* transaction_piece]

block =
  [ header
  , block_transactions   : [* block_transaction] ; This is new
  , auxiliary_data_set   : {* transaction_index => auxiliary_data }
  , invalid_transactions : [* transaction_index ]
  ]; Valid blocks must also satisfy the following constraint:
   ; 1) every transaction_index must be strictly smaller than the
   ;    length of block_transactions
```

### Transaction Size Limit

A transaction broken into pieces should still have approximately the same total size as the whole
transaction. There are a few things to note:

- If two transaction pieces require the same witness (ie, both pieces require a signature from
Alice), this witness would now effectively appear twice.
- Certain items can appear in multiple pieces (eg, the same input can be spent/referenced, tokens can
be minted/burned that would otherwise cancel out, etc).

Despite the above, it is probably fine to leave the maximum transaction size as is, at least to
start. The transaction fee would naturally incentivize users/aggregators to minimize the amount of
duplication in a transaction.

### Block Size Limit

Due to the possible duplicate items in each transaction and the fact that a block is made up of
multiple transactions, the issues in the Transaction Size Limit section are slightly exacerbated.
However, it should still be fine to keep the current block size limit, at least initially. Just like
with transactions, the transaction fee would naturally incentivize users to minimize duplications.

### Smart Contract Execution

While the cryptographic keys only need to sign the relevant transaction pieces, the smart contracts
would be executed against the full transaction. This requirement enables the current smart contract
interface to remain mostly untouched. The flow is essentially:

1. Deterministically derive the whole transaction from the list of pieces.
2. Generate the script context for the whole transaction.
3. Evaluate the smart contract using this script context.

When combining the transaction pieces, the required executions (ie, script + datum + redeemer) can
be built up as well. Duplicate executions should be removed. For example, if two transaction pieces
look to spend the same smart contract input using the same redeemer, there is no reason to evaluate
this scenario twice since they are guaranteed to have the same result.

### Transaction Fee and Collateral

Both the fee and collateral fields of the transaction body can be set in any piece, but only the
aggregator needs to set this (in their final piece that is used to finish balancing the batch). They
have all of the pieces that will go into the batch which means they can deterministically calculate
the required fee and collateral for the batch they are creating. Their final piece can be updated
after determining the required fee and collateral.

By having the aggregator put up the collateral, they are naturally incentivized not to include any
transaction pieces with smart contract executions that will fail. They can know whether the smart
contract execution will fail ahead of submission due to the determinism of the eUTxO model being
preserved, despite the transaction body being broken into pieces. The same incentives apply for the
transaction fee since the aggregator will want to minimize their own costs, and therefore, won't
waste execution resources.

### Transaction Piece Monoid Instance

The monoid instance for transaction pieces defines the rules for combining the pieces. In order to
be able to deterministically derive the full transaction, this instance must be standardized. The
monoid instance requires answering two questions:

1. What is an empty transaction piece?
2. How are two transaction pieces combined?

The first question is simple to answer: an empty transaction piece is an empty transaction body.
Users fill out as much information as they wish when creating their transaction piece. The rest of
the fields can remain empty.

> [!IMPORTANT]
> It doesn't really make sense to create a transaction piece with an input but no output, or an
> output but no input. Therefore, these fields can remain required fields. The fee is also required,
> but that can be set to zero in the pieces not paying the fee. All other fields in the transaction
> body are already optional.

The second question requires more consideration, but as a general rule, as long as there are no
incompatibilities between transaction pieces, they can be combined into the full transaction. Any
transaction that contains incompatible pieces should be rejected.

#### Ordering

The creator of the transaction piece gets to specify the order of inputs, outputs, reference inputs,
and collateral inputs **within** their piece. Then, the aggregator (the one that batches pieces and
submits the transaction) gets to decide the order **between** the pieces.

For example, if Alice creates a piece with `input1` followed by `input2` and Bob creates a piece
with `input3` followed by `input4`, then Charlie (the aggregator) only has two options:

```
[input1, input2, input3, input4] OR [input3, input4, input1, input2]
```

Charlie cannot put `input2` before `input1` because this would violate Alice's intent. The order of
everything else is standardized (eg, token mints are sorted by name, withdrawals are sorted by
credential, etc), so no one can control the order of them.

> [!IMPORTANT] 
> This would required [CIP-128](https://github.com/cardano-foundation/CIPs/pull/758) since the order
> of the inputs and reference inputs would need to be preserved. There may be intents where the
> order of these fields matter which is why the intent creator should get to specify their ordering.
> The collateral inputs could be an exception, but if we are already making the change for inputs
> and reference inputs, why not also make the change for collateral inputs?

#### Duplicate Inputs

It is valid for two separate transaction pieces in a batch to spend the same UTxOs (eg, a liquidity
source UTxO). This UTxO can still only be spent once and the batch must still be fully balanced
anyway, so there is no reason to prevent such collisions.

The only exception to this rule is when a smart contract protected UTxO is spent using different
redeemers in the different pieces. In this context, the pieces cannot actually be combined so a
transaction with a redeemer disagreement should be rejected. 

#### Minting Tokens

Token values already have a [monoid
instance](https://github.com/IntersectMBO/plutus/blob/36311fe6293c543694299fe4bb92bfde52a46597/plutus-ledger-api/src/PlutusLedgerApi/V1/Value.hs#L248)
and the same instance should be used here. The only exception is when the minting policies use
different redeemers across the transaction pieces; these combinations should be rejected.

#### Validity Intervals

When combining transaction pieces using validity intervals, the most restrictive interval that
satisfies both pieces should be used.

#### Transaction Fee

Just like with collateral, only the final balancing piece needs to specify the transaction fee
amount. But if two pieces do specify a transaction fee, the sum of the two fees should be used.

> [!NOTE] 
> Using the maximum of the two transaction fees could also work, but if multiple intents specify
> fees instead of only having the final balancing piece specify the fee, having the extra ada be
> free for the taking by the aggregator seems like a betrayal of the user's intent. It seems better
> to have the extra fee go to the Cardano Treasury. There really is no reason more than one
> transaction piece needs to specify a transaction fee amount.

#### All Other Fields

All other fields are essentially just lists and have a standardized sorting method. Therefore, they
should just be concatenated and sorted appropriately. Duplicates should be removed from the
resulting lists.

If the field can require a smart contract execution, redeemer disagreements across transaction
pieces should not be allowed.

### Phase 1 Validation

Phase 1 validation must be slightly changed to check:
1. All of the transaction pieces can be combined into a whole transaction (ie, there are no
   incompatibilities).
2. Each transaction piece is properly witnessed.
3. The whole transaction is a valid transaction. 

The rest of the current phase 1 checks should still be performed against the whole transaction (eg,
properly balanced, pays enough of a transaction fee, etc).

### Phase 2 Validation

Phase 2 validation remains unchanged since the smart contracts are still executed against the whole
transaction. 

> TODO: Does the collateral claiming mechanism (in the case of a phase 2 failure) need to be
> changed? I do not believe so, but I am not entirely sure.

## Rational: how does this CIP achieve its goal?

Thanks to the eUTxO model, transactions can safely be broken into pieces and aggregated off-chain
without having to sacrifice any determinism. By leveraging this feature, Cardano would gain two
unique abilities:

1. Users would be able to trustlessly build up transactions off-chain without having to coordinate
   with each other.
2. Transaction pieces can possibly be unbalanced.

These two properties are exactly the requirements for a simple, expressive, and efficient
(economically and computationally) intent settlement system. 

While this CIP would introduce some minor duplication in transactions and blocks, the fact that the
transaction fee is also based on the size of the transaction means all users would be naturally
incentivized to minimize this duplication as much as possible. The ability to push a significant
amount of activity off-chain (like in the high frequency trading example) would likely more than
make up for any remaining duplicate information in each transaction/block. Furthermore, the impact
this CIP has on the average block size seems smaller than the impact the main alternative proposals
would have on the average block size.

## Alternatives

### Validation Zones

[Validation Zones](https://github.com/cardano-foundation/CIPs/pull/862) is another intent settlement
system proposal, but it is unable to properly model all intents since it doesn't allow for
unbalanced intents (ie, intents without counter-party information). As a result of the model not
accurately representing all intents, the proposal requires a lot of extra complexity and friction
with its usage.

The Validation Zones CIP fundamentally models intents as full transactions which means all intents
must be balanced. Without the ability to specify unbalanced intents, Validation Zones forces users
to try to guess what actions the counter-party will use when satisfying their intent. In practice,
this means Alice must use input and output **placeholders** in her intent, and these placeholders
must also specify the value of the UTxO that will eventually go there; these placeholders are
necessary to finish balancing the intent transaction. But this creates problems for potential
counter-parties: 

- Only UTxOs that exactly fit those placeholders can be used
- The counter-party can't add or remove placeholders after the fact

Imagine if Alice wants to swap 100 ADA for 50 DJED; this says nothing about how the counter-party
will satisfy her swap. Perhaps Bob (the counter-party) wants to provide the DJED, but it is
currently broken up across three UTxOs. And perhaps he wants the 100 ADA he receives to be stored in
two separate outputs. If Alice specifies only one input placeholder and one output placeholder in
her intent transaction, Bob might be unable to act as her counter-party. If Bob really wanted to
still trade with Alice, he would have to find a way to merge his inputs and outputs into one input
and one output. This may not always be possible and Bob may have to give up on being Alice's
counter-party. In other words, because Alice was forced to specify placeholders in her intent, she
missed out on a potential trading partner.

DApps would also be unable to be direct liquidity sources for these intents due to not always being
able to match the value specified in each placeholder. If the input place holder is for 10.3 ADA but
the liquidity source UTxO actually has 20.5 ADA, this liquidity source cannot be used despite it
having enough liquidity. The Validation Zones CIP argues that DApps can just add support for
breaking-off/merging UTxOs so that the liquidity source UTxOs can be forced into the proper forms
for the required placeholders. However, this would dramatically increase the complexity and attack
surface of DApps that do this. And this added risk to users is just to compensate for a limitation
in the Validation Zones' design.

In addition to the counter-party issue, there must be a way for the ledger to actually support and
satisfy these placeholders. To accomplish this, the Validation Zones CIP introduces zones, unlocked
requests, and unlocked outputs. These new features require adding a lot of extra complexity to the
ledger and makes using Validation Zones intents a very complicated experience. For example,
satisfying a single intent actually requires multiple transactions (packaged as a zone).

Again, the counter-party issue and extra complexity in Validation Zones are simply due to not being
able to accurately model unbalanced intents. Since this CIP *can* model unbalanced intents, it can
cover all of the same use cases while only adding a fraction of the complexity.

It is also worth noting that, since the Validation Zones design uses otherwise unnecessary
placeholders and extra transactions just to satisfy these placeholders, the impact Validation Zones
would have on the average block size is likely equivalent to, if not larger than, the impact this
CIP would introduce.

### Westberg's "Smart Transactions"

[Smart
Transactions](https://github.com/input-output-hk/Developer-Experience-working-group/issues/47) is
very similar to Validation Zones in that it tries to use fully balanced transactions to model all
intents. Because of this, it suffers from the same counter-party issue, over-complexity, and
possible overly-increased average block size as Validation Zones.

### Original Babel Fees Design

The original design effectively required minting policies to be executed in every transaction, but
this is not always possible/feasible.

## Path To Active

### Acceptance Criteria

- [] It is approved by the community and the ledger/plutus teams.

### Implementation Plan

- [] The ledger spec is updated to use transaction pieces.
- [] Implementation of the Cardano node with a new era/hardfork.
- [] Deployed on testnet/mainnet

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
