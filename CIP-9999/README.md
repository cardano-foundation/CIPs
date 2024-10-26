---
CIP: 9999
Title: Cardano Problem Statements
Status: Active
Category: Meta
Authors:
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pulls/366
Created: 2022-10-14
License: CC-BY-4.0
---

## Abstract

A Cardano Problem Statement (CPS) is a formalized document for the Cardano ecosystem and the name of the process by which such documents are produced and listed. CPSs are meant to complement CIPs and live side-by-side in the CIP repository as first-class citizens.

> **Note** Read this CIP's number as "CIP minus 1"

## Motivation: why is this CIP necessary?

A common friction point regarding complex CIPs is how their main problems are stated. For example, the _'Motivation'_ section in CIPs is sometimes not sufficient -- or simply underused -- to describe the various aspects of a problem, its scope, and its constraints in the necessary detail. This lack of clarity leads, in the end, to poorly defined issues and unfruitful debates amongst participants who understand problems differently.

The introduction of the **Cardano Problem Statements** (CPSs) addresses this gap by defining a formal template and structure around the description of problems. CPSs are meant to replace the more elaborate motivation of complex CIPs. However, they may also exist on their own as requests for proposals from ecosystem actors who've identified a problem but are yet to find any suitable solution.

Over time, CPSs may complement grant systems that want to target well-known problems of the ecosystem; they can, for example, serve as the foundation for RFP (Request For Proposals) documents. We hope they may also help make some discussions more fluid by capturing a problem and its various constraints well.

## Specification

### CPS

#### Structure

CPSs are, first and foremost, documents that capture a problem and a set of constraints and hypotheses. Documents are [Markdown][Markdown] files with a front matter _Preamble_ and pre-defined sections. CPS authors must abide by the general structure, though they are free to organize each section as they see fit.

The structure of a CPS file is summarized in the table below:

Name               | Description
---                | ---
Preamble           | Headers containing metadata about the CPS ([see below](#header-preamble)).
Abstract           | A short (\~200 word) description of the target goals and the technical obstacles to those goals.
Problem            | A more detailed description of the problem and its context. This section should explain what motivates the writing of the CPS document.
Use cases          | A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are unsuitable.
Goals              | A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve. <br/><br/>Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns. <br/><br/>Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is.
Open Questions     | A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their _'Rationale'_ section and provide an argued answer to each.
_optional sections_| If necessary, these sections may also be included in any order:<br/>**References**<br/>**Appendices**<br/>**Acknowledgements**<br>Do not add material in an optional section if it pertains to one of the standard sections.
Copyright                                       | The CPS must be explicitly licensed under acceptable copyright terms (see [Licensing](#licensing)).

##### Header preamble

Each CIP must begin with a YAML key:value style header preamble (also known as 'front matter data'), preceded and followed by three hyphens (`---`).

Field                | Description
---                  | ---
`CPS`                | CPS number (without leading 0), or "\?" before being assigned
`Title`              | A succinct and descriptive title
`Status`             | Open \| Solved \| Inactive (..._reason_...)
`Category`           | One registered or well-known category covering one area of the ecosystem.
`Authors`            | A list of authors' real names and email addresses (e.g. John Doe <john.doe@email.domain>)
`Proposed Solutions` | A list of CIPs addressing the problem, if any
`Discussions`        | A list of links where major technical discussions regarding this CPS happened. Links should include any discussion before submission, a link to the pull request that created the CPS, and any pull request that modifies it.
`Created`            | Date created on, in ISO 8601 (YYYY-MM-DD) format
`License`            | Abbreviation of an approved license(s)

For example:

```yaml
---
CPS: 1
Title: The Blockchain Trilemma
Status: Open
Category: Consensus
Authors:
    - Alice <alice@domain.org>
    - Bob <bob@domain.org>
Proposed Solutions: []
Discussions:
    - https://forum.cardano.org/t/solving-the-blockchain-trilemma/107720
    - https://github.com/cardano-foundation/cips/pulls/9999
Created: 2009-02-14
---
```

> **Note** A reference template is available in [.github/CPS-TEMPLATE.md][CPS-TEMPLATE.md]

##### Repository Organization

A CPS must be stored in a specific folder named after its number and in a file called `README.md`. Before a number is assigned, use `????` as a placeholder name (thus naming new folders as `CPS-????`). After a number has been assigned, rename the folder.

Additional supporting files (such as diagrams, binary specifications, dialect grammars, JSON schemas etc.) may be added to the CPS's folder under freely chosen names.

For example:

```
CPS-0001
├── README.md
└── requirements.toml
```

#### Statuses

From its creation onwards, a problem statement evolves around the following statuses.

Status       | Description
---          | ---
Open         | Any problem statement that is fully formulated but for which there still exists no solution that meets its goals. Problems that are only partially solved shall remain _'Open'_ and list proposed solutions so far in their header's preamble.
Solved       | Problems for which a complete solution has been found[^1] and implemented. When solved via one or multiple CIPs, the solved status should indicate it as such: `Solved: by <CIP-XXXX>[,<CIP-YYYY>,...]`.
Inactive    | The statement is deemed obsolete or withdrawn for another reason. A short reason must be given between parentheses. For example: `Inactive (..._reason_...).

> **Note** There is no "draft" status: a proposal which has not been merged (and hence exists in a PR) is a draft CPS. Draft CPSs should include the status they aim for on acceptance, typically but not always; this will be _'Open'_.

#### Categories

As defined in [CIP-0001][].

#### Licensing

CPSs are licensed in the public domain. More so, they must be licensed under one of the following licenses. Each new CPS must identify at least one acceptable license in its preamble. In addition, each license must be referenced by its respective abbreviation below in the _"Copyright"_ section.

| Purpose             | Recommended License                                                                    |
| ---                 | ---                                                                                    |
| For software / code | Apache-2.0 - [Apache License, version 2.0][Apache-2.0]                                 |
| For documentation   | CC-BY-4.0 - [Creative Commons Attribution 4.0 International Public License][CC-BY-4.0] |

> **Warning**
>
> All licenses not explicitly included in the above lists are not acceptable terms for a Cardano Problem Statement unless a later CIP extends this one to add them.

### The CPS Process

#### 1. Early stages (same as CIP-0001)

##### 1.a. Authors open pull requests with their problem statement [(as defined in CIP-0001)](https://cips.cardano.org/cips/cip1#authors-a-open-pull-requests)

##### 1.b. Authors seek feedback [(as defined in CIP-0001)](https://cips.cardano.org/cips/cip1#authors-seek-feedback)

#### 2. Editors' role (same as CIP-0001)

##### 2.a. Triage in bi-weekly meetings [(as defined in CIP-0001)](https://cips.cardano.org/cips/cip1##triage-in-bi--weekly-meetings)

##### 2.b. Reviews [(as defined in CIP-0001)](https://cips.cardano.org/cips/cip1#reviews)

#### 3. Merging CPSs in the repository

A statement must be well-formulated (i.e. unambiguous) and demonstrate an existing problem (for which use cases exist with no suitable alternatives). When related to a current project, the problem statement must also have been acknowledged by its respective project maintainers. In some cases, problem statements may be written after the facts and be merged directly as _'Solved'_ should they document in more depth what motivated an existing solution.

Problem statements deemed unclear, for which alternatives exist with no significant drawbacks or establish unrealistic goals, shall be rejected (i.e. pull request closed without merge) with justifications or withdrawn by their authors.

Similarly, problems that appear abandoned by their authors shall also be rejected until resurrected by their authors or another community member.

##### 4. Actors of the ecosystem design and work on possible solutions

Once merged, authors, project maintainers, or any other ecosystem actors may propose solutions addressing the problem in the form of CIP. They add their CIP to the _'Proposed Solutions'_ field in the CPS' _'Preamble'_ once a solution has been fully implemented and reaches the goals fixed in the original statement.

Of course, a solution may only partially address a problem. In this case, one can alter the problem statement to incorporate the partial solutions and reflect the remaining issue(s) to solve.

### Editors

As defined in [CIP-0001][].

## Rationale: how does this CIP achieve its goals?

### Goals

Goals make it easier to assess whether a solution solves a problem. Goals also give a direction for projects to follow and can help navigate the design space. The section is purposely flexible -- which we may want to make more rigid in the future if it is proven hard for authors to articulate their intents. Ideally, goals capture high-level requirements.

### Use Cases

Use cases are essential to understanding a problem and showing that a problem addresses a need. Without use cases, there is, in fact, no problem, and merely disliking a design doesn't make it problematic. A use case is also generally user-driven, which encourages the ecosystem to open a dialogue with users to build a system that is useful to others and not only well-designed for the mere satisfaction of engineers.

### Open questions

This section is meant to _save time_, especially for problem statement authors who will likely be the ones who end up reviewing proposed solutions. Open questions allow authors to state upfront elements they have already thought of and that any solution should consider in its design. Moreso, it is an opportunity to mention, for example, security considerations or common pitfalls that solutions should avoid.

## Path to Active

### Acceptance Criteria

- [x] Review this proposal with existing actors of the ecosystem
- [x] Formulate at least one problem statement following this process
    - [CPS-0001: Metadata Discoverability & Trust](https://github.com/cardano-foundation/CIPs/pull/371)
    - [CPS-0002: Pointer Addresses](https://github.com/cardano-foundation/CIPs/pull/374)

### Implementation Plan

- [x] Confirm after repeated cycles of CPS submissions, reviews, and merges that the CPS process is both effective and accessible to the community.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[^1]: A problem may be only _partially solved_, in which case it remains in status _'Open'_. Authors are encouraged to amend the document to explain what part of the problem remains to be solved. Consequently, CPS that are _'Solved'_ are considered fully addressed.

[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[CIP-0001]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0001
[CPS-TEMPLATE.md]: https://github.com/cardano-foundation/CIPs/tree/master/.github/CPS-TEMPLATE.md
[CODE_OWNERS]: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
[CPS]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-9999
[Discussions:editors]: https://github.com/cardano-foundation/CIPs/discussions/new?category=editors
[Markdown]: https://en.wikipedia.org/wiki/Markdown
[PullRequest]: https://github.com/cardano-foundation/CIPs/pulls
[RFC 822]: https://www.ietf.org/rfc/rfc822.txt
[Repository]: https://github.com/cardano-foundation/CIPs/pulls
[CoC]: https://github.com/cardano-foundation/CIPs/tree/master/CODE_OF_CONDUCT.md
[Discord]: https://discord.gg/Jy9YM69Ezf
