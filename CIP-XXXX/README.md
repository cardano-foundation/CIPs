---
CIP: XXXX
Title: Cardano URIs - DRrep Delegation
Category: Wallets
Status: Proposed
Authors:
    - Mad Orkestra <mad@madorkestra.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2025-07-29
License: CC-BY-4.0
---

## Abstract

This CIP proposes a new [CIP-13](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013) extension: A new URI scheme authority named `delegate` under `web+cardano` to enable Cardano mobile wallets and wallet extensions to create and submit a DRep delegation transaction for a given DRep-Id, using a standardized, interoperable URI format.

## Motivation: why is this CIP necessary?

With Cardano Governance now in full effect a high level of participation / DRep delegation is needed to solidify and secure the consensus mechanisms put in place and ensure decentralisation of power. Delegating to a DRep however - especially on mobile devices - can be a cumbersome task involving multiple steps from copying or typing a complicated DRep-Id or visiting a dedicated website, search for DRep by Id or Name, create and sign a transaction - or use in-app DRep explorers which some wallets offer right now, others don’t.

The goal of this CIP is to make DRep delegation as easy as clicking a button on desktop browsers or scanning a QR-Code with your mobile device, which automatically opens the user's preferred wallet via deep-linking compatible method and create a DRep-delegation transaction for the transmitted DRep-Id for the user to review, sign and submit the transaction.

With the existing `web+cardano://` URIs for almost all other methods of participation in the Cardano ecosystem such as payments and Stake Pool delegation already defined, this proposed extension adds another missing piece of the puzzle.

This CIP will enable fast, frictionless and error-prone DRep delegation and will provide DReps at the same time with another way to promote themselves without the need of lengthy DRep-Ids, specific governance websites or dedicated DRep browsers/interfaces inside of wallets.

Especially for real world events this will provide a feasible solution for instant DRep-delegation in environments where copy & pasting a DRep-Id isn't an option. It will also mitigate some of the painpoints for wallets to implement their own way of DRep discovery and delegation by providing an ecosystem-wide standard for One-Click-Delegation.

## Specification

This extension to the [CIP-13](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0013) URN scheme defines the delegate authority for Cardano URIs.

### URI Format

`web+cardano://delegate/<DRep-Id>`

- Authority (REQUIRED): delegate
- DRep-Id (REQUIRED): Bech32 [CIP-129](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0129) DRep-Id | "always_abstain" | "always_no_confidence"

### Example URIs

`web+cardano://delegate/always_abstain`

### Wallet Behavior

- Parse and validate the given DRep-Id against [CIP-129](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0129) or one of the default options
- Check on-chain if the given DRep-Id belongs to a registered DRep
- Create a delegation transaction
- Display the DRep-Id (and registration status) to the user and prompt to sign and submit the delegation transaction

### Security Considerations

- Wallets SHOULD validate if the given DRep-Id is a valid [CIP-129](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0129) DRep-Id, otherwise provide a warning to the user
- Wallets SHOULD validate if the given DRep-Id belongs to a registered DRep - otherwise provide a warning to the user.

## Rationale: how does this CIP achieve its goals?

A dedicated `delegate` authority isolates app navigation from other authorities such as `pay`, `browse` or `stake`, improving clarity and interoperability.

## Path to Active

### Acceptance Criteria

- [ ] Community Feedback and Review Integrated
- [ ] One or more wallets support this new delegate authority

### Implementation Plan

Leveraging existing connections within the ecosystem; we will find willing partners to integrate this new standard and deploy a proof of concept integration.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

