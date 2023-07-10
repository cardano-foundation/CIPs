---
CIP: ?
Title: Distributed Artifact Token Metadata Standard
Category: Tokens
Status: Proposed
Authors:
  - Wout Fierens <wout@venster.art>
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/530
Created: 2023-06-30
License: CC-BY-4.0
---

## Abstract

This standard was initially developed for on-chain generative tokens, but it is also suitable for other use cases. It describes a method to store code and data on the blockchain in a space-efficient way using Cardano's Native Tokens.

Generative tokens created following this standard are called **Distributed Artifact Tokens** or **DAT**s. They are not necessarily a replacement for NFTs but rather a layer on top of Cardano's Native Tokens. They can be fungible, semi-fungible, or non-fungible.

DATs introduce a way to instruct token viewers to query information from the blockchain. Creators can use the queried data to create dynamic, evolving, or interlinked token collections. Queries may include:

- Information about the current state of the blockchain
- Details from the token's mint transaction
- Details from previously minted tokens

## Motivation: why is this CIP necessary?

The four following problems describe the motive for creating this standard.

### Problem 1: Storage limit

Cardano is very well suited for on-chain generative tokens. Compared to other blockchains, it has a low L1 storage cost per kB, but the maximum transaction size of 16 kB is more limited than other chains.

How can we create generative tokens with larger on-chain codebases without hurting the blockchain?

### Problem 2: Inefficient use of block space

Some existing on-chain projects on Cardano make inefficient use of block space by repeatedly storing the same monolithic blob accompanied by a few unique parameters. The result is thousands of copies of the same code, close to or at the total capacity of the 16 kB transaction limit.

Without imposing more restrictions on creators, how do we drastically reduce the on-chain storage footprint of generative token collections?

### Problem 3: Diversity of tools

While JavaScript has become the dominant language for on-chain art, it's only a fraction of other languages and tools available to artists. Many established artists use tools that are not based on web technologies and sometimes adapt or limit their workflow to make their work run in a web browser.

What is the best interface for token viewers to support a diverse set of tools and languages?

### Problem 4: Archival qualities

Storing all dependencies for a generative token on the blockchain is not always convenient, sensible, or even viable. Examples are p5.js, three.js, Processing, and Blender, to name a few. There is currently no way to describe token dependencies, so third parties can render or reproduce digital artifacts.

What's the best way to describe external dependencies and maximize the archival qualities of digital artifacts?

## Specification

A single DAT is distributed over at least two tokens, represented by three possible token types: _scene_, _renderer_ and optionally, _dependency_.

Typically, _scene_ tokens don't hold any code. They carry a reference to the _renderer_ token, arguments for invocation of the _renderer_ and token-specific properties. _Scene_ tokens are therefore relatively small (less than 3kB). All _scene_ tokens in a collection reference one, or at most a few, _renderer_ tokens.

The code to render all _scene_ tokens is stored in a _renderer_ token, which in turn can reference _dependency_ tokens containing shared libraries or assets. _Dependency_ tokens are considered extensions to the _renderer_ and can not be referenced directly by _scene_ tokens.

**Note**: The DAT Metadata Standard builds on the existing [CIP-0025](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025) standard.

### **1**. Scene

The _scene_ token is the part the end user will receive in their wallet. It contains all the information to render the DAT.

#### **1.a.** Metadata

_Scene_ tokens require a `renderer` property to be present, referencing the token containing the code of the renderer.

Although not mandatory, it's advisable to bundle token-specific properties in the `properties` object to avoid pollution of the token's root namespace. It will help token viewers locate and render those details.

```diff
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "name": <string>,
        "description": <string>,

        "image": <uri | array>,
        "mediaType": image/<mime_sub_type>,

        "files": [{
          "name": <string>,
          "mediaType": <mime_type>,
          "src": <uri | array>,
+         "license": <string>,
          <other_properties>
        }],

+       "renderer": {
+         "main": <asset_name>,
+         "arguments": <array>
+       },

+       "properties": {
+         <properties>
+       }
      }
    }
  }
}
```

Properties for the _scene_ token:

- **`renderer`** (_required_): an object with two properties
  - **`main`** (_required_): the `asset_name` of the _renderer_ token within the
    current `policy_id` (e.g. `my_renderer`)
  - **`arguments`** (_required_): an array with arbitrary values used as
    arguments for the invocation of the _renderer_ (e.g.: `[123]`)
- **`properties`** (_optional_): an object with arbitrary key/value pairs describing the token's (unique) properties

### **1.b.** Argument directives

Several directives for dynamic arguments can be passed to the renderer. Before rendering a DAT, viewers must resolve any directives by querying the requested data from the blockchain and passing the actual values to the renderer.

_Current token_

- **`@tx_hash`** (`string`): transaction hash of the mint (can for example, be used as the seed value for a Sfc32 PRNG)
- **`@epoch`** (`number`): epoch in which the token was minted
- **`@slot`** (`number`): slot in which the token was minted
- **`@block`** (`number`): block in which the token was minted
- **`@block_size`** (`number`): the size of the token's block
- **`@block_hash`** (`string`): hash of the token's block
- **`@owner_addresses`** (`string[]`): an array of owner addresses

_Previously minted token_

- **`@tx_hash.previous`** (`string | null`): transaction hash
- **`@epoch.previous`** (`number | null`): epoch in which the token was minted
- **`@slot.previous`** (`number | null`): slot in which the token was minted
- **`@block.previous`** (`number | null`): block in which the token was minted
- **`@block_size.previous`** (`number | null`): the size of the token's block
- **`@block_hash.previous`** (`string | null`): hash of the token's block
- **`@arguments.previous`** (`array | null`): token's _renderer_ arguments

_Specific token (within the same policy_id)_

- **`@tx_hash.asset_name`** (`string | null`): transaction hash
- **`@epoch.asset_name`** (`number | null`): epoch in which the token was minted
- **`@slot.asset_name`** (`number | null`): slot in which the token was minted
- **`@block.asset_name`** (`number | null`): block in which the token was minted
- **`@block_size.asset_name`** (`number | null`): the size of the token's block
- **`@block_hash.asset_name`** (`string | null`): hash of the token's block
- **`@arguments.asset_name`** (`array | null`): token's _renderer_ arguments

_Current blockchain state_

- **`@current_epoch`** (`number`): current (latest) epoch
- **`@current_slot`** (`number`): current (latest) slot
- **`@current_block`** (`number`): current (latest) minted block
- **`@current_block_size`** (`number`): the size of the current block
- **`@current_block_hash`** (`string`): hash of the current block

Passing argument directives to the _renderer_ works just like static arguments. For example:

```
[
  123,
  "@tx_hash",
  "@block",
  "@current_block",
  "@epoch.previous",
  "@arguments.the_perfect_nft_000"
]
```

Referencing another token's arguments does not work recursively.

**Note**: The list of directives mentioned above is not final. Proposals for new directives will be considered and added over time.

## **2**. Renderer

The _renderer_ token is at the heart of a DAT collection and can either be a self-contained program or one with dependencies. It is always part of the same `policy_id` as the _scene_ tokens. Multiple _renderer_ tokens can exist within a policy, but _scene_ tokens can only reference one _renderer_ at a time.

### **2.a.** Metadata

The _renderer_'s code is stored in the `files` property as-is or as a base64-encoded string. The `name` property of the file must match the `asset_name` with the appropriate file extension, so viewers can filter out the renderer-related files.

A _renderer_ must always define an `outputType`. Token viewers decide which output types to support.

**Note**: A single _renderer_ token can have multiple files of different mime types, as long as the file names match the token's `asset_name`.

```diff
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "files": [{
          "name": <asset_name>.<extension>,
          "mediaType": <mime_type>,
          "src": <uri | array>,
+         "license": <string>,
          <other_properties>
        }],

+       "outputType": <mime_type>,

+       "dependencies": [{
+         "type": <string>,
+         <other_properties>
+       }],

+       "browsers": {
+         <browser_name>: <major_version>
+       }
      }
    }
  }
}
```

Properties for the _renderer_ token:

- **`outputType`** (_required_): the mime type of the renderer's output (it's up to the viewer to define the supported formats)
- **`dependencies`** (_optional_): an array of objects with dependency definitions
- **`browsers`** (_required for browser-based DATs_): an object with versions of browsers against which the _renderer_ is tested

**Note**: While not mandatory, adding a **`license`** property to every file in the `files` section is advisable—more info on licenses is below in section 2.f.

The _renderer_ token should be burned after minting to free up the UTxO.

### **2.b.** On-chain dependencies

These are policy-specific on-chain dependencies managed by the creator. They must be minted within the same `policy_id` and are referenced by their `asset_name`.

```
{
  "type": "onchain",
  "asset_name": <asset_name>
}
```

- **`type`** (_required_): dependency type
- **`asset_name`** (_required_): name of the asset within the same policy

### **2.c.** Internal dependencies:

These are on-chain dependencies managed internally by the viewer and made available to the _renderer_ at runtime.

They can be referenced by using the dependency's asset `fingerprint`:

```
{
  "type": "internal",
  "fingerprint": <asset_fingerprint>
}
```

- **`type`** (_required_): dependency type
- **`fingerprint`** (_required_): asset fingerprint

Alternatively, the asset's `policy_id` and `asset_name` can be used:

```
{
  "type": "internal",
  "policy_id": <policy_id>,
  "asset_name": <asset_name>
}
```

- **`type`** (_required_): dependency type
- **`asset_name`** (_required_): name of the asset
- **`policy_id`** (_required_): policy id of the asset

### **2.d.** External dependencies:

These are off-chain dependencies managed by the viewer and made available to the _renderer_ at runtime.

```
{
  "type": "external",
  "name": <library_name>,
  "version": <version_number>,
  "source": <uri>,
  "module": <boolean>
}
```

- **`type`** (_required_): dependency type
- **`name`** (_required_): name of the library (list provided by viewers)
- **`version`** (_required_): version of the library
- **`source`** (_required_): URI of the library (IPFS, Arweave, etc.)
- **`module`** (_required_): module flag; if set to `false`, an iife variant is used

**Note**: The _external_ dependency definitions are not referencing any token on the blockchain, unlike the _onchain_ and _internal_ variants. Their sole purpose is instructing token viewers which external dependency to load at runtime. A list of available libraries is maintained in the [venster-external-dependencies repo](https://github.com/venster-io/venster-external-dependencies).

### **2.e.** Build instructions

This section only applies to non-browser-based renderers.

The build of a locally executed token revolves around a Dockerfile that should be included in the files of the _renderer_ token. Optionally, package or configuration files can be included that are required by the Dockerfile to build the image.

```
{
  "files": [{
    "name": "Dockerfile",
    "mediaType": "text/plain",
    "src": <array>
  }]
}
```

### **2.f.** License types

For creators, it is recommended to choose a license that aligns with their values and with the purpose of the digital artifact. Any license can be used, but popular licenses are:

- [NFT License 2.0](https://www.nftlicense.org/)
- [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- [AGPL 3.0](https://www.gnu.org/licenses/agpl-3.0.en.html)

Using [no license](https://choosealicense.com/no-permission/) is also an option to explicitly indicate that no one other than the creator may use the software.

## **3**. Dependency

This section applies to _onchain_ and _internal_ dependencies. Aside from how they are referenced, they are technically the same.

Dependency tokens can have multiple parts if they do not fit into one 16kB transaction. The dependency referenced from the _renderer_ serves as an entry point, referencing the additional parts.

### **3.a.** Metadata

The code is stored in the **`files`** property as-is or as a base64-encoded string. The `name` property of the file must match the `asset_name`. Like the _renderer_, every file can have an individual `license` property.

```diff
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "files": [{
          "name": <asset_name>.<extension>,
          "mediaType": <mime_type>,
          "src": <uri | array>,
          "license": <string | null>,
          <other_properties>
        }],

+       "parts": [
+         <part_asset_name>
+       ]
      }
    }
  }
}
```

Properties for the _dependency_ token:

- **`parts`** (_optional_): an array with asset names (e.g. `asset_name_part_2`)

**Note**:
While not mandatory, adding a **`license`** property to each file in the `files` section is advisable—more info on licenses is in section 2.f.

Dependency tokens should be burned after minting to free up the UTxOs.

## Rationale: how does this CIP achieve its goals?

This section presents the resolutions to the four problems mentioned in the motivation section of this CIP. Given that this standard has already been embraced by a few collections, real-world examples are used to demonstrate the implementation and advantages of DATs.

## Solution 1: **Storage limit**

The distributed nature of DATs allows bigger on-chain codebases with dependencies. The separation of code and metadata effectively doubles the available space.

Additionally, dependencies can be stored in chunks, which allows for the realistic storage of up to fifty times more code than was previously possible.

**Note**: It is important to note that the increase of storage capacity applies to _renderer_ tokens, not _scene_ tokens. Therefore, the additional space is only available for code used by the _renderer_ and not for static data like images in _scene_ tokens.

### Example 1

This collection contains 3409 tokens and the first one ever minted using the DAT Metadata Standard.

| token type                 |   token size |   minted | collection size |
| -------------------------- | -----------: | -------: | --------------: |
| **scene**                  |      1.42 kB |     3409 |      4840.78 kB |
| **renderer (JS/CSS/HTML)** |     12.85 kB |        1 |        12.85 kB |
| **lib dependency (JS)**    |     11.77 kB |        1 |        11.77 kB |
| **font dependency 1**      |     15.35 kB |        1 |        15.35 kB |
| **font dependency 2**      |     15.24 kB |        1 |        15.24 kB |
| **total**                  | **56.63 kB** | **3413** |  **4895.99 kB** |

### Example 2

This collection contains 512 tokens and the second one ever minted using the DAT Metadata Standard.

| token type                 |   token size |  minted | collection size |
| -------------------------- | -----------: | ------: | --------------: |
| **scene**                  |      2.44 kB |     512 |      1249.50 kB |
| **renderer (JS/CSS/HTML)** |      9.72 kB |       1 |        12.85 kB |
| **lib dependency (JS)**    |     11.77 kB |       1 |        11.77 kB |
| **font dependency**        |     15.35 kB |       1 |        15.35 kB |
| **total**                  | **39.28 kB** | **515** |  **1289.47 kB** |

## Solution 2: **Inefficient use of block space**

By looking at three real-world cases, it becomes clear that using DATs requires roughly 90% less block space than using isolated monolithic NFTs.

The data used in the following examples is extracted from existing token collections. The first two examples used monolithic NFTs, while the third one used DATs.

### Example 1

This collection contains 17190 tokens as monolithic HTML NFTs.

|                        | renderer size | token size | total kB | total MB |
| ---------------------- | ------------: | ---------: | -------: | -------: |
| **as monolithic NFTs** |           N/A |    5.34 kB | 91792 kB |  89.6 MB |
| **as DATs**            |       4.91 kb |    0.53 kB |  9116 kB |   8.9 MB |

This collection would have used **90.03 %** less block space with DATs

### Example 2

This collection contains 1744 tokens as monolithic HTML NFTs.

|                        | renderer size | token size | total kB | total MB |
| ---------------------- | ------------: | ---------: | -------: | -------: |
| **as monolithic NFTs** |           N/A |    13.9 kB | 24241 kB |  23.7 MB |
| **as DATs**            |      13.40 kB |    1.46 kB |  2556 kB |   2.5 MB |

This collection would have used **89.54 %** less block space with DATs.

#### Example 3

This is a collection of 3409 tokens and the first one ever minted using the DAT Metadata Standard.

|                        | renderer size | token size |  total kB | total MB |
| ---------------------- | ------------: | ---------: | --------: | -------: |
| **as monolithic NFTs** |           N/A |   56.63 kB | 193052 kB | 188.5 MB |
| **as DATs**            |      55.21 kB |    1.42 kB |   4896 kB |   4.8 MB |

By using DATs, **97.46 %** less block space was used. It is also important to note that, since the token as monolithic NFT is larger than 16 kB, this collection wouldn't have been possible on Cardano.

### Solutions 3 and 4: **Diversity of tools and archival qualities**

Although problems 3 and 4 address different topics, one solution solves both: providing a standardized way to describe dependencies and build instructions.

There are two variants of DATs: browser-based and non-browser-based. Almost all on-chain generative tokens on any blockchain fall into the first group. This standard supports both variants.

#### Variant 1: **Browser-based**

Existing token viewers and blockchain explorers already support monolithic browser-based generative tokens. The most commonly used output formats are HTML and SVG, which can handle embedded JavaScript but can't have any dependencies.

Through dependency definitions, DATs can instruct token viewers to load libraries, such as [p5.js](https://p5js.org/), to allow generative tokens beyond just plain JavaScript. Token viewers can decide which libraries, and versions thereof, to support.

To enhance a token's archival qualities, DATs require a list of supported browsers with their versions in which the program is tested and confirmed to work correctly. It will help collectors to reproduce their token collections in the distant future.

#### Variant 2: **Non-browser-based**

Generative artists regularly use tools that run outside the confines of web browsers. At least two on-chain generative token collections on Cardano do not use web technologies for rendering and describe the reproduction process in an improvised way.

DATs solve this by including a [Dockerfile](https://docs.docker.com/engine/reference/builder/) and, if necessary, a package file for the appropriate language. Viewers supporting this variant only need Docker installed to render the token using the unique arguments given by the _scene_ token.

**Note**: The choice for [Docker](https://www.docker.com/) is one in favor of simplicity and familiarity. It requires the least effort and additional tooling on the side of the token viewer or anyone wanting to reproduce a generative token. If a more suitable solution presents itself with the same ease of use in the future, then it may be added as an alternative.

## Path to Active

This standard was developed through implementation, which means it is already in use. There is also a viewer prototype publicly available and roughly 4000 tokens minted using the standard.

### Acceptance Criteria

- [x] Build a token-viewer prototype
- [x] Create a real-world use case of browser-based DATs
- [ ] Create a real-world use case of non-browser-based DATs

### Implementation Plan

Wout Fierens will finalize the remaining part of this CIP by creating a DAT collection using the non-browser-based DAT variant.

## Copyright

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
