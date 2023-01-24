---
CIP: ?
Title: Maybe Datum
Category: Plutus
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/321
    - https://github.com/cardano-foundation/CIPs/pull/418
Created: 2023-01-18
License: CC-BY-4.0
---
# CIP-XXXX: Maybe Datum

## Abstract
Currently all plutus spending scripts take a datum directly from the UTxO being spent. While this allows for creating a very simple ledger-script interface, there are a number of use cases where this feature is not just undesired but can also be an obstacle to Dapp developement. I propose changing all plutus scripts so that they optionally take the datum directly from the UTxO being spent. This single change would solve a number of issues currently motivating different CIPs/CPSs. 

## Motivation: why is this CIP necessary?
As of now, plutus spending scripts take the datum directly from the UTxO being spent. While it allows the ledger-script interface to be very simple, it causes three major problems.

### Problem 1: Spending Script Redundant Executions
Using the eUTxO model, it is currently possible to create spending scripts that validate based off of the transaction as a whole instead of any individual UTxO. Imagine if three UTxOs were spent from such a script's address within the same transaction. Which datum should be passed to the spending script? Currently, the ledger-script interface passes each UTxO's datum to the script individually and executes this "transaction level" spending script three times. Since the transaction context does not change between executions, these additional executions are completely redundant. There is currently no way to use a transaction level spending script so that these redundant executions do not happen. This limitation significantly handicaps Cardano's usage of the eUTxO model. While there is a potential workaround, the workaround has its own major drawbacks. You can read more about it in the related CPS [here](https://github.com/fallen-icarus/CIPs/tree/full-eUTxO-potential/CPS-%3F%3F%3F%3F#readme).

Note: While Cardano simple scripts do not use a datum, they may also suffer from this limitation.

### Problem 2: Wrong/Missing Datums Result in Permanently Locked Script UTxOs
When a script's UTxO is missing a datum or has the wrong datum, the plutus spending script is unable to parse the datum attached to the UTxO and is therefore guaranteed to fail. This results in permanently locked UTxOs at the script's address. In order to help prevent accidental locking of script UTxOs, proxies are generally used. The idea is for users to send their funds to this proxy first. The proxy then attaches the required datum for the users and passes the funds onto the desired script address. However, it is very difficult to use such proxies in a decentralized way. In short, by being forced to use proxies, the Dapp loses some of its decentralization.

Further, there are a number of use cases where a datum is not needed for the Dapp to function. In these situations, a dummy datum is still required just to prevent locking.

As an addition point, regulators are not going to like any application where it is easy to accidentally lock (lose) users' funds permanentally. Regulators may force certain certifications for Dapp developers as a consequence. The motivation is exactly the same for why finanical advisors need to be licensed. Currently, this ease of accidental locking is the default on Cardano. This needs to be changed if we do not want regulators forcing developer certifications that are inherently centralizing.

### Problem 3: No Universal Plutus Script
Since plutus spending scripts take a datum while plutus minting and staking scripts do not, it is currently not possible to create a universal plutus script (one that can do all three). There are use cases where the Dapp would be more secure if the same script could be used for both spending and minting. An example is to only mint a token if a deposit is made to the relevant script address. 

Right now, if a developer wanted to do this, he/she would need to hardcode the spending script hash into the minting policy AND the minting policy id would need to be passed to the spending script as a datum. If a universal script could be used, the spending script hash would be the same as the minting policy id. In the former case, the security of this process depends on how well the datum usage can be guarded. In the latter case, the process is secure by default since the hash cannot be faked/wrong.

## Specification
### `Data` Specification for `Maybe Datum`
Before the ledger-script interface passes the datum to the plutus script, the datum will be wrapped in a `Maybe` data type. Seen as type `Data`, this wrapping is:

``` Haskell
Nothing = Constr 0 []
Just datum = Constr 1 [datumAsData]
```

The datum will only be converted from `BuiltinData` if the `Just` is going to be used. No parsing should be attempted if the `Nothing` is going to be used.

As an example, to pass the unit datum into a plutus spending script, the following `Data` would be passed:
``` Haskell
Just () = Constr 1 [Constr 0 []]
```

### Creating Universal Plutus Scripts
All plutus scripts will now be written as:
```
mkUniversalScript :: Maybe Datum -> Redeemer -> ScriptContext -> Bool
mkUniversalScript (Just d) r ctx = ...
mkUniversalScript Nothing r ctx = ...
```

### Using Universal Plutus Scripts
#### Minting and Staking
When a universal script is to be used for either minting or staking, `Nothing` will automatically be passed into the script. A `plutus-script-v3` flag will be needed to differentiate whether a universal script is being used or a v1/v2 script is being used.

#### Spending
Using the universal scripts, there will now be two ways to use a spending script.

1. **UTxO level spending scripts**: These scripts will have the datum attached to the UTxO being spent parsed and passed to the universal script as `Just datum`. These scripts are meant to be executed once per UTxO consumed from the script address.
2. **Transaction level spending scripts**: These scripts will have `Nothing` passed to the universal script without attempting to parse the datums attached to the UTxOs being spent. These scripts are meant to be executed once per transaction. The datums will still be present in the `ScriptContext`.

#### `cardano-cli`
`cardano-cli` will need to be expanded to add `--utxo-level` and `--tx-level` flags so that users can explicitly say which level of the spending script to use.

Example UTxO level spending script flag usage:
``` Bash
  --tx-in <script_utxo_to_spend> \
  --utxo-level-spending-tx-in-reference <ref_script_utxo_id> \
  --plutus-script-v3 \
  --utxo-level-spending-reference-tx-in-inline-datum-present \
  --utxo-level-spending-reference-tx-in-redeemer-file <script_redeemer> \
```

Example transaction level spending script flag usage:
``` Bash
  --tx-in <script_utxo1> \
  --tx-in <script_utxo2> \
  --tx-in <script_utxo3> \
  --tx-level-spending-tx-in-reference <ref_script_utxo_id> \
  --plutus-script-v3 \
  --tx-level-spending-reference-tx-in-redeemer-file <script_redeemer> \
```

For transaction level scripts, since there is no need to parse the datums attached to each UTxO, the datum flags are not needed. Any datums present will still appear in the `ScriptContext` that gets passed to the plutus script. All UTxOs being validated by the transaction level script are assumed to be using the same redeemer which is why it is okay to place the redeemer flag at the end.

Users **MUST** explicitly state which level to use. Building a transaction should fail if the level is not explicitly stated or if both levels are specified for the same UTxO.

#### Script Context
Currenty, the `ScriptPurpose` part of `ScriptContext` is defined like this:

``` Haskell
-- | Purpose of the script that is currently running
data ScriptPurpose
    = Minting CurrencySymbol
    | Spending TxOutRef
    | Rewarding StakingCredential
    | Certifying DCert
```

When the script is a spending script, the `TxOutRef` of the UTxO being validated is used. This setup does not allow for transaction level scripts: if there are three UTxOs being validated, which `TxOutRef` should be used?

To expand the `ScriptPurpose` to also enable transaction level spending scripts, I propose introducing this new sum type:
``` Haskell
-- | Spending script validation level
data SpendingLevel
    = UTxOLevel TxOutRef
    | TxLevel ValidatorHash
```

Then the `ScriptPurpose` definition will be changed to use this new sum type:
``` Haskell
-- | Purpose of the script that is currently running
data ScriptPurpose
    = Minting CurrencySymbol
    | Spending SpendingLevel  -- ^ Uses new sum type
    | Rewarding StakingCredential
    | Certifying DCert
```

For the `Data` specification of `SpendingLevel`, I propose:

``` Haskell
UTxOLevel txOutRef = Constr 0 [txOutRefAsData]
TxLevel validatorHash = Constr 1 [validatorHashAsData]
```

Whenever the `--tx-level` flags are used for spending scripts, the `TxLevel` constructor will be used in the `ScriptPurpose`. To make it easy to get the `ValidatorHash` of the transaction level script, a `--tx-level-spending-hash` flag can also be required when building the transaction. The idea is similar to how building a transaction with a reference script for a minting policy requires the explicit use of the `--policy-id HASH` flag. Conversely, whenever the `--utxo-level` flags are used, the `UTxOLevel` constructor will be used.

Several functions use the `ScriptPurpose` in order to get certain information in on-chain code. An example is the `ownHash` function that uses the `Spending TxOutRef` to get the hash of the current validator. New plutus v3 versions of these functions will be needed to use the new `ScriptPurpose`.

#### Simple Scripts
Given that Cardano simple scripts are only for multisig and time locking, and both scenarios are ones that validate based off of the transaction as a whole, simple scripts are only usable as transaction level scripts. If the simple scripts language is going to be extended in the future, perhaps it would "future proof" the ledger-script interface to still have the option for using simple scripts at the UTxO level even though there are no use cases right now.

#### Ensuring All Script Witnesses Are Present
The node is already capable of detecting if all required witnesses are present. This tooling will just need to be adapted to allow transaction level scripts to witness all UTxOs while being executed only once. The idea is similar to only one pubkey signature being required no matter how many UTxO are being spent from the corresponding address.

The node is also capable of detecting if extraneous witnesses are present. This can be leveraged to make sure only one spending level is used for each UTxO being validated.

#### Does This Require A Hardfork?
According to [CIP-0035](https://github.com/michaelpj/CIPs/blob/8e296066c0afc7d2ed46db88eca43f409830e011/CIP-0035/README.md#scripts-in-the-cardano-ledger), what is being suggested here is a change to the ledger-script interface. This means a new Plutus Core ledger language (LL) is required. The CIP states that this requires a hardfork. However, being that the way things are stored on-chain will not change, this should be a smaller hardfork than the past few.

## Rationale: how does this CIP achieve its goals?
The key idea of this CIP is to address multiple developer concerns as simply as possible. There have been (at least) 6 proposals created so far whose motivations can all be addressed by the `Maybe Datum` ([#364](https://github.com/cardano-foundation/CIPs/pull/364),[#423](https://github.com/cardano-foundation/CIPs/issues/423),[#309](https://github.com/cardano-foundation/CIPs/pull/309),[#418](https://github.com/cardano-foundation/CIPs/pull/418),[#310](https://github.com/cardano-foundation/CIPs/pull/310),[#321](https://github.com/cardano-foundation/CIPs/pull/321)). 

By allowing for transaction level spending scripts, redundant executions are eliminated. By not always forcing the parsing of datums attached to script UTxOs, the accidental locking is stopped. And by allowing a plutus script to be used as all three types (spending, minting, and staking), more secure-by-default Dapps can be written.

### `ScriptArgs` Alternative
The `ScriptArgs` proposal ([here](https://github.com/cardano-foundation/CIPs/pull/321)) could also address all three issues motivating this CIP. However, the `ScriptArgs` approach would be much more complicated to implement since passing the arguments to the scripts as a sum type would be a major divergence from the way things are currently implemented. For this reason, I believe the `Maybe Datum` would be a better approach.

### Backwards Compatibility
Only plutus scripts that use the `plutus-script-v3` flag will have their datums and `ScriptPurpose` handled in this way. All other plutus version will retain their usage. This flag will be exclusively used with the new universal plutus script.

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)