---
CIP: 87
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

## Abstract
Currently all plutus spending scripts take a datum directly from the UTxO being spent. When a user/developer forgets to add a datum to a UTxO being sent to a plutus script's address, this results in the permanent locking of the UTxO. This CIP proposes changing the ledger-script interface so that all plutus scripts take an optional datum argument. Then, if the UTxO being spent is missing a datum or the plutus script is being used to mint/stake, the `Nothing` equivalent for the argument will be passed to the plutus script being executed. This latter part allows for universal plutus scripts.

## Motivation: why is this CIP necessary?

### Problem 1: Missing Datums Result in Permanently Locked Script UTxOs
When a UTxO locked at a plutus script's address is missing a datum, the plutus spending script is unable to execute since the datum argument is mandatory and it can only be obtained from the UTxO being spent. Therefore, validation of this UTxO is always guaranteed to fail. This results in a permanently locked UTxO at the script's address. This situation makes it risky for users to send funds directly to a plutus script's address. What datum to use needs to be known by every user sending to the associated plutus script address. A few workarounds have been suggested:

- Using an extended address format - the information about what datum to use could be encoded directly into the address users are trying to send to. This approach suffers from being unable to trustlessly verify the correctness of the datum in the extended address used: 
    1. How do you verify that the datum in the address is correct? What if the datum is meant to convey information about the owner of the input UTxO? A malicious person can trick users into sending to a malicously crafted extended address.
    2. This increases the need to trust software that is being used to get the datum information from the extended address. A malicious frontend can alter the datum information so that it can steal funds from the user.
- Using a proxy - users send their funds to a middle contract/entity that then attaches the required datum for the users and passes the funds onto the desired script address. Currently, the only way to use proxies in a trustless manner is to use a plutus script as the proxy. But then we are back to where we started: a missing datum will result in the permanent locking of the funds sent to the proxy contract. So the only real proxy workaround for completely preventing locking due to a missing datum is to use a multisig native script or another pubkey address and have the owner(s) attach the proper datum for the users. Both of these options force reliance on centralized parties.

As a final point, there are use cases where a datum is not needed for the Dapp to function. In these situations, a dummy datum is still required just to prevent locking.

### Problem 2: No Universal Plutus Script
Since plutus spending scripts take a datum while plutus minting and staking scripts do not, it is currently not possible to create a universal plutus script (one that can do all three). There are use cases where the Dapp would be better able to guarantee proper usage if the same script could be used for both spending and minting. An example is to only mint a token if a deposit is made to the relevant script address. 

The `eopsin` pythonic smart contract tooling has implemented a workaround for this, however, it requires an "ugly hack" that some developers may not be comfortable using. You can read more about it [here](https://github.com/ImperatorLang/eopsin/blob/master/ARCHITECTURE.md#minting-policy---spending-validator-double-function).

Right now, if a developer wanted to implement the above example without using the "ugly hack", he/she would need to hardcode the spending script hash into the minting policy AND the minting policy id would need to be passed to the spending script as a datum. But now what would happen if a user accidentally uses the wrong policy id in the datum? Since the plutus script can only know about the associated minting policy through the policy id in the datum, the plutus script has no choice but to treat the incorrect datum as if it was correct. This can produce undesired behavior at best or permanent locking of funds at worst (like when the plutus spending script forces the asset associated to the policy id to be burned instead of being withdrawn from the address).

If a universal script could be used, the spending script hash would be the same as the minting policy id. There would be no need to rely on the datum for the plutus script to know about the proper minting policy. 

In the former case, the proper usage of this process depends on how well the datum usage can be guarded. In the latter case, the usage is guaranteed by default since the hash cannot be faked/wrong.

## Specification

### Creating Universal Plutus Scripts
All plutus scripts, including minting and staking scripts, will be changed to take an optional datum argument. Using the haskell syntax, it would look like this:

``` Haskell
mkUniversalScript :: Maybe Datum -> Redeemer -> ScriptContext -> Bool
mkUniversalScript (Just d) r ctx = ...
mkUniversalScript Nothing r ctx = ...
```

### `Data` Specification for `Maybe Datum`
Before the ledger-script interface passes the datum to the plutus script, the datum will be wrapped in a `Maybe` data type. Seen as type `Data`, this wrapping is:

``` Haskell
Nothing = Constr 0 []
Just datum = Constr 1 [datumAsData]
```

### Using Universal Plutus Scripts
#### Spending
If the UTxO being spent is missing a datum, then the `Nothing` constructor will be passed to the plutus script. Otherwise, the datum will be wrapped in the `Just` constructor before being passed to the plutus script.

As an example, to pass the unit datum into the plutus script, the following `Data` would be passed:
``` Haskell
Just () = Constr 1 [Constr 0 []]
```

#### Minting and Staking
When a universal script is being used for either minting or staking, `Nothing` will automatically be passed into the plutus script.

### Plutus v3
According to [CIP-0035](https://github.com/michaelpj/CIPs/blob/8e296066c0afc7d2ed46db88eca43f409830e011/CIP-0035/README.md#scripts-in-the-cardano-ledger), what is being suggested here is a change to the ledger-script interface. This means a new Plutus Core ledger language (LL) is required. CIP-0035 states that this requires a hardfork. However, being that the way things are stored on-chain will not change, this should be a smaller hardfork than the past few.

## Rationale: how does this CIP achieve its goals?
The key idea of this CIP is to address multiple developer concerns as simply as possible. There have been (at least) 5 proposals created so far whose motivations can all be addressed by the `Maybe Datum` ([#364](https://github.com/cardano-foundation/CIPs/pull/364),[#423](https://github.com/cardano-foundation/CIPs/issues/423),[#309](https://github.com/cardano-foundation/CIPs/pull/309),[#310](https://github.com/cardano-foundation/CIPs/pull/310),[#321](https://github.com/cardano-foundation/CIPs/pull/321)). 

With this change, UTxOs would no longer be permanently locked simply for missing a datum. Further, it would now be possible to use the same plutus script for spending, minting, and staking.

### Backwards Compatibility
Only plutus scripts that use the new plutus ledger language will have their datums handled in this way. All other plutus ledger languages will retain their usage.

### `ScriptArgs` Alternative
The `ScriptArgs` proposal ([here](https://github.com/cardano-foundation/CIPs/pull/321)) could also address the issues motivating this CIP. The `ScriptArgs` approach could allow for easily implementing future changes such as allowing scripts to take other kinds of arguments. However, all of the details have yet to be ironed out.

## Path to Active
### Acceptance Criteria
1. Personally, I would like to see the `ScriptArgs` proposal finished and merged so that the community can properly debate the pros and cons for both proposals.
2. `plutus` and `cardano-ledger` have been updated to the new design.
3. The new design has been incorporated into the new plutus ledger language.

### Implementation Plan
The Plutus team or an equally qualified group implements the changes.

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)