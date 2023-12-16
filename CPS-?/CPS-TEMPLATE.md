---
CPS: ?
Title: CIP67 prefixes for validity/auth twinned tokens
Status: Open
Category: ?
Authors:
    - waalge<kompactio@proton.me>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 16/12/2023
Categories:
    - Tokens
---

## Abstract

CIP67 labels for twinned tokens that do not follow CIP68 datum stipulations.

## Problem

In Plutus SCs native assets, particularly NFTs, are used to indicate validity of data and/or authorize actions.
It is a common pattern to twin two tokens: a validity token locked at SC address spendable only if the corresponding auth token is also spent. 
This pattern is present in CIP68, but this CIP also specifies the datum type which is not, in general, suitable. 

Tooling is being built around CIP68 which does helpful things like recognize twinned tokens.
Simply reusing the labels would allow us to leverage these tools - no new CIP required. 
However, such tools will perform suboptimally on handling the datum. 

## Use cases

- Like CIP68, but with a different datum types.

## Goals

Allow for the development and use of tooling wrt twinned tokens to be coherent.

## Open Questions

### Is there a enough of a problem here to warrant a CIP? 

This CPS exists because CIP68 is an example of a more general and elementary pattern.
Is this too elementary to want a CIP?

Twinned tokens considered here covers a tranche of cases.
For any such CIP there will be a YMMV attached.
But at some point more exotic cases will emerge: one-to-many, many-to-one, many-to-many twins? tiered auth? ...
We cannot shoehorn all possible use-cases into a single CIP. 
Is there enough of a coherent problem to warrant a CIP?
Should a solution anticipate extensibility? How much?

### What should a solution be?

A solution might involve requesting bands of CIP67 be reserved for related purposes. 
For example, validity tokens will have hex label `XX0643b0` where `XX` might be used to indicate the data format. 
This would then be CIP68 compatible with `XX = 00`.

### Is CIP67 fit for (this) purpose? 

Following from the above it is reasonable to consider that if this is worth doing, 
is it worth trying to be compatible with existing CIPs?
CIP67 has only 2 bytes of space.
The `XX` here can only represent 128 cases (I think) - over or under allocating is an immediate concern. 

A short digression on a replacing/ extending CIP67 with a spec allowing for more bytes.

I'm not familiar with why CIP67 has padding at both ends. 
(The beginning provides a cheap filter of definitely not cip67 compliant tokens. The end?)
Given that this is how it is, we could use it to introduce the following extension. 
Labels will have the following form: 
```
  [ 0000 | 8*N bits label_num | 8 bits checksum | 0000 ]
```
for natural number `N`. For example, `N=2` is CIP67.
(We may wish to exclude the pathological cases where there is more than one parsing.)

Declaring a CIP with, say, `N=10` might be a naive resolution to the label size concern. 
The 32 bytes of token name real-estate are often subject to other requirements that there is no one-size-fits-all `N`. 

For example, suppose a dapp requires the functionality that twinned tokens allows. 
For general dapp coherence the policy id is fixed.
The mint of twins is at user's discretion, thus the dapp must somehow ensure the twins are genuine NFTs. 
There are a few options to prevent NFTs becoming FTs.
The simplest is to create essentially unique tags on each mint by hashing a spent oref, truncating it, and setting it as the suffix of a token name.

Say we wish to have 160-bit tag (20bytes. Overkill? maybe). 
We also want a human friendly label, say 5 bytes to match a ticker.
That leaves only 7 bytes for the prefix and thus 5 bytes of label real-estate.

### A good time to specify how to specify data formats? 

Is it sensible that the same CIP specifies how to "register" or "declare" a new datum types?
