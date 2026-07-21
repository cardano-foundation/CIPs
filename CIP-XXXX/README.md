---
CIP: "?"
Title: DRep Pledge
Category: Ledger
Status: Proposed
Authors:
    - Ryan Wiley <cerkoryn@gmail.com>
Implementors: []
Discussions: [Original PR: https://github.com/cardano-foundation/CIPs/pull/1225]
Solution To:
    - CPS-0033: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0033
Created: 2026-07-09
License: CC-BY-4.0
---

## Abstract

Cardano's on-chain governance model allows Ada holders to delegate voting power to registered DReps. However, the ledger currently has no DRep pledge field. A DRep may register, publish metadata, receive delegated voting power, and vote on governance actions, but there is no ledger-native value by which that DRep can declare an amount of Ada as personal stake in the role.

This CIP adds `drepPledge` as a declared `Coin` field to DRep registration and update certificates. The value is stored in DRep ledger state and exposed to ledger queries. It is analogous to stake pool declared pledge in that it is a declared amount recorded by the ledger, but this CIP does not enforce the declaration and defers it for use in any voting-power, reward, registration, activity, or compensation calculation.

The purpose of this CIP is to introduce the mechanism for DRep pledge first. Future CIPs may use DRep pledge for voting-power limits, compensation eligibility, Sybil resistance, reputation signaling, or other incentive mechanisms. Those future mechanisms should not activate before DReps have had adequate time to declare pledge and for tooling to add support once this capability exists on-chain.

## Motivation: Why is this CIP necessary?

### DReps have delegated voting power but no pledge field

[CIP-1694](../CIP-1694/README.md) introduced DReps as one of Cardano's governance bodies. Any Ada holder may register as a DRep, and other Ada holders may delegate voting rights to that DRep. DRep voting power is based on delegated Lovelace.

This establishes the delegation side of the system, but it does not establish an on-chain pledge field for DReps. A DRep may have large delegated voting power without any ledger-native way to declare personal economic commitment. Today, tools can show metadata, payment addresses, voting history, and delegated stake, but not a ledger-defined DRep pledge.

### Metadata is useful but insufficient for future ledger rules

[CIP-0119](../CIP-0119/README.md) defines useful DRep metadata. That metadata can describe a DRep's identity, motivations, qualifications, payment address, and other public information. It is intentionally off-chain and flexible.

Pledge is different. If future ledger rules are expected to use pledge as an input, the value should be represented directly in ledger state. A metadata-only pledge field would be useful for social signaling, but it would not provide a deterministic, consensus-visible value that later ledger rules can reference without depending on off-chain metadata interpretation.

### Pledge should be introduced before incentives

If a future hard fork were to introduce pledge incentives and the pledge field at the same time, DReps could face a race to update their registrations before pledge-dependent rules affected voting, rewards, or eligibility. That creates unnecessary operational and security risk.

This CIP avoids that problem by adding only the declaration field. DReps can begin declaring pledge as part of normal registration and update workflows, while the community continues researching whether and how pledge should later affect governance incentives or constraints.

## Specification

### Terminology

- `drepPledge`: the declared amount of Ada, represented as a `Coin`, associated with a registered DRep.
- `drep_pledge`: the CDDL field name corresponding to `drepPledge`.
- "Declared DRep pledge": DRep pledge recorded in ledger state.

### DRep registration certificates

DRep registration certificates MUST include `drepPledge`.

In CDDL-like form:

```cddl
reg_drep_cert = (16, drep_credential, coin, anchor / nil, coin / nil)
```

where:

- `drep_credential` is the DRep credential.
- `coin` remains the DRep registration deposit supplied by the certificate.
- `anchor / nil` remains the optional DRep metadata anchor.
- `drep_pledge` is the declared DRep pledge.

When a DRep is registered, the ledger MUST store `drepPledge` in the DRep's ledger state.

### DRep update certificates

DRep update certificates MUST include `drepPledge`.

In CDDL-like form:

```cddl
update_drep_cert = (18, drep_credential, anchor / nil, drep_pledge : coin)
```

where:

- `drep_credential` is the DRep credential.
- `anchor / nil` remains the optional updated DRep metadata anchor.
- `drep_pledge` is the updated declared DRep pledge.

When a DRep update certificate is accepted, the ledger MUST replace the previous `drepPledge` value for that DRep with the value supplied in the update certificate.

An update that changes only the DRep metadata anchor still MUST include `drepPledge`. If the DRep does not intend to change pledge, the update certificate should resubmit the current pledge value.

### DRep ledger state

DRep ledger state MUST include `drepPledge`.

Conceptually:

```haskell
data DRepState = DRepState
  { drepExpiry  :: EpochNo
  , drepAnchor  :: StrictMaybe Anchor
  , drepDeposit :: CompactForm Coin
  , drepPledge  :: Coin
  , drepDelegs  :: Set (Credential Staking)
  }
```

The exact implementation type MAY use a compact representation if ledger maintainers prefer consistency with other stored `Coin` values.

### Accepted pledge values

`drepPledge` MAY be zero.

`drepPledge` MAY be any non-negative `Coin` value that can be represented by the ledger's `Coin` type.

This CIP does not introduce a minimum DRep pledge, maximum DRep pledge, pledge ratio, pledge leverage parameter, or pledge-specific protocol parameter.

### Authorization

DRep registration, update, and deregistration authorization remains unchanged from CIP-1694.

The DRep credential or script that authorizes the DRep registration or update also authorizes the declared `drepPledge` value in that certificate. This CIP does not introduce any additional witness, payment credential, stake credential, owner credential, or pledge-specific authorization requirement.

### Hard-fork activation and migration

This CIP changes ledger certificate serialization and DRep ledger state. It therefore requires a hard fork into a new ledger era.

At the hard-fork boundary:

- all already-registered DReps MUST be migrated with `drepPledge = 0`;
- the existing DRep deposit values MUST be preserved;
- the existing DRep metadata anchors MUST be preserved;
- the existing DRep expiry/activity state MUST be preserved;
- the existing DRep delegation state MUST be preserved.

After activation, new-era DRep registration and update certificates MUST include `drepPledge`. Old-shape post-activation DRep registration and update certificates that omit `drepPledge` MUST be rejected as invalid for the new era.

Historical pre-activation transactions and certificates remain valid historical ledger data under their original era rules.

### Ledger queries and tooling

Ledger state queries SHOULD expose `drepPledge` for registered DReps.

Wallets, CLIs, explorers, indexers, governance tools, and DRep directories SHOULD display this value as declared DRep pledge.

## Rationale: How does this CIP achieve its goals?

### A ledger field is the smallest useful primitive

This proposal intentionally does not define a DRep compensation scheme, voting-power cap, pledge leverage mechanism, or proof-of-ownership rule. Those mechanisms require separate design work and likely separate community debate.

However, many such mechanisms need the same primitive: a ledger-native DRep pledge value. Adding `drepPledge` first allows the ecosystem to build tooling, index the value, display it to delegators, and gather real-world usage data before pledge is used in higher-stakes calculations.

### DRep pledge mirrors stake pool pledge as a declaration

Stake pool pledge is already familiar to Cardano users as a declared value in pool parameters. This CIP uses the same general idea for DReps, but without the current stake pool pledge satisfaction check or any reward effect (for now).

That limitation is deliberate. DRep pledge should not immediately change governance power or incentives before the community has agreed on the right incentive model.
The naming and storage model intentionally mirrors pool pledge at the appropriate level:

- current stake pool parameters include `sppPledge :: Coin` and current stake pool state stores `spsPledge :: Coin`;
- this CIP adds `drepPledge :: Coin` to DRep state;
- the CDDL label is `drepPledge : coin`, matching the existing pool parameter label.

The absence of a DRep pledge satisfaction check is deliberate. DRep pledge should not immediately change governance power or incentives before the community has agreed on the right incentive model.

### A hard fork is required

Current Conway-era certificate and state shapes do not include DRep pledge.

The Conway CDDL defines DRep registration and update certificates as:

```cddl
reg_drep_cert = (16, drep_credential, coin, anchor / nil)
update_drep_cert = (18, drep_credential, anchor / nil)
```

The current ledger API likewise represents DRep registration as credential, deposit, and optional anchor, while DRep updates contain only credential and optional anchor. Current DRep state stores expiry, anchor, deposit, and delegators.

Adding `drepPledge` to the certificate and DRep state changes consensus-visible ledger serialization and state. It is therefore a new-era hard-fork change, not an optional wallet or metadata convention.

Relevant current implementation references include:

- [Conway CDDL](https://raw.githubusercontent.com/IntersectMBO/cardano-ledger/master/eras/conway/impl/cddl-files/conway.cddl)
- [Conway DRep certificates](https://cardano-ledger.cardano.intersectmbo.org/cardano-ledger-conway/Cardano-Ledger-Conway-TxCert.html)
- [Conway governance certificate transition](https://cardano-ledger.cardano.intersectmbo.org/cardano-ledger-conway/src/Cardano.Ledger.Conway.Rules.GovCert.html)
- [DRep state](https://cardano-ledger.cardano.intersectmbo.org/cardano-ledger-core/Cardano-Ledger-DRep.html)

### Separating declaration from enforcement avoids a registration race

If pledge-dependent rules were introduced at the same time as the pledge field, existing DReps would have no prior opportunity to declare pledge. Depending on the later incentive mechanism, that could temporarily distort voting power, compensation eligibility, DRep visibility, or other governance behavior.

By introducing the field first and migrating existing DReps to zero pledge, DReps can update voluntarily before any future rule uses pledge. This creates a cleaner path for future CIPs and a safer operational rollout.

### Relationship to DRep metadata

CIP-0119 remains the right place for rich DRep profile information. A DRep may still describe goals, qualifications, payment information, and social identity in metadata.

This CIP only adds a small consensus-visible value. The value is suitable for later ledger rules because every node sees and stores the same value as part of DRep state.

### Future use cases

Future CIPs may use `drepPledge` for mechanisms such as:

- limiting DRep voting power to a multiple of declared pledge;
- making declared pledge one input to DRep compensation eligibility;
- adding anti-concentration rules based on the relationship between pledge and delegated voting power;
- providing a Sybil-resistance signal for DRep discovery tools;
- improving reputation displays for delegators choosing among DReps.

Any future CIP that uses DRep pledge should define its own incentive rules, snapshot behavior, migration window, and consequences for under-pledged DReps.

## Path to Active

### Acceptance Criteria

- [ ] The ledger specification and CDDL include `drepPledge` in DRep registration and update certificates.
- [ ] The ledger implementation stores `drepPledge` in DRep state and migrates existing DReps with `drepPledge = 0`.
- [ ] State query and transaction-building interfaces expose enough information for wallets, CLIs, explorers, indexers, and governance tools to submit and display declared DRep pledge.
- [ ] The change is released as part of a hard fork that has passed the required on-chain governance process.

### Implementation Plan

- [ ] Update the next-era CDDL and ledger specification for DRep registration and update certificates.
- [ ] Extend DRep ledger state with `drepPledge`.
- [ ] Add hard-fork migration logic that initializes existing registered DReps with `drepPledge = 0`.
- [ ] Update DRep registration and update transition rules to store the supplied `drepPledge`.
- [ ] Update ledger queries, transaction builders, and downstream tooling to handle the new field.
- [ ] Add ledger conformance tests covering registration, update, migration, deregistration, and unchanged voting-power/activity behavior.
- [ ] Include the change in a node release for the target hard-fork era.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
