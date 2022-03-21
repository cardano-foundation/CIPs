---
CIP: 35
Title: Daedalus URI Scheme
Authors: Daniel Main <daniel.main@iohk.io>
Comments-URI:
- https://github.com/cardano-foundation/CIPs/pull/130
Status: Draft
Type: Informational
Created: 2022-03-18
License: CC-BY-4.0
---

# Abstract

This proposal is an extension of CIP-0013, which describes a basic URI scheme to handle ada transfers or partial transactions with Daedalus or any desktop Wallet installed in the operating system.

# 💡 Motivation

DEX, Web-dApps and Desktop-dApps (e.g. games or desktop applications) should have the possibility to interact directly with desktop wallets. By defining a URI scheme and registering it in the operating system, it will allow opening Daedalus or any desktop wallet same as when you call or click a mailto:email@sample.com and your email client is opened.

An application could ask for a payment and offer options like PayPal, Visa, cardano-web. Although a user might want to help cardano to get more decentralized using a full-node-wallet that is why the application could also offer payments with a cardano-desktop.
The usage of a different URL will solve the problem of users, which have multiple wallets: browser-wallet for daily usage and a secure desktop wallet for the savings.

# 📖 Specification

The core implementation should follow the [BIP-21](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki) standard (with `bitcoin:` replaced with `web+cardano:`)

Correct examples:
```
<a href="web+cardano://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd?unix-timestamp-timeout=1647896861">Buy/Send/Donate</a>
<a href="web+cardano-testnet://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd?unix-timestamp-timeout=1647896861">Buy/Send/Donate (Testnet)</a>
<a href="web+cardano-flight://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd?unix-timestamp-timeout=1647896861">Buy/Send/Donate (Mainnet and using Daedalus Flight)</a>
```

## Considerations

- Since Daedalus is shiped for a single network separately (mainnet and testnet) and can be installed alongside a fligt version (mainnet), the url needs to specify what version is being refered.
- Adding the unix-timestamp-timeout parameter, in other words: the time in (Unix format) in the future where the transaction is no longer valid. This will allow using a desktop wallet that might take minutes to start or not be yet synchronized will avoid the user to send unnecessarily a transaction.