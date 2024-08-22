---
CIP: 118
Title: Nested Transactions
Category: Ledger
Status: Proposed
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>  
    - Will Gould <will.gould@iohk.io>
    - Alexey (if he wants!)
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/780
    - https://github.com/cardano-foundation/CIPs/pull/862
    - https://github.com/cardano-foundation/CIPs/pull/880
Created: 2024-03-11
License: CC-BY-4.0
---

## Abstract

We propose a set of changes that revolve around validation zones, a construct for allowing
certain kinds of _underspecified transactions_. In particular, for the Babel-fees usecase
we discuss here, we allow transactions that specify
_a swap request_. Underspecified transaction bodies are included in the 
body of a _top-level_ transactions (which may itself be partially specified) alongside
additional required data (e.g. their redeemers). We call the 
set of transactions containing the top-level transaction and the _sub-transactions_
it includes a _batch_. Applying a complete batch results in a valid ledger update, 
however, applying each of the individual transactions may not. For example, insufficient 
fees or collateral may be provided, missing witness info, etc.
In the Babel-fees usecase, transactions do not 
need to be balanced, i.e they do not require specifying where any missing funds come from, 
or any extra funds go. A complete batch, however, must be balanced.

## Motivation: why is this CIP necessary?

This CIP provides a partial solution to the problems described in 
[CPS-15](https://github.com/cardano-foundation/CIPs/pull/779).
In particular, it describes some ledger changes that allow intent settlement
of intents that require “counterparty irrelevance”, including many of the swap use cases
and dApp fee sponsorship. The motivation behind designing this solution is _Babel fees_,
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

1. transactions in a single batch may pay each others' fees and `minUTxOValue` ;
2. sharing (for the purpose of deduplication) of scripts and datums across transactions 
in a single batch ;
3. scripts may inspect the contents of other transactions within the same batch ;
4. the top-level transaction may provide collateral (and, optionally, the `ExUnits`
for the scripts in its sub-transactions) ;
5. a new intent we call "spend-by-output", wherein a sub-transactions may specify _outputs_ it 
intends to spend, and the top-level transaction specifies the inputs that point 
to those outputs in the UTxO set. This is included as a way to showcase that this 
change to the ledger rules establishes the infrastructure to add additional 
kids of supported intents (see CPS-15).

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

1. `isTopLevel : Bool`\
- whether or not a give transaction is top-level (set by builder of top level Tx)

2. `subTxs : ℙ TxId `\
- fixes all attached sub-transactions

3. `requiredTxs : ℙ TxId`\
- fixes what transactions will be shown to plutus scripts being run by this transaction 

4. `spendOuts : List TxOut`\
- outputs being spent for which inputs are provided by top-level tx

5. `corInputs : ℙ TxIn`\
- inputs corresponding to `spentOuts`

6. `knowsOwnUnits : Bool`\
- toggles whether the sub-tx provides its own `ExUnits` or the top-level tx provides them

7. `subUnits : TxId ⇀ (RdmrPtr  ⇀ ExUnits)`\
- units for sub-txs (needed when they do not provide their own)

We define a new record type, `Swap`, which is similar to `Tx` but avoids recursive definition 
of `Tx` as containing a filed made up of other `Tx`s. It has the fields :

1. `stxTxBody : TxBody`\ 
- tx body

2. `stxWits : VKey ⇀ Sig`\
- keys and signatures on the tx body

3. `stxRdmrs : RdmrPtr  ⇀ Redeemer × ExUnits`\
- redeemers for scripts

4. `stxAux : Maybe AuxiliaryData`\
- aux data

The `Swap` record does not contain scripts or datums because those are necessarily provided 
by the top-level tx to avoid duplication.

We add the following new fields to `Tx` : 

1. `subTxBodies : TxId ⇀ Swap`
- sub-transaction data
      
2. `requiredTxBodies : TxId ⇀ TxBody`
- other transactions visible to scripts in this transaction (may be all bodies in `subTxBodies` or only some of them)

### Plutus

#### New version

A new Plutus version, `PlutusV4`, will be required, since the constraints on what it means for 
a transaction to be valid, as well as the tx structure itself, are changed. Transactions 
that are top-level transactions with no sub-transactions are still able to interact 
with V3 scripts. Other transactions are not. 

#### New script purpose

A new tag, `SpendOut`, is introduced. This new constructor, `SpendOut : TxIn → ScriptPurpose`,
 is required to indicate 
that a script is being run to validate spending an output, but it is identified by the input 
provided by another transaction (in the same batch) via `corInputs` (rather than via `txins`).

#### TxInfo

The `TxInfo` shown to a Plutus script is replaced with `List TxInfo` where the first
element is the `TxInfo` of the transaction `tx` whose scripts are being run, and the subsequent
elements in the list are `TxInfo` records for the transactions `tx` scripts are allowed to 
inspect, i.e. those in its `requiredTxBodies`.


### Ledger Transition Changes

The prototype for the changes can be found
[here](https://github.com/IntersectMBO/formal-ledger-specifications/compare/polina-nested-txs)

The transition structure is changed from 

`LEDGERS -> LEDGER -> UTXOW -> UTXO -> UTXOS` 

to 

`LEDGERS -> LEDGER -> SWAPS -> SWAP -> UTXOW -> UTXO -> UTXOS`

**Decision Required** It may be that

`LEDGERS -> SWAPS -> SWAP -> LEDGER -> UTXOW -> UTXO -> UTXOS`

Is a transition order that is closer to the previous usage of these transitions. 


#### `LEDGER` and `LEDGERS`

The transition `LEDGERS` still calls the `LEDGER` transition for each transaction in the given block,
but `LEDGER` does not case split on the `isValid` tag. Instead, `LEDGER` performs
a number of checks that require inspection of the top-level transaction as well as 
the sub-transactions, such as the check that the entire batch is balanced, then 
calls `SWAPS` on the list of transactions in the (constructed) tx batch. The 
checks are :

1. Fees are correct. `feesOK` is modified by (1) replacing `txfee` with 
the sum total of `txfee` values of all the transactions in the batch, and 
the total ExUnits are computed as the sum of all ExUnits in all batch transactions. 
Note that the ExUnits are provided according to `knowsOwnUnits`.
The per-transaction fee is collected only once for the batch. 

2. Batch is balanced when `batchValid` is true. This allows un-balanced batches with failing 
scripts (and sufficient collateral, see [Collateral](#collateral)) to still be posted on-chain. 
Both sides of the equation now sum all of what used to be the 
`produced` and `consumed` values for individual transactions. The value spend by `corInputs` 
is added to the `consumed` side. 

3. Transaction size (which includes top-level and all sub-transactions) is below max for a single transaction

4. All `txins` and `corInputs` are contained in the UTxO set to which the top-level tx is being applied 

5. Check that all required transactions of all batch transactions are present in `subTxs`

6. `isTopLevel` value of top-level transaction is `true`

7. `batchValid` is set the conjunction of all `isValid` tags in the batch.

8. Check that top-level tx provides execution units via `subUnits` for all transactions that don't specify their own execution units

9. The sum of the execution units of all transactions in a batch is less than the max for a single transaction 

10. No `corInputs` provided are also provided as regular `txins` in any transaction

11. Check that `txins` in top-level tx correspond 1-1 to `spendOuts` in the UTxO set

To construct the batch transaction list, the original transaction prepends the 
top-level transaction to a list of transactions corresponding to each of its
swaps, constructed from them in the following way :

1. The body, the signatures, the redeemer pointer structure with redeemers, the 
ExUnits, `isValid`, and the aux data are instantiated as specified in the `Swap`
2. The datums and scripts are instantiated as those of the top-level transaction (TODO FIX THIS!)
3. `subTxBodies` is empty
4. `requiredTxBodies` is *either* populated by the bodies in `subTxBodies` of the top-level 
tx that correspond to `requiredTxs` specified in the swap body
(in the case `knowsOwnUnits` is `true` in the swap body), *or* it is 
populated by *all* bodies in `subTxBodies` (in the case 
`knowsOwnUnits` is `false` in the swap body) 
(see [Setting `knowsOwnUnits`](#setting-knowsownunits))
5. The `rdmrPtr` is *either* the one provided by the `Swap` (in the case 
`knowsOwnUnits` is `true` in the swap body) *or* the replaced the `ExUnits`
(in the case `knowsOwnUnits` is `false` in the swap body) 
(see [Setting `knowsOwnUnits`](#setting-knowsownunits))
6. `isTopLevel` is set to `false`
7. `batchValid` is set to the `batchValid` tag of the top-level tx

TODO - limit the shown datums! these should be fixed by the transaction as they are now. 

**Decision Required** Should we also require scripts to be limited to only required ones?
Or relax this restriction?

#### SWAP and SWAPS

`SWAPS` iterates over all transaction in a batch, calling `SWAP` on each. The rule `SWAP`
functions the way `LEDGER` did, conditioning on the `batchValid` tag to determine whether
certificates and gov-actions need to be applied, then calling `UTXOW` to update the 
UTxO state. 

#### UTXOW 

The `UTXOW` rule additionally checks :

1. all `subTxs` have corresponding swaps attached to the transaction
2. `subTxs` only non-empty in top-level tx

Existing function that checks that required witness data is provided now 
also checks that such data is provided for the `corInputs`. 

TODO : deal with reference inputs correctly?

#### UTXO

The `feesOK` check, as well as the `txsize` and `produced = consumed` checks, 
are removed from this rule (and moved to the `LEDGER` rule). 


#### UTXOS

The function `collectPhaseTwoScriptInputs` that appears in the `UTXOS` constructors 
now receives the `requiredTxBodies` data in addition to own transaction data .
As before, constructor of `UTXOS` checks that `isValid` is correctly specified based 
on script execution output.

The `UTXOS` rule is updated to have three constructors :

1. `Scripts-Yes` : in the case that `batchValid` is true, it removes both the 
`txins` and the `corInputs` from the UTxO set (in addition to all the existing 
changes done previously by `Scripts-Yes`).

2. `Scripts-No` : in the case `batchValid = false`, and `isTopLevel = false`.
No changes are made to the state here because collateral is only collected from the top-level transaction.

3. `Scripts-No-TopLevel` : in the case `batchValid = false`, but `isTopLevel = true`.
Collateral is collected, as in the previous version of the `Scripts-No` rule. 

### Setting `knowsOwnUnits`

This tag is set within the transaction body to specify whether `ExUnits` for running 
scripts are correctly specified in the `rdmrPtr` structure. Setting it to `false` 
will require that the top-level transaction provides the `ExUnits` via the 
`subUnits` structure. When this tag is `false` for a given sub-tx, it will 
also receive data for all of `subTxs` via the `requiredTxBodies`, which is 
given as input to script validation for that sub-tx.

The purpose of this is to allow a given sub-tx to case split on all of the other 
batch transaction data without having to specify which transactions scripts 
will inspect during validation (e.g. via listing all the txIds
of the transaction bodies that will be viewed).

### Collateral

Enough collateral must be provided by the top-level transaction for the sum of all the 
fees of all batch transactions. The collateral 
can only ever be collected from the top-level transaction.
The sub-txs are not obligated to provide sufficient 
collateral for their own scripts, but they may choose to. A Babel fees service [Babel Service](#babel-service)
may or may not require incoming underspecified transactions to provide their 
own collateral, depending on whether they want to assume the risk of not being 
compensated for running failing scripts. 

### System Component Changes

### Ledger

The ledger changes follow the specification changes outlined above.
The ledger prototype introducing the new era containing 
the changes as described in the specification can be found here.
TODO fix this link

#### CBOR

...

### New Plutus Version

TODO : Link to prototype.


### Network and Consensus Changes

Probably not much?

### Off-Chain Component Architecture

Underspecified transactions cannot be communicated across the Cardano 
network or stored in the mempool. This must be done off-chain.
Data should probably be sent as `Tx`, rather than a 
`Swap`, because it should include any associated scripts and datums. In the 
reset of the off-chain discussion, we assume `Tx` data is communicated off-chain, 
then turned into a `Swap` to be posted as a sub-tx, or as-is if it is posted 
as a top-level tx. 

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
A light client server cares about transactions that do not specify their own inputs,
and instead specify `spendOuts`. An exchange may care about offers of any popular 
asset at a good price. 

Moreover, different usecases may have different constraints on how "valid"
they expect the underspecified transactions to be. Some may require that 
incoming transactions are valid in every way except possibly un-balanced.
Others may be willing to provide collateral for any (correctly constructed)
transactions with correct `ExUnits`. Yet others may be willing to take on the risk of computing the 
`ExUnits` for the incoming transactions, and specifying them in the top-level tx 
they construct.


#### Babel Service

A Babel service is the catch-all name we use here to refer to a service that is interested 
in engaging with underspecified unbalanced transactions. Communication channels between such services and users constructing 
unbalanced transactions are required. Such a service can be run by anyone, probably 
alongside a full node. It would have to have a filter set for the kinds of transactions 
it will engage with. There is no guarantee that every unbalanced transaction 
will eventually be balanced by a subsequent incoming one, so each service will have 
to solve this problem for themselves, probably using an appropriate filter.

#### Light Client Service

The design outlined here can facilitate a trustless LC service.
Light clients may use the `corInputs` and `spendOuts` features to execute the following protocol.
LC is the light client, and SP is the service provider. We assume there exists a 
high-level language in which a light client can specify what they want a 
transaction constructed for them by the SP to do, e.g. pay `x` amount from my 
wallet to some other wallet, or mint some NFT. 

1. LC -> SP : a high-level specification `s` 
2. SP : construct a `tx` that 
- meets `s`, 
- includes one input `i` from SP's wallet
- includes a payment to SP for light-client services
3. SP : replace all inputs except `i` in `tx` with corresponding `spendOuts` from the UTxO set to make `tx'`
4. SP -> LC : `tx'`
5. LC : checks `tx'` meets `s`, signs it
6. LC -> SP : signed `tx'`
7. SP : constructs top-level `tx''` that provides the `corInputs` for `tx'`
8. SP : submits to Cardano the top-level `tx''` with sub-tx `tx'`

Note that `tx'` may also be unbalanced, simultaneously allowing the LC 
to make a payment in a non-Ada token for the service. This design ensures that 
an LC cannot construct a fully valid transaction from `tx'`, since they do not have access to 
the current UTxO (presumably, if they did, they would construct their own valid transaction).
It also ensures that the SP is paid (in step 2) for their services. 

## Rationale: how does this CIP achieve its goals?

Same as the related CIPs/ motivation. More info here later. 

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
underspecified transactions. 


### Comparison with Other Designs

### CIP-0131 "[Transaction Swaps](https://github.com/cardano-foundation/CIPs/pull/880)"

Transaction swaps achieve almost exactly the same goals as this CIP. The main differences 
are :

1. The top-level transaction contains multiple pieces of data called `Swap`s, which 
are actually transaction bodies paired with other required data (redeemers, etc.).
They can are then converted to `Tx` (by attaching appropriate scripts and datums, etc.),
and processed as individual transactions, alongside the top-level tx. As a result, 

- the `TxIn` of each output can be computed for each output underspecified transaction  
at the time of construction 

- the `TxId` of the transaction for each entry in the UTxO set is necessarily 
signed bt all the keys required by that transaction

- the input to (and therefore output of) each script is predictable at the time of (underspecified) tx construction, 
so that it is possible to compute required `ExUnits` for each of the scripts run by every sub-transaction 
at the time of construction (but it's not compulsory)

2. Contracts can only view data in transactions fixed by `requiredTxs`, rather than 
all sub-txs

3. In this design, script outputs can be computed by any Babel service receiving an incoming 
underspecified transaction, and they do not depend on the top-level transaction, 
this makes constructing (and determining whether it is even possible to construct) 
a valid top-level transactions more straightforward. 


### CIP-0118 "Validation Zones-implicit"

The key difference between the Validation Zones-implicit design and this design is that 
this design does not require as many (any?) major changes to be made to the operation 
of the mempool. This is achieved by building a top-level transaction that includes 
a list of sub-transactions, rather than modifying block structure to contain 
such lists of transactions directly. Also, this design allows `ExUnits` to be specified by the top-level transaction for 
sub-transactions.

### Validation zones for settling other types of intents

We provide the example of the *intent to spend an output* as proof that this nested 
transaction design can support additional intents in the future, as discussed 
in the CPS-15. 


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
