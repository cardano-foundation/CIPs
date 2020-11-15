```
CIP: ?
Title: Single-Pool Stake URI Scheme
Author: Robert Phair <rphair@cosd.com>
Discussions-To:
Comments-Summary: No comments yet.
Comments-URI:
Status: Draft
Type: Standards
Created: 2020-09-22
License: CC-BY-4.0
Post-History: https://forum.cardano.org/t/40594
Post-History: https://github.com/cardano-foundation/CIPs/pull/25
## Summary

Support stake pool references through a URI scheme, facilitating delegation via web links in all Cardano wallets and other means of delegation.

## Abstract

This meets the simple but vital use case of individual pool web sites and other Internet content providing a one-click reference directly into a user's delegation wallet.

## Motivation

Centralised sources of information, such as the Daedalus ranking algorithm and its presentation to the delegating user, have led a growing amount of stake to be disproportionately assigned to pools pushed near & beyond the saturation point.

Stake pool URIs will provide a convenient and popular alternative to the trend of stake centralisation, while supporting diversity and resilience in the Cardano network.

## Specification

Example, pool ticker:
`web+cardano://stake?COSD`

Example, pool ID:
`web+cardano://stake?c94e6fe1123bf111b77b57994bcd836af8ba2b3aa72cfcefbec2d3d4`

Use of the `web+cardano` protocol extends the proposed **ABNF Grammar** in the related **CIP: Cardano URI Scheme** ([current draft](https://github.com/Emurgo/CIPs/blob/payment-urls/PaymentUrls/PaymentUrls.md), not yet [merged](https://github.com/cardano-foundation/CIPs/pull/30)) as follows:

* URI "authority" (`//stake`) differentiates the stake pool reference(s) from a payment request URIs or references to some other Cardano resource.
* The single argument is a 3 to 5 character `poolTicker` or a 56-hex-digit `poolHexID`.

#### Notes on pool references

For brevity, essential in many Internet contexts, a `poolTicker`  must be supported here in addition to the unambiguous `poolHexID`.  This should be safe because of the Daedalus wallet's integration with [SMASH](https://github.com/input-output-hk/smash) metadata to avoid fake pool registrations.

The value of the first URI argument, and all further arguments, should (by preference of the wallet UI designers) *either* be ignored *or* generate a warning message: to avoid leading the user to believe they are implementing an (as yet) unsupported delegation list.

When there is more than one pool registered with the specified `poolTicker` (e.g. for pool groups which have the same ticker for all pools), the choice to which pool to actually delegate is left to the user through the wallet UI.  Especially in such cases, the wallet must present a UI to confirm the pool choice from multiple options.

In all cases, the wallet UI must select, out of multiple wallets, which wallet(s) the user will be delegating from.

## Rationale

As K continues to increase, options for convenient *and informed* re-delegation will become more important.  Both delegators and small pools looking to survive will inevitably rely on sources of information outside the wallet to suggest pools beyond the highly contested top choices of the in-wallet ranking algorithms.

More meaningful association between a pool's social identity and delegated stake will help ensure that pool operators are rewarded, by their own communities and other supporters, for helping maintain a number of pools sufficient to accommodate Cardano's needs during any expected expansion period.

Cardano's decentralisation stage will overlap with its smart contract introduction, and a sudden DeFi migration to Cardano would also mean a vast, sudden increase in transaction frequency and depth that the stake pool network will need to support with quality and diversity.

Beyond the obvious help to small pools, further increases in the K value will also make this feature important for *larger* pools, to provide an "exit strategy" for saturated or saturating pools, redirecting their delegators toward alternates.

## Backwards compatibility

This proposal does not break backwards compatibility because it is an offchain change.

### Copyright

© 2020 Robert Phair (22 September 2020).  This CIP is licensed under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode) license.