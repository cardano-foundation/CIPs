---
CIP: 1
Title: CIP process
Authors: Frederic Johnson <frederic.johnson@cardanofoundation.org>, Sebastien Guillemot <sebastien@dcspark.io>, Matthias Benkort <matthias.benkort@cardanofoundation.org>, Duncan Coutts <duncan.coutts@iohk.io>
Status: Active
Type: Process
Created: 2020-03-21
License: CC-BY-4.0
---

## Abstract

A Cardano Improvement Proposal (CIP) is a formalized design document for the Cardano community. It provides information or describes a new feature for the Cardano network, its processes, or environment concisely and technically sufficiently. In this CIP, we tell what a CIP is, how the CIP process functions, and how users should go about proposing, discussing and structuring a CIP.

The Cardano Foundation intends CIPs to be the primary mechanisms for proposing new features, collecting community input on an issue, and documenting design decisions that have gone into Cardano. Plus, because CIPs are text files in a versioned repository, their revision history is the historical record of the feature proposal.

## Motivation

CIPs come to address mainly two challenges:

1. The need for various parties to agree on a common approach to ease the interoperability of tools or interfaces.

2. The need to propose and discuss changes to the protocol or established practice of the ecosystem.

The CIP process does not _by itself_ offer any form of governance. Yet, it is a crucial, community-driven component of the governance decision pipeline as it helps to collect thoughts and proposals in an organized fashion.

## Specification

### Types

Type          | Description
---           | ---
Core          | A core CIP describes a change affecting the Cardano blockchain's core components. For instance, a change in the ledger rules, a modification of the on-the-wire binary format or adjustments to the rewards and incentives strategy.
Process       | A process defines a common standard to follow to achieve a certain degree of interoperability between various actors. It can be a formal document describing a specific procedure or a set of recommendations/guidelines on one particular topic.
Informational | An informational CIP documents a particular design decision. These are often written a posteriori to address a gap in understanding and knowledge sharing.

### Structure

Each CIP must have the following parts:

Name           | Description
---            | ---
Preamble       | Headers containing metadata about the CIP ([see below](#header-preamble)).
Abstract       | A short (\~200 word) description of the technical issue.
Motivation     | A clear and short explanation that introduces the reason behind a proposal. Changing an established design, must outline design issues that motivate a rework.
Specification  | The technical specification should describe the syntax and semantics of any new feature. The specification should be detailed enough to allow competing, interoperable implementations.
Rationale      | The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during the discussion. It must also explain how the proposal affects the backward compatibility of existing solutions when applicable.
Path to Active | A reference implementation, observable metrics or anything showing the acceptance of the proposal in the community. Any CIP must have an approved 'Path to Active' before it can move to 'Active'. It acts as a high-level roadmap for the proposal.
Copyright      | The CIP must be explicitly licensed under acceptable copyright terms ([see below](#licensing)).

<details>
  <summary><span id="header-preamble"><strong>Header preamble</strong></span></summary>

Each CIP must begin with an [RFC 822](https://www.ietf.org/rfc/rfc822.txt) key:value style header preamble (also known as 'front matter data'), preceded and followed by three hyphens (`---`).

Field     | Description
---       | ---
`CIP`     | CIP number (without leading 0), or "\?" before being assigned
`Title`   | A succinct and descriptive title
`Authors` | Comma-separated list of authors' real names and email addresses (e.g. John Doe <john.doe@email.domain>).
`Status`  | Draft \| Proposed \| Active \| Obsolete
`Type`    | Core \| Process \| Informational
`Created` | date created on, in ISO 8601 (YYYY-MM-DD) format
`License` | abbreviation of an approved license(s)

For example:

```yaml
---
CIP: 1
Title: CIP process
Authors: Frederic Johnson <frederic.johnson@cardanofoundation.org>, Sebastien Guillemot <sebastien@dcspark.io>, Matthias Benkort <matthias.benkort@cardanofoundation.org>, Duncan Coutts <duncan.coutts@iohk.io>
Status: Active
Type: Process
Created: 2020-03-21
License: CC-BY-4.0
---
```

</details>

<details>
  <summary><span id="licensing"><strong>Licensing</strong></span></summary>

The following licenses are accepted. Each new CIP must identify at least one acceptable license in its preamble. In addition, each license must be referenced by its respective abbreviation below.

#### Recommended licenses

- for software / code: Apache-2.0: [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
- for documentation: CC-BY-4.0: [Creative Commons Attribution 4.0 International Public License](https://creativecommons.org/licenses/by/4.0/legalcode)

#### Unacceptable licenses

All licenses not explicitly included in the above lists are not acceptable terms for a Cardano Improvement Proposal unless a later CIP extends this one to add them.

</details>

<p align="right">
  A reference template is available in <a href="https://github.com/cardano-foundation/CIPs/tree/master/.github/CIP-TEMPLATE.md">.github/CIP-TEMPLATE.md</a>.
</p>

### Statuses

From its creation and onwards, a proposal evolves around the following statuses.

Status   | Description
---      | ---
Draft    | An implicit status given to newly proposed CIPs that haven't yet been validated or reviewed. Historically, some CIPs have been merged as 'Draft'.
Proposed | Any proposal which is not yet active but that has been reviewed, accepted and is now working towards acceptance. A 'Proposed' CIP must have a clear path to 'Active' defined and approved which defines the criteria it must meet in order to become 'Active'.
Active   | The proposal has completed all steps needed for its activation. Said differently, it means observable metrics showing its adoption in the ecosystem.
Obsolete | A retired CIP or one made obsolete by a newer CIP.
Rejected | A proposal rejected for various reasons, but kept nonetheless for the record. It may also indicate ideas that were considered but deemed invalid, as a way to inform future authors.

### Repository organization

CIP editors should strive to keep up to date with general technical conversations and Cardano proposals. For each new draft proposal submitted on [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs/pulls) an editor might review it as follows:

- Read the proposal to check if it is ready, sound, and complete.
- Check if it has been [properly formatted](#structure).
- Check if sufficient time has been allowed for proper discussion amongst the community.
- Ensure the motivation behind the CIP is valid and that design choices have relevant justifications or rationale.
- Confirm licensing terms are acceptable.
- Assign a CIP number
- Suggest a different type for a CIP
- Request wording/grammar adjustments

CIPs that do not meet a sufficient level of quality or don't abide by the process described in this document will be rejected until their authors address review comments.

Note that editors may provide technical feedback on proposals in some cases, although they aren't expected to be the sole technical reviewers of proposals. CIPs are, before anything, a community-driven effort. While editors are here to facilitate the discussion and mediate debates, they aren't necessarily technical experts on all subjects covered by CIPs. Therefore, the editors' duty also comprises finding relevant technical experts to review proposals. CIPs authors are also encouraged to reach out to known experts to demonstrate their good faith and openness when they champion a proposal.

Current editors are listed here below:

| Frederic Johnson <br/> [@crptmppt][] | Matthias Benkort <br/> [@KtorZ][] | Sebastien Guillemot <br/> [@SebastienGllmt][] | Robert Phair <br/> [@rphair][] |
| ---                                  | ---                               | ---                                           | ---                            |

[@crptmppt]: https://github.com/crptmppt
[@KtorZ]: https://github.com/KtorZ
[@SebastienGllmt]: https://github.com/SebastienGllmt
[@rphair]: https://github.com/rphair

### Progression

##### 1. Authors open pull requests with their proposal

Proposals must be submitted to the [cardano-foundation/CIPs](https://github.com/cardano-foundation/CIPs/pulls) repository as a pull request named after the proposal's title. Ideally, the community should have already discussed a proposal before its submission. Early reviews streamline the process down the line -- although it isn't a strict requirement.

##### 2. Editors triage proposals bi-weekly, community technical reviews ensue.

CIP editors meet regularly (on a 2-week cadence) in [a public Discord server](https://discord.gg/Jy9YM69Ezf) to go through newly proposed ideas in a "triage" phase. As a result of a triage, editors acknowledge new CIPs, and briefly review their preamble. It is recommended not yet to assign a number and pick `?` when first opening a proposal. Instead, editors will allocate a temporary number as part of the triage phase. The triage also allows new CIPs to get visibility for potential reviews.

In every meeting, editors will also review in more depth some chosen CIPs (based on their readiness and the stability of the discussions about them). The goal of a review is to assess points mentioned earlier and, in particular, judge whether a CIP is reaching a consensus within the community. A proposal must also have an approved (by the editors) path to 'Active', demonstrating the adoption of the CIP to move forward. Each proposal is unique and has a bespoke path to 'Active', which must then be reviewed case-by-case.

##### 3. Once reviewed, proposals are merged as 'Proposed' or 'Rejected'

Once accepted, CIPs are merged with the status `Proposed` until they meet their path to 'Active' requirements. In some cases (mainly in the case of informational CIPs), proposals may be merged as `Active` immediately. In general, however, there must be sufficient time between the first appearance of a proposal and its acceptance into the repository to ensure enough opportunity for community members to review it.

Ideas deemed unsound shall be rejected with justifications or withdrawn by the authors. Similarly, proposals that appear abandoned by their authors shall be rejected until resurrected by their authors or another community member.

##### 4. Authors work towards completeness following their path to 'Active'

Once merged, authors shall champion their proposals and work towards their transition to active. In particular, once all of the path to 'Active' requirements have been met, authors, shall make another pull request to change their CIP's status to `Active`. Editors may also do this on occasion.

### Comments

Discussions and comments shall mainly happen on Github in pull requests. Outcomes of bi-weekly meetings shall be reported as bullet-point feedback to CIPs authors. When discussed on other mediums, we expect authors or participants to report back a summary of their discussions to the original pull request to keep track of the most critical conversations in a written form and all in one place. A dedicated Discord channel may also be created for some long-running discussions to support quick chats and progress on particular topics (while still being regularly summarized on the repository).

As much as possible, commenters/reviewers shall remain unbiased in their judgement and assess proposals in good faith. Authors have the right to reject comments or feedback but are strongly encouraged to address concerns in their 'Rationale' section. Ultimately, CIP editors shall make the last call concerning the various statements made on a proposal and their treatment by the author(s).

By opening pull requests or posting comments, commenters and authors agree to our [Code of Conduct](../CODE_OF_CONDUCT.md). Any comment infringing this code of conduct shall be removed or altered without prior notice.

## Rationale

- This is the second major iteration of this document, which aims at simplifying the process and capturing the current reality of the CIP process. Over time, the process has evolved to reach the form described above. While some points may still need to be addressed, we will address them in future updates or extensions to this CIP.

- Status has been simplified to the minimum as experience has proven a thinner granularity unnecessary.

- The choice of a code of conduct has been made following other popular open source initiatives. It serves as a good, unilaterally accepted foundation which can be later revisited if necessary.

## Path to Active

N/A

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
