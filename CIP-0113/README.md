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
    - https://github.com/cardano-foundation/CIPs/pull/944
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
(programmable tokens) and their lifecycle.

The solution proposed includes (answering to the open questions of CPS-0003):

> 1) How to support wallets to start supporting validators?

With the use of standard smart wallets, that the user can derive deterministically,
and an on-chain registry of programmable tokens. Any new programmable token that is 
registered in the on-chain registry is immediately supported by the smart wallet.

> 2) How would wallets know how to interact with these tokens? - smart contract registry?

The requirements for a valid transaction are described in this standard.

From an indipendent party implementing the standard perspective,
it will be clear how and where to find the necessary reference inputs
to satisfy the smart wallet that handles the programmable tokens.

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

The term "user" is used to indicate, interchangeably:
- "public key hash" credentials
- "script" credentials (smart contracts)

The term "creator" is used to indicate a user that creates a new programmable token.
The term "admin" is used to indicate a user that can execute priviledged actions on a certain programmable token without explicit permission of the users.
The term "issuer" is used to indicate a user that can mint and/or burn a certain programmable token.

The term "policy" indicates a Cardano native token (CNT) policy, which is the hash of the script that can mint such token.
The term "unit" indicates the concatenation of a token policy and a token name to uniquely represent a certain CNT.

The following terminology represents all the on-chain components of the standard:
- `tokenRegistry`: on-chain registry where anyone can register new programmable tokens. It's a smart contract that implements the linked list pattern. The contract ensures the list is always sorted by the entry's policy. It is made of: 
    - `registryNode`: a node (or entry) of the tokenRegistry is a UTxO representing a specific programmable token
    - `registrySpendScript`: Spend script where all the registryNodes exist
    - `registryMintingPolicy`: Minting script of NFTs that represent valid registryNodes
- `programmableLogicBase`: the unique Spend script that always holds all existing programmable tokens 
- `transferLogicScript`: a token-specific Withdraw script that implements the custom transfer logic for such programmable token
- `thirdPartyTransferLogicScript`: a token-specific Withdraw script that defines admin actions on such programmable token
- `issuancePolicy`: a Minting script that mints programmable token. While this script code is one for all possible programmable tokens, its deployment is token-specific because issuancePolicy is parametrized by the hash of an issuanceLogicScript
- `issuanceLogicScript`: a token-specific Withdraw script that impelments the custom minting/burning logic for such programmable token
- `globalState`: an optional token-specific unique UTxO whose datum contains global information regarding the token (if it's frozen, if transfers are paused, etc.)

The term "substandard" indicates a specific implementation of all the on-chain components that guarantees a certain behaviour and a consistent way to build the transactions. Any programmable token must belong to a certain substandard, otherwise wallets and dApps don't know how to manage them.

The term "smart wallet" indicates all the UTxOs living inside the programmableLogicBase script and belonging to a certain user.
To know a user's smart wallet address check the dedicated following section.

### High level flow

The creator wants to release a new programmable token.

The tokenRegistry and the programmableLogicBase are already deployed on-chain.

The creator writes a new transferLogicScript where he defines the rules to transfer the new token.

Then he writes a new thirdPartyTransferLogicScript where he defines who are the admins and what the actions they can do without permission of any other user.

Then he writes a new issuanceLogicScript where he defines who can mint and burn the new token.

Then he deploys a new issuancePolicy instance parametrized by the new issuanceLogicScript.

Finally, the creator adds a registryNode to the tokenRegistry with the hashes of all the above scripts and with additional required
information. The registration cannot happen if the policy has been already registered or if the issuancePolicy is wrong.

During or after the registration process, the creator can mint the new programmable token.
This new token is enforced to be sent in the programmableLogicBase script.

Off-chain, any user can deterministically derive their smart wallet (as explained in the next section).

When an user wants to transfer some of his programmable tokens, for each token a proof of registration (or non registration) is required: if the policy is present in the tokenRegistry then the associated transferLogicScript MUST be running in the same transaction; if the policy is not present in the tokenRegistry, the token is treated as a normal, non programmable, CNT and can always leave the programmableLogicBase script.

In any moment for each token, admins can execute privileged actions as defined in thirdPartyTransferLogicScript.

In any moment for each token, issuers can mint more token or burn existing ones that are held by them.

### User's smart wallet address derivation

The smart wallet address has the following form:
(fixedPaymentCredentials, userDefinedStakeCredentials)

where:
- fixedPaymentCredentials never change and they are the credentials obtained from the hash of programmableLogicBase
- userDefinedStakeCredentials are different for each user.
The smart wallet logic is the same for every user. If the user is a wallet, he MAY choose to user either their payment credentials or their stake credentials. We suggest to use his payment credentials to allow anyone to derive indipendently the address of the user.
If the user is a smart contract, then it's the payment credentials of that contract.

In other words, a smart wallet is the set of UTxOs that live in the programmableLogicBase script and that have a specific stake credential that identifies the owner.

### TokenRegistry entry datum

Every entry in the tokenRegistry MUST have attached an inline datum following this standard type:

```ts
type RegistryNode {
    tokenPolicy: ByteArray,
    nextTokenPolicy: ByteArray, 
    transferLogicScript: ByteArray,
    userStateManagerHash: ByteArray,
    globalStateUnit: ByteArray, 
    thirdPartyTransferLogicScript: ByteArray
}
```

This datum is enforced by the execution of the tokenRegistry at registration.

The ordering of the fields MUST be respected.

#### `tokenPolicy`

MUST be a bytestring of length 28. This field is also the key of the entry (registryNode) 
and the token name of the NFT minted via registryMintingPolicy and that is included in the entry UTxO.

#### `nextTokenPolicy`

MUST be a bytestring of length 28.

As the tokenRegistry is a ordered linked list, it's the next key (a tokenPolicy) in the tokenRegistry in lexicographic order.

#### `transferLogicScript`

MUST be a bytestring of length 28.

Represents the hash of the "Withdraw 0" script to be included in a transfer transaction for validation.

#### `userStateManagerHash`

MUST be a bytestring of either length 0 or length 28.

It represents the optional hash of the "Withdraw 0" script that manages the state for each user.

If the value has length 28, when creating a transfer transaction one or more reference inputs MUST be 
included depending on the sub-standard (see below).

If the value has length 0, when creating a transfer transaction no reference input representing the user state is expected.

#### `globalStateUnit`

MUST be a bytestring of either length 0 or length between 28 inclusive and 60 exclusive.

It represents the optional unit of an NFT that is contained in a UTxO with the global state as inline datum.

If the value has length 0, it means there is no global state for this programmable token.
For this reason, when creating a transfer transaction no reference input is expected to represent the global state.

If the bytestring has length greater than or equal to 28,
the value represents the concatenation of a token policy (of length 28)
and a token name (of length between 0 and 32).
In this case, when creating a transfer transaction a reference input having an NFT matching the unit MUST be included. 

#### `thirdPartyTransferLogicScript`

MUST be a bytestring of either length 0 or length 28.

It represents the optional hash of the "Withdraw 0" script that defines who is admin (third party) 
and the admin actions on the programmable token.

If the value has length 0, the programmable token does NOT allow admins to transfer programmable tokens on the users' behalf.

If the value has length 28, an admin can transfer users' tokens creating a transaction that executes this script.

### Programmable token registration

To create a new programmable token, it must be properly registered in the tokenRegistry.
The on-chain validation won't allow the creator to cheat or deviate from the enforced rules.

Recalling that the tokenRegistry is an ordered linked list sorted by the `tokenPolicy` field, the transaction to 
register the token has the following requirements:
1) The registryNode preceding the policy of the new token, called here prev_node, MUST be spent
2) The output of the transaction MUST include: 
    - prev_node with the value and the datum unchanged except for the field `nextTokenPolicy` that is now set to the new token `tokenPolicy`
    - a new registryNode representing the new token with the proper registryDatum fields, in particular `nextTokenPolicy` 
    is set to the input value of prev_node `nextTokenPolicy`
3) The transaction MUST include the registration certificate of `transferLogicScript`
4) The new registryNode `globalStateUnit` MAY be an empty string if the logic of
the programmable token does not require a global state;
otherwhise it MUST be a bytestring of length between
28 inclusive and 60 (28 + 32) exclusive.
5) The new registryNode SHOULD have the minimum amount of lovelaces that the protocol allows,
and MUST include a newly minted NFT, under the `registryMintingPolicy`,
and the programmable token policy as NFT name. 
6) Both the outputs MUST NOT have any reference script.
7) Both the outputs address MUST **only** have payment credentials.
8) The new token `issuancePolicy` MUST be an instance of the official script parametrized by a custom `issuanceLogicScript`

### Transfer
**TODO This section must be updated**

In order to spend an utxo holding programmable tokens,
a standard redeemer must be passed to the smart wallet:

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

Depending on the constructor used, for each programmable token, either the `transferManager` or the `thirdPartyActionRules` contract will be used respectively.

Independently of the constructor, the first field of the redeemer MUST include a list of indexes to be used on the reference inputs field.

The list MUST include one index for each non-lovelace token policy, programmable and not, present on the utxo's value.

The list order must match the lexicographic ordering of the value.

For example, the index at position 0 indicates the index of the reference input coming from the registry
that indicates the presence (or the absence) of the first policy of the input value.

(for reference, a typescript implementation of the lexicographic ordering can be found
[here](https://github.com/HarmonicLabs/uint8array-utils/blob/c1788bf351de24b961b84bfc849ee59bd3e9e720/src/utils/index.ts#L8-L27))

### Implementing programmable tokens in DeFi protocols
**TODO This section must be updated**

### Implementing programmable tokens in wallets and dApps
**TODO This section must be updated**

#### Existing substandards

**TODO This section must be updated**

In order to validate a transfer, transfer managers MAY need to read informations about the state of the users involved in the transaction.

However, depending on the implementation, said state MAY be managed in different ways.

Some examples of state management may be:

- no state
- one state per user involved in the spending, to be queried by NFT.
- one state per user involved in the transfer (both inputs and outputs), to be queried by NFT.
- a single reference input representing the root of a merkleized state.

And many more state managements are possible, depending on the specific implementation.

For this reason, we make explicit the need for sub standards

## Rationale: how does this CIP achieve its goals?
The current CIP version, informally called V3, is the result of several iterations to create the best standard for programmable tokens.
This standard safely extends the functionality of tokens on Cardano, in a scalable way and without disruptions, leveraging CNTs that live
forever in a single smart contract.

The proposal does not affect backward compatibilty being the first proposing a standard for programmability over transfers.

Existing native tokens are not conflicting with the standard, instead, native tokes are used in this specification for various purposes.

### History of the proposed standard
The [first proposed implementation](https://github.com/cardano-foundation/CIPs/pull/444/commits/525ce39a89bde1ddb62e126e347828e3bf0feb58) (which we could informally refer as v0) was quite different by the one shown in this document

Main differences were:
- [use of sorted merkle trees to prove uniqueness](https://github.com/cardano-foundation/CIPs/pull/444/commits/525ce39a89bde1ddb62e126e347828e3bf0feb58#diff-370b6563a47be474523d4f4dbfdf120c567c3c0135752afb61dc16c9a2de8d74R72) of an account during creation;
- account credentials as asset name

This path was abandoned due to the logaritmic cost of creation of accounts, on top of the complexity.

Other crucial difference with the first proposed implementation was in the `accountManager` redeemers;
which included definitions for `TransferFrom`, `Approve` and `RevokeApproval` redeemers, aiming to emulate ERC20's methods of `transferFrom` and `approve`;

After [important feedback by the community](https://github.com/cardano-foundation/CIPs/pull/444#issuecomment-1399356241), 
it was noted that such methods would not only have been superfluous, but also dangerous, and are hence removed in this specification.

After a first round of community feedback, a 
[reviewed standard was proposed](https://github.com/cardano-foundation/CIPs/pull/444/commits/f45867d6651f94ba53503833098d550326913a0f) 
(which we could informally refer to as v1).
[This first revision even had a PoC implementation](https://github.com/HarmonicLabs/erc20-like/commit/0730362175a27cee7cec18386f1c368d8c29fbb8), 
but after further feedback from the community it was noted that the need to spend an UTxO on the receiving side could cause UTxO contention 
in the moment two or more parties would have wanted to send a programmable token to the same receiver at the same time.

After "v1", another improved standard was proposed, informally referred to as "v2".
v2 proposed a standard interface for programmable tokens, based on the exsistence of 2 contracts: the `stateManager` and the `transferManager`.

By the v2 standard, each user must "register" to the policy by creating an utxo on the `stateManager` so that they could
spend programmable tokens using the `transferManager`

This soft requirement for registration was not well received from the community, and for this reason we are now at the "v3" version of the standard.

The specification proposed in this file addresses all the previous concerns.

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

- having at least one instance of the smart contracts described on:
    - mainnet
    - preview testnet
    - preprod testnet
- having at least 2 different wallets integrating programmable asset functionalities, mainly:
    - displayning balance of a specified programmable assets
    - independent transaction creation with `Transfer` redeemers

### Implementation Plan
- [ ] Issuance of at-least one smart token via the proposed standard on the following networks:
  - [ ] 1. Preview testnet
  - [ ] 2. Mainnet 
- [ ] End-to-end tests of programmable token logic. 
- [ ] Finally, a widely adopted wallet that can read and display programmable token balances to users and allow the user to conduct transfers of such tokens.

### Implementation Plan
- [ ] Implement the contracts detailed in the specification. 
- [ ] Implement the offchain code required to query programmable token balances and construct transactions to transfer such tokens. 

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
