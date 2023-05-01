---
CIP: ?
Title: Proposal creation metadata
Category: Metadata
Status: Proposed
Authors:
    - Emily Martins <emily@liqwid.finance>
Implementors:
    - Agora
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/511
Created: 2023-05-01
License: CC-BY-4.0
---

## Abstract
On-chain governance on Cardano requires requires metadata in order to make the intentions of proposers visible. This CIP describes a metadata standard for proposal mint transactions to include that can be read by off-chain applications in a consistent way. On-chain implementation is not restricted or specified and the standard should be compatible with many on-chain governance implementations. The standard includes fields for title, description and voteable options of a proposal, but is not limited to just those, and may be extended in a future CIP.

## Motivation: why is this CIP necessary?
In on-chain governance implementation on the Cardano blockchain, there is a price to pay on including any auxiliary information in the datums that are included in the governance system. Many implemenations of the idea will as a result rely on fully off-chain implementation of voting. However, for even truly on-chain implementations, an argument is to be made that the proposal title and description are not necessary in the on-chain parts. They are a human component and have no consequences in future transactions, at least as far as enforcable constraints go. This extra information is however a quite critical defining point of a proposal. Two proposals may both have Yes/No votes, but their title will ultimately be the most important part. So they should live on-chain in some irrefutable way. The metadata field of a transaction is therefore the right place.

This CIP is necessary for ensuring this defining part of proposals does not go absent, become implemented in a vague way, or otherwise. Proposals being forced to adhere to this system means there is no point of argument around such a vital part of proposals. Additionally, the transparency added to proposals this way means various implementors can follow the same specification and display it in similar ways.

## Specification

A new metadata tag of **839** is proposed, which is added to any transaction that "creates" a proposal (the exact specifics of creation to be discussed shortly). This tag has three required fields:
| Field | Type  | Description | Can be IPFS |
|--|--|--|--|
| `title` | string | The title of the proposal  | **No** |
| `description` | string | The description of the proposal | **Yes** |
| `results` | list | The result options for the proposal, described below. | **No** |

### IPFS links
IPFS can be used in place of large descriptions where it may be useful. Due to the limitation of 64 character limit in on-chain metadata, this is particularly useful. IPFS links must be prefixed by `ipfs://` in fields that wish to use them. After this prefix, only the CID should be present. (Correct example: `ipfs://QmS9VN83tGH9j22tRSBvppWJAbFPMxdUvtdRdToYqadfQB`) Reliance on IPFS for proposals is in theory quite tricky for front-end implementation, which is why the title *must not* be available only as an IPFS hash. This way, even if the IPFS lookup is broken, an application that implements this spec can still use the title and display some information that identifies one proposal from another. When IPFS lookup is not working correctly, or not implemented for another reason, the application *should* make the actual CID available to the user.

### The use of markdown in `description`

While it is not strictly a requirement for implementation, the `description` field should be expected to include markdown formatting. An implementation *should* either strip the markdown altogether, or render it properly.

### Result list
In addition to the `title` and `description` fields, the `results` field must be present. This field is relevant in order to discern each of the options that a proposal can receive. This is useful in some governance implementations where, on-chain, options are associated in the datum with a number. In this case, the index into the array must associate to this mapping in the on-chain implementation. However, in governance systems where this isn't even a concern at all, it's still important to include this information. The `results` field is a list, each element being a record with the following required fields:
| Field | Type  | Description | Can be IPFS |
|--|--|--|--|
| `name` | string | The name of the result  | **No** |
| `description` | string | A description of what this result means | **Yes** |

Similarly to before, the `name` field must be present, but the `description` can be an IPFS link.

### Defining the creation transaction

The exact point at which a proposal is created isn't super well-defined in all cases. So the requirements are just that it must be in some way:
- unique: Two proposals can be distinguished in some way from one another. This can be through the datum, or a minting policy, or some other mechanism.
- identifiable: Finding the transaction for the creation of a proposal doesn't require complex datum-delving.
- governance-associated: Each governance instance must differ in some way from one another.

Implementing these requirements can be done through additional metadata fields as well.

### Extension

Implementations should not be rigid in interpreting this tag's contents, as various extensions may be applied over top of this. For example, one use case could be applying categories to proposals, or specific milestones. Due to the nature of the standard, these extensions necessarily are optional, and can help hydrate the information presented to the users.

## Rationale: how does this CIP achieve its goals?

The decisions made here are mostly a retroactive generalization of the approach taken in the implementation of the frontend in [Agora]'s [first instance](https://app.liqwid.finance/governance). This of course means that it is at risk of being too specific for this use case. However, I believe it is sufficiently general for any other on-chain governance implementation in the future to adopt, and due to Agora's open source nature, it should not exactly pose a threat to anything that may compete.

Additionally, since this is a metadata proposal with very little burden of implementation, it should not clash with any existing CIPs nor any in the future.

[Agora]: https://github.com/Liqwid-Labs/agora/

## Copyright

This CIP is licensed under [CC-BY-4.0].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
