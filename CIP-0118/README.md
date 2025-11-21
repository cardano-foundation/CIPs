---
CIP: 118
Title: Nested Transactions
Category: Ledger
Status: Proposed
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>
    - Will Gould <will.gould@iohk.io>
    - Alexey Kuleshevich <alexey.kuleshevich@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/780
    - https://github.com/cardano-foundation/CIPs/pull/862
    - https://github.com/cardano-foundation/CIPs/pull/880
Created: 2024-03-11
License: CC-BY-4.0
---

## Abstract

We propose a set of changes that revolve around nested transactions, a construct for composing
certain kinds of _partially valid transactions_, such as unbalanced transactions, or transactions
with missing fees. The missing value or data must be provided by a subsequent
transaction. Such partially valid transactions, which are called sub-transactions,
must be placed into batches by aggregators.
The batch must also include a _top-level_ transaction. The completed batch must be fully balanced.
Applying a complete batch results in a valid ledger update,
however, applying each of the individual transactions would not be possible. This scheme allows users
to make and accept swap offers without the need for a centralized exchange or two-way communication.
It gives non-ADA holders a way to engage with the Cardano ecosystem. It also creates new business opportunities
for users willing to make and accept offers, run aggregator services, subsidize the use of their DApps, etc.

## Motivation: why is this CIP necessary?

This CIP provides a partial solution to the problems described in
[CPS-15](https://github.com/cardano-foundation/CIPs/pull/779).
In particular, it describes some ledger changes that allow settlement
of intents that require *counterparty irrelevance*, including many of the swap use cases
and DApp fee sponsorship. *Counterparty irrelevance* is a property of a transaction batching protocol
wherein a transaction author is not required to approve the batch into which the
transaction will be included, and that decision can be made autonomously by the batcher.
This property allows batches to be made with one-way communication (i.e. broadcast) only.

One of the motivations behind designing this solution is _Babel fees_,
which is a requirement to support "paying transaction fees in non-ADA tokens".
The Babel-fees usecase is a special case of a swap. Supporting swaps is very desirable functionality for cryptocurrency
ledgers.

There are off-chain solutions being developed for the purpose of achieving the same
(major) goals, including fee coverage, atomic swaps, DApp fee sponsorship,
collateral sponsorship, etc. This gives us indication that it is a worthy pursuit
to solve this problem at the ledger level, in a way that is cheaper, more convenient,
maintains formal guarantees, requires less off-chain communication, and does not require deposits or interaction
with smart contracts.

### New functionality

The ledger changes we describe have been developed as a result of the discussions and
proposals in previous CIPs, including previous versions of validation zones proposals,
and Transaction Swaps. The following
new functionality are supported by the changes :

1. transactions can be batched
- batch contains one top-level transaction, with multiple possible sub-transactions ;

2. the batch must be balanced, but individual transactions in it do not have to be, so
- transactions in a single batch may satisfy each others' fees and minUTxOValue ;
- unbalanced transactions can be interpreted as swap offers or intents, getting resolved within a complete batch ;

3. scripts are shared across all transactions in a single batch
- enables script deduplication ;

4. guarding scripts enable sub-transactions to specify properties required of batches in which they may be included
- allows transaction authors to impose constraints
on the batches into which their transactions are added without knowing the exact contents of the batch ;

5. the top-level transaction must provide collateral for all scripts in its sub-transactions
- sub-transactions will not be required to cover the collateral for scripts that they will include ;

We note that the functionality added by (4) makes it possible to view each sub-transaction as an *intent*
to perform a specific action (whose fulfillment within the batch is ensured by the validation of the guard script).
The types of intents supported by this are ones that *do not require
the relaxation of existing ledger rules*. That is, a user can specify any intent the rest of the batch
must satisfy without violating existing ledger rules. Adding support for intents that *do require ledger rule relaxations*, such
the ones in (2, 3, 5) above, must be done
more carefully to ensure secure operation of the ledger program.

### New use cases

As a result of introducing this new functionality, many new use cases will be supported, 
among which are the following : 

**Open (atomic) swaps.** A user wants to swap 10 Ada for 5 tokens `myT`. He creates an unbalanced transaction `tx` that
has extra 10 Ada, but is short 5 `myT`.
Any counterparty that sees this transaction can create a top-level
transaction `tx'` that includes `tx` as a sub-transaction. The transaction
`tx'` would have extra 5 `myT`, and be short (missing) 10 Ada. Implementing nested transactions 
will allow users to build sub- and top-level-transactions that achieve this swap without 
the need for interacting with a smart contract.

**DEX aggregators.** A DEX aggregator aggregates multi-party swaps, often using its
own liquidity to complete favourable trades. The mechanism for achieving this using nested transactions
is the same as it is for atomic swaps, but a single may include many more transactions in a
top-level transaction.

**Babel fees.** A Babel fee-type transaction is a specific instance of the first use case. A user creates a sub-transaction `tx`
where the missing assets are necessarily a
quantity of Ada. In particular, it does not pay its own fees, collateral, or cover any new `minUTxOValue`s. 
The counterparty creates a top-level transaction which includes `tx` as a sub-transaction and includes 
extra Ada which goes towards paying transaction fees, collateral, etc.

**DApp fee and min-UTxO sponsorship.** A DApp may choose to subsidize the cost of its use 
(e.g. by paying the cost of ExUnits, paying fees/minUTxO, and providing collateral) for the 
purposes of encouraging users to interact with it. Implementing nested transactions 
will allow building transaction batches that subsidize 
DApp-using sub-transactions in this way.

## Specification

For the Agda specification prototype built on top of the current ledger spec,
see [Agda spec](https://github.com/IntersectMBO/formal-ledger-specifications/compare/polina-nested-txs).

### Transaction structure changes

We add the following new field to `TxBody` :

1. `subTxs :: [SubTx]`
-  sub-transactions in the batch

2. We also need implementation of the [CIP-112 - Observe script type](https://github.com/cardano-foundation/CIPs/pull/749) in order to allow sub-transactions to require scripts to be executed at the top level with all sub-transactions in their context. "Observe script type" is called "Guard script type in the Ledger implementation, therefore going forward we will use term "gurads", instead of "observers", while refering to the same concept.

### Plutus

#### New version

A new Plutus version, `PlutusV4`, will be required, since the constraints on what it means for
a transaction to be valid, as well as the transaction structure itself, are changed. Top-level transactions with no sub-transactions are still able to interact
with prior versions of Plutus scripts, as they will be completely backwards compatible. Transactions that are partially valid and/or using any new features
introduced here are not. That is, transactions containing sub-transactions or top-level guards
cannot run scripts with `PlutusV3` or earlier version.

#### TxInfo

The `TxInfo` shown to a PlutusV4 script has an added field :

- `txInfoSubTxs :: [SubTxInfo]`, which is populated with the `SubTxInfo` data for all sub-transactions in the batch
whenever both hold : (1) the transaction for which info is being constructed is top-level, and (2) the script purpose for
which this info is constructed is `Guard` from [CIP-112](https://github.com/cardano-foundation/CIPs/pull/749).

### Changes to Transaction Validity

Key points about transaction validity are as follows :

1. Sub-transactions are not allowed to contain sub-transactions themselves (enforced during deserialization, see [CDDL section](#CDDL)).

2. Sub-transactions are not allowed to contain collateral inputs or collateral return output (enforced during deserialization, see [CDDL section](#CDDL)). Only the top-level transaction is allowed to (furthermore, obligated to)
provide sufficient collateral for all scripts that are run as part of validating all sub-transactions in that batch. If any script in a
batch fails, none of the transactions in the batch are applied, only the collateral is collected.

3. Sub-transactions are not allowed to specify the fee, since the final fee will depend on the complete batch and the top-level transaction (enforced during deserialization, see [CDDL section](#CDDL)).

4. Transactions using new features are not allowed to run scripts of PlutusV3 or earlier.

5. All scripts are shared across all transactions within a single batch, so attaching one script to either a sub- or a top-level-transaction
allows other transactions to run it without also including it in its own scripts. This includes references scripts that are sourced from the
outputs to which reference inputs point in the UTxO. These referenced UTxO entries could be outputs of preceding transactions in the batch.
Datums (both from reference inputs and ones attached to other transactions) are also shared in this way. As before, only the datums fixed by the
executing transaction are included in the `TxInfo` constructed for its scripts, however, now they don't necessarily have to be attached to
that transaction.

6. All inputs of all transactions in a single batch must be contained in the UTxO set before any of the
batch transactions are applied. This ensures that operation of scripts is not disrupted, for example, by
temporarily duplicating thread tokens, or falsifying access to assets via flash loans.
In the future, this may be up for reconsideration.

7. The batch must be balanced (POV holds). The updated `produced` and `consumed` calculations sum up the appropriate
quantities not for individual transactions, but for the entire batch, including the top-level and its sub-transactions.

8. The total size of the top-level transaction (including all its sub-transactions) must be less than the `maxTxSize`.
This constraint is necessary to ensure efficient network operation since batches will be transmitted wholesale across the Cardano network.

### Collateral and Phase-2 Invalid Transactions

Enough collateral must be provided by the top-level transaction to cover the sum of all the
execution units of all Plutus scripts in sub-transactions and top level transaction.
The sub-transactions will not be able to supply collateral for their own scripts.

Same as previously, it is important to first perform a phase-1 validation for the full transaction, including all of its sub-transactions, before executing any Plutus scripts. In other words phase-2 validation is performed for the full transaction as the last step of validation, instead of on per sub-transaction basis. This part is critical for the safety of the mempool, in order to prevent an attack where many invalid transactions are submitted with very expensive scripts.

### Required Top Level Guards

[CIP-112](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0112) introduces Guards, which are arbitrary scripts that can be required by the transaction builder. It seems natural to tap into this functionality to allow sub-transaction builders to require arbitrary scripts to be executed at the top-level as well. In order to achieve that, sub-transactions will have a new field `requiredTopLevelGuards`, which will not be available in the top level transaction. The only enforcement that Ledger will have to do is to make sure that script hashes listed in that field are also present in the list of Guards in the top-level transaction. It will be the responsibility of the top level transaction builder to satisfy this requirement by adding all of the required guards from sub-transactions in the top level transaction. Moreover, in case when required guard is a plutus script, top level transaction builder will have to supply the redeemr for that script.

Sub-transaction builders might not have access to the full transaction until their sub-transaction is included on chain, therefore they will not be able to provide executions units for those top level guards they require. However, they will need ability to provide an argument to such scripts. For this reason this field will look like this:

```haskell
  requiredTopLevelGuards :: [(ScriptHash, Data)]
```

In other words, the data, which will be passed when script gets executed, will be supplied by sub-transaction together with the hash of that script.

One of the properties that is applicable only to the guard scripts in the top level transaction, when comparing to other type of scripts in a transaction, is that they will be able to see the full transaction in their context, including all of the sub-transactions. These are the only scripts that, in their `TxInfo` data, get a non-empty `txInfoSubTxs :: [SubTxInfo]` field, which is populated with the infos of the sub-transactions.

By taking this approach, we provide the means for sub-transaction builders to require scripts that will have access not only to their own sub-transaction they are building, but also to the top level transaction and all other sub-transactions it will include.

### System Component Changes

#### CDDL

The changes to the CDDL specification are as follows :

```cddl
;; CIP-112
guards = nonempty_set<addr_keyhash>
       / nonempty_oset<credential>

transaction_body =
  {   0  : set<transaction_input>
  ,   1  : [* transaction_output]
  ,   2  : coin
  , ? 3  : slot_no
  , ? 4  : certificates
  , ? 5  : withdrawals
  , ? 7  : auxiliary_data_hash
  , ? 8  : slot_no
  , ? 9  : mint
  , ? 11 : script_data_hash
  , ? 13 : nonempty_set<transaction_input>
  , ? 14 : guards
  , ? 15 : network_id
  , ? 16 : transaction_output
  , ? 17 : coin
  , ? 18 : nonempty_set<transaction_input>
  , ? 19 : voting_procedures
  , ? 20 : proposal_procedures
  , ? 21 : coin
  , ? 22 : positive_coin
  , ? 23 : [+ sub_transaction] ;; new field
  }

sub_transaction =
  [sub_transaction_body, transaction_witnesses, auxiliary_data / nil]

;; Missing `fee`, `collateral` and `collateral return output`, when comparing to `transaction_body`
sub_transaction_body =
  {   0  : set<transaction_input>
  ,   1  : [* transaction_output]
  , ? 3  : slot_no
  , ? 4  : certificates
  , ? 5  : withdrawals
  , ? 7  : auxiliary_data_hash
  , ? 8  : slot_no
  , ? 9  : mint
  , ? 11 : script_data_hash
  , ? 14 : guards
  , ? 15 : network_id
  , ? 17 : coin
  , ? 18 : nonempty_set<transaction_input>
  , ? 19 : voting_procedures
  , ? 20 : proposal_procedures
  , ? 21 : coin
  , ? 22 : positive_coin
  , ? 24 : [+ required_top_level_guard] ;; new field
  }

required_top_level_guard = [credential, plutus_data / null]
```

### Network and Consensus Changes

With this design, there are no changes to these components at all.

### Cardano CLI

Tools for building transactions will need to introduce ability to build sub-transactions in
isolation and ability include sub-transactions into the top level transaction.

### Off-Chain Component Architecture

Partially valid transactions cannot be communicated across the Cardano
network or stored in the mempool. This must be done off-chain.
This CIP does not include an off-chain component, even though one would be necessary
for

- communicating,
- storing, and
- matching

such transactions. The reason
for this is that different usecases may require different off-chain architecture.
In particular, different usecases will have specific configurations of the
kinds of transactions or requests they are interested in engaging with.
For example, an individual user may care only about offers of a specific token.
An exchange may care about offers of any popular
asset at a good price.

Most importantly, off chain component does not have to be open source, nor distributed and can be used to build a for-profit business around it.


#### Babel Service

A Babel service is the catch-all name we use here to refer to a service that is interested
in engaging with partially valid unbalanced transactions. Communication channels between such services and users constructing
unbalanced transactions are required. Such a service can be run by anyone, probably
alongside a full node. It would have to have a filter set for the kinds of transactions
it will engage with. There is no guarantee that every unbalanced sub-transaction
will ever make it on chain, since there is no guarantee that it will be eventually balanced by a subsequent incoming sub-transaction. So, each service will have
to solve this problem for themselves, probably using an appropriate filter.

#### Required Top level Guards

A service processing partially valid transactions (such as the Babel service) may accept incoming transactions
that contain non-empty `requiredTopLevelGuards`. This means this service must construct batches containing these
transactions and also satisfy the batch-level constraints imposed by these scripts being included in the `guards` field of the top level transaction.

An additional high-level language may be beneficial to specify what the guard scripts
actually require of the batch, as Plutus script constraints may be difficult to work with directly.

## Rationale: how does this CIP achieve its goals?

The primary purpose of this CIP is to enable Cardano node support for a specific kind of transaction 
batching which we call *nested transactions*. The specification we presented includes the features 
discussed in the [Motivation section](#Motivation). In particular, it allows the individual 
sub-transactions inside batches (top-level transactions) to be unbalanced, and to not
be obligated to pay fees or provide collateral, while still ensuring the preservation of 
value property and a functioning collateral mechanism at the batch level. 
This is the main property required to securely support the use cases 
discussed in the [Motivation section](#Motivation).

**Pseudo-code example**. To give a more detailed illustration of how the specification changes presented 
in this CIP support use cases and features discussed in the [Motivation section](#Motivation), we present the following 
pseudocode example :

```
tx =
  Body
  { inputs = [txIn0:FOO 5]
  , outputs = [txOut:ADA 9]
  , fee = 1 ADA
  , subTx =
     [ Tx
       { body = Body
         { inputs = [txIn00:FOO 95]
         , outputs = [txOut00:ADA 200]
         , requiredTopLevelGuards = [(scriptHash0, data00)]
         }
         Wits {
          redeemers = [(RedeemerPtr Spending 0, (exUnits000, data000))]
          scripts = [spendingScript00]
        }
       }
     , Tx
       { body = Body
         { inputs = [txIn10:ADA 210]
         , outputs = [txOut10:FOO 100]
         , requiredTopLevelGuards = [(scriptHash0, data10), (scriptHash1, data11)]
         }
       }
         Wits {
          redeemers = [(RedeemerPtr Spending 0, (exUnits100, data100))]
          scripts = [spendingScript10, guardScript1]
        }
     ]
  , guards = [scriptHash0, scriptHash1]
  }
  Wits {
   redeemers = [ (RedeemerPtr Guard 0, (exUnits0, data0))
               , (RedeemerPtr Guard 1, (exUnits1, data1))
               , (RedeemerPtr Spending 0, (exUnits2, data2))
               ]
   scripts = [guardScript0, spendingScript0]
  }
```

This example showcases the following use cases and features :

- performing a swap of 95 `FOO` for 200 `ADA` (this amount includes the counterparty paying for the transaction fee of the swap-offer transaction)

- top level transaction builder is paying the fee with a multi asset (aka Babel fee)

- execution of scripts at all levels, i.e. `spendingScript00` and `spendingScript10` for sub-transactions, and `guardScript0`, `guardScript1`, `spendingScript0` for top-level transaction.

The top-level transaction executes a spending script `spendingScript0`, which is not given `txInfoSubTxs`, and two
guard scripts, `guardScript0`, `guardScript1`, which do get to see `txInfoSubTxs`. No sub-tx scripts
(`spendingScript0` and `spendingScript1`) get to see `txInfoSubTxs` or the top level transaction, they only see their own respective sub-transaction in the `TxInfo`.

- Sub-transaction supplies `guardScript1` for the top level execution, while `guardScript0` is supplied in the top level transaction witnesses. This serves as the example of irrelevance of where the scripts are coming from, as long as they are supplied by someone.

- Both sub-transactions require execution of the same `guardScript0` script, which is executed only once with all the arguments supplied to it, instead of executing it as many times as it appears in sub-transactions.

### Comparison with Other Designs

#### CIP-0131 "[Transaction Swaps](https://github.com/cardano-foundation/CIPs/pull/880)"

Transaction swaps achieve almost exactly the same goals as this CIP. The main differences
are :

1. The top-level transaction contains subTxs, which
are lists of transactions. They are processed as individual transactions, alongside the top-level tx. As a result,

- the `TxIn` of each output can be computed for each output partially valid transaction
at the time of construction

- the `TxId` of the transaction for each entry in the UTxO set is necessarily
signed by all the keys required by that transaction

- the input to (and therefore output of) each script is predictable at the time of (partially valid) tx construction,
so that it is possible to compute required `ExUnits` for each of the scripts run by every sub-transaction
at the time of construction

2. Contracts can only view data in the transaction running them, except in the case
that a top-level tx is running a guard script

3. In this design, script outputs (except of guards) can be computed by any Babel service receiving an incoming
partially valid transaction (as well as the author of the transaction), and they do not depend on the top-level transaction.
This makes constructing (and determining whether it is even possible to construct)
a valid top-level transactions more straightforward.


#### CIP-0118 "Validation Zones-implicit"

The key difference between the Validation Zones-implicit design and this design is that
this design does not require any changes to be made to the operation
of the mempool. This is achieved by building a top-level transaction that includes
a list of sub-transactions, rather than modifying block structure to contain
such lists of transactions directly. Also, this design allows `ExUnits` to be specified by the top-level transaction for
sub-transactions.


## Path to Active

### Acceptance Criteria

- [ ] Deployment to testnet/mainnet

### Implementation Plan

- [ ] Update to the formal ledger specification with the changes proposed here
- [ ] Implement the outlined changes in the Cardano node 
- [ ] Complete a hard fork enabling support for the changes outlined here
- [ ] Track implementation of this CIP via top level ticket on the Ledger repository, including links to implementations: [Nested Transactions](https://github.com/IntersectMBO/cardano-ledger/issues/5123)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
