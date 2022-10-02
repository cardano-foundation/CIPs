---
CIP: 49?
Title: 721 Metatdatum extenstion tag
Authors: Jack ([9000] pool, https://forum.cardano.org/u/jack7e/, @ada9000_ twitter)
Comments-URI: https://forum.cardano.org/t/cip-extended-721/
Status: Draft
Type: Informational
Created: 2022-09-28
---

# Abstract

This standard proposes a method to extend the 721 metadatum standard bypassing the restrictions created by the version tag.

# Motivation

- NFT's on Cardano are static and rely on a version tag change to implement new features.
- The version tag is not very modular and restricts innovation.

# Specification

- The standard 721 metadatum tag is used.
- The version tag is **deprecated** at it's current `version:2` by the `ext` keyword.
  - To use the version 1 tag I suggest `"ext":["v1"]`
  - To use the version 2 tag I suggest `"ext":["v2"]`
  - This might seem odd at first but going foward instead of adding version 3 we just define the CIP as an optional `ext` array element. For example CIPX with version 2 would be `"ext":["v2","cipx"]`
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
