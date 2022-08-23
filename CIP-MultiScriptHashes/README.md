---
CIP: "???"
Title: Multi-Script Hashes
Authors: Mario Blažević <mario@mlabs.city>
Discussions-To: TBD
Comments-Summary: TBD
Comments-URI: TBD
Status: Draft
Type: Standards Track  
Created: <date created on, in ISO 8601 (yyyy-mm-dd) format>  
License: CC-BY-4.0  
License-Code: Apache-2.0  
Post-History: [2022-06-09](https://forum.cardano.org/t/cip-draft-multi-script-hashes/102845)
---

## Abstract

This is a (draft) CIP to introduce a simple way to statically identify a collection of scripts that depend on each
other, so that each script can detect if a transaction tries to substitute an outside script address for an expected
one.

## Motivation

Most non-trivial DApps will be distributed not only in the usual sense, but will also have their on-chain logic spread
across multiple validator scripts. Some types of transactions will then be expected to consume and create UTxOs
belonging to different scripts.

To take an abstracted example, consider a DApp with only two validators scripts, `S₁` and `S₂`. There are transactions
`T₁` that deal only with the first validator script, transactions `T₂` that deal only with the second, and
transactions `T₁₂` that involve both. A `T₁₂` might for example simply move some funds from the first script to the
second. The question is, how can the `S₁` ensure that the recipient is in fact `S₂`?

The simplest solution is that we first compile `S₂`, then supply its `ValidatorHash` or its `Address` as a parameter
to `S₁` which can trivially compare it to the recipient's address.

If, however, there is also a valid transaction `T₂₁` that moves funds from `S₂` to `S₁`, we can't apply the same
solution: there is currently no way to resolve a mutual dependency between scripts.

There are workarounds to guard against the substitution. We can mint a limited amount of a token, for example, supply
its `CurrencySymbol` as a parameter to all scripts, and then ensure that every UTxO locked by any script in our DApp
carries one of these tokens as an identification badge. This however introduces unnecessary complexity and increases
all transaction costs. It would be better to solve the root issue of mutual dependency.

## Specification

The minimum required functionality can be provided with just two additional functions in Plutus API, and a new field
in `TxInfo`:

```
validatorHashes :: [Validator] -> [ValidatorHash]
allScripts :: [Validator] -> ScriptLookups Any
txInfoValidators :: TxInfo -> [ValidatorHash]
```

The new `validatorHashes` function is a generalization of the existing

```
validatorHash :: Validator -> ValidatorHash
```

The new function would hash the entire list of validators, together with `[1..n]` for each result hash. The length of
the result list would equal the length of the argument, and the value of every single `ValidatorHash` result list item
would depend on every `Validator` item in the argument list. In other words, a change to any single `Validator` would
affect every `ValidatorHash`.

The same explanation applies to the new `allScripts` function, which is a generalization of the existing

```
otherScript :: Validator -> ScriptLookups Any
```

The `[ValidatorHash]` list calculated by `allScripts` would be made available as the `txInfoValidators` accessor so
each validator triggered by the transation could check it against the addresses of transaction's UTxOs.

Furthermore, if `allScripts` is invoked with argument `vs`, every `TxOut` consumed by the transaction must satisfy
``all (`elem` validatorHashes vs) . toValidatorHash . txOutAddress``. The transaction otherwise fails in phase 1 of
validation.

## Rationale

Assume the off-chain portion of our example DApp consistently specifies the `allScripts [S₁, S₂]` lookup with every
transaction and that both validators use `txInfoValidators` to verify both the `ownInput` address and the destinations
of both `T₁₂` and `T₂₁`. If an attacker attempts to submit a transaction substituting a third address `S₃`, the
validators would reject it. Adding `otherScript S₃` or `allScripts [S₁, S₃]` as a lookup would not work: the former
would not populate `txInfoValidators` and the latter would provide the wrong address for `S₁`.

## Backwards Compatibility

The addition of two new functions `validatorHashes` and `allScripts` would be a backward-compatible extension of the
API. The addition of `txInfoValidators` is more problematic. Perhaps it can be done without a hard fork, but I'm not
sure.

## Copyright

Apache-2.0
