---
CPS: ????
Title: Handle Provider Interoperability
Category: Tools
Status: Open
Authors:
  - Slavcho King <support@getmyid.today>
  - Jesse Anderson <papa.goose@koralabs.io>
Created: 2026-05-28
License: CC-BY-4.0
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1187
  - https://github.com/cardano-foundation/CIPs/pull/1199
---

## Abstract

Cardano lacks a common resolver-interoperability framework for
wallets and dApps that need to support multiple naming and handle
providers safely, transparently, and without breaking existing
users. As more providers emerge, the absence of shared technical
standards creates ambiguous resolution, potential loss of funds,
inconsistent user experience, and friction for both new providers
and wallet implementors. This CPS documents the problem space and
defines the properties that a future solution must satisfy.

## Problem

### No shared technical standard exists for handle providers

Multiple handle and naming providers operate on Cardano
independently — each with their own Policy ID, resolver
endpoint, metadata format, and namespace convention. There is
no shared specification defining how providers should publish
their resolver capabilities, how wallets should query them, or
how provider context should be communicated to users.

Without a shared standard, every wallet team must independently
research and integrate each naming provider separately. This
creates friction that scales poorly as the number of providers
grows and increases the likelihood of inconsistent or incorrect
implementations.

### Ambiguous resolution causes risk of fund loss

When a user enters a handle string in a wallet send field, the
wallet must determine which provider issued that handle and
query the correct resolver. Without a standard, wallets have
no deterministic method for this determination.

If two providers both issue handles using the same visible
format under different Policy IDs, a wallet resolving to the
wrong provider may send funds to an unintended recipient. This
is not a hypothetical risk. It has already occurred as naming
providers have proliferated on Cardano.

CPS-0008 documented this exact scenario using a concrete
example of two providers both using the same suffix. That
problem remains unsolved and has grown more acute as additional
providers have entered the ecosystem. This CPS supersedes
CPS-0008 and provides a more complete definition of the
problem space.

### No provider discovery mechanism exists

Wallets and dApps have no standard way to discover which naming
providers exist on Cardano, what namespace formats they use,
what their resolver endpoints are, or what technical
capabilities they support. Integration requires direct contact
with each provider individually and results in implementations
that vary across wallets.

### Wallet UX for multi-provider resolution is undefined

When a wallet supports multiple naming providers there is no
standard defining how provider context should be displayed to
users, how ambiguous inputs should be handled, how users should
select between providers when multiple providers can resolve the
same visible string, or what warnings should appear when a
handle resolves to unexpected address types such as script
addresses.

Without these standards wallet implementations vary widely,
user experience is inconsistent, and the risk of user error
or fund loss increases.

### Abuse resistance is undefined

Because handle resolution directly affects where user funds are
sent, naming providers occupy a position of significant trust
in the wallet ecosystem. There is currently no standard
defining what signals wallets and dApps should inspect before
enabling resolution for a provider, how to detect abandoned
or malicious providers, or how to protect users from
impersonation, phishing, or broken resolution caused by
low-quality or bad-faith providers.

A future solution must consider how to prevent bad actors from
inserting themselves into address resolution flows.

## Use Cases

### Wrong address resolution across providers

A user receives a payment link containing a handle in a format
used by two different providers under different Policy IDs.
Their wallet resolves to the wrong provider and sends funds to
an unintended recipient. No warning was shown because the wallet
had no standard for detecting or surfacing this ambiguity.

### User unaware of provider context

A user enters a handle in their wallet. The wallet resolves it
but does not indicate which provider was used, which Policy ID
was queried, or whether the resolved address is a standard
payment address or a script address. The user has no way to
verify the resolution is correct before sending funds.

### Wallet implementor friction

A wallet team wants to support all Cardano naming providers.
They must manually research each provider, find their API
documentation, understand their metadata format, and implement
a custom integration. There is no standard format to implement
once and no mechanism to discover when new providers emerge.

### Developer testing without real ADA

A developer building a dApp that uses handle resolution needs
to test their integration before deploying to mainnet. No
standard testnet handle infrastructure or testing guidance
exists. Without a standard defining testnet requirements,
developers must either build their own test infrastructure
or test directly on mainnet.

### Provider abandonment or migration

A naming provider shuts down or migrates to a new Policy ID.
Users who hold handles from that provider have no guarantee
their handles will continue to resolve correctly. Wallets have
no standard mechanism for handling provider deprecation
gracefully.

## Goals

A solution to this problem MUST:

- Define a standard format for providers to publish their
  resolver capabilities so wallets and dApps can discover and
  integrate providers without requiring direct contact with
  each provider team.

- Define a standard resolver interface so wallets can query
  any compliant provider using consistent code regardless of
  which provider is being queried.

- Define wallet display requirements so users always receive
  clear provider context when a handle is resolved, including
  which provider resolved the handle and confirmation of the
  resolved address.

- Define collision handling behavior so wallets surface a
  clear warning and present a provider selection option when
  a handle string is resolvable by multiple providers under
  different Policy IDs.

- Define objective provider-evaluation signals that wallets
  and dApps can inspect before enabling resolution for a
  provider. These may include documented Policy IDs, supported
  networks, resolution methods, test vectors, security contact
  information, operational status, known limitations,
  deprecation status, and verification guidance.

- Protect existing users by ensuring full backward
  compatibility with handles already issued by any provider
  under any existing Policy ID.

A solution SHOULD:

- Define on-chain resolution methods alongside API resolution
  so wallets can verify handle ownership trustlessly without
  depending solely on provider API availability.

- Define payment URI parameters that convey provider context
  explicitly so payment links can indicate the intended
  provider, reducing ambiguity for the recipient's wallet.

- Define provider deprecation metadata so wallets can handle
  providers that shut down or migrate gracefully.

- Define best practices for wallet implementors based on
  real-world lessons learned from existing integrations
  including input handling, visual confirmation, and address
  type warnings.

- Support testnet environments so developers can test handle
  resolution integrations without spending real ADA.

This CPS intentionally does not prescribe whether the solution
should use a registry, resolver metadata file, on-chain
discovery mechanism, URI parameters, wallet-local provider
list, or another mechanism. Those design choices belong in
one or more future CIPs.

## Open Questions

- What objective signals should wallets use to evaluate
  provider quality and trustworthiness before enabling
  resolution?

- Should on-chain resolution be required or optional for a
  provider to be considered compliant with the standard?

- How should wallets handle ambiguous inputs when multiple
  providers can resolve the same visible handle string?

- How should the standard handle providers that use the same
  visible namespace format under different Policy IDs?

- How should payment URI parameters be structured to convey
  provider context?

- How should the standard address provider deprecation and
  ensure continuity for users when a provider shuts down
  or migrates?

- Should the standard distinguish between handle providers
  and domain name providers given that these serve different
  user needs?

## References

- [CPS-0008 — Domain Name Resolution](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0008/README.md)
- [CIP-0010 — Transaction Metadata Label Registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/README.md)
- [CIP-0025 — NFT Metadata Standard](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025)
- [CIP-0068 — Datum Metadata Standard](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068)
- [GetMyID Platform](https://getmyid.today)
- [ADA Handle Platform](https://handle.me)
- [ADA Handle Verified Integration Guidelines](https://handle.me/#verified_integration)

## Copyright

This CPS is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
