---
CIP: 100?
Title: Supercharged Native Scripts for Minting and Burning Cardano Native Tokens
Category: Tokens
Status: Proposed
Authors:
    - Niels Mündler <n.muendler@posteo.de>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/479
Created: 2023-03-15
License: CC-BY-4.0
---
## Abstract

This CIP proposes replacing the current native scripts used for minting Cardano Native Tokens with simple, parameterized smart contracts called "Supercharged Native Scripts". The main goal is to allow users to burn their native assets at any time by utilizing smart contracts that enforce the minting conditions while always allowing burning. The concept is standardized and generalized for broader use-cases.

## Motivation

The current process for minting and burning Cardano Native Tokens relies on native scripts, which do not provide a simple mechanism for users to burn their tokens and reclaim the minUTxO (ADA) locked by those tokens. As a result, users may end up with many unwanted tokens or NFTs, locking a considerable amount of ADA.

This proposal aims to create a standardized solution for minting and burning tokens in the Cardano ecosystem, making it easier for users to manage their assets and recover locked ADA. Generalizing from this, the proposal suggests the standardization and adoption of "Supercharged Native Scripts" as a preferred, more powerful alternative to Native Scripts.


## Specification

Super-charged native scripts are Plutus (V1/V2) Smart Contracts that have the following properties

- They are parameterized by a PlutusData object representing a Native Script
- They have no requirements regarding the type or content of the input datum and redeemer (including whether a datum is present or not)
  
> Note: for the time being, UTxOs locked at a Smart Contract address _must_ be locked together with a Datum to be spent. This is different to Native Scripts, which don't require datums. Hence one still needs to be aware whether they are interacting with a Supercharged, or Normal Native Script

- They enforce that the parameterized Native Script conditions are met, unless specific conditions are met that are specified in the contract. 

Examples include:
  - Minting validators that always allow burning of funds
  - Spending validators that allow withdrawing non-ADA tokens

These Smart Contracts are identified by their UPLC script being of the format `[[(lam _ <script>) (con bytestring #xx)] (con data <cbor of native script encoding>)]` where `xx` is an identifier
of the specific examples mentioned earlier.
This CIP will collect and list all widely used validators.

#### List of supercharged validator tags, with specification

1. `#000001`: "Always burning" Minting Validators, that always validates if all amounts of minted assets of the governed policy id are negative (i.e. being burned)

#### Representation of Native Scripts as PlutusData

The standard representation of Native Scripts as PlutusData objects can be derived from the following specification (in PyCardano `PlutusData` notation):

```python
@dataclass()
class RequireSignature(PlutusData):
    CONSTR_ID = 0
    vkeyhash: bytes  # this is either a PubKeyHash or a VerificationKeyHash


@dataclass()
class RequireAllOf(PlutusData):
    CONSTR_ID = 1
    scripts: List[Datum]  # "Script"


@dataclass()
class RequireAnyOf(PlutusData):
    CONSTR_ID = 2
    scripts: List[Datum]  # "Script"


@dataclass()
class RequireMOf(PlutusData):
    CONSTR_ID = 3
    num: int
    scripts: List[Datum]  # "Script"


@dataclass()
class RequireBefore(PlutusData):
    CONSTR_ID = 4
    unixtimestamp: int


@dataclass()
class RequireAfter(PlutusData):
    CONSTR_ID = 5
    unixtimestamp: int


Script = Union[
    RequireSignature,
    RequireMOf,
    RequireAnyOf,
    RequireAllOf,
    RequireAfter,
    RequireBefore,
]
```

## Rationale

By replacing native scripts with smart contracts for minting and burning tokens, users will have a simple and standardized way to manage their assets and recover locked ADA. This proposal will help prevent the accumulation of unwanted tokens or NFTs and give users more control over their assets.

Furthermore, the proposed solution will not force all tokens to be burnable, allowing users to opt-in for burnable tokens when desired. The optional tag will make it easy for wallets to identify and handle burnable tokens, improving the user experience.

## Path to Active


### Acceptance Criteria

- [ ] Sample Plutus smart contracts emulating native scripts are developed and tested (in different languages)
  - [ ] PlutusTx
  - [x] [eopsin](https://github.com/OpShin/eopsin/blob/5466faab6da42d2b21b328e433c6dfff99cddfdd/examples/smart_contracts/simple_script.py)
  - [x] [hebi](https://github.com/OpShin/hebi/blob/master/examples/smart_contracts/simple_script.py)
  - [ ] ...
- [ ] Simple tooling for non-developers is built to allow supercharging Native Script definitions.
  - [ ] Converter Native Script --> PlutusData for Script parameterization
  - [ ] Converter Slot number --> POSIXTime
- [ ] An optional tag within the UPLC script or specific metadata is defined.
- [ ] Tutorials and documentation are updated to reflect the new minting and burning process.
- [ ] Wallets implement the necessary features to support the burning of tokens using the proposed smart contracts.

### Implementation Plan

- [x] Develop and test the Plutus smart contracts that emulate native script behavior.
- [ ] Develop tooling to interact with smart contracts
- [ ] Update existing tutorials and documentation.
- [ ] Collaborate with wallet developers to implement the necessary features for burning tokens using the proposed smart contracts.

### Copyright

This CIP is licensed under the Creative Commons Attribution 4.0 International License (CC-BY-4.0).
