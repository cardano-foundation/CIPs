---
CIP: ?
Title: Maybe Datum
Category: Plutus, Ledger
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
Currently all plutus spending scripts take a datum directly from the UTxO being spent. While this allows for creating a very simple ledger-script interface, there are a number of use cases where this feature is not just undesired but can also be an obstical to Dapp developement. I propose changing plutus scripts so that they optionally take the datum directly from the UTxO being spent. This single change would solve a number of issues currently motivating different CIPs/CPSs. 

## Motivation: why is this CIP necessary?
As of now, plutus spending scripts take the datum directly from the UTxO being spent. While it allows the ledger-script interface to be very simple, it causes three major problems.

### Problem 1: Spending Script Redundant Executions
Using the eUTxO architecture, it is currently possible to create spending scripts that validate based off of the transaction as a whole instead of any individual UTxO. Imagine if three UTxOs were spent from such a script's address within the same transaction? Which datum should be passed to the spending script? Currently, the ledger-script interface passes each UTxO's datum to the script individually and executes this "transaction level" spending script three times. Since the transaction context does not change between executions, these additional executions are completely redundant. There is currently no way to use a transaction level spending script so that these redundant exections do not happen. This limitation significantly handicaps Cardano's usage of the eUTxO architecture. While there is a potential workaround, the workaround has its own major drawbacks. You can read more about it in the related CPS [here](https://github.com/fallen-icarus/CIPs/tree/full-eUTxO-potential/CPS-%3F%3F%3F%3F#readme).

### Problem 2: Wrong/Missing Datums Result in Permanently Locked Script UTxOs
When a script's UTxO is missing a datum or has the wrong datum, the spending script is unable to parse the datum attached to the UTxO and is therefore guaranteed to fail. This results in permanently locked UTxOs at the script address. In order to help prevent accidental locking of script UTxOs, proxies are generally used. However, it is very difficult to use such proxies in a decentralized way. In short, by being forced to use proxies, the Dapp loses some of its decentralization.

As an addition point, regulators are not going to like any application where it is easy to accidentally lock (lose) users' funds permanentally. Regulators may force certain certifications for Dapp developers as a consequence. The motivation is exactly the same for why finanical advisors need to be licensed. Currently, this ease of accidental locking is the default on Cardano. This needs to be changed if we do not want regulators forcing developer certifications that are inherently centralizing.

### Problem 3: No Universal Plutus Script
Since spending scripts take a datum while minting and staking scripts do not, it is currently not possible to create a universal script (one that can do all three). There are use cases where the Dapp would be more secure if the same script could be used for both spending and minting. An example is to only mint a token if a deposit is made to the relevant script address. 

Right now, if a developer wanted to do this, he/she would need to hardcode the spending script hash into the minting policy AND the minting policy id needs to be passed to the spending script as a datum. If a universal script could be used, the spending script hash would be the same as the minting policy id. In the former case, the security of this process depends on how well the datum usage can be guarded. In the latter case, the process is secure by default since the hash cannot be faked/wrong.

## Specification
### `Data` Specification for `Maybe Datum`
Before the ledger-script interface passes the datum to the plutus script, the datum will be wrapped in a `Maybe` data type. Seen as type `Data` this wrapping is:

``` Haskell
Nothing = Constr 0 []
Just datum = Constr 1 [datumAsData]
```

The datum will only be converted from `BuiltinData` if the `Just` is going to be used. No parsing should be attempted if the `Nothing` is going to be used.

As an example, to pass the unit datum into a script, the following `Data` would be passed:
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
When universal script is to be used for either minting or staking, `Nothing` will automatically be passed into the script. A `plutus-script-v3` flag will be needed to differentiate whether a universal script is being used or a v1/v2 script is being used.

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

Since there is no need to parse the datums attached to each UTxO, the datum flags are not needed. Any datums present will still appear in the `ScriptContext` that gets passed to the plutus script. All UTxOs being spent are assumed to be using the same redeemer which is why it is okay to place the redeemer flag at the end.

Users **MUST** explicitly state which level to use. Building a transaction should fail if the level is not explicitly stated.

#### Ensuring All Script Witnesses Are Present
The node is already capable of detecting if all required witnesses are present. This tooling will just need to be adapted to allow transaction level scripts to witness all UTxOs while being executed only once. The idea is similar to only one pubkey signature being required no matter how many UTxO are being spent from the corresponding address.

#### Does This Require A Hardfork?
According to [CIP-0035](https://github.com/michaelpj/CIPs/blob/8e296066c0afc7d2ed46db88eca43f409830e011/CIP-0035/README.md#scripts-in-the-cardano-ledger), what is being suggested here is a change to the ledger-script interface. This means a new Plutus Core ledger language (LL) is required. The CIP states that this requires a hardfork.

## Rationale: how does this CIP achieve its goals?
The key idea of this CIP is to address multiple developer concerns as simply as possible. There have been (at least) 6 proposals created so far whose motivations can all be addressed by the `Maybe Datum` ([#364](https://github.com/cardano-foundation/CIPs/pull/364),[#423](https://github.com/cardano-foundation/CIPs/issues/423),[#309](https://github.com/cardano-foundation/CIPs/pull/309),[#418](https://github.com/cardano-foundation/CIPs/pull/418),[#310](https://github.com/cardano-foundation/CIPs/pull/310),[#321](https://github.com/cardano-foundation/CIPs/pull/321)). 

By allowing for transaction level spending scripts, redundant executions are eliminated. By not forcing the parsing of datums attached to script UTxOs, the accidental locking is stopped. And by allowing a plutus script to be used as all three types (spending, minting, and staking), more secure-by-default Dapps can be written.

### `ScriptArgs` Alternative
The `ScriptArgs` proposal ([here](https://github.com/cardano-foundation/CIPs/pull/321)) could also address all three issues motivating this CIP. However, the `ScriptArgs` approach would be much more complicated to implement since it would be a major divergence from the way things are currently implemented. For this reason, I believe the `Maybe Datum` would be a better approach.

### Backwards Compatibility
Only plutus scripts that use the `plutus-script-v3` flag will have their datums handled in this way. All other plutus version will retain their usage.

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)