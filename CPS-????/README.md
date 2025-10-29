---
CPS: ?
Title: Canonical CBOR Serialization Standard
Category: Tools, Wallets, Ledger
Status: Open
Authors:
    - Hinson Wong <hinson.wong@deltadefi.io>
    - Tsz Wai Wu <tszwai@deltadefi.io>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2025-10-29
License: CC-BY-4.0
---

## Abstract

There is no canonical CBOR serialization standard in Cardano. While this is a delibrate design choice initially, standardizing it has growing popularity in Cardano developer community as evidenced by developer meetups such as Cardano Builder Fest 2025 hosted in Vietnam. This CPS outlines the motivation of the growing concern of fragmented CBOR serialization patterns across in the community.

## Problem

<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

Unstandardized CBOR serialization has hindered the progress for Cardano developers community for a long time. While it allows higher flexibility of tool chain selection, it caused community overheads

- Wallet sign tx change the tx body
- Unpredictable transaction building
- Difference in script serialzation

## Use cases

<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

- Developers can switch across libraries and tools and yield a predictable result

## Goals

<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

Solving this CPS means:

1. There is a CIP specifying guidance on standardizing Cardano CBOR serialization.

2. The community, naming serialization libraries and wallets are aware of the standard and comply accordingly.

3. Optional: If we deemed the standard should be enforced, the standard is then implemented on the ledger.

A good solution should consist of both a well crafted standard with clear guiding principle, carrying our the comprehensive `Path to Active`.

## Open Questions

<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

<!-- OPTIONAL SECTIONS: see CIP-9999 > Specification > CPS > Structure table -->

### Should we enforce it in ledger?

- Not enforcing: difficult to make wider tooling community comply with it
- Enforcing: backward compatibility issue, might not be practical to do so

### What are the guiding principles to decide the standard?

Some possible dimensions:

- Efficiency: whichever producing smallest size of transaction
- Friction: whichever more adapted in current community
- etc

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
