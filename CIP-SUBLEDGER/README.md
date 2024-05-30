---
CIP: ?
Title: A Subledger in Plutus Enabling Native-Asset Seizure for Regulatory Compliance
Status: Proposed
Category: Ledger
Authors:
    - Micah Kendall <micah@butane.dev>
Implementors: [Micah Kendall, <you?>]
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-05-30
License: CC-BY-4.0
---

# CIP \*\*\*: A Subledger in Plutus Enabling Native-Asset Seizure for Regulatory Compliance

## Abstract
We aim to establish a simple standard to ensure native assets can exist in a locked smart contract system, referred to as the "subledger". This subledger will enable functionality defined in the minting policy to seize assets.

This design preserves the benefits of Cardano's native assets by enabling the reuse of most EUTxO patterns. It is significant that DEXs or other Plutus applications can be easily adapted to function within the subledger environment.

# Motivation: why is this CIP necessary?

A solution is required to enable asset seizure such as revoking USDC. We attempt to provide one in an EUTXO-harmonious style, for the sake of developer & user experience. 

# Specification
## Objectives
This CIP encompasses:
- An implementation of a smart contract system (subledger)
- The particular build & deployment of that smart contract
- A guide for usage and integration by SDKs, wallets, and the ecosystem

## Proposed Implementation

### Identifying Seizable Assets
- Seizable assets are identified by a prefix on the asset name.
  - To prevent 'accidental' membership in the seizure set, a long prefix and a checksum are recommended.

### Authorization of Seizure Capabilities
- Seizure capabilities are authorized via multi-validators on the asset policy (withdrawals).

### The RWA Script
We have a universal script, henceforth the "RWA Script", which maintains the capabilities of EUTXO by specifying in the datum either the signing key or the withdrawal that must be invoked in lieu of a spending validator.

#### Datum Structure
```rs
type Datum {
    // verification_key: check extra_signatories
    // script_hash: check for withdrawal of 0
    owner: Credential,
    datum: Data
    // usually empty, allows sane handling of seizure
    seized: Map<ByteArray, Int>
}
```

### Constraints on Spending
- Any assets in the UTxO must **remain** at a new UTxO in the RWA Script. They are only allowed to change the "owner" field; the `output.address.payment_credential` cannot change.
- This is enforced by folding over the input value set (at the script), the mint value, and the output values (at the script):
  - `input_values + mint_value - output_values`
  - Remove negatives
  - Any positives must not match the "prefix" condition that identifies seizable assets
- It is impossible to define clawback/seizure for existing assets, particularly for ADA. Hence we can ignore fee/withdrawals.

This guarantees that you can always utilize the policy-level functionality on the UTxOs.


### Policy-Level Functionality

#### Additional Constraint (Redeemer Endpoint)
- Value may be withdrawn from a UTxO.
- Must create a continuing output with the un-seized assets.
- Must insert the seized assets into the 'seized' map.
- For that value to be withdrawn, we must invoke the same minting policy those assets are under, except under the "withdrawal" endpoint. Typically, a withdrawal of 0 is used.

#### Redeemer Structure

```rs
type Redeemer {
    withdrawals: List<AdminSeizures>,
    extra: Data
}

type AdminSeizures {
    input_oref: OutputReference,
    assets: List<ByteArray>
}
```
- Where assets represent the list of asset names being withdrawn.
- The extra field is for arbitrary extra redeemer data
- Extra field example: could be used for a signed payload if it's an admin endpoint using a key.

## Development
The primary improvement for developers is the ability to specify all these "capabilities to freeze/unfreeze" externally to the user-level experience of transferring the UTxOs.

This script can be implemented without any parameterization of UTxOs or network-specific values, allowing us to compile, deploy, and spend to the same script hash across mainnet, testnets, and emulators.

For an enhanced developer experience, we should subject the implementation (in Aiken) to external analysis from the developer community before finalizing the exact instance to be enshrined in this CIP.

## Rationale: how does this CIP achieve its goals?

We accomplish the seizure capabilities on a technical basis, and the implementation style follows Keep-It-Simple-Stupid principles to minimise developer headache.

## Path to Active

### Acceptance Criteria
- [ ] An implementation must be provided that aligns with the CIP's textual description.
- [ ] The implementation (including code, build, and deployment) must undergo an external audit by a reputable firm.
- [ ] A basic example of a minting policy that supports asset seizures under the subledger protocol must be included.

### Implementation Plan
- [ ] Wait for high-level feedback
- [ ] Implement in Aiken
- [ ] Undergo further feedback
- [ ] Volunteer or Hire Audit

## Glossary

| Term                                            | Explanation                                                                                                                                        |
|-------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| **RWA (Real World Asset)**                      | Assets that exist in the physical world, such as real estate, commodities, or other tangible items, which are tokenized on the blockchain.         |
| **USDC (USD Coin)**                             | A stablecoin pegged to the US Dollar, used for trading and transactions on various blockchain platforms.                                           |
| **CIP (Cardano Improvement Proposal)**          | A formalized proposal for improvements or new features to be implemented on the Cardano blockchain.                                                |
| **Plutus**                                      | A smart contract platform on the Cardano blockchain that allows for the creation and execution of complex financial contracts.                     |
| **Smart Contract**                              | Self-executing contracts with the terms of the agreement directly written into code, running on a blockchain.                                      |
| **SDK (Software Development Kit)**              | A collection of software tools and libraries that developers use to create applications for specific platforms.                                    |
| **DEX (Decentralized Exchange)**                | A peer-to-peer marketplace where transactions occur directly between crypto traders without the need for an intermediary.                          |
| **EUTXO (Extended Unspent Transaction Output)** | An extension of the UTXO model used in Cardano, allowing for more complex transaction logic and smart contract capabilities.                       |
| **Datum**                                       | Data associated with a UTxO in a smart contract, used to store information necessary for the contract's execution.                                 |
| **Redeemer**                                    | Data provided when spending a UTxO, used to satisfy the conditions of a smart contract.                                                            |
| **Credential**                                  | An identifier used in the Cardano blockchain to represent ownership or authority over an asset or transaction.                                     |
| **OutputReference**                             | A reference to a specific UTxO, used in transactions to identify which outputs are being spent.                                                    |
| **AdminSeizures**                               | A structure representing the seizure of assets by an administrator, including references to the inputs and the assets being seized.                |
| **UTxO (Unspent Transaction Output)**           | A model used in blockchain transactions where outputs from previous transactions are used as inputs for new transactions.                          |
| **Minting Policy**                              | Rules and conditions defined in a smart contract that govern the creation and management of new tokens on the blockchain.                          |
| **Seizure**                                     | The act of taking control of assets, typically for regulatory compliance or enforcement purposes.                                                  |
| **Clawback Script**                             | A smart contract script that allows for the retrieval or seizure of assets under certain conditions, acting as a subledger within the main ledger. |
| **Subledger**                                   | A subset of the main ledger that tracks specific types of transactions or assets, often with additional rules or functionality.                    |
| **Script Hash**                                 | A unique identifier for a smart contract script, derived from the script's code and used to reference the script on the blockchain.                |
| **Mainnet**                                     | The primary, live blockchain network where real transactions occur and have real economic value.                                                   |
| **Testnet**                                     | A separate blockchain network used for testing and development, where transactions do not have real economic value.                                |
| **Emulator**                                    | A software tool that mimics the behavior of a blockchain network, used for testing and development purposes.                                       |

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
