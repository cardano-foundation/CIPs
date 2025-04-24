---
CIP: 8
Title: Message Signing
Status: Active
Category: Tools
Authors:
  - Sebastien Guillemot <sebastien@emurgo.io>
Implementors:
  - Mesh <https://meshjs.dev/>
  - Cardano Ballot <https://github.com/cardano-foundation/cf-cardano-ballot>
  - SundaeSwap governance <https://governance.sundaeswap.finance/>
  - Emurgo <https://www.emurgo.io/>
Discussions:
  - https://github.com/Emurgo/EmIPs/pull/5
  - https://forum.cardano.org/t/message-signing-specification/41032
  - https://cardano.ideascale.com/a/dtd/Create-message-signing-standard/323158-48088
Created: 2020-09-28
License: CC-BY-4.0
---

## Abstract

Private keys can be used to sign arbitrary data. If you have the public key, you can verify the data was signed by the owner of the private key. This is how transaction signing works internally but its utility is not limited to transactions. This document tries to set a standard for how to represent and verify signed messages for Cardano.

## Motivation: why is this CIP necessary?

Most common use cases:

1) Proving ownership of a set addresses (possibly to prove ownership of more then X Ada)
1) Proving ownership of addresses used in a transaction
1) Proving ownership of an identity or other off-chain data with a public key attached to it

## Specification

### Versions

| version | description     |
|---------|-----------------|
| 1       | initial version |

### Signing and Verification

#### Overview

First we will show a very basic example of the structure to help the reader understand the definitions that comes after

```
[
  bstr,               ; protected header
  { * label => any }, ; unprotected header
  bstr / nil,         ; message to sign
  [                   ; signature array
    [                     ; first signature
      bstr                ; protected
      { * label => any }, ; unprotected
      bstr                ; signature
    ]
  ]
]
```

You can see the structure has two layers -- both containing a `protected` and an `unprotected` section. Items inside `protected` are part of the data signed while `unprotected` is meant to annotate the COSE structure (for example add annotations as you pass a message across a stack). Items MUST NOT be duplicated.

You can find more complete definitions of `protected` and `unprotected` in [RFC 8152 section-3](https://tools.ietf.org/html/rfc8152#section-3) and you can see some the reserved entries (called `Generic_Headers`) in the maps in [RFC 8152 section-3.1](https://tools.ietf.org/html/rfc8152#section-3.1).

Note: `payload` can be `nil`. This means that the payload is known by both the signer and the verifier and therefore doesn't need to be encoded.

For your convenience, the structure is provided here:

```
empty_or_serialized_map = bstr .cbor header_map / bstr .size 0

header_map = {
    Generic_Headers,   ; reserved headers (see COSE section 3.1)
    * label => values  ; any number of int/string labels for application-specific purpose.
}

Headers = (
    protected : empty_or_serialized_map,
    unprotected : header_map
)

; signature layer
COSE_Signature =  [
    Headers,
    signature : bstr
]

; if signing with just ONE key
COSE_Sign1 = [
    Headers,
    payload : bstr / nil,
    signature : bstr
]

# if signing with >1 key
COSE_Sign = [
    Headers,
    payload : bstr / nil,
    signatures : [+ COSE_Signature]
]

signed_message = COSE_SIGN / COSE_Sign1
```

#### Signing and Verification target format

Instead of signing the full structure, we instead sign the following type which is derived from the structure

```
Sig_structure = [
  context : "Signature" / "Signature1" / "CounterSignature",    ; explained below
  body_protected : empty_or_serialized_map,                     ; protected from layer 1
  ? sign_protected : empty_or_serialized_map,                   ; not present in Sign1 case
  external_aad : bstr,                                          ; explanation below
  payload : bstr
]
```

The `external_aad` allows an application to ask the user to sign some extra data but NOT put it inside the COSE structure (only as part of the data to sign). Defaults to `h''`. You can read more about this at [RFC 8152 section-4.3](https://tools.ietf.org/html/rfc8152#section-4.3).

The `context` is meant to encode what structure was used for the COSE request. `CounterSignature` is explained in a later section of this specification.

#### Signing and Verification process

To be able to effectively verify we need two things:

1) P1 - (optional) knowledge of the relation of a public key and a Cardano address
1) P2 - Knowledge of which algorithm was used to sign

For `P1`, the mapping of public keys to addresses has two main cases:

1) for Shelley addresses, one payment key maps to many addresses (base, pointer, enterprise)
2) for Byron addresses, chaincode and address attributes need to be combined with the public key to generate an address

To resolve this, one SHOULD add the full address to the protected header when using a v2 address. The v2 addresses contain the chaincode + attributes and we can verify the address matches combining it with the verification public key.

```
? address: bstr,
```

For `P2`, we use the `alg` header and to specify which public key was used to sign, use the [cwt](https://tools.ietf.org/html/rfc8392) protected header.

### Encryption

Although COSE defines multiple ways to encrypt, we simplify our spec to the two following cases:

1) Encrypted with the recipient's public key (called `key transport` in COSE spec)
2) Encrypted with a user-chosen password (called `passwords` in COSE spec)

In order to facilitate implementations in wallets, we limit the usage of these to the following

```
ChachaPoly
Ed25519PubKey
```

We will explain what this means shortly but you can find the full list of the types of encryption allowed by COSE at [RFC 8152 section 5.1.1](https://tools.ietf.org/html/rfc8152#section-5.1.1)

#### Structure

The COSE specification is made to be composable -- that is you can have a plaintext that you wrap with a signature, then wrap with an encryption, then wrap with a signature again (and so on).

That means that for encryption in particular, it can either

1) Be used to encrypt plaintext directly
2) Be used to encrypt another COSE message

In this spec, we care about the case where you encrypt a `signed_message`

Here is the overall CBOR structure

```
; holds encrypted content itself
COSE_Encrypt = [
  Headers,
  ciphertext : bstr / nil, ; contains encrypted signed_message
  recipients : [+COSE_recipient]
]

; holds encrypted keys the receiver can use to decrypt the content
COSE_recipient = [
  Headers,
  ciphertext : bstr / nil, ; contains encrypted key to decrypt the COSE_Encrypt ciphertext
  ? recipients : [+COSE_recipient] ; in case you need multiple rounds to get decryption key
]
```

To encrypt the structure as a whole, we call our encryption method once for each level (root, recipient, etc.) recursively. For example, we encrypt the `signed_message` and put it in the `COSE_Encrypt` ciphertext, then we encrypt the decryption key and put it in the `COSE_recipient` ciphertext.

For the `Headers`,

- The `protected` fields MUST be empty. These are meant to be used with AEAD which we  don't need in this  specification (you can read more about it at [RFC 8152 section 5.3](https://tools.ietf.org/html/rfc8152#section-5.3)).

We define two ways to encrypt content:

##### Password-based encryption

For password-based encryption we don't need a receiver field (anybody who knows the password can decrypt) so we instead use the following (simplified) structure

```
COSE_Encrypt0 = [
    Headers,
    ciphertext : bstr / nil,
]

PasswordEncryption = 16 (COSE_Encrypt0)
```

The COSE spec uses the following parameters for ChaCha20/Poly1305 as specified in [10.3](https://tools.ietf.org/html/rfc8152#section-10.3):

- 256-bit key
- 128-bit tag
- 96-bit nonce

We RECOMMEND using `19162` iterations as this matches the existing password encryption in the [Yoroi encryption spec](https://github.com/Emurgo/yoroi-frontend/blob/737595fec5a89409aacef827d356c9a1605515c0/docs/specs/code/ENCRYPT.md)`.

##### Public key based encryption

We only allow encrypting based on `ED25519` public keys (the ones used for Cardano). To encrypt based on these public keys, you must

1) Compute a password consisting of 22 case-sensitive alphanumeric (a–z, A–Z, 0–9) characters (this gives you ~128 bits of entropy)

Now, for each receiver, you must

2) Compute an ephemeral key pair using `ED25519 extended`
1) Compute the shared DH secret between the private key from step (1) and the public key received (using the `exchange` functionality)
1) Use this as the password to encrypt the password in (1) using [the Yoroi encryption spec](https://github.com/Emurgo/yoroi-frontend/blob/737595fec5a89409aacef827d356c9a1605515c0/docs/specs/code/ENCRYPT.md)

The structure will look like the following:

```
COSE_Encrypt = [
  Headers,
  ciphertext : bstr / nil, ; contained signed_message encrypted with random password
  recipients : [+COSE_recipient]
]

COSE_recipient = [
  Headers,
  ciphertext : bstr / nil, ; contains random password encrypted with shared secret
]

PubKeyEncryption = 96 (COSE_Encrypt)
```

The `Headers` for the recipient MUST have a `epk` label containing the public key of the ephemeral keypair as described in the [CBOR Encoded Message Syntax](http://www.watersprings.org/pub/id/draft-schaad-cose-02.html).

#### Version

The `Headers` for the body MUST have `version: uint` in the `unprotected` field. See [Versions table](#versions) for possible version numbers.

#### Payload encoding

To solve `E3`, `signed_message` body header MUST contain `hashed: bool` as an `unprotected` header which defines whether or not we signed the `payload` OR the `Blake2b224` hash of the `payload`. The hash MUST be used in the following two cases

1) The size of the raw `payload` would otherwise be too big to fit in hardware wallet memory (see E1). Note that the exact size for which this is the case depends on the device.
1) The payload characters (ex: non-ASCII) that cannot be displayed on the hardware wallet device (see E3)

We RECOMMEND showing the user the full payload on the device if possible because it lowers the attack surface (otherwise the user has to trust that the hash of the payload was calculated correctly).

`Blake2b224` was chosen specifically because `224` bits is already a long string for hardware wallets.

### User-Facing Encoding

Once we have our top-level `encrypted_message` or `signed_message` we need to encode them in way that can be displayed to users (doesn't need to be stored and can be inferred just from the data)

We define the encoding in three parts `prefix || data || checksum` (where || means append)

### Prefix

We need a human-readable prefix. We use "CM" for "Cardano Message" followed by the message type:

- `encrypted_message`: `cme_`
- `signed_message`: `cms_`
- `mac_message`: `cmm_` (unused in this spec)

#### Data

Data is simply the `base64url` encoding of the message

#### Checksum

We use fnv32a on the data for the checksum and store it as the `base64url` encoding of its network byte order representation.

### Other remarks

We recommend usage of unprotected headers vs protected headers when possible. This is because we have to limit the amount of data passed to a hardware wallet  to satisfy E1. If the only effect of an adversary changing an unprotected header only leads to the signature not matching, then it's best to leave it unprotected.

The public key SHOULD NOT contain any chaincode information, as it could compromise child non-hardened keys. It is both a privacy and a security risk (see [here](https://bitcoin.org/en/wallets-guide#hierarchical-deterministic-key-creation) for more detail).

## Rationale: how does this CIP achieve its goals?

### Requirements

On top being usable for all cases mentioned in [Motivation](#motivation-why-is-this-cip-necessary), we also desire the following to ensure it works well with hardware wallets:

- E1 - Low runtime memory environment
- E2 - Low app size environment (cannot implement every cryptographic algorithm on the device or app size would be too big)
- E3 - Works well with limited display (some hardware wallets cannot display long text and cannot display UTF8)

### Related specifications

#### Requirement Levels [[RFC 2119](https://tools.ietf.org/html/rfc2119)]

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

#### Concise Binary Object Representation (CBOR) [[RFC 7049](https://tools.ietf.org/html/rfc7049)]

CBOR is a way to serialize structured data in a more compact way than what is allowed by JSON. It is widely used across the Cardano ecosystem and so we use it to encode the data for this specification.

#### *Concise Data Definition Language (CDDL)* [[RFC 8610](https://tools.ietf.org/html/rfc8610)]

CDDL is a human-readable CBOR notation format. CBOR schemas defined in this document are defined uinsg CDDL. We use `label = int / tstr` in several places.

#### *CBOR Object Signing and Encryption (COSE)* [[RFC 8152](https://tools.ietf.org/html/rfc8152)] 

This is a standard for how to use CBOR for message signing. It is based on the JSON equivalent *JSON Object Signing and Encryption* [RFC 7520](https://tools.ietf.org/html/rfc7520). 

We base our construction on COSE because all Cardano libraries already depend on CBOR due to its use in the base protocol (which means we don't need to introduce a new library). It is also more compact, which is useful in case data generated by this standard ever needs to be stored on-chain.

#### *CBOR Web Token (CWT)* [[RFC 8392](https://tools.ietf.org/html/rfc8392)]

This is a standard for pre-defined header elements for message signing based on the equivalent standard for JSON (*JWT* [[RFC 7519](https://tools.ietf.org/html/rfc7519)]). This allows us to standardize notions of concepts like expiration time of a signed message.

#### *Address Formats*

BECH32 ([BIP-173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki)) is a standard for encoding addresses such that they

- Are human readable (both in length and contain a common prefix)
- Can easily be displayed in a QR code
- Contain error detection through a BCH checksum

Cardano has several address types based on the era they were created in:
* `v1` - Legacy Daedalus (starts with Dd)
* `v2` - Legacy Icarus (starts with Ae2)
* `v3` - Shelley (bech32)


Although `v3` is relevant to us for encoding public keys into addresses, we do not use `bech32`'s scheme for encoding in this specification. This is because

- The payload may be too big to reasonably encode in a QR code so the benefits of using base32 are limited.
- BCH checksums are not made for large payloads and additionally the polynomial used has to be fine-tuned for the expected length (but the length of our payload varies too much in this spec)

#### fnv32a

Although Cardano Byron addresses use CRC32 (IEEE variation), due to `E1` and `E2` we use fnv32a for checksums.

This is because CRC32:

1) Has fairly few collisions compared to other hashes
2) Is moderately slower than other hashes
3) Requires more memory than alternatives (need to build a lookup table)
4) Is somewhat complex implementation (many alternatives exist)

while fnv32a:

1) Still has fairly few collisions
2) Is faster than CRC32 in general
3) Needs only O(1) memory requirement
4) Is simple to implement

In particular, using fnv32a over CRC32 frees up 1024 bytes of memory due to not having a lookup table which is significant on hardware wallets.

#### Blake2b [[RFC 7693](https://tools.ietf.org/html/rfc7693)]

Blake2b is a hash algorithm used commonly in Cardano. Notably, Blake2b-224, Blake2b-256 and Blake2b512 are used depending on the context.

#### base64url [[RFC 4648 section 5](https://tools.ietf.org/html/rfc4648#section-5)]

`base64url` allows encoding bytes in a human-readable format that is also safe to pass in URLs.

#### Other blockchain standards

Other blockchains have existing specifications for message signing, but they mostly revolve around scripts trying to validate messages. We don't leverage any of their work in particular but it may be of interest.

- [BIP-137](https://github.com/bitcoin/bips/blob/master/bip-0137.mediawiki) - simply scheme for message signing that works with P2PKH, P2PSH and bech32
- [BIP-322](https://github.com/kallewoof/bips/blob/master/bip-0322.mediawiki) - reuses Bitcoin script to process a generic signed message format

- [EIP-191](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-191.md) - encode data for Ethereum contracts
- [EIP-712](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md) - encode structs for Ethereum contracts

### Existing Code

#### Cryptography

Cardano already allows message signing within the WASM bindings. Notably,

1) [sign](https://github.com/Emurgo/cardano-serialization-lib/blob/4792b1b121e728a51686d5fcbffd33489d65c903/rust/src/crypto.rs#L279)
2) [verify](https://github.com/Emurgo/cardano-serialization-lib/blob/4792b1b121e728a51686d5fcbffd33489d65c903/rust/src/crypto.rs#L322)

You can see an example of these two functions [here](https://repl.it/repls/FlusteredSimpleFunction)

Even if you use cryptographically secure `sign` and `verify` functions, you still have the following problems:

1) No human-recognizable prefix
0) No error detection
0) User could accidentally sign a transaction or a block thinking it's harmless data

We also have a risk of a few different kinds of replay attacks

4) A dapp asks person A to sign "BOB" and then another dapp asks user B to sign "BOB". B can just use the signature from A
0) A dapp asks person A to sign "BOB" on a testnet chain. Person B then sends this signed message to the same dapp running on mainnet (same argument applies to sidechains)

### Reference implementations

- [COSE-JS](https://github.com/erdtman/cose-js)
- [Rust message signing](https://github.com/Emurgo/message-signing)

### Unresolved

This specification provides no means of Revocation.

## Path to Active

### Acceptance Criteria

- [x] There are wallets supporting creation of signed messages as per this protocol (enumerated 2023-12-19 as per [CardanoBallot list of wallets](https://voting.summit.cardano.org/user-guide) supporting CIP-8 signed messages):
  - [x] Flint
  - [x] Eternl
  - [x] Nami
  - [x] Typhon
  - [x] Yoroi
  - [x] Nufi
  - [x] Gerowallet
  - [x] Lace
- [x] There exist one or more implementations in commonly used development libraries:
  - [x] [Mesh](https://meshjs.dev/)
  - [x] `@emurgo/cardano-message-signing-asmjs`
- [x] There exist CLI Tools supporting creation and verification of signed messages:
  - [x] [cardano-signer](https://github.com/gitmachtl/cardano-signer)
- [x] There exist one or more implementations in web sites and other tools:
  - [x] SundaeSwap Governance voting

### Implementation Plan

- [x] Make this standard available as well-supported means of message signing across Cardano wallets, dApps, and CLI tools.
- [x] Support this standard in a usable reference implementation ([`@emurgo/cardano-message-signing-asmjs`](https://www.npmjs.com/package/@emurgo/cardano-message-signing-asmjs)).

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
