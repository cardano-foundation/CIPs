---
CIP: 38
Title: Arbitrary Script as Native Script spending conditions
Authors: Sebastien Guillemot <seba@dcspark.io>
Comments-URI: TBD
Status: Draft
Type: Standards
Created: 2022-07-27
License: CC-BY-4.0
---

# Abstract

Native scripts behave differently than Plutus scripts, notably by being easier & cheaper to work with for both users and developers. However, limited composability between native scripts and Plutus scripts limits leveraging these facts.

This CIP introduces a way to use native scripts as a starting point for more complex interactions which helps unlock use cases such as simple proxy contracts

# Motivation #1: Proxy contracts

Suppose that you are part of a DAO whose funds are managed by a Plutus contract. Your DAO, in order to receive payments, would like receive ADA or tokens to its script address directly. However, this is non-trivial because applications cannot sent to arbitrary Plutus scripts as they do not know how to structure the datum or what other kind of restrictions may exist for this contract.

To solve this, one way would be to instead have a proxy contract that receives funds and forwards them to your DAO with the proper structure. Native scripts at the moment can play this role by creating a native script multisig where some set of DAO members have their public keys specified in the spending condition of the multisig. However, this approach has the following problems:

- There is no way to guarantee that these members will actual forward the funds to the DAO instead of pocketing the funds
- DAO membership may not easily be representable by a small set of fixed public keys

To avoid unnecessary feature creep to the native script feature, the most generic solution is to allow a new condition where a native scripts can only be spent if a specific Plutus script is also part of the transaction input. This allows the multisig to simply handle receiving the funds and having all the complex logic (DAO membership checks, output checks, etc.) to be added to the Plutus script.

# Motivation #2: Cost reduction

If you have a system that handles many Plutus UTXO entries locked by the same condition, spending many of them at the same may be expensive due to the cumulative Plutus execution cost of every utxo. This CIP would allow having all utxos locked under the same native script that all can only be spent according to some master Plutus singleton that encodes the spending condition. Depending on the contract, this can easily bring cost of a transaction down from 100 Plutus contract executions to just 1 Plutus contract and 99 native script (cheap) executions.

# Specification

The current definition of native scripts uses the following BNF notation

```BNF
<native_script> ::=
             <RequireSignature>  <vkeyhash>
           | <RequireTimeBefore> <slotno>
           | <RequireTimeAfter>  <slotno>

           | <RequireAllOf>      <native_script>*
           | <RequireAnyOf>      <native_script>*
           | <RequireMOf>        <num> <native_script>*
```

Importantly, note that native scripts can only require other native scripts and not plutus scripts or any other future script type introduced.

Therefore, this proposal suggests the definition be changed to

```BNF
<native_script> ::=
             <RequireSignature>  <vkeyhash>
           | <RequireScript>     <scripthash>
           | <RequireTimeBefore> <slotno>
           | <RequireTimeAfter>  <slotno>

           | <RequireAllOf>      <native_script>*
           | <RequireAnyOf>      <native_script>*
           | <RequireMOf>        <num> <native_script>*
```

Which we propose uses the `type: script` when used in JSON notation such as in the following example:

```json
{
  "type": "all",
  "scripts":
  [
    {
      "type": "script",
      "scriptHash": "b275b08c999097247f7c17e77007c7010cd19f20cc086ad99d398538"
    },
  ]
}
```

# Backwards compatibility

Currently there are two versions of native scripts:

- V1 starting in Shelley that had `RequireAllOf`, `RequireAnyOf`, `RequireMOf`, `RequireSignature`
- V2 starting in Allegra that added `RequireTimeBefore`, `RequireTimeAfter`

Note that all that was required to add functionality in Allegra was to create a new native script language internally (`SimpleScriptV1` vs `SimpleScriptV2`) inside the Cardano codebase and did not require a new hash namespace or a new address for existing scripts. The same should be true for this proposal.
