##### Registering as a Team
There is an expressed community appetite to delegate to teams of individuals who register as a single DRep using [a native Plutus script](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694#registered-dreps), these will need an extra layer of information to present to people who are potentially interested in delegating to them.

`teamname`
- Compulsory
- The existence of this field will indicate to tooling that it should be expecting the metadata to take the form outlined in this section for a team of people who are registering as a single DRep
- A very short freeform text field. Limited to 80 characters.
- This SHOULD NOT support markdown text styling.
- The team authoring this metadata MUST use this field for their profile name/ username.
- The team authoring this metadata SHOULD attempt to make this field unique whilst also avoiding crass language.

`picture`
- Optional 
- A base 64 encoded profile picture
- Moderation of this image must be handled on the client side to comply with their TOS
- This SHOULD be treated as the team's profile picture by tools interpreting and displaying the metadata

`consensus`
- Optional
- To tell people how votes will be decided by the team, e.g. "x of y votes" or "Chad votes on Treasury Withdrawals and Stephan votes on..."
- If the team is following best proctice and using a native Plutus script then multisig rules will be on-chain anyway, and this field SHOULD be used to add context.

`bio`
- Compulsory
- A freeform text field.
- This SHOULD NOT support markdown text styling.
- This SHOULD be used to introduce the team and its USP.
-- I.e. “We are a team of successful Project Catalyst builders with a broad array of interests and expertise, which makes us perfect...”

`links`
- Optional
- A list of urls to the social media/ websites associated with the DRep
- Tools MUST only be expected to display the first 5 urls listed, but if more are listed they can display more.
- It is up to the client to check where these links go
- Warning about linking to external links

`donotlist`
- Optional
- If not included then the value is assumed to be false
- A boolean expression
- A true value means that the DRep does not want to show up in tooling that displays DReps. 
-- I.e. they do not want to appear in GovTool’s DRep Explorer feature

`members`
- Compulsory
- The fields describing the individual details of each team member is nested inside this field. The nested fields follow the same format as the Registering as an Individual section below except with the addition of the `role` field described below and the removal `donotlist` field in the Registering as an Individual section (teams cannot choose to omit individual members without arousing suspicion).
- Tooling MUST display the compulsory `name` and `identity` fields for each team member, all other fields are optional.

`role`
- Optional
- To describe the speciality of each individual team member e.g. "Constitutional Expert"
- A very short freeform text field. Limited to 80 characters.

