---
CIP: 107
Title: URI Scheme - Block and transaction objects
Status: Proposed
Category: Tools
Authors:
    - Pi Lanningham <pi@sundaeswap.finance>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/556
Created: 2020-09-22
License: CC-BY-4.0
---

## Abstract

This extends CIP-13, which describes a Cardano URI scheme, with several more objects that would be useful to be able to assign addresses to, in particular blocks, transactions, transaction metadata, and transaction outputs.

## Motivation: why is this CIP necessary?

CIP-13 defined two initial URL authorities, for payment links and delegating to a stakepool.

However, in a number of contexts, it would be useful to canonically link to other Cardano objects, such as:
- Providing links to a transaction, to be opened in a wallet or chain explorer of the users choice
- To provide richly interconnected metadata, such as in [CIP-100](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100)

Without a canonical standard for how to define these URIs, these objects are either unaddressable, not machine-interpretable, or will suffer from a divergence of convention. Similarly, we seek to fit an existing structure, such as CIP-0013, to reduce the number of different conventions that need be supported by the ecosystem.

## Specification

We extend CIP-13 with 2 new authorities for referencing blocks and transactions.

Examples:
```
web+cardano://block?hash=c6a8976125193dfae11551c5e80a217403d953c08ebbd69bba904d990854011f
web+cardano://block?height=12345678890
web+cardano://transaction/7704a68404facf7126fa356f1b09f0e4c552aeef454cd0daba4208f3a64372e9
web+cardano://transaction/7704a68404facf7126fa356f1b09f0e4c552aeef454cd0daba4208f3a64372e9#1
web+cardano://transaction/7704a68404facf7126fa356f1b09f0e4c552aeef454cd0daba4208f3a64372e9/metadata
web+cardano://transaction/d3616b772c91f118346e74863d1722810a4858e4d7cc7663dc2eed345d7bca72/metadata/674
web+cardano://transaction/self/metadata/1694
```

### Grammar & interpretation

We extend the grammar from CIP-0013 with two new authorities:

```
authorityref = (... | blockref | transactionref)
```

#### Block queries

A link referencing a block by either block hash or height.

> WARNING: Referencing blocks by height is provided in the case of extremely tight space requirements, but referencing a recent block (within the rollback horizon of the chain) is unstable.  Due to chain re-orgs, it may refer to different content for different users, or at different times. This should only be used when this is not critical, or for blocks outside of the rollback horizon.

```
blockref = "//block" query
query = ( "?block=" block_hash | "?height=" block_height)

block_hash = 64HEXDIG
block_height = *digit
```

#### Transaction queries

A link referencing *this* transaction, another transaction, transaction output, the full transaction metadata, or specific tag within the transaction metadata.

```
transactionref = "//transaction/" (tx_id | utxo_id | tx_metadata | tx_metadata_tag)

tx_id = "self" | 64HEXDIG
utxo_id = tx_id "#" *digit
tx_metadata = tx_id "/" metadata
tx_metadata_tag = tx_id "/" metadata "/" *digit
```

> NOTE: tx_id can be set to "self", which is useful for making self-referential metadata, before the transaction ID is known.  For example, in CIP-100, you may want to store governance metadata on the transaction which casts the vote. The transaciton hash is not yet known, and so the `anchor` field cannot link to the transaction by transaction ID. 

For grammar reference, see:

  - [Wikipedia > Augmented Backus–Naur form](https://en.wikipedia.org/wiki/Augmented_Backus%E2%80%93Naur_form)
  - [RFC 2234: Augmented BNF for Syntax Specifications: ABNF](https://datatracker.ietf.org/doc/html/rfc2234)
  - [Unicode in ABNF](https://tools.ietf.org/html/draft-seantek-unicode-in-abnf-00)

## Rationale: how does this CIP achieve its goals?

This CIP defines a canonical format for URIs referencing four new Cardano objects: blocks, transactions, transaction metadata, and specific tags within the transaction metadata. It utilizes existing cardano standards (CIP-0013) and industry standards (URIs), minimizing the number of new concepts that a developer needs to learn. By utilizing URIs, it creates a natural path to integration with existing tools, such as browsers. And finally, it allows a canonical URI for these objects, such as storing CIP-100 metadata on-chain, and referring to it in the anchor field.
## Path to Active

### Acceptance Criteria

- [ ] CIP-100 is standardized utilizing these URI schemes for on-chain references.
- [ ] At least one governance tool utilizes these URI schemes
- [ ] At least one explorer or wallet utilizes these URI schemes

### Implementation Plan

The current community sentiment towards adopting this in CIP-100 is high (it was the original inspiration).

Advocacy and education about this format should be performed by:

- Implementors of CIP-100 and governance metadata tooling
- Wallet and Explorer developers

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
