---
CIP: ????
Title: Guard Script Purpose and Credential
Category: Ledger
Status: Proposed
Authors:
    - Philip DiSarro <philipdisarro@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/???
Created: 2025-07-24
License: CC-BY-4.0
---

## Abstract

This CIP proposes the introduction of a new script credential type, `GuardScriptCredential`, and a corresponding `Guard` script purpose. This enhancement allows a smart contract to validate not only UTxO spends from its address, but also UTxO creations to its address. The lack of such a mechanism today forces developers to implement complex workarounds involving authentication tokens, threaded NFTs, and registry UTxOs to guard against unauthorized or malformed deposits. This CIP aims to provide a native mechanism to guard script addresses against incoming UTxOs, thereby improving protocol safety, reducing engineering overhead, and eliminating a wide class of vulnerabilities in the Cardano smart contract ecosystem.

## Motivation: why is this CIP necessary?

In Cardano’s current eUTxO model, smart contracts can enforce logic only when their locked UTxOs are being spent. They have no ability to reject or validate UTxOs being sent to them. This leads to a fundamental weakness: anyone can send arbitrary tokens and datum to a script address, potentially polluting its state or spoofing valid contract UTxOs. To mitigate this, developers today must:

- Mint authentication tokens
- Use threading tokens to track contract state
- Build registry systems with always-fails scripts
- Validate datums defensively with token-datum context coupling

These workarounds add significant complexity, on-chain cost, and surface area for bugs. A native mechanism to guard UTxO creations at a script address would eliminate the need for most of these patterns.

## Specification
We propose:

1. **A new credential type**:
   ```haskell
   data Credential =
       KeyCredential PubKeyHash
     | ScriptCredential ScriptHash
     | GuardScriptCredential ScriptHash -- new
   ```
2. **Two new `ScriptPurpose`s:**
   ```haskell
    data ScriptPurpose =
        Spending TxOutRef
    | Minting CurrencySymbol
    | Certifying DCert
    | Rewarding StakingCredential
    | Voting Vote
    | Proposing Proposal
    | Guarding ScriptHash         -- NEW: only output(s) to script
    | GuardingContinuing ScriptHash -- NEW: both input(s) and output(s)
   ```

**Guard validation rule:**
During phase-2 script validation, for each transaction output to a `GuardScriptCredential`, the associated script must be executed using one of two new script purposes:

- `Guarding` is used when the transaction includes one or more outputs to the script, but no inputs from it.
- `GuardingContinuing` is used when the transaction includes both inputs and outputs involving the same `GuardScriptCredential`.

This separation ensures that input-side and output-side logic can remain cleanly isolated. Output validation logic can be entirely handled within `Guarding` and `GuardingContinuing`, while spending logic can be isolated to the `Spending` script purpose.

Critically, this design avoids redundant script execution. Without it, spending scripts would need to inspect transaction outputs in every case — even when no guarding logic is necessary — leading to wasted validation effort and bloated execution budgets.

If any `Guarding` or `GuardingContinuing` script **fails** during evaluation, the **entire transaction is invalid** and is rejected during phase-2 validation.

### CDDL Extension

```cddl
; Extend Credential with GuardScriptCredential
credential = 
  [ 0, addr_keyhash             ; KeyCredential
  // 1, script_hash             ; ScriptCredential
  // 2, script_hash             ; GuardScriptCredential (NEW)
  ]

; Extend ScriptPurpose with Guarding
redeemer_tag =
    0 ; spend    
  / 1 ; mint     
  / 2 ; cert     
  / 3 ; reward   
  / 4 ; voting   
  / 5 ; proposing
  / 6 ; guarding   ; NEW: script validates output creation to GuardScriptCredential
```

## Rationale: how does this CIP achieve its goals?

The proposed `GuardScriptCredential` and `Guard` script purpose solve the long-standing problem of uncontrolled UTxO injection at script addresses. By giving smart contracts the ability to validate outputs being sent to them during phase-2 validation, developers can:

- Ensure only valid state transitions or authenticated deposits are accepted
- Enforce access control and structural correctness of datums before a UTxO is created
- Remove the need for workaround patterns such as:
  - Authentication tokens
  - Threading/state tokens
  - The issues from cyclic depenencies that are inherent in both of the above. 

This CIP is also forward-compatible and additive. Existing contracts using `ScriptCredential` remain unaffected. Contracts that require guarded output validation may opt-in by using `GuardScriptCredential`.

### Alternatives considered

- **Status quo**: Relying on auth tokens, thread tokens, and registry patterns introduces complexity, performance bottlenecks, and cyclic dependencies that are fragile and hard to audit. It has also led to serious exploits in real-world protocols due to misused or mishandled tokens.

- **Off-chain filtering**: While indexers and DApp backends can attempt to filter out junk UTxOs, they provide no on-chain security and cannot be relied on in adversarial environments or in composable settings.

- **Multivalidator pattern**: While technically feasible, this couples minting and spending logic into a single script, constrained by the 16KB script size limit. Furthermore, this introduces a huge layer of complexity and an associated attack surface. Managing the lifecycle of minted state tokens to prevent smuggling is extremely difficult, and becomes more impractical as the complexity of the dApp increases (ie. The attack surface for state token smuggling in a protocol that has 12 different validator scripts is nearly impossible to secure). In practice, this constraints the realm of what types of dApps are feasible on Cardano, you cannot build a cutting-edge financial instrument like AAVE, Balancer, or MakerDAO on Cardano because managing the lifecycle of dozens of state tokens across dozens of scripts while preventing smuggling is infeasible. 

### Backward Compatibility

This proposal can be **fully backward-compatible** with previous Plutus versions. There are no obvious issues with this. However, for extra-safety and to avoid any 
unintended consequences, it is also possible to strictly disallow Guarding scripts to be present in transactions that also execute scripts from Plutus versions before they
are introduced.

Wallets, nodes, and off-chain tooling must be updated to:
- Recognize and encode/decode `GuardScriptCredential` addresses
- Include `Guarding` redeemers in transactions with guarded outputs
- Extend phase-2 validation to evaluate `Guarding` scripts
- Address decoding/encoding that correctly identifies the new credential

Node software, CLI, Plutus libraries, and serialization tooling (e.g., `cardano-api`, `cardano-ledger`, `plutus-ledger-api`) would require coordinated upgrades.


### Acceptance Criteria

- Agreement from Cardano Ledger and Plutus teams
- Implementation of:
  - `GuardScriptCredential` in address serialization
  - `Guarding` in ledger script validation rules
  - `Guarding` and `GuardingContinuing` in Plutus
  - Phase-2 validation for guarded outputs
- Inclusion in a future era upgrade (e.g., Voltaire or beyond)

### Implementation Plan

1. Extend ledger types to introduce the `GuardingScriptCredential` type. 
2. Modify transaction validation logic to detect guarded outputs and invoke appropriate scripts.
3. Add redeemer indexing logic for `Guarding` purposes tied to `txOutputs`.
4. Introduce CDDL changes for redeemer tags and address credential variants.
5. Update transaction witnesses, CLI tooling, and Plutus interpreter to support `Guarding`.
6. Provide test cases for:
   - Correct execution of `Guarding` scripts
   - Rejection of invalid guarded outputs
7. Provide examples and documentation for contract authors.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
