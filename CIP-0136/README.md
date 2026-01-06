---
CIP: 136
Title: Governance metadata - Constitutional Committee votes
Category: Metadata
Status: Proposed
Authors:
    - Ryan Williams <ryan.williams@intersectmbo.org>
    - Eystein Magnus Hansen <eysteinsofus@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/878
Created: 2024-07-17
License: CC-BY-4.0
---

## Abstract

The Conway ledger era ushers in on-chain governance for Cardano via [CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md), with the addition of many new on-chain governance artifacts.
Some of these artifacts support the linking of off-chain metadata, as a way to provide context to on-chain actions.

The [CIP-100 | Governance Metadata](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100) standard provides a base framework for how all off-chain governance metadata can be formed and handled.
This standard was intentionally limited in scope, so that it can be expanded upon by more specific subsequent CIPs.

This proposal aims to provide a specification for the off-chain metadata vocabulary that can be used to give context to Constitutional Committee (CC) votes.

## Motivation: Why is this CIP necessary?

The high-level motivation for this proposal is to provide a standard which improves legitimacy of Cardano's governance system.

### Clarity for governance action authors

Governance action authors are likely to have dedicated a significant amount of time to making their action meaningful and effective (as well as locking a significant deposit).
If this action is not able to be ratified by the CC, it is fair for the author to expect a reasonable explanation from the CC.

Without reasonable context being provided by the CC votes, authors may struggle to iterate upon their actions, until they are deemed constitutional.
This situation could decrease perceived legitimacy in Cardano's governance.

### Context for other voting bodies

By producing a standard we hope to encourage all CC members to attach rich contextual metadata to their votes.
This context should show CC member's decision making is fair and reasonable.

This context allows the other voting bodies to adequately check the power of the CC.

### CC votes are different to other types of vote

The CC and their votes are fundamentally very different from the other voting bodies.
This makes reusing standards from these voting bodies problematic.

### Inclusion within interim constitution

Cardano's [Interim Constitution Article VI Section 4](https://github.com/IntersectMBO/interim-constitution/blob/75155526ce850118898bd5eacf460f5d68ceb083/cardano-constitution-0.txt#L330) states:

```txt
Constitutional Committee processes shall be transparent.
The Constitutional Committee shall publish each decision.
When voting no on a proposal, the Committee shall set forth the basis
for its decision with reference to specific Articles of this Constitution
that are in conflict with a given proposal.
```

This section suggests that the CC shall provide rationale documents.
Specifying a standard structure and common vocabulary for these documents aids the creation of supporting tooling. 

### Tooling

By creating and implementing these metadata standards we facilitate the creation of tooling that can read and write this data.
Such tooling greatly expands the reach and effectiveness of rationales as it allows for rich user interfaces to be created.
i.e. translation tools, rationale comparison tools.

## Specification

We define a specification for fields which can be added to CC votes.

### Extended Body Vocabulary

The following properties extend the potential vocabulary of [CIP-100](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100)'s `body` property.

#### `summary`

- A short text field. Limited to `300` characters.
- Authors SHOULD use this field to clearly state their stance on the issue.
- Authors SHOULD use this field to succinctly describe their rationale.
- Authors SHOULD give a brief overview of the main arguments will support your position.
- This SHOULD NOT support markdown text styling.
- Compulsory.

#### `rationaleStatement`

- A long text field.
- Authors SHOULD use this field to fully describe their rationale.
- Authors SHOULD discuss their arguments in full detail.
- This field SHOULD support markdown text styling.
- Compulsory.

#### `precedentDiscussion`

- A long text field.
- The author SHOULD use this field to discuss what they feel is relevant precedent.
- This field SHOULD support markdown text styling.
- Optional.

#### `counterargumentDiscussion`

- A long text field.
- The author SHOULD use this field to discuss significant counter arguments to the position taken.
- This field SHOULD support markdown text styling.
- Optional.

#### `conclusion`

- A long text field.
- The author SHOULD use this field to conclude their rationale.
- This SHOULD NOT support markdown text styling.
- Optional.

#### `internalVote`

- A custom object field.
- This field SHOULD be used to reflect any internal voting decisions within CC member.
- This field SHOULD be used by members who are constructed from organizations or consortiums.
- Optional.

##### `constitutional`

- A positive integer.
- The author SHOULD use this field to represent a number of internal votes for the constitutionality of the action.
- Optional.

##### `unconstitutional`

- A positive integer.
- The author SHOULD use this field to represent a number of internal votes against the constitutionality of the action.
- Optional.

##### `abstain`

- A positive integer.
- The author SHOULD use this field to represent a number of internal abstain votes for the action.
- Optional.

##### `didNotVote`

- A positive integer.
- The author SHOULD use this field to represent a number of unused internal votes.
- Optional.

##### `againstVote`

- A positive integer.
- The author SHOULD use this field to represent a number of internal votes to not vote on the action.
- Optional.

### Extended `references` Vocabulary

Here we extend CIP-100's `references` field.

#### `RelevantArticles`

- We add to CIP-100's `@type`s, with a type of `RelevantArticles`.
- Authors SHOULD use this field to list the relevant constitution articles to their argument.

### Application

CC must include all compulsory fields to be considered CIP-136 compliant.
As this is an extension to CIP-100, all CIP-100 fields can be included within CIP-136 compliant metadata.

### Test Vector

See [test-vector.md](./test-vector.md) for examples.

### Versioning

This proposal should not be versioned, to update this standard a new CIP should be proposed.
Although through the JSON-LD mechanism further CIPs can add to the common governance metadata vocabulary.

## Rationale: How does this CIP achieve its goals?

By providing a peer reviewed structure for CC vote rationale, we encourage detailed voting rationales increasing the legitimacy of CC votes within the governance system.

### `summary`

We include compulsory summary with limited size to allow for the creation of tooling which layers of inspection to vote rationale.
This allows readers to get a summary of a rationale at a high level before reading all the details.

### `rationaleStatement`

This field allows for a very long-form discussion of their rationale.
This is compulsory because it forms the core of their rationale.

By setting some fields to compulsory we ensure a minimum amount of data for downstream tools to expect to render.

### `precedentDiscussion`

This is a dedicated field to be able to discuss specific precedent of votes.
By separating this from `rationaleStatement` we encourage specific discussion of precedence as well as clear separation in tooling.

### `counterargumentDiscussion`

This is a dedicated field to be able to discuss counterarguments from those proposed in the other fields.
By separating this from `rationaleStatement` we encourage specific discussion of counterarguments as well as clear separation in tooling.

### `internalVote`

This field, gives the ability for CC members who are operated by multiple individuals to share insights on specific voting choice of the individuals.
This could add additional context to the workings and opinions of the individuals who operate the CC member.

### `relevantArticles`

By providing a new type to CIP-100 `References` we encourage tooling to differentiate clearly `References` to the constitution from other types of `Reference`.

## Path to Active

### Acceptance Criteria

- [ ] This standard is supported by two separate tools, which create and submit CC votes.
- [ ] This standard is supported by two different chain indexing tools, used to read and render metadata.

### Implementation Plan

- [x] Seek feedback from individuals who are members of current Interim Constitutional Committee.
- [x] Author to provide test vectors, examples, and schema files.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
