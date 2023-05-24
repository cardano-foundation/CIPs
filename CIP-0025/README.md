---
CIP: 25
Title: Media NFT Metadata Standard
Authors: Alessandro Konrad <alessandro.konrad@live.de>, Smaug <smaug@pool.pm>
Comments-URI:
Status: Active
Type: Informational
Created: 2021-04-08
Post-History: https://forum.cardano.org/t/cip-nft-metadata-standard/45687 and https://www.reddit.com/r/CardanoDevelopers/comments/mkhlv8/nft_metadata_standard/
License: CC-BY-4.0
---

## Abstract

This proposal defines an Media NFT Metadata Standard for Native Tokens.

## Motivation

Tokens on Cardano are a part of the ledger. Unlike on Ethereum, where metadata can be attached to a token through a smart contract, this isn't possible on Cardano because tokens are native and Cardano uses a UTxO ledger, which makes it hard to directly attach metadata to a token.
So the link to the metadata needs to be established differently.
Cardano has the ability to send metadata in a transaction, that's the way we can create a link between a token and the metadata. To make the link unique, the metadata should be appended to the same transaction, where the token forge happens:

> Given a token in a EUTXOma ledger, we can ask “where did this token come from?” Since tokens
> are always created in specific forging operations, we can always trace them back through their
> transaction graph to their origin.

(Section 4 in the paper: https://iohk.io/en/research/library/papers/utxomautxo-with-multi-asset-support/)

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
	-  If an inline base64-encoded image will be used, the data must be prepended with a valid `data:<mime_type>;base64` prefix as specified by the [data URL scheme standard](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs) to indicate the image is an inline data object
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
