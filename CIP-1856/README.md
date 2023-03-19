---
CIP: 1856
Title: Extend NFT metadata standard to support string localization
Category: Metadata
Status: Draft
Authors:
    - Vito Melchionna <info@granadapool.com>
    - Aaron Schmid <aaron@fortech.group>
    - Carolina Isler (@LaPetiteADA) <lapetiteada@granadapool.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-03-19
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta                   | For meta-CIPs which typically serves another category or group of categories.
- Reward-Sharing Schemes | For CIPs discussing the reward & incentive mechanisms of the protocol.
- Wallets                | For standardisation across wallets (hardware, full-node or light).
- Tokens                 | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata               | For proposals around metadata (on-chain or off-chain).
- Tools                  | A broad category for ecosystem tools not falling into any other category.
- Plutus                 | Changes or additions to Plutus
- Ledger                 | For proposals regarding the Cardano ledger
- Catalyst               | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
This proposal defines an addition to the NFT metadata standard to support text localization

## Motivation: why is this CIP necessary?
Current NFT metadata only supports a single hardcoded language (mostly English), which limits the accessibility to a certain culture. In order to get closer to mass adoption, we need to bring down language bariers by introducing a standard to add translations to native token metadata. This is specially relevant for games, metaverse solutions, and realfi use-cases of NFTs.  

## Specification
This proposal follows the same specifications as <CIP-0025>(https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025).
  
## Proposed structure

New metadata standard will look like this:
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
        },
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
      "version": <version_id>
  }
}

```

> **Note**
> This metadata standard extension doesn't affect the currently used standard, as dapps can default on the legacy values if the localized strings are not available.

## Implementation (TypeScript)

To access the localized strings from the fetched metadata for a native asset from an application written with TypeScript, it will look like this:
```

const response = await fetch(`${BASE_URL}/policyId/${policyId}`);    
            
const metadata = response.json();
const strings = metadata["721"][policyId]["strings"][culture]

console.log(`Asset name: ${strings["name"]}`);
            
```
            
## Path to Active

### Acceptance Criteria
- NFT metadata standard extension covers all existing localization needs and use-cases on web2.
- Implementation is compliant to JSON conventions.
- Access to localized strings is easy and logical from a coding perspective.
            
### Implementation Plan
Add this new standard to all relevant documentations and references for web3 developers.

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. -->

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
