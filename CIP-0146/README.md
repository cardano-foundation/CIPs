---
CIP: 146
Title: Multi-signature wallet registration and discovery
Category: Wallets
Status: Proposed
Authors:
  - Ola Ahlman <ola.ahlman@tastenkunst.io>
  - Marcel Baumberg <marcel.baumberg@tastenkunst.io>
Implementors:
  - Eternl <https://eternl.io/>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/971
Created: 2025-01-22
License: CC-BY-4.0
---

## Abstract

This document describes how to format and register a multi-signature wallet registration on the blockchain. The 
individual parties that are part of the multi-signature wallet can through this registration transaction easily be 
discovered and added to the Cardano wallet software that implement the standard.

This standard both extend on and add restrictions to
[CIP-1854 | Multi-signature HD Wallets](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1854/README.md)
to provide the structure of transaction auxiliary data.

## Motivation: why is this CIP necessary?

Term     | Definition
---      | ---
Multisig | Shorthand for Multi-party signature scheme.
CSL      | [Cardano serialization lib](https://github.com/Emurgo/cardano-serialization-lib) by Emurgo.

Multisig wallets have the ability to communicate scripts and metadata ahead of time through a registration 
transaction utilizing the transaction auxiliary data. This is a convenient way for the multisig participants to 
discover the multisig wallet before it's first usage.

A common structure of the auxiliary data is needed for interoperability between wallets and web applications. The 
metadatum label `1854` is used to define the native script types added in the auxiliary data and optionally provide 
information about the wallet and its participants. 

## Specification

The following rules apply for a multisig registration to be valid:

- Auxiliary data with a non-empty native scripts array.
- Auxiliary data with label `1854` metadata that at a minimum includes a mapping for script types.
- `ScriptType` mapping array in metadata must match the length of, and directly corresponds to the elements in the 
  `native_script` array of transaction auxiliary data.
- Native scripts array must at least include a payment script. Other script types are optional.
- Public key hashes (credentials) included in the native scripts must be derived in accordance with CIP-1854, ie using 
  `purpose=1854'`. 
- Key derivation limited to path `1854'/1815'/0'/x/y`, ie account `0` for best cross-project interoperability and performance.
- Key index (`y`) must be incremented by `1` for each publicly registered multisig wallet.
- Key for role (`x`) must use the same index (`y`) for all native scripts in the registration transaction.
- Additional optional metadata can be added to the `1854` metadatum label to describe the multisig.
- Optional icon fields is a URL to a non-animated image file, maximum 40kb in size.

### Data Types

#### MultiSigRegistration
Label `1854` metadata.
```ts
interface MultiSigRegistration {
  types: ScriptType[];
  name?: string;
  description?: string;
  icon?: string;
  participants?: MultiSigParticipants;
}
```

#### ScriptType
A number representing a specific type (role). This corresponds to the key derivation path role (`x`).
```ts
type ScriptType = number;
```

#### MultiSigParticipants
A mapping between key credential and participant details.
```ts
interface MultiSigParticipants {
  [key: string]: MultiSigParticipant;
}
```

#### MultiSigParticipant
Multisig participant details.
```ts
interface MultiSigParticipant {
  name: string;
  description?: string;
  icon?: string;
}
```

#### OffChainMultiSigRegistration
The hex-encoded bytes for a transaction auxiliary data `metadata` and `native_script` array.
```ts
interface OffChainMultiSigRegistration {
  metadata: string;
  native_scripts: string;
}
```

### Registration

After the multisig wallet has been defined according to the Cardano native script standard, and adhering to the
[rules](#specification), either a registration transaction can be put on the blockchain or a JSON download provided for 
off-chain sharing. 

>Note that the registration **must** use previously unused keys in the scripts **if** registered in a transaction. 

The transaction auxiliary data metadata ([MultiSigRegistration](#multisigregistration)) should be formatted using 
NoConversions JSON schema.

If using the CSL library, this can be accomplished with helper functions `encode_json_str_to_metadatum` and 
`decode_metadatum_to_json_str` specifying `MetadataJsonSchema.NoConversions` as the JSON schema.

Input Output Global (IOG) documentation also describe the
[no schema](https://github.com/input-output-hk/cardano-node-wiki/blob/main/docs/reference/tx-metadata.md#no-schema)
JSON mapping in more detail.

#### Transaction

A registration transaction is the most user-friendly alternative as it allows for automatic multisig wallet discovery 
by its participants. 

#### Off-chain download

The off-chain JSON file should have the format of `OffChainMultiSigRegistration`.

### Discovery

Discovering registered multisig wallets on the blockchain that has public keys included for a participant wallet 
can be done in the following way.

- Derive Ed25519 verification keys from path `1854'/1815'/0'/x/y`.
- Create key credentials, `blake2b-224` hash digests of derived keys in previous step.
- Search for multisig registration transactions on the blockchain that contain metadata with metadatum label `1854` 
  and key credentials matching participant wallet. Only the first (oldest) encountered match should be returned.
- Use `types` field in metadata to map native scripts and figure out its purpose
- Repeat until no more matches are found, either sequentially or in bulk.

>Note that there might be updated metadata for the registration. In addition to locating the initial registration, a
> scan for updated metadata conforming to specification and at least one input UTxO matching the multisig payment script 
> should be performed. If available, the last valid metadata update is to be used.

### Metadata update

Metadata included in the original registration transaction might need to be updated after the initial registration. To 
support this, a metadata update transaction can be created that spends at least one input UTxO from the multisig wallet 
to verify ownership. If this transaction includes label `1854` metadata according to specification mentioned in
[registration](#registration), this will replace and update previously registered metadata.

### Encrypted metadata (optional)

To increase anonymity, encrypting the metadata following the specification of [CIP-83 | Encrypted Transaction message/comment metadata](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0083/README.md)
is supported. For this to be valid, the `enc` key should be added to the root metadata object and each value 
(**except** `types`) within the metadata should be base64 encrypted according to CIP-83 specification.

>Note that `types` mapping array within metadata should always be unencrypted! 

Example structure:
```json
{ 
  "1854": { 
    "enc": "<encryption-method>",
    "types": [0,2],
    "name": "base64-string",
    "description": "base64-string",
    "icon": "base64-string",
    "participants": {
      "<pub-key-hash>": {
        "name": "base64-string",
        "description": "base64-string",
        "icon": "base64-string"
      }
      ...
    }
  }
}
```

## Rationale: how does this CIP achieve its goals?

The structure to handle registration of native scripts ahead of time has been available from the Allegra era and 
beyond by including script pre-image in transaction auxiliary data. The principal aim for this specification is to 
reduce friction and increase interoperability between wallet providers and web applications by adding some common 
rules and restrictions for format of metadata and keys used in scripts.

### Q & A
A couple of questions was raised during discussions with team members and other projects when formalizing this 
standard. The answers lay the ground in large for the specification and restrictions defined.  

#### Why limit it to purpose 1854 and not allow both HD (1852) and Multi-Signature (1854) keys?
Mostly due to compatibility across projects and hardware devices as this is how the well established CIP-1854 
specification describe that it should be done. Also for discovery, it reduces complexity and increases
performance by only having to scan for a restricted amount of keys.
 
#### Why not encourage and scan any account index, and not just index 0?
Account indexes is a very useful feature for normal wallets to separate funds, multi-delegation and much more. 
However, for multisig wallets, they add little value. The idea behind a multisig is that each participant is its own 
identity, either person or wallet. Having multiple keys in the multisig from the same root key adds false security.

#### But what if I want to utilise the benefits of account separation for fund splitting between the same set of participants?
This can easily be solved without additional accounts by adding an `after` timelock with the current slot height of 
the blockchain. This creates a unique multisig wallet (address) even if the rest of the script is identical. This way,
an infinite number of multisig wallets can be created similar to account separation.

#### What roles should be supported on discovery?
This specification doesn't restrict discovery to any specific role, depending on the use case of the implementer and 
additional roles defined in the future through new CIPs. CIP-1854 define role 0 (payment) and role 2 (stake) for 
script wallets. CIP-105 was created to extend key definition with additional governance roles 3-5.

#### What about key role and index restrictions?
The main reason for the incrementing key index is to mitigate a possible attack vector where a malicious actor could 
replay a publicly registered multisig wallet, modifying the script in a nefarious way. When the wallets connected to the
users multisig key are discovered, both the valid and the invalid multisig registrations would be discovered and the 
user might interact with the malicious wallet. By only allowing a key to be registered once, this threat can be 
eliminated. 

Keeping key index in sync for all roles for the same registration makes key handling more manageable.

#### Is types mapping in metadata really necessary?
It's true that on the wallet side when deriving purpose `1854` keys and scanning for registered wallets, it's known 
from what path the keys where derived and thus one could figure out the type of native script based on key credential. 
However, enforcing the transaction to include metadata with metadatum label `1854` and the types mapping make it clear 
that this is a multisig registration and easier to scan for. 

## Path to Active

### Acceptance Criteria

- [ ] The specification is implemented by three wallet providers or dApps (web applications).
  - [x] [Eternl Wallet](https://eternl.io)

### Implementation Plan

- [x] Author to engage with wallet providers and web applications for feedback.
  - [x] Discussion channel opened on [Cardano Improvement Proposals Discord server](https://discordapp.com/channels/971785110770831360/1336823914671767663)
  - [x] [GitHub PR](https://github.com/cardano-foundation/CIPs/pull/971) for proposal.
- [x] Author to implement said standard in Eternl wallet.
- [ ] Collaborate with web applications and wallet providers to drive adoption of standard.

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
