---
CIP: ????
Title: Cardano Governance Identifier
Status: Proposed
Category: Wallets
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

This specification describes the structure and the bech32 format of the identifiers for DRep, CC keys, and Gov Actions

## Motivation: why is this CIP necessary?

Cardano Conway era introduces new credentials for different actors, and introduces proposal procedures for governance actions. It is required to be able to find, link, share these identifiers in bytes form across the tooling and community.

## Specification

### Introduction
We define a bytes representation for the various credentials and identifiers along with the their bech32 prefixes in this CIP. Taking inspiration from the Cardano addresses bytes format, we define an 8 byte header and a payload to define the key, which look similar to the reward address byte form but with a new specification and using the governance credentials.

In this CIP, We also define a simple bech32 prefix for gov actions, which does not have a credential. Gov actions only contain transaction ID bytes and an index, defined in the Gov Action Section below.

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

We *reserve* the values 0 and 1, as these are used in the Cardano Address Network tag. By not using these values we will make the gov identifies not become accidentally compatible with a valid address.

Credential Type (`. . . . c c c c`)   | Semantic
---                                   | ---
`....0010`                            | Key Hash 
`....0011`                            | Script Hash

### Gov Action

Cardano Conway era introduces proposal procedures to submit gov actions. Gov actions are vote on chain by different kinds of keys, and as such it is necessary to be able to share gov actions across communication channels. The gov action is currently defined as combination of a transaction ID it was submitted in and an index within the transaction.

We define a byte format to combine the tx ID and the index to form a single valid byte string, as such it can be converted into a hex format and have its own bech32 prefix.

Transaction ID is always a 32 byte length, hence we can append the index bytes to the tx id, please see below


TX ID in Hex - `0000000000000000000000000000000000000000000000000000000000000000`
Gov Action index in HEX - `11` (number 17)

gov action ID - `000000000000000000000000000000000000000000000000000000000000000011`

bech32 - `gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf`

## Bech32 Encoding

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

## Rationale: how does this CIP achieve its goals?

By introducing a header and payload design for different keys, we can achieve specifying credentials in a hex format (bytes), being able to share and use across tooling is possible. We also specify bech32 prefixes for user friendly identification of the identifiers.


## Path to Active

### Acceptance Criteria

- [] implemented by various tools

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).