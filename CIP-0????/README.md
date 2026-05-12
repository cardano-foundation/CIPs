---
CIP: ????
Title: GetMyID Handle Standard — .id Namespace
Status: Proposed
Category: Tokens
Authors:
  - GetMyID Team <support@getmyid.today>
Created: 2026-05-12
License: CC-BY-4.0
---

## Abstract

This CIP defines the `.id` handle namespace on Cardano. NFTs minted under
the GetMyID Policy ID with asset names ending in `.id` represent
human-readable identity handles that resolve to Cardano wallet addresses.
This enables users to send ADA to `$john.smith.id` instead of a
60-character bech32 address.

## Motivation

Existing Cardano naming solutions use `$name` (ADA Handle, CIP-0068) and
`name.ada` (CNS) formats. GetMyID introduces `$name.id` — a professional
identity namespace optimized for real human names in
`firstname.lastname.id` format, at a flat 10 ADA price regardless of
character length.

The `.id` suffix is universally associated with identity across the
internet (W3C DID specification, ISO 3166 country code). This makes
GetMyID handles immediately intuitive for non-crypto users who receive
payment links.

Key differentiators from existing solutions:
- Flat pricing regardless of handle length (10 ADA for all 2+ char handles)
- Format optimized for real names: `firstname.lastname.id`
- Fully open resolver API — any wallet or dApp can integrate for free
- `.id` suffix is unambiguous and cannot collide with ADA Handle or CNS

## Specification

### Policy ID
fde643f9cb864ca69f40eec06a7f97f720a14ff3561963b25da8cade

### Asset Name Format

UTF-8 encoded string ending in `.id`, minimum 3 characters total.

Valid examples:
- `john.smith.id`
- `alice.id`
- `mk.id`

### NFT Metadata (CIP-25 compliant)

```json
{
  "721": {
    "<policy_id>": {
      "<handle_name>": {
        "name": "$john.smith.id",
        "handle": "john.smith.id",
        "type": "getmyid_handle",
        "image": "https://getmyid.today/api/image/john.smith.id",
        "website": "https://getmyid.today",
        "platform": "GetMyID",
        "version": "1.0"
      }
    }
  }
}
```

### Resolver API

GET https://getmyid.today/api/resolve/{handle}

Response (200 OK):
```json
{
  "handle": "john.smith.id",
  "address": "addr1qx...",
  "policy_id": "fde643f9cb864ca69f40eec06a7f97f720a14ff3561963b25da8cade"
}
```

Response (404 Not Found):
```json
{
  "error": "Handle not found"
}
```

### Wallet Integration Rule

When a user enters `$anything.id` in a send address field:

1. Strip the `$` prefix
2. Confirm the string ends with `.id`
3. Call `GET https://getmyid.today/api/resolve/{handle}`
4. Use the returned `address` as the recipient

Detection rule:

asset_name.endsWith('.id')
AND
policy_id === 'fde643f9cb864ca69f40eec06a7f97f720a14ff3561963b25da8cade'

## Rationale

The `.id` suffix creates an unambiguous namespace that cannot collide with
any existing Cardano naming standard. A wallet can implement a simple
`endsWith('.id')` check with zero risk of false positives against ADA
Handle or CNS.

Resolution is always live — the resolver returns the current NFT holder's
address, which automatically supports secondary market transfers. Whoever
holds the NFT owns the handle identity.

Uniqueness is enforced at the Cardano protocol level. Duplicate asset
names under the same Policy ID are rejected by the network consensus
rules, making the system trustless by design.

## Security Considerations

- **Uniqueness**: Enforced by Cardano protocol. Two tokens with the same
  name cannot exist under the same Policy ID.
- **Immutability**: The Policy ID is locked. No new tokens can be minted
  without the platform private key.
- **Trustless resolution**: Resolution reflects the current on-chain NFT
  holder, not a centralized database.
- **Open resolver**: The resolver API specification is public. Anyone can
  run an independent resolver by querying Blockfrost directly for assets
  under the GetMyID Policy ID.

## References

- [CIP-0025 — NFT Metadata Standard](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025)
- [CIP-0068 — Datum Metadata Standard (ADA Handle)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068)
- [GetMyID Platform](https://getmyid.today)
- [GetMyID Resolver API](https://getmyid.today/api/resolve/)

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
