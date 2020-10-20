---
CIP: TODO
Title: Cardano URI Scheme
Authors: Sebastien Guillemot <sebastien@emurgo.io>, Vicente Almonacid <vicente@emurgo.io>
Comments-URI:
- https://github.com/Emurgo/EmIPs/pull/2
- https://forum.cardano.org/t/cip-cardano-payment-uri-scheme/41457
Status: Draft
Type: Informational
Created: 2020-10-20
License: CC-BY-4.0
---

# Abstract

This proposal describes a basic URI scheme to handle ADA transfers, as well
as possible approaches for a multiplatform implementation.

# Motivation

Users who create community content often want donations as a financial incentive. However, forcing users to open their wallet and copy-paste an address lowers the amount of people likely to send tokens (especially if they have to sync their wallet first).

If donating was as simple as clicking a link that opens a light wallet with pre-populated fields, users may be more willing to send tokens. URI schemes would enable users to easily make payments by simply clicking links on webpages or scanning QR Codes.

# Specification

The core implementation should follow the [BIP-21](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki) standard (with `bitcoin:` replaced with `web+cardano:`)

Rationale:
- Use `cardano:` over `ada:` as other projects that implement this standard tend to take the project name over the currency name (this makes sense if we consider this protocol as a generic way for interacting with the blockchain through wallets - as opposed to a simple payment system)
- Many wallets support multiple currencies. Following the same standard will ensure higher adoption of our protocol.

Example:
```
<a href="web+cardano:Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd">Donate</a>
```

## Considerations

1. BIP-21 is limited to only features Bitcoin supports. A similar feature for Ethereum would, for example, also support gas as an extra parameter. BIP-21 is easily extensible but we have to take precaution to avoid different wallets having different implementations of these features as they become available on Cardano. To get an idea of some extra features that could be added, consider this (still under discussion) proposal for Ethereum: [EIP-681](https://eips.ethereum.org/EIPS/eip-681)

2. Depending on the protocol registration method (see next section), browsers generally enforce a `web+` or `ext+` prefix for non-whitelisted protocols (note: `bitcoin:` was whitelisted). The prefix `ext+` is recommended for extensions, but not mandatory.

## ABNF Grammar (Proposal)

This is an initial, simplified protocol definition for fast implementation; it only requires an address and an optional amount parameter. As discussed above, these rules are likely to evolve in time in order to support additional features, including unique capabilities of the Cardano blockchain.

```
cardanourn     = "web+cardano:" cardanoaddress [ "?" amountparam ]
cardanoaddress = *base58
amountparam    = "amount=" *digit [ "." *digit ]
```

The amount parameter must follow the [same rules](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki#transfer-amountsize) described in BIP-21, namely, it must be specified in decimal ADA, without commas and using the period (.) decimal separator.

## Security Considerations

1. We cannot prompt the user to send the funds right away as they may not be fully aware of the URI they clicked or were redirected to. Instead, it may be better to simply pre-populate fields in a transaction.
2. We should be wary of people who disguise “donate” links as actually opening up a phishing website that LOOKS like a wallet.

# Rationale

## Why not use Universal links, deep links and other non-protocol-based Solution

An alternative solution to the original problem described above is to use standard URL links in combination with a routing backend system. The routing system is used to redirect to the app's URI. The advantage of this scheme is that it allows to provide a fallback mechanism to handle the case when no application implementing the protocol is installed (for instance, by redirecting to the App Store or Google Play). This is the approach behind iOS Universal Links and Android App Links. In general, it provides a better user experience but requires a centralized system which makes it unsuitable for as a multi-app standard.

## Read More

https://developer.mozilla.org/en-US/docs/Web/API/Navigator/registerProtocolHandler

https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/protocol_handlers

https://developer.android.com/training/app-links/deep-linking#adding-filters

https://facebook.github.io/react-native/docs/linking.html

https://developer.apple.com/documentation/uikit/core_app/allowing_apps_and_websites_to_link_to_your_content/defining_a_custom_url_scheme_for_your_app
