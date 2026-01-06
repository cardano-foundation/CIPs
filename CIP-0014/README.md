---
CIP: 14
Title: User-Facing Asset Fingerprint 
Status: Active
Category: Tokens
Authors:
  - Matthias Benkort <matthias.benkort@iohk.io>
  - Rodney Lorrimar <rodney.lorrimar@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/64
Created: 2020-02-01
License: CC-BY-4.0
---

## Abstract

This specification defines a user-facing asset fingerprint as a bech32-encoded blake2b-160 digest of the concatenation of the policy id and the asset name.

## Motivation: Why is this CIP necessary?

The Mary era of Cardano introduces the support for native assets. On the blockchain, native assets are uniquely identified by both their so-called policy id and asset name. Neither the policy id nor the asset name are intended to be human-readable data. 

On the one hand, the policy id is a hash digest of either a monetary script or a Plutus script. On the other hand, the asset name is an arbitrary bytestring of up to 32 bytes (which does not necessarily decode to a valid UTF-8 sequence). In addition, it is possible for an asset to have an empty asset name, or, for assets to have identical asset names under different policies. 

Because assets are manipulated in several user-facing features on desktop and via hardware applications, it is useful to come up with a short(er) and human-readable identifier for assets that user can recognize and refer to when talking about assets. We call such an identifier an _asset fingerprint_.

## Specification

We define the asset fingerprint in pseudo-code as:

```
assetFingerprint := encodeBech32
  ( datapart = hash
    ( algorithm = 'blake2b'
    , digest-length = 20
    , message = policyId | assetName
    )
  , humanReadablePart = 'asset'
  )
```

where `|` designates the concatenation of two byte strings. The `digest-length` is given in _bytes_ (so, 160 bits).

### Reference Implementation

#### Javascript

[cip14-js](https://www.npmjs.com/package/@emurgo/cip14-js)

#### Haskell (GHC >= 8.6.5)

<details>
  <summary>Language Extensions</summary>

```hs
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TypeApplications #-}
```
</details>

<details>
  <summary>Imports</summary>

```hs
-- package: base >= 4.0.0
import Prelude
import Data.Function
    ( (&) )

-- package: bech32 >= 1.0.2
import qualified Codec.Binary.Bech32 as Bech32

-- package: bech32-th >= 1.0.2
import Codec.Binary.Bech32.TH
    ( humanReadablePart )

-- package: bytestring >= 0.10.0.0
import Data.ByteString
    ( ByteString )

-- package: cryptonite >= 0.22
import Crypto.Hash
    ( hash )
import Crypto.Hash.Algorithms
    ( Blake2b_160 )

-- package: memory >= 0.14
import Data.ByteArray
    ( convert )

-- package: text >= 1.0.0.0
import Data.Text
    ( Text )
```
</details>

```hs
newtype PolicyId = PolicyId ByteString
newtype AssetName = AssetName ByteString
newtype AssetFingerprint = AssetFingerprint Text

mkAssetFingerprint :: PolicyId -> AssetName -> AssetFingerprint
mkAssetFingerprint (PolicyId policyId) (AssetName assetName)
    = (policyId <> assetName)
    & convert . hash @_ @Blake2b_160
    & Bech32.encodeLenient hrp . Bech32.dataPartFromBytes
    & AssetFingerprint
  where
    hrp = [humanReadablePart|asset|]
```

### Test Vectors

> :information_source: `policy_id` and `asset_name` are hereby base16-encoded; their raw, decoded, versions should be used when computing the fingerprint.

```yaml
- policy_id: 7eae28af2208be856f7a119668ae52a49b73725e326dc16579dcc373
  asset_name: ""
  asset_fingerprint: asset1rjklcrnsdzqp65wjgrg55sy9723kw09mlgvlc3

- policy_id: 7eae28af2208be856f7a119668ae52a49b73725e326dc16579dcc37e
  asset_name: ""
  asset_fingerprint: asset1nl0puwxmhas8fawxp8nx4e2q3wekg969n2auw3

- policy_id: 1e349c9bdea19fd6c147626a5260bc44b71635f398b67c59881df209
  asset_name: ""
  asset_fingerprint: asset1uyuxku60yqe57nusqzjx38aan3f2wq6s93f6ea

- policy_id: 7eae28af2208be856f7a119668ae52a49b73725e326dc16579dcc373
  asset_name: 504154415445
  asset_fingerprint: asset13n25uv0yaf5kus35fm2k86cqy60z58d9xmde92

- policy_id: 1e349c9bdea19fd6c147626a5260bc44b71635f398b67c59881df209
  asset_name: 504154415445
  asset_fingerprint: asset1hv4p5tv2a837mzqrst04d0dcptdjmluqvdx9k3

- policy_id: 1e349c9bdea19fd6c147626a5260bc44b71635f398b67c59881df209
  asset_name: 7eae28af2208be856f7a119668ae52a49b73725e326dc16579dcc373
  asset_fingerprint: asset1aqrdypg669jgazruv5ah07nuyqe0wxjhe2el6f

- policy_id: 7eae28af2208be856f7a119668ae52a49b73725e326dc16579dcc373
  asset_name: 1e349c9bdea19fd6c147626a5260bc44b71635f398b67c59881df209
  asset_fingerprint: asset17jd78wukhtrnmjh3fngzasxm8rck0l2r4hhyyt

- policy_id: 7eae28af2208be856f7a119668ae52a49b73725e326dc16579dcc373
  asset_name: 0000000000000000000000000000000000000000000000000000000000000000
  asset_fingerprint: asset1pkpwyknlvul7az0xx8czhl60pyel45rpje4z8w
```

## Rationale: How does this CIP achieve its goals?

### Design choices

- The asset fingerprint needs to be _somewhat unique_ (although collisions are plausible, see next section) and refer to a particular asset. It must therefore include both the policy id and the asset name.

- Using a hash gives us asset id of a same deterministic length which is short enough to display reasonably well on small screens.

- We use bech32 as a user-facing encoding since it is both user-friendly and quite common within the Cardano eco-system (e.g. addresses, pool ids, keys).

### Security Considerations

- With a 160-bit digest, an attacker needs at least 2^80 operations to find a collision. Although 2^80 operations is relatively low (it remains expansive but doable for an attacker), it 
  is considered safe within the context of an asset fingerprint as a mean of _user verification_ within a particular wallet. An attacker may obtain advantage if users can be persuaded 
  that a certain asset is in reality another (which implies to find a collision, and make both assets at the reach of the user). 

- We recommend however that in addition to the asset fingerprint, applications also show whenever possible a visual checksum calculated from the policy id and the asset name as specified in [CIP-YET-TO-COME](). Such generated images, which are designed to be unique and easy to distinguish, in combination with a readable asset fingerprint gives strong verification means to end users. 

## Path to Active

### Acceptance Criteria

- [x] Asset fingerprints as described have been universally adopted in: wallets, blockchain explorers, query layers, token minting utilities, NFT specifications, and CLI tools.

### Implementation Plan

- [x] Reference implementations available in both Javascript and Haskell.
- [x] Public presentation with confirmed interest in adopting this standard in advance of Mary ledger era.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
