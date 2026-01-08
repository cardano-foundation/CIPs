---
CIP: 102
Title: Royalty Datum Metadata
Authors: 
 - Sam Delaney <sdelaney@ikigaitech.org>
Implementors: 
- Grabbit <https://grabbit.market/>
- Nebula <https://github.com/spacebudz/nebula/>
Discussions:
 - https://github.com/ikigai-github/CIPs/pull/1
 - https://github.com/cardano-foundation/CIPs/pull/551
Status: Proposed
Category: Tokens
Created: 2023-08-08
License: CC-BY-4.0
---

## Abstract

This proposal makes use of the onchain metadata pattern established in [CIP-0068][] to provide a way to store royalties with greater assurance and customizability.

## Motivation: Why is this CIP necessary?

The inability to create trustless onchain royalty validation with [CIP-0027][] is a major drawback to Cardano NFTs. The pattern defined in CIP-68 represents an opportunity to upgrade the standard to support onchain validation. This CIP aims to eliminate that drawback and demonstrate better support for developers, NFT creators, and NFT collectors, ultimately attracting dapps & NFT projects that would otherwise have taken their talents to another blockchain.

In addition, this standard allows royalties to be split between multiple addresses, another limitation of the CIP-27 royalty schema. Future versions of this standard could  also easily support multiple royalty policies defined for a single collection, applied at the level of individual tokens.

## Specification

### 500 Royalty Datum Standard

The following defines the `500` Royalty NFT standard with the registered `asset_name_label` prefix value

| asset_name_label            | class        | description                                                          |
| --------------------------- | ------------ | -------------------------------------------------------------------- |
| 500                         | NFT          | Royalty NFT stored in a UTxO containing a datum with royalty information |

#### Class

The `royalty NFT` is an NFT (non-fungible token).

#### Pattern

The `royalty NFT` **must** have an identical `policy id` as the collection.

The `asset name` **must** be `001f4d70526f79616c7479` (hex encoded), it contains the [CIP-0067][] label `500` followed by the word "Royalty".

Example:\
`royalty NFT`: `(500)Royalty`\
`reference NFT`: `(100)Test123`

#### 500 Datum Metadata

The royalty info datum is specified as follows (CDDL):

```cddl
big_int = int / big_uint / big_nint
big_uint = #6.2(bounded_bytes)
big_nint = #6.3(bounded_bytes)

optional_big_int = #6.121([big_int]) / #6.122([])

royalty_recipient = #6.121([
              address,                    ; definition can be derived from: 
                                          ; https://github.com/input-output-hk/plutus/blob/master/plutus-ledger-api/src/PlutusLedgerApi/V1/Address.hs#L31
              int,                        ; variable fee ( calculation: ⌊1 / (fee / 10)⌋ ); integer division with precision 10
              optional_big_int,           ; min fee (absolute value in lovelace)
              optional_big_int,           ; max fee (absolute value in lovelace)
            ])

royalty_recipients = [ * royalty_recipient ]

; version is of type int, we start with version 1
version = 1  

; Custom user defined plutus data.
; Setting data is optional, but the field is required
; and needs to be at least Unit/Void: #6.121([])
extra = plutus_data

royalty_info = #6.121([royalty_recipients, version, extra])
```

#### Example of onchain variable fee calculation:

```cddl
; Given a royalty fee of 1.6% (0.016)

; To store this in the royalty datum
1 / (0.016 / 10) => 625

; To read it back
10 / 625 => 0.016
```
Because the computational complexity of Plutus primitives scales with size, this approach significantly minimizes resource consumption.

To prevent abuse, it is **recommended** that the `royalty NFT` is stored at the script address of a validator that ensures the specified fees are not arbitrarily changed, such as an always-fails validator.

### Reference Datum Royalty Flag

If not specified elsewhere in the token's datums, a malicious user could send transactions to a protocol which do not reference the royalty datum. For full assurances, a new optional flag should be added to the reference datum

```cddl
extra = 
	{
		...

		? royalty_included : big_int
	}
```

- If the field is present and > 1 the validators must require a royalty input.
- If the field is present and set to 0 the validators don't need to search for a royalty input.
- If the field is not present, validators should accept a royalty input, but not require one.

### Examples

In-code examples can be found in the [reference implementation](https://github.com/SamDelaney/CIP_102_Reference).

#### Retrieve metadata as 3rd party

A third party has the following NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` and they want to look up the royalties. The steps are

1. Construct `royalty NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(500)Royalty`
2. Look up `royalty NFT` and find the output it's locked in.
3. Get the datum from the output and look up metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

#### Retrieve metadata from a Plutus validator

We want to bring the royalty metadata of the NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` in the Plutus validator context. To do this we

1. Construct `royalty NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(500)Royalty` (off-chain)
2. Look up `royalty NFT` and find the output it's locked in. (off-chain)
3. Reference the output in the transaction. (off-chain)
4. Verify validity of datum of the referenced output by checking if policy ID of `royalty NFT` and `user token` and their asset names without the `asset_name_label` prefix match. (on-chain)

## Rationale: How does this CIP achieve its goals?

The specification here is made to be as minimal as possible. This is done with expediency in mind and the expectation that additional changes to the specification may be made in the future. The sooner we have a standard established, the sooner we can make use of it. Rather than attempting to anticipate all use cases, we specify with forward-compatibility in mind.

### 500 Royalty Token Datum

This specification is largely based on [the royalty specification in Nebula](https://github.com/spacebudz/nebula/tree/main#royalty-info-specification), with a couple key departures:

- The royalty token is recommended to be locked at a script address, rather than stored in the user's wallet. This encourages projects to guarantee royalties won't change by sending their royalties to an always-fails (or similar) script address, but still allows for creative royalty schemes and minimizes disruption to existing projects.

- The policyId of the royalty NFT must match that of the reference NFT. This enables lookups based on the user token in the same way as is done for the tokens specified in the original CIP-68 standard.

### Reference Datum Flag

In addition to providing a way to create guaranteed royalties, this has several advantages:

- Backwards Compatibility - Existing royalty implementations will still work, just not have the same assurances.
- Minimal Storage Requirement - An optional boolean has about the smallest memory impact possible. This is especially important because it's attached to the - Reference NFT and will be set for each individual NFT.
- Intra-Collection Utility - This already allows for minting a collection with some NFTs with royalties and some without. A future version of this standard will likely make use of this field to allow for multiple versions of royalties for even more granular control.

### Backward Compatibility

To keep metadata compatibility with changes coming in the future, we introduce a `version` field in the datum.

### Extending & Modifying this CIP

See the [CIP-0068 Extension Boilerplate](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068/extension_boilerplate.md)

## Path to Active

### Acceptance Criteria

- [x] This CIP should receive feedback, criticism, and refinement from: CIP Editors and the community of people involved with NFT projects to review any weaknesses or areas of improvement.
- [x] Guidelines and examples of publication of data as well as discovery and validation should be included as part of of criteria for acceptance.
- [x] Minimal reference implementation making use of [Lucid](https://github.com/spacebudz/lucid) (off-chain), [PlutusTx](https://github.com/input-output-hk/plutus) (on-chain): [Reference Implementation](https://github.com/SamDelaney/CIP_102_Reference).
- [ ] Implementation and use demonstrated by the community: NFT Projects, Blockchain Explorers, Wallets, Marketplaces.

### Implementation Plan

- [x] Publish open source reference implementation and instructions related to the creation, storage and reading of royalty utxos.
- [ ] Implement in open source libraries and tooling such as [Lucid](https://github.com/spacebudz/lucid), [Blockfrost](https://github.com/blockfrost/blockfrost-backend-ryo), etc.
- [ ] Achieve additional "buy in" from existing community actors and implementors such as: blockchain explorers, token marketplaces, minting platforms, wallets.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-0027]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027
[CIP-0067]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067
[CIP-0068]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068
