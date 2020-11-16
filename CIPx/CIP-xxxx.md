---
CIP: ?
Title: On-chain stake pool operator to delegates communication
Authors: Marek Mahut <marek.mahut@fivebinaries.com>, Sebastien Guillemot <sebastien@emurgo.io>, Ján Hrnko <jan.hrnko@fivebinaries.com>
Comments-URI: https://forum.cardano.org/t/
Status: Draft
Type: Standards
Created: 2020-11-07
License: CC-BY-4.0
Requires: CIP10
---

## Abstract

Standard format for metadata used in on-chain stake pool owner communication towards their delegates.

## Terminology


We define two types of communication metadata, which are distinguished by the transaction metadata label as defined in the [CIP10 Transaction metadata label registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP10/README.md).

 * *Message board communication* is a type of metadata that has been included in a on-chain transaction between two base addresses associated with the stake pool operator owner address. Given the onetime fee for this communication, we are considering this as a message board of the stake pool, as it also enables delegates to easier access historical metadata communication.
 
 * *Direct delegate communication* is a type of metadata that has been included in an on-chain transaction between the stake pool owner account and the delegate's account. This type of communication is more expensive for the stake pool owner, preventing higher abuse and therefore enables wallets to implement notification granularity. It might be suitable for targeting specific delegates, such as messaging only new joined delegates, loyal delegates, high-amount delegates etc.



## Motivation

The lack of on-chain communication standard between the stake pool owner and their delegates. 

<!-- Link to CIP6 link once/if merged -->

Working in progrress [CIP6](https://github.com/cardano-foundation/CIPs/pull/15) defines an external feed of a stake pool within the extended metadata, but as an alternative, there is a need for more verifiable on-chain communication standard, that will also ensure associated cost with such communication to prevent its abuse. 

## Specification

As per [CIP10 Transaction metadata label registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP10/README.md), we assign:

* *Message board communication* the transaction metadata label `1990`,
* *Direct delegate communication* the transaction metadata label `1991`.

## Metadata

Metadata is written in a JSON format and the maximum size of the metadata is 16kb.

| key | Value | Rules |
| --- | ---  | --- |
| `title` *(required)*| Title of the communication | 64 bytes UTF-8 encoded string  |
| `content` *(required)*| Content of the communication | An array of 64 bytes UTF-8 encoded strings |
|||
| `language` *(optional)*| ISO 639-3 languange code of the content | 3 bytes UTF-8 encoded string
| `link` *(optional)*| Link for additional communication | 64 bytes UTF-8 encoded string, must be a valid URL |
| `expires` *(optional)* | Slot number until the communication is valid | Unsigned integer |

### Metadata JSON schema

The [schema.json](./schema.json) file defines the metadata inside the label.

### Metadata example including the transaction metadata label

```
{
  "1991": {
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
    "link": "https://example.com/blog.html",
    "language": "lat",
    "expire": 10669033
  }
}
```

## Rationale

The format of the `content` field as an array of 64 bytes chunks is required, as this is the maximum size of a JSON field in the Cardano ledger. Tools, such as wallets, are required to recompose the content of the message.

The Cardano ledger also imposes the metadata size of 16kb.


## Backwards compatibility

No backwards compatibility breaking changes are introduced.

## Reference implementation

We leave the decisions, such as what and how to display communication messages, up to downstream tools and wallets.

 * [Simple communication tool](https://github.com/fivebinaries/cip-metadata-communication-example)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
