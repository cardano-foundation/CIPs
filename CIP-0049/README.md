---
CIP: 49?
Title: 721 Metatdatum extenstion tag
Authors: Jack ([9000] pool, https://forum.cardano.org/u/jack7e/, @ada9000_ twitter)
Comments-URI: https://github.com/cardano-foundation/CIPs/pull/249
Status: Draft
Type: Informational
Created: 2022-09-28
---

# Abstract

This standard proposes a method to define optional extensions the 721 metadatum standard. Allowing users to know what to expect in the metadata.

# Motivation

- Cardano NFT Metadata parsing is becoming complex due to optional metadata json tags.
- If Cardano NFT's want to develop we need to define what's inside the metadata to avoid conflicts with custom optional tags and tags defined in new CIPs.

# Specification

- The `ext` tag is added within the `"721"` metadatum tag
- The `ext` tag should be lowercase. When parsing nft metadata the developer will use a to lowercase function on all elements in the `ext` array

```json
{
   "721":{
      "ext": <array>
      "<policy_id>":{
         "<asset_name>": {
            "name": <string>,
            "image": <uri | array>
         }
      }
   }
}
```

# Example usage

The theoretical cipX in this example defines a script tag that must be present. To implement this CIP in our 721 metadatum JSON we simply add CIPX to the `"ext"` array.

```json
{
   "721":{
      "ext": ["cipX"]
      "<policy_id>":{
         "script":"<script_policy_id>"
         "<asset_name>": {
            "name": <string>,
            "image": <uri | array>
         }
      }
   }
}
```

Where cipX defines some property for the **JSON**. In this particular example cipX is a fictional CIP that requires the nft to contain a `"script"` tag with a `"<script_policy_id>"`.
