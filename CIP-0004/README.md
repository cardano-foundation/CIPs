---
CIP: 4
Title: Wallet Checksums
Status: Proposed
Category: Wallets
Authors:
  - Ruslan Dudin <ruslan@emurgo.io>
  - Sebastien Guillemot <seba@dcspark.io>
Implementors:
  - Ruslan Dudin <ruslan@emurgo.io>
  - Sebastien Guillemot <seba@dcspark.io>
Discussions:
  - https://forum.cardano.org/t/cip4-wallet-checksum/32819
  - https://github.com/cardano-foundation/CIPs/pull/4
Created: 2019-05-01
License: Apache-2.0
---

## Abstract

We introduce a checksum algorithm to help users verify they are restoring the right wallet before the restoration actually takes place.

## Motivation: why is this CIP necessary?

Users occasionally enter the wrong [mnemonic](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) for their wallet. In this case, they simply see a 0 ADA wallet after syncing is over. This not only wastes the user's time, in the worst case it makes them think they either lost all their ADA or think there is a bug in the wallet implementation.

To solve this, we introduce a checksum that can be computed without having to perform wallet restoration.

## Specification

First, it's important to note that the method for generating a checksum is heavily dependent on the type of wallet (ex: BIP44, etc.). We outline an algorithm that works with most, but not all, types of wallet.

### Requirements for checksum

1) Easily recomputed without access to mnemonic, private key or other similarly sensitive data
2) Does not reveal anything about the wallet (irreversible -- cannot tell addresses, private key, etc. from just seeing the checksum)
3) Negligible chance of collision
4) Easy to memorize for the user
5) Can be easily saved both digitally or on paper

### Implementation Outline

To satisfy (1), the checksum SHOULD be seeded from the public key for the wallet. Notably, in the [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) case, it should come from the bip44 account derivation level's public key.
**Note**: For HD wallets, the public key used SHOULD contain the chaincode also because we need to make sure that not just the public key, but all its child keys also, are properly generated.

To satisfy (2) and (3), the a hash of the public key is used

To satisfy (4) and (5), we generate for an *ImagePart* and a *TextPart*. The brain can roughly remember images allowing you to quickly dismiss checksums that look totally different. However, since images can sometimes be similar, a *TextPart* is also provided for double-checking. Additionally, if the user does not have access to a printer, the text part can be easily written down by hand on a piece of paper to satisfy (5).

## Rationale: how does this CIP achieve its goals?

We first provide a template for the code, explain the template and then provide the parameterization we use for Cardano

```js
function calculateChecksum(publicKeyHash: string /* note: lowercase hex representation */) {
  const hash = hash1(publicKeyHash);
  const [a, b, c, d] = hash_to_32(hash); // get a 4 byte value from the hash
  const alpha = `ABCDEJHKLNOPSTXZ`; // take 16 letters from the alphabet that are easy to distinguish

  // construct the TextPart from a group of letters and a group of numbers
  const letters = x => `${alpha[Math.floor(x / 16)]}${alpha[x % 16]}`;
  const numbers = `${((c << 8) + d) % 10000}`.padStart(4, '0');
  const id = `${letters(a)}${letters(b)}-${numbers}`;

  return {
    hash, // used to generate the ImagePart
    id, // used as the TextPart
  };
}
```

### TextPart rationale

For ease of perception it seems that short alphanumeric sequences are the best for humans to remember, especially when letters and numbers are separated and not mixed together.

#### Letter part

For letters, we render the bytes in hex, but replace the alphanumeric used in hex with this letter-only alphabet:

`A B C D E J H K L N O P S T X Z`

This alphabet satisfies the following requirements:

1) Has exactly 16 letters (one-to-one mapping with 2 bytes in HEX)
1) Does not contain characters that look too much like each other
1) Minimizes occurrences of undesirable words in [this list](https://www.noswearing.com/fourletterwords.php).

#### Number part

The last two bytes are compressed to a 4-digit number. For this we will simply take the last 4 digits of the 16-bit integer number constructed from 2 bytes as `((A << 8) + B) % 10000` (zero-padded).

This above produces 10000 unique values across all possible values of A and B and giving maximum of 7 potential collisions per value and 6.5 average collisions per value, which is the minimum, given the fact that we reduce maximum potential number 65536 to 4 digits.
**Note**: resulting number is zero-padded to 4 digits.

### ImagePart rationale

For the image, we take the result of `hash1` and use it as the seed for the [blockies](https://github.com/ethereum/blockies) library.

This library in particular has the following benefits:

- Has been audited
- Used by other blockchains and therefore has common libraries for implementation

**Note**: This library internally re-hashes its input to a 128-bit entropy string

### Hash algorithms used in Byron + ITN

For `hash1`, we use `blake2b512`. [Blake2b](https://tools.ietf.org/html/rfc7693) is a standardized hash function that is used in Cardano for other purposes like key derivations. Reusing blake2b means one less dependency. We use `512` bytes of output to try and future-proof this algorithm (better to spread the entropy across more bits than needed than end up not capturing the full entropy in the future).

For `hash_to_32` we use CRC32. We hash a second time for the following:

1) The *TextPart* is constructed from 4 bytes (2 for letters, 2 for numbers) and so we need to project the result of `hash1` down to 4 bytes.
2) We don't want to simply take the last 4 bytes of `hash1` because that would reveal part of the input used to generate the *ImagePart*. Although strictly speaking this should not be of a concern (since the result of `hash1` doesn't reveal any information about the original key), we take this as a precaution.
3) `CRC32` is used in the Byron implementation of Cardano as a checksum for addresses, meaning no additional dependency has to be added.

Although there is no specification for CRC32 and many variations exist, in Cardano we use the CRC-32-IEEE variation. You can find a C implementation [here](https://github.com/cardano-foundation/ledger-app-cardano/blob/3f784d23c1b87df73cda552ef01428d3e2733237/src/crc32.c#L6)

### Hash algorithms used in Shelley mainnet

1) For `hash1`, we still use `blake2b512` but we now set the blake2b `personalization` to the the utf-8 byte equivalent of `wallets checksum` (exactly 16 utf-8 bytes in length) to avoid collision with any other standard that decides to hash a public key.
2) For `hash_to_32`, we no longer use `crc32` for the following reasons:

- It has multiple competing implementations all called `crc32` (easily to get the wrong implementation library)
- It requires building a lookup table, making it slower than other hashing algorithms for similar safety
- Cardano no longer uses `crc32` in the Shelley mainnet as addresses now use [BIP173 - bech32](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki) which has its own checksum algorithm.

Instead, we replace it with [FNV-1a](https://tools.ietf.org/html/draft-eastlake-fnv-10) in 32-bit mode. FNV-1a is fast, easy to implement inline and gives good empirical distribution.

### When no public key is present

Note that a different construction is needed for wallet types which do not have a public key (such as a balance tracking application which simply manages a set of addresses). In the balanace tracking case, simply hashing the set of addresses used is possible, but it means that adding & removing an address would change the checksum (possibly unintuitive). Since the checksum is meant to represent the wallet itself, we also cannot run a checksum on the name of the wallet or any other user-inputted data.

## Path to Active

### Acceptance Criteria

- [x] There exists a reference implementation with test vectors.
- [ ] Checksums are adopted by two or more wallets.
  - [x] Yoroi

### Implementation Plan

- [x] Reference implementations:
  - [Javascript](https://github.com/Emurgo/CIP4)

## Copyright

This CIP is licensed under Apache-2.0
