---
CIP:
  ?
Title: Cardano URIs - Enhanced Payments
Category: Wallets
Status: Proposed
Authors:
  - Adam Dean <adam@crypto2099.io>
Implementors: [ ]
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-06-15
License: Apache-2.0
---

## Abstract

This CIP will propose a new [CIP-13] Extension; introducing a new,
dedicated `payment` authority and provide support for _Native Assets_ and
transactional _Metadata_ as well as providing for extensibility and versioning.
All features lacking in the original [CIP-13] payment URIs.

## Motivation: why is this CIP necessary?

[CIP-13] was originally introduced in early 2021, prior to the Mary hard fork
event that brought _Native Assets_ to Cardano. Since that time the Cardano
Native Asset ecosystem has flourished and become a large, multi-million dollar
economy. However, [CIP-13] Payment URIs have not been updated to support Native
Assets and have struggled to find adoption amongst mobile wallet creators.

## Specification

**COMING SOON<sup>TM</sup>**

## Rationale: how does this CIP achieve its goals?

This CIP achieves its goals by defining a new, explicit `Payment URI` standard
that is aligned with modern Cardano transaction standards such as:

* Providing an address to pay to
* Providing a Lovelace amount to send
* Providing one (or more) Native Assets to send
* Providing a transaction metadata message to send
* Providing an optional datum to include

## Path to Active

### Acceptance Criteria

* [ ] Community Feedback and Review Integrated
* [ ] At least one wallet supports this payment standard
* [ ] At least one project utilizing this payment standard

### Implementation Plan

Leveraging existing connections within the ecosystem we will find willing
partners to integrate this new standard and deploy a proof of concept
integration.

## Copyright

This CIP is licensed
under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[CIP-13]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0013/
