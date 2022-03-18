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

The core implementation should follow the [BIP-21](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki) standard (with `bitcoin:` replaced with `desktop+cardano:`)

Correct examples:
```
<a href="desktop+cardano-mainnet://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd">Buy/Send/Donate</a>
<a href="desktop+cardano-testnet://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd">Buy/Send/Donate</a>
<a href="desktop+cardano-mainnet-flight://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd">Buy/Send/Donate</a>

<a href="desktop+cardano-mainnet://stake?c94e6fe1123bf111b77b57994bcd836af8ba2b3aa72cfcefbec2d3d4">Stake with us</a>
<a href="desktop+cardano-mainnet://stake?POOL1=3.14159&POOL2=2.71828">Split between our 2 related pools</a>
<a href="desktop+cardano-mainnet://stake?COSD">Choose our least saturated pool</a>
```

Wrong examples:
```
<a href="desktop+cardano://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd?network=testnet">Buy/Send/Donate</a>
<a href="desktop+cardano-testnet://Ae2tdPwUPEZ76BjmWDTS7poTekAvNqBjgfthF92pSLSDVpRVnLP7meaFhVd?network=mainnet">Buy/Send/Donate</a>
<a href="desktop+cardano-mainnet://stake?POOL1=3.14159&POOL2=2.71828&network=testnet">Split between our 2 related pools</a>
```

## Considerations

Since Daedalus is shiped for a single network separately (mainnet and testnet) and can be installed alongside a fligt version (mainnet), the url needs to specify what version is being refered.

# ⚠️ Open questions
1. Most of the DEX relies on timing due to price volatility. If the user is only using a secure full-node wallet, which is not yet fully synchronized, how is a timeout handled?
2. Similar to 1. what if the starting of the wallet takes 2-10 mins? Is that still acceptable for a DEX? Should a timeout parameter be defined in the URL so that the user DOES NOT make the transaction if the dApp runs in a timeout?