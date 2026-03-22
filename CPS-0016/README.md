---
CPS: 16
Title: Cardano URIs
Status: Open
Category: Tools
Authors:
  - Adam Dean <adam@crypto2099.io>
Proposed Solutions:
  - CIP-0013: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013
  - CIP-0099: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0099
  - CIP-0107: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0107
  - CIP-0134: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0134
Discussions:
  - https://github.com/cardano-foundation/CIPs/issues/836
  - https://github.com/cardano-foundation/CIPs/pull/559
  - https://github.com/cardano-foundation/CIPs/pull/635
  - https://github.com/cardano-foundation/CIPs/pull/841
  - https://github.com/cardano-foundation/CIPs/pull/843
  - https://github.com/cardano-foundation/CIPs/pull/888
Created: 2024-06-15
License: CC-BY-4.0
---

## Abstract

Cardano URI schemes ([CIP-13]) have been defined since early 2021. However, some
of the proposed standards have languished and struggled for adoption even as
the amount of wallet developers in the ecosystem has skyrocketed. This CPS aims
to create a centralized point of reference for those interested in creating new
standards or publishing integration solutions.

## Problem

A keen pain point in the utilization of blockchain is the archaic and convoluted
processes necessary to interact with the blockchain or cite historical ledger
data. Well-defined URI schemes can provide a plethora of easy access and
interaction methods, particularly to mobile users, since they can leverage
deep-linking and QR technologies to pass data between applications.

## Use cases

The Cardano URI Scheme(s) that exist already present several fantastic use cases
for URI schemes. We welcome additional or expanded definitions to be added to
this section for further discussion, development, and adoption by the community.

### Easy On-Chain Interactions

#### Payments

1. The original specification of [CIP-13][CIP-13-payment] defined only the
   base `web+cardano:` **scheme** and an **authority**-less path consisting of a
   payment address and an optional `amount` query parameter to specify via QR
   code or deep-link an address and amount of Lovelace to send.
2. In 2024 [a new CIP was proposed](https://github.com/cardano-foundation/CIPs/pull/843) defining an explicit `//pay`
   **authority** as well as path and query parameters to support _Native Assets_
   and transaction _Metadata_.

#### Staking/Delegation

1. The first extension to [CIP-13][CIP-13-staking] added the `//stake`
   **authority** and some query parameter options to specify a Cardano Stake
   Pool. The goal of these URIs would be to make it easy for a user to switch
   their wallet's stake delegation to the pool in question. This could be
   performed via easy deep-link integration on stake pool website(s) and social
   media, and also through real-world advertising such as banners, flyers, and
   business cards at marketing and networking events.

#### Onboarding/Airdrops

1. In 2023 [CIP-99] was introduced, adding a `//claim` **authority** and
   defining a URI + wallet interaction protocol that would allow a user with
   only access to a URI to "claim" an airdrop of _Lovelace_ and/or _Native
   Assets_ assuming that both the wallet and the project server were correctly
   configured to follow the protocol.

### Easy Historical Reference

#### Blocks and Transactions

1. In 2023 [CIP-107] was proposed, this CIP introduced the `//block` and
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
2. What new authorities or protocols could be built to leverage these URIs?
3. What does the process look like to register a new `web+cardano:` URI
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
original version of [CIP-13] declared an authority-less, path-only structure:
**All future `web+cardano:` URI extensions MUST register a new, unique authority
or SHOULD define a new version of an existing **authority** that has explicitly
allowed for versioning in its definition.

The following are the currently registered URI **authorities** mentioned in
CIPs:

* `null`: (Blank/no Authority) registered in [CIP-13][CIP-13-payment]
* `//stake`: registered in [CIP-13][CIP-13-staking]
* `//claim`: supports versioning, registered in [CIP-99]
* `//transaction`: supports versioning (?), registered in [CIP-107]
* `//block`: supports versioning (?), registered in [CIP-107]
* `//addr/`: registered in [CIP-134]

## Copyright

This CPS is licensed under [CC-BY-4.0].

[CIP-13]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013

[CIP-13-payment]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013#for-payment-uris

[CIP-13-staking]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013#for-stake-pool-uris

[CIP-99]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0099

[CIP-107]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0107

[CIP-134]:https://github.com/cardano-foundation/CIPs/tree/master/CIP-0134

[CC-BY-4.0]:https://creativecommons.org/licenses/by/4.0/legalcode

[URI Syntax]:https://en.wikipedia.org/wiki/Uniform_Resource_Identifier#Syntax
