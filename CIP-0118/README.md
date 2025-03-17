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

We propose a set of changes that revolve around nested transactions, a construct for composing
certain kinds of _underspecified transactions_. Such transactions specify an intended action,
but are missing certain data to perform this action. This data must be provided by a subsequent 
transaction. In particular, for the Babel-fees usecase
we discuss here, we allow transactions that are unbalanced, i.e. specify
_a swap_. This intent can be fulfilled by another transaction providing the 
funds requested in the swap (missing in the transaction), and accepting the offered funds
(extra funds in the transaction). Transactions containing intents must be included in  
a _top-level_ transaction. We call the 
set of transactions containing the top-level transaction together with the _sub-transactions_
it includes a _batch_. Applying a complete batch results in a valid ledger update, 
however, applying each of the individual transactions may not. For example, insufficient 
fees or collateral may be provided, missing witness info, etc.

## Motivation: why is this CIP necessary?

This CIP provides a partial solution to the problems described in 
[CPS-15](https://github.com/cardano-foundation/CIPs/pull/779).
In particular, it describes some ledger changes that allow settlement
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

1. transactions can be batched
- batch contains one top-level transaction, with multiple possible sub-transactions ;

2. the batch must be balanced, but individual transactions in it do not have to be, so 
- transactions in a single batch may pay each others' fees and minUTxOValue ;
- unbalanced transactions can be interpreted as swap offers, getting resolved within a complete batch ;

3. script data is shared across all transactions in a single batch 
- enables script deduplication ;

4. batch observer scripts enable sub-transactions to specify properties required of batches in which they may be included 
- design inspired by script observers ;

5. the top-level transaction must provide collateral for all scripts in its sub-transactions 
- sub-transactions are not required to cover their own collateral ;

6. a new intent we call "spend-by-output", wherein a sub-transaction may specify outputs it 
- intends to spend, and the top-level transaction specifies the inputs that point to those outputs in the UTxO set ;
- example of possible additional supported intents (see CPS-15)
potentially useful for LC functionality ;

We note that the functionality added by (4) makes it possible to specify any and all intents that *do not require
the relaxation of existing ledger rules*. That is, a user can specify any intent (action or property) the rest of the batch 
must satisfy without violating existing ledger rules. Adding support for intents that *do require ledger rule relaxations*, such 
the ones in (2, 3, 5, 6) above, must be done 
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

1. `requireBatchObservers : ℙ ScriptHash`
- set of scripts that must be run by the top-level transaction in the batch (where `TxInfo` includes info of all batch transactions)

2. `spendOuts : Ix ⇀ TxOut`
- (indexed) outputs being spent 

3. `corInputs : ℙ TxIn`
- inputs corresponding to `spentOuts`

4. `subTxIds : ℙ TxId`
-  IDs of sub-transactions in the batch

The following field is added to `Tx`:

1.  `subTxs : List Tx` 
- list of sub-transactions

**Note** In the Agda spec, the transaction body contains `subTxIds : ℙ TxId`. The Haskell implementation aligns 
with this to avoid confusion. A better design will be to include the full sub-transactions 
directly in the body of the top-level transaction, making `Tx` a recursive type. 
However, the recursive types design is more difficult to represent in Agda. 

**Note** The era which will include this CIP may be combined with the following additional changes :

- `RdmrPtr ⇀ Redeemer` structure inside the body
- datums inside the body
- `requiredObservers` scripts that are checked by a transaction but are not for the purpose of validating a specific action (see 
[CIP-0112](https://github.com/cardano-foundation/CIPs/pull/749))

### Plutus

#### New version

A new Plutus version, `PlutusV4`, will be required, since the constraints on what it means for 
a transaction to be valid, as well as the tx structure itself, are changed. Transactions 
that are top-level transactions with no sub-transactions are still able to interact 
with V3 scripts. Transactions that are underspecified and/or using any new features 
introduced here are not. 

#### New script purposes

The following two new script purposes are introduced (together with script purpose tags with the same names) : 

1. `SpendOut : Ix → ScriptPurpose`, where the index indicates that a script is being run to validate spending a specific 
output in `spendOuts`.

2. `BatchObs : ScriptHash → ScriptPurpose`, where the script has indicates the script that must be run by the top-level 
transaction to observe the validity of the batch.

`ScriptsNeeded` and `getDatum` are modified accordingly to include scripts for these purposes. `collectPhaseTwoScriptInputs` 
also requires an additional parameter for constructing `TxInfo` to either contain lists of `TxInfo` for sub-transactions or not.

#### TxInfo

The `TxInfo` shown to a PlutusV4 script has an added field :

- `otherInfos : List TxInfo`, which is populated with the `TxInfo` data for all sub-transactions in the batch 
whenever both hold : (1) the transaction for which info is being constructed is top-level, and (2) the script purpose for 
which this info is constructed is `BatchObs`.


### Ledger Transition Changes

The prototype for the changes can be found
[here](https://github.com/IntersectMBO/formal-ledger-specifications/compare/polina-nested-txs)

The transition structure is changed from 

`LEDGERS -> LEDGER -> UTXOW -> UTXO -> UTXOS` 

to 

`LEDGERS -> LEDGER -> SWAPS -> SWAP -> UTXOW -> UTXO -> UTXOS`


#### `LEDGER` and `LEDGERS`

The transition `LEDGERS` still calls the `LEDGER` transition for each transaction in the given block,
but `LEDGER` does not case split on the `isValid` tag. Instead, `LEDGER` performs
a number of checks that require inspection of the top-level transaction as well as 
the sub-transactions, such as the check that the entire batch is balanced, then 
calls `SWAPS` on the list of transactions in the (constructed) tx batch. The 
checks are :

1. Fees are correct. `feesOK` is modified by (1) replacing `txfee` with 
the sum total of `txfee` values of all the transactions in the batch.
The per-transaction fee is collected only once for the batch. 

2. No regular inputs in any transaction are also included as `corInputs` of the top-level tx

3. All `txins` and `corInputs` are contained in the UTxO set to which the top-level tx is being applied 

4. `corInputs` in top-level tx point to the same (unordered) list of outputs in the UTxO set 
as the list given by `spendOuts` 

5. If the batch is not made up of a single transaction with failing scripts, the batch 
must be balanced (POV holds). Both sides of the equation of POV now sum all of what used to be the 
`produced` and `consumed` values for individual transactions. The value spend by `corInputs` 
is added to the `consumed` side.*

6. Transaction size (which includes top-level and all sub-transactions) is below max for a single transaction

7. The sum of the execution units of all transactions in a batch is less than the max for a single transaction 

8. The list of IDs of `subTxs` contains the same IDs as in `subTxIds` 

9. There are no repeating transaction IDs in `subTxs`

(*) By not requiring a single transaction with failing scripts to be balanced, we allow Babel services
to post on-chain phase-1 valid transactions for which they have already used their resources 
to check scripts (and found that one or more failed). Such transactions will be processed by 
collecting collateral only, so none of their other actions, including moving assets, will be applied,
and therefore will not affect the ledger.  

To construct the transaction list representing the complete batch, the original transaction prepends the 
top-level transaction to its `subTx` list.

The `LEDGER` rule then calls the `SWAPS` rule on the batch list, and the same state as it itself 
has. The result of the `LEDGER` state update is computed by `SWAPS`. 
However, the environment for `SWAPS` is distinct from `LEnv` (see below). 

**Batch Information**  We define a new type, `BatchData`, to allow `LEDGER` to indicate to `SWAPS` via its environment
the batch info required for correctly processing it. The type has constructors :

- `SingularTransaction`, which indicates that the batch contains only one transaction with no sub-txs, but this tx contains new features

- `OldTransaction`, which indicates that the batch contains only one transaction with no new features (old version of Plutus can be run)

- `BatchParent txid batchValid` which indicates that this batch contains a top-level tx with ID `txid`, and it has sub-txs. The conjunction of 
all `isValid` tags of all transactions in the batch (sub- and top-) is `batchValid`.

We compute also compute `validPath : BatchData → Tx → Bool`, which 
is true whenever all transactions in the batch are marked as phase-2 valid, or the singular/old transaction 
has a true `isValid`.

**`SWAPS` Environment** `SWAPS` has the same state and signal as `LEDGER`, but it has a distinct environment, `SwapEnv`,
which is set when `LEDGER` calls `SWAPS` :

- `lenv : LEnv` is set to the `LEnv` of the `LEDGER` transition

- `bdat : BatchData` is set to the appropriate computed value as described above 

- `reqObs : ℙ ScriptHash` is set to the `requireObservers` of the top-level transaction

- `bScripts : ℙ Script` is set to the union of all scripts attached to all transactions in the batch

- `valP : Bool` is set to the result of the `validPath bdat tx` computation

**NOTE** Should we also require scripts to be limited to only required ones?
Or relax this restriction? With the restriction, changes to `UTXOW` are required.

**NOTE :** A possible improvement to the design may entail sharing of in-line (reference) scripts and datums across transactions.
This will require collecting all in-line scripts and datums at this stage, and potentially including them in 
the context.

#### SWAP and SWAPS

`SWAPS` iterates over the list of transaction in a batch, calling `SWAP` on each. The transition `SWAP`
does exactly what `LEDGER` used to, except it is conditioned on the `validPath` value it gets in its environment. 
To call the `UTXOW` rule, `SWAP` specifies the signal as the same `tx` that was its signal, and 
sets the (new additional) `UTxOEnv` environment variables as follows

- `bObs : ℙ ScriptHash` to `reqObs` in `SwapEnv`
- `batchData : BatchData` to `bdat` in `SwapEnv`
- `validPath : Bool` to `valP` in `SwapEnv`
- `isTop : Bool` to `True` if batch data is `BatchParent txid batchValid`, and the ID of the signal transaction is equal to `txid`
- `batchScripts : ℙ Script` to `bScripts` in `SwapEnv`

#### UTXOW 

The `UTXOW` rule additionally checks :

1. `requireBatchObservers` is contained in the batch observers (in the environment)

2. no sub-transactions contain sub-transactions.

Other changes include :

- Existing function that checks that required witness data is provided now 
also checks that such data is provided for the `corInputs`. 

- the supported language check requires that `PlutusV3` or earlier is 
only allowed in (singleton) transactions that do not use new features. That is, 

    - are balanced 
    - have empty `requireObservers`, `spendOuts`, `conInputs`, and `subTxIds` fields.

- instead of checking that all required scripts are attached to the transaction itself, 
their presence in the environment variable containing all transactions' scripts is checked 

`UTxOEnv` contains, in addition to existing fields, 

- `BatchData` (that is passed on to the `UTXO` and `UTXOS` rules), and
- a set of batch observer script hashes (also passed on to the `UTXO` and `UTXOS` rules)


#### UTXO

The `feesOK` check, the `txsize` check, the `produced = consumed` check, 
and the check that `txins` are contained in the UTxO set,
are removed from this rule (and moved to the `LEDGER` rule). 

The check that only top-level transactions may contain a non-empty 
`corInputs` field is added. 

#### UTXOS

`UTXOS` transition now conditions on 

- `validPath`

- `isTop`, which 
is true whenever the ID of the transaction matches the ID of the top-level transaction in the batch.

The `UTXOS` rule is updated to have three constructors :

1. `Scripts-Yes` : in the case that `validPath` is true, it removes both the 
`txins` and the `corInputs` from the UTxO set (in addition to all the existing 
changes done previously by `Scripts-Yes`).

2. `Scripts-No` : in the case `validPath` is false, and `isTop` is false.
No changes are made to the state here because collateral is only collected from the top-level transaction.

3. `Scripts-No-TopLevel` : in the case `validPath` is false, and `isTop` is true.
Collateral is collected, as in the previous version of the `Scripts-No` rule. 

### Collateral and Phase-2 Invalid Transactions

Enough collateral must be provided by the top-level transaction to cover the sum of all the 
fees of all batch transactions. The collateral 
can only ever be collected from the top-level transaction.
The sub-txs are not obligated to provide sufficient 
collateral for their own scripts, but they may choose to (this is never checked for sub-transactions). 
A Babel fees service [Babel Service](#babel-service)
may or may not require incoming underspecified transactions to provide their 
own collateral, depending on whether they want to assume the risk of not being 
compensated for running failing scripts. 

If a sub-transaction passes required phase-1 checks (excluding being balanced/POV, and checks related to `spendOuts` and `corInputs`),
it can be posted on-chain as a `SingularTrasaction`, so that it will be processed as top-level, and its collateral will be collected.

### Batch Observers 

Batch observers are scripts that must be run by a top-level transaction, but may be required by its sub-transactions 
as a way to specify batch-level constraints. The have the script purpose with the tag `BatchObs` and the identifier `ScriptHash`.
These are the only scripts that, in their `TxInfo` data, get a non-empty `otherInfos : List TxInfo` field, which is populated 
with the infos of the sub-transactions. This is inspired by, and may be implemented in conjunction with the 
[Observe Script Type CIP](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0112). 

The difference is that for a tx-observer script in the linked CIP is run on the `TxInfo` of the transaction 
that requires it. With batch observers, the scripts are required by a sub-tx, but run with top-level input. 
For the same top-level transaction, a regular observer and a batch observer in a transaction will get different `TxInfo`. 

Batch observers are a way to specify any intents that do not require changes to the ledger rules. For example, 
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

The transaction body is as follows ("`...`" stands for unchanged existing fields) :

```
transaction_body =
  { 0 : set<transaction_input>             ; inputs
  , ...
  , ? 23 : set<$hash32>                    ; New; Swaps
  , ? 24 : set<scripthash>                 ; New; Observer Scripts
  , ? 25 : [* spend_out]                   ; New; Spend Outs
  , ? 26 : set<cor_input>                  ; New; Cor Inputs
  }
```

The transaction is :

```
transaction =
  [ transaction_body
  , ...
  , swaps / null
  ]
```

Swaps (i.e. sub-transactions) are :

```
swaps = [ * transaction ]
transaction_index = uint .size 2
```

New redeemer tags must be added :

```
redeemer_tag =
    0 ; Spending
  / 1 ; Minting
  / 2 ; Certifying
  / 3 ; Rewarding
  / 4 ; Voting
  / 5 ; Proposing
  / 6 ; SpendOut
  / 7 ; BatchObs
```


### New Plutus Version

The Plutus prototype, changing the 
[context](https://github.com/willjgould/plutus/blob/wg/batch-observers/plutus-ledger-api/src/PlutusLedgerApi/V4/Contexts.hs).
The fork link is [here](https://github.com/willjgould/plutus/tree/wg/batch-observers). 

### Network and Consensus Changes

With this design, it is likely minimal changes will be required.

### Off-Chain Component Architecture

Underspecified transactions cannot be communicated across the Cardano 
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
A light client server cares about transactions that do not specify their own inputs,
and instead specify `spendOuts`. An exchange may care about offers of any popular 
asset at a good price. 

Moreover, different usecases may have different constraints on how "valid"
they expect the underspecified transactions to be. Some may require that 
incoming transactions are valid "enough" to collect collateral from as singular transactions.
Some services may be willing to look at the requirements imposed by `requiredBatchObservers`, while 
others may not be.


#### Babel Service

A Babel service is the catch-all name we use here to refer to a service that is interested 
in engaging with underspecified unbalanced transactions. Communication channels between such services and users constructing 
unbalanced transactions are required. Such a service can be run by anyone, probably 
alongside a full node. It would have to have a filter set for the kinds of transactions 
it will engage with. There is no guarantee that every unbalanced transaction 
will eventually be balanced by a subsequent incoming one, so each service will have 
to solve this problem for themselves, probably using an appropriate filter.

#### Batch Observers

A service processing underspecified transactions (such as the Babel service) may accept incoming transactions 
that contain non-empty `requiredObservers`. This means this service must construct batches containing these 
transactions and also satisfy the batch-level constraints imposed by the scripts specified in their `requiredObservers` 
in order to create valid batches.

An additional high-level language may be beneficial to specify what the batch observer scripts 
actually require of the batch, as Plutus script constraints may be difficult to work with directly.

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
- sub-transactions are not required to cover their own collateral ;

6. a new intent we call "spend-by-output", wherein a sub-transaction may specify outputs it 
- intends to spend, and the top-level transaction specifies the inputs that point to those outputs in the UTxO set ;
- example of possible additional supported intents (see CPS-15)
potentially useful for LC functionality ;

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

1. The top-level transaction contains `subTxs`, which 
are lists of transactions. They are processed as individual transactions, alongside the top-level tx. As a result, 

- the `TxIn` of each output can be computed for each output underspecified transaction  
at the time of construction 

- the `TxId` of the transaction for each entry in the UTxO set is necessarily 
signed by all the keys required by that transaction

- the input to (and therefore output of) each script is predictable at the time of (underspecified) tx construction, 
so that it is possible to compute required `ExUnits` for each of the scripts run by every sub-transaction 
at the time of construction

2. Contracts can only view data in the transaction running them, except in the case 
that a top-level tx is running a batch-observer script

3. In this design, script outputs (except of batch-observers) can be computed by any Babel service receiving an incoming 
underspecified transaction (as well as the author of the transaction), and they do not depend on the top-level transaction.
This makes constructing (and determining whether it is even possible to construct) 
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
