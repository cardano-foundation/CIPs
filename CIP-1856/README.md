---
CIP: ?
Title: Extend token metadata for translations
Category: Metadata
Status: Proposed
Authors:
    - Vito Melchionna <info@granadapool.com>
    - Aaron Schmid <aaron@fortech.group>
    - Carolina Isler (@LaPetiteADA) <lapetiteada@granadapool.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/488
Created: 2023-03-19
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta                   | For meta-CIPs which typically serve another category or group of categories.
- Reward-Sharing Schemes | For CIPs discussing the reward & incentive mechanisms of the protocol.
- Wallets                | For standardization across wallets (hardware, full-node or light).
- Tokens                 | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata               | For proposals around metadata (on-chain or off-chain).
- Tools                  | A broad category for ecosystem tools not falling into any other category.
- Plutus                 | Changes or additions to Plutus
- Ledger                 | For proposals regarding the Cardano ledger
- Catalyst               | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
This proposal defines an additional property to the metadata standard for tokens (NFTs and FTs) to support text localization.

## Motivation: why is this CIP necessary?
Current token metadata only supports a single hardcoded language (mostly English), which limits the accessibility to a certain culture. To get closer to mass adoption, we need to bring down language barriers by extending the current standard to support translations. This is especially relevant for games, metaverse solutions, and RealFi use cases of NFTs.

## Specification
This proposal follows the same specifications as [CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025).
    
The name of a culture consists of its [[ISO-639]](https://www.iso.org/standard/4767.html) language code with small letters and its [[ISO-3166]](https://www.iso.org/standard/63545.html) country/region code with capital letter separated by a dash "-". For instance, this proposal was written in "en-US": English with the US culture.

This convention is compatible with most operative systems (Linux and Windows) and widely used translation software.
    
### Proposed structure

The new JSON metadata standard will look like this:
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
                "image": <localized uri for Italian German | array>,     
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

> **Note**
> This metadata standard extension is backward compatible and it doesn't affect applications using the current standard. Dapps implementing the proposed extended standard can also default on the legacy values if the localized strings are not available on an asset.

### Code example to access localized properties (TypeScript)

To access the localized strings from the fetched metadata for a native asset, we can simply access the JSON properties from the front end by using the user's selected culture:

```

const response = await fetch(`${<BASE_URL>}/policyId/${<policyId>}`);
            
const metadata = response.json();
const policy = metadata["721"][<policy_id>];

function getPolicyString(policy, key, culture="en") {
    return policy["strings"][culture][key] 
        ? policy["strings"][culture][key] 
        : policy[key]; // default value (not localized)
}

function getAssetString(policy, asset, key, culture="en") {
    return policy[asset]["strings"][culture][key] 
        ? policy[asset]["strings"][culture][key] 
        : policy[asset][key]; // default value (not localized)
}

console.log(`Default policy property: ${getPolicyString(policy, <policy_property>)}`);
console.log(`Localized policy property: ${getPolicyString(policy, <policy_property>, "it-IT")}`);
console.log(`Default asset name: ${getAssetString(policy, <asset_name>, "name")}`);
console.log(`Localized asset name: ${getAssetString(policy, <asset_name>, "name", "de-CH")}`);
         
```
     
## Path to Active

### Acceptance Criteria
- NFT metadata standard extension covers all existing localization needs and use cases on web2.
- Implementation is compliant with JSON conventions.
- Implementation is compliant with the [[ISO-639]](https://www.iso.org/standard/4767.html) standard for language code, and the [[ISO-3166]](https://www.iso.org/standard/63545.html) standard for country/region code.
- Access to localized strings is easy and logical from a coding perspective.
            
### Implementation Plan
Add this new standard to all relevant documentation and references for web3 developers.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
