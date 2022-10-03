---
CIP: 25
Title: NFT Metadata Standard
Authors: Alessandro Konrad <alessandro.konrad@live.de>, Smaug <smaug@pool.pm>
Comments-URI:
Status: Active
Type: Informational
Created: 2021-04-08
Post-History: https://forum.cardano.org/t/cip-nft-metadata-standard/45687 and https://www.reddit.com/r/CardanoDevelopers/comments/mkhlv8/nft_metadata_standard/
License: CC-BY-4.0
---

## Abstract

This proposal defines an NFT Metadata Standard for Native Tokens.

## Motivation

Tokens on Cardano are a part of the ledger. Unlike on Ethereum, where metadata can be attached to a token through a smart contract, this isn't possible on Cardano because tokens are native and Cardano uses a UTxO ledger, which makes it hard to directly attach metadata to a token.
So the link to the metadata needs to be established differently.
Cardano has the ability to send metadata in a transaction, that's the way we can create a link between a token and the metadata. To make the link unique, the metadata should be appended to the same transaction, where the token forge happens:

> Given a token in a EUTXOma ledger, we can ask “where did this token come from?” Since tokens
> are always created in specific forging operations, we can always trace them back through their
> transaction graph to their origin.

(Section 4.1 in the paper: https://hydra.iohk.io/build/5400786/download/1/eutxoma.pdf)

## Considerations

That being said, we have unique metadata link to a token and can always prove that with 100% certainty. No one else can manipulate the link except if the policy allows it to ([update mechanism](#update-metadata-link-for-a-specific-token)).

## Specification

This is the registered `transaction_metadatum_label` value

| transaction_metadatum_label | description  |
| --------------------------- | ------------ |
| 721                         | NFT Metadata |

### General structure

The structure allows for multiple token mints, also with different policies, in a single transaction.

```
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "name": <string>,

        "image": <uri | array>,
        "mediaType": image/<mime_sub_type>,

        "description": <string | array>,

        "files": [{
          "name": <string>,
          "mediaType": <mime_type>,
          "src": <uri | array>,
          <other_properties>
        }],

        <other properties>
      }
    },
    "version": <version_id>
  }
}
```

### CDDL

[Version 1](./cddl/version_1.cddl)\
[Version 2](./cddl/version_2.cddl)

- In version `1` the **`asset_name`** must be `utf-8` encoded and in text format for the key in the metadata map. In version `2` the the raw bytes of the **`asset_name`** are used.

- In version `1` the **`policy_id`** must be in text format for the key in the metadata map. In version `2` the the raw bytes of the **`policy_id`** are used.

- The  **`name`** property is marked as required.
- The **`image`** property is required and must be a valid [Uniform Resource Identifier (URI)](https://www.rfc-editor.org/rfc/rfc3986) pointing to a resource with mime type `image/*`.  Note that this resource is used as thumbnail or the actual link if the NFT is an image (ideally <= 1MB). If the string representing the resource location is >64 characters, an array may be used in place of a simple JSON string type, which viewers will automatically concatenate to create a single URI.
	- Please note that if distributed storage systems like IPFS or Arweave are used it is required to use a URI containing the respective scheme (e.g., `ipfs://` or `ar://`) and not merely the content identifier (CID) as NFT viewers may not be able to locate the file.
		- Valid identifiers would include:
			- `"https://cardano.org/favicon-32x32.png"`
			- `"ipfs://QmbQDvKJeo2NgGcGdnUiUFibTzuKNK5Uij7jzmK8ZccmWp"`
			- `["ipfs://", "QmbQDvKJeo2NgGcGdnUiUFibTzuKNK5Uij7jzmK8ZccmWp"]`
		- Invalid identifiers would include:
			- `"cardano.org/favicon-32x32.png"`
			- `"QmbQDvKJeo2NgGcGdnUiUFibTzuKNK5Uij7jzmK8ZccmWp"`
			- `["Qm", "bQDvKJeo2NgGcGdnUiUFibTzuKNK5Uij7jzmK8ZccmWp"]`
	-  If an inline base64-encoded image will be used, the data must be prepended with a valid `data:<mime_type>;base64` prefix as specified by the [data URL scheme standard](https://datatracker.ietf.org/doc/html/rfc2397) to indicate the image is an inline data object
		- For example, the [Cardano logo](https://cardano.org/) would be `data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjUwIDI1MS4xNyI+PGcgaWQ9IkxheWVyXzIiIGRhdGEtbmFtZT0iTGF5ZXIgMiI+PGcgaWQ9IkxheWVyXzEtMiIgZGF0YS1uYW1lPSJMYXllciAxIj48cGF0aCBkPSJNNzQuNDksMTI0LjY0QTE4LjM0LDE4LjM0LDAsMCwwLDkxLjczLDE0NGwxLDBhMTguMywxOC4zLDAsMSwwLTE4LjI5LTE5LjM1WiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik02LjI1LDEyMGE1LjkxLDUuOTEsMCwxLDAsNS41Nyw2LjI0QTUuOSw1LjksMCwwLDAsNi4yNSwxMjBaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTczLjMzLDE4LjQzYTUuOTIsNS45MiwwLDEsMC04LTIuNjJBNS45Myw1LjkzLDAsMCwwLDczLjMzLDE4LjQzWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik05MS45LDUwLjgxYTkuMTQsOS4xNCwwLDEsMC0xMi4yOC00LjA1QTkuMTQsOS4xNCwwLDAsMCw5MS45LDUwLjgxWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0yOS40MSw3My4wOGE3LjUzLDcuNTMsMCwxLDAtMi4xNi0xMC40MkE3LjUzLDcuNTMsMCwwLDAsMjkuNDEsNzMuMDhaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTQwLjU0LDExNi42N2E5LjE0LDkuMTQsMCwxLDAsOC42MSw5LjY1QTkuMTUsOS4xNSwwLDAsMCw0MC41NCwxMTYuNjdaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTMwLjQxLDE3OC4xMmE3LjUzLDcuNTMsMCwxLDAsMTAuMTIsMy4zM0E3LjUzLDcuNTMsMCwwLDAsMzAuNDEsMTc4LjEyWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik02NS45NCw5Ny43OGExMC43NiwxMC43NiwwLDEsMC0zLjEtMTQuOUExMC43NSwxMC43NSwwLDAsMCw2NS45NCw5Ny43OFoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTc4LjY2LDUwLjA5QTkuMTUsOS4xNSwwLDEsMCwxNzYsMzcuNDIsOS4xNCw5LjE0LDAsMCwwLDE3OC42Niw1MC4wOVoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTk3LjQyLDE3LjgxYTUuOTIsNS45MiwwLDEsMC0xLjcxLTguMTlBNS45Miw1LjkyLDAsMCwwLDE5Ny40MiwxNy44MVoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTgwLjEsMTA3LjIyQTE4LjMsMTguMywwLDEsMCwxNzgsMTQzLjc3Yy4zNSwwLC43MSwwLDEuMDYsMGExOC4zLDE4LjMsMCwwLDAsMTMuNjQtMzAuNDlBMTguMDgsMTguMDgsMCwwLDAsMTgwLjEsMTA3LjIyWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik05Ny45MSw5Ni41MWExOC4yMywxOC4yMywwLDAsMCwxNi4zNiwxMC4wN0ExOC4zMSwxOC4zMSwwLDAsMCwxMzAuNjEsODAsMTguMjQsMTguMjQsMCwwLDAsMTE0LjI1LDcwLDE4LjMxLDE4LjMxLDAsMCwwLDk3LjkxLDk2LjUxWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0yNDEuNDEsNzMuMDZhNy41Myw3LjUzLDAsMSwwLTEwLjEyLTMuMzRBNy41NCw3LjU0LDAsMCwwLDI0MS40MSw3My4wNloiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTk1LDc4Ljg5YTEwLjc2LDEwLjc2LDAsMSwwLDE0LjQ1LDQuNzdBMTAuNzUsMTAuNzUsMCwwLDAsMTk1LDc4Ljg5WiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0xMzUuMjIsMTUuMDVhNy41Myw3LjUzLDAsMSwwLTcuMDktNy45NEE3LjUzLDcuNTMsMCwwLDAsMTM1LjIyLDE1LjA1WiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0xMzUuMTQsNjIuNDRBMTAuNzYsMTAuNzYsMCwxLDAsMTI1LDUxLjA4LDEwLjc3LDEwLjc3LDAsMCwwLDEzNS4xNCw2Mi40NFoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNNzYuODQsMTcyLjI4YTEwLjc2LDEwLjc2LDAsMSwwLTE0LjQ1LTQuNzZBMTAuNzYsMTAuNzYsMCwwLDAsNzYuODQsMTcyLjI4WiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0xNDIuMDksNzguMTRhMTguMywxOC4zLDAsMSwwLDE1LjMzLTguMjdBMTguMzIsMTguMzIsMCwwLDAsMTQyLjA5LDc4LjE0WiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0xNzMuOTEsMTU0LjY3YTE4LjMsMTguMywwLDEsMC0xNi4zNCwyNi41NCwxOC41LDE4LjUsMCwwLDAsOC4yNC0yQTE4LjMxLDE4LjMxLDAsMCwwLDE3My45MSwxNTQuNjdaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTIwNS44OSwxNTMuMzlhMTAuNzYsMTAuNzYsMCwxLDAsMy4wOSwxNC45QTEwLjc4LDEwLjc4LDAsMCwwLDIwNS44OSwxNTMuMzlaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTI0MC45MywxMjUuOWE5LjE0LDkuMTQsMCwxLDAtOS42NSw4LjYxQTkuMTUsOS4xNSwwLDAsMCwyNDAuOTMsMTI1LjlaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTI2Ni4yNSwxMTkuMzlhNS45Miw1LjkyLDAsMSwwLDUuNTcsNi4yNUE1LjkzLDUuOTMsMCwwLDAsMjY2LjI1LDExOS4zOVoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMjQyLjQxLDE3OC4wOWE3LjUzLDcuNTMsMCwxLDAsMi4xNywxMC40M0E3LjUzLDcuNTMsMCwwLDAsMjQyLjQxLDE3OC4wOVoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNNzQuNDEsMjMzLjM2YTUuOTIsNS45MiwwLDEsMCwxLjcsOC4yQTUuOTIsNS45MiwwLDAsMCw3NC40MSwyMzMuMzZaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTE5OC40OSwyMzIuNzRhNS45Miw1LjkyLDAsMSwwLDcuOTUsMi42MkE1LjkxLDUuOTEsMCwwLDAsMTk4LjQ5LDIzMi43NFoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTI5LjczLDE3M2ExOC4zLDE4LjMsMCwxLDAtMTUuMzIsOC4yN0ExOC4yMSwxOC4yMSwwLDAsMCwxMjkuNzMsMTczWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik05My4xNiwyMDEuMDlhOS4xNCw5LjE0LDAsMSwwLDIuNjQsMTIuNjZBOS4xNSw5LjE1LDAsMCwwLDkzLjE2LDIwMS4wOVoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTM1LjgzLDIzNi4xMmE3LjUzLDcuNTMsMCwxLDAsNy4wOSw3Ljk1QTcuNTMsNy41MywwLDAsMCwxMzUuODMsMjM2LjEyWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0xMzUuOTEsMTg4Ljc0QTEwLjc2LDEwLjc2LDAsMSwwLDE0NiwyMDAuMDksMTAuNzUsMTAuNzUsMCwwLDAsMTM1LjkxLDE4OC43NFoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMTc5LjkyLDIwMC4zNmE5LjE1LDkuMTUsMCwxLDAsMTIuMjksNEE5LjEzLDkuMTMsMCwwLDAsMTc5LjkyLDIwMC4zNloiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNMzgxLjg2LDgyLjM1YzE3LjcyLDAsMzAuMTMsOS43NCwzMC4xMywyNy44Mkg0MzUuMmMwLTMxLjcyLTIzLjM5LTQ3LTUzLjY5LTQ3LTM3LjIyLDAtNTguODQsMjAuMjEtNTguODQsNjIuOTIsMCw0My43NywyMS42Miw2Mi45MSw1OC44NCw2Mi45MSwzMC42NiwwLDUzLjY5LTE0Ljg4LDUzLjY5LTQ2LjYxSDQxMi44N2MwLDE3LjcyLTEyLjIzLDI3LjQ3LTMxLDI3LjQ3LTI0LjY0LDAtMzYtMTMuNjUtMzYtNDJ2LTMuNTRDMzQ1Ljg5LDk2LjUyLDM1Ny40LDgyLjM1LDM4MS44Niw4Mi4zNVoiIGZpbGw9IiMwMDMzYWQiLz48cGF0aCBkPSJNNDk2LjU3LDY1LjMzLDQ0OS4yNSwxODYuOTFoMjMuNGw5Ljc0LTI2LjQxSDUzOEw1NDgsMTg2LjkxaDI0LjQ2TDUyNS4xMSw2NS4zM1ptLTcuMDksNzZMNTAxLjg5LDEwOGMyLjQ4LTYuNTUsNi45MS0yMC43Myw3LjgtMjMuMjFoLjg4Yy44OSwyLjQ4LDUuMzIsMTYuODMsNy44LDIzLjIxbDEyLjQsMzMuMzJaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTY5OSwxMDIuMTljMC0yMi41LTEyLjk0LTM2Ljg2LTM5LjctMzYuODZINTk1LjE0VjE4Ni45MWgyMi42OXYtNDdoMzcuNzRsMjMsNDdoMjQuODFsLTI2LTUwLjUxQzY5MS43MywxMzAuNzMsNjk5LDExOC42OCw2OTksMTAyLjE5Wk02NTcuNTIsMTIwLjhINjE3LjgzVjg0LjY1aDM5LjY5YzEyLjIzLDAsMTguNjEsNi41NiwxOC42MSwxNy41NEM2NzYuMTMsMTEzLjcyLDY2OS4yMiwxMjAuOCw2NTcuNTIsMTIwLjhaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTc3OC41OCw2NS4zM0g3MzBWMTg2LjkxaDQ4LjU2YzM2LjY4LDAsNTktMTkuMTQsNTktNjAuNzlTODE1LjI2LDY1LjMzLDc3OC41OCw2NS4zM1ptMzUuOCw2Mi41NmMtLjE4LDI2LjU5LTEyLjc2LDM5LjctMzUuOCwzOS43SDc1Mi43MVY4NC42NWgyNS44N2MyMywwLDM1LjgsMTMuMTIsMzUuOCwzOS43WiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik04OTcsNjUuMzMsODQ5LjY2LDE4Ni45MWgyMy4zOWw5Ljc1LTI2LjQxaDU1LjY1bDkuOTIsMjYuNDFoMjQuNDZMOTI1LjUxLDY1LjMzWm0tNy4wOSw3Nkw5MDIuMywxMDhjMi40OC02LjU1LDYuOTEtMjAuNzMsNy44LTIzLjIxSDkxMWMuODgsMi40OCw1LjMyLDE2LjgzLDcuOCwyMy4yMWwxMi40LDMzLjMyWiIgZmlsbD0iIzAwMzNhZCIvPjxwYXRoIGQ9Ik0xMDc2LjU0LDEzNy42NGMwLDIuMy4zNSw4LjUuMzUsOS41N2wtLjg4LjM1Yy0uNTMtLjctNC4wOC02LjkxLTYtOS43NGwtNTIuODEtNzIuNDlIOTk1LjU1VjE4Ni45MWgyMS44VjExNC4wN2MwLTMtLjM2LTguODYtLjM2LTkuNzVsLjg5LS41M2MuNTMuNzEsMy4xOSw1Ljg1LDYsOS45M2w1My4xNyw3My4xOWgyMS4yNlY2NS4zM2gtMjEuNzl2NzIuMzFaIiBmaWxsPSIjMDAzM2FkIi8+PHBhdGggZD0iTTExODguNjgsNjMuMjFjLTM4LjEsMC02MS4xNCwyMC4yLTYxLjE0LDYyLjkxczIzLDYyLjkxLDYxLjE0LDYyLjkxLDYxLjMyLTIwLjIsNjEuMzItNjIuOTFTMTIyNi43OCw2My4yMSwxMTg4LjY4LDYzLjIxWm0zOC4xLDY0Ljg2YzAsMjcuODItMTMuMjksNDEuODItMzguMSw0MS44Mi0yNC42MywwLTM3LjkyLTE0LTM3LjkyLTQxLjgydi0zLjcyYzAtMjcuODMsMTMuNDctNDIsMzcuOTItNDIsMjQuNjQsMCwzOC4xLDE0LjE3LDM4LjEsNDJaIiBmaWxsPSIjMDAzM2FkIi8+PC9nPjwvZz48L3N2Zz4=`
	- See [the OpenSea "IPFS and Arweave URIs" section in their reference guide](https://docs.opensea.io/docs/metadata-standards#ipfs-and-arweave-uris) for more helpful information on the topic.

- The **`description`** property is optional.

- The **`mediaType`** and **`files`** properties are optional.<br /> **`mediaType`** is however required inside **`files`**. The **`src`** property inside **`files`** is an URI pointing to a resource of this mime type. If the mime type is `image/*`, **`mediaType`** points to the same image, like the on in the **`image`** property, but in an higher resolution.

- The **`version`** property is also optional. If not specified the version is `1`. It will become mandatory in future versions if needed.

- This structure really just defines the basis. New properties and standards can be defined later on for varies uses cases. That's why there is an "other properties" tag.

- The retrieval of the metadata should be the same for all however.

Optional fields allow to save space in the blockchain. Consequently the minimal structure for a single token is:

#### Version 1

```
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "name": <string>,
        "image": <uri | array>
      }
    }
  }
}
```

#### Version 2

```
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "name": <string>,
        "image": <uri | array>
      }
    },
    "version": 2
  }
}
```

### Retrieve valid metadata for a specific token

As mentioned above this metadata structure allows to have either one token or multiple tokens with also different policies in a single mint transaction. A third party tool can then fetch the token metadata seamlessly. It doesn't matter if the metadata includes just one token or multiple. The proceedure for the third party is always the same:

1. Find the latest mint transaction with the label 721 in the metadata of the specific token
2. Lookup the 721 key
3. Lookup the Policy Id of the token
4. Lookup the Asset name of the token
5. You end up with the correct metadata for the token

### Update metadata link for a specific token

Using the latest mint transaction with the label 721 as valid metadata for a token allows to update the metadata link of this token. As soon as a new mint transaction is occurring including metadata with the label 721, the metadata link is considered updated and the new metadata should be used. This is only possible if the policy allows to mint or burn the same token again.

## Backward Compatibility

To keep NFT metadata compatible with changes coming up in the future, we use the **`version`** property.
A future version will introduce [schema.org](https://schema.org).

## References

- Mime type: https://tools.ietf.org/html/rfc6838.
- CIP about reserved labels: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010
- EIP-721: https://eips.ethereum.org/EIPS/eip-721
- URI: https://tools.ietf.org/html/rfc3986, https://tools.ietf.org/html/rfc2397

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
