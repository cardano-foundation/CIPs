---
CIP: 129
Title: Governance Identifiers
Status: Proposed
Category: Tools
Authors:
  - Ashish Prajapati <ashish@strica.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/845
  - https://github.com/cardano-foundation/CIPs/pull/857
Created: 2024-07-15
License: CC-BY-4.0
---

## Abstract

This Cardano Improvement Proposal (CIP) defines a standardized structure for encoding and representing various governance and credential identifiers, specifically designed for DRep, Constitutional Committee (CC) keys, and Governance Actions within the Conway era. This specification introduces a single-byte header that encapsulates metadata related to the key type and credential type, allowing identifiers to retain critical metadata even when stored as byte arrays. By encoding this metadata directly into the bech32 format, we enhance both usability and interoperability across Cardano infrastructure and tools.

## Motivation: Why is this CIP necessary?

The Conway era on Cardano introduces new governance features, requiring unique and identifiable credentials for roles such as DReps, Constitutional Committee members, and distinct governance actions. Existing infrastructure and tools that process bech32 identifiers often decode and store the raw byte data for efficiency, unintentionally stripping away the metadata embedded in the bech32 prefix. This CIP addresses that limitation by embedding metadata into a structured single-byte header, allowing credentials to be stored in byte form without losing essential metadata. This standardization facilitates seamless linkage, sharing, and compatibility of governance identifiers across the ecosystem, supporting a robust and interoperable governance framework in Cardano.

## Specification

### Introduction
We define a bytes representation for the various credentials and identifiers along with the their bech32 prefixes in this CIP. Taking inspiration from the Cardano addresses bytes format, we define an 8 bit header and a payload to define the key, which look similar to the reward address byte format but with a new specification and using the governance credentials.

In this CIP, We also define a simple bech32 prefix for gov actions, which does not have a credential. Gov actions only contain transaction ID bytes and an index, defined in the Gov Action Section below. The chosen prefixes for each identifier align with Cardano's established naming convention used in ledger specification, ensuring easy recognition and minimizing confusion within the ecosystem.

### Binary format

In the header-byte, bits [7;4] indicate the type of gov key being used. The remaining four bits [3;0] are used to define the credential type. There are currently 3 types of credentials defined in the Cardano Conway era, this specification will allow us to define a maximum of 16 different types of keys in the future.

```
  1 byte     variable length   
 <------> <-------------------> 
┌────────┬─────────────────────┐
│ header │        key      │
└────────┴─────────────────────┘
    🔎                          
    ╎          7 6 5 4 3 2 1 0  
    ╎         ┌─┬─┬─┬─┬─┬─┬─┬─┐ 
    ╰╌╌╌╌╌╌╌╌ |t│t│t│t│c│c│c│c│ 
              └─┴─┴─┴─┴─┴─┴─┴─┘ 
```

#### Key Type
There are currently 3 types of governance keys, and it is defined using the first half (bits [7;4]) of the header. The different types are summarized below,

Key Type (`t t t t . . . .`)      | Key
---                               | ---
`0000....`                        | CC Hot 
`0001....`                        | CC Cold
`0010....`                        | DRep

#### Credential Type

The second half of the header (bits [3;0]) refers to the credential type which can have the values and types as summarized in the table below,

We *reserve* the values 0 and 1 to prevent accidental conflicts with Cardano Address Network tags, ensuring that governance identifiers remain distinct and are not inadvertently processed as addresses.

Credential Type (`. . . . c c c c`)   | Semantic
---                                   | ---
`....0010`                            | Key Hash 
`....0011`                            | Script Hash

### Governance Action Identifiers

Cardano's Conway era introduces proposal procedures to submit governance actions. Governance actions are voted on by different kinds of credentials, and as such it is necessary to be able to share governance action identifiers across communication channels.

Governance action identifiers are defined via CIP-1694 as combination of a transaction ID it was submitted in and an index within the transaction.

We define a byte format to combine the transaction ID and the index to form a single valid byte string, as such it can be converted into a hex format and have its own Bech32 prefix.

Transaction ID is always a 32 byte length, hence we can append the index bytes to the transaction id, please see examples below:

#### Example 1

Original standard definition - `0000000000000000000000000000000000000000000000000000000000000000#17`

Transaction ID in Hex - `0000000000000000000000000000000000000000000000000000000000000000`

Governance Action index in Hex - `11` (number 17)

(CIP-129) Governance action ID in Hex - `000000000000000000000000000000000000000000000000000000000000000011`

(CIP-129) Governance action ID in Bech32 - `gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf`

#### Example 2

Original standard definition - `1111111111111111111111111111111111111111111111111111111111111111#0`

Transaction ID in Hex - `1111111111111111111111111111111111111111111111111111111111111111`

Governance Action index in Hex - `00` (number 0) 

(CIP-129) Governance action ID in Hex - `111111111111111111111111111111111111111111111111111111111111111100`

(CIP-129) Governance action ID in Bech32 - `gov_action1zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygsq6dmejn`

### Bech32 Encoding

| Prefix        | Meaning                                                 | Contents                                                          |
| ------------- | --------------------------------------------------------| ----------------------------------------------------------------- |
| `drep`        | DRep identifier                                         | DRep Credential                                                   |
| `cc_hot`      | CC Hot identifier                                       | CC Hot Credential                                                 |
| `cc_cold`     | CC Cold identifier                                      | CC Cold Credential                                                |
| `gov_action`  | gov action identifier                                   | gov action tx id concatenated with index                          |


### Identifier Test Vector

We can define a complete identifier as per the spec above by combining the header and the key, see below

#### Constitutional Committee Hot Credential

Key - `00000000000000000000000000000000000000000000000000000000`
Type - `Key Hash`

Identifier - `0200000000000000000000000000000000000000000000000000000000`

Bech32 - `cc_hot1qgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvcdjk7`

#### Constitutional Committee Cold Credential

Key - `00000000000000000000000000000000000000000000000000000000`
Type - `Script Hash`

Identifier - `1300000000000000000000000000000000000000000000000000000000`

Bech32 - `cc_cold1zvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6kflvs`

#### DRep Credential

Key - `00000000000000000000000000000000000000000000000000000000`
Type - `Key Hash`

Identifier - `2200000000000000000000000000000000000000000000000000000000`

Bech32 - `drep1ygqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq7vlc9n`

## Rationale: How does this CIP achieve its goals?

This CIP achieves its objectives by introducing a unified header and payload structure for governance-related keys, allowing for metadata to be directly embedded within the byte-level representation of each identifier. By defining a single-byte header that includes both key type and credential type, the proposal provides a consistent, compact format that retains crucial metadata even when stored or transmitted as raw byte arrays. This specification is designed to be forward-compatible, with a capacity to support up to 16 key types, allowing it to evolve with Cardano’s governance and credential requirements.

This approach aligns with existing Cardano address encoding practices while adding specificity for governance keys in the Conway era. By also defining distinct bech32 prefixes for each identifier type, the CIP enhances user-friendliness and makes it easier for tooling and infrastructure to recognize, validate, and link these identifiers within the ecosystem. This design ensures governance identifiers are not only interoperable across platforms but also intuitive and accessible, paving the way for streamlined governance interactions within Cardano’s tooling and community.


## Path to Active

### Acceptance Criteria
Tools, Wallets, and Explorers to utilize the identifiers and bech32 prefixes defined in this CIP for communication and view purposes.

- [ ] Requires updating Ledger nano app, and Trezor. The changes can be proposed once the CIP is merged.
- [ ] Tooling
  - [x] CNTools
  - [x] SPO Scripts
  - [x] typhonjs
  - [x] Gov Tools
  - [x] cardano-signer
- [ ] APIs
  - [x] Koios
  - [x] Cardanoscan API
  - [ ] Blockfrost
- [x] Explorers
  - [x] Cardanoscan.io
  - [x] AdaStat.net
- [ ] Wallets
  - [x] Eternl
  - [x] Typhon Wallet
  - [ ] Lace
  - [x] Gero

### Implementation Plan
- This CIP uses some bech32 prefixes which are already defined by CIP105 and ref by CIP005, This PR includes updates to both the CIPs with updated vector spec. The suggested changes align with the design of the original CIP005.

- For key generation tools - To move faster to this CIP, current tools which implement CIP105 based bech32 prefixes do not have to implement this CIP specification. They can change the prefix according to the updates suggested in this CIP, updating bech32 prefix will be a find and replace sort of an updated and it will instantly become compatible with this CIP.

- Tools like explorers and wallets - These tools can potentially support both formats to start with for the purpose of allowing users to search for drep, cold keys, hot keys as these 3 are impacted by this CIP upgrade. And can continue to show only this CIP specification, having an easy backward compatibility as well moving to this CIP standard.

- This CIP does not require a hard fork for implementation, the goal is to use the identifies specified in this CIP for the UI, and as a medium of communication for sharing such keys and IDs.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
