---
CIP: 160
Title: Receiving Script Purpose and Addresses
Category: Ledger
Status: Proposed
Authors:
    - Philip DiSarro <philipdisarro@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1063
Created: 2025-07-24
License: CC-BY-4.0
---

## Abstract

This CIP proposes the introduction of a new Address type, `ProtectedAddress`, and a corresponding `Receiving` script purpose. This enhancement allows a smart contract to validate not only UTxO spends from its address, but also UTxO creations to its address. The lack of such a mechanism today forces developers to implement complex workarounds involving authentication tokens, threaded NFTs, and registry UTxOs to guard against unauthorized or malformed deposits. This CIP aims to provide a native mechanism to guard script addresses against incoming UTxOs, thereby improving protocol safety, reducing engineering overhead, and eliminating a wide class of vulnerabilities in the Cardano smart contract ecosystem.

## Motivation: Why is this CIP necessary?

In Cardano’s current eUTxO model, smart contracts can enforce logic only when their locked UTxOs are being spent. They have no ability to reject or validate UTxOs being sent to them. This leads to a fundamental weakness: anyone can send arbitrary tokens and datum to a script address, potentially polluting its state or spoofing valid contract UTxOs. To mitigate this, developers today must:

- Mint authentication tokens
- Use threading tokens to track contract state
- Build registry systems with always-fails scripts
- Validate datums defensively with token-datum context coupling

These workarounds add significant complexity, on-chain cost, and surface area for bugs. A native mechanism to guard UTxO creations at a script address would eliminate the need for most of these patterns.

## Specification
We propose:

1. **A new address type**:

    ```haskell
    data Address = 
      Address
        { addressCredential         :: Credential
        -- ^ the payment credential
        , addressStakingCredential  :: Maybe StakingCredential
        -- ^ the staking credential
        }
      ProtectedAddress -- new 
        { address :: Credential 
        , addressStakingCredential  :: Maybe StakingCredential 
        }
    ```

2. **A new `ScriptPurpose`:**

    ```haskell
    data ScriptPurpose =
        Spending TxOutRef
    | Minting CurrencySymbol
    | Certifying DCert
    | Rewarding StakingCredential
    | Voting Vote
    | Proposing Proposal
    | Receiving ScriptHash         -- NEW: only output(s) to script
    ```

Normal addresses and protected addresses are differentiated by the introduction of an `isProtected` bit in the address header bytes, if the bit is set then the address is a protected address, otherwise it is unprotected.  

### Receiving validation rule

Any output to a protected address requires the witness for the payment credential of that address to be provided in the transaction. For outputs to protected addresses with public key payment credentials this means the transaction must be signed 
by the owner of that public key. For outputs to protected addresses with plutus script payment credentials this means the associated plutus script must be executed in phase-2 validation. 

During phase-2 script validation, for each transaction output to a `ProtectedAddress`, with a script payment credential the associated script must be executed using the script purpose:

- `Receiving` is used when the transaction includes an output to a `ProtectedAddress` where the payment credential is a script.

If any `Receiving` script **fails** during evaluation, the **entire transaction is invalid** and is rejected during phase-2 validation. 

### CDDL Extension

```cddl
; Extend ScriptPurpose with Receiving
redeemer_tag =
    0 ; spend    
  / 1 ; mint     
  / 2 ; cert     
  / 3 ; reward   
  / 4 ; voting   
  / 5 ; proposing
  / 6 ; receiving   ; NEW: script validates output creation to a ProtectedAddress
```

## Rationale: How does this CIP achieve its goals?

The proposed `ProtectedAddress` and `Receiving` script purpose solve the long-standing problem of uncontrolled UTxO injection at script addresses. By giving smart contracts the ability to validate outputs being sent to them during phase-2 validation, developers can:

- Ensure only valid state transitions or authenticated deposits are accepted
- Enforce access control and structural correctness of datums before a UTxO is created
- Remove the need for workaround patterns such as:
  - Authentication tokens
  - Threading/state tokens
  - The issues from cyclic depenencies that are inherent in both of the above. 

This CIP is also forward-compatible and additive. Existing contracts using unprotected `Address` remain unaffected. Contracts that require guarded output validation may opt-in by using `GuardScriptCredential`.

### Alternatives considered

- **Status quo**: Relying on auth tokens, thread tokens, and registry patterns introduces complexity, performance bottlenecks, and cyclic dependencies that are fragile and hard to audit. It has also led to serious exploits in real-world protocols due to misused or mishandled tokens.

- **Off-chain filtering**: While indexers and DApp backends can attempt to filter out junk UTxOs, they provide no on-chain security and cannot be relied on in adversarial environments or in composable settings.

- **Multivalidator pattern**: While technically feasible, this couples minting and spending logic into a single script, constrained by the 16KB script size limit. Furthermore, this introduces a huge layer of complexity and an associated attack surface. Managing the lifecycle of minted state tokens to prevent smuggling is extremely difficult, and becomes more impractical as the complexity of the dApp increases (ie. The attack surface for state token smuggling in a protocol that has 12 different validator scripts is nearly impossible to secure). In practice, this constraints the realm of what types of dApps are feasible on Cardano, you cannot build a cutting-edge financial instrument like AAVE, Balancer, or MakerDAO on Cardano because managing the lifecycle of dozens of state tokens across dozens of scripts while preventing smuggling is infeasible. 

### Backward Compatibility

This proposal can be **fully backward-compatible** with previous Plutus versions. There are no obvious issues with this. However, for extra-safety and to avoid any 
unintended consequences, it is also possible to strictly disallow Receiving scripts to be present in transactions that also execute scripts from Plutus versions before they
are introduced.

Wallets, nodes, and off-chain tooling must be updated to:
- Recognize and encode/decode `ProtectedAddress` addresses
- Include `Receiving` redeemers in transactions with outputs to `ProtectedAddress`s
- Extend phase-2 validation to evaluate `Receiving` scripts

Node software, CLI, Plutus libraries, and serialization tooling (e.g., `cardano-api`, `cardano-ledger`, `plutus-ledger-api`) would require coordinated upgrades.

## Path to Active

### Acceptance Criteria

- Agreement from Cardano Ledger and Plutus teams
- Implementation of:
  - `ProtectedAddress` in address serialization
  - `Receiving` in ledger script validation rules
  - `Receiving` in Plutus
  - Phase-2 validation for transactions with outputs to protected addresses
- Inclusion in a future era upgrade (e.g., Voltaire or beyond)

### Implementation Plan

1. Extend ledger types to introduce the `ProtectedAddress` type. 
2. Modify transaction validation logic to detect outputs to protected addresses and invoke appropriate scripts.
3. Introduce CDDL changes for redeemer tags and the new address variant.
4. Update transaction witnesses, CLI tooling, and Plutus interpreter to support `Receiving`.
5. Provide test cases for:
   - Correct execution of `Receiving` scripts
   - Rejection of transactions that include outputs to protected addresses and do not have the required witnesses or where the associated `Receiving` script execution fails. 
6. Provide examples and documentation for contract authors.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
