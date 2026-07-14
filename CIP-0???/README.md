---
CIP: "????"
Title: Handle Provider Registry & Resolver
Category: Tools
Status: Proposed
Authors:
  - Slavcho King <support@getmyid.today>
  - Jesse Anderson <papa.goose@koralabs.io>
Implementors: []
Discussions:
  - "CPS-0032 PR: https://github.com/cardano-foundation/CIPs/pull/1199"
Created: 2026-06-01
License: CC-BY-4.0
---

## Abstract

This CIP defines a technical standard for interoperability
between Cardano handle and naming providers. It specifies a
provider registry format, a standard resolver interface, wallet
display requirements, collision handling behavior, and provider
evaluation criteria. The goal is to allow wallets and dApps to
support multiple naming providers safely and transparently
without requiring per-provider custom integrations, and without
assigning namespace ownership or mandatory resolution priority
to any single provider.

This CIP addresses the problems documented in CPS-0032.

## Motivation: Why is this CIP necessary?

CPS-0032 documented the following problems in the Cardano
naming ecosystem:

- No shared technical standard exists for handle providers
- Ambiguous resolution across providers causes risk of fund loss
- No provider discovery mechanism exists
- Wallet UX for multi-provider resolution is undefined
- Abuse resistance criteria are undefined

This CIP provides the technical solution to those problems.

## Specification

### Provider Registry

#### Registry Format

The provider registry is a JSON file (`registry.json`) maintained
in this CIP's directory in the Cardano CIPs repository. Each
entry represents one registered handle provider.

Any provider may submit a pull request to add themselves to the
registry provided they meet the minimum criteria defined in
section 4 of this CIP. Entries are assigned a serial number by
CIP editors in order of pull request merge date. Serial numbers
are sequential integers starting from 1 and incrementing by 1
for each new entry.

#### Registry Entry Format

```json
{
  "serial": 1,
  "provider": "Provider Name",
  "namespace": ".did",
  "policy_ids": {
    "mainnet": "abc123...",
    "preprod": "def456..."
  },
  "resolver": {
    "api": "https://example.com/api/resolve/",
    "onchain_method": "policy_asset_holder"
  },
  "metadata_standard": "CIP-25",
  "website": "https://example.com",
  "security_contact": "security@example.com",
  "status": "active",
  "registered": "2026-06-01"
}
```

#### Registry Fields

| Field | Required | Description |
|-------|----------|-------------|
| serial | Yes | Sequential integer assigned by CIP editors |
| provider | Yes | Human-readable provider name |
| namespace | Yes | Namespace format (e.g. `.did`, `$name`, `name.ada`) |
| policy_ids | Yes | Object containing mainnet and optionally preprod Policy IDs |
| resolver.api | Yes | HTTPS endpoint implementing the resolver interface defined in section 2 |
| resolver.onchain_method | Yes | On-chain resolution method identifier (see section 2.3) |
| metadata_standard | Yes | CIP-25 or CIP-68 |
| website | Yes | Provider's public website |
| security_contact | Yes | Email address for security disclosures |
| status | Yes | One of: active, deprecated, inactive |
| registered | Yes | ISO 8601 date of registry entry merge |

#### Serial Number and Resolution Order

Serial numbers are assigned in order of pull request merge date
and represent registration order only. Wallets SHOULD present
providers in serial number order when displaying provider options
to users. Serial numbers do not constitute namespace ownership
and do not mandate wallet behavior beyond display ordering.

When only one registered provider supports a given namespace
format, wallets MUST resolve to that provider automatically
without requiring user selection.

When multiple registered providers support the same visible
namespace format, wallets SHOULD default to the provider with
the lowest serial number for that format while always providing
a clearly accessible user override option.

### Resolver Interface

#### API Resolution

All registered providers MUST implement the following HTTP
endpoint:

```
GET /resolve/{handle}
```

Optional query parameter:
```
?network=mainnet|preprod
```

If no network parameter is provided the provider MUST default
to mainnet resolution.

**Response 200 — handle found:**

```json
{
  "handle": "john.smith.did",
  "address": "addr1qx...",
  "policy_id": "abc123...",
  "provider": "Provider Name",
  "network": "mainnet"
}
```

**Response 404 — handle not found:**

```json
{
  "error": "Handle not found",
  "handle": "john.smith.did",
  "provider": "Provider Name"
}
```

**Response 400 — invalid handle format:**

```json
{
  "error": "Invalid handle format",
  "handle": "..."
}
```

All responses MUST use `Content-Type: application/json` and
MUST use HTTPS.

#### Input Handling Requirements

Wallets and dApps implementing this standard MUST:

- Not rely solely on debounce techniques for handle resolution.
  Resolution MUST be triggered by an explicit user action such
  as pressing Enter or Tab, clicking a button, or the input
  field losing focus. If debounce is used it MUST be
  re-confirmed after an explicit user action.
- Disable browser autofill on address input fields to prevent
  inadvertent selection of autofill values.

#### On-Chain Resolution

In addition to API resolution, providers MUST support on-chain
resolution so wallets can verify handle ownership trustlessly
without depending on provider API availability.

On-chain resolution is performed by querying the Cardano
blockchain for the current holder of the NFT asset identified
by `{policy_id}{asset_name_hex}` where `asset_name_hex` is
the UTF-8 encoded handle string in hexadecimal.

The address currently holding that asset is the resolved
address for the handle.

Providers MUST document their on-chain resolution method in
their registry entry.

#### Test Vectors

Providers SHOULD include at least one publicly documented test
vector — a known handle and its expected resolved address on
preprod testnet — so wallet implementors can verify their
integration without spending real ADA.

### Wallet Display Requirements

Wallets implementing this standard MUST:

- Display the provider name and policy ID used to resolve a
  handle, so users always know which provider was queried.
- Redisplay the resolved handle back to the user as
  confirmation that the correct handle was resolved.
- Display the handle NFT image if available as an additional
  visual confirmation.
- Display a clear warning if a handle resolves to a script
  address, especially if no datum is attached.
- On transaction review pages, display the handle name and
  resolved address together so users can verify both before
  confirming.

Wallets implementing this standard SHOULD:

- Display the provider's NFT image alongside the provider
  name for visual identification.
- Allow users to set a preferred default provider in wallet
  settings.

### Collision Handling

When a user enters a handle string that matches the namespace
format of multiple registered providers, wallets MUST:

1. Query all matching registered providers
2. If only one provider resolves the handle successfully —
   use that result and display the provider name to the user
3. If multiple providers resolve the same handle — display
   a provider selection interface showing:
   - Each provider's name
   - Each provider's resolved address
   - Each provider's policy ID
   - A clear prompt asking the user to select the intended
     provider

Wallets MUST NOT silently resolve to one provider when multiple
providers can resolve the same visible handle string without
surfacing this ambiguity to the user.

### Provider Evaluation Criteria

To be eligible for inclusion in the registry a provider MUST
demonstrate:

- A working live platform accessible at the declared website
- At least one NFT asset minted on Cardano mainnet under the
  declared policy ID
- A functioning resolver API endpoint returning responses in
  the format defined in section 2.1
- A valid security contact email address
- On-chain resolution support for the declared policy ID
- Publicly documented metadata following CIP-25 or CIP-68

A provider SHOULD demonstrate:

- A preprod testnet deployment with a separate preprod policy ID
- At least one documented test vector for integration testing

CIP editors review registry addition pull requests for
compliance with these criteria before merging.

### Provider Deprecation

When a provider ceases operation or migrates to a new policy
ID they MUST update their registry entry status field to
`deprecated` or `inactive` and SHOULD provide a migration
path for existing handle holders.

Wallets reading a deprecated or inactive registry entry MUST:

- Stop resolving new handles for that provider
- Display a warning to users when a handle from a deprecated
  provider is entered
- Not remove previously resolved addresses from transaction
  history

### Payment URI Integration

Payment URIs that include handle resolution SHOULD use the
following parameter format to specify provider context
explicitly:

```
cardano:{address}?handle={handle}&handle-provider={provider-name}
```

Example:
```
cardano:addr1qx...?handle=john.smith.did&handle-provider=GetMyID
```

When a wallet receives a payment URI containing a
`handle-provider` parameter it SHOULD use the specified
provider for resolution rather than prompting the user to
select a provider.

### Security Considerations

#### Homograph Attacks

Wallets MUST display the full resolved address alongside any
handle and MUST NOT replace the address display with only the
handle name at any point in the transaction flow.

#### Script Address Warnings

Wallets MUST display a prominent warning when a handle resolves
to a script address. Unless the script address has an attached
datum, this is most likely an error and users should be
discouraged from proceeding without verification.

#### Provider Impersonation

The registry is the authoritative source of provider policy
IDs. Wallets MUST verify that the policy ID returned in a
resolver response matches the policy ID declared in the
registry entry for that provider. Responses with mismatched
policy IDs MUST be rejected and the user MUST be warned.

#### API Availability

Wallets SHOULD implement on-chain resolution as a fallback
when a provider's API endpoint is unavailable. Wallets MUST
NOT silently fail when a provider API is unavailable — they
MUST notify the user that resolution was unsuccessful.

## Rationale: How does this CIP achieve its goals?

### Registry model

The CIP-0010 transaction metadata label registry was chosen as
the model for the provider registry because it is a proven
pattern in the Cardano ecosystem, requires no new
infrastructure, uses the existing trusted CIP process, and
can be upgraded to a smart contract registry in the future
if the community decides that is desirable.

### Serial number ordering

Serial numbers reflect registration order and are used as the
default display ordering for providers when wallets present
options to users. This gives earlier registrants a mild
display advantage without constituting namespace ownership or
mandatory resolution priority. Wallet teams retain discretion
over their implementation and users retain override capability
at all times.

### Collision handling

The collision handling approach — surface ambiguity to the
user rather than silently choosing — is the safest behavior
in a system where multiple providers can resolve the same
visible string. Silent resolution to a default provider when
ambiguity exists could cause fund loss if the user intended
a different provider.

### On-chain resolution requirement

Requiring on-chain resolution in addition to API resolution
ensures that handle ownership is always verifiable without
depending on any provider's infrastructure being available.
This is consistent with Cardano's decentralization values and
protects users if a provider's API goes offline.

## Path to Active

### Acceptance Criteria

- At least two independent Cardano wallet implementations
  support the resolver interface defined in section 2 and
  the wallet display requirements defined in section 3
- At least two naming providers have submitted registry
  entries meeting the criteria in section 5
- The registry JSON file is maintained and validated by
  CIP editors

### Implementation Plan

1. This CIP is accepted and the registry.json file is created
2. Existing providers (ADA Handle, GetMyID, CNS) are invited
   to submit registry addition pull requests
3. Wallet developers implement the resolver interface and
   display requirements
4. The community validates implementations against the test
   vectors provided by registered providers

## References

- [CPS-0032 — Handle Provider Interoperability](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0032/README.md)
- [CPS-0008 — Domain Name Resolution](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0008/README.md)
- [CIP-0010 — Transaction Metadata Label Registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/README.md)
- [CIP-0025 — NFT Metadata Standard](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025)
- [CIP-0068 — Datum Metadata Standard](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068)
- [ADA Handle Verified Integration Guidelines](https://handle.me/#verified_integration)
- [GetMyID Platform](https://getmyid.today)
- [ADA Handle Platform](https://handle.me)

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
