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
with insufficient fees. The missing value or data must be provided by a subsequent 
transaction. Such partially valid transactions, which are called sub-transactions,
must be placed into batches by aggregators. 
The batch must also include a _top-level_ transaction. The completed batch must be fully balanced.
Applying a complete batch results in a valid ledger update, 
however, applying each of the individual transactions may not. This scheme allows users 
to make and accept swap offers without the need for a centralized exchange or two-way communication.
It gives non-ada holders a way to engage with the Cardano ecosystem. It also creates new business opportunities 
for users willing to make and accept offers, run aggregator services, subsidize the use of their Dapps, etc.

## Motivation: why is this CIP necessary?

This CIP provides a partial solution to the problems described in 
[CPS-15](https://github.com/cardano-foundation/CIPs/pull/779).
In particular, it describes some ledger changes that allow settlement
of intents that require *counterparty irrelevance*, including many of the swap use cases
and dApp fee sponsorship. *Counterparty irrelevance* is a property of a transaction batching protocol 
wherein a transaction author is not required to approve the batch into which the 
transaction will be included, and that decision can be made autonomously by the batcher.
This property allows batches to be made with one-way communication (i.e. broadcast) only. 

The motivation behind designing this solution is _Babel fees_,
which is a requirement to support "paying transaction fees in a non-Ada currency".
The Babel-fees usecase is a special case of a swap. Supporting swaps is very desirable functionality for cryptocurrency
ledgers.

There are off-chain solutions being developed for the purpose of achieving the same 
(major) goals, including fee coverage, atomic swaps, DApp fee sponsorship, 
collateral sponsorship, etc. This gives us indication that it is a worthy pursuit 
to solve this problem at the ledger level, in a way that is cheaper, more convenient, 
maintains formal guarantees, requires less off-chain communication, and does not require deposits or interaction 
with smart contracts. 

The ledger changes we describe have been developed as a result of the discussions and 
proposals in previous CIPs, including previous versions of validation zones proposals, 
and Transaction Swaps. The following 
new usecases and functionality are supported by the changes :

1. transactions can be batched
- batch contains one top-level transaction, with multiple possible sub-transactions ;

2. the batch must be balanced, but individual transactions in it do not have to be, so 
- transactions in a single batch may pay each others' fees and minUTxOValue ;
- unbalanced transactions can be interpreted as swap offers, getting resolved within a complete batch ;

3. scripts are shared across all transactions in a single batch 
- enables script deduplication ;

4. batch observer scripts enable sub-transactions to specify properties required of batches in which they may be included 
- design inspired by script observers ;
- allows all transaction authors the impose constraints
on the batches into which their transactions are added, despite the fact that they do no get to approve 
the final batches (i.e. counterparty irrelevance) ;

5. the top-level transaction must provide collateral for all scripts in its sub-transactions 
- sub-transactions are not required to cover their own collateral ;

We note that the functionality added by (4) makes it possible to view each transaction as on *intent* 
to perform a specific action (whose fulfillment within the batch is ensured by the validation of the batch observer script). 
The types of intents supported by this are ones that *do not require
the relaxation of existing ledger rules*. That is, a user can specify any intent the rest of the batch 
must satisfy without violating existing ledger rules. Adding support for intents that *do require ledger rule relaxations*, such 
the ones in (2, 3, 5) above, must be done 
more carefully to ensure secure operation of the ledger program.  


## Specification

For the Agda specification prototype built on top of the current ledger spec, 
see [Agda spec](https://github.com/IntersectMBO/formal-ledger-specifications/compare/polina-nested-txs).

### Missing and extra assets 

For a given transaction body, let `produced` and `consumed` be the produced and consumed 
values, respectively. Then

extra assets/currency `:= { aid ↦ v | aid ↦ v ∈ consumed - produced , v > 0 }`

missing assets/currency `:= { aid ↦ v | aid ↦ v ∈ produced - consumed , v > 0 }`

### Transaction structure changes

We add the following new fields to `TxBody` : 

1. `requireTopLevelObservers : ScriptHash ⇀ Data`
- set of scripts that must be run by the top-level transaction in the batch (where `TxInfo` includes info of all batch transactions), 
together with the associated data they are provided by the transaction author that is requiring them to be run

2. `subTxs : ℙ TxId`
-  sub-transactions in the batch

### Plutus

#### New version

A new Plutus version, `PlutusV4`, will be required, since the constraints on what it means for 
a transaction to be valid, as well as the tx structure itself, are changed. Transactions 
that are top-level transactions with no sub-transactions are still able to interact 
with V3 scripts. Transactions that are partially valid and/or using any new features 
introduced here are not. That is, transactions containing sub-transactions or top-level observers
cannot run PlutusV3 scripts.

#### New script purposes

The following two new script purpose is introduced (together with script purpose tags with the same names) : 

1. `TopLevelObservers : (TxId x ScriptHash) → ScriptPurpose`, where 
- the `TxId` indicates the transaction requesting the script to be run, and 
- the `ScriptHash` of the script that must be run as the top-level observer 

#### TxInfo

The `TxInfo` shown to a PlutusV4 script has an added field :

- `subTxInfos : List TxInfo`, which is populated with the `TxInfo` data for all sub-transactions in the batch 
whenever both hold : (1) the transaction for which info is being constructed is top-level, and (2) the script purpose for 
which this info is constructed is `TopLevelObservers`.

### Changes to Transaction Validity

Key points about transaction validity are as follows :

1. Sub-transactions are not allowed to contain sub-transactions themselves.

2. Sub-transactions are not allowed to contain collateral inputs. Only the top-level transaction is allowed to (furthermore, obligated to)
provide sufficient collateral for all scripts that are run as part of validating all transactions in that batch. If any script in a 
batch fails, none of the transactions in the batch are applied, only the collateral is collected.

3. Transactions using new features are not allowed to run scripts of PlutusV3 or earlier.

4. All scripts are shared across all transactions within a single batch, so attaching one script to either a sub- or a top-level-transaction 
allows other transactions to run it without also including it in its own scripts. This includes references scripts that are sourced from the 
outputs to which reference inputs point in the UTxO. These referenced UTxO entries could be outputs of preceding transactions in the batch. 
Datums (both from reference inputs and ones attached to other transactions) are also shared in this way. As before, only the datums fixed by the 
executing transaction are included in the `TxInfo` constructed for its scripts, however, now they don't necessarily have to be attached to 
that transaction.

5. All inputs of all transactions in a single batch must be contained in the UTxO set before any of the 
batch transactions are applied. This ensures that operation of scripts is not disrupted, for example, by 
temporarily duplicating thread tokens, or falsifying access to assets via flash loans.
In the future, this may be up for reconsideration. 

6. The batch must be balanced (POV holds). The updated `produced` and `consumed` calculations sum up the appropriate 
quantities not for individual transactions, but for the entire batch, including the top-level and its sub-transactions.

7. All transactions (sub- and top-level) may specify a non-zero fee. The total fee summed up across all transactions in 
a batch is required to cover the minimum fees of all transactions. The fees specified in all transactions are always collected. 
Individual transactions in a batch do not need to meet the min-fee requirement.

8. The total size of the top-level transaction (including all its sub-transactions) must be less than the `maxTxSize`. 
This constraint is necessary to ensure efficient network operation since batches will be transmitted wholesale across the Cardano network.

### Collateral and Phase-2 Invalid Transactions

Enough collateral must be provided by the top-level transaction to cover the sum of all the 
fees of all batch transactions. The collateral 
can only ever be collected from the top-level transaction.
The sub-txs are not obligated to provide sufficient 
collateral for their own scripts. Moreover, they are not allowed to have non-empty collateral.

**NOTE** The Agda specification performs phase-1 checks followed by phase-2 checks for each 
transaction (i.e. for sub- and top-level-). If a phase-1 check fails after some scripts for previous 
transactions in a batch have already been run, the entire batch is invalid, but the executed scripts 
are not paid for with collateral. That means that modifications need to be made in the Haskell implementation 
to ensure that scripts are only run after phase-1 checks are successful for all transactions in a given batch.

### Batch Observers 

Batch observers are scripts that must be run by a top-level transaction, but may be required by its sub-transactions 
as a way to specify batch-level constraints. The have the script purpose with the tag `TopLevelObservers` and the identifier `ScriptHash`.
These are the only scripts that, in their `TxInfo` data, get a non-empty `subTxInfos : List TxInfo` field, which is populated 
with the infos of the sub-transactions. This is inspired by, and may be implemented in conjunction with the 
[Observe Script Type CIP](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0112). However, this CIP is not 
necessary for Nested Transactions.

The difference is that for a tx-observer script in the linked CIP is run on the `TxInfo` of the transaction 
that requires it. With batch observers, the scripts are required by a sub-tx, but run with top-level input. 
For the same top-level transaction, a regular observer and a batch observer in a transaction will get different `TxInfo`. 

Batch observers are a way to specify any intents that to not require changes to the ledger rules. For example, 
I may include a payment in my sub-transaction to specific address, and require via a batch observer that 
any transaction that completes this 
batch must execute some particular script. In this case, my intent is to get a party to interact with that contract. 

### System Component Changes

### Ledger

The ledger changes follow the specification changes outlined above.
The ledger prototype introducing the new era containing 
the changes as described in the specification can be found [here](https://github.com/willjgould/cardano-ledger/tree/wg/babel-rework).

#### CDDL

See [CDDL](https://github.com/willjgould/cardano-ledger/blob/wg/babel-rework/eras/babel/impl/cddl-files/babel.cddl).

The changes to the CDDL specification are as follows :

TODO


### New Plutus Version

The Plutus prototype, changing the 
[context](https://github.com/willjgould/plutus/blob/wg/batch-observers/plutus-ledger-api/src/PlutusLedgerApi/V4/Contexts.hs).
The fork link is [here](https://github.com/willjgould/plutus/tree/wg/batch-observers). 

### Network and Consensus Changes

With this design, it is likely minimal changes will be required if any at all.

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
Some services may be willing to look at the requirements imposed by `requiredTopLevelObservers`, while 
others may not be.


#### Babel Service

A Babel service is the catch-all name we use here to refer to a service that is interested 
in engaging with partially valid unbalanced transactions. Communication channels between such services and users constructing 
unbalanced transactions are required. Such a service can be run by anyone, probably 
alongside a full node. It would have to have a filter set for the kinds of transactions 
it will engage with. There is no guarantee that every unbalanced transaction 
will eventually be balanced by a subsequent incoming one, so each service will have 
to solve this problem for themselves, probably using an appropriate filter.

#### Batch Observers

A service processing partially valid transactions (such as the Babel service) may accept incoming transactions 
that contain non-empty `requiredObservers`. This means this service must construct batches containing these 
transactions and also satisfy the batch-level constraints imposed by the scripts specified in their `requiredObservers` 
in order to create valid batches.

An additional high-level language may be beneficial to specify what the batch observer scripts 
actually require of the batch, as Plutus script constraints may be difficult to work with directly.

## Rationale: how does this CIP achieve its goals?

The primary purpose of this CIP is to enable Babel Fees. Our design allows users to perform arbitrary 
swaps without two-way off-chain communication, and with counterparty irrelevance. This simulates
fee payment in arbitrary currency whenever another use is willing 
to accept the non-primary asset offer in exchange for paying the transaction fee. This is the core 
requirement of Babel fees. In addition, the goal of this design is to lay the groundwork for 
supporting more general intents and the possibility of extending to additional ones. 
We have done so by adding the following set of features :

1. transactions can be batched
- batch contains one top-level transaction, with multiple possible sub-transactions ;

2. the batch must be balanced, but individual transactions in it do not have to be, so 
- transactions in a single batch may pay each others' fees and minUTxOValue ;
- unbalanced transactions can be interpreted as swap offers, getting resolved within a complete batch ;

3. script data is shared across all transactions in a single batch 
- enables script deduplication ;

4. batch observer scripts enable sub-transactions to specify properties required of batches in which they may be included 
- design inspired by script observers ;
- represents all possible intents that do not require ledger rule relaxation ;

5. the top-level transaction must provide collateral for all scripts in its sub-transactions 
- sub-transactions are neither required nor allowed to cover their own collateral ;


## Use cases

### Open (atomic) swaps

A user wants to swap 10 Ada for 5 tokens `myT`. He creates an unbalanced transaction `tx` that 
has extra 10 Ada, but is short 5 `myT`. 
Any counterparty that sees this transaction can create a top-level 
transaction `tx'` that includes `tx` as a sub-transaction. The transaction 
`tx'` would have extra 5 `myT`, and be short 10 Ada. 

### DEX aggregators

A DEX aggregator running a Babel service would set its filter to only accept transactions 
trading tokens it is interested in, and are being traded at a favourable price. 
It may or may not require incoming transactions to cover their own fees and/or collateral. 
In the case a set of sub-transactions is not fully balanced, and the aggregator is interested 
in participating in the exchange offers within the batch, it would have to include its own 
liquidity pool as one of the inputs 
in the top-level transaction, and output any extra tokens to its updated liquidity pool UTxO.  

### Babel fees

Babel fees is a specific subtype of the first usecase where the missing assets are necessarily
a quantity of Ada. Usually, it also implies that no Ada is contained in the inputs
of such a transaction, and the missing Ada goes towards paying transaction fees.


### DApp fee and min-UTxO sponsorship

DApp may run a Babel service which only cares only about transactions interacting with a 
certain DApp, discarding all other incoming transactions immediately. This service 
may include calculating ExUnits, paying fees/minUTxO for, and providing collateral for such 
partially valid transactions. 

## Pseudo-code Example 

```
tx =
  Body
  { inputs = [txIn0:FOO 5]
  , outputs = [txOut:ADA 5]
  , fee = 5 ADA
  , subTx =
     [ Tx
       { body = Body
         { inputs = [txIn00:FOO 95]
         , outputs = [txOut00:ADA 200]
         , requiredObservers = [(scriptHash0 , data01)]
         }
         Wits {
          redeemers = [ (RedeemerPtr Spending 0, (exUnits000, data000))
                      ]
          scripts = [ spendingScript0 ]
        }
       }
     , Tx
       { body = Body
         { inputs = [txIn10:ADA 210]
         , outputs = [txOut10:FOO 100]
         , requiredObservers = [(scriptHash0 , data0) , (scriptHash1 , data1)]
         }
       }
         Wits {
          redeemers = [ (RedeemerPtr Spending 0, (exUnits101, data111))
                      ]
          scripts = [ spendingScript1 ]
        }
     ]
  }
  Wits {
   redeemers = [ (RedeemerPtr BatchObserver 0, (exUnits100, data100))
               , (RedeemerPtr BatchObserver 1), (exUnits10, data10)
               , (RedeemerPtr Spending 0, (exUnits0, data0))
               ]
   scripts = [observerScript0 , observerScript1 , spendingScript2]
  }
```

This example it captures couple of different uses cases:

- performing a swap of 95 `FOO` for 200 `ADA` (this amount includes the counterparty paying for the transaction fee of the swap-offer transaction)

- top level transaction builder is paying the fee with a multi asset (aka Babel fee)

- execution of scripts at all levels, i.e. `spendingScript0` and `spendingScript1` for sub-txs, and `observerScript0 , observerScript1 , spendingScript2` for top-level transaction.

The top-level transaction executes a spending script `spendingScript2`, which is not given `subTxInfos`, and two 
batch observer scripts, `observerScript0 , observerScript1`, which do get to see `subTxInfos`. No sub-tx scripts 
(`spendingScript0` and `spendingScript1`) get to see `subTxInfos`.

## Comparison with Other Designs

### CIP-0131 "[Transaction Swaps](https://github.com/cardano-foundation/CIPs/pull/880)"

Transaction swaps achieve almost exactly the same goals as this CIP. The main differences 
are :

1. The top-level transaction contains subTxs`, which 
are lists of transactions. They are processed as individual transactions, alongside the top-level tx. As a result, 

- the `TxIn` of each output can be computed for each output partially valid transaction  
at the time of construction 

- the `TxId` of the transaction for each entry in the UTxO set is necessarily 
signed bt all the keys required by that transaction

- the input to (and therefore output of) each script is predictable at the time of (partially valid) tx construction, 
so that it is possible to compute required `ExUnits` for each of the scripts run by every sub-transaction 
at the time of construction

2. Contracts can only view data in the transaction running them, except in the case 
that a top-level tx is running a batch-observer script

3. In this design, script outputs (except of batch-observers) can be computed by any Babel service receiving an incoming 
partially valid transaction (as well as the author of the transaction), and they do not depend on the top-level transaction.
This makes constructing (and determining whether it is even possible to construct) 
a valid top-level transactions more straightforward. 


### CIP-0118 "Validation Zones-implicit"

The key difference between the Validation Zones-implicit design and this design is that 
this design does not require any changes to be made to the operation
of the mempool. This is achieved by building a top-level transaction that includes 
a list of sub-transactions, rather than modifying block structure to contain 
such lists of transactions directly. Also, this design allows `ExUnits` to be specified by the top-level transaction for 
sub-transactions.


## Path to Active

### Software Readiness Level

It is difficult to specify the SRL for this CIP because it effects each component
of the Cardano node. The kind of testing required to thoroughly analyze the
changes we propose can only be done on testnet. We estimate that the SRL
would remain between 3 and 6 until

- an era is specified into which this feature is included
- a testnet containing this feature is launched

### Acceptance Criteria

- The use cases as described here can be implemented and tested on a testnet

### Implementation Plan

- Implementation of the proposed ledger changes in the formal ledger spec
- Updated CIP Specification with full detail
- Community acceptance through Intersect
- Implementation in the Cardano node in the context of a new era/hardfork
- Deployment to testnet/mainnet

## Links to implementations




## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
