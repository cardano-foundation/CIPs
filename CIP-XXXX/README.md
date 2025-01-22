---
CIP: \?
Title: Multi-signatures wallet registration and discovery
Category: Wallets
Status: Proposed
Authors:
  - Ola Ahlman <ola.ahlman@tastenkunst.io>
Implementors:
  - Eternl <https://eternl.io/>
Discussions:
Created: 2022-02-24
License: CC-BY-4.0
---

## Abstract

This document describes how to format and register a multi-signatures wallet registration on the blockchain. The 
individual parties that are part of the multi-signatures wallet can through this registration transaction easily be 
discovered and added to the Cardano wallet software that implement the standard.

This standard both extend on and add restrictions to
[CIP-1854 | Multi-signatures HD Wallets](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1854/README.md)
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
metadatum label **1854** is used to define the native script types added in the auxiliary data and optionally provide 
information about the wallet and its participants. 

## Specification

The following rules apply for a multisig registration to be valid:

- Auxiliary data with a non-empty native scripts array.
- Auxiliary data with label 1854 metadata that at a minimum includes a mapping for script types.
- `ScriptType` mapping array in metadata must match the length of, and directly corresponds to the elements in the 
  `native_scripts` array of `AuxiliaryData`.
- Public key hashes included in the native scripts must be derived in accordance with CIP-1854, ie using 
  `purpose=1854'`. 
- Key derivation limited to path `1854'/1815'/0'/x/0` for best cross-project interoperability and performance.
- Additional **optional** metadata can be added to the 1854 metadatum label to describe the multisig.
- Optional icon fields is a URL to a non-animated image file, maximum 40kb in size.

### Data Types

#### MultiSigRegistration
Label 1854 metadata.
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
Native script type (to be extended as needed)
```ts
type ScriptType = 'payment' | 'stake' | 'drep';
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

#### AuxiliaryDataJSON
The transaction auxiliary data as defined by CSL. Only the metadata, native_scripts, and prefer_alonzo_format fields 
should be used but the entire interface is provided for completeness. 
```ts
interface AuxiliaryDataJSON {
  metadata?: {
    [k: string]: string;
  } | null;
  native_scripts?: NativeScriptJSON[] | null;
  plutus_scripts?: string[] | null;
  prefer_alonzo_format: boolean;
}
```

#### NativeScriptJSON
```ts
type NativeScriptJSON =
  | {
      ScriptPubkey: ScriptPubkeyJSON;
    }
  | {
      ScriptAll: ScriptAllJSON;
    }
  | {
      ScriptAny: ScriptAnyJSON;
    }
  | {
      ScriptNOfK: ScriptNOfKJSON;
    }
  | {
      TimelockStart: TimelockStartJSON;
    }
  | {
      TimelockExpiry: TimelockExpiryJSON;
    };
```

#### ScriptPubkeyJSON
```ts
interface ScriptPubkeyJSON {
  addr_keyhash: string;
}
```

#### ScriptAllJSON
```ts
interface ScriptAllJSON {
  native_scripts: NativeScriptJSON[];
}
```

#### ScriptAnyJSON
```ts
interface ScriptAnyJSON {
  native_scripts: NativeScriptJSON[];
}
```

#### ScriptNOfKJSON
```ts
interface ScriptNOfKJSON {
  n: number;
  native_scripts: NativeScriptJSON[];
}
```

#### TimelockStartJSON
```ts
interface TimelockStartJSON {
  slot: string;
}
```

#### TimelockExpiryJSON
```ts
interface TimelockExpiryJSON {
  slot: string;
}
```

### Registration

After the multisig wallet has been defined according to the Cardano native script standard, and adhering to the
[rules](#specification), either a registration transaction can be put on the blockchain or a JSON download provided for 
offline sharing.

The transaction auxiliary data metadata should be formatted using NoConversions JSON schema.

If using the CSL library, this can be accomplished with helper functions `encode_json_str_to_metadatum` and 
`decode_metadatum_to_json_str` specifying `MetadataJsonSchema.NoConversions` as the JSON schema.

Input Output Global (IOG) documentation also describe the
[no schema](https://github.com/input-output-hk/cardano-node-wiki/blob/main/docs/reference/tx-metadata.md#no-schema)
JSON mapping in more detail.

#### Transaction

A registration transaction is the most user-friendly alternative as it allows for automatic multisig wallet discovery 
by its participants. 

#### Offline download

The offline JSON file should have the format of `AuxiliaryDataJSON`.

### Discovery

Discovering registered multisig wallets on the blockchain that has public keys included for a participant wallet 
can be done in the following way.

- Derive Ed25519 verification keys from path `1854'/1815'/0'/x/0`.
- Create key credentials, `blake2b-224` hash digests of derived keys in previous step.
- Search for multisig registration transactions on the blockchain that contain metadata with metadatum label **1854** 
  and key credentials matching participant wallet.
- Use `types` field in metadata to map native scripts and figure out its purpose

## Rationale: how does this CIP achieve its goals?

The structure to handle registration of native scripts ahead of time has been available from the Allegra era and 
beyond by including script pre-image in transaction auxiliary data. The principal aim for this specification is to 
reduce friction and increase interoperability between wallet providers and web applications by adding some common 
rules and restrictions for format of metadata and keys used in scripts.

### Q & A
A couple of questions was raised during discussions with team members and other projects when formalizing this 
standard. The answers lay the ground in large for the specification and restrictions defined.  

#### Why limit it to purpose 1854 and not allow both HD (1852) and Multi-Signatures (1854) keys?
Mostly due to compatibility across projects and hardware devices as this is how the well established CIP-1854 
specification describe that it should be done. Also for discovery, it reduces complexity and increases
performance by only having to scan for a restricted amount of keys.
 
#### Why not encourage and scan any account index, and not just index 0?
Account indexes is a very useful feature for normal wallets to separate funds, multi-delegation and much more. 
However, for multisig wallets, they add little value. The idea behind a multisig is that each participant is its own 
identify, either person or wallet. Having multiple keys in the multisig from the same root key adds false security.

#### But what if I want to utilise the benefits of account separation for fund splitting between the same set of participants?
This can easily be solved without additional accounts by adding an `after` timelock with the current slot height of 
the blockchain. This creates a unique multisig wallet (address) even if the rest of the script is identical. This way,
an infinite number of multisig wallets can be created similar to account separation.

#### What roles should be supported on discovery?
This specification doesn't restrict discovery to any specific role, depending on the use case of the implementer and 
additional roles defined in the future through new CIPs. CIP-1854 define role 0 (payment) and role 2 (stake) for 
script wallets. CIP-105 was created to extend key definition with additional governance roles 3-5.

#### What about key index?
This is another restriction in comparison to CIP-1854 specification that allow for multiple indexes. In theory, it 
can add some limited privacy features. What we gain is simplicity and performance. The rationale here was that the 
pros outweigh cons.

#### Is types mapping in metadata really necessary?
It's true that on the wallet side when deriving purpose 1854 keys and scanning for registered wallets, it's known 
from what path the keys where derived and thus one could figure out the type of native script based on key. However, 
enforcing the transaction to include metadata with metadatum label 1854 and the types mapping make it clear that 
this is a multisig registration and easier to scan for. 

## Path to Active

### Acceptance Criteria

- [ ] The specification is implemented by three wallet providers or dApps (web applications).
  - [Eternl Wallet](https://eternl.io)
  - ...

### Implementation Plan

- [x] Author to engage with wallet providers and web applications for feedback.
  - Discussion channel opened on [MeshJS Discord server](https://discord.gg/WvnCNqmAxy)
- [x] Author to implement said standard in Eternl wallet.
- [ ] Collaborate with web applications and wallet providers to drive adoption of standard.

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
