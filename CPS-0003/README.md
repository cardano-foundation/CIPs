---
CPS: 3
Title: Smart Tokens
Status: Open
Category: Tokens
Authors:
    - Istvan Szentandrasi <szist@zoeldev.com>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/382
Created: 2022-11-20
---

## Abstract

The aim of this problem statement is to raise the issue around the ability to control a native token's lifecycle at more points in time.
Currently only forging of the tokens can be controlled, but not interactions with them. Extending the blockchain to support other interactions is non-trivial and might require many tradeoffs.

## Problem

The Mary era introduced native tokens, that could be minted/burned using native scripts. These native scripts for example could allow defining basic conditions to allow forging like required signatures or time validity range. The native tokens are identified with `policyId` and `assetName`. The `policyId` identifies the "publisher" or "publishers" while `assetName` can be an arbitrary.

With the Alonzo era, plutus scripts were introduced. They allowed extending the functionality of the native scripts with more generic logic scoped at the transaction level. The format and shape of native tokens didn't change - the `policyId` became the hash of the plutus scripts pushing the "publisher" role responsibility to smart contracts.

Skipping ahead, although Babbage didn't add any additional functionality directly, the addition of reference inputs indirectly opened additional use-cases to the the token's lifecycle. To be specific an example: imagine an decentralized bridge with a wrapped token that gets dynamically minted or burned. As a safeguard they would introduce a global UTxO (e.g. with a datum including signature by a multisig wallet or validity token) controlled by recognized members or governance voting mechanism that includes an `enable` flag. The enable flag could be checked by the wrapped token minting policy through a reference input. When a governance vote would pass, the UTxO datum could be changed and the flag could be set to freeze the token.

Even in the Babbage era, after the token is minted, there is no way to control the token after it leaves a smart-contract environment. Users can freely exchange tokens and transfer among each other. This allows cheaper, more efficient and more open ecosystem. In contrast with this, ERC-20 tokens are smart-contracts that fully control any interaction with a token.

Similar to how UTxO addresses can be optionally fully controlled by smart-contracts, there could be potential also to optionally control other lifecycle points of a token than just forging on Cardano.

## Use cases

There are multiple use-cases that would benefit from having the ability to validate token interactions.

From the **NFT space**, having royalties for tokens is currently a social contract where the publisher provides the royalty information while minting the tokens. The marketplaces can choose to honor this information and transfer part of the token sales towards the author. The problem is, this is not enforced and "black market" can thrive. As an author of an art NFT, I would like to benefit from any token transfers that involve smart contracts (a marketplace platform).

From the **dapp-space**, consider validity and authorization tokens. For example, liquidity pools the liquidity provider token minting can be authorized by a validity token. This token _should_ be fully controlled by the liquidity pool smart contracts. If it were to leak out of the liquidity pool smart contract, it would give the ability to anyone to mint LP tokens and drain liquidity pools of the actual funds (as seen in the Minswap security vulnerability). IF the authorization token was itself controlled by a smart contract, even after it left the liquidity pool, the vulnerability could be avoided.

Another use-case comes up around **bridged wrapped tokens**. Due to regulations, some publishers might require the ability to freeze or selectively allow specific flow directions for the token at times. These issues were raised also at the `interoperability working group`. Bridges bridging stables from Ethereum would like more control over the wrapped bridged tokens to be in-line with regulations and help with security.

When it comes to regulations, also **native stable coins** are another case, where the publisher might want to control the ability to freeze or require authorization with interactions of their tokens.

## Goals

The first main goal is to **achieve a consensus** if having more control over the tokens is actually something that would be in-line with the values and direction of Cardano. There are multiple tradeoffs from the usability perspective. Having validated lifecycle for tokens would have an impact on all dapps and all wallets.

The second main goal is **create a CIP** with the technical direction how smart tokens could function. Below is a potential direction and possible issues and roadblocks that would need to be addressed in the CIP.

### Validating token transfers

A direct way to support the use-cases above, would be to require a validator minting policy to be executed, whenever a token is included in a transaction. Currently plutus smart contract have 4 different usages:

- SPEND - used by utxo validator scripts
- MINT - used minting policy scripts
- REWARD and CERTIFY - for staking use-cases

UTxOs have basically 2 operations associated with them:

- READ - by reference inputs
- SPEND - whenever the utxo is an input

From these only the SPEND is controlled by smart-contracts. Currently reference inputs cannot control the transactions they are in (which is a topic for another CPS).

In comparison, the operations with tokens are 3 fold:

- mint
- burn
- transfer

The MINT plutus scripts control mint and burn, but not transfer. There are 2 possible directions how the transfer could be validated:

1. Call the token policy with the `MINT`, also whenever a smart token is transferred. The minting policy then could decide based on the redeemer for how it should validate the transaction.
2. Introduce a `TRANSFER` operation and a separate script type that would be used for this exact use-case.

Both of these options would strain wallets and dapps, as they would need additional specific logic to handle smart tokens. The token validation scripts might not be generic enough and might be costly to do in every interaction. As the blockchain evolves, some interactions couldn't be predicted by the token and evolving the scripts would be problematic.

A workaround might be, if some smart-token policies delegated the validation to some validations scripts. Unfortunately, without adding the ability to execute validation on referenced scripts, even this would require either: minting/forging a token in the transaction or spending an utxo with the desired validation logic. This approach doesn't seem scalable-enough, either.

### Identifying smart tokens

Drawing parallels with addresses, on cardano addresses have a 1 byte header identifying if they are a script address, pubkey address, reward address, etc. Unfortunately this is not the case with tokens currently. Policy IDs unfortunately do not have headers and it's assumed that it's always the hash of a native or plutus script.

The identification is necessary, so that the nodes knows when it would require an additional transfer script to be present in the transaction. There might be 3 directions how "smart" or "validated" tokens could be identified in transactions:

**1. segregate tokens**
In this case, the validated and smart tokens could be separated in the transaction structures. In the CDDL:

```cddl
value = coin / [coin,multiasset<uint>] / [coin, multiasset<uint>, smartasset<uint>]
mint = multiasset<int64> / [multiasset<uint>, smartasset<uint>]
```

Alternatively the value could be "objectified" similar to babbage tx outputs:

```cddl
value = {
  0: coin,
  ? 1: multiasset<uint>,
  ? 2: smartasset<uint>
}
```

This explicit segregation would have the benefit that it could be easier backwards compatible. In this format also the policy ids could remain as `hash28` script hashes.

**2. add policy headers**
This would be a breaking change to the structures and policies. Basically it would be redefining the multiasset structure to:

```cddl
multiasset<a> = { * policy_id_with_header => { * asset_name => a } }
; token identifier format:
; [ 8 bit header | policy_id ];
; 0 - open transfer token
; 1 - smart token
policy_id_with_header = bytes
policy_id = scripthash
```

**3. policy id length**

In this situation, similar to how value can be just a coin or an array, the `policy_id` could be redefiend to be:

```
policy_id = scripthash / bytes ; as above [ 8 bit header | scripthash ]
```

Both 2. and 3. are relatively error-prone, as many projects and tools assume 28byte policy IDs. Especially when encoding them as `subject` - for example for the offchain registry, there would be no way to tell, if the policyID is with the header or not.

**TBD** add more considerations

## Open Questions

1. How to support wallets to start supporting validators?
1. How would wallets know how to interact with these tokens? - smart contract registry?
1. Is there a possibility to have a transition period, so users won't have their funds blocked until the wallets start supporting smart tokens?
1. Can this be achieved without a hard fork?
1. How to make validator scripts generic enough without impacting costs significantly?
1. Can we introduce smart tokens without significantly increasing Cardano's attack surface?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
