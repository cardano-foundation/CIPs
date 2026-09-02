---
CPS: ?
Title: Voluntary Block Producer Software Signalling
Category: Consensus/Monitoring (?)
Status: Open
Authors:
    - Alex Moser <alexander.moser@cardanofoundation.org>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>

Proposed Solutions: []
Discussions:
    - /
Created: 2026-09-02
License: CC-BY-4.0
---

## Abstract

Cardano is transitioning from a single-implementation network to a multi-node network, with several independent block-producing implementations expected to forge valid mainnet blocks under one consensus. There is currently no standardized, voluntary way for an SPO to signal *which* software produced a given block. 
Two ad-hoc mechanisms are known — the free bytes of the protocol *minor* version in the block header, and small on-chain marker transactions (~60 bytes) — but no ecosystem-wide agreement exists on which to use or how to encode it. 

This CPS states the problem and calls for a standard, strictly opt-in, one-way signalling mechanism, comparable in spirit to Bitcoin's version-bits signalling (BIP 8 / BIP 9) or Ethereum's graffiti field.


## Problem

1. **No per-block attribution of producing software.** Once multiple implementations forge mainnet blocks, client diversity becomes a first-order network-resilience metric. Today it can only be estimated indirectly (relay handshakes, surveys, self-reporting), none of which attribute *individual blocks* to a client.
2. **Existing options are unstandardized and mutually incompatible.**
   - *Protocol minor version in the block header*: effectively free information (the field is vestigial for hard-fork readiness signalling in the Conway governance era). It is emitted by the block producer itself, so attribution is per-block and tied to the forger — but there is no agreed encoding, no identifier registry, and uncoordinated use by different clients would collide or be misread.
   - *Marker transactions* (~60 bytes, e.g. metadata-labelled): flexible and extensible, but not intrinsically bound to block production; a transaction author is not necessarily the block producer, so attribution is weaker and requires convention.
3. **No general-purpose, low-friction (unlike Governance Info Actions), "fluid" (per block, time-unbounded) one-way signalling channel.** Beyond client identification, the ecosystem lacks an agreed low-bandwidth channel for SPOs to signal readiness or positions (feature support, informal polling, (fork readiness)), the way Bitcoin miners do via version bits, or Ethereum BPs do via graffiti. Each future need currently reinvents an ad-hoc scheme, creates technical debt, and would in some cases even require hard forks.
4. **Risk of de-facto fragmentation.** If each node implementation ships its own signalling convention, downstream consumers (explorers, dashboards, researchers, exchanges assessing network health) must special-case every client, and signals become ambiguous or unparseable.
Any solution must remain **strictly voluntary**: signalling software identity is an SPO's choice, never an obligation, and non-signalling blocks must remain fully valid and unpenalized.


## Use cases

- **Client diversity monitoring**: explorers and dashboards showing the live share of blocks per implementation (Haskell `cardano-node`, Amaru, Dingo, …), analogous to Ethereum client-diversity dashboards.
- **Upgrade/rollout observation**: tracking adoption of a new client or version across the active stake distribution during consensus-critical transitions.
- **Readiness signalling**: While we do have CIP-1694 voting, which can be used for hard fork readiness, and have used major protocol version bits in past hard forks to monitor network readiness, SPOs could indicate support for an upcoming (soft/hard) fork or feature ahead of a governance action, or ahead of physically upgrading the node software, giving a continuous on-chain readiness signal rather than point-in-time surveys.
- **Incident response**: when a consensus divergence or forging bug is suspected, per-block client attribution could materially speed up triage.
- **Research**: quantitative resilience analysis (e.g., "what fraction of active stake would be affected by a bug in client X?").


## Goals

1. Agree on **one** standard mechanism (header minor-version bytes, marker transactions, or a defined combination) so all implementations and consumers interoperate.
2. Define a **compact encoding** and a lightweight, openly governed **registry of client identifiers** (plausibly maintained in the CIP repository itself).
3. Preserve **per-block attribution** where the mechanism allows it, and clearly document the trust model where it does not (self-declared, spoofable, non-cryptographic).
4. Keep the mechanism **generic**: Avoid building dedicated, over-fit features, which increase bloat and complexity of Cardano codebases. Client identity could be the first payload, but the channel should accommodate future one-way signals (feature/fork readiness bits, BIP 8/9-style semantics).
5. Guarantee the mechanism is **opt-in, zero cost, and consensus-neutral**: no ledger rule changes, no validity impact, no obligation.


## Open questions
- Header minor version vs. marker transaction — or header for identity (producer-bound) plus transactions for richer, occasional signals?
- Who assigns and maintains client/version identifiers, and how are collisions and deprecations handled? A CIP, a repo?
   - In Cardano, we have lots of precedence in that regard, as we maintain various registries already. 
- How should consumers treat the signal given it is unauthenticated and trivially spoofable — is "self-declared" an acceptable trust model, or is binding to the operational (KES/VRF) credentials desirable?
- How does the mechanism survive planned header changes (e.g., Ouroboros Leios / CIP-0164 era block structure)?
- Should the standard define BIP 8/9-style state machines (start/timeout/lock-in) for readiness signals over a certain period of time (like the difficulty adjustment period, or an epoch), or is it a continously rolling window and keep it a raw channel on purpose, leaving semantics to per-signal CIPs?
- Are there privacy or targeting concerns for SPOs who disclose their software (e.g., exploit targeting of a known-vulnerable client), and should the standard note this trade-off explicitly?


## References
- BIP 9: Version bits with timeout and delay; BIP 8: Version bits with lock-in by height (Bitcoin)
- Ethereum block `extraData` / "graffiti" convention and client-diversity monitoring
- CIP-0164 (Ouroboros Leios) — future header structure considerations
- CIP-9999 — Cardano Problem Statement process
