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

# Motivation #2: Duplicate script condition cost reduction

If you have a system that handles many Plutus UTXO entries locked by the same condition, spending many of them at the same may be expensive due to the cumulative Plutus execution cost of every utxo. This CIP would allow having all utxos locked under the same native script that all can only be spent according to some master Plutus singleton that encodes the spending condition. Depending on the contract, this can easily bring cost of a transaction down from 100 Plutus contract executions to just 1 Plutus contract and 99 native script (cheap) executions.

# Motivation #3: Evolving scripts

Some systems may want the behavior of their script to change at a specific slot number. A good example of this is an NFT mint that may want one behavior to start (ex: allow minting new tokens), but switch to another behavior later (ex: allow minting or burning only in special situations)

This CIP enables this behavior by using the `before` and `after` functionality of native scripts to toggle the behavior of the contract

```json
{
	"type": "any",
	"scripts": [{
    // standard multisig "before" clause"
		"type": "all",
		"scripts": [{
				"type": "before",
				"slot": 40272443
			},
			{
				"type": "sig",
				"keyHash": "ed6f3e2144d70e839d8701f23ebcca229bcfde8e1d6b7838bda11ac8"
			}
		]
	}, {
    // after some time has passed, switch to now using a multisig to govern the mint/burn behavior
		"type": "all",
		"scripts": [{
				"type": "after",
				"slot": 40272443
			},
			{
				"type": "script",
				"scriptHash": "plutus_script_hash_here"
			}
		]
	}]
}
```

Native scripts are nice for minting assets, but have no way to add conditions for burning assets post-mint. 
If you have a system that handles many Plutus UTXO entries locked by the same condition, spending many of them at the same may be expensive due to the cumulative Plutus execution cost of every utxo. This CIP would allow having all utxos locked under the same native script that all can only be spent according to some master Plutus singleton that encodes the spending condition. Depending on the contract, this can easily bring cost of a transaction down from 100 Plutus contract executions to just 1 Plutus contract and 99 native script (cheap) executions.

# Motivation #4: Better smart contract wallets

Some projects want to create smart-contract powered wallets. However, in a lot of cases, these don't actually need all the power of Plutus in the average use case. That is to say, a native script can be used to encode the happy path as well as a fallback Plutus path when needed

```json
{
	"type": "any",
	"scripts": [{
	  		// in the general case, the user such signs like normal
			"type": "sig",
			"keyHash": "ed6f3e2144d70e839d8701f23ebcca229bcfde8e1d6b7838bda11ac8"
		},
		{
		    // but they may use a more complicated Plutus path when needed
			"type": "script",
			"scriptHash": "plutus_script_hash_here"
		}
	]
}
```

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

Here is an illustration of transactions with their input set annotated by which ones fail and which ones succeed

![image](https://user-images.githubusercontent.com/2608559/227744589-b8610d44-ff75-4559-b022-de75c2cb542b.png)

# Backwards compatibility

Currently there are two versions of native scripts:

- V1 starting in Shelley that had `RequireAllOf`, `RequireAnyOf`, `RequireMOf`, `RequireSignature`
- V2 starting in Allegra that added `RequireTimeBefore`, `RequireTimeAfter`

Note that all that was required to add functionality in Allegra was to create a new native script language internally (`SimpleScriptV1` vs `SimpleScriptV2`) inside the Cardano codebase and did not require a new hash namespace or a new address for existing scripts. The same should be true for this proposal.
