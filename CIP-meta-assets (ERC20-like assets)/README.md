---
CIP: 113
Title: Programmable token-like assets
Category: Tokens
Status: Proposed
Authors:
    - Michele Nuzzi <michele.nuzzi.2014@gmail.com>
    - Matteo Coppola <m.coppola.mazzetti@gmail.com>
    - Philip DiSarro <philipdisarro@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/444
Created: 2023-01-14
License: CC-BY-4.0
---

## Abstract

This CIP proposes a standard for programmable tokens.

We use the term "programmable tokens" to describe the family of tokens that require
the successful execution of a script in order to change owner.

## Motivation: why is this CIP necessary?

This CIP proposes a solution at the Cardano Problem Statement 3 
([CPS-0003](https://github.com/cardano-foundation/CIPs/pull/947)).

If adopted it would allow to introduce the programmability over the transfer of tokens
(meta-tokens) and their lifecycle .

The solution proposed includes (answering to the open questions of CPS-0003):

> 1) How to support wallets to start supporting validators?

The use of standard smart wallets, that the user can derive deterministically,
and an on-chain registry of programmable tokens,
any new programmable token that is registered in the on-chain registry is
immediately supported by the smart wallet.

> 2) How would wallets know how to interact with these tokens? - smart contract registry?

The requirements for a valid transaction are described in this standard.

From an indipendent party implementing the standard perspective,
it will be clear how and where to find the necessary reference inputs
to satisfy the smart wallet handling the programmable tokens.

> 3) Is there a possibility to have a transition period, so users won't have their funds blocked until the wallets start supporting smart tokens?

Programmable tokens are normal native tokens in a smart wallet.

There is no need for a transition period, because there will be no change from the ledger persepective.

> 4) Can this be achieved without a hard fork?

Yes.

> 5) How to make validator scripts generic enough without impacting costs significantly?

Validator scripts will be standard "withdraw 0" contracts.
The impact on costs is strictly dependend on the specific implementation.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
[RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

We will use [`mermaid`](https://mermaid.js.org/) to help with the visualization of transactions and flow of informations.

The term "user" is used to indicate, interchangeably:
- "public key hash" credentials
- "script" credentials (smart contracts)
- the smart wallets derived from their credentials.

The term "registry" indicates the standard on-chain contract that implements the linked list
pattern. The contract ensures the list is always sorted by the entry's policy.

The term "entry" indicates an UTxO present at the registry address.

The term "policy" or indicates the cardano native token (CNT) policy;
that is the hash of the script that can mint such token.

The policy is specified in the datum of the entry present at the registry.

The term "CNT" is short for "cardano native token",
that is a token natively reconized by the ledger.

### High level idea

An on-chain registry is deployed.

Each UTxO on the registry, represents a registered programmable token.

On registration, the registry ensures the list stays sorted.

Off-chain, the user can deterministically derive the smart wallet.

The smart wallet will require a proof of registration (or non registration)
for each CNT that is spent.

If the CNT policy was registered as programmable,
the associated script in the registry MUST be running in the same transaction.

If the CNT policy was not present in the sorted list,
the token is trated as a normal, non programmable, CNT.

### User address derivation

The smart wallet logic is the same for every user.

So the payment credentials of the resulting address will aways be the one of
a fixed standard contract.

The stake credentials are instead what identifies the user wallet.

The user MAY choose to user either their payment credentials or their stake credentials,
however, to allow anyone to derive indipendently the address of the user,
using the payment credentials is RECOMMENDED.


### Registry entry datum

```ts
type RegistryNode {
    tokenPolicy: ByteArray, // minting policy of this programmable token
    nextTokenPolicy: ByteArray, // linked list 
    transferManagerHash: ByteArray, // spending logic
    userStateManagerHash: ByteArray, // user state contract
    globalStateUnit: ByteArray, // nft of a global state for 
    thirdPartyActionRules: ByteArray, // hash
}
```

Every entry in the registry MUST have attached an inline datum following this standard type.

This is enforced by the execution of the registry at registration.

The ordering of the fields MUST be respected.

#### `tokenPolicy`

MUST be a bytestring of length 28. This field is also the key of the entry,
and the token name of the minted NFT to be attached to the UTxO generated at registration.

#### `nestTokenPolicy`

MUST be a bytestring of length 28.

#### `transferManagerHash`

MUST be a bytestring of length 28.

Represents the hash of the "withdraw 0" validator to be included in a transfer transaction for validation.

#### `userStateManagerHash`

MUST be a bytestring of either length 0 or length 28.

This field is meant to indicate the hash of the contract that manages the state for each user.

If present, meaning the bytestirng is of length 28,
one or more reference inputs MUST be included,
depending on the sub-standard (see below).

If not present, meaning the bytestirng has length 0,
no reference inputs representing the user state are expected.

#### `globalStateUnit`

MUST be a bytestring of either length 0 or length between 28 inclusive and 60 exclusive.

If the value has length 0, no additonal reference inputs are expected representing the policy global state.

If the bytestring has length greater than or equal to 28,
the value represents the concatenation of a token policy (of length 28)
and a token name (of length between 0 and 32).

When present a reference input having an NFT matching token policy and token name MUST be included. 

#### `thirdPartyActionRules`

MUST be a bytestring of either length 0 or length 28.

This field is meant to indicate the hash of the contract that will validate
transfers requested by third parties.

If the value has length 0, the programmable token does NOT allow third parties to transfer programmable tokens on the users' behalf.

If the value has length 28, a "withdraw 0" validator with the same hash MUST be included in the transaction.

### Programmable token registration

Every entry in the registry is sorted by the `tokenPolicy` field (first field of the datum).

Every entry remembers the following entry `tokenPolicy` in the `nextTokenPolicy` field (5th field).

Requirements to register a programmable token:

1) The node preceding the policy to be registered MUST be spent.

2) The output of the transaction MUST include: 
- the node spent, with all the fields except `nextTokenPolicy` unchanged,
and `nextTokenPolicy` setted to the new entry `tokenPolicy`
- the new entry, having `nextTokenPolicy` setted to the value of the node spent previous `nextTokenPolicy`

3) The transaction MUST include the registration certificate of `transferManagerHash`.

4) The new entry `globalStateUnit` MAY be an empty string if the logic of
the programmable token does not require a global state;
otherwhise it MUST be a bytestring of length between
28 inclusive and 60 (28 + 32) exclusive.

5) The entry for the programmable token that was already registered before the transaction
MUST keep the same value that was present in the corresponding input.

6) The new entry SHOULD have the minimum amount of lovelaces that the protocol allows,
and MUST include a newly minted NFT, under the registry policy,
and the programmable token policy as NFT name. 

7) Both the outputs MUST NOT have any reference script.

8) Both the outputs address MUST **only** have payment credentials.

### Transfer

```ts
type TransferRedeemer {
    Transfer {
        registryNodes: List<Int>
    }
    ThirdParty {
        registryNodes: List<Int>
    }
}
```

### Sub standards

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It SHOULD describe alternate designs considered and related work. The rationale SHOULD provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It MUST also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section SHOULD explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

The [first proposed implementation](https://github.com/cardano-foundation/CIPs/pull/444/commits/525ce39a89bde1ddb62e126e347828e3bf0feb58) (which we could informally refer as v0) was quite different by the one shown in this document

Main differences were in the proposed:
- [use of sorted merkle trees to prove uniqueness](https://github.com/cardano-foundation/CIPs/pull/444/commits/525ce39a89bde1ddb62e126e347828e3bf0feb58#diff-370b6563a47be474523d4f4dbfdf120c567c3c0135752afb61dc16c9a2de8d74R72) of an account during creation;
- account credentials as asset name

this path was abandoned due to the logaritmic cost of creation of accounts, on top of the complexity.

Other crucial difference with the first proposed implementation was in the `accountManager` redeemers;
which included definitions for `TransferFrom`, `Approve` and `RevokeApproval` redeemers, aiming to emulate ERC20's methods of `transferFrom` and `approve`;

after [important feedback by the community](https://github.com/cardano-foundation/CIPs/pull/444#issuecomment-1399356241), it was noted that such methods would not only have been superfluous, but also dangerous, and are hence removed in this specification.

After a first round of community feedback, a [reviewed standard was proposed](https://github.com/cardano-foundation/CIPs/pull/444/commits/f45867d6651f94ba53503833098d550326913a0f) (which we could informally refer to as v1).
[This first revision even had a PoC implementation](https://github.com/HarmonicLabs/erc20-like/commit/0730362175a27cee7cec18386f1c368d8c29fbb8), but after further feedback from the community it was noted that the need to spend an UTxO on the receiving side could cause UTxO contention in the moment two or more parties would have wanted to send a programmable token to the same receiver at the same time.

The specification proposed in this file addresses all the previous concerns.

The proposal does not affect backward compatibilty being the first proposing a standard for programmability over transfers;

exsisting native tokens are not conflicting for the standard, instead, native tokes are used in this specification for various purposes.

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

- having at least one instance of the smart contracts described on:
    - mainnet
    - preview testnet
    - preprod testnet
- having at least 2 different wallets integrating meta asset functionalities, mainly:
    - displayning balance of a specified meta asset if the user provides the address of the respecive account manager contract
    - independent transaction creation with `Transfer` redeemers

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if NOT applicable. -->

- [ ] [PoC implementation](https://github.com/HarmonicLabs/erc20-like)
- [ ] [showcase transactions](https://github.com/HarmonicLabs/erc20-like)
- [ ] wallet implementation 

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
