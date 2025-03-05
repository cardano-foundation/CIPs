---
CIP: 12
Title: On-chain stake pool operator to delegates communication
Status: Proposed
Category: Metadata
Authors:
  - Marek Mahut <marek.mahut@fivebinaries.com>
  - Sebastien Guillemot <sebastien@emurgo.io>
  - Ján Hrnko <jan.hrnko@fivebinaries.com>
Discussions:
  - https://forum.cardano.org/t/on-chain-stake-pool-operator-to-delegates-communication/42229
  - https://github.com/cardano-foundation/CIPs/pull/44
Created: 2020-11-07
License: CC-BY-4.0
---

## Abstract

Standard format for metadata used in an on-chain communication of stake pool owner towards their delegates.

## Motivation: why is this CIP necessary?

Stake pool owners and their delegates lack an on-chain communication standard between them.

[CIP-0006](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0006/README.md) already defines an external feed of a stake pool within the extended metadata. However, there is need for a more verifiable on-chain communication standard that will also provide additional cost associated with such communication to prevent its abuse.

## Specification

### Terminology

We define two types of communication metadata, which are distinguished by transaction metadata label as defined in [CIP-0010: Transaction metadata label registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/README.md):

 * *Message board communication* is a type of metadata that has been included in an on-chain transaction between two base addresses associated with a stake pool operator owner address. Given the onetime fee for this communication, we are considering this as a message board of a stake pool, as it also enables delegates to easier access historical metadata communication.

 * *Direct delegate communication* is a type of metadata that has been included in an on-chain transaction between a stake pool owner account and a delegate's account. This type of communication is more expensive for the stake pool owner, preventing higher abuse and therefore enables wallets to implement notification granularity. It might be suitable for targeting specific delegates, such as messaging only new joined delegates, loyal delegates, high-amount delegates etc.

As per CIP-0010, we assign:

* *Message board communication* transaction metadata label `1990`,
* *Direct delegate communication* transaction metadata label `1991`.

### Metadata

Metadata are written in JSON format and maximum size of metadata around 16KB.

The root object property is a 3 bytes UTF-8 encoded string representing the ISO 639-3
language code of the content.

| key                    | Value                                        | Rules                                      |
| ---------------------- | -------------------------------------------- | ------------------------------------------ |
| `title` *(required)*   | Title of the communication                   | 64 bytes UTF-8 encoded string              |
| `content` *(required)* | Content of the communication                 | An array of 64 bytes UTF-8 encoded strings |
|                        |                                              |
| `valid` *(optional)*   | Slot number the communication becomes valid  | Unsigned integer                           |
| `expires` *(optional)* | Slot number until the communication is valid | Unsigned integer                           |

#### Metadata JSON schema

The [schema.json](./schema.json) file defines the metadata.

#### Metadata example including the transaction metadata label

```
{
  "1991": [ {
    "lat": {
      "title": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do",
      "content": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do ",
        "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut e",
        "nim ad minim veniam, quis nostrud exercitation ullamco laboris n",
        "isi ut aliquip ex ea commodo consequat. Duis aute irure dolor in",
        " reprehenderit in voluptate velit esse cillum dolore eu fugiat n",
        "ulla pariatur. Excepteur sint occaecat cupidatat non proident, s",
        "unt in culpa qui officia deserunt mollit anim id est laborum."
      ],
      "valid": 10661033,
      "expire": 10669033
    }
   },
   {
    "eng": {
      "title": "But I must explain to you how all this mistaken idea",
      "content": [
        "But I must explain to you how all this mistaken idea of denounci",
        "ng of a pleasure and praising pain was born and I will give you ",
        "a complete account of the system, and expound the actual teachin",
        "gs of the great explorer of the truth, the master-builder of hum",
        "an happiness. No one rejects, dislikes, or avoids pleasure itsel",
        "f, because it is pleasure, but because those who do not know how",
        " to pursue pleasure rationally encounter consequences."
      ],
      "valid": 10661033,
      "expire": 10669033
    }
   }
  ]
}
```

## Rationale: how does this CIP achieve its goals?

The format of the `content` field is required to be an array of 64 bytes chunks, as this is the maximum size of a JSON field in the Cardano ledger. Tools, such as wallets, are required to recompose the content of the message.

The current Cardano protocol parameter for maximum transaction size, that will hold the metadata, is around 16KB.

### Backwards compatibility

No backwards compatibility breaking changes are introduced.

## Path to Active

### Acceptance Criteria

 * [ ] Indications that more than one wallet or backend supports this standard, including:
   * [ ] Yoroi (in progress from [Implement CIP12 to Yoroi backends](https://www.lidonation.com/en/proposals/implement-cip12-to-yoroi-backends))

### Implementation Plan

 * [x] Develop reference implementation ([CIP12 communication tool examples](https://github.com/fivebinaries/cip-metadata-communication-example))
 * [x] Offer this standard for implementation in downstream tools and wallets: pending their own decisions about whether and how to display communication messages.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
