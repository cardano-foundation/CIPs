---
CIP: 13
Title: Cardano URI Scheme
Status: Proposed
Category: Wallets
Authors:
    - Robert Phair <rphair@cosd.com>
    - Sebastien Guillemot <sebastien@emurgo.io>
    - Vicente Almonacid <vicente@emurgo.io>
Implementors: N/A
Discussions:
    - https://github.com/Emurgo/EmIPs/pull/2
    - https://forum.cardano.org/t/cip-cardano-payment-uri-scheme/41457
    - https://github.com/cardano-foundation/CIPs/pull/25
    - https://github.com/cardano-foundation/CIPs/pull/61
    - https://github.com/cardano-foundation/CIPs/pull/86
    - https://forum.cardano.org/t/cip-stake-uri-scheme-for-pools-delegation-portfolios/40594
    - https://forum.cardano.org/t/cip-generalized-cardano-urls/57464
    - https://github.com/cardano-foundation/CIPs/pull/546
    - https://github.com/cardano-foundation/CIPs/pull/559
Created: 2020-09-22
License: CC-BY-4.0
---

## Abstract

This describes a general standard URI scheme with two specific protocols to handle Ada transfers and links to weighted lists of stake pools.

## Motivation: Why is this CIP necessary?

### In general:

Developers of protocols that use URI schemes should be able to choose unique protocol keywords indicating how these links are handled by applications.

Beyond the two earliest defined protocols below, protocols using distinct keywords (e.g. `//stake`) can be defined in other CIPs and implemented without ambiguity by applications which interpret those particular URI protocols.

### For payment URIs:

Users who create community content often want donations as a financial incentive. However, forcing users to open their wallet and copy-paste an address lowers the amount of people likely to send tokens (especially if they have to sync their wallet first).

If donating was as simple as clicking a link that opens a light wallet with pre-populated fields, users may be more willing to send tokens. URI schemes would enable users to easily make payments by simply clicking links on webpages or scanning QR Codes.

### For stake pool URIs:

Centralised sources of information have led a growing amount of stake to be disproportionately assigned to pools pushed near & beyond the saturation point.

Stake pool URIs will provide an additional means for small pools to acquire delegation and maintain stability, supporting diversity and possibly fault-tolerance in the Cardano network through a more even distribution of stake.

Interfaces that connect delegators with pools beyond the highly contested top choices of the in-wallet ranking algorithms are important to avoid saturation and maintain decentralization.

Larger pools and collectives can also use these URIs to link to, and spread delegation between, a family of pools they own to avoid any one of their pools becoming saturated.

Pool links allow for interfaces to initiate delegation transactions without requiring any code modifications to the wallets themselves.

URIs for weighted stake pool lists provide alternatives to using a JSON file to implement *delegation portfolios* in a way that may better suit certain platforms, applications, or social contexts.

## Specification

The core implementation should follow the [BIP-21](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki) standard (with `bitcoin:` replaced with `web+cardano:`)

Examples:
```
<a href="web+cardano:Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd">Donate</a>
<a href="web+cardano://stake?c94e6fe1123bf111b77b57994bcd836af8ba2b3aa72cfcefbec2d3d4">Stake with us</a>
<a href="web+cardano://stake?POOL1=3.14159&POOL2=2.71828">Split between our 2 related pools</a>
<a href="web+cardano://stake?COSD">Choose our least saturated pool</a>
<a href="web+cardano://claim/v1?faucet_url=https%3A%2F%2Fclaim.hosky.io&code=consensus2023">Claim $HOSKY</a>
```

The protocol term (e.g. `//stake`) is called the _authority_ as defined in [Wikipedia > Uniform Resource Identifier > Syntax](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier#Syntax).

### Choice of URI scheme name

`cardano:` is chosen over `ada:` because other projects that implement this standard tend to take the project name over the currency name (this makes sense if we consider this protocol as a generic way for interacting with the blockchain through wallets and dApps - as opposed to a simple payment system).

Depending on the protocol registration method (see Rationale), browsers generally enforce a `web+` or `ext+` prefix for non-whitelisted protocols (note: `bitcoin:` was whitelisted; see [registerProtocolHandler > Permitted schemes](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/registerProtocolHandler#permitted_schemes)). The prefix `ext+` is recommended for extensions, but not mandatory (see [protocol_handlers](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/protocol_handlers)).

### Grammar & interpretation

This top-level definition is mainly to allow switching to a particular protocol for each separately defined `authority`, with a payment link being the default:

* When `authority` is unspecified, it is a payment URI (with an address and an optional amount parameter;
* When `authority` is explicit (containing `//` followed by the authority keyword), it is defined in the `//stake` case below or in a separate CIP for that protocol.

```
cardanouri = "web+cardano:" (paymentref | authorityref)

authorityref = (stakepoolref | otherref)
otherref = "//" authority query
```

For grammar reference, see:

  - [Wikipedia > Augmented Backus–Naur form](https://en.wikipedia.org/wiki/Augmented_Backus%E2%80%93Naur_form)
  - [RFC 2234: Augmented BNF for Syntax Specifications: ABNF](https://datatracker.ietf.org/doc/html/rfc2234)
  - [Unicode in ABNF](https://tools.ietf.org/html/draft-seantek-unicode-in-abnf-00)

#### Payment URI queries

```
paymentref = cardanoaddress [ "?" amountparam ]
cardanoaddress = *(base58 | bech32)
amountparam = "amount=" *digit [ "." *digit ]
```

The amount parameter must follow the [same rules](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki#transfer-amountsize) described in BIP-21, namely, it must be specified in decimal ADA, without commas and using the period (.) decimal separator.

#### Stake pool URI queries

```
stakepoolref = "//stake" query
query = ( "?" stakepoolpair) *( "&" stakepoolpair)
stakepoolpair = stakepool [ "=" proportion]

stakepool = poolhexid | poolticker
poolhexid = 56HEXDIG
poolticker = 3*5UNICODE

proportion = *digit [ "." *digit ]
```

For brevity, essential in many Internet contexts, `poolticker`  must be supported here in addition to the unambiguous `poolhexid`.

##### Interpretation of `proportion`

* If only one stake pool is specified, any proportion is meaningless and ignored.
* If all stake pools have a numerical proportion, each component of the resulting stake distribution will have the same ratio as the provided `proportion` to the sum of all the propotions.
* Any missing `proportion` is assigned a precise value of `1`.
* If a stake pool is listed multiple times, the URI is rejected as invalid.

##### Handling stake pool links

When there is more than one pool registered with any of the specified `poolticker` parameters (whether for pool groups which have the same ticker for all pools, or for separate pools using the same ticker), the choice to which pool(s) to finally delegate is left to the user through the wallet UI.

The wallet UI should always confirm the exact delegation choice even when it is unambiguous from the URI.  When the user has multiple wallets, the wallet UI must select which wallet(s) the user will be delegating from.

If, during a wallet or other application's development process, it is still only able to support single pool links, these parameters in the URI query string should (by preference of the wallet UI designers) *either* be ignored *or* generate a warning message, to avoid leading the user to believe they are implementing a currently unsupported but perhaps popularly referenced multi-pool delegation list:

* any value for the first URI query argument;
* any URI query argument beyond the first.

#### Other URI queries

An ABNF grammar should be specified and explained similarly for each CIP that defines a new Cardano URI authority by explicitly defining the terms `authority` and `query` as for the "Stake pool" case above.

### Security Considerations

1. For payment links, we cannot prompt the user to send the funds right away as they may not be fully aware of the URI they clicked or were redirected to. Instead, it may be better to simply pre-populate fields in a transaction.
2. For either payment or staking links, we should be wary of people who disguise links as actually opening up a phishing website that LOOKS like that corresponding part of the wallet UI.
3. If wallets *create* stake pool links, the actual ada or lovelace balance should not be used literally as the `proportion` figure, to avoid revealing the identity of the wallet owner who is creating the portfolio (e.g. the proportions could be scaled to normalise the largest to `1`).

## Rationale: How does this CIP achieve its goals?

### Rationale for general URI scheme

#### Why not use Universal links, deep links or other non-protocol-based Solution?

An alternative solution to the original problem described above is to use standard URL links in combination with a routing backend system. The routing system is used to redirect to the app's URI. The advantage of this scheme is that it allows to provide a fallback mechanism to handle the case when no application implementing the protocol is installed (for instance, by redirecting to the App Store or Google Play). This is the approach behind iOS Universal Links and Android App Links. In general, it provides a better user experience but requires a centralized system which makes it unsuitable for as a multi-app standard.

For background, see

  - [Android Developer Docs > Add intent filters for incoming links](https://developer.android.com/training/app-links/deep-linking#adding-filters)
  - [Apple Developer Docs > Defining a custom URL scheme for your app](https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app)
  - [React Native > Linking](https://reactnative.dev/docs/linking.html)

### Rationale for payment links

#### Why confine payment links to address and amount like BIP-21?

BIP-21 is limited to only features Bitcoin supports. A similar feature for Ethereum would, for example, also support gas as an extra parameter. BIP-21 is easily extensible but we have to take precaution to avoid different wallets having different implementations of these features as they become available on Cardano. To get an idea of some extra features that could be added, consider this (still under discussion) proposal for Ethereum: [EIP-681](https://eips.ethereum.org/EIPS/eip-681)

### Rationale for stake pool links

#### How do URI delegation portfolio links supplement use of JSON files for the same purpose?

URIs facilitate the "social element" of delegated staking and pool promotion through a socially familiar, easily accessible, and less centralised convention for sharing stake pool references and potential delegation portfolios without having to construct or host a JSON file.

The processing of a JSON file delivered by a web server will depend highly on a user's platform and might not even be seen by the wallet application at all.  With a properly associated `web+cardano:` protocol, developers and users have another option available in case JSON files are not delivered properly to the wallet application.

For a CIP based on this principle, see [CIP-0017](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0017/README.md).

## Path to Active

### Acceptance Criteria

- [x] There exist one or more wallets supporting Payment URIs.
  - [x] Yoroi
  - [x] Begin Wallet
- [x] There exist one or more wallets supporting Stake Pool URIs.
  - [ ] TBD
- [x] There exist other CIPs or drafts defining additional URI protocols.
  - [x] [CIP-0099](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0099/README.md)  
- [x] There exist one or more wallets supporting additional URI protocols.
  - [x] Yoroi (CIP-0099)
  - [x] Begin Wallet (CIP-0099)
  - [x] VESPR (CIP-0099)  

### Implementation Plan

Encourage wallet and dApp developers to support all currently defined URI protocols, keeping in mind these are each likely to be considered separately:

- Payment URIs
- Stake Pool URIs
- all other URI schemes defined in separate CIPs

Education and advocacy about these standards should be done by:

- Developers of applications and standards requiring new URI schemes
- Cardano sponsoring companies
- Community advocates
- CIP editors

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
