---
CIP: 120
Title: Constitution specification
Category: Metadata
Status: Proposed
Authors:
    - Ryan Williams <ryan.williams@intersectmbo.org>
    - Danielle Stanko <danielle.stanko@iohk.io>
Implementors: 
    - Danielle Stanko <danielle.stanko@iohk.io>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/796
Created: 2024-03-19
License: CC-BY-4.0
---

## Abstract

Cardano's minimum viable governance model as described within
[CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md)
introduces the concept of a Cardano constitution.
Although CIP-1694 gives no definition to the constitution's content or form.

This proposal aims to describe a standardized technical form for the Cardano
Constitution to enhance the accessibility and safety of the document.

> **Note:** This proposal only covers the technical form of the constitution,
> this standard is agnostic to the content of the constitution.

## Motivation: Why is this CIP necessary?

CIP-1694 defines the on-chain anchor mechanism used to link the off-chain
Constitution document to on-chain actions.
This mechanism was chosen due to its simplicity and cost effectiveness,
moving the potentially large Cardano constitution off-chain,
leaving only a hash digest and URI on-chain.
This is the extent to which CIP-1694 outlines the Cardano Constitution:
CIP-1694 does not provide suggestions around hashing algorithm,
off-chain storage best practices or use of rich text styling.

By formalizing the form of the constitution and its iterations,
we aim to promote its longevity and accessibility.
This is essential to ensure the effectiveness of the CIP-1694 governance model.

This standard will impact how Ada holders read the Constitution but
the main stakeholders for this are the tool makers who wish to read,
render and write a constitution.

### Safety

Without describing best practices for the form and handling of the constitution,
 we risk the constitution document being stored in an insecure manner.
By storing the constitution on a decentralized platform,
we can ensure its immutability and permissionless access.
This is a step to improve the longevity and accessibility of each constitution
iteration.

### Interoperability

By defining a file extension and formatting rules for the constitution we
ensure that tooling reading and writing the constitution will be interoperable.
Furthermore we aim to make the role of constitution iteration comparison tools
easier, by minimizing formatting and style changes between iterations.
This will reduce compatibility issues between tools,
promoting the accessibility of the constitution.

### Usability

Rich text formatting greatly enhances the readability of text,
especially in large complex documents.
Without the ability to format text, it could easily become cumbersome to read,
negatively effecting the accessability of the Cardano constitution.

## Specification

The following specification SHOULD be applied to all constitution iterations.
This standard could be augmented in the future via a separate CIP which aims to
replace this one.

### Terminology

#### Capitalisation of key terms

To avoid unnecessary edits, and therefore checksum changes,
constitution authors MUST follow the following standard English capitalisation
rules unless a translation language indicates otherwise:

##### `Constitution` vs. `constitution`

- The Constitution in effect — either the "initial" one or any new constitution — is unique and therefore capitalised ("Constitution") as a proper noun.
- Draft or proposed constitutions are not unique & therefore are not capitalised ("constitution") as a common noun.
- "Cardano Constitution" is a very specific proper noun phrase (also a title) and so each word is capitalised.
- The phrase "the Constitution", unless used non-specifically (e.g. "the constitution that voters prefer"), would generally be assumed to be _the_ Constitution and capitalised as a proper noun.

##### `Ada` vs. `ada` vs. `ADA`

- `Ada` is the currency, while `ada` indicates units of that currency (e.g. "Ada holders can accumulate more ada to increase their influence.")
- `ADA` is the trading symbol (e.g. "Fluctuations in ADA might influence decisions about the Treasury.")

### Characters

The constitution text MUST only contain printable text characters in UTF-8
encoding.

### Lines

Each line in the constitution text MUST contain at maximum 80 characters,
including spaces and punctuation.

While 80 characters is a limit, authors don't have to try and always hit 80.
Legibility of the raw (unrendered) document SHOULD be kept in mind.

#### Sentences

The constitution text MUST only contain a maximum of one sentence per line,
with each sentence followed by a newline.
Each new sentence SHOULD start on its own line with a capitalized letter.

Long sentences can be split multiple lines,
when writing the author SHOULD try to split long sentences along natural breaks.

Example:

```md
This is a short sentence on one line.

This is a long sentence and I have valid reasons for it being so long,
such as being an example of a long sentence.
When this sentence is rendered it SHOULD be shown to directly follow the 
sentence above.

This sentence is the start of a new paragraph.
```

When rendered,
these newlines between sentences SHOULD NOT be shown as newlines.
Instead they SHOULD be rendered as a space character between sentences.

Paragraphs are shown by leaving a blank line between text.

### File

Constitution files MUST be `.txt` files.

Constitution files SHOULD be named in sequential whole numbers.
Following the pattern `cardano-constitution-{i}.txt`
where `{i}` is the iteration number.

Starting from an interim constitution named `cardano-constitution-0.txt`,
the next constitution SHOULD be named `cardano-constitution-1.txt`.

To prevent misalignment, constitutions governing networks other than Cardano's
mainnet, CAN be prefixed with the network name.
For example, on the preview network the constitution file COULD be named
`preview-cardano-constitution-0.txt`.

### Hashing

When supplying a constitution hash digest to chain, the algorithm used MUST be
Blake2b-256.
Before creating a hash digest the constitution plain text MUST be in its raw
text, including any [Rich Text Formatting](#rich-text-formatting)
related characters.

### Storage

The each ratified constitution MUST be stored,
immutably on a distributed storage mechanism where backups can be easily made
in a permissionless manner by interested parties.
This storage platform SHOULD be easily accessible, with strong tooling support.

When generating a URI for the document, authors SHOULD NOT include centralized
gateways.

We propose using the
[InterPlanetary File System (IPFS)](https://www-ipfs-tech.ipns.dweb.link/).

### Rich Text Formatting

The constitution text MAY include a strict subset of rich text styling as
defined in this specification.
Tooling rendering the constitution SHOULD recognize these and render them
faithfully.

#### Line Breaks / Paragraphs

To create paragraphs, use a blank line to separate one or more lines of text.

Examples:

```md
Here's a line for us to start with.

This line is separated from the one above by two newlines,
so it will be a *separate paragraph*.

This line is also a separate paragraph, but...
This line is only separated by a single newline,
so it's a separate line in the *same paragraph*.
```

#### Headers

Headers are denoted via a hashtag character `#` followed by a space ` `.
There are six levels of headers, with each lower level set via an added `#`.
Headers are ended via a line break.
Headers SHOULD be followed below by a blank line.
Headers SHOULD not be preceded by whitespace.

The lower the number of `#` the larger order the text SHOULD be rendered.

Example:

```md
# H1

## H2

Some non-heading text.

### H3

#### H4

##### H5

###### H6

```

If text is in a header no other formatting can be applied.

An empty line SHOULD be left above and below each heading

#### Emphasis

Emphasis is applied to text between single or double asterisks,
without space between asterisks and text.
Italicized emphasis is shown via single asterisk (`*`).
Bold emphasis is shown via double asterisks (`**`).

Emphasis cannot span multiple lines.

Examples:

```md
Emphasis, aka italics, with single *asterisks*.

Strong emphasis, aka bold, with double **asterisks**.
```

Both italicized and bold cannot be applied to the same text.

#### Code and Syntax Highlighting

Texted can be highlighted as code, when encased without spaces by backticks.
This MUST not contain line breaks.

Example:

```md
Inline `code` has `back-ticks around` it.
```

The text contained within headings or emphasis cannot be highlighted as code.

#### Ordered Lists

To create an ordered list,
add line items with numbers followed by one period and then one space.
Each line item is separated by an empty line.
The numbers MUST be in numerical order,
but the list SHOULD start with the number one.

Ordered lists MUST NOT have indented items.
Ordered lists MUST NOT include headings.

```md
1. This is the first item in my ordered list

2. this is the second item in my list

3. the third item
```

#### Unordered Lists

To create an unordered list, add dashes (`-`) and one space,
in front of line items.
Each line item is separated by an empty line.

Unordered lists MUST NOT have indented items.
Unordered lists MUST NOT start with a number followed by a period.

```md
- this is my list

- I like unordered lists
```

Unordered lists MUST NOT include headings.

### Best Practices

#### Rendering

When rendering the raw document tooling COULD use standard markdown rendering
tools.

#### Hashing

When submitting an update constitution governance action,
tooling SHOULD verify the document hash digest and matches the document.

Tooling reading constitution anchors from chain SHOULD always perform a
correctness check using the hash digest on-chain.
If the hash provided on-chain does not match the hash produced from
the off-chain document, then the tooling SHOULD highlight this in a
very obvious way to users.

#### Conformance

Tools writing constitutions SHOULD strive to follow this specification.
If tooling discovering and rendering constitution documents discovers that
the document does not follow the "MUST"s in this specification then a small
warning SHOULD be given to users.

#### Form

Authors SHOULD aim to keep the document as clean and consistent as possible.

Text SHOULD try to be left aligned, without using unneeded whitespace leading
or trailing lines.

Spaces SHOULD be used over tab characters.

The last line in the document SHOULD be empty.

### Test vectors

See [Test vector file](./test-vector.md).

## Rationale: How does this CIP achieve its goals?

### Line length

We choose to restrict the maximum number of characters per line in aims of
improving readability of the document in plain text and within diff views.

It SHOULD also be considered that the 80-character limit also helps one find
run-on sentences.
If your sentence is much longer than 80, it might need breaking down.
And you SHOULD never want to see a sentence that's over two
lines long in normal text.

### Sentences

By limiting documents to one sentence per line we hope to improve the
experience when comparing documents and commenting on specific sentences.
Conventional document comparison tools such as git diff views, compare
documents on a by line basis.
By spreading text across lines,
it greatly improves tooling's ability to differentiate between documents.

Furthermore, isolating one sentence per line, allows users to more easily
isolate specific lines to comment upon.
This gives each sentence an unambiguous reference point,
which can be very useful for sharing and discussing.

### Versioning

We chose to only allow replacement of this document rather than including a
more conventional versioning scheme.
This was done for simplicity to minimize the amount of effort required to
create tooling which reads and writes constitutions.

The alternative was to add some details of version to the constitution document.
This would make changing hashing algorithm, rich text formatting, etc.
much easier.
But this makes the standard and subsequent, more complex than necessary.
We do not believe the added complexity is justified,
for the expected number of future replacement CIPs to this one.

### File

The text file was chosen, due to its ubiquity across platforms.
By choosing a common format,
we improve the accessibility of the raw document.

We choose to add sequential numbering to constitution document iterations to
improve differentiation between documents.

### Hashing

Blake2b-256 was chosen for its common use across the Cardano ecosystem.
This means that a lot of Cardano tooling already has this algorithm implemented.
This lowers the bar to entry for existing tool makers to add
constitutional support.

For simplicity, we decide not to include an easy mechanism for changing of
hashing algorithms between constitutions.

### Storage

Ensuring the Cardano Constitution and its iterations can be accessed in a
permissionless manor is paramount.
Permissionless networks such as IPFS reduce the ability for parties to
censor the content.
With each interested party able to make copies of constitutions,
this improves the resilience of the documents from deletion.

The primary competing idea to platforms such as IPFS is to store the
constitution text on Cardano itself.
This would philosophically be superior to storing the document off-chain,
keeping the Cardano Constitution on Cardano.
The counter point to this is that,
Cardano is not a general data storage system, rather it is a ledger.
Storing data on Cardano is expensive and difficult, without strong tooling
support.

### Rich Text Formatting

Rich text styling will greatly improve the readability of the
constitution documents, when rendered.

#### Markdown

Markdown styling was chosen due to its ubiquity, with strong tooling support.
Furthermore, markdown has a benefit in that the unrendered documents are
still human readable.
This is in contrast to other solutions such as HTML.

#### Strict subset

We chose a strict subset of markdown text styling for two reasons.
Firstly, markdown contains a very large and varied syntax,
reducing the scope making implementation easier for all tooling.
Secondly, some features of markdown may not want to be used in a formal
constitution document.
Embedded HTML or videos are likely things to be avoided.

### Open Questions

- [x] How can we support multi-languages?
  - The Cardano constitution will be in English, but we will add best practice guidelines via [Best Practices](#best-practices).
- [x] Should we specify any standardization for the proposal policy?
  - Due to lack of interest in this, we will leave it out of this standard.
- [x] How can we add page breaks?
  - We wont, instead we will prioritize a minimum set of rich text formatting. We can provide some guidance via [Best Practices](#best-practices).
- [x] Do we want a mechanism for specifying authors? (similar to CIP-100)
  - No, as CIP-100 compliant metadata can be supplied at time of constitution update.
- [x] What SHOULD we name the constitution file? we could embed some nice naming or metadata.
  - Naming the file `cardano-constitution` seems specific enough, adding iteration numbers is a nice addition too.

## Path to Active

### Acceptance Criteria

- [x] This standard is followed for the interim Cardano Constitution
- [ ] This standard is utilized by two tools reading constitution data from chain
  - [constitution.gov.tools](https://constitution.gov.tools/)

### Implementation Plan

#### Solicitation of feedback

- [x] Answer all [Open Questions](#open-questions)
- [ ] Review from the Civics Committee

#### Test vector

- [x] Author to provide a test vector file with examples.

## Acknowledgements

<details>
  <summary><strong>First draft</strong></summary>
  
  We would like to thank those who reviewed the first draft of this proposal;
  - Danielle Stanko
  - Kevin Hammond
  - Steven Johnson

</details>

<details>
  <summary><strong>Significant Contributions</strong></summary>
  
  We would like to thank Robert Phair ([@rphair](https://github.com/rphair)) for
  his expert contributions to this proposal.

</details>

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
