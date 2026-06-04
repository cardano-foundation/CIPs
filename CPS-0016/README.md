---
CPS: 16
Title: Cardano URIs
Category: Tools
Status: Open
Authors:
  - Adam Dean <adam@crypto2099.io>
  - Mad Orkestra <mad@madorkestra.com>
Proposed Solutions:
  - CIP-0013: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013
  - CIP-0099: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0099
  - CIP-0107: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0107
  - CIP-0134: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0134
  - CIP-0158: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0158
  - CIP-0162: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0162
Discussions:
  - Issue - CIP-0013 Current state of integration and further advancements: https://github.com/cardano-foundation/CIPs/issues/836
  - CIP-0013 pull request: https://github.com/cardano-foundation/CIPs/pull/559
  - CIP-0107 pull request: https://github.com/cardano-foundation/CIPs/pull/635
  - Original pull request: https://github.com/cardano-foundation/CIPs/pull/841
  - CIP-0134 pull request: https://github.com/cardano-foundation/CIPs/pull/888
Created: 2024-06-15
License: CC-BY-4.0
---

## Abstract

Cardano URI schemes ([CIP-0013]) have been defined since early 2021. However, some
of the proposed standards have languished and struggled for adoption event as
the amount of wallet developers in the ecosystem has skyrocketed. This CPS aims
to create a centralized point of reference for those interested in creating new
standards or publishing integration solutions.

## Problem

A keen pain point in the utilization of blockchain is the archaic and convoluted
processes necessary to interact with the blockchain or cite historical ledger
data. Well-defined URI schemes can provide a plethora of easy access and
interaction methods, particularly to mobile users, since they can leverage
deep-linking and QR technologies to pass data between applications.

## Use Cases

The Cardano URI Scheme(s) that exist already present several fantastic use cases
for URI schemes. We welcome additional or expanded definitions to be added to
this section for further discussion, development, and adoption by the community.

### Easy On-Chain Interactions

#### Payments

1. The original specification of [CIP-0013][CIP-0013-payment] defined only the
   base `web+cardano:` **scheme** and an **authority**-less path consisting of a
   payment address and an optional `amount` query parameter to specify via QR
   code or deep-link an address and amount of Lovelace to send.
2. In 2024 [a new CIP was proposed](https://github.com/cardano-foundation/CIPs/pull/843) defining an explicit `//pay`
   **authority** as well as path and query parameters to support _Native Assets_
   and transaction _Metadata_.

#### Staking/Delegation

1. The first extension to [CIP-0013][CIP-0013-staking] added the `//stake`
   **authority** and some query parameter options to specify a Cardano Stake
   Pool. The goal of these URIs would be to make it easy for a user to switch
   their wallet's stake delegation to the pool in question. This could be
   performed via easy deep-link integration on stake pool website(s) and social
   media, and also through real-world advertising such as banners, flyers, and
   business cards at marketing and networking events.

#### Onboarding/Airdrops

1. In 2023 [CIP-0099] was introduced, adding a `//claim` **authority** and
   defining a URI + wallet interaction protocol that would allow a user with
   only access to a URI to "claim" an airdrop of _Lovelace_ and/or _Native
   Assets_ assuming that both the wallet and the project server were correctly
   configured to follow the protocol.

#### Open URLs in the in-app browser

1. In 2026 [CIP-0158] introduced a new `//browse` **authority** defining a URI
   with versioning to allow opening a percent-encoded `https://` or `http://` address
   including forwarded parameters in the in-app browser of mobile wallets with
   the intent to gain easier access to the full wallet functionality and improve
   the overall mobile user experience.

#### DRep links

1. Also in 2026 [CIP-0162] introduced a new `//drep` **authority** defining a new
   URI and wallet behaviour for frictionless DRep delegation, taking in a [CIP-0129]
   DRep-Id with the intent to open the wallet-app, validate the DRep-Id against
   on-chain data and - if a valid Id of a registered DRep has been provided -
   create a governance delegation transaction for the user to sign and submit.

### Easy Historical Reference

#### Blocks and Transactions

1. In 2023 [CIP-0107] was proposed, this CIP introduced the `//block` and
   `//transaction` **authorities** along with relevant **path** and **query**
   parameters. This novel use of URI structures allows for easy reference to
   specific events and points in time of the blockchain ledger's history. This
   proposal makes referencing a point in the chain's history relatively trivial
   which can be an important step in data availability layers for external on-
   and off-chain solutions.

## Goals

The goals of this CPS are as follows:

* [X] Provide an easy-to-reference repository for all `web+cardano:` URI
  solutions to simplify integrations.
* [X] Define a list of known `web+cardano:` URI authorities to prevent overlap
  and collision by developers creating new solutions.
* [X] Provide a platform to centralize new discussions about emerging standards
  that may arise in the future.

## Open Questions

1. What can we do as a community to encourage more applications and software
   providers to support `web+cardano:` URIs?
2. What software or best practices exist to aid developers in deploying support
   for `web+cardano:` URIs?
3. What new authorities or protocols could be built to leverage these URIs?
4. What does the process look like to register a new `web+cardano:` URI
   authority or protocol?

### Proposal Process

Recent best practices in this repository suggest that the preferred method is
for new standards that expand functionality should be defined as new, discrete
CIPs unless the existing CIP provides for the capability of versioning and
iterative improvement.

By creating separate, discrete CIPs for new standards this allows for a clean
history of discussion and community consensus building around new standards as
well as measurable progress towards adoption.

### Registered URI Authorities

Per [URI Syntax] a URI consists of the following structure:

```abnf
URI = scheme ":" ["//" authority] path ["?" query] ["#" fragment]
```

Given that the shared scheme of `web+cardano:` is known and accepted and the
original version of [CIP-0013] declared an authority-less, path-only structure:
**All future `web+cardano:` URI extensions MUST register a new, unique authority
or SHOULD define a new version of an existing **authority** that has explicitly
allowed for versioning in its definition.

The following are the currently registered URI **authorities** mentioned in
CIPs:

* `null`: (Blank/no Authority) registered in [CIP-0013][CIP-0013-payment]
* `//stake`: registered in [CIP-0013][CIP-0013-staking]
* `//claim`: supports versioning, registered in [CIP-0099]
* `//transaction`: supports versioning (?), registered in [CIP-0107]
* `//block`: supports versioning (?), registered in [CIP-0107]
* `//addr`: registered in [CIP-00134]
* `//browse`: registered in [CIP-0158]
* `//drep`: registered in [CIP-0162]

## Copyright

This CPS is licensed under [CC-BY-4.0].

[CIP-0013]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013

[CIP-0013-payment]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013#for-payment-uris

[CIP-0013-staking]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013#for-stake-pool-uris

[CIP-0099]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0099

[CIP-0107]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0107

[CIP-0129]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0129

[CIP-00134]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0134

[CIP-0158]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0158

[CIP-0162]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0162

[CC-BY-4.0]:https://creativecommons.org/licenses/by/4.0/legalcode

[URI Syntax]:https://en.wikipedia.org/wiki/Uniform_Resource_Identifier#Syntax
