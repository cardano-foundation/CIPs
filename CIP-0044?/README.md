---
CIP: 44
Title: Additional factors for NFT market verification
Authors: havealoha <havealoha@gmail.com>
Comments-Summary: No comments
Comments-URI: https://forum.cardano.org/t/cip-proposal-for-discussion-market-cnft-policyid-verification/95268/31
Status: Draft
Type: Process
Created: 2022-02-09
License: CC-BY-4.0
Requires: 
---

# Additional factors for facilitating NFT policyID market verification

# Simple Summary

A community standard for CNFT policyID's to facilitate market verification utilizing a no name asset with tag 808 correlated with one or more online or onchain accounts by confirming policyID information from each source. This proposed standard will allow for verification of CNFT policyID’s across the secondary market space. Existing policyID verification varies by market but often relies on a multi step 3 way process involving exchanging a social media message, email or webform which contains the name of the creator, collection name, social media account, and email address. Markets could utilize this proposal to automate the collection of the required information, queue the policyID for manual verification, present consumers with a rating system and/or choose to fully automate the verification process.

## Abstract

A creator would start by making a new Cardano NFT policy. Then they create a document or tweet on Twitter, GitHub, a webpage or any URI based online platform within their control. Additionally, an ADA Handle (Handle) with an augmentation specifying a policyID could be used. Within the Handle, tweet or document they would add the policyID of the NFT collection in question. This proves that their Handle, online persona or social reputation controls that particular account. Any popular platform could be used so long as it provides a URI for the market so that it can retrieve the account information and the document with the policyID without impediment. The creator would then create the no name 808 asset, within which, additional tags will specify creator, collection name, and a URI array. Within the URI array, one or more URI’s resolve to the Handle, Tweet or document that contains the policyID. This two step process proves that the creator has control of both the policyID on the chain and the one or more Handles or online accounts. The current verification system would be a fallback for creators with pre-existing collections that can not be updated with an 808 asset or for individual assets where it is otherwise not feasible. Being similar to CIP-0027, the ecosystem is already familiar with part of this proposal. This same set of tags could be added to individual assets as they are minted instead of utilizing the 808 no name token. In that instance, the assetID would be utilized instead of the policyID.

## Motivation

CNFT marketplaces struggle to keep up with verifying new collection policyID’s due to the influx of new creators and projects. This standard would relieve the market spaces from verifying new policyID’s and could instead display the social media accounts of the creator who owns the collection. From here the consumer is left to do their due diligence. This process also provides the marketplace with the creator name, collection name and possibly an Avatar\PFP if one is available from the platform hosting the URI.

## Specification

A new tag of 808 is proposed for this implementation.

1. The creator makes a new Cardano policy.
2. They then use one or more existing online platforms where they have a social reputation, one that their potential consumers find trustworthy. On this platform they create content that contains the policyID of the NFT collection in question. If using a Handle, the owner adds the policyID as an augmentation.
3. The 808 verification tags are to be written to an unnamed asset, using the policy to be used for the intended Cardano Assets.
4. Updates or rewrites are allowed.
5. Within this created asset will be the metadata for verification. It will use a tag of 808, and then have three tags to identify the name of the collection, the name of the creator, and URI. Those tags will be “collection”, “creator”, and “URI” respectively.
6. The “collection”, “creator” and “URI” key tags can be any UTF-8 value or array. By allowing for an array, any tag can exceed the per line 64 character limitation.
7. All markets will be instructed to look for the latest minted 808 asset on a policy and cross reference the URI document policyID data with the 808 asset. If they match, the projectID can be considered validated. The market could then issue a rating system. If multiple URI’s were validated they could show a higher validation score. The creators social media handles could be displayed next to the verified collection or asset.

## Example JSON with string

```
{
	"808": {
		"collection": "Aloha",
		"creator": "Ēwe hānau o ka ʻāina",
		"URI": [
			"https://twitter.com/hadaloha/status/1493080687959699459",
			"https://github.com/nicholseric/nicholseric/blob/master/My%20CNFT%20PolicyIDs",
			"$conrad\augmentation\policyIDs"
		]
	}
}
```

## Example Tweet

I created this new Cardano NFT policy!
6574f051ee0c4cae35c0407b9e104ed8b3c9cab31dfb61308d69f33c

## Example GitHub

I created this new Cardano NFT policy!
6574f051ee0c4cae35c0407b9e104ed8b3c9cab31dfb61308d69f33c

## Process Flow

1. Create policy for planned assets.
2. Create online platform document or Handle by inserting or augmenting with a policyID.
3. Mint no name asset with 808 metadata.
4. Mint planned assets using this same policy.
5. Existing policies can mint an appropriate 808 asset.
6. The 808 asset can be burned.

## Rationale

By creating a new tag for the distinct purpose of policyID verification, Cardano Asset makers, and Marketplaces can uniformly verify their policyID’s with predictable results. By creating the instructions on a single, no name asset, all marketplaces will know the correct location of the policyID verification asset, without having to further locate it. By enforcing the requirement of honoring only the latest mint, Cardano NFT creators can move or change their social media accounts and collection information. It is easy to work with this new standard, and does not require an in depth understanding of smart contracts. One URL could potentially support multiple policyID’s. Marketplaces could choose to have these automated verified collections queue into a human review.

20220209 21:24 Discussion on Discord in Blade adahandle channel:
Special thanks to gorath for suggestions on making additional tags available for manual verification or those not wanting to use a Handle.
Thanks to BenOJosh for asking hard questions.
20200213 Discussion on [CIP Proposal for discussion " Market CNFT policyID verification "](https://forum.cardano.org/t/cip-proposal-for-discussion-market-cnft-policyid-verification/95268) with @HeptaSean and @LonacheG
Tweeted @ many marketplaces and community members to come and engage:
https://twitter.com/hadaloha/status/1493435217716998147
https://twitter.com/hadaloha/status/1492719282769121280
https://twitter.com/hadaloha/status/1492715689513132034
https://twitter.com/hadaloha/status/1491639230430208002
https://twitter.com/hadaloha/status/1491559058926555138
Also posted in a few other discord channels.
