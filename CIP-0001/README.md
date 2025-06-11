---
CIP: 1
Title: CIP Process
Category: Meta
Status: Active
Authors:
    - Frederic Johnson <frederic@advanceweb3.com>
    - Sebastien Guillemot <sebastien@dcspark.io>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Duncan Coutts <duncan.coutts@iohk.io>
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Robert Phair <rphair@cosd.com>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/366
    - https://github.com/cardano-foundation/CIPs/pull/331
    - https://github.com/cardano-foundation/CIPs/tree/3da306f3bfe89fa7de8fe1bf7a436682aeee25c5/CIP-0001#abstract
    - https://github.com/cardano-foundation/CIPs/pull/924
Created: 2020-03-21
License: CC-BY-4.0
---

## Abstract

A Cardano Improvement Proposal (CIP) is a formalised design document for the Cardano community and the name of the process by which such documents are produced and listed. A CIP provides information or describes a change to the Cardano ecosystem, processes, or environment concisely and in sufficient technical detail. In this CIP, we explain what a CIP is, how the CIP process functions, the role of the CIP Editors, and how users should go about proposing, discussing, and structuring a CIP.

The Cardano Foundation intends CIPs to be the primary mechanisms for proposing new features, collecting community input on an issue, and documenting design decisions that have gone into Cardano. Plus, because CIPs are text files in a versioned repository, their revision history is the historical record of significant changes affecting Cardano.

## Motivation: why is this CIP necessary?

CIPs aim to address two challenges mainly:
1. The need for various parties to agree on a common approach to ease the interoperability of tools or interfaces.
2. The need to propose and discuss changes to the protocol or established practice of the ecosystem.

The CIP process does not _by itself_ offer any form of governance. For example, it does not govern the process by which proposed changes to the Cardano protocol are implemented and deployed. Yet, it is a crucial, community-driven component of the governance decision pipeline as it helps to collect thoughts and proposals in an organised fashion. Additionally, specific projects may choose to actively engage with the CIP process for some or all changes to their project.

This document outlines the technical structure of the CIP and the technical requirements of the submission and review process.  The history, social features and human elements of the CIP process are described the [CIP repository Wiki][Wiki].

## Specification

### Table of Contents

- [Document](#document)
  - [Structure](#structure)
    - [Header Preamble](#header-preamble)
    - [Translations](#translations)
    - [Repository Organization](#repository-organization)
    - [Versioning](#versioning)
    - [Licensing](#licensing)
  - [Statuses](#statuses)
    - [Status: Proposed](#status-proposed)
    - [Status: Active](#status-active)
    - [Status: Inactive](#status-inactive)
  - [Path to Active](#path-to-active)
  - [Categories](#categories)
  - [Project Enlisting](#project-enlisting)
- [Process](#process)
  - [1. Early Stage](#1-early-stages)
    - [1.a. Authors open a pull request](#1a-authors-open-a-pull-request)
      - [Naming CIPs with similar subjects](#naming-cips-with-similar-subjects)
    - [1.b. Authors seek feedback](#1b-authors-seek-feedback)
  - [2. Editors' role](#2-editors-role)
    - [2.a. Triage in bi-weekly meetings](#2a-triage-in-bi-weekly-meetings)
    - [2.b. Reviews](#2b-reviews)
  - [3. Merging CIPs in the repository](#3-merging-cips-in-the-repository)
  - [4. Implementors work towards Active status following their 'Implementation Plan'](#4-implementors-work-towards-active-status-following-their-implementation-plan)
- [Editors](#editors)
  - [Missions](#missions)
  - [Reviews](#reviews)
  - [Nomination](#nomination)

### Document

#### Structure

A CIP is, first and foremost, a document which proposes a solution to a well-defined problem. Documents are [Markdown][] files with a _Preamble_ and a set of pre-defined sections. CIPs authors must abide by the general structure, though they are free to organise each section as they see fit.

The structure of a CIP file is summarised in the table below:

Name                                            | Description
---                                             | ---
Preamble                                        | Headers containing metadata about the CIP ([see below](#header-preamble)).
Abstract                                        | A short (\~200 word) description of the proposed solution and the technical issue being addressed.
Motivation: why is this CIP necessary?          | A clear explanation that introduces a proposal's purpose, use cases, and stakeholders. If the CIP changes an established design, it must outline design issues that motivate a rework. For complex proposals, authors must write a [Cardano Problem Statement (CPS) as defined in CIP-9999][CPS] and link to it as the `Motivation`.
Specification                                   | The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely based on the design outlined in the CIP. A complete and unambiguous design is necessary to facilitate multiple interoperable implementations. <br/><br/>This section must address the [Versioning](#versioning) requirement unless this is addressed in an optional Versioning section.<br/><br/> If a proposal defines structure of on-chain data it must include a CDDL schema.
Rationale: how does this CIP achieve its goals? | The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion. <br/><br/>It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a [CPS][], the 'Rationale' section should explain how it addresses the CPS and answer any questions that the CPS poses for potential solutions.
Path to Active                                  | Organised in two sub-sections (see [Path to Active](#path-to-active) for detail):<br/><h5>Acceptance Criteria</h5>Describes what are the acceptance criteria whereby a proposal becomes _'Active'_.<br/><h5>Implementation Plan</h5>Either a plan to meet those criteria or `N/A` if not applicable.
_optional sections_                             | May appear in any order, or with custom titles, at author and editor discretion:<br/>**Versioning**: if [Versioning](#versioning) is not addressed in Specification<br/>**References**<br/>**Appendices**<br/>**Acknowledgements**
Copyright                                       | The CIP must be explicitly licensed under acceptable copyright terms ([see below](#licensing)).

> [!NOTE]
> Each of these section titles (*Abstract* onward) should be an H2 heading (beginning with markdown `##`).  Subsections like _Versioning_ or _Acceptance Criteria_ should be H3 headings (e.g. `### Versioning`).  Don't include a H1 title heading (markdown `#`): for web friendly contexts, this will be generated from the Preamble.

##### Header Preamble

Each CIP must begin with a YAML key:value style header preamble (also known as _front matter data_), preceded and followed by three hyphens (`---`).

Field          | Description
---            | ---
`CIP`          | The CIP number (without leading 0), or "\?" before being assigned
`Title`        | A succinct and descriptive title.  If necessary, use a `-` delimiter to begin with an applicable classification (see [Naming CIPs with similar subjects](#naming-cips-with-similar-subjects)).  Don't use backticks (<code>`</code>) in titles since they disrupt formatting in other contexts.
`Category`     | One of the editorially accepted [categories](#categories) covering one area of the ecosystem.
`Status`       | Proposed \| Active \| Inactive (.._reason_..)
`Authors`      | A list of authors' real names and email addresses (e.g. John Doe <john.doe@email.domain>)
`Implementors` | A list of implementors committed to delivering an implementation of the proposal, when applicable. `N/A` when not applicable and `[]` when there's currently no implementor.
`Discussions`  | A list of links where major technical discussions regarding this CIP happened. Links should include any discussion before submission, and _must_ include a link to the pull request that created the CIP and any pull request that modifies it.
`Solution-To`  | A list of [CPS][] that this CIP addresses, if any. Omitted when not applicable.
`Created`      | Date created on, in ISO 8601 (YYYY-MM-DD) format
`License`      | Abbreviation of an approved license(s)

For example:

```yaml
---
CIP: 1
Title: CIP Process
Category: Meta
Status: Active
Authors:
    - Frederic Johnson <frederic.johnson@cardanofoundation.org>
    - Sebastien Guillemot <sebastien@dcspark.io>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Duncan Coutts <duncan.coutts@iohk.io>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/366
Created: 2020-03-21
License: CC-BY-4.0
---
```

Especially because Markdown link syntax is not supported in the header preamble, labels can be added to clarify list items; e.g.:
```yaml
Discussions:
    - Original-PR: https://github.com/cardano-foundation/CIPs/pull/366
```

> [!TIP]
> A reference template is available in [.github/CIP-TEMPLATE.md][CIP-TEMPLATE.md]

##### Repository Organization

A CIP must be stored in a specific folder named after its number (4-digit, left-padded with `0`) and in a file called `README.md`. Before a number is assigned, a placeholder folder name should be used (e.g. `CIP-my-new-feature`). After a number has been assigned, rename the folder.

Additional supporting files (such as diagrams, binary specifications, dialect grammars, JSON schemas etc.) may be added to the CIP's folder under freely chosen names.

For example:

```
CIP-0010
├── README.md
├── registry.json
└── registry.schema.json

```

##### Translations

While CIPs are mainly technical documents meant to be read primarily by developers -- and thus often written in English; some may be translated into various languages to increase their outreach. Any file in a CIP folder may also include translated content satisfying the following rules:

- Any translated file shall share a common basename with its original source.

- Translation file basenames must have a suffix using an [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code, separated by a dot `.` character. (e.g. `README.fr.md`).

- When no language code is provided as suffix, the default language for the document is assumed to be English (UK/US).

- Translated CIPs (i.e. `README` files), must not include the original preamble. They must, however, include the following preamble as yaml frontmatter data:

Field          | Description
---            | ---
`CIP`          | The CIP number (without leading 0)
`Source`       | The canonical GitHub link to the original CIP document
`Title`        | A translation of the CIP's title
`Revision`     | Whenever possible, the commit hash (7 first hex-digits, e.g. `12ab34c`) of the source in the main repository. If the source was not committed to the main repo, use the best known translation date in ISO format (if unknown, use the date posted in the translation's PR branch).
`Translators`  | A list of translators names and email addresses (e.g. `John Doe <john.doe@email.domain>`)
`Language`     | An [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) code of the target language (e.g. `fr`)

- Translated CIPs inherit the same licensing terms as their original sources.

##### Versioning

CIPs must indicate how the defined Specification is versioned.  **Note** this does not apply to the CIP text, for which annotated change logs are automatically generated and [available through the GitHub UI](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/viewing-and-comparing-commits/differences-between-commit-views) as a history of CIP files and directories.

Authors are free to describe any approach to versioning that allows versioned alterations to be added without author oversight.  Stipulating that the proposal must be superseded by another is also considered to be valid versioning.

A single Versioning scheme can be placed either as a subsection of the Specification section or in an optional Versioning top-level section near the end.  If the Specification contains multiple specification subsections, each of these can have a Versioning subsection within it.

##### Licensing

CIPs are licensed in the public domain. More so, they must be licensed under one of the following licenses. Each new CIP must identify at least one acceptable license in its preamble. In addition, each license must be referenced by its respective abbreviation below in the _"Copyright"_ section.

| Purpose             | Recommended License                                                                    |
| ---                 | ---                                                                                    |
| For software / code | Apache-2.0 - [Apache License, version 2.0][Apache-2.0]                                 |
| For documentation   | CC-BY-4.0 - [Creative Commons Attribution 4.0 International Public License][CC-BY-4.0] |

> **Warning**
>
> All licenses not explicitly included in the above lists are not acceptable terms for a Cardano Improvement Proposal unless a later CIP extends this one to add them.

#### Statuses

CIPs can have three statuses: `Proposed`, `Active` or `Inactive`. [The CIP Process section](#process) highlights how CIPs move through these statuses; no CIP should be given one of these statuses without satisfying the criteria described here below.

> **Note** There is no "draft" status: a proposal which has not been merged (and hence exists in a PR) is a draft CIP. Draft CIPs should include the status they are aiming for on acceptance. Typically, but not always, this will be _'Proposed'_.

##### Status: Proposed

A _'Proposed'_ CIP is any CIP that meets the essential CIP criteria but is not yet _'Active'_. The criteria that must meet a CIP to be merged as _'Proposed'_ are:

- It must contain all the sections described in [Structure](#structure).
- The quality of the content must be to the Editors’ satisfaction. That means it must be grammatically sound, well-articulated and demonstrates noticeable efforts in terms of completeness and level of detail.
- Its technical soundness should have been established. Where necessary, this may require review by particular experts and addressing their concerns. Note that the requirement is that the proposal makes sense (i.e. be technically sound), yet no consulted experts need to think it is a good idea.
- It must have a valid [Path to Active](#path-to-active) as defined below.

##### Status: Active

An _'Active'_ CIP has taken effect according to the criteria defined in its _'Path to Active'_ section. Said differently, each CIP defines by which criteria it can become _'Active'_ and those criteria are included in the review process. Exact criteria thereby depends on the nature of the CIP, typically:

- For CIPs that relate to particular projects or pieces of technology, it becomes _'Active'_ by being implemented and released;
- For changes to the Cardano protocol, a CIP becomes _'Active'_ by being live on the Cardano mainnet;
- For ecosystem standards, it means gaining sufficient and visible adoption in the community.
- It must have a valid [Path to Active](#path-to-active) as defined below: even the CIP is already acknowledged as `Active` or being documented retroactively (after acceptance and implementation).

A proposal that is _'Active'_ is considered complete and is synonymous with "production readiness" when it comes to the maturity of a solution. _'Active'_ CIPs will not be updated substantially (apart from minor edits, proofreading and added precisions). They can, nevertheless, be challenged through new proposals if need be.

##### Status: Inactive

An _'Inactive'_ CIP describes any proposal that does not fit into the other types. A CIP can therefore be _'Inactive'_ for various reasons (e.g. obsolete, superseded, abandoned). Hence the status must indicate a justification between parentheses; for example:

```
Status: Inactive (superseded by CIP-0001)
```

#### Path to Active

This must be subdivided into two sub-sections:

  - _'Acceptance Criteria'_

    This sub-section must define a list of criteria by which the proposal can become active. Criteria must relate to observable metrics or deliverables and be reviewed by editors and project maintainers when applicable. For example: "The changes to the ledger rules are implemented and deployed on Cardano mainnet by a majority of the network", or "The following key projects have implemented support for this standard".

  - _'Implementation Plan'_

    This sub-section should define the plan by which a proposal will meet its acceptance criteria, when applicable. More, proposals that require implementation work in a specific project may indicate one or more implementors. Implementors must sign off on the plan and be referenced in the document's preamble.

    In particular, an implementation that requires a hard-fork should explicitly mention it in its _'Implementation Plan'_.

> **Note** the statuses of `Proposed` and `Active` _both_ require a _Path to Active_ section, making this a _required_ section for all viable proposals.  Even if a CIP is edited or submitted with an `Inactive` status, it may still be helpful to have a `Path to Active` if there are conditions that might lead to its acceptance or implementation.

#### Categories

CIPs are classified into distinct categories that help organise (and thus, find) them. Categories are meant to be flexible and evolve as new domains emerge. Authors may leave the category as `?` should they not be sure under which category their proposal falls; editors will eventually assign one or reject the proposal altogether should it relate to an area where the CIP process does not apply.

Submissions can be made to these categories whenever relevant, without following any particular submission guidelines:

Category | Description
---      | ---
Meta     | Designates meta-CIPs, such as this one, which typically serve another category or group of categories
Wallets  | For standardisation across wallets (hardware, full-node or light)
Tokens   | About tokens (fungible or non-fungible) and minting policies in general
Metadata | For proposals around metadata (on-chain or off-chain)
Tools    | A broad category for ecosystem features not falling into any other category

Additionally, representatives of ecosystem categories may explicitly _enlist_ their categories (see next section) to suggest a closer relationship with the CIP process. The following categories are confirmed as enlisted according to CIPs which define that relationship:

Category | Description
---      | ---
Plutus   | Changes or additions to Plutus, following the process described in [CIP-0035][]
Ledger   | For proposals regarding the Cardano ledger, following the process described in [CIP-0084][]

These tentatively enlisted categories await CIPs to describe any enlistment relationship:

Category  | Description
---       | ---
Catalyst  | For proposals affecting Project Catalyst or the Jörmungandr project
Consensus | For proposals affecting implementations of the Cardano Consensus layer and algorithms
Network   | Specifications and implementations of Cardano's network protocols and applications

#### Project Enlisting

Project representatives intending to follow an "enlisted" category above agree to coordinate with related development by sharing efforts to review and validate new proposals.
It should be noted that single organisations can no longer represent any ecosystem or development category, which makes these enlistment guidelines both decentralised and cooperative, including whenever possible:

- allocating time to **review** proposals from actors of the community when solicited by editors (i.e. after one first round of reviews);
- defining additional rules and processes whereby external actors can engage with their project as part of the CIP process;
- defining boundaries within their project for which the CIP process does apply;
- establishing points of contact and any designated reviews for a category;
- agreeing upon how proposals move from the state of idea (i.e. CIP) to actual implementation work;
- writing CIPs for significant changes introduced in their projects when it applies.

Any guidelines for this cooperation should be described by a dedicated CIP whenever possible.  When such a CIP is posted or supersedes another one, it will be entered into the above table in the Categories section.  Participants of enlisted categories should follow the requirements outlined in that CIP and should update such proposals whenever these requirements or relationships change.

> **Warning** A positive review by any enlisted project representative does not constitute a commitment to implement the CIP. It is still the CIP author's responsibility to create an implementation plan and identify implementors.

Editors occasionally invite representatives from enlisted categories to speak during review meetings and solicit them for ultimate approvals of proposals in their area of expertise.

**Note** Optionally, projects may show their enlisting using the following badge on their introductory README: ![https://github.com/cardano-foundation/CIPs](https://raw.githubusercontent.com/cardano-foundation/CIPs/master/.github/badge.svg)
>
> ```md
> ![https://github.com/cardano-foundation/CIPs](https://raw.githubusercontent.com/cardano-foundation/CIPs/master/.github/badge.svg)
> ```

### Process

#### 1. Early stages

##### 1.a. Authors open a pull request

Proposals must be submitted to the [cardano-foundation/CIPs][Repository] repository as a pull request named after the proposal's title. The pull request title **should not** include a CIP number (and use `?` instead as number); the editors will assign one. Discussions may precede a proposal: early reviews and discussions streamline the process down the line.

PRs should not contain commits that also appear in other repository PR's: usually the consequence of re-using a branch in your fork or submitting your work from your fork's `master` branch.  To avoid this, please:
- Don't submit your PR from your fork's `master` branch.
- Create a new branch for every pull request that you intend to submit.

> [!TIP]
> The CIP title in the pull request should be kept consistent with the CIP header `Title:`.

> [!IMPORTANT]
> Pull requests should not include implementation code: any code bases should instead be provided as links to a code repository.

> [!NOTE]
> Proposals addressing a specific CPS should also be listed in the corresponding CPS header, in _'Proposed Solutions'_, to keep track of ongoing work.

###### Naming CIPs with similar subjects

When a CIP title *and* subject matter share a common element, begin the CIP title with that common element and end it with the specific portion, delimited with the `-` character.  Example (CIP-0095):

> *Web-Wallet Bridge **-** Governance*

CIP editors will help determine these common elements and, whenever necessary, rename both CIP document titles and PR titles accordingly.  The objective is to provide commonly recognisable names for similar developments (e.g. multiple extensions to another CIP or scheme).

###### Link to proposal from PR first comment

In the original comment for your pull request, please include a link to the directory or the `README.md` for the CIP in your working branch, so readers and reviewers can easily follow your work.  This makes it easier for editors and the community to read and review your proposal.

> [!NOTE]
> If this link changes (e.g. from the CIP directory being renamed), please keep this link updated.

###### Follow a reviewer- and editor-friendly review process

As review progresses:
- When editors and reviewers submit changes that you accept, commit them from the GitHub UI so these review points are resolved.
- Even if resolving these in your own environemnt, mark any review points Resolved as they are resolved: otherwise your PR will appear stalled and merging will likely be delayed.
- **Don't "force push"**: which overwrites commit histories and disrupts change visibility during the review process.  Instead, `git merge` the PR branch back into your local environment: which will preserve any collaborative editing history.


##### 1.b. Authors seek feedback

Authors shall champion their proposals. The CIP process is a collaborative effort, which implies discussions between different groups of individuals. While editors may provide specific inputs and help reach out to experts, authors shall actively seek feedback from the community to help move their proposal forward.

Discussions and comments shall mainly happen on Github in pull requests. When discussed on other mediums, we expect authors or participants to report back a summary of their discussions to the original pull request to keep track of the most critical conversations in a written form and all in one place.

As much as possible, commenters/reviewers shall remain unbiased in their judgement and assess proposals in good faith. Authors have the right to reject comments or feedback but **are strongly encouraged to address concerns in their 'Rationale' section**. Ultimately, CIP editors shall make the last call concerning the various statements made on a proposal and their treatment by the author(s).

By opening pull requests or posting comments, commenters and authors agree to our [Code of Conduct][CoC]. Any comment infringing this code of conduct shall be removed or altered without prior notice.

> [!NOTE]
> For acceptability guidelines, including a concise review checklist, see 
[CIP Wiki > CIPs for Reviewers & Authors](https://github.com/cardano-foundation/CIPs/wiki/2.-CIPs-for-Reviewers-&-Authors).

#### 2. Editors' role

##### 2.a. Triage in bi-weekly meetings

CIP editors meet regularly in [a public Discord server][Discord] to go through newly proposed ideas in a triage phase. As a result of a triage, editors acknowledge new CIPs, and briefly review their preamble. Editors also assign numbers to newly proposed CIPs during this phase. Incidentally, the triage allows new CIPs to get visibility for potential reviews.

##### 2.b. Reviews

In every meeting, editors will also review in more depth some chosen CIPs (based on their readiness and the stability of the discussions) and assess if they meet the criteria to be merged in their aimed status.

During review sessions, editors will regularly invite project maintainers or actors from the ecosystem who are deemed relevant to the meeting's agenda. However, meetings are open and held in public to encourage anyone interested in participating.

A dedicated Discord channel may also be created for some long-running discussions to support quick chats and progress on particular topics (while still being regularly summarised on the repository).

#### 3. Merging CIPs in the repository

Once a proposal has reached all requirements for its target status (as explained in [Statuses](#statuses)) and has been sufficiently and faithfully discussed by community members, it is merged with its target status.

> [!WARNING]
> Ideas deemed unsound shall be rejected with justifications or withdrawn by the authors. Similarly, proposals that appear abandoned by their authors shall be rejected until resurrected by their authors or another community member.

CIPs are generally merged with the status _'Proposed'_ until they meet their _'Path to Active'_ requirements. In some rare cases (mainly when written after the facts and resulting in a broad consensus), proposals may be merged as _'Active'_ immediately.

Each proposal is unique and has a bespoke _'Path to Active'_, which must be reviewed case-by-case. There must be sufficient time between the first appearance of a proposal and its merge into the repository to ensure enough opportunity for community members to review it.

#### 4. Implementors work towards Active status following their 'Implementation Plan'

Once merged, implementors shall execute the CIP's _'Implementation Plan'_, if any. If a proposal has no implementors or no _'Implementation Plan'_, it may simply remain as _'Proposed'_ in the repository.

> [!WARNING]
> It is perfectly fine to submit ideas in the repository with no concrete implementation plan, yet they should be treated as such: ideas.

Besides, once all of the _'Path to Active'_ requirements have been met, authors shall make another pull request to change their CIP's status to _'Active'_. Editors may also do this on occasion.

### Editors

For a full, current description of Editor workflow, see [CIP Wiki > CIPs for Editors](https://github.com/cardano-foundation/CIPs/wiki/3.-CIPs-for-Editors).

#### Missions

CIP Editors safeguard the CIP process: they form a group enforcing the process described in this document and facilitating conversations between community actors. CIP editors should strive to keep up to date with general technical discussions and Cardano proposals. For each new draft proposal submitted on [cardano-foundation/CIPs][PullRequest] an editor might review it as follows:

- Read the proposal to check if it is ready, sound, and complete.
- Check if it has been [properly formatted](#structure).
- Check if sufficient time has been allowed for proper discussion amongst the community.
- Ensure the motivation behind the CIP is valid and that design choices have relevant justifications or rationale.
- Confirm licensing terms are acceptable.
- Assign a CIP number
- Assign a given category to help with searching
- Request wording/grammar adjustments

CIPs that do not meet a sufficient level of quality or don't abide by the process described in this document will be rejected until their authors address review comments.

#### Reviews

Note that editors **may** provide technical feedback on proposals in some cases, although they aren't expected to be the sole technical reviewers of proposals. CIPs are, before anything, a community-driven effort. While editors are here to facilitate the discussion and mediate debates, they aren't necessarily technical experts on all subjects covered by CIPs.

Therefore, CIPs authors are encouraged to reach out to known experts to demonstrate their good faith and openness when they champion a proposal. Editors may help with such efforts but cannot be expected to do this alone.

#### Nomination

Existing editors or the community may nominate new editors, provided they have proven to be already existing and active contributors to the CIP process and are ready to commit some of their time to the CIP process regularly.

The missions of an editor include, but aren't exclusively limited to, any of the tasks listed above. Active members that seek to become listed editors may also come forth and let it be known. Any application will take the form of a pull request updating this document with a justification as the pull request's description.

Current editors are listed here below:

| Robert Phair <br/> [@rphair][] | Ryan Williams <br/> [@Ryun1][] | Adam Dean <br/> [@Crypto2099][] | Thomas Vellekoop <br/> [@perturbing][] |
| ---                            | ---                            | ---                             | ---                                    |

[@rphair]: https://github.com/rphair
[@Ryun1]: https://github.com/Ryun1
[@Crypto2099]: https://github.com/Crypto2099
[@perturbing]: https://github.com/perturbing

Emeritus editors:
- Frederic Johnson - [@crptmppt](https://github.com/crptmppt)
- Sebastien Guillemot - [@SebastienGllmt](https://github.com/SebastienGllmt)
- Matthias Benkort - [@KtorZ](https://github.com/KtorZ)
- Duncan Coutts - [@dcoutts](https://github.com/dcoutts)

## Rationale: how does this CIP achieve its goals?

### Key changes from CIP-0001 (version 1)

#### Introduction of Cardano Problem Statements

A significant friction point regarding complex CIPs is often how the main problem is stated. The _'Motivation'_ is often insufficient (or simply underused) to describe various aspects of a problem, its scope, and its constraints. This lack of clarity leads, in the end, to poorly defined issues and debates over solutions that feel unclear amongst different participants.

The introduction of [CIP-9999: Cardano Problem Statements][CIP-9999] addresses this gap by introducing a formal template and structure around problem statements. However, requiring any CIP to be preceded by a CPS would likely be overkill and become an obstacle to the overall adoption of the CIP process for more straightforward problems. At this stage, it is reasonable to think either (a) that CIP authors would foresee the complexity and state their problem as a CPS beforehand or (b) that editors or reviewers will require authors to write a CPS to clarify a perhaps ambiguous motivation on complex CIPs.

We also anticipate project maintainers or community actors will write standalone CPS to document well-known issues for which the design space is still to be explored.

#### Explicit enlisting

A recurring pain point with the previous CIP process was the lack of clear ownership/accountability of some proposals affecting remote parts of the ecosystem. On several occasions, proposals from community members have concerned, for example, core components of the Cardano architecture. However, those proposals have been hard to move forward with and to either reject or turn into concrete action steps. Authors usually do not have the technical proficiency required to implement them and rely on the core engineering team in charge of projects to do so. Thus, explicit compliance and collaboration of those engineering teams are necessary to propose changes affecting their work.

By asking teams to explicitly state their compliance with the CIP process with clear, accountable owners (as individuals), it becomes plausible to now establish a dialogue between community members and technical leadership responsible for specific ecosystem projects. Furthermore, projects that, on the contrary, do not seek to participate in CIP or receive contributions in the form of CIP/CPS are automatically taken out of this process, saving time and energy for both reviewers and authors.

#### Nomination of new editors

The _'Editors'_ section now details how to become a CIP editor. The process aims to be simple and define those involved the most with editorship tasks as editors. Thus, being an active contributor to the CIP process as a prerequisite only makes sense. We want to leave the room open for either existing editors to refer an existing community as an editor or for community members to formulate that request explicitly.

There are no delays or number of contributions necessary to pretend to become an editor. Those criteria are often less relevant than others and more subjective, such as the quality of one's participation or their relevance. Since editors also need to work with one another in the end, it seems logical that existing editors have their final say about whom they intend to work with.

#### Removal of `type` in the preamble

The `type` field in the header has shown to be:

- confusing (often authors are getting it wrong);
- not-too-useful (as a `type` tells you very little about the nature of the CIP).

An ad-hoc classification by non-rigid categories, which may evolve over time to reflect ecosystem areas, seems better suited. Therefore, we do not require authors to categorise their CIPs; instead, categories will be added and maintained by editors as a side task atop the CIP process.

#### Simplification of the statuses

Over time we've learnt that the valuable information a status should convey is really about the readiness of a CIP, especially regarding standards. For a long time, many CIPs have lived as `Draft` despite some being used in dozens of systems. Consequently, the `status` has lost a bit of its meaning. The frontier between `Draft` and `Proposed` hasn't always been clear, and it has proven challenging to come up with good statuses to describe all possible rejections. So instead, the current division of statuses is as simple-as-it-can-be and remains flexible regarding rejections.

### Choice of CoC

The choice of a code of conduct follows other popular open source initiatives. It serves as a good, unilaterally accepted foundation which can be later revisited if necessary.

## Path to Active

### Acceptance criteria

- [x] The proposal has been reviewed by the community and sufficiently advertised on various channels.
    - [x] Cardano Forum
    - [x] IOG Technical Community Discord
    - [x] Twitter
    - [x] Reddit
    - [x] Cardano Summit 2022
    - [x] IO ScotFest 2022

- [x] All major concerns or feedback have been addressed. The document is as unambiguous as it can be and it outlines a process that a supermajority of reviewers is happy to follow.

### Implementation Plan

- [x] Rework existing draft CIPs to adopt this new format and process. In particular, CIPs affecting enlisted projects should be brought to the attention of the respective project maintainers.
- [x] Edit / align old CIPs preambles and sections to at least reflect also this new format.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[CIP-0035]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0035
[CIP-0084]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084
[CIP-9999]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-9999
[CIP-TEMPLATE.md]: https://github.com/cardano-foundation/CIPs/tree/master/.github/CIP-TEMPLATE.md
[CODE_OWNERS]: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
[CPS]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-9999
[Discussions:editors]: https://github.com/cardano-foundation/CIPs/discussions/new?category=editors
[Markdown]: https://en.wikipedia.org/wiki/Markdown
[PullRequest]: https://github.com/cardano-foundation/CIPs/pulls
[RFC 822]: https://www.ietf.org/rfc/rfc822.txt
[Repository]: https://github.com/cardano-foundation/CIPs/pulls
[CoC]: https://github.com/cardano-foundation/CIPs/tree/master/CODE_OF_CONDUCT.md
[Discord]: https://discord.gg/J8sGdCuKhs
[Wiki]: https://github.com/cardano-foundation/CIPs/wiki
