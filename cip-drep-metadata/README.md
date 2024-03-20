---
CIP: ?
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
The Conway ledger era ushers in on-chain governance for Cardano via [CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md), with the addition of many new on-chain governance artefacts. Some of these artefacts support the linking off-chain metadata, as a way to provide context.

The [CIP-100 | Governance Metadata](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0100) standard provides a base framework for how all off-chain governance metadata should be formed and handled. But this is intentionally limited in scope, so that it can be expanded upon by more specific subsequent CIPs.

This proposal aims to provide a specification for off-chain metadata vocabulary that can be used to give context to CIP-100 for DRep registration and updates. Without a sufficiently detailed standard for DRep metadata we introduce the possibility to undermine the ability of DReps to explain their motivations and therefore people looking for someone to represent them with the best possible information available to make that choice. Furthermore a lack of such standards risks preventing interoperability between tools, to the detriment of user experiences.

#### Thank you
Thank you to [everyone who participated in the CIP workshops](#Acknowledgements)

## Motivation: why is this CIP necessary?
CIP-1694 has set forth a compelling vision of a blockchain controlled by its community, and in doing so has thrown down the gauntlet to tooling providers to build apps and other kinds of tooling that will allow their users easy enjoyment of the governance features currently being built into the fabric of the Cardano blockchain. As I write this developers are feverishly hammering away at their keyboards like the blacksmiths of old to bring us the first iteration of these tools in a minimum viable format. 

The motivation for this CIP therefore is to provide these toolmakers with a simple and easy to accomodate standard which once adopted will allow them to read and display the metadata created by anyone who follows this standard when creating their DRep registration or update metadata. Tooling designed for DReps so that they can easily create metadata will also be made possible, because toolmakers will not need to all individually innovate over the contents or structure of the metadata that their tool creates.  

Metadata is needed because blockchains are poor choices to act as content databases. This is why governance metadata anchors were chosen to provide a way to attach long form metadata content to on-chain events. By only supplying an On-Chain hash of the off-chain we ensure correctness of data whilst minimising the amount of data posted to the chain.

## Specification
CIP-1694 specifies that metadata anchors are optional for DRep registration and updates. This CIP covers metadata for the aforementioned transaction types, but it does not cover metadata for voting transactions. 

#### A Note on Teams
CIP-1694 allows for DReps to be registered using a native or Plutus script credential, this implies that individuals could organise to form a team that would have a broad range of experitise, and would perhaps therefore be more attractive to some delegating Ada Holders. 

Participants at the workshop held to debut the first draft of this CIP strongly advocated in favour of a CIP that would include features that would assist a DRep comprised of a team of individuals properly describe their endeavour to delegating Ada Holders and anyone else reading the metadata associated with their registration.

This CIP has not included these features, the decision not to include these features was made in order to simplify this CIP so that it became suitable for the minimum viable level of tooling, with the expectation that further CIPs will build on it. 

### Formatting
If DRep Metadata is not formatted in the way described by this CIP then tooling SHOULD either:
1. Deal with it as described in CIP-100 (by rendering the raw unformatted document)
2. Not display the any of the metadata

In either case the tooling SHOULD provide a warning that this has happened and link to the url described in the metadata anchor of the DRep registration.

### Missing
If the DRep metadata cannot be found at the address specified in the anchor then the tooling SHOULD provide a warning. There is no need to link to the url in the metadata anchor. 

### Witnesses
DRep Metadata will not follow the CIP-100 specification related to signing the metadata, instead they are attached to a DRep registration. The need for an `authors` field will also be discarded in favour of including usernames inside of the `body` field. 

### Extended Vocabulary
Like CIP-108, this CIP also extends the potential vocabulary of CIP-100's `body` property. For all of these properties tooling providers MUST be aware that they are responsible for what they display to their users and that these fields could be used for illegal, unsavoury, or innapropriate purposes or language. Therefore such tools SHOULD have a terms of service which they enforce to moderate what they show to their users. The following are a list of properties tooling should expect to encounter:

#### `paymentAddress`
Dreps may want to recieve tokens for a variety of reasons such as:
- donations
- expenses
- any incentive program

Therefore there will be a `payment_address` field in the metadata where such payments could be sent. This makes such an address public and payments to DReps transparent. 

#### `username`
- Compulsory
- A very short freeform text field. Limited to 80 characters.
- This SHOULD NOT support markdown text styling.
- Authors MUST use this field for their profile name/ username.
- Authors SHOULD attempt to make this field unique.
- Authours SHOULD avoid crass language.

The compulsory nature of this field was controversial because the `username`s cannot be made unique and therefore are open to abuse (by e.g. copycats). However this is not a reason to not include a `username` it a reason for people reviewing governance actions to properly check the whole profile of a DRep before delegating to them. A `username` MUST be included because it is a human readable identifier, it is the property that people reviewing DReps will most likely identify that DRep by even in the presence of copycats.

#### `picture`
- Optional 
- A base 64 encoded profile picture
- Moderation of this image must be handled on the client side to comply with their TOS
- This SHOULD be treated as the profile picture of the individual

#### `objectives`
- Optional
- A freeform text field with a maximum of 1000 characters
- A short description of what the person believes nd what they want to achieve as a DRep

#### `motivation`
- Optional
- A freeform text field with a maximum of 1000 characters
- A short description of why they want to be a DRep, what personal and professional experiences have they had that have driven them to 

#### `qualifications`
- Optional
- A freeform text field with a maximum of 1000 characters 
- A space to list the qualifications that the subject of this metadata has that are relevant to being a DRep

#### `identity`
- Compulsory
- A link to a social media profile where the person must reference their DRep ID in their profile.
- This will be used by people reviewing this DRep to prove and verify that the person described in the metadata is the same as the person who set up the social media profile.
- Tooling providers SHOULD warn people that none of the information is verified by the tool and they should DYOR
- Tooling providers making metadata SHOULD provide some information about why this is important.

PKI cryptographic solutions were also considered in the place of the current solution however they were generally considered too complex to implement for minimum viable tooling. There were also other issues with cryptographic forms of identification for MVPs:
1. solutions that involve a public/private key setup still require people verifying the identity of a DRep to know what the authentic pulic key is.
2. specifying the use of a verification service such as [Keybase](https://keybase.io/) would lead to centralisation and therefore reliance on a 3rd party for DReps.

#### `links`
- Optional
- A list of urls to the social media/ websites associated with the DRep
- It is up to the client to check where these links go
- Warning about linking to external links

#### `donotlist`
- Optional
- If not included then the value is assumed to be false
- A boolean expression
- A true value means that the DRep does not want to show up in tooling that displays DReps. 
-- I.e. they do not want to appear in GovTool’s DRep Explorer feature


### Application
DRep metadata must include all compulsory fields to be considered CIP-???? compliant. As this is an extension to CIP-100, all CIP-100 fields can be included within CIP-???? compliant metadata.

### Test Vector
See test-vector.md for examples.

### Versioning
This proposal should not be versioned, to update this standard a new CIP should be proposed. Although through the JSON-LD mechanism further CIPs can add to the common governance metadata vocabulary,

## Rationale: how does this CIP achieve its goals?
We intentionally have kept this proposal brief and uncomplicated. This was to reduce the time to develop and deploy this standard. This way we enable tooling which depends on this standard to start development. The fields which have been chosen for this standard are heavily inspired by those that we are seeking to introduce for GovTool. We did this because GovTool will likely be the first technical implementation of this standard. 

I believed that this CIP would provide a benefit to:

#### Potential delegators
When observing from the chain level, tooling can only see the content and history of DRep registration and update certificates and any associated anchors. These on-chain components do not give any context to the motivation of a DRep, even though this information would likely be the desired context for people who might delegate their voting power. By providing rich contextual metadata we enable people choosing a DRep to delegate their voting power to make well informed decisions.

#### DReps
DReps will be able to use tools that create metadata in a standard format. This in turn will allow their metadata to be read by apps that will render their words on screen for potential delegating Ada Holders to enjoy, this may lead to greater levelso of delegation. 

#### All participants
By standardising off-chain metadata formats for any tooling which creates and/or renders metadata referenced in DRep registration and update transactions we facilitate interoperability. This in turn promotes a rich user experience between tooling. This is good for all governance participants.

### Open Questions
1. ~~Do we allow profile pictures to be included in metadata~~ <-- YES! possibly a list of pictures.
2. ~~Do we need to replace the `bio` field with a more structured set of fields~~
3. ~~Can we include and verify an ADA handle to uniquely identify a DRep~~
4. ~~What do we do about lack of metadata integrity~~ <-- not show the metadata and make it clear that the #metadata =/ metadata#
5. ~~Should we split this CIP up into separate transactions or also add the vote transaction metadata~~ <-- the scope is fine
6. ~~Compulsory vs optional for all fields~~
7. ~~types of DRep (script? representing an organisation? want delegations?)~~
8. ~~How can we verify the information that we are displaying(?)~~ 
9. ~~Tooling providers displaying data SHOULD warn people that none of the information is verified and they should DYOR~~
10. ~~Tooling providers making metadata SHOULD provide some information about best practices such as putting DRep ID in twitter bio.~~
11. ~~What do we care about when someone is retiring?~~ <-- just the reason why
12. ~~When someone updates do we want a 1 line summary of what has changed?~~
13. ~~Tooling to inform people of recent changes?~~
14. ~~incentives address, where DRep incentives are paid ???~~
15. ~~PKI Public Key, Fingerprint, or DID?~~ 

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
