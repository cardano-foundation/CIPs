---
CIP: 59
Title: Terminology Surrounding Core Features
Status: Active
Category: Meta
Authors:
  - Jared Corduan <jared.corduan@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/274
Created: 2022-06-09
License: CC-BY-4.0
---

## Abstract

This CIP seeks to clarify the language around groups of features.
At the very least, it provides some history.

## Motivation: Why is this CIP necessary?

When @CharlesHoskinson conceived of Cardano, he had a vision for what features the network would support.
This vision is still present on the [Cardano roadmap website](https://roadmap.cardano.org).
In particular, the features are grouped into "phases", which are mostly named after poets (Goguen is the exception).
The word "era" is used interchangeably with "phases" on the roadmap.

### History

The word "era", however, has been muddled by an implementation detail in the Cardano ledger.
The Shelley phase was implemented as an entire re-write of the code from the Byron phase.
While the consensus layer for the Shelley phase was written with an abstraction in place for the ledger,
the ledger layer was not written with any abstractions to make future phases possible.

Upon starting into the Goguen phase, the ledger team retroactively introduce a notion of "era"
into the ledger code, and deemed the Shelley features "the Shelley era".
In hindsight, however, the word "era" in unfortunate, since the Goguen phase was completed in the ledger
by what was called "the Allegra era, the Mary era, the Alonzo era, and the Babbage era".

The names Allegra and Mary were chosen for their connection to the poet Percy Shelley,
and were only intended to be used as
[variable names](https://github.com/input-output-hk/cardano-ledger/blob/1cbf1fc2bb005a8206e5b5a7cdf44d35baaca455/eras/shelley-ma/impl/src/Cardano/Ledger/Allegra.hs#L40)
for a very specific abstraction used in the ledger code.
(The story is even a bit more confusing, since the Allegra and Mary era share a lot of code
and are specified together in the "Shelley-MA
[specification](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/mary-ledger.pdf).
The letters "MA" can hilariously refer to both "Mary Allegra" and "Multi-Assets".)

How did we then go from poets to Alonzo?
Recall that "Goguen" was the only non-poet named in the phases on the Cardano roadmap.
We found it fitting, therefore, to name the ledger era which introduced Plutus
after the person who invented the lambda calculus
(Plutus Core uses a variant of [system F](https://en.wikipedia.org/wiki/System_F).).

Moreover, going forward, we decided to use names in A, B, C, ... order, names coming from
other people who walk the line between mathematics and computer science.
One lack of consistency to notice is that we have used both first and last names.
The inconsistency was mostly driven by the desire to find short and memorable names.

Another complication to the story is the notion of "intra-era hard forks".
A new era _must_ be introduced with a hard fork, but the ledger can also
change semantics during a controlled hard fork with another mechanism, namely
an intra-era hard fork.
This is an implementation detail which involves bumping the major protocol version
but not creating a new ledger era.
The Alonzo era experienced an intra-era hard fork when going from major protocol version 5 to 6.

Yet another complication stems from the named releases.
We chose to honor the late Cardano community member and Bulgarian mathematician Vasil Dabov
by naming a release date after him.
The ledger era after the Alonzo era was named Babbage.
Babbage is a feature set, Vasil is a release date which ushered in the Babbage era.

Lastly, it is important to understand that not all of the semantic changes to the Cardano network involve the ledger,
though the changes to the ledger are often the most user-facing.
Changes to the consensus protocol or the networking layer may also involve a hard fork.
Moreover, there is an abstraction that sits between the consensus and ledger layers,
which we have named the "protocol" (a regrettably vague name).

The distinction between the ledger protocols and the ledger eras
correspond roughly to how block headers are validated (protocol) versus
how block bodies are validated (era).
The Shelley era used the "transitional Praos" protocol (or TPraos for short).
It consisted of Praos together with a transition system to move away from Ouroboros-BFT.
The Babbage era replaced TPraos with Praos.

## Specification

A table of all the features, as of the time this CIP was submitted, can be found [here](./feature-table.md).

Note that the protocol version mentioned above is unrelated to the node-to-node and node-to-client protocol versions.
The consensus layer maintains a versioning scheme for the node queries which does not necessarily
align with the protocol version described in this CIP.

Note also that the protocol version present inside of each block header indicates the maximum supported protocol version
that the block producer is capable of supporting (see section 13, Software Updates, of the
[Shelley ledger specification](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf)).

Let us use the following language:

* **Phase** - A phase in Cardano is a high level collection of features described on the Cardano roadmap.
* **Ledger Era** - A ledger era (or era for short if there is no confusion) in Cardano is a collection of ledger features introduced at a hard fork. Moreover, starting with the Alonzo era, they will be named after mathematicians and computer scientists (preferably both!) in A, B, C, ... ordering. Some letters might prove challenging.
* **Intra-era Hardfork** - An intra-era hard fork in Cardano is a small and focused semantic change to the ledger which requires a hard fork.
* **Consensus mechanism** - A consensus mechanism in Cardano is a collection of consensus features introduced at a hard fork. Historically, these have had the name "Ouroboros" in them.
* **Ledger Protocol** - A ledger protocol in Cardano is a collection of ledger features sitting between the consensus layer and the ledger layer, roughly characterized by block header validation.
* **Release Dates** - When we are confident about the release of a new features, we can chose to honor Cardano community members by naming a date after them.

## Rationale: How does this CIP achieve its goals?

If we can agree to common language, it will greatly improve communication among ourselves and also with new community members.

### Backwards compatibility

Since this is an issue of language, we will strive to use consistent language going forward, and we can correct misalignment when we find it.

## Path to Active

### Acceptance Criteria

- [x] Terminology has met with positive response from community.
- [x] Terminology has continued in use particularly in the CIP process and the Feature Table has been kept up to date.

### Implementation Plan

- [x] Ledger architects have committed to standardising their language for the community.
- [x] Table of strict definitions, with protocol versions and block heights, is produced to remove any ambiguities.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
