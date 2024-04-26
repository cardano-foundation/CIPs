---
CIP: 119
Title: Governance metadata - DReps
Category: Metadata
Status: Proposed
Authors:
    - Thomas Upfield <thomas.upfield@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/788
Created: 2024-02-07
License: CC-BY-4.0
---

## Abstract
The Conway ledger era ushers in on-chain governance for Cardano via [CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md), with the addition of many new on-chain governance artefacts. Some of these artefacts support linking to off-chain metadata as a way to provide context.

The [CIP-100 | Governance Metadata](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100) standard provides a base framework for how all off-chain governance metadata should be formed and handled. But this is intentionally limited in scope, so that it can be expanded upon by more specific subsequent CIPs.

This proposal aims to provide a specification for off-chain metadata vocabulary that can be used to give context to CIP-100 for DRep registration and updates. Without a sufficiently detailed standard for DRep metadata we introduce the possibility to undermine the ability of DReps to explain their motivations and therefore people looking for someone to represent them with the best possible information available to make that choice. Furthermore a lack of such standards risks preventing interoperability between tools, to the detriment of user experiences.

#### Thank you
Thank you to [everyone who participated in the CIP workshops](#Acknowledgements)

## Motivation: why is this CIP necessary?
CIP-1694 has set forth a model of a blockchain controlled by its community, and in doing so has challenged providers to build apps and tools that will allow users easy access to the governance features currently being built into Cardano.  Minimum viable tools must be ready at the time these governance features are launched.

The motivation for this CIP therefore is to provide these toolmakers with a simple and easy to accommodate standard which, once adopted, will allow them to read and display the metadata created by anyone who follows this standard when creating their DRep registration or update metadata. Tooling designed for DReps so that they can easily create metadata will also be made possible, because toolmakers will not need to individually innovate over the contents or structure of the metadata that their tool creates.  

Metadata is needed because blockchains are poor choices to act as content databases. This is why governance metadata anchors were chosen to provide a way to attach long form metadata content to on-chain events. By only supplying an On-Chain hash of the off-chain we ensure correctness of data whilst minimising the amount of data posted to the chain.

### Benefits
I believed that this CIP would provide a benefit to:

#### Potential delegators
When observing from the chain level, tooling can only see the content and history of DRep registration and update certificates and any associated anchors. These on-chain components do not give any context to the motivation of a DRep, even though this information would likely be the desired context for people who might delegate their voting power. By providing rich contextual metadata we enable people choosing a DRep to delegate their voting power to make well informed decisions.

#### DReps
DReps will be able to use tools that create metadata in a standard format. This in turn will allow their metadata to be read by apps that will render their words on screen for potential delegating Ada Holders to enjoy, this may lead to greater levels of delegation. 

#### All participants
By standardising off-chain metadata formats for any tooling which creates and/or renders metadata referenced in DRep registration and update transactions we facilitate interoperability. This in turn promotes a rich user experience between tooling. This is good for all governance participants.

## Specification
CIP-1694 specifies that metadata anchors are optional for DRep registration and updates. This CIP covers metadata for the aforementioned transaction types, but it does not cover metadata for voting transactions. 

#### A Note on Teams
CIP-1694 allows for DReps to be registered using a native or Plutus script credential, this implies that individuals could organise to form a team that would have a broad range of experitise, and would perhaps therefore be more attractive to some delegating Ada Holders. 

Participants at the workshop held to debut the first draft of this CIP strongly advocated in favour of a CIP that would include features that would assist a DRep comprised of a team of individuals properly describe their endeavour to delegating Ada Holders and anyone else reading the metadata associated with their registration.

This CIP has not included these features, the decision not to include these features was made in order to simplify this CIP so that it became suitable for the minimum viable level of tooling, with the expectation that further CIPs will build on it. 

### Witnesses
DRep Metadata will not follow the CIP-100 specification related to signing the metadata, the [authors property](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#high-level-description) can be left blank without the need for tooling providers to warn their users that the author has not been validated. Instead the author can be derived from the DRep ID associated with the registration. The need for an `authors` field will also be discarded in favour of including usernames inside of the `body` field. For the avoidance of doubt this CIP recommends that the entire authors property be left blank, and that tooling ignore it. 

### Extended Vocabulary
Like CIP-108, this CIP also extends the potential vocabulary of CIP-100's `body` property. 

Furthermore we extend the Schema.org definition of a [Person](https://schema.org/Person). Any property of Person maybe included within the `body`.

  

>**Reminder for tooling providers/builders** DRep metadata is user generated content.

The following are a list of properties tooling should expect to encounter:

#### `paymentAddress`
- Optional

Dreps may want to recieve tokens for a variety of reasons such as:
- donations
- expenses
- any incentive program

Therefore there MAY be a `paymentAddress` field in the metadata where such payments could be sent. This makes such an address public and payments to DReps transparent. 

This SHOULD NOT be confused with the `address` property of a [Person](https://schema.org/Person), `address` in the context of a DRep refers to their location and NOT their payment address.

#### `givenName`
- Compulsory
- This is a property inherited from [Person](https://schema.org/Person)
- It is the only compulsory property
- A very short freeform text field. Limited to 80 characters.
- This MUST NOT support markdown text styling.
- It is intended that authors will use this field for their profile name/ username.

#### `Image`
- Optional
- This is a property inherited from [Person](https://schema.org/Person)
- This SHOULD be treated as the profile picture of the individual
- This should contain an [`imageObject`](https://schema.org/ImageObject) property
  - `imageObject` SHOULD contain a base64 encoded image in its [`contentURL`](https://github.com/schemaorg/schemaorg/issues/2696) property in a [dataURI](https://en.wikipedia.org/wiki/Data_URI_scheme) format. 


#### `objectives`
- Optional
- A freeform text field with a maximum of 1000 characters
- A short description of what the person believes and what they want to achieve as a DRep

#### `motivations`
- Optional
- A freeform text field with a maximum of 1000 characters
- A short description of why they want to be a DRep, what personal and professional experiences have they had that have driven them to register 

#### `qualifications`
- Optional
- A freeform text field with a maximum of 1000 characters 
- A space where the registrant can to list the qualifications they hold that are relevant to their role as a DRep
- This is distinct from the properties of a Person listed as `knows` and `knowsAbout` 

#### `references`
- Optional
- This CIP extends the `references` property from [CIP-100](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100#high-level-description)
- `references` contain the following sub-properties `type`, `label`, and `uri`
- This CIP adds two `@type` identifiers "Identity" and "Link"
- The creator of the metadata SHOULD add a `label`, this `label` SHOULD describe the source of the url, e.g. if it is a link to the DRep's X account then the `label` SHOULD say "X". If it is a personal website the `label` should say "Personal Website" rather than domain_name.com.
- The `label` of each link SHOULD NOT be left blank
- Each link MUST have exactly one `uri` (as specified in CIP-100) which MUST not be blank.

##### `type`: Link
- Optional
- It is expected that these links will be the addresses of the social media/ websites associated with the DRep in order to give a person reviewing this information a fulsome overview of the DRep's online presence.

##### `type`: Identity
- Optional
- The `uri` of a reference with the `type` "Identity" is a way for DReps to prove that they are who they say they are
- Each piece of metadata referenced in the anchor of a DRep registristration or update transaction MUST contain at least one reference with the `type` "Identity". Else tooling SHOULD ignore the metadata.
- It is expected that the "Identity" of a DRep will be the addresses of their most active social media account twitter, linkedin etc. or personal website.
- The DRep must reference their DRep ID in a prominent place at the location that is specified in the `uri` property of that reference. This will be used by people reviewing this DRep to prove and verify that the person described in the metadata is the same as the person who set up the social media profile.

PKI cryptographic solutions were also considered in the place of the current solution however they were generally considered too complex to implement for minimum viable tooling. There were also other issues with cryptographic forms of identification for MVPs:
1. solutions that involve a public/private key setup still require people verifying the identity of a DRep to know what their authentic public key is.
2. specifying the use of a verification service such as [Keybase](https://keybase.io/) would lead to centralisation and therefore reliance on a 3rd party for the identity validation of DReps.

#### `doNotList`
- Optional
- If not included then the value is assumed to be false
- A boolean expression
- A true value means that the DRep does not want to show up in tooling that displays DReps. 
  - e.g. a DRep who does not want to appear in GovTool’s DRep Explorer feature creates metadata with donotlist as true.

### Application
DRep metadata must include all compulsory fields to be considered CIP-119 compliant. As this is an extension to CIP-100, all CIP-100 fields can be included within CIP-119 compliant metadata.

### Test Vector
See [test-vector.md](./test-vector.md) for examples.

### Versioning
This proposal should not be versioned, to update this standard a new CIP should be proposed. Although through the JSON-LD mechanism further CIPs can add to the common governance metadata vocabulary.

## Rationale: how does this CIP achieve its goals?
We intentionally have kept this proposal brief and uncomplicated. This was to reduce the time to develop and deploy this standard. This way we enable tooling which depends on this standard to start development. 

### Rationale for Insisting on a compulsory username
The compulsory nature of this field was controversial because the `username`s cannot be made unique and therefore are open to abuse (by e.g. copycats). However this is not a reason to not include a `username` it a reason for people reviewing a DRep's profile to properly check their whole profile before delegating to them. A `username` MUST be included because it is a human readable identifier, it is the property that people reviewing DReps will most likely identify that DRep by even in the presence of copycats.

### Rationale for multiple freeform fields
It has been suggested that the `objectives`, `motifications`, and `qualifications` properties ([or at least the latter two](https://github.com/cardano-foundation/CIPs/pull/788#discussion_r1546391918)) could be one freeform property instead of 3. The rationale for having 3 sepparate properties is to provide structure to DReps so that they have a useful set of prompts about what they can and should write about. The author noticed in research that a single `bio` field in a form typically resulted in lower quality, often single line, responses from respondees than when this `bio` field was split into smaller fields with more highly specified purposes.

It has also been suggested that the format of the input into these three properties could be more tightly specified for example `qualifications` could require a list of qualifications. Whilst this will probably be needed I have left this up to a future CIP to specify what these specifications should be because at this stage (MVP) I have no concrete examples of how people will end up using these fields and I want to leave it up to the community to experiment with this. 


### Open Questions
|QID |Question |Answer |
|----|---------|-------|
|1   |Should we accommodate for profile pictures to be included in metadata? | Yes, furthermore, a future CIP may allow for multiple pictures |
|2   |Do we need to replace the `bio` field with a more structured set of fields? | Yes, adding structure is intended to guide people to add data which is more interesting to the reader |
|3   |Can we include and verify an ADA handle to uniquely identify a DRep |[This](#type-identity) is how we verify the identity of a DRep |
|4   |What do we do about lack of metadata integrity | This is up to the tooling provider|
|5   |Should we split this CIP up into separate transactions or also add the vote transaction metadata |The scope is fine |
|6   |Compulsory vs optional for all fields |See the relevant section for each property |
|7   |types of DRep (script? representing an organisation? want delegations?)| This CIP is optimised for individuals who are DReps, but doesnt exclude teams. It is agnostic as o wherther the DRep is registered via a script or not |
|8   |How can we verify the information that we are displaying(?) |This CIP adopts provisions from CIP-100 about how to display metadata which is in an unexpected format. Otherwise this CIP leaves questions surrounding the display of data to tooling providers. Identity verification is covered in QID 8. |
|9   |Should tooling providers displaying data warn people that none of the information is verified and they should DYOR? |This is not specified in this CIP |
|10  |Should tooling providers making metadata provide some information about best practices such as putting DRep ID in twitter bio? |This is not specified in the CIP |
|11  |What do we care about when someone is retiring? | Retirement transactions no longer include a metadata anchor|
|12  |When someone updates do we want a 1 line summary of what has changed? |Possibly future CIPs could include this feature |
|13  |Should tools inform people of recent changes? |This is up to tooling providers |
|14  |Should there be an incentives address, where DRep incentives are paid? |See [`paymentAddress`](#paymentAddress) |
|15  |PKI Public Key, Fingerprint, or DID? | See [`type`: Identity](#type-identity) |

## Path to Active

### Acceptance Criteria


### Implementation Plan
<!-- How I plan to meet the acceptance criteria -->

## Acknowledgements
There have been 3 lively public workshops on this subject, and I would like to thank the following people

<details>
  <summary><strong>Workshop 1 - 07/02/2024</strong></summary>

- Abhik Nag
- Adam Dean
- Adam Rusch
- Digital Fortress (Rick McCracken)
- Eduardo Silka
- Jose Miguel De Gamboa
- Leonardo Silka
- Lorenzo Bruno
- Mike Susko
- Nicolas Cerny
- Peter Wolcott
- Ryan Williams
- Sheldon Hunt
- Tyler Wales
- Upstream SPO
- Valeria Devaux
- Дима

</details>

<details>
  <summary><strong>Workshop 2 - 20/03/2024</strong></summary>
    
- Adam Rusch
- Aleksandar Djuricic (Aleks)
- Christopher Hockaday
- Digital Fortress (Rick McCracken)
- Eduardo Silka
- HD5000
- Igor Velickovic
- Input Endorsers
- Konstantinos Dermentzis
- Leonardo Silka
- Michael Madoff
- Michał Szałowski
- Mike Hornan
- Peter Wolcott
- Ryan
- Ryan (Cerkoryn)
- Ryan Williams
- Steve Lockhart 

</details>

<details>
  <summary><strong>Austtralia and APAC Workshop  - 05/03/2024</strong></summary>
    
- Andreas,
- Linh P,
- Mark Byers,
- Mike Hornan,
- Pedro Lucas,
- Phil Lewis,
</details>

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). 