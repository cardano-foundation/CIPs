---
CIP: ?
Title: Info action classification
Category: Tools
Status: Proposed
Authors:
    - Elena Bardo <elena.bardo@intersectmbo.org>
    - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors:
    - Elena Bardo <elena.bardo@intersectmbo.org>
    - Ryan Williams <ryan.williams@intersectmbo.org>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2025-01-15
License: CC-BY-4.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

There are special kinds of Info action defined by the Constitution (NCL, Budget)
yet there is no machine readable way to classify normal info actions from these special info actions

Without machine readable classification, tools misrepresent ratification thresholds for these special actions.

By defining a machine readable structure to be included within the Info action governance metadata, we ensure that tools can accurately represent such special cases to voters.

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

### Ledger Implementation

The ideal solution to this problem is differentiation at the ledger level, between these types of info action. But this would require significant work and a hard fork event, using metadata structures is much quicker and simpler for now.

### Other places within the metadata?

An alternative approach is to include a standardize structure within the text fields of governance action metadata.
This approach is not ideal as it would be much more fragile to authors mistyping, as well as placing a higher burden on tools to decode and search through text fields.

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. Uncomment the license you wish to use (delete the other one) and ensure it matches the License field in the header.

If AI/LLMs were used in the creation of the copyright text, the author may choose to include a disclaimer to describe their application within the proposal.
-->

<!-- This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). -->
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
