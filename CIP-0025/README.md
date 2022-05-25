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

### Structure

The structure allows for multiple token mints, also with different policies, in a single transaction.

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
          "name": <string>,
          "mediaType": <mime_type>,
          "src": <uri | array>,
          <other_properties>
        }],

        <other properties>
      }
    },
    "version": "1.0"
  }
}
```

The **`asset_name`** must be `UTF-8` encoded for the key in the metadata map and the actual NFT. This is true for version `1.0`, future versions will use the `hex` encoding for **`asset_name`**.

The **`image`** and **`name`** property are marked as required. **`image`** should be an URI pointing to a resource with mime type `image/*` used as thumbnail or as actual link if the NFT is an image (ideally <= 1MB).

The **`description`** property is optional.

The **`mediaType`** and **`files`** properties are optional.<br /> **`mediaType`** is however required inside **`files`**. The **`src`** property inside **`files`** is an URI pointing to a resource of this mime type. If the mime type is `image/*`, **`mediaType`** points to the same image, like the on in the **`image`** property, but in an higher resolution.

The **`version`** property is also optional. If not specified the version is `1.0`. It will become mandatory in future versions if needed.

This structure really just defines the basis. New properties and standards can be defined later on for varies uses cases. That's why there is an "other properties" tag.

The retrieval of the metadata should be the same for all however.

Optional fields allow to save space in the blockchain. Consequently the minimal structure for a single token is:

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

To keep NFT metadata compatible with changes coming up in the future, we use the **`version`** property. Version `1.0` is used in the current metadata structure of this CIP.
Version `2.0` will introduce [schema.org](https://schema.org).

## References

- Mime type: https://tools.ietf.org/html/rfc6838.
- CIP about reserved labels: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010
- EIP-721: https://eips.ethereum.org/EIPS/eip-721
- URI: https://tools.ietf.org/html/rfc3986, https://tools.ietf.org/html/rfc2397

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
