---
CPS: ????
Title: Coordination of Hierarchical Handle Namespace
Status: Open
Category: Tokens
Author:
  - Slavcho King <support@getmyid.today>
Created: 2026-05-22
License: CC-BY-4.0
---

## Abstract

This CPS documents the absence of an open governance framework for
human-readable handle namespaces on Cardano. Multiple naming platforms
currently operate with no shared standard, no defined hierarchy, and no
coordination mechanism. This creates conflicts between platforms,
ambiguous wallet resolution, and no protection for users or independent
developers who invest in building new naming solutions.

## Problem

### 1. No open standard exists for handle namespace hierarchy

Cardano currently has multiple handle and naming services operating
independently with no shared governance framework and no defined
hierarchy. Each platform independently decides which suffixes to use,
which Policy IDs to mint under, and how resolution works.

### 2. Namespace conflicts cannot be prevented or resolved

Nothing in the current Cardano ecosystem prevents any naming platform
from minting handles with any suffix at any time. A new entrant who
goes through the proper CIP process in good faith can have their
proposed namespace claimed by another platform after submission. There
is no technical or governance mechanism to prevent this.

This is not hypothetical. During the submission of CIP PR #1187, it
was discovered that ADA Handle already mints handles ending in `.id`,
directly conflicting with the proposed GetMyID namespace. Additionally,
a speculative handle `$did` was minted immediately after the `.did`
namespace was discussed publicly — demonstrating that namespace
squatting is trivially easy with no governance in place.

### 3. Wallet resolution is ambiguous across multiple providers

When multiple platforms mint handles with the same suffix under
different Policy IDs, wallets have no deterministic rule for
resolution. Wallets default to whichever Policy ID they integrated
first, typically the incumbent. Users who purchased handles from a
newer platform may find their handles do not resolve correctly in
popular wallets, through no fault of their own.

### 4. No open participation framework exists

ADA Handle achieved widespread wallet integration and community
adoption without contributing any open specification or CIP to the
Cardano ecosystem. New entrants have no defined process for
participating in the handle namespace on equal terms. Independent
developers without institutional funding or existing wallet
relationships face structural disadvantages that a governance framework
would eliminate.

### 5. The CIP process alone cannot enforce compliance

As acknowledged by the CIP editors, participation in the CIP process
is entirely voluntary. A CIP or CPS cannot prevent any entity from
minting handles in any format at any time. Without an on-chain
governance mechanism, any standard can be bypassed by any participant.

## Use Cases

### UC-1: Unambiguous wallet resolution

A user holds `john.smith.did` minted by Platform A. Another user holds
`john.smith.did` minted by Platform B under a different Policy ID.
Wallets need a deterministic rule to resolve the correct address.
Currently no such rule exists.

### UC-2: Open participation for new providers

An independent developer builds a handle platform, proposes a CIP,
and invests in building a user base — only to have another platform
claim the same namespace with no recourse. A governance framework
would define the process for namespace registration and protect new
entrants who participate in good faith.

### UC-3: User protection across platform changes

If a naming platform shuts down or is acquired, users holding handles
from that platform need assurance that their handles will continue to
resolve. A governance framework with defined standards protects users
from platform-specific failures.

### UC-4: Reference implementation recognition

An independent developer who identifies a governance gap, proposes a
framework, builds a live working implementation, and goes through the
proper CIP process should have a defined path to recognition as the
reference implementation for the namespace they pioneered — provided
the governance framework confirms their technical and community
criteria are met.

GetMyID (getmyid.today) is currently the only platform running both
testnet and mainnet handle resolution simultaneously, and was the
first to formally propose a governance framework for hierarchical
handle namespaces through the CIP process. The question of how such
prior effort and contribution should be recognized within a governance
framework is an open question this CPS invites the community to
address.

## Goals

A solution to this problem MUST:

1. Define a technical framework for hierarchical namespace management
   on Cardano that any qualified entity can participate in.

2. Establish clear and deterministic resolution rules so wallets can
   resolve handles unambiguously when multiple providers exist.

3. Prevent namespace squatting by requiring that entities wishing to
   issue handles in a registered namespace participate in the
   governance framework.

4. Allow open participation — any technically qualified entity should
   be able to register as a handle provider, not just a single
   licensed incumbent.

5. Be verifiable on-chain — the registry of approved providers and
   their Policy IDs should be queryable trustlessly without depending
   on any centralized API.

6. Protect existing users — any governance transition must ensure
   that handles already purchased continue to resolve correctly.

A solution SHOULD:

- Align with the W3C Decentralized Identifier specification
  (https://www.w3.org/TR/did-core/) where applicable.
- Define a dispute resolution process for namespace conflicts.
- Involve the Cardano Foundation given their trademark interests in
  the Cardano and Ada brand names.

## Open Questions

1. Should the on-chain registry be managed by a smart contract, a
   governance action, or a community-appointed committee?

2. How should resolution priority be determined when multiple providers
   exist under the same namespace — registration order, stake weight,
   or community vote?

3. Can existing handles from current platforms be migrated into an
   open framework retroactively, or must new namespaces be created?

4. Should the Cardano Foundation serve as the ultimate arbiter of
   namespace disputes given their trademark position?

5. What minimum technical and community criteria should a provider
   meet before being admitted to the governance registry?

6. How should prior contribution — such as building a live reference
   implementation, proposing the governance framework, and going
   through the formal CIP process — be recognized and weighted when
   assigning namespace registration priority?

## References

- [CIP PR #1187 — GetMyID Handle Standard](https://github.com/cardano-foundation/CIPs/pull/1187)
- [CIP-0001 — CIP Process](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0001/README.md)
- [W3C Decentralized Identifier Specification](https://www.w3.org/TR/did-core/)
- [GetMyID Platform](https://getmyid.today)
- [ADA Handle](https://handle.me)
- [Cardano Name Service](https://www.cns.io)

## Copyright

This CPS is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
