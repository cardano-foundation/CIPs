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
    - https://vimeo.com/912374177/0e9299fb5d?share=copy
    - https://vimeo.com/915297122/c39f4a739b?share=copy
Created: 2024-02-07
License: CC-BY-4.0
---

## Abstract
The Conway ledger era ushers in on-chain governance for Cardano via [CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md), with the addition of many new on-chain governance artefacts. Some of these artefacts support linking to off-chain metadata as a way to provide context.

The [CIP-100 | Governance Metadata](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100) standard provides a base framework for how all off-chain governance metadata should be formed and handled. But this is intentionally limited in scope, so that it can be expanded upon by more specific subsequent CIPs.

This proposal aims to provide a specification for off-chain metadata vocabulary that can be used to give context to CIP-100 for DRep registration and updates. Without a sufficiently detailed standard for DRep metadata we introduce the possibility to undermine the ability of DReps to explain their motivations and therefore people looking for someone to represent them with the best possible information available to make that choice. Furthermore a lack of such standards risks preventing interoperability between tools, to the detriment of user experiences.

#### Thank you
Thank you to [everyone who participated in the CIP workshops](#Acknowledgements), and to @ryun1 for creating the JSON-LD schemas for this CIP and for his excellent technical support and invaluble advice. Thank you also to the other CIP editors and attendees of the CIP Editors' Meetings where this CIP was refined, most notably @rphair and @Crypto2099. 

## Motivation: why is this CIP necessary?
CIP-1694 has set forth a model of a blockchain controlled by its community, and in doing so has challenged providers to build apps and tools that will allow users easy access to the governance features currently being built into Cardano.  Minimum viable tools must be ready at the time these governance features are launched.

The motivation for this CIP therefore is to provide these toolmakers with a simple and easy to accommodate standard which, once adopted, will allow them to read and display the metadata created by anyone who follows this standard when creating their DRep registration or update metadata. Tooling designed for DReps so that they can easily create metadata will also be made possible, because toolmakers will not need to individually innovate over the contents or structure of the metadata that their tool creates.  

Metadata is needed because blockchains are poor choices to act as content databases. This is why governance metadata anchors were chosen to provide a way to attach long form metadata content to on-chain events. By only supplying a url to the off-chain metadata, and a hash of that metadata to the blockchain we ensure correctness of data whilst minimising the amount of data posted on-chain.

### Benefits
I believed that this CIP would provide a benefit to:

#### Potential delegators
When observing from the chain level, tooling can only see the content and history of DRep registration and update certificates and any associated anchors. These on-chain components do not give any context to the motivation of a DRep, even though this information would likely be the desired context for people who might delegate their voting power. By providing rich contextual metadata we enable people choosing a DRep to delegate their voting power to make well informed decisions.

#### DReps
DReps will be able to use tools that create metadata in a standard format. This in turn will allow their metadata to be read by apps that will render their words on screen for potential delegating Ada Holders to enjoy, this may lead to greater levels of delegation. 

#### All participants
By standardising off-chain metadata formats for any tooling which creates and/or renders metadata that is referenced in DRep registration and update transactions we facilitate interoperability. This in turn promotes a rich user experience between tooling. This is good for all governance participants.

## Specification
This CIP explains the structure of any metadata referenced in a metadata anchor optionally included in any DRep registration or update transaction. 

### Teams
This CIP has been written for individuals acting in the capacity of DReps, and not for teams of people collaborating as a single DRep, although this does not preclude teams from using metadata in the structure explained by this CIP.

### Witnesses
DRep Metadata will not follow the CIP-100 specification related to signing the metadata, the [`authors` property](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#high-level-description) can be left blank without the need for tooling providers to warn their users that the author has not been validated. Instead the author can be derived from the DRep ID associated with the registration or update. The need for an `authors` field will also be discarded in favour of including `givenName`s and `Identity` inside of the `body` field. For the avoidance of doubt this CIP recommends that the entire authors property be left blank, and that tooling ignore it. 

### Extended Vocabulary
Like CIP-108, this CIP also extends the potential vocabulary of CIP-100's `body` property. 

Furthermore we extend the Schema.org definition of a [Person](https://schema.org/Person). Any property of Person maybe included within the `body`.

>**Reminder for tooling providers/builders** DRep metadata is user generated content.

The following are a list of properties tooling should expect to encounter:

#### `paymentAddress`
- Optional
- Bech32 encoded payment address, for the same network as the DRep registration is to be submitted to.

DReps may want to receive tokens for a variety of reasons such as:
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

#### `image`
- Optional
- This is a property inherited from [Person](https://schema.org/Person)
- This SHOULD be treated as the profile picture of the individual
- This MUST contain a fully described [`imageObject`](https://schema.org/ImageObject) property 
 
##### `imageObject`
- This is to be included in a metadata file as a property of the `image` property, only if the `image` property is included.
- It explains the image to those (inc. tools) who are viewing it.
- `imageObject` MUST take one of the following forms:
  1. base64 encoded image
  2. URL of image

###### base64 encoded image explained:
`imageObject` contains a base64 encoded image in its [`contentUrl`](https://github.com/schemaorg/schemaorg/issues/2696) property in a [dataURI](https://en.wikipedia.org/wiki/Data_URI_scheme) format:
  - i.e. _data:content/type;base64,_ (AND NOT _data:domain.tld_)
  - e.g. _contentURL:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==_ (AND NOT _contentURL:https://avatars.githubusercontent.com/u/113025685?v=4_)

###### URL of image explained:
If the `imageObject` DOES NOT contain a base64 encoded image, the `contentUrl` MUST contain the URL where the image can be found and the `sha256` property MUST be populated with the SHA256 hash of the image file contents found at the `contentUrl`. The SHA256 hash is needed in order for readers to verify that the image has not been altered since the metadata anchor was submitted on-chain.

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
- This is distinct from the properties of a Person listed as `knows` and `knowsAbout` because it encompasses things that the DRep has done as well as things that they know that qualify them for this position. 

#### `references`
- Optional
- This CIP extends the `references` property from [CIP-100](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100#high-level-description)
- `references` contain the following sub-properties `@type`, `label`, and `uri`
- This CIP adds two `@type` identifiers "Identity" and "Link"

##### `@type`: Link
- Optional
- It is expected that these links will be the addresses of the social media/ websites associated with the DRep in order to give a person reviewing this information a fulsome overview of the DRep's online presence.
- The creator of the metadata SHOULD add a `label`, this `label` SHOULD describe the source of the url, e.g. if it is a link to the DRep's X account then the `label` SHOULD say "X". If it is the only personal website provided by the DRep the `label` should say "Personal Website" rather than domain_name.com.
- The `label` of each `Link` SHOULD NOT be left blank
- Each `Link` MUST have exactly one `uri` (as specified in CIP-100) which SHOULD not be blank.

##### `@type`: Identity
- Optional
- The `uri` of a reference with the `@type` "Identity" is a way for DReps to prove that they are who they say they are
- It is expected that the "Identity" of a DRep will be the addresses of their most active social media account twitter, linkedin etc. or personal website.
- The DRep must reference their DRep ID in a prominent place at the location that is specified in the `uri` property of that reference. This will be used by people reviewing this DRep to prove and verify that the person described in the metadata is the same as the person who set up the social media profile.

#### `doNotList`
- Optional
- Is a boolean expression that can be given a single value of either `true` or `false`.
- If not included then the value is assumed to be `false`.
- A `true` value means that the DRep does **not** want to campaign for delegation via tooling.
- A `false` value means that the DRep does want to campaign for delegation via tooling and thus be shown via that tooling.
- e.g. a DRep who does not want to appear in GovTool’s DRep Directory feature creates metadata with `doNotList=true`.

### Application
Only the `givenName` property is listed above as compulsory, DRep metadata must include it to be considered CIP-119 compliant. As this is an extension to CIP-100, all CIP-100 fields can be included within CIP-119 compliant metadata.

### Test Vector
See [test-vector.md](./test-vector.md) for examples.

### Versioning
This proposal should not be versioned, to update this standard a new CIP should be proposed. Although through the JSON-LD mechanism further CIPs can add to the common governance metadata vocabulary.

## Rationale: how does this CIP achieve its goals?
We intentionally have kept this proposal brief and uncomplicated. This was to reduce the time to develop and deploy this standard. This way we enable tooling which depends on this standard to start development. 

### Rationale for insisting on a compulsory name
The compulsory nature of this field was controversial because the `givenName`s cannot be made unique and therefore are open to abuse (by e.g. copycats). However this is not a reason to not include a `givenName`, it a reason for people reviewing a DRep's profile to properly check their whole profile before delegating to them. A `givenName` MUST be included because a person must always have a name. Iit is a human readable identifier, it is the property that people reviewing DReps will most likely identify a given DRep by, even in the presence of copycats.

### Rationale for multiple freeform fields
It has been suggested that the `objectives`, `motivations`, and `qualifications` properties ([or at least the latter two](https://github.com/cardano-foundation/CIPs/pull/788#discussion_r1546391918)) could be one freeform property instead of 3. The rationale for having 3 separate properties is to provide structure to DReps so that they have a useful set of prompts about what they can and should write about. The author noticed in research that a single `bio` field in a form typically resulted in lower quality, often single line, responses from respondents than when this `bio` field was split into smaller fields with more highly specified purposes.

It has also been suggested that the format of the input into these three properties could be more tightly specified for example `qualifications` could require a list of qualifications. Whilst this will probably be needed I have left this up to a future CIP to specify what these specifications should be because at this stage (MVP) I have no concrete examples of how people will end up using these fields and I want to leave it up to the community to experiment with this. 

### Rationale for the identity solution that is used
PKI cryptographic solutions were also considered in the place of the current solution however they were generally considered too complex to implement for minimum viable tooling. There were also other issues with cryptographic forms of identification for MVPs:
1. solutions that involve a public/private key setup still require people verifying the identity of a DRep to know what their authentic public key is.
2. specifying the use of a verification service such as [Keybase](https://keybase.io/) would lead to centralisation and therefore reliance on a 3rd party for the identity validation of DReps.

### Rationale for extending the schema.org Person property
This CIP is not written to specifically cover the metadata created to describe teams of people collaborating to register as a DRep, but it is written to cover the metadata created by individuals to describe themselves in their capacity as a DRep. Therefore DReps are people. 

People who want to extend the use of the DRep metadata can now do so in a way that allows tooling providers to use off the peg solutions. Furthermore there may be SEO benefits to using schema.org templates. 

### Rationale for decisions made regarding `imageObject` and b64 encoding
According to schema.org The `image` property inherited from [Person](https://schema.org/Person) can either be a URL to a separate location where an image is stored, or it can be an `imageObject`. 

For the following reasons it was originally intended that this CIP would specify the use of an `imageObject` with a b64 encoded image only, because:
1. The data at the location specified by a URL could be subject to change without the hash in the metadata anchor needing to be changed
2. Choosing just one way to write and read image data would to limit the amount of tooling options that need to be created to cater to those wishing to create DRep metadata. 

However it was pointed out that this may quickly lead to relatively massive (multi-megabyte) metadata files that are more difficult to fetch and store without providing substantial value. Even IPFS would take a relatively long time to serve these files, and if there was a need to index them by some chain indexer (such as DB-Sync) then this could massively increase the storage space needed to run the indexer. 

It is also the case that CIP-100 allows for metadata to be saved within a governance transaction, and including b64 encoded images directly within transactions would be troublesome due to their size. This would not be an issue with including an image file URL. 

Therefore it was decided to allow a provision for people to submit `imageObject`'s with a URL only if a hash was included OR with a base64 encoded image, and allow them to make the decision as to which was most appropriate for their use case.  

#### Rationale for `doNotList`

This field was intended for DReps who wish to identify themselves via rich metadata but are not seeking to campaign for delegations.
By not being listed via "DRep aggregation/campaign" tools the idea is that these DReps are less likely to attract unwanted delegation from ada holders.
These DReps could be organizations that want to use their ada to vote in a transparent way on-chain but do not wish to vote on the behalf of others.

It is expected that tooling such as block explorers will list DReps using `doNotList=true`. Tooling built specifically for DRep campaign and delegation should respect the intent of this field. 

This proposal cannot force tooling to respect this desire from DReps. DReps must be aware that any information anchored on-chain can be found via tooling and may result in delegation.

### A Note on Teams
CIP-1694 allows for DReps to be registered using a native or Plutus script credential, this implies that individuals could organise to form a team that would have a broad range of expertise, and would perhaps therefore be more attractive to some delegating Ada Holders.

Participants at the workshop held to debut the first draft of this CIP strongly advocated in favour of including features that would assist a DRep comprised of a team of individuals to properly describe their endeavour.

This CIP has not included these features, the decision not to include these features was made in order to simplify this CIP so that it became suitable for the minimum viable level of tooling, with the expectation that further CIPs will build on it.

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
- Publish JSON-LD schemas & test-vector.md
- Adoption by at least one community tool

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

[A recording of this meeting can be found here](https://vimeo.com/912374177/0e9299fb5d?share=copy)
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

[A recording of this meeting can be found here](https://vimeo.com/915297122/c39f4a739b?share=copy)
</details>

<details>
  <summary><strong>Australia and APAC Workshop  - 05/03/2024</strong></summary>
    
- Andreas,
- Linh P,
- Mark Byers,
- Mike Hornan,
- Pedro Lucas,
- Phil Lewis,
</details>

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). 
