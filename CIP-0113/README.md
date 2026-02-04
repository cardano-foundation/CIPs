---
CIP: 113
Title: Programmable token-like assets
Category: Tokens
Status: Proposed
Version: 3.0
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

## Specification Versions

**Current Version: 3.0** (This document)

This specification has evolved through community feedback:
- **Version 0** (deprecated) - Initial proposal with Merkle tree account uniqueness, included Approve/TransferFrom patterns
- **Version 1** (deprecated) - Removed Merkle trees, but had UTxO contention issues on receiver side
- **Version 2** (deprecated) - Introduced stateManager/transferManager pattern with user registration requirement
- **Version 3** (current) - Removed registration requirement, simplified to transferLogicScript pattern

Previous specification versions are available in the [deprecated/](./deprecated/) directory.

For detailed evolution history, see the [Rationale](#rationale-how-does-this-cip-achieve-its-goals) section.

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

### General Terms

The term "user" is used to indicate, interchangeably:
- "public key hash" credentials
- "script" credentials (smart contracts)

The term "creator" is used to indicate a user that creates a new programmable token.
The term "admin" is used to indicate a user that can execute privileged actions on a certain programmable token without explicit permission of the users.
The term "issuer" is used to indicate a user that can mint and/or burn a certain programmable token.

The term "policy" indicates a Cardano Native Token (CNT) policy, which is the hash of the script that can mint such token.
The term "unit" indicates the concatenation of a token policy and a token name to uniquely represent a certain CNT.

### Layer 1: Registry Components

These components form the infrastructure layer shared by ALL programmable tokens. They are deployed once and used by all tokens:

- `registry`: The on-chain registry where anyone can register new programmable tokens. It implements a sorted linked list pattern where entries are ordered by token policy. The registry ensures only properly configured programmable tokens can be registered.
    - `RegistryNode`: A node (or entry) in the registry. Each RegistryNode is a UTxO representing a specific programmable token with an inline datum containing all the token's configuration.
    - `registrySpendScript`: The Spend script that controls all RegistryNode UTxOs. It enforces the linked list invariants during insertions and modifications.
    - `registryMintingPolicy`: The Minting script for NFTs that mark valid RegistryNodes. Each RegistryNode contains a unique NFT minted by this policy, using the token's policy as the NFT name.

### Layer 2: Standard Components

These components form the common validation infrastructure shared by ALL programmable tokens:

- `programmableLogicBase`: The unique Spend script that holds all existing programmable tokens. All programmable tokens live at addresses with this script as the payment credential. This script acts as a gatekeeper, delegating actual validation to the programmableLogicGlobal stake validator.
- `programmableLogicGlobal`: The Stake validator that performs the actual validation logic for transfers and third-party actions. It is invoked via the withdraw-zero pattern when programmable tokens are spent from the programmableLogicBase script.
- `smart wallet`: The set of UTxOs living inside the programmableLogicBase script that belong to a specific user. Ownership is determined by the stake credential attached to the UTxOs, not the payment credential (which is always programmableLogicBase).

### Layer 3: Substandard Components

These components are token-specific and define the custom behavior of each programmable token. They are deployed per token and implement the "substandard":

- `transferLogicScript`: A token-specific Withdraw-0 script that implements the custom transfer logic for user-initiated transfers. This script validates whether a transfer is allowed based on the token's rules (e.g., whitelist checks, transfer limits, compliance rules).
- `thirdPartyTransferLogicScript`: A token-specific Withdraw-0 script that defines admin/third-party actions on the programmable token. This includes privileged operations like seizure, forced transfers, or emergency actions that can be executed without explicit user permission.
- `issuanceLogicScript`: A token-specific Withdraw-0 script that implements the custom minting/burning logic for the programmable token. It defines who can mint new tokens, under what conditions, and the burning rules.
- `issuanceMintingPolicy`: The Minting script that mints/burns programmable tokens. While the script code is shared across all programmable tokens, each deployment is token-specific because the policy is parameterized by the hash of the token's specific issuanceLogicScript.
- `globalState`: An optional token-specific unique UTxO whose datum contains global information regarding the token (e.g., if it's frozen, if transfers are paused, total supply, etc.). Not all tokens require a global state.
- `globalStateUnit`: The unit (policy + token name) of the NFT contained in the globalState UTxO. This NFT uniquely identifies the global state for a specific programmable token.

The term "substandard" indicates a specific implementation of all the token-specific components (Layer 3) that guarantees a certain behaviour and a consistent way to build transactions. Any programmable token MUST belong to a certain substandard, otherwise wallets and dApps don't know how to properly interact with them.

To know a user's smart wallet address, check the dedicated following section.

### High level flow

The creator wants to release a new programmable token.

The registry (along with registrySpendScript and registryMintingPolicy), programmableLogicBase, and programmableLogicGlobal are already deployed on-chain as the shared infrastructure (Layers 1 and 2).

The creator writes a new transferLogicScript where they define the rules to transfer the new token (e.g., whitelist checks, transfer limits).

(Optional) Then they write a new thirdPartyTransferLogicScript where they define who are the admins and what actions they can do without permission of any other user (e.g., seizure, forced transfers).

Then they write a new issuanceLogicScript where they define who can mint and burn the new token.

Then they deploy a new issuanceMintingPolicy instance parameterized by the hash of the new issuanceLogicScript.

Finally, the creator adds a RegistryNode to the registry with the hashes of all the above scripts and with additional required information. The registration cannot happen if the policy has already been registered or if the issuanceMintingPolicy is wrong.

During or after the registration process, the creator can mint the new programmable token. This new token is enforced to be sent to the programmableLogicBase script.

Off-chain, any user can deterministically derive their smart wallet address (as explained in the next section).

When a user wants to transfer some of their programmable tokens, the programmableLogicBase script delegates validation to the programmableLogicGlobal stake validator (via withdraw-zero pattern). For each token, a proof of registration (or non-registration) is required: if the policy is present in the registry then the associated transferLogicScript MUST be executed in the same transaction; if the policy is not present in the registry, the token is treated as a normal, non-programmable CNT and can always leave the programmableLogicBase script.

At any moment, for each token, admins can execute privileged actions as defined in the thirdPartyTransferLogicScript.

At any moment, for each token, issuers can mint more tokens or burn existing ones that are held by them.

### User's smart wallet address derivation

The smart wallet address has the following form:
(fixedPaymentCredentials, userDefinedStakeCredentials)

where:
- fixedPaymentCredentials never change, and they are the credentials obtained from the hash of programmableLogicBase
- userDefinedStakeCredentials are different for each user.
The smart wallet logic is the same for every user. If the user is a wallet, he MAY choose to user either their payment credentials or their stake credentials. We suggest to use his payment credentials to allow anyone to derive independently the address of the user.
If the user is a smart contract, then it's the payment credentials of that contract.

In other words, a smart wallet is the set of UTxOs that live in the programmableLogicBase script and that have a specific stake credential that identifies the owner.

### RegistryNode datum

Every entry in the registry MUST have attached an inline datum following this standard type:

```ts
type RegistryNode {
    key: ByteArray,
    next: ByteArray,
    transfer_logic_script: Credential,
    third_party_transfer_logic_script: Credential,
    global_state_cs: ByteArray
}
```

This datum is enforced by the execution of the registrySpendScript at registration.

The ordering of the fields MUST be respected.

#### `key`

MUST be a bytestring of length 28. This field is also the key of the RegistryNode
and the token name of the NFT minted via registryMintingPolicy and that is included in the RegistryNode UTxO.
This represents the currency symbol (policy) of the programmable token being registered.

#### `next`

MUST be a bytestring of length 28.

As the registry is an ordered linked list, this is the next key (a tokenPolicy) in the registry in lexicographic order.

#### `transfer_logic_script`

MUST be a Credential (either PubKeyCredential or ScriptCredential with a 28-byte hash).

Represents the credential of the "Withdraw 0" script to be executed in a transfer transaction for validation.
This script implements the custom logic for user-initiated transfers.

#### `third_party_transfer_logic_script`

MUST be a Credential (either PubKeyCredential or ScriptCredential with a 28-byte hash).

Represents the credential of the "Withdraw 0" script that defines who is an admin (third party)
and the admin actions on the programmable token.

This script is used for privileged actions (such as seizure or forced transfers) that can be executed without user permission.

#### `global_state_cs`

MUST be a bytestring of either length 0 or length 28.

It represents the optional currency symbol (policy ID) of an NFT that marks a UTxO containing the global state as inline datum.

If the value has length 0, it means there is no global state for this programmable token.
For this reason, when creating a transfer transaction no reference input is expected to represent the global state.

If the bytestring has length 28, it represents the policy ID of the NFT that uniquely identifies the global state UTxO.
In this case, when creating a transfer transaction a reference input containing an NFT with this policy MUST be included.

### Programmable token registration

To create a new programmable token, it must be properly registered in the registry.
The on-chain validation won't allow the creator to cheat or deviate from the enforced rules.

Recalling that the registry is an ordered linked list sorted by the `key` field, the transaction to
register the token has the following requirements:
1) The RegistryNode preceding the policy of the new token, called here prev_node, MUST be spent
2) The output of the transaction MUST include:
    - prev_node with the value and the datum unchanged except for the field `next` that is now set to the new token `key`
    - a new RegistryNode representing the new token with the proper RegistryNode datum fields, in particular `next`
    is set to the input value of prev_node `next`
3) The transaction MUST include the registration certificate of `transfer_logic_script`
4) The new RegistryNode `global_state_cs` MAY be an empty bytestring if the logic of
the programmable token does not require a global state;
otherwise it MUST be a bytestring of length 28.
5) The new RegistryNode SHOULD have the minimum amount of lovelaces that the protocol allows,
and MUST include a newly minted NFT, under the `registryMintingPolicy`,
with the programmable token policy as NFT name.
6) Both the outputs MUST NOT have any reference script.
7) Both the outputs address MUST **only** have payment credentials.
8) The new token `issuanceMintingPolicy` MUST be an instance of the official script parameterized by a custom `issuanceLogicScript`

### Transfer

In order to spend a UTxO holding programmable tokens from the programmableLogicBase script,
the programmableLogicGlobal stake validator MUST be invoked via the withdraw-zero pattern.
The redeemer passed to the programmableLogicGlobal stake validator follows this standard type:

```ts
type ProgrammableLogicGlobalRedeemer {
    TransferAct {
        registryProofs: List<RegistryProof>
    }
    ThirdPartyAct {
        seize_input_idx: Int,
        seize_output_idx: Int,
        registry_node_idx: Int
    }
}

type RegistryProof {
    TokenExists {
        node_idx: Int
    }
    TokenDoesNotExist {
        node_idx: Int
    }
}
```

#### Architecture: Delegation Pattern

The programmableLogicBase script is a lightweight gatekeeper that:
1. Accepts any redeemer (of type `Data`)
2. Verifies that the programmableLogicGlobal stake validator is invoked in the transaction
3. Delegates all validation logic to the programmableLogicGlobal stake validator

The programmableLogicGlobal stake validator performs the actual validation when invoked via withdraw-zero.

#### TransferAct Constructor

The `TransferAct` constructor is used when the owner of the programmable tokens wants to transfer them.
This represents the standard transfer flow initiated by the token owner.

When using this constructor:
1. The `registryProofs` field MUST contain a list of proofs, one for each non-lovelace token policy present in any spent UTxO from programmableLogicBase
2. For each proof of type `TokenExists`:
   - The corresponding RegistryNode MUST be included as a reference input at the specified index (`node_idx`)
   - The token's `transfer_logic_script` MUST be executed in the transaction (via withdraw-zero)
3. For each proof of type `TokenDoesNotExist`:
   - The covering RegistryNode MUST be included as a reference input at the specified index (`node_idx`)
   - The token is treated as a normal CNT and can be transferred without additional validation

#### ThirdPartyAct Constructor

The `ThirdPartyAct` constructor is used when an admin (third party) wants to execute privileged actions on programmable tokens
without the explicit permission of the token owner. This is specifically designed for **seizure operations** where tokens are removed from a user's smart wallet.

When using this constructor:
1. `seize_input_idx`: The index (in the transaction inputs) of the UTxO from programmableLogicBase being seized
2. `seize_output_idx`: The index (in the transaction outputs) of the resulting UTxO after seizure
3. `registry_node_idx`: The index (in reference inputs) of the RegistryNode for the token being seized

**Validation Requirements:**
- Only ONE input from programmableLogicBase is allowed (the seized input at `seize_input_idx`)
- The RegistryNode at `registry_node_idx` MUST exist and contain the token's configuration
- The token's `third_party_transfer_logic_script` MUST be executed in the transaction (via withdraw-zero)
- The output at `seize_output_idx` MUST:
  - Have the same address as the seized input
  - Have the same datum as the seized input
  - Contain the original value MINUS the seized tokens
- At least some tokens MUST be removed (to prevent DoS attacks)
- The authorization check for the stake credential is bypassed (admins don't need user permission)

#### RegistryProof Requirements

The `registryProofs` list MUST satisfy the following requirements:

1. **Completeness**: The list MUST include one proof for each distinct non-lovelace token policy present in any UTxO being spent from programmableLogicBase
2. **Ordering**: The list order MUST match the lexicographic ordering of the token policies.
   For example, if spending UTxOs contains policies A, B, and C (in lexicographic order),
   then `registryProofs[0]` is for policy A, `registryProofs[1]` for policy B, and `registryProofs[2]` for policy C
3. **Correctness**: Each proof must accurately represent the registration status of the corresponding token

(For reference, a TypeScript implementation of lexicographic ordering can be found
[here](https://github.com/HarmonicLabs/uint8array-utils/blob/c1788bf351de24b961b84bfc849ee59bd3e9e720/src/utils/index.ts#L8-L27))

#### Proving Registration Status

**TokenExists Proof**: To prove a token policy IS registered in the registry, include the RegistryNode with that exact `key` matching the token policy as a reference input.

**TokenDoesNotExist Proof**: To prove a token policy is NOT registered in the registry, include as a reference input the "covering node" - the RegistryNode whose `key` is the largest value that is still less than the token being proven absent, and whose `next` is greater than the token being proven absent.

For example:
- If the registry contains policies [A, C, E] and you want to prove policy D is not registered
- You must include the RegistryNode for policy C as a reference input (at `node_idx`)
- Because C < D < E (lexicographically), this proves D is not in the registry

#### programmableLogicGlobal Validation

The programmableLogicGlobal stake validator performs the following validation:

1. **Authorization Check** (TransferAct only): For each spent UTxO from programmableLogicBase:
   - If the stake credential is a public key hash, verify the transaction is signed by that key
   - If the stake credential is a script hash, verify that script is executed in the transaction
   - Exception: ThirdPartyAct bypasses this check (admins don't need user permission)

2. **Proof Validation** (TransferAct only): For each RegistryProof:
   - Verify the referenced RegistryNode exists at the specified index in reference inputs
   - For TokenExists: verify the RegistryNode's `key` matches the policy being validated
   - For TokenDoesNotExist: verify the covering node relationship (prev.key < unregistered < prev.next)

3. **Logic Script Execution**: For each registered programmable token:
   - TransferAct: verify the token's `transfer_logic_script` is executed (appears in withdrawals)
   - ThirdPartyAct: verify the token's `third_party_transfer_logic_script` is executed

4. **Output Validation**:
   - TransferAct: Verify all programmable tokens in outputs remain at programmableLogicBase addresses with valid stake credentials
   - ThirdPartyAct: Verify the output at `seize_output_idx` matches requirements (same address, datum, value minus seized tokens)

#### Additional Reference Inputs

Depending on the substandard and the specific programmable token implementation, additional reference inputs MAY be required:

1. **Global State**: If the RegistryNode's `global_state_cs` field is non-empty, a reference input containing an NFT with that policy MUST be included
2. **User State**: Depending on the substandard implementation, one or more reference inputs representing user state MAY be required. The exact requirements depend on the substandard (see "Existing substandards" section)

#### Security Considerations for Transfers

- The programmableLogicBase/programmableLogicGlobal split ensures all programmable tokens can only be spent if proper validation occurs
- The RegistryProof mechanism prevents bypassing transfer restrictions by claiming a token is unregistered when it actually is registered
- Third-party actions provide a mechanism for compliance (seizure, freezes) while maintaining clear on-chain definitions of admin powers
- The authorization check ensures users maintain control over their tokens (except when third-party actions are explicitly defined)
- ThirdPartyAct is limited to single-input operations to prevent DoS attacks and ensure predictable seizure behavior

### CIP-113 Version

A **CIP-113 version** is identified by the hash of the bootstrap transaction that initializes the framework (empty registry, protocol params, issuance script). This hash locks in all contract hashes for that deployment.

| Network | Bootstrap Tx Hash (Version) |
|---------|----------------------------|
| Preview | `61fae36e28a62a65496907c9660da9cf5d27fa0e9054a04581e1d8a087fbd93e` |

### Implementing programmable tokens in DeFi protocols
**TODO This section must be updated**

### Implementing programmable tokens in wallets and dApps

Wallets supporting programmable tokens MUST implement:
1. **Balance queries** — display programmable token holdings
2. **Transaction history** — track transfers in/out of user's smart wallet
3. **Native transfers** — build TransferAct transactions (optional, nice-to-have)

Admin operations (mint/burn/freeze/seize) are handled by token-specific dApps.

#### Address Derivation

Smart wallet address format: `(programmableLogicBase, userStakeCredential)`

The `userStakeCredential` can be derived from either the user's payment key or staking key. This is up to the team developing the substandard.

**Preview testnet parameters:**
```
programmableLogicBase script hash: f2182b00a37bd746e20575c9af01ab31312213514cd31e872e0a2a3e
registry address: addr_test1wr3z0me2xnj7crmvwwdkf8d02p2jjyhxpwecp23utf8ywus6w78q6
```

**Example derivation:**

Given user address `addr_test1qra006fdksqadv3z09a8lqf4aw8n62nmgkra9narr683x9rn2r00tud22p3ylwhk4s85764ndh5zdpnmfmfqleagml4qkhan0d`:
- Payment key hash: `faf7e92db401d6b222797a7f8135eb8f3d2a7b4587d2cfa31e8f1314`
- Staking key hash: `7350def5f1aa50624fbaf6ac0f4f6ab36de826867b4ed20fe7a8dfea`

| Stake Credential Source | Prog Token Address |
|------------------------|-------------------|
| Payment key | `addr_test1zreps2cq5daaw3hzq46untcp4vcnzgsn29xdx8589c9z50h67l5jmdqp66ezy7t607qnt6u08548k3v86t86x850zv2q8hv2dj` |
| Staking key | `addr_test1zreps2cq5daaw3hzq46untcp4vcnzgsn29xdx8589c9z50nn2r00tud22p3ylwhk4s85764ndh5zdpnmfmfqleagml4qe650tm` |

#### Balance Queries

Query UTxOs at the user's prog token address:

```bash
# Blockfrost API
curl -H "project_id: $BLOCKFROST_API_KEY" \
  "https://cardano-preview.blockfrost.io/api/v0/addresses/addr_test1zreps2cq5daaw3hzq46untcp4vcnzgsn29xdx8589c9z50nn2r00tud22p3ylwhk4s85764ndh5zdpnmfmfqleagml4qe650tm"
```

#### Identifying Programmable Tokens

To verify a token is programmable, check if its policy ID exists as a `key` in the registry:

```bash
# Query registry UTxOs
curl -H "project_id: $BLOCKFROST_API_KEY" \
  "https://cardano-preview.blockfrost.io/api/v0/addresses/addr_test1wr3z0me2xnj7crmvwwdkf8d02p2jjyhxpwecp23utf8ywus6w78q6/utxos"
```

For each UTxO, decode the inline datum — the `key` field contains the policy ID of a registered programmable token.

Example: policy `00216cc4179840e4d355e60cf071137e317d94a8de0fccf43b4b514a` is registered at tx `b0d4869018467a262b3df341f07350a86a38f08431041747f735d8712badf873` output index 2.

#### Transaction History

Follow balance changes at the user's prog token address to reconstruct transfer history.

#### Native Transfers

Example using [MeshSDK](https://meshjs.dev/):

```typescript
const txBuilder = new MeshTxBuilder({
  fetcher: provider,
  submitter: provider,
});

// Spend programmable token UTxOs
for (const utxo of selectedUtxos) {
  txBuilder
    .spendingPlutusScriptV3()
    .txIn(utxo.input.txHash, utxo.input.outputIndex)
    .txInScript(logic_base.cbor)
    .txInRedeemerValue(spendingRedeemer, "JSON")
    .txInInlineDatumPresent();
}

// Withdraw-zero pattern for transfer validation
txBuilder
  .withdrawalPlutusScriptV3()
  .withdrawal(substandard_transfer.reward_address, "0")
  .withdrawalScript(substandard_transfer._cbor)
  .withdrawalRedeemerValue(substandardTransferRedeemer, "JSON")

  .withdrawalPlutusScriptV3()
  .withdrawal(logic_global.reward_address, "0")
  .withdrawalScript(logic_global.cbor)
  .withdrawalRedeemerValue(programmableLogicGlobalRedeemer, "JSON")
  .requiredSignerHash(senderCredential.toString())

  // Outputs
  .txOut(changeAddress, [{ unit: "lovelace", quantity: "1000000" }]);

if (returningAmount > 0) {
  txBuilder
    .txOut(senderAddress, returningAssets)
    .txOutInlineDatumValue(tokenDatum, "JSON");
}

txBuilder
  .txOut(targetAddress, recipientAssets)
  .txOutInlineDatumValue(tokenDatum, "JSON")

  // Reference inputs (protocol params + registry)
  .readOnlyTxInReference(protocolParamsUtxo.input.txHash, protocolParamsUtxo.input.outputIndex)
  .readOnlyTxInReference(progTokenRegistry.input.txHash, progTokenRegistry.input.outputIndex)

  .txInCollateral(collateral.input.txHash, collateral.input.outputIndex)
  .selectUtxosFrom(walletUtxos)
  .changeAddress(changeAddress);

return await txBuilder.complete();
```

Full implementation with parameter derivation: [transfer.ts](https://github.com/cardano-foundation/cip113-programmable-tokens/blob/main/src/programmable-tokens-frontend/lib/mesh-sdk/transactions/transfer.ts#L25)

#### Existing substandards

Substandards define token-specific behavior (Layer 3 components). Each substandard MAY manage user state differently:
- no state
- one state per user involved in the spending, queried by NFT (e.g., sender must provide a reference input containing their whitelist NFT)
- one state per user involved in the transfer (inputs and outputs), queried by NFT (e.g., both sender and receiver must provide reference inputs proving KYC status)

**Available substandards:**

| Substandard | Description | Repository |
|-------------|-------------|------------|
| **Dummy Token** | Simplest possible programmable token — requires a specific redeemer to allow mint/burn/transfer. Useful for developers getting familiar with the prog token stack. | [dummy](https://github.com/cardano-foundation/cip113-programmable-tokens/tree/main/src/substandards/dummy) |
| **Freeze and Seize** | Simplified stablecoin contract with compliance features (freeze, unfreeze, seize). Useful for testing all prog token capabilities. | [freeze-and-seize](https://github.com/cardano-foundation/cip113-programmable-tokens/tree/main/src/substandards/freeze-and-seize) |
| **BaFin Standard** | Regulatory-compliant token standard developed by FluidTokens. | [fn-bafin-cardano-sc](https://github.com/FluidTokens/fn-bafin-cardano-sc) |

## Rationale: how does this CIP achieve its goals?
The current specification (Version 3.0) is the result of several iterations to create the best standard for programmable tokens.
This standard safely extends the functionality of tokens on Cardano, in a scalable way and without disruptions, leveraging CNTs that live
forever in a single smart contract.

The proposal does not affect backward compatibility being the first proposing a standard for programmability over transfers.

Existing native tokens are not conflicting with the standard, instead, native tokes are used in this specification for various purposes.

### History of the proposed standard
The [first proposed implementation](https://github.com/cardano-foundation/CIPs/pull/444/commits/525ce39a89bde1ddb62e126e347828e3bf0feb58) (Version 0) was quite different by the one shown in this document

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
(Version 1).
[This first revision even had a PoC implementation](https://github.com/HarmonicLabs/erc20-like/commit/0730362175a27cee7cec18386f1c368d8c29fbb8),
but after further feedback from the community it was noted that the need to spend an UTxO on the receiving side could cause UTxO contention
in the moment two or more parties would have wanted to send a programmable token to the same receiver at the same time.

After Version 1, another improved standard was proposed (Version 2).
Version 2 proposed a standard interface for programmable tokens, based on the exsistence of 2 contracts: the `stateManager` and the `transferManager`.

By the Version 2 standard, each user must "register" to the policy by creating an utxo on the `stateManager` so that they could
spend programmable tokens using the `transferManager`

This soft requirement for registration was not well received from the community, and for this reason we are now at Version 3.0 of the standard.

The specification proposed in this file addresses all the previous concerns.

## Path to Active

### Acceptance Criteria
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
