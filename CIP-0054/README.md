---
CIP: 54
Title: Cardano Smart NFTs
Status: Proposed
Category: Tokens
Authors:
  - Kieran Simkin <hi@clg.wtf>
Implementors:
  - Kieran Simkin
Discussions:
  - https://forum.cardano.org/t/cip-draft-cardano-smart-nfts/100470
  - https://github.com/cardano-foundation/CIPs/pull/263
Created: 2022-05-18
License: CC-BY-4.0
---

## Abstract

This CIP specifies a standard for an API which should be provided to Javascript NFTs, it also defines some additions to the 721 metadata standard defined in [CIP-0025](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025) which allow an NFT to specify it would like to receive certain current information from the blockchain. 

## Motivation: Why is this CIP necessary?

Currently if an NFT creator wishes to change or otherwise “evolve” their NFT after minting, they must burn the token and re-mint. It would be very nice if the user were able to modify their NFT simply by sending it to themselves with some extra data contained in the new transaction metadata. This would allow implementation of something like a ROM+RAM concept, where you have the original immutable part of the NFT (in Cardano’s case represented by the original 721 key from the mint transaction), and you also have a mutable part – represented by any subsequent transaction metadata.

It would also be nice to be able to retrieve data that has been previously committed to the blockchain, separately to the NFT which wishes to access it. This would be useful for retrieving oracle data such as current Ada price quotes – as well as for allowing an NFT to import another NFT’s data.

Further to this - for on-chain programatically generated NFTs, it makes sense to mint the code to render the NFT as one token, and then have the individual NFTs contain only the input variables for that code. This CIP specifies an additional metadata option which specifies that an NFT should be rendered by another token - this will massively reduce code duplication in on-chain NFTs.

This combination of functionality enables many exciting new possibilities with on-chain NFTs.

## Specification

### The Metadata

Minting metadata for Smart NFTs – based on the existing [CIP-0025](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025) standard:

```
{
	"721": {
		"<policy_id>": {
			"<asset_name>": {
				"name": <string>,

				"image": <uri | array>,
				"mediaType": "image/<mime_sub_type>",

				"description": <string | array>,

				"files": [{
					"id": <string>
					"name": <string>,
					"mediaType": <mime_type>,
					"src": <uri | array>,
					<other_properties>
				}],

				"uses": {
					"transactions": <string | array>,
					"tokens": <string | array>,
					"renderer": <string>	  
				}
			}
		},
		"version": "1.0"
	}
}
```

Here we have added the “uses” key – any future additions to the Smart NFT API can be implemented by adding additional keys here. 
We've also added an additional field to the files array - this is to specify a unique identifier to enable the files to be referenced by the Javascript API below. 

#### The transactions key

To enable evolving NFTs where the NFT monitors a transaction history and changes in response to new transaction metadata, we define a sub-key called “transactions”, which can contain either a string or an array, specifying the tokens or addresses the NFT wishes to receive the transaction history for. These transaction histories will be provided to the NFT via the Javascript API detailed below.

We also define a special keyword “own” which can be used to monitor the NFT’s own transaction history. So if we wish to create an “evolvable” NFT that can respond to additions to its own transaction history, the “uses” key within the metadata would look like:

```
	"uses": {
		"transactions": "own"
	}
```

If you wanted to create an evolving NFT which monitors its own transaction history, as well as that of an external smart contract address, the metadata would look like this:

```
 	"uses": {
		"transactions": [
			"own",
			"addr1wywukn5q6lxsa5uymffh2esuk8s8fel7a0tna63rdntgrysv0f3ms"
		]			
	}
```
Finally, we also provide the option to receive the transaction history for a specific token other than the NFT itself (generally this is intended to enable import of Oracle data or control data from an external source – although monitoring an address transaction history could also be used for that). 

When specifying an external token to monitor, you should do so via the token’s fingerprint as in this example:

```
 	"uses": {
		"transactions": [
			"own",			
			"asset1frc5wn889lcmj5y943mcn7tl8psk98mc480v3j"
		]
	}
```

#### The tokens key

To enable modifier tokens - (that is, a token which you can hold alongside a Smart NFT which changes the Smart NFT's appearance or behaviour in some way); we provide a way for the Smart NFT to monitor the tokens held by a specific address. Similarly to the “transactions” key, the “tokens” key will also accept either a string or array.

In this case we define the “own” keyword to mean the tokens held by the same stake key that currently holds the Smart NFT itself.

For example, to create an evolvable NFT which also supports modifier tokens, the “uses” block would look like this: 

```
	"uses": {
		"transactions": "own",
		"tokens": "own"
	}
```

We could also monitor a particular smart contract address, for example if we wanted to see how many tokens were listed for sale on a marketplace. The following example creates an NFT that supports modifier tokens and also monitors the tokens held by a script address:

```
	"uses": {
		"tokens": [
			"own",
			"addr1wywukn5q6lxsa5uymffh2esuk8s8fel7a0tna63rdntgrysv0f3ms"
		]
	}
```

#### The renderer key

The idea behind the renderer key is to reduce code duplication in on-chain Javascript by moving the generative code part of the project into a single asset which is minted once in the policy. Each individual NFT within a project is then just a set of input parameters to the generative script - this totally removes the need to fill the metadata of every mint transaction with encoded HTML and Javascript, as is the case with many on-chain Javascript NFTs now. 

When a Smart NFT is encountered which specifies another asset as the renderer, the site rendering the NFT should look-up the referenced asset and render that - the rendering token will then be responsible for reading the appropriate information via the Javascript API below and changing its appearance and/or behaviour based on that. In its simplest form, the rendering token could simply read the current token fingerprint and use that to seed a random number generator - this would enable a generative project to mint NFTs without even changing anything in the metadata and still have the renderer change its appearance for each one. In practice though, it's probably cooler to put actual traits like "colour scheme" or "movement speed" into the metadata and then have the renderer change its behaviour based on that. 

Via the Javascript API, the rendering token will always receive the properties of the child token which specified it as its renderer. This means if you wish to use a renderer with a token which also evolves based on its own transaction history, you will need to specify both "renderer" and "transactions" keys within the child token, and within the renderer token you do not need to specify these keys. 

For example, to create a Smart NFT which is rendered by another token, and is also evolvable based on its own transaction history, the "uses" key would look like this:

```
	"uses": {
		"transactions": "own",
		"renderer": "asset1frc5wn889lcmj5y943mcn7tl8psk98mc480v3j"
	}
```

### The Javascript API

When an on-chain Javascript NFT is rendered which specifies any of the metadata options above, the website / dApp / wallet which creates the `<iframe>` sandbox, should inject the API defined here into that `<iframe>` sandbox. It is worth saying that the wallet dApp integration API from [CIP-0030](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030) should probably not be exposed inside the sandbox, to prevent cross-site-scripting attacks. 

The Paginate data type along with APIError and PaginateError are copied directly from [CIP-0030](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030) and these functions should operate in a similar manner to that API. 

It is recommended that the Smart NFT API not be injected for every NFT – only the ones which specify the relevant metadata - this is an important step so that it’s clear which NFTs require this additional API, and also to enable pre-loading and caching of the required data. We are aiming to expose only the specific data requested by the NFT in its metadata – in this CIP we are not providing a more general API for querying arbitrary data from the blockchain. 

*There is potentially a desire to provide a more open-ended interface to query arbitrary data from the blockchain – perhaps in the form of direct access to GraphQL – but that may follow in a later CIP – additional fields which could be added to the `uses: {}` metadata to enable the NFT to perform more complex queries on the blockchain.*

Although an asynchronous API is specified – so the data could be retrieved at the time when the NFT actually requests it – it is expected that in most instances the site which renders the NFT would gather the relevant transaction logs in advance, and inject them into the `<iframe>` sandbox at the point where the sandbox is created, so that the data is immediately available to the NFT without having to
perform an HTTP request. 

### `cardano.nft.fingerprint: String`

The fingerprint of the current token - in the case where we're rendering a child token, this will be the fingerprint of the child token. 

### `cardano.nft.metadata : Array`
 
The content of the 721 key from the metadata json from the mint transaction of the current NFT - if we are rendering on behalf of a child NFT, this will be the metadata from the child NFT.

### `cardano.nft.getTransactions( string which,  paginate: Paginate = undefined ) : Promise<Object>`

Errors: `APIError`, `PaginateError`

The argument to this function should be either an address, token fingerprint or the keyword “own”. It must match one of the ones specified via the `transactions` key in the new metadata mechanism detailed above.

This function will return a list of transaction hashes and metadata relating to the specified address or token. The list will be ordered by date with the newest transaction first, and will match the following format:

```
 {
	"transactions": [
		{ 
			"txHash":  "1507d1b15e5bd3c7827f1f0575eb0fdc3b26d69af0296a260c12d5c0c78239e0",
			"metadata": <raw metadata from blockchain>,
			"datum": <the datum from the UTXO holding the token, if set>
		},
		<more transactions here>
	],
	"fetched": "2022-05-01T22:39:03.369Z"
}
```
For simplicity, we do not include anything other than the txHash and the metadata – since any other relevant details about the transaction can always be encoded into the metadata, there is no need to over-complicate by including other transaction data like inputs, outputs or the date of the transaction etc. That is left for a potential future extension of the API to include more full GraphQL support.

### `cardano.nft.getTokens( string address, paginate: Paginate = undefined ) : Promise<Object>`

Errors: `APIError`, `PaginateError`

This function accepts either an address or the keyword “own” as its argument - it must match one of the ones specified via the the `tokens` key in the new metadata mechanism detailed above.

This function will return a list of the tokens held by the address specified in the argument, or held by the same stake key as the current token in the case of the “own” keyword. 

```
 {
	"tokens": [
		{ 
			"policyID": "781ab7667c5a53956faa09ca2614c4220350f361841a0424448f2f30",
			"assetName": "Life150",
			"fingerprint": "asset1frc5wn889lcmj5y943mcn7tl8psk98mc480v3j",
			"quantity": 1,
			"datum": <the datum from the UTXO holding the token, if set>
		},
		<more tokens here>
	],
	"fetched": "2022-05-01T22:39:03.369Z"
}
```

### `cardano.nft.getFileURL( string id = null, string fingerprint = null ) : Promise<String>`

Errors: `APIError`

This function provides access to the contents of files listed in the `files[]` array for this NFT - if the NFT is rendering on behalf of another NFT, the files arrays from both should be merged, with the child NFT items overwriting the rendering NFT, in the case of ID conflicts. 

The first argument specifies which entry from the files array should be retreived - if this argument is null, then the NFT's default image should be returned, which will typically come from the NFT's `image` metadata field rather than the files array. 
The second argument allows you to specify which token's files to search - it should either be the token itself (either the child token or the rendering token, in the case of tokens with a separate renderer). In the case where an NFT also uses the `tokens` part of this API, then the getFileURL() function will also allow you to specify any one of the fingerprints returned by the getTokens() query.

The URL returned by this function should be in a format that is accessible from within the `<iframe>` sandbox - perhaps using `window.URL.createObjectURL()` to generate a static URL from raw data if necessary. 

## Rationale: How does this CIP achieve its goals?

Currently the NFT sites which support on-chain Javascript NFTs do so by creating a sandboxed `<iframe>` into which they inject the HTML from the NFT’s metadata. From within this sandbox it is not possible to bring-in arbitrary data from external sources – everything must be contained within the NFT, or explicitly bought into the sandbox via an API.

This proposal suggests an addition to the 721 metadata key from [CIP-0025](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025), to enable an NFT to specify that it would like to receive a particular transaction history accessible to it from within the sandbox – thus defining it as a “Smart NFT”.

In tandem with the additional metadata, we also define a standard for the Javascript API which is provided to the NFT within the sandbox.

### The Smart NFT toolchain

This CIP now has a [reference implementation](https://clg.wtf/policy/smart-life) which consists of a [front-end React control](https://github.com/kieransimkin/SmartNFTPortal) which takes care of rendering an NFT - it creates the sandbox and exposes the CIP54 Javascript API to it. This works in tandem with a [backend library](https://github.com/kieransimkin/libcip54) which takes care of reading the necessary data from a dbsync instance and making it available for the front end control to render. 

There is also an [integrated development environment](https://nft-playground.dev/) made available to enable realtime experimentation and debugging of Smart NFTs without having to repeatedly mint new tokens. 

Furthermore, [a complete visual blockchain explorer](https://clg.wtf/) has been made available which utilises libcip54 and SmartNFTPortal and fully supports the reference implementation of this standard. 

The first CIP54 collection has been minted on mainnet under the policy ID `1eaf3b3ffb75ff27c43c512c23c6450b307f138281efb1d690b84652` and is [available to see here](https://clg.wtf/policy/smart-life). [A number of other instructive example NFTs](https://nft-playground.dev/examples) have also been provided as part of the NFT Playground website.

[Libcip54](https://github.com/kieransimkin/libcip54), [SmartNFTPortal](https://github.com/kieransimkin/SmartNFTPortal), [Cardano Looking Glass](https://github.com/kieransimkin/looking-glass) and the [NFT Playground](https://github.com/kieransimkin/cip54-playground) are all opensource - pull requests are welcome!

## Path to Active

### Acceptance Criteria

- [ ] Identify at least 1 pair of wallets, minting services, CLIs, or software utilities from separate providers which do at least 1 each of:
  - [ ] creating NFTs according to this specification
  - [ ] rendering NFTs according to this specification

### Implementation Plan

- [X] Provide a [reference](https://github.com/kieransimkin/libcip54) [implementation](https://github.com/kieransimkin/smartnftportal) of this scheme, which illustrates both:
  - [X] [a means of creating a "Smart NFT"](https://nft-playground.dev/)
  - [X] [a means of rendering it](https://clg.wtf/)
  - [ ] Update this specification to match the new features added in the reference implementation.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
