---
CIP: 113
Title: Programmable token-like assets
Category: Tokens
Status: Proposed
Authors:
    - Michele Nuzzi <michele.nuzzi.2014@gmail.com>
    - Matteo Coppola <m.coppola.mazzetti@gmail.com>
    - Philip DiSarro <philipdisarro@gmail.com>
    - Giovanni Gargiulo <giovanni.gargiulo@cardanofoundation.org>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/444
    - https://github.com/cardano-foundation/CIPs/pull/944
Solution-To:
    - https://github.com/cardano-foundation/CIPs/blob/master/CPS-0003/README.md
Created: 2023-01-14
License: CC-BY-4.0
---

## Abstract

This CIP proposes a standard for programmable tokens.

We use the term "programmable tokens" to describe the family of tokens that require
the successful execution of a script in order to change owner.

## Motivation: Why is this CIP necessary?

Cardano native tokens (CNTs) are powerful but lack programmable transfer logic. Once minted, CNTs can move freely between addresses without restrictions. This limitation prevents implementing common token requirements such as:

- **Regulated stablecoins** — Issuers cannot enforce compliance rules, freeze accounts, or seize tokens for legal/regulatory reasons
- **Transfer restrictions** — No way to implement allowlists, denylists, or KYC requirements on token transfers
- **Tokenized securities** — Securities require transfer restrictions and regulatory compliance that CNTs cannot enforce

This CIP introduces programmable tokens — tokens that require successful script execution to change ownership. The standard enables these capabilities without a hard fork, using existing Cardano primitives (native tokens, stake credentials, withdraw-zero pattern).

The design addresses [CPS-0003](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0003/README.md) by providing:
- Deterministic smart wallet addresses for immediate wallet support
- An on-chain registry for discoverability
- No transition period required — programmable tokens are normal CNTs from the ledger's perspective
- Minimal cost impact via withdraw-zero validators

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

- `programmableLogicBase`: The unique Spend script that holds all existing programmable tokens. All programmable tokens live at addresses with this script as the payment credential. It is parameterized by the `protocolParameters` NFT policy. Its only job is to locate the protocol parameters, read the live `programmableLogicGlobal` credential from them, and require that credential's withdraw-zero. It runs once per programmable-token input, so its cost is multiplied by every such input in a transaction, which is why it performs no other work and inspects no token.
- `programmableLogicGlobal`: The Stake validator reached from `programmableLogicBase`. It is a dispatcher, not the validator of record: it is parameterized by the credentials of the action delegates (see below) and does exactly one thing — require that the delegate for the declared action was invoked in this transaction. All validation of an action is performed by that action's delegate.
- `action delegates`: The Withdraw-0 scripts that hold the protocol's actual validation logic, one per action — transfer, third-party action, and unfracking. Each delegate carries its own redeemer, in which the indices and proofs that action needs travel and are validated by the delegate itself.
- `protocolParameters`: A unique UTxO, marked by a one-shot NFT, whose inline datum holds the protocol's live wiring — the credentials of `programmableLogicGlobal`, of the protocol-level issuance logic, and of the transfer and third-party delegates. Because `programmableLogicBase` reads this wiring at runtime rather than being parameterized by it, the protocol's dispatch can be re-pointed without changing the address at which any token lives.
- `smart wallet`: The set of UTxOs living inside the programmableLogicBase script that belong to a specific user. Ownership is determined by the stake credential attached to the UTxOs, not the payment credential (which is always programmableLogicBase).

### Layer 3: Substandard Components

These components are token-specific and define the custom behavior of each programmable token. They are deployed per token and implement the "substandard":

- `transferLogicScript`: A token-specific Withdraw-0 script that implements the custom transfer logic for user-initiated transfers. This script validates whether a transfer is allowed based on the token's rules (e.g., allowlist checks, transfer limits, compliance rules).
- `thirdPartyLogicScript`: A token-specific Withdraw-0 script that defines third-party actions on the programmable token. Third parties are defined by the token's substandard: the standard places no constraint on who, if anyone, may invoke this script. This enables operations like seizure, forced transfers, auto-compounding, or other custom logic that can be executed without explicit user permission.
- `issuanceLogicScript`: A token-specific Withdraw-0 script that implements the custom minting/burning logic for the programmable token. It defines who can mint new tokens, under what conditions, and the burning rules.
- `issuanceMintingPolicy`: The Minting script that mints/burns programmable tokens. While the script code is shared across all programmable tokens, each deployment is token-specific because the policy is parameterized by (1) the credential of the token's own minting logic — the substandard's Withdraw-0 script, which is the per-token entropy in the resulting policy — and (2) the policy of the protocol parameters NFT, which is shared infrastructure. Note the split of responsibilities: this policy is permanent, while the protocol-level `issuanceLogicScript` it defers to is read live from the protocol parameters and is therefore replaceable.
- `globalState`: An optional token-specific unique UTxO whose datum contains global information regarding the token (e.g., if it's frozen, if transfers are paused, total supply, etc.). Not all tokens require a global state.
- `globalStateUnit`: The unit (policy + token name) of the NFT contained in the globalState UTxO. This NFT uniquely identifies the global state for a specific programmable token.

The term "substandard" indicates a specific implementation of all the token-specific components (Layer 3) that guarantees a certain behaviour and a consistent way to build transactions. Any programmable token MUST belong to a certain substandard, otherwise wallets and dApps don't know how to properly interact with them.

To know a user's smart wallet address, check the dedicated following section.

### High level flow

The creator wants to release a new programmable token.

The registry (along with registrySpendScript and registryMintingPolicy), programmableLogicBase, programmableLogicGlobal, the action delegates and the protocol parameters UTxO are already deployed on-chain as the shared infrastructure (Layers 1 and 2). The creator deploys none of these and is not required to know their hashes: the wiring is read from the protocol parameters at validation time.

The creator writes a new transferLogicScript where they define the rules to transfer the new token (e.g., allowlist checks, transfer limits).

(Optional) Then they write a new thirdPartyLogicScript where they define who can execute third-party actions and what those actions are (e.g., seizure, forced transfers, auto-compounding).

Then they write a new issuanceLogicScript where they define who can mint and burn the new token.

Then they deploy a new issuanceMintingPolicy instance parameterized by the credential of their own minting logic script and by the protocol parameters policy.

Finally, the creator adds a RegistryNode to the registry with the hashes of all the above scripts and with additional required information. The registration cannot happen if the policy has already been registered or if the issuanceMintingPolicy is wrong.

During or after the registration process, the creator can mint the new programmable token. This new token is enforced to be sent to the programmableLogicBase script.

Off-chain, any user can deterministically derive their smart wallet address (as explained in the next section).

When a user wants to transfer some of their programmable tokens, the programmableLogicBase script delegates validation to the programmableLogicGlobal stake validator (via withdraw-zero pattern). For each token, a proof of registration (or non-registration) is required: if the policy is present in the registry then the associated transferLogicScript MUST be executed in the same transaction; if the policy is not present in the registry, the token is treated as a normal, non-programmable CNT and can always leave the programmableLogicBase script.

At any moment, for each token, third parties can execute actions as defined in the thirdPartyLogicScript.

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
    minting_logic_script: Credential,
    transfer_logic_script: Credential,
    third_party_logic_script: Credential,
    unfracking_logic_script: Credential,
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

#### `minting_logic_script`

MUST be a Credential (either PubKeyCredential or ScriptCredential with a 28-byte hash).

Represents the credential of the "Withdraw 0" script implementing the token's minting and burning
logic. The substandard's minting logic locates its own RegistryNode by equality on this field, which
yields the token's `key` (its policy) without recomputing the issuance hash.

This field cannot lie: at registration the `registry` validator cryptographically binds it to the
policy being registered (see the "Programmable token registration" section).

#### `transfer_logic_script`

MUST be a Credential (either PubKeyCredential or ScriptCredential with a 28-byte hash).

Represents the credential of the "Withdraw 0" script to be executed in a transfer transaction for validation.
This script implements the custom logic for user-initiated transfers.

#### `third_party_logic_script`

MUST be a Credential (either PubKeyCredential or ScriptCredential with a 28-byte hash).

Represents the credential of the "Withdraw 0" script that defines who can execute third-party actions
and what those actions are on the programmable token.

This script is used for actions (such as seizure, forced transfers, or auto-compounding) that can be executed without explicit user permission.

#### `unfracking_logic_script`

MUST be a Credential (either PubKeyCredential or ScriptCredential with a 28-byte hash).

Represents the credential whose "Withdraw 0" MUST be invoked by any unfracking action touching this
policy — the issuer-declared constraint hook for holder-driven, same-owner restructuring of a smart
wallet's UTxOs.

The default is least-permission: an empty PubKeyCredential means unfracking is FORBIDDEN for this
policy. A ScriptCredential delegates the decision to the issuer's hook validator. A
PubKeyCredential gives signature-gated unfracking, since a withdrawal against a public-key reward
account requires that key's signature.

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
3) Any credential whose Withdraw-0 is invoked MUST already have its reward account registered on
the ledger, that being a prerequisite for a withdrawal to appear in a transaction at all. This is not
checked by the registry: it is a ledger requirement, and it applies to the substandard's minting logic
here because registration invokes it. Note that the Withdraw-0 scripts of this standard permit
registration of their own credential and refuse every other certificate, so such an account can be
brought into service but cannot afterwards be deregistered or delegated, and therefore cannot be
disabled out from under the scripts that depend on it
4) The new RegistryNode `global_state_cs` MAY be an empty bytestring if the logic of
the programmable token does not require a global state;
otherwise it MUST be a bytestring of length 28.
5) The new RegistryNode SHOULD have the minimum amount of lovelaces that the protocol allows,
and MUST include a newly minted NFT, under the `registryMintingPolicy`,
with the programmable token policy as NFT name.
6) Both the outputs MUST NOT have any reference script.
7) Both the outputs address MUST **only** have payment credentials.
8) The new token `issuanceMintingPolicy` MUST be an instance of the official script parameterized by
the creator's own minting logic credential and by the protocol parameters policy. This is enforced
cryptographically rather than by declaration: see below.

#### Registry redeemer and the binding of policy to logic

The `registryMintingPolicy` takes the following redeemer:

```ts
type RegistryRedeemer {
    RegistryInit
    RegistryInsert { key: ByteArray, minting_logic_script: Credential }
}
```

- `RegistryInit` initialises the registry with the origin node, once, at bootstrap.
- `RegistryInsert` registers a new programmable token policy. `key` is the policy being registered
  and `minting_logic_script` is the credential of the substandard's minting logic.

On insertion the registry enforces three things:

1. The new RegistryNode's `minting_logic_script` datum field MUST equal the credential named in the
   redeemer, so a registrar cannot declare one credential and write another into the datum.
2. The official issuance script, parameterized with that credential, MUST hash to `key`. The
   parameter's hash is derived inside the validator and is not supplied as a redeemer field, so
   collision resistance of the hash function — not a runtime equality check — is what forces the
   policy and its minting logic to agree.
3. The substandard's minting logic MUST be invoked in the registering transaction, i.e. its
   credential appears in the transaction's withdrawals.

To perform (2) the validator reconstructs the expected policy from a reference input carrying the
official issuance script's byte layout:

```ts
type IssuanceCborHex {
    prefix_cbor_hex: ByteArray,
    postfix_cbor_hex: ByteArray
}
```

The expected policy is the hash of `prefix_cbor_hex` followed by the parameter hash followed by
`postfix_cbor_hex`, and it MUST equal `key`.

A registration MAY, but need NOT, carry a first mint of the new token in the same transaction.
Registering with no mint is valid and is the expected shape for real-world-asset issuance and for
supply-aware substandards that must initialise global state before any token exists. A substandard
requiring a strict register-then-mint lifecycle MUST enforce that in its own minting logic.

### Transfer

In order to spend a UTxO holding programmable tokens from the programmableLogicBase script,
the programmableLogicGlobal stake validator MUST be invoked via the withdraw-zero pattern.
The redeemer passed to the programmableLogicGlobal stake validator follows this standard type:

```ts
type ProgrammableLogicGlobalRedeemer {
    TransferAct
    ThirdPartyAct
    UnfrackingAct
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

The arms carry no payload. Everything an action needs — registry proofs, node indices, output
offsets — travels in the redeemer of that action's delegate, where the delegate validates it.
Repeating any of it in the dispatcher's redeemer would create a second, unchecked claim about the
same fact, and forcing the two to agree would require the dispatcher to decode the delegate's
redeemer, which is the work this split exists to avoid.

The delegate redeemers are:

```ts
type TransferRedeemer {
    proofs: List<RegistryProof>
}

type ThirdPartyRedeemer {
    registry_node_idx: Int,
    outputs_start_idx: Int
}

type UnfrackingRedeemer {
    registry_node_idx: Int,
    outputs_start_idx: Int
}
```

#### Architecture: Delegation Pattern

Validation is delegated along a chain of four links, each of which narrows what the next one may be:

```
programmableLogicBase -> protocolParameters -> programmableLogicGlobal -> action delegate
```

1. `programmableLogicBase` runs once per programmable-token input being spent. It locates the
   protocol parameters UTxO among the reference inputs, reads one field from its datum — the live
   `programmableLogicGlobal` credential — and requires that credential's withdraw-zero. It makes no
   decision about the action being performed and never inspects a token.
2. `programmableLogicGlobal` is parameterized at compile time by the credentials of the action
   delegates. It reads the declared action from its redeemer and requires that action's delegate to
   have been invoked. It performs no validation of its own.
3. The action delegate validates the action.

The redeemer of `programmableLogicBase` is:

```ts
type BaseSpendRedeemer {
    params_idx: Int,
    wdrl_idx: Int
}
```

- `params_idx`: the index of the protocol parameters UTxO in the transaction's reference inputs.
- `wdrl_idx`: the index of the `programmableLogicGlobal` credential's entry in the transaction's
  withdrawal map, which the ledger orders script credentials first and bytewise within each kind.

Both fields are hints that the validator resolves and then checks, rather than values it trusts. A
wrong `params_idx` or `wdrl_idx` resolves to something other than what the validator requires and the
check fails, so a dishonest hint can only invalidate its own transaction. This is the general
discipline for indices throughout this standard: the caller states where a thing is, and the
validator confirms that it is what was claimed, so correctness never depends on the hint being
honest.

Because the protocol parameters are read at runtime, a mandatory reference input holding the
protocol parameters NFT is required by every transaction spending programmable tokens.

**Actions.** The standard defines three actions, each with its own delegate and its own redeemer:

| Action | Purpose |
|---|---|
| `TransferAct` | An ordinary transfer, initiated by the holder |
| `ThirdPartyAct` | An action performed without the holder's consent, as permitted by the token's `third_party_logic_script` |
| `UnfrackingAct` | Holder-driven restructuring of the holder's own UTxOs, leaving ownership unchanged, as constrained by the token's `unfracking_logic_script` |


#### TransferAct Constructor

The `TransferAct` constructor is used when the owner of the programmable tokens wants to transfer them.
This represents the standard transfer flow initiated by the token owner.

When using this action, the `transfer` delegate's `TransferRedeemer` is filled as follows:
1. The `proofs` field MUST contain a list of proofs, one for each distinct non-lovelace token policy
present in any spent UTxO from programmableLogicBase **or** in `tx.mint`. Minted and burned values are
folded into the same accumulator as spent values, so one list validates both
2. For each proof of type `TokenExists`:
   - The corresponding RegistryNode MUST be included as a reference input at the specified index (`node_idx`)
   - The token's `transfer_logic_script` MUST be executed in the transaction (via withdraw-zero)
3. For each proof of type `TokenDoesNotExist`:
   - The covering RegistryNode MUST be included as a reference input at the specified index (`node_idx`)
   - The token is treated as a normal CNT and can be transferred without additional validation
**Output Value Calculation:**
The expected output value at programmableLogicBase addresses is the sum of validated input programmable token value **plus** validated mint value. This enables:
- **Partial burn during transfer**: e.g., input 100 tokens, burn 30, output 70
- **Minting during transfer**: e.g., input 100 tokens, mint 50, output 150

#### ThirdPartyAct Constructor

The `ThirdPartyAct` constructor is used when a third party wants to execute actions on programmable tokens
without the explicit permission of the token owner. Third parties are defined by the token's substandard: the standard places no constraint on who, if anyone, may invoke this script. This is commonly used for **seizure operations** but can support any custom logic defined by the token's substandard.

This constructor supports **multiple UTxOs** in a single transaction for batch operations.

When using this action, the `third_party` delegate's `ThirdPartyRedeemer` is filled as follows:
1. `registry_node_idx`: The index (in reference inputs) of the `RegistryNode` for the token being acted upon
2. `outputs_start_idx`: The index in `tx.outputs` at which the paired continuing outputs begin

**Input/Output Pairing**

The delegate walks `tx.inputs` in order. Every input at a programmableLogicBase address is paired
with the next consecutive output, starting from `tx.outputs[outputs_start_idx]`; inputs at other
addresses are skipped and consume no output. The *n*-th programmableLogicBase input encountered is
therefore paired with `tx.outputs[outputs_start_idx + n]`.

Outputs before `outputs_start_idx` are not paired with any input, but any programmable tokens of the
subject policy that they hold at programmableLogicBase addresses still count toward the output side
of the balance invariant below. This lets a third-party action share a transaction with other actions
that produce earlier programmableLogicBase outputs.

**Validation Requirements:**
- The RegistryNode at `registry_node_idx` MUST exist and contain the token's configuration
- The token's `third_party_logic_script` MUST be executed in the transaction (via withdraw-zero)
- For each input/output pair:
  - The output MUST have the same address as the input
  - The output MUST have the same datum as the input
  - Non-policy assets (i.e., all assets except the seized token's policy) MUST be exactly equal between input and output
  - The seized policy's tokens MUST actually change between input and output (to prevent DoS attacks with no-op seizures)
- The authorization check for the stake credential is bypassed (third parties don't need user permission)

**Balance Invariant:**
Instead of requiring each paired output to contain the input value minus seized tokens, the validator enforces a global balance invariant: the total output of the seized policy's tokens across **all outputs at programmableLogicBase** MUST be greater than or equal to the total input tokens of that policy (adjusted for mints/burns). This ensures seized tokens stay within the programmable token system and enables:
- **Partial seizure**: Seize some tokens from an owner while leaving others (e.g., seize 40 of 100 tokens, leaving 60 with the owner)
- **Wipe** (seize + burn): Seize tokens and burn them in the same transaction via `tx.mint` with negative quantities. The burn reduces the expected output accordingly
- **Top-up** (seize + mint): Seize tokens and mint additional ones in the same transaction

The adjusted input for the balance check is computed as: `total_input_policy_tokens + tx.mint_policy_tokens`, filtering out non-positive entries. Authorization for minting/burning is enforced separately by the `issuanceMintingPolicy` validator and the Cardano ledger.

#### UnfrackingAct Constructor

The `UnfrackingAct` action lets a holder restructure the programmableLogicBase UTxOs they already own
for **one** registered policy, without transferring anything to anyone. Ownership does not change.

The motivating case is a "fracked" UTxO holding several policies at once: a restriction scoped to one
of them — a freeze, say — immobilises every other token sharing that UTxO. Acting on the restricted
policy moves its tokens into their own UTxO and leaves everything else spendable.

When using this action, the `unfracking` delegate's `UnfrackingRedeemer` is filled as follows:
1. `registry_node_idx`: The index (in reference inputs) of the `RegistryNode` for the acted-on policy
2. `outputs_start_idx`: The index in `tx.outputs` at which the paired continuing outputs begin

**Requirements:**
- Exactly one policy is acted on per action, named by the RegistryNode at `registry_node_idx`
- The acted-on policy's `unfracking_logic_script` MUST be invoked via withdraw-zero. Least permission
  is the default: where that field is an empty public-key credential there is no such script, no
  transaction can satisfy the requirement, and unfracking is forbidden for that policy. Issuers opt
  in explicitly, and a token carrying state constrains its own restructuring through this hook
- The holder MUST authorise the action, by the same rule as a transfer: a signature where the stake
  credential is a public key, or execution of the script where it is a script
- Inputs and outputs are paired positionally, as in `ThirdPartyAct`. For each pair, the address, the
  datum, the reference script and the tokens of **every** policy other than the acted-on one MUST be
  byte-identical between input and output. Ada may move freely
- The acted-on policy MUST be stripped **entirely**: present in the input, absent from the continuing
  output. A partial strip MUST be rejected — a continuing output still holding the acted-on policy
  would still require that policy's transfer proof on every later spend, which defeats the purpose,
  and any partial same-owner rebalancing is a transfer, to be validated by that policy's transfer
  logic rather than through this path

#### RegistryProof Requirements

The `proofs` list MUST satisfy the following requirements:

1. **Completeness**: The list MUST include one proof for each distinct non-lovelace token policy present in any UTxO being spent from programmableLogicBase **or** in `tx.mint`
2. **Ordering**: The list order MUST match the lexicographic ordering of the token policies.
   For example, if spending UTxOs contains policies A, B, and C (in lexicographic order),
   then `proofs[0]` is for policy A, `proofs[1]` for policy B, and `proofs[2]` for policy C
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

#### Validation performed by the action delegates

`programmableLogicGlobal` validates nothing itself: it requires that the declared action's delegate
was invoked, and the delegate named below performs the validation for that action. The numbering
below is therefore a description of each delegate's obligations, not of steps taken by a single
script.

1. **Authorization Check** (TransferAct only): For each spent UTxO from programmableLogicBase:
   - If the stake credential is a public key hash, verify the transaction is signed by that key
   - If the stake credential is a script hash, verify that script is executed in the transaction
   - Exception: ThirdPartyAct bypasses this check (third parties don't need user permission)

2. **Proof Validation** (TransferAct only): For each RegistryProof in `proofs`, which covers spent and minted or burned policies alike:
   - Verify the referenced RegistryNode exists at the specified index in reference inputs
   - For TokenExists: verify the RegistryNode's `key` matches the policy being validated
   - For TokenDoesNotExist: verify the covering node relationship (prev.key < unregistered < prev.next)

3. **Logic Script Execution**: For each registered programmable token, the delegate verifies that the
   token's own substandard script for this action is executed, i.e. appears in the transaction's
   withdrawals:
   - TransferAct: the token's `transfer_logic_script`
   - ThirdPartyAct: the token's `third_party_logic_script`
   - UnfrackingAct: the token's `unfracking_logic_script`. A registry node whose
     `unfracking_logic_script` is an empty public-key credential has no such script, so no unfracking
     action can satisfy this requirement and unfracking is thereby forbidden for that policy

4. **Output Validation**:
   - TransferAct: Verify that outputs at programmableLogicBase addresses contain at least the expected programmable token value (validated input value + validated mint value). All programmable tokens in outputs MUST remain at programmableLogicBase addresses with valid stake credentials
   - ThirdPartyAct: Verify input/output pair constraints (same address, same datum, unchanged non-policy assets, changed policy tokens) and enforce the balance invariant (total output policy tokens at programmableLogicBase >= total input policy tokens adjusted for mints/burns)

#### Reference Inputs

Every transaction spending programmable tokens MUST include:

1. **Protocol parameters**: the UTxO holding the protocol parameters NFT. `programmableLogicBase`
   reads the live `programmableLogicGlobal` credential from its datum on every such transaction, and
   addresses it by `params_idx` in the `BaseSpendRedeemer`
2. **Registry nodes**: one RegistryNode for each policy requiring a registry proof, as described in
   the RegistryProof requirements above

Depending on the substandard and the specific programmable token implementation, additional reference inputs MAY be required:

3. **Global State**: If the RegistryNode's `global_state_cs` field is non-empty, a reference input containing an NFT with that policy MUST be included
4. **User State**: Depending on the substandard implementation, one or more reference inputs representing user state MAY be required. The exact requirements depend on the substandard (see "Existing substandards" section)

#### Security Considerations for Transfers

- The programmableLogicBase/programmableLogicGlobal split ensures all programmable tokens can only be spent if proper validation occurs
- The RegistryProof mechanism prevents bypassing transfer restrictions by claiming a token is unregistered when it actually is registered
- Minted and burned programmable tokens are validated against the registry via the same `proofs` list as spent tokens, since mint value is folded into the input accumulator, preventing unvalidated tokens from bypassing the directory check
- Third-party actions provide a mechanism for compliance (seizure, freezes, wipe) while maintaining clear on-chain definitions of third-party capabilities
- The balance invariant ensures seized tokens remain within the programmable token system (at programmableLogicBase addresses) and cannot escape to external addresses
- The authorization check ensures users maintain control over their tokens (except when third-party actions are explicitly defined)
- ThirdPartyAct supports batch operations on multiple UTxOs while requiring policy token changes to prevent DoS attacks

### Protocol upgradability

The credentials that make up a deployment are held in the protocol parameters datum as data, rather
than being compiled into the scripts that consume them. A deployment can therefore be re-pointed
without redeploying the tokens that depend on it.

**What MAY be re-pointed.** The `programmableLogicGlobal` credential, the protocol-level issuance
logic credential, and the action delegate credentials. Replacing any of these takes effect for every
programmable token at once, since each is read live at validation time.

**What MUST NOT move.** The `programmableLogicBase` credential is the payment credential of every
smart wallet address in the deployment. Changing it would relocate every holder's funds, so it is not
part of the upgradable surface; a deployment that needs a different one is a different deployment,
identified by its own bootstrap transaction. The token-minting policy of an individual programmable
token is likewise permanent, which is what allows a token's identity to survive an upgrade of the
logic that governs it.

**Authorisation.** The right to perform an upgrade is itself a credential recorded in the protocol
parameters. The standard does not prescribe what that credential is: a single key, a multi-signature
arrangement, a governance mechanism, or a script implementing any other rule all satisfy it equally,
and the choice is a property of the deployment rather than of CIP-113. Implementations MUST document
which they use.

**Requirements on the upgrade path.** A conforming deployment MUST satisfy the following, whatever
authority it chooses:

1. A change of the upgrade authority MUST be two-phase: a nomination, then a separate promotion of
   the standing nominee. Replacing the authority in a single step risks handing control to a
   credential that does not exist or cannot act, which is unrecoverable.
2. The promotion MUST be authorised by the nominee itself, which is the evidence that the incoming
   authority exists, can act, and consents.
3. A change of protocol wiring MUST NOT carry a change of the upgrade authority, and vice versa, so
   that an authority handover is always visible on chain as a transaction of its own rather than as
   a rider on a parameter change.
4. Each upgrade transaction MUST declare which of these it is, so that each may be validated as one
   closed rule set.

**Consequences for integrators.** Because delegate credentials are read live, an integrator holding
a programmable token cannot assume that the logic which validated a past transfer is the logic that
will validate the next one. Where that matters, the protocol parameters UTxO — not a cached script
hash — is the authority on the current wiring, and the upgrade authority recorded there is the
correct subject of any trust assessment of a deployment.

### CIP-113 Version

A **CIP-113 version** is identified by the hash of the bootstrap transaction that initializes the framework (empty registry, protocol params, issuance script). This hash locks in all contract hashes for that deployment.

| Network | Bootstrap Tx Hash (Version) |
|---------|----------------------------|
| Preview | `61fae36e28a62a65496907c9660da9cf5d27fa0e9054a04581e1d8a087fbd93e` |

### Implementing programmable tokens in DeFi protocols

Programmable tokens are compatible with existing DeFi infrastructure. They are standard CNTs that live at the `programmableLogicBase` script address rather than user-controlled addresses.

#### DEX Integration

For AMM-style DEXes (e.g., Minswap, SundaeSwap):

1. **Liquidity Provision**: LP tokens involving programmable tokens MUST be sent to the user's smart wallet address
2. **Swaps**: Transactions MUST include the `transferLogicScript` withdrawal (via withdraw-zero pattern) and the relevant `registryNode` as reference input
3. **Batcher Integration**: Batchers can process programmable token swaps by including all required reference inputs and batching multiple CIP-113 transfers in a single transaction

Example implementation: [Minswap CIP-113 DEX](https://minswap-cip113-dev.fluidtokens.com/)

#### Lending Protocols

1. **Collateral**: Protocols receive tokens at a smart wallet address they control; `transferLogicScript` validation applies during deposit/withdrawal
2. **Liquidations**: Liquidation transactions MUST include proper registry proofs
3. **Substandard Considerations**: Protocols SHOULD verify the substandard before accepting tokens — some (e.g., freeze-and-seize) permit third-party actions that move tokens without the holder's consent, which could affect collateral

#### Yield Aggregators and Vaults

Vaults manage programmable tokens by:
1. Receiving deposits at the vault's smart wallet address
2. Moving tokens between protocols with proper validation on each transfer
3. Sending withdrawals to users' smart wallet addresses

#### Token Management dApps

Token issuers use dedicated dApps for policy creation, minting, and third-party operations.

Example implementation: [CIP-113 Policy Manager](https://cip113-policy-manager-dev.fluidtokens.com/)

#### Transaction Construction

DeFi protocols constructing transactions with programmable tokens MUST:
1. Include the protocol parameters UTxO as a reference input, and address it by `params_idx` in each
   `programmableLogicBase` input's redeemer
2. Include `registryNode` as reference input for each programmable token policy (or proof of non-registration)
3. Execute the `programmableLogicGlobal` withdrawal (amount = 0) declaring the action, and address its
   position in the withdrawal map by `wdrl_idx` in each `programmableLogicBase` input's redeemer
4. Execute the withdrawal (amount = 0) of the delegate for that action, carrying the delegate's own
   redeemer
5. Execute `transferLogicScript` withdrawal (amount = 0) for each programmable token
6. Send programmable tokens ONLY to properly derived smart wallet addresses (`programmableLogicBase` as payment credential, owner's stake credential)

Steps 1 and 3 are easy to omit when adapting an existing integration, because neither is visible in
the token's own configuration: both are properties of the deployment, read at validation time.

#### Gas Efficiency

Programmable token transactions have additional script execution costs:
- Each unique policy requires one registry proof
- The `transferLogicScript` execution adds to transaction fees
- Batching multiple transfers of the same token is more efficient than separate transactions
- `programmableLogicBase` runs once per programmable-token input, so its cost scales with the number
  of such inputs rather than with the number of policies
- Each action loads only its own delegate. The transfer delegate is on the path of every ordinary
  transfer; third-party and unfracking transactions reference their own delegate instead and do not
  load the transfer delegate

#### Security Considerations

1. **Substandard Verification**: Verify the substandard before integration by reviewing its `thirdPartyLogicScript`, answering two independent questions: (a) *what* actions can it authorise without the holder's consent (freeze, seize, forced transfer, rebase, etc.), and (b) *who* can trigger them. A script may be permissioned, permissionless, or restricted to actions that cannot reduce a holder's balance; the standard does not constrain this, so neither question can be answered from CIP-113 alone
2. **Registry Integrity**: Verify using the canonical registry; monitor for spoofing attempts
3. **Smart Wallet Security**: Users retain full control via stake credentials; protocols cannot access funds without proper validation

### Implementing programmable tokens in wallets and dApps

Wallets supporting programmable tokens MUST implement:
1. **Balance queries** — display programmable token holdings
2. **Transaction history** — track transfers in/out of user's smart wallet
3. **Native transfers** — build TransferAct transactions (optional, nice-to-have)

Issuance and third-party operations (mint/burn/freeze/seize) are handled by token-specific dApps.

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
- one state per user involved in the spending, queried by NFT (e.g., sender must provide a reference input containing their allowlist NFT)
- one state per user involved in the transfer (inputs and outputs), queried by NFT (e.g., both sender and receiver must provide reference inputs proving KYC status)

**Available substandards:**

| Substandard | Description | Repository |
|-------------|-------------|------------|
| **Dummy Token** | Simplest possible programmable token — requires a specific redeemer to allow mint/burn/transfer. Useful for developers getting familiar with the prog token stack. | [dummy](https://github.com/cardano-foundation/cip113-programmable-tokens/tree/main/src/substandards/dummy) |
| **Freeze and Seize** | Simplified stablecoin contract with compliance features (freeze, unfreeze, seize). Useful for testing all prog token capabilities. | [freeze-and-seize](https://github.com/cardano-foundation/cip113-programmable-tokens/tree/main/src/substandards/freeze-and-seize) |
| **BaFin Standard** | Regulatory-compliant token standard developed by FluidTokens. | [fn-bafin-cardano-sc](https://github.com/FluidTokens/fn-bafin-cardano-sc) |

Where a substandard's `thirdPartyLogicScript` requires signatures from a designated key set — as
the freeze-and-seize substandard does — that key set is referred to as the substandard's *admin*. This is a
property of that individual substandard and not of CIP-113: the standard fixes no permissioning for the
`thirdPartyLogicScript`, which MAY be permissioned, permissionless (e.g., an auto-compounding
rebase any user can trigger), or restricted to actions that cannot reduce a holder's balance. Integrators
MUST therefore determine a token's third-party capabilities and its trigger authority from its substandard,
never from CIP-113 conformance alone.

## Rationale: how does this CIP achieve its goals?
The current specification (Version 3.0) is the result of several iterations to create the best standard for programmable tokens.
This standard safely extends the functionality of tokens on Cardano, in a scalable way and without disruptions, leveraging CNTs that live
forever in a single smart contract.

The proposal does not affect backward compatibility being the first proposing a standard for programmability over transfers.

Existing native tokens are not conflicting with the standard, instead, native tokes are used in this specification for various purposes.

### History of the proposed standard

This specification has evolved through community feedback:

| Version | Status | Description |
|---------|--------|-------------|
| [0](./deprecated/v0.md) | deprecated | Initial proposal with Merkle tree account uniqueness, included Approve/TransferFrom patterns |
| [1](./deprecated/v1.md) | deprecated | Removed Merkle trees, but had UTxO contention issues on receiver side |
| [2](./deprecated/v2.md) | deprecated | Introduced stateManager/transferManager pattern with user registration requirement |
| 3 | **current** | Removed registration requirement, simplified to transferLogicScript pattern |

[Version 0](./deprecated/v0.md) used sorted Merkle trees to prove account uniqueness and included `TransferFrom`, `Approve` and `RevokeApproval` redeemers to emulate ERC20 patterns. This was abandoned due to logarithmic cost of account creation and [community feedback](https://github.com/cardano-foundation/CIPs/pull/444#issuecomment-1399356241) noting these methods were superfluous and dangerous.

[Version 1](./deprecated/v1.md) removed Merkle trees but required spending a UTxO on the receiver side, causing contention when multiple parties sent to the same receiver simultaneously.

[Version 2](./deprecated/v2.md) introduced `stateManager` and `transferManager` contracts, requiring users to "register" before spending programmable tokens. This registration requirement was not well received.

Version 3 (current) addresses all previous concerns by removing the registration requirement and simplifying to the `transferLogicScript` pattern.

### Versioning

Minor improvements, clarifications, or security fixes to this specification should be proposed via pull request to this CIP.

Major redesigns that accomplish the same goals but with a fundamentally different approach should be proposed as a new CIP, clearly highlighting the limitations addressed or improvements made over this specification.

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
