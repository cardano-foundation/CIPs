---
CIP: TBD
Title: Implement Ouroboros Leios to increase Cardano throughput
Authors: Duncan Coutts <duncan.coutts@iohk.io>
Status: Draft
Type: Core
Created: 2022-11-18
License: CC-BY-4.0
---

Included documents: [*Ouroboros Leios: design goals and concepts*](leios-design.pdf)

## Abstract

As Cardano evolves, there will be increasing demand for greater network
capacity to support new and existing users and applications. The long term
solution is to rebase Cardano on the new Ouroboros Leios protocol.
Ouroboros Leios is a new member of the Ouroboros family that is designed
specifically for high throughput, without compromising security.  This will
meet expected future demands, providing a basis for continuing Cardano growth
and scalability.

## Motivation

Cardano's current throughput (measured both in data rate and available script
execution time) is adequate for the current demand. There is also some
opportunity to increase the block sizes and script execution limits to meet
emerging future demands for increased network capacity. There are however
fundamental limits to how far the block size and the script execution budget
can be pushed, while maintaining system security.

Under Ouroboros Praos, in order to ensure the security of the overall system,
blocks must be distributed across the network reliably in "$\Delta$" time slots.
This is set to be 5 seconds on the Cardano mainnet. The block relaying process
is an essentially serial process: blocks must be relayed between consecutive
block producer nodes through a series of intermediate relay nodes. The overall
time that this takes is proportional to the number of network hops between one
block producer and the next, and the network latency of each of those hops
(which must in general span the whole globe). Given that this must always
happen within 5 seconds, this puts a hard upper limit on how large each block
can be and also on how much time can be spent validating transactions and
scripts.

In order to substantially scale beyond this requires changes to the underlying
blockchain algorithm. There are significant opportunities to scale: the
network and CPU resources on most nodes are almost idle much of the time. With
a different algorithm, these resources can be used to increase the total chain
bandwidth.

## Specification

Ouroboros Leios is a substantial new design. To do it justice, we do not
include it in full in this README. Instead, as part of this CIP we include a
larger document that describes Ouroboros Leios in much more detail:

[*Ouroboros Leios: design goals and concepts*](leios-design.pdf)

There may be further updates to this design document over time. The latest
published version will be available in the
[IOG research library](https://iohk.io/en/research/library/papers/ouroboros-leios-design-goals-and-concepts/).

## Rationale

The included document sets out in more detail the limitations of the existing
design, the goals for the new design, and a design strategy that lead to the
proposed Ouroboros Leios design. It explains how the new design relates to
existing features. It sets out a very high level development strategy for how
Ouroboros Leios can be developed and integrated into Cardano.

## Path to Active

The path to the implementation of Ouroboros Leios within Cardano will be a long
one, as it will require substantial research, development and integration
effort. The proposed high level development strategy is set out in the linked
document.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0

