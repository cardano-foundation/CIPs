---
CIP: 124
Title: Extend token metadata for translations
Category: Metadata
Status: Proposed
Authors:
  - Vito Melchionna <info@granadapool.com>
  - Aaron Schmid <aaron@entropilabs.io>
  - Carolina Isler @LaPetiteADA <lapetiteada@granadapool.com>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/488
Created: 2023-03-19
License: CC-BY-4.0
---

## Abstract

This proposal defines an additional property to the metadata standard for tokens (NFTs and FTs) to support text localization.

## Motivation: why is this CIP necessary?

Current token metadata only supports a single hardcoded language (mostly English), which limits the accessibility to a certain culture. To get closer to mass adoption, we need to bring down language barriers by extending the current standard to support translations. This is especially relevant for games, metaverse solutions, and RealFi use cases of NFTs.

## Specification

This proposal follows the same specifications as [CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025) (all versions).

The name of a culture consists of its [[ISO-639]](https://www.iso.org/standard/4767.html) language code with small letters and its [[ISO-3166]](https://www.iso.org/standard/63545.html) country/region code with capital letter separated by a dash "-". For instance, this proposal was written in "en-US": English with the US culture.

This convention is compatible with most operative systems (Linux and Windows) and widely used translation software.

### General structure

The extended JSON metadata standard (CIP-25) allows flexible off- and on-chain string tranlations:

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
            "src": "<uri | array>"
          }],

          <other properties>

          "strings": {
              "de-CH": {
                "name": <string in Swiss German>,
                "image": <localized uri for Swiss German | array>,
                "description": <string in Swiss German | array>
                 <other localized properties>
              },
              "it-IT": {
                "name": <string in Italian>,
                "image": <localized uri for Italian | array>,
                "description": <string in Italian | array>
                <other localized properties>
              },

              <other languages and cultures>
          }
        },
      },
      "version": <version_id>,

      <information about collection>

      "strings": {
              "de-CH": {
                 <localized information about collection in de-CH>
              },
              "it-IT": {
                 <localized information about collection in it-IT>
              },

              <other languages and cultures>
      }
  }
}
```

### CDDL

Extended versions of CIP-25

[Version 1](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0124/cddl/version_1.cddl)

[Version 2](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0124/cddl/version_2.cddl)

- The new `strings` properties are optional, but if included, they must be valid JSON objects.
  - The JSON object's keys and structure should match the same keys defined on the `policy_id` level for collection-specific information, or on the `asset_name` level for asset-specific properties, depending which attributes have translations. By doing so, the developer experience to access the localized strings significantly improves.

## Rationale: how does this CIP achieve its goals?

### Access valid localized properties of a token's metadata

After fetching the policy's metadata, the procedure stays the same when looking up CIP-25 properties. However, to find culture-based translations, developers have to access the `strings` property located at the same level of the wanted information.

In case of the ´policy_id´ level (collections):

1. Lookup the 721 key
2. Lookup the Policy Id of the token
3. Lookup the strings property
4. Lookup for the culture
5. You end up with the translated metadata for the policy

In case of the ´asset_name´ level (specific assets):

1. Lookup the 721 key
2. Lookup the Policy Id of the token
3. Lookup the Asset name of the token
4. Lookup the strings property
5. Lookup for the culture
6. You end up with the translated metadata for the specific asset

> **Note**
> The metadata's size is a constraint that should be considered as it could eventually push the boundaries of Cardano's transaction limits and scalability in terms of memory resources. The translations under the "strings" keys can be stored off-chain on an IPFS server using the proposed JSON structure. Then, the localized texts will be accessible through an URL, similarly to the "image" property.

### Code example (JavaScript/TypeScript)

To access the localized strings from the fetched metadata for a native asset, we can simply access the JSON properties from the front end by using the user's selected culture:

```
const response = await fetch(`${<BASE_URL>}/policyId/${<policyId>}`);

const metadata = response.json();
const policy = metadata["721"][<policy_id>];

// This check determines if the translations are stored off-chain on an IPFS url
function isValidURL(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
}

function fetchTranslationStrings(url) {
  const response = await fetch(url);
  const translations = await response.json();
  return translations || null;
}

function getPolicyString(policy, key, culture="en") {
    // translations are stored off-chain
    if(isValidURL(policy["strings"])) {
      const translations = fetchTranslationStrings(policy["strings"]);
      if(translations) {
        return translations[culture][key] || policy[key]; // default value (not localized)
      }
    }

    // translations are stored on-chain
    return policy["strings"][culture][key]
        ? policy["strings"][culture][key]
        : policy[key]; // default value (not localized)
}

function getAssetString(policy, asset, key, culture="en") {
    // translations are stored off-chain
    if(isValidURL(policy[asset]["strings"])) {
      const translations = fetchTranslationStrings(policy[asset]["strings"]);
      if(translations) {
        return translations[culture][key] || policy[asset][key]; // default value (not localized)
      }
    }

    // translations are stored on-chain
    return policy[asset]["strings"][culture][key]
        ? policy[asset]["strings"][culture][key]
        : policy[asset][key]; // default value (not localized)
}

console.log(`Default policy property: ${getPolicyString(policy, <policy_property>)}`);
console.log(`Localized policy property: ${getPolicyString(policy, <policy_property>, "it-IT")}`);
console.log(`Default asset name: ${getAssetString(policy, <asset_name>, "name")}`);
console.log(`Localized asset name: ${getAssetString(policy, <asset_name>, "name", "de-CH")}`);
```

### Update metadata and translations

Following the specifications stated on CIP-25, the strings can be only changed if the policy allows it.

### Backward Compatibility

This metadata standard extension is backward compatible and it doesn't affect applications using the current standard. Dapps implementing the proposed extended standard can also default on the legacy values if the localized strings are not available on an asset.

## Path to Active

### Acceptance Criteria

- [x] Implementation is compliant with JSON conventions.
- [x] Implementation is compliant with the [[ISO-639]](https://www.iso.org/standard/4767.html) standard for language code, and the [[ISO-3166]](https://www.iso.org/standard/63545.html) standard for country/region code.
- [ ] Implementations and peer review verify that:
  - [ ] NFT metadata standard extension covers all existing localization needs and use cases on web2.
  - [ ] Access to localized strings is easy and logical from a coding perspective.

### Implementation Plan

- [ ] Propose this method in documentation and references for web3 developers.
- [x] NMKR has supported this CIP with peer feedback.
- [ ] NMKR has provided a pilot implementation of this localization method.

## References

- CIP about Media Token Metadata Standard [CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025).
- [[ISO-639]](https://www.iso.org/standard/4767.html) language code.
- [[ISO-3166]](https://www.iso.org/standard/63545.html) country/region code.

## Copyright

This CIP is licensed under [CC-BY-4.0].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
