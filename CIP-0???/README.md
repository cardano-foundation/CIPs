---
CIP: TBD
Title: Handle Provider Registry & Resolver
Category: Tools
Status: Proposed
Authors:
  - Slavcho King <support@getmyid.today>
Implementors: []
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1229
  - Early discussion: https://github.com/cardano-foundation/CIPs/pull/1187
  - CPS-0032 review: https://github.com/cardano-foundation/CIPs/pull/1199
Solution To:
  - CPS-0032: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0032
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

### Namespace Definition

A namespace in the context of this CIP is a syntactic pattern
that uniquely identifies handles issued by a specific provider.
Each provider may register one or more namespaces in the registry under separate entries.

Three namespace types are defined:

#### Suffix Namespace

The distinguishing element appears at the end of the handle
string, preceded by a delimiter character.

**Format:** `{delimiter}{word}`

**Excluded delimiter characters** (not permitted because they
conflict with URL encoding, URI parsing, or display rendering):
`?` `&` `%` `"` `'` `<` `>` `(` `)` `[` `]` `{` `}` `,`
`^` `` ` `` newline tab space

Any special character not in the excluded list above MAY be used
as a suffix delimiter.

**Word:** letters and numbers only, 1 to 20 characters

**Examples:** `.did`, `#cardano`, `@id`, `-gid`, `_ada`, `$did`

**Detection rule:** `handle.endsWith(namespace_value)`

**Example:** `john.smith.did` matches namespace `.did`

Only one suffix per provider registration is permitted.
The suffix is defined as the delimiter character plus
everything after the LAST occurrence of any delimiter
character in the handle string.

#### Prefix Namespace

The distinguishing element appears at the start of the
handle string as a single special character. The prefix
character is a visual convention and is NOT part of the
on-chain asset name — it is stripped before on-chain
lookup.

**Allowed prefix characters:** any single special character not in
the following excluded list:
`?` `&` `%` `"` `'` `<` `>` `(` `)` `[` `]` `{` `}` `,`
`^` `` ` `` newline tab space

**Detection rule:** `handle.startsWith(namespace_value)`
where the prefix character is stripped before on-chain
lookup

**Example:** `$john.smith` matches namespace `$` — the
actual on-chain asset name queried is `john.smith`

#### Bare Namespace

No prefix or suffix. The entire input string is the
complete on-chain asset name. This is the model used
by providers whose handles have no distinguishing
syntactic element.

**Detection rule:** bare namespace providers are always
queried as a fallback when no suffix or prefix match
is found among registered providers.

Multiple providers may register under the bare namespace
type under different Policy IDs. Bare namespace providers
are displayed with lowest priority in the collision
selection interface.

#### Namespace Registry Fields

The following fields MUST be added to each registry entry
to define the provider namespace:

| Field | Required | Description |
|-------|----------|-------------|
| namespace | Yes | The namespace value e.g. `.did`, `$`, empty string for bare |
| namespace_type | Yes | One of: `suffix`, `prefix`, `bare` |
| namespace_delimiter | Suffix only | The delimiter character used e.g. `.` `#` `@` `-` `_` |

Updated registry entry examples:

Suffix namespace:
```json
{
  "namespace": ".did",
  "namespace_type": "suffix",
  "namespace_delimiter": "."
}
```

Prefix namespace:
```json
{
  "namespace": "$",
  "namespace_type": "prefix"
}
```

Bare namespace:
```json
{
  "namespace": "",
  "namespace_type": "bare"
}
```

#### Namespace Detection Algorithm

When a user enters a handle string, wallets implementing
this CIP MUST use the following algorithm to determine
which registered provider or providers to query:

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

#### On-Chain Resolution

Wallets MUST use on-chain resolution when populating
a transaction recipient address from a handle.
On-chain resolution queries the Cardano blockchain
directly and does not involve any provider
infrastructure.

On-chain resolution is performed as follows:

**Step 1 — Construct the asset name hex:**

Encode the handle string as UTF-8 bytes and convert
to lowercase hexadecimal:

asset_name_hex = UTF8_bytes(handle_string).to_hex()

Example:
handle = "slavcho.did"
asset_name_hex = "736c617663686f2e646964"

**Step 2 — Construct the full asset ID:**

asset_id = policy_id + asset_name_hex

Example:
policy_id = "10dd14b19beadb996be9d322d7f4a3a8ed20d0002f48e0ef10e4f1f6"
asset_id = "10dd14b19beadb...736c617663686f2e646964"

**Step 3 — Query the blockchain for the current NFT
holder using any of the following:**

- A third-party node provider (Blockfrost, Koios,
  Maestro or equivalent):

GET https://preprod.koios.rest/api/v1/asset_addresses
?_asset_policy={policy_id}
&_asset_name={asset_name_hex}

- A self-hosted Cardano node via cardano-db-sync,
  Ogmios, or any other Cardano chain indexer that
  can query asset holders

**Step 4 — Use the holder address:**

The address currently holding the NFT with this
asset ID is the resolved address. If no address
holds the asset the handle has not been minted and
cannot be resolved.

Wallets MUST NOT use a provider API endpoint as the
sole basis for populating a transaction recipient
address. The resolved address used for any financial
transaction MUST be obtained from a blockchain query
as defined above.

#### Input Handling Requirements

Wallets and dApps implementing this standard MUST:

- Trigger handle resolution on explicit user action
  only — pressing Enter or Tab, clicking a button,
  or the input field losing focus. Debounce alone
  is not sufficient.
- Disable browser autofill on address input fields
  to prevent unintended address substitution.

#### API Resolution (Non-financial use only)

Providers MAY publish an HTTPS resolver API endpoint
at the URL registered in the `resolver.api` field.

This endpoint MAY be used for:

- Developer tooling and testing
- dApps displaying handle information without
  initiating financial transactions
- Address book lookups where the user manually
  confirms the resolved address before any
  transaction is submitted

The API endpoint MUST NOT be used as the sole basis
for populating a transaction recipient address in
any wallet or dApp that initiates financial
transactions.

When API resolution is used for non-financial
purposes the resolved address SHOULD be verified
against an on-chain query before any transaction
is submitted.

#### Test Vectors

Providers SHOULD include at least one publicly
documented test vector — a known handle and its
expected resolved address on preprod testnet — so
wallet implementors can verify their integration
without spending real ADA.

Example test vector for GetMyID on preprod:

handle = "slavcho.did"
policy_id = "10dd14b19beadb996be9d322d7f4a3a8ed20d0002f48e0ef10e4f1f6"
asset_name_hex = "736c617663686f2e646964"
network = preprod
expected_holder = addr_test1qzhgu6hg0a6ujuurfvc0mdzpq98gn5fgt9aafh3r25gqtkryzeqzvxl258rhm8y7p6g0xn42dx98p3qp3j9gxqdejxzqs4ektt

### Wallet Display Requirements

Wallets implementing this CIP SHOULD support resolution for
all active registry entries that meet the technical criteria
defined in this document. Registry inclusion confirms
technical conformance only — it does not constitute
endorsement, create a presumptive right to wallet
enablement, or transfer wallet security decisions to the
registry or CIP editors.

Wallets MAY decline to support a specific provider based
on security, privacy, legal, operational, or
user-protection requirements. Wallets are not required to
publicly document reasons for exclusion when doing so would
compromise security investigations, confidential legal
advice, or active vulnerability disclosures. Wallets
SHOULD publish general provider evaluation policies where
possible.

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

### Security Considerations

#### Resolution Security

On-chain resolution eliminates dependence on any
provider infrastructure for financial transactions.
A provider API being compromised, their DNS being
hijacked, or their service being unavailable does
not affect on-chain resolution because the wallet
queries Cardano directly.

Both on-chain resolution via third-party RPC and
API resolution share a common trust assumption —
the wallet must connect to a service that accurately
represents the current blockchain state. Wallets
running their own Cardano node eliminate this
dependency entirely.

For the highest security wallets SHOULD use their
own Cardano node or validate results across multiple
independent RPC providers before populating a
transaction recipient address.

#### Homograph Attacks

Wallets MUST display the full resolved address
alongside any handle and MUST NOT replace the
address display with only the handle name at any
point in the transaction flow.

#### Script Address Warnings

Wallets MUST display a prominent warning when a
handle resolves to a script address. Unless the
script address has an attached datum this is most
likely an error and users should be discouraged
from proceeding without verification.

#### Provider Impersonation

The registry is the authoritative source of provider
Policy IDs. Wallets MUST verify that the on-chain
asset queried uses the Policy ID declared in the
registry entry for that provider. Assets under
unregistered Policy IDs MUST NOT be resolved as
handles under this standard.

#### API Availability

Wallets SHOULD implement on-chain resolution as the
primary method at all times. If a third-party RPC
provider is unavailable wallets SHOULD notify the
user that resolution was unsuccessful rather than
falling back to API resolution for financial
transactions.

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

### Why this CIP benefits wallet teams

A common objection to this standard is that wallet teams
already have working handle integrations through existing
provider relationships and have no incentive to implement
a new standard.

The answer is that this CIP reduces wallet engineering
burden over time. Today a wallet that wants to support
three handle providers must build three separate
integrations, maintain three separate relationships, and
handle three different API formats. With this standard,
one implementation supports all current and future
compliant providers automatically.

The marginal cost of adding a compliant provider after
initial implementation is minimal — the wallet already
speaks the standard interface. Provider diversity is free
after the first implementation.

## Path to Active

### Acceptance Criteria

- At least two independent Cardano wallet implementations
  support the resolver interface defined in the
  [Resolver Interface](#resolver-interface) and
  [Wallet Display Requirements](#wallet-display-requirements)
  sections
- At least two naming providers have submitted registry
  entries meeting the criteria in the
  [Provider Evaluation Criteria](#provider-evaluation-criteria)
  section
- The registry JSON file is maintained by CIP editors with
  pull request review for each new entry

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

## Appendix

### Example Registry Entries

The following examples illustrate how the registry.json file
should be populated. These are not real providers.

The example also demonstrates a namespace collision scenario:
Example Provider A and Example Provider D both use the `.did`
namespace under different Policy IDs. In this case wallets
MUST surface a provider selection interface to the user rather
than silently resolving to one provider. The provider with the
lower serial number (Example Provider A, serial 1) SHOULD be
presented as the default option.

```json
{
  "registrations": [
    {
      "serial": 1,
      "provider": "Example Provider A",
      "namespace": ".did",
      "namespace_type": "suffix",
      "namespace_delimiter": ".",
      "policy_ids": {
        "mainnet": "aabbccddee112233445566778899001122334455667788990011223344",
        "preprod": "112233445566778899001122334455667788990011223344556677889900"
      },
      "resolver": {
        "api": "https://example-a.com/api/resolve/",
        "onchain_method": "policy_asset_holder"
      },
      "metadata_standard": "CIP-25",
      "website": "https://example-a.com",
      "security_contact": "security@example-a.com",
      "status": "active",
      "registered": "2026-06-01"
    },
    {
      "serial": 2,
      "provider": "Example Provider B",
      "namespace": "$",
      "namespace_type": "prefix",
      "policy_ids": {
        "mainnet": "bbccddee1122334455667788990011223344556677889900112233445566"
      },
      "resolver": {
        "api": "https://example-b.com/api/resolve/",
        "onchain_method": "policy_asset_holder"
      },
      "metadata_standard": "CIP-68",
      "website": "https://example-b.com",
      "security_contact": "security@example-b.com",
      "status": "active",
      "registered": "2026-06-01"
    },
    {
      "serial": 3,
      "provider": "Example Provider C",
      "namespace": "_ada",
      "namespace_type": "suffix",
      "namespace_delimiter": "_",
      "policy_ids": {
        "mainnet": "ccddee112233445566778899001122334455667788990011223344556677",
        "preprod": "ddee11223344556677889900112233445566778899001122334455667788"
      },
      "resolver": {
        "api": "https://example-c.com/api/resolve/",
        "onchain_method": "policy_asset_holder"
      },
      "metadata_standard": "CIP-25",
      "website": "https://example-c.com",
      "security_contact": "security@example-c.com",
      "status": "deprecated",
      "registered": "2026-06-02"
    },
    {
      "serial": 4,
      "provider": "Example Provider D",
      "namespace": ".did",
      "namespace_type": "suffix",
      "namespace_delimiter": ".",
      "policy_ids": {
        "mainnet": "eeff001122334455667788990011223344556677889900112233445566778899"
      },
      "resolver": {
        "api": "https://example-d.com/api/resolve/",
        "onchain_method": "policy_asset_holder"
      },
      "metadata_standard": "CIP-25",
      "website": "https://example-d.com",
      "security_contact": "security@example-d.com",
      "status": "active",
      "registered": "2026-06-03"
    }
    {
      "serial": 5,
      "provider": "Example Provider E",
      "namespace": "",
      "namespace_type": "bare",
      "policy_ids": {
        "mainnet": "aabbccddeeff00112233445566778899001122334455667788990011"
      },
      "resolver": {
        "api": "https://example-e.com/api/resolve/",
        "onchain_method": "policy_asset_holder"
      },
      "metadata_standard": "CIP-25",
      "website": "https://example-e.com",
      "security_contact": "security@example-e.com",
      "status": "active",
      "registered": "2026-06-04"
    }
  ]
}
```

In the collision scenario above, when a user enters
`john.smith.did` in a wallet, the wallet MUST query both
Example Provider A (serial 1) and Example Provider D
(serial 4) since both support the `.did` namespace. If both
resolve the handle, the wallet MUST present a provider
selection interface. Example Provider A SHOULD be presented
as the default option due to its lower serial number.

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
