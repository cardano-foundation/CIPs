---
CIP: 48?
Title: 721 References and Payloads
Authors: Jack (ada9000, https://forum.cardano.org/u/jack7e/, @ada9000_ twitter)
Comments-URI: https://forum.cardano.org/t/cip-extended-721/
Status: Draft
Type: Informational
Created: 2022-04-22 (updated 2022-09-22)
---

## Important note

This CIP mentions the `ext` json key defined by [CIP49](https://github.com/cardano-foundation/CIPs/pull/343/files) which is an outcome of work on CIP48.

# Abstract

- This standard proposes a method to allow NFT assets to reference other onchain data.
- This would allow users of 721 metadata to increase or reduce the amount of data an NFT asset uses.

# Motivation

- Large token mints that duplicated data could be dramatically reduced in size by pointing to one transaction payload that contains a ‘boilerplate’ structure.
- 16kB is the upper limit of data in each transaction but If a user wanted more there is no alternative than to store that data off-chain using an external service such as ipfs.
- There is no current mechanism to reduce duplicated metadata
- NFT assets are restricted by there own metadata scope, optional references would prevent this restriction
- There is currently no way to reference on chain data stored in a different policy

# Specification

### **Inside the 721 metadata JSON**

| reserved | description                                            | scope                     |
| -------- | ------------------------------------------------------ | ------------------------- |
| refs     | references tag, defines where to find the onchain data | Inside `<asset_name>` tag |
| p        | contains raw data (on chain data).                     | Inside `<policy_id>` tag  |

### **The `refs` tag**

Contains the `name`, `mediaType`, `src` tags (and the optional `type` tag)

- `name` (string) is the references name (similar usage to name in the current `files` tag)
- `mediaType` (string) defines the mime type for the data referenced in `src`
  - is a string
- `src` (string array) is an **ordered** array of references.
  - The order is that of which the data will be parsed. For example `["1","3","2"]` will result in payload `"1"` being the start of the data, followed by payload `"3"` and ending with payload `"2"`.

### **Optional `type` tag for `refs`**

The default CIP-48 behavior is to assume the assets parent `<policy_id>` contains all the payloads.

Optionally we define `type` and two options `policy` and `txhash`. To allow for non-default behavior

- `policy`
  - Defines an external policy (instead of the default behavior of using the parent policy)
  - example
    ```json
      "refs": [
        {
          "name": "...",
          "mediaType": "...",
          "type": {
            "policy": "<some_external_policy>"
          }
        }
      ]
    ```
- `txhash`
  - Defines a specific transaction hash (instead of the default behavior of using the parent policy)
  - example
    ```json
      "refs": [
        {
          "name": "...",
          "mediaType": "...",
          "type": {
            "txhash": "<some_mint_txhash>"
          }
        }
      ]
    ```
  - `txhash` is faster than parsing all transactions in a given policy.
  - `txhash` can dramatically reduce onchain data usage if duplicated data is referenced here _(however, the bytes required to define the reference would have to be less than the reference data itself)_

### **The payload `p` tag**

- Defined within the `<policy_id>` scope
- contains payload reference names followed by a string array of payload data
- example
  ```json
    "p":
      {
        "1": ["1 is a valid payload"],
        "payloadA": ["a...64","b...64"], //a string has a max length of 64 characters
        "payloadB": ["I'm found by referencing payloadB"],
      }
  ```

## General structure

```json
{
  "721": {
    "ext": ["cip48"], // tells 'user' cip48 is in use within the metadata
    "<policy_id>": {
      "<asset_name>": {
        "project": "<string>",
        "name": "<string>",
        "image": "<ref_name | uri | array>" // image is defined by refs or a uri
        // references
        "refs": [
          {
            "name": "<ref_name>",
            "mediaType": "text/plain",
            "src": ["<payload_id>", "<payload_id>"] // array of required payload ids (ordered)
          }
        ]
      },
      // payload
      "p": {
        "<payload_id>": ["<data>", "<data>"], // payload0
        "<payload_id>": ["<data>"] // payload1
      }
    }
  }
}
```

## Notes

- CIP25 currently defines a 'required' image tag.
  - CIP48 alters the use of image. Requiring the 'user' to first check if the image string matches any reference names. Then to fallback on the default behavior.
    - example, in which the image is found by referring to payloads.
    ```json
    {
      "image":"myImageNFT"
      "refs":[
        {
          "name": "myImageNFT"
          "mediaType":"image/svg+xml;utf8"
          "src": ["refToPayloadA", "refToPayloadB"]
        }
      ]
    }
    ```
  - The `files` tag can still be used to describe higher resolution files images, though it should also adopt the same usage of `<ref_name>` described for `image` tag in the aforementioned note
  - The `image` tag can still be used as a thumbnail if required.
  - Not all NFT's require an image (CIP 25 is confusing called the `NFT metadata standard?`) TODO: review

# Example

Mint transaction 1

```json
{
  "721": {
    "ext": ["cip48"],
    "0000000000000000000000000000000000000000000000000000000A": {
      "NFT0": {
        "project": "CIP48 Example",
        "name": "NFT0",
        // references
        "refs": [
          {
            "name": "NFT0",
            "mediaType": "text/plain",
            "src": ["0", "2"]
          }
        ]
      },
      // payload
      "p": {
        "0": ["Hello"],
        "1": ["Goodbye"]
      }
    }
  }
}
```

Mint transaction 2

```json
{
  "721": {
    "ext": ["cip48"],
    "0000000000000000000000000000000000000000000000000000000A": {
      "NFT1": {
        "project": "CIP48 Example",
        "name": "NFT1",
        // references
        "refs": [
          {
            "name": "NFT1",
            "mediaType": "text/plain",
            "src": ["0", "3"]
          }
        ]
      },
      // payload
      "p": {
        "2": ["World"],
        "3": ["Moon"]
      }
    }
  }
}
```

### Pseudo code walk through using the above example (using default behavior)

1. Find all transactions for the given `<policy_id>`

   - `found 2 mint transcations`

2. Check the **ext** tag for **cip48**

   - `found cip48` we now know the metadata contains references and payloads

3. Iterate over each transaction. If a payload is found append that to an map or some data structure

   - found 4 payloads
   - ```js
     payloads = { 0: "Hello", 1: "Goodbye", 2: "World", 3: "Moon" };
     ```

4. Find all `refs` (references) for the `<asset_name>` we use NFT0. Then build the data in the order defined by the `src` array.

   - found 2 references
   - ```js
     nft0_refs = ["0", "2"];
     nft0_data = "HelloWorld";
     ```

5. use the mediaType (mimetype) to determine the data.
   - mediaType = "test/plain"
   - NFT0 contains text "HelloWorld"

# Backwards compatibility

Handled via the use of the `"ext"` tag defined in CIP-48.

# Further considerations

- Later we may want to use different reference types, maybe even plutus contract references. Due to this I have defined the `type` tag inside the `refs` (references) tag.
- `p` is used instead of **payload** to reduce bytes. Specifically `p` is not used within the `<asset_name>` tag therefore readability is less of a priority than data size. Unlike `refs` which is defined in the `<asset_name>` tag
- JSON is kept over CBOR or alternatives as this CIP is encapsulated in the 721 metadatum tag and JSON is easier for developers to adopt

### Duplicate data

There could be issues with duplicate payloads. To solve the payload defined in the most recently minted tx takes priority.
