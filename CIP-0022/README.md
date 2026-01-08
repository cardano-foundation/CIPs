---
CIP: 22
Title: Pool operator verification
Status: Active
Category: Tools
Authors:
  - Andrew Westberg <andrewwestberg@gmail.com>
  - Martin Lang <martin@martinlang.at>
  - Ola Ahlman <ola@ahlnet.nu>
Implementors:
  - CNCLI
  - JorManager
  - StakePoolOperator Scripts
  - CNTools
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/102
Created: 2021-06-21
License: CC-BY-4.0
---

## Abstract

This proposal describes a method allowing a stakepool operator to provide credentials to verify that they are the rightful manager for their stakepool.

## Motivation: Why is this CIP necessary?

Many websites such pooltool.io, adapools.org, and others need to allow pool operators special access to modify the way their pool appears on the website. SPOCRA and other organizations also have a need to allow voting on proposals and ensure that each vote cast is from a valid pool operator. Today, these sites and organizations all use different techniques for validating pool operators.

pooltool.io - Validates operators by receiving 1 ada spent from the pool's registered rewards account

adapools.org - Validates operators by requesting that the operator include a special generated value in their extended pool metadata json file.

This proposal is to simplify and streamline a single approach that all can reference in order to verify that a pool operator is who they say they are.

## Specification

In order to achieve the goals of this CIP, the pool operator needs to provide some credential or credentials to the validating party which cannot be spoofed. The VRF pool keys and VRF signature algorithm implemented in libsodium are chosen to build and provide this credential/signature. This signature can then be validated and the operator verified without ever exposing any of the pool's private key information. This technique is very similar to verifying that a block produced by another pool is valid. The only difference is that instead of validating the slot seed for a given pool, we're validating a pre-determined message hash.

### Verification Steps:

1. Stakepool Operator (SPO) sends their pool_id and public pool.vrf.vkey to the Validating Server (VS)
2. VS validates that the vrf hash in the pool's registration certificate on the blockchain matches the blake2b hash of the sent vkey. Note: The VS should use the latest registration certificate on the chain for matching as the VRF is a "hot" key and can be changed at any time by the pool operator. A single point-in-time verification is sufficient to properly identify the pool operator.
3. The VS sends a challenge request to the SPO which is the domain of the VS and a random 64-byte nonce.
4. The SPO creates a blake2b hash of "cip-0022{domain}{random_nonce}" and then signs this with their private VRF key.
5. The SPO sends this to VS as the challenge response within a 5-minute window to the VS
6. The VS validates the signed challenge response

### Code Example (Validating server):

```kotlin
// Server side, create inputs for a challenge. Store this and only allow responses
// within 5 minutes to be successful.
val random = SecureRandom()
val domain = "pooltool.io"
val nonce = ByteArray(64)
random.nextBytes(nonce)
println("domain: $domain, nonce: ${nonce.toHexString()}")
```

### Code Example (Pool Operator side):

```kotlin
// Node operational VRF-Verification-Key: pool.vrf.vkey
//{
//    "type": "VrfVerificationKey_PraosVRF",
//    "description": "VRF Verification Key",
//    "cborHex": "5820e0ff2371508ac339431b50af7d69cde0f120d952bb876806d3136f9a7fda4381"
//}
//
// Node operational VRF-Signing-Key: pool.vrf.skey
//{
//    "type": "VrfSigningKey_PraosVRF",
//    "description": "VRF Signing Key",
//    "cborHex": "5840adb9c97bec60189aa90d01d113e3ef405f03477d82a94f81da926c90cd46a374e0ff2371508ac339431b50af7d69cde0f120d952bb876806d3136f9a7fda4381"
//}

// We assume the pool operator has access to the pool's vrf secret key
val skeyCbor = "5840adb9c97bec60189aa90d01d113e3ef405f03477d82a94f81da926c90cd46a374e0ff2371508ac339431b50af7d69cde0f120d952bb876806d3136f9a7fda4381".hexToByteArray()
val vrfSkey = (CborReader.createFromByteArray(skeyCbor).readDataItem() as CborByteString).byteArrayValue()
val vkeyCbor = "5820e0ff2371508ac339431b50af7d69cde0f120d952bb876806d3136f9a7fda4381".hexToByteArray()
val vrfVkey = (CborReader.createFromByteArray(vkeyCbor).readDataItem() as CborByteString).byteArrayValue()

// Client side, construct and sign the challenge
val challengeSeed = "cip-0022${domain}".toByteArray() + nonce
val challenge = SodiumLibrary.cryptoBlake2bHash(challengeSeed, null)
println("challenge: ${challenge.toHexString()}")

val signature = SodiumLibrary.cryptoVrfProve(vrfSkey, challenge)
println("signature: ${signature.toHexString()}")
```

### Code Example (Validating server):

```kotlin
// Server side, verify the message based on only knowing the pool_id, public vkey, signature, and constructing
// the challenge ourselves the same way the client should have.
val challengeSeed = "cip-0022${domain}".toByteArray() + nonce
val challenge = SodiumLibrary.cryptoBlake2bHash(challengeSeed, null)

// Get the vkeyHash for a pool from the "query pool-params" cardano-cli command
// This comes from the pool's registration certificate on the chain.
val vkeyHash = "f58bf0111f8e9b233c2dcbb72b5ad400330cf260c6fb556eb30cefd387e5364c".hexToByteArray()

// Verify that the vkey from the latest minted block on the blockchain (or the client supplied if they
// haven't yet minted a block) is the same as the one on-chain in the pool's registration certificate
val vkeyHashVerify = SodiumLibrary.cryptoBlake2bHash(vrfVkey, null)
assertThat(vkeyHash).isEqualTo(vkeyHashVerify)

// Verify that the signature matches
val verification = SodiumLibrary.cryptoVrfVerify(vrfVkey, signature, challenge)
println("verification: ${verification.toHexString()}")

println("Verification SUCCESS!")
```

### Code Example output:

```
vrfSkey: adb9c97bec60189aa90d01d113e3ef405f03477d82a94f81da926c90cd46a374e0ff2371508ac339431b50af7d69cde0f120d952bb876806d3136f9a7fda4381
vrfVkey: e0ff2371508ac339431b50af7d69cde0f120d952bb876806d3136f9a7fda4381
domain: pooltool.io, nonce: c936ab102a86442c7120f75fa903b41d9f6f984a9373a6fa0b7b8cb020530318bdec84512468681c7d8454edf3a0e0bf21f59c401028030a8fb58117edc8b03c
challenge: 6977c480a3acb4c838ba95bb84d1f4db1c2591ea6ebe5805ed0394f706c23b05
signature: a3c9624aa14f6f0fba3d47d3f9a13bb55f0790eacd7bad9a89ce89fecb9e7eb8ca0d19aea8b6a7be39ae3e8b9768211b4d8aa789e82c1e150826fe15a0b0323f08e18635deb94c49d7f4421750d44903
signatureHash: 9ca4c7e63ba976dfbe06c7a0e6ec4aec5a5ef04b721ffc505222606dfc3d01572ddce3b55ac5c9470f061f137dafe31669794ea48118d1682d888efbe0cb4d1a
verification: 9ca4c7e63ba976dfbe06c7a0e6ec4aec5a5ef04b721ffc505222606dfc3d01572ddce3b55ac5c9470f061f137dafe31669794ea48118d1682d888efbe0cb4d1a
Verification SUCCESS!
```

## Rationale: How does this CIP achieve its goals?

Implementing this simplifies and commonizes the process for verifying that a pool operator is who they say they are in 3rd party systems. Having a common way of verify pool operators also allows simple integration into pool management tools.

There is also some overlap with [CIP-0006](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0006/README.md#extended-metadata---flexible-but-validable) and the `rawdata-sign` command although it specifies generating a new key instead of utilizing the pool's existing `vrf.skey` to sign like this proposal.

## Path to Active

### Acceptance Criteria

- [x] Tools that have implemented, or are implementing, this proposal:
  - [x] [CNCLI](https://github.com/AndrewWestberg/cncli)
  - [x] [JorManager](https://bitbucket.org/muamw10/jormanager/)
  - [x] [StakePoolOperator Scripts](https://github.com/gitmachtl/scripts)
  - [x] [CNTools](https://cardano-community.github.io/guild-operators/#/Scripts/cntools)

### Implementation Plan

- [x] Consensus between providers of the most popular tools and CLIs for stake pool operators that this approch is viable and desirable.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
