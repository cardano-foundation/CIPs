---
CPS: 36
Title: Voluntary Block Producer Signalling
Category: Consensus
Status: Open
Authors:
    - Alex Moser <alexander.moser@cardanofoundation.org>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>

Proposed Solutions:
    - CIP-0203? | Block Producer Identifier Registry: https://github.com/cardano-foundation/CIPs/pull/1276
    - CIP-0202? | Node Observability Snapshot Protocol: https://github.com/cardano-foundation/CIPs/pull/1275
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1260
    - Early CIP discussion: https://github.com/cardano-foundation/CIPs/pull/1157
    - Ledger header version semantics: https://github.com/IntersectMBO/cardano-ledger/issues/5763
    - Porto node diversity workshop: https://forum.cardano.org/t/cardano-node-diversity-workshop-in-porto-june-2026/155216
Created: 2026-09-02
License: CC-BY-4.0
---

## Abstract

Cardano is transitioning from a single-implementation network to a multi-node network, with several independent block-producing implementations forging valid mainnet blocks under one consensus. Client diversity then becomes a first-order resilience metric, yet today it can only be estimated indirectly — nothing attributes individual blocks to a client. There is currently no standardized, voluntary way for an SPO to signal *which* software produced a given block.
For lack of better alternatives, implementations started to tag blocks ad hoc through the block header's protocol *minor* version (formally a self-reported software tag), and countless other solutions are proposed, but no ecosystem-wide agreement exists on which to use or how to encode it. 

This CPS states the problem and calls for a standard, opt-in, one-way signalling mechanism, comparable in spirit to Bitcoin's version-bits signalling (BIP 8 / BIP 9) or Ethereum's graffiti field.


## Problem

1. **No per-block attribution of producing software.** With multiple implementations forging mainnet blocks, client diversity becomes a first-order network-resilience metric. Today it can only be estimated indirectly (relay handshakes, surveys, self-reporting), none of which attribute *individual blocks* to a client.
2. **Existing channels are unstandardized and mutually incompatible.** Block producers can already signal through several channels, each with its own binding to the pool, cadence and cost:

   | Channel | Bound to the pool | Cadence | Examples |
   |---|---|---|---|
   | Header major version | yes (KES-signed block) | every block | era/hard fork readiness ([CIP-0059](../CIP-0059/README.md)) |
   | Header minor version (`self_reported_software_tag`) | yes (KES-signed block) | every block | cardano-node releases, Dingo, CIP-0203 |
   | New header or body field (needs a new era) | yes (KES-signed block) | every block | CIP-0180 |
   | Transaction metadata ("marker transactions") | only if signed with pool keys | any time | [CIP-0094](../CIP-0094/README.md) polls |
   | Pool registration and extended metadata | yes (cold key) | on update | [CIP-0006](../CIP-0006/README.md), [CIP-0151](../CIP-0151/README.md) |
   | Governance votes | yes (cold key) | per action | [CIP-1694](../CIP-1694/README.md) hard-fork and info actions |
   | Node-to-node protocol | not signed; per connection, also reaches relays | per connection | handshake ([ouroboros-network#4905](https://github.com/IntersectMBO/ouroboros-network/issues/4905)), CIP-0202 |
   | Signed message diffusion | yes (KES) | any time | [CIP-0137](../CIP-0137/README.md) (Mithril, Leios, Peras) |
   | Off-chain reporting | optional ([CIP-0022](../CIP-0022/README.md)) | ad hoc | PoolTool via cncli, surveys |

   The header minor version is the de-facto choice for client identity: never validated by the ledger, and formally a `self_reported_software_tag` from the Dijkstra era ([cardano-ledger#6084](https://github.com/IntersectMBO/cardano-ledger/pull/6084)). cardano-node uses it as a release counter and other implementations as a client identifier (e.g. Dingo: 69), but there is no agreed encoding or registry, and values already collide (67 is used by both cardano-bean and Gerolamo). 

3. **No general-purpose, low-friction (unlike Governance Info Actions), "fluid" (per block, time-unbounded) one-way signalling channel.** Beyond client identification, the ecosystem lacks an agreed low-bandwidth channel for SPOs to signal readiness or positions (feature support, informal polling, (fork readiness)), the way Bitcoin miners do via version bits, or Ethereum BPs do via graffiti. Each future need currently reinvents an ad-hoc scheme, creates technical debt, and would in some cases even require hard forks.
4. **Risk of de-facto fragmentation.** If each node implementation ships its own signalling convention, downstream consumers (explorers, dashboards, researchers, exchanges assessing network health) must special-case every client, and signals become ambiguous or unparseable.
Any solution must remain **strictly voluntary**: signalling software identity is an SPO's choice, never an obligation, and non-signalling blocks must remain fully valid and unpenalized.


## Use Cases

- **Client diversity monitoring**: explorers and dashboards showing the live share of blocks per implementation (Haskell `cardano-node`, Amaru, Dingo, …), analogous to Ethereum client-diversity dashboards.
- **Upgrade/rollout observation**: tracking adoption of a new client or version across the active stake distribution during consensus-critical transitions.
- **Readiness signalling**: While we do have CIP-1694 voting, which can be used for hard fork readiness, and have used major protocol version bits in past hard forks to monitor network readiness, SPOs could indicate support for an upcoming (soft/hard) fork or feature ahead of a governance action, or ahead of physically upgrading the node software, giving a continuous on-chain readiness signal rather than point-in-time surveys.
- **Sub-protocol participation**: which pools run Mithril signers, message diffusion ([CIP-0137](../CIP-0137/README.md)) or future Leios and Peras components, and where to reach their optional services (@Crypto2099).
- **Incident response**: when a consensus divergence or forging bug is suspected, per-block client attribution could materially speed up triage.
- **Research**: quantitative resilience analysis (e.g., "what fraction of active stake would be affected by a bug in client X?").


## Goals

1. Agree on **one** standard channel per kind of signal, client identity first, so all implementations and consumers interoperate.
2. If the solution is carried within an existing data field with a different origingating purpose (e.g. header minor version) - Define a **compact encoding** and a lightweight, openly governed **registry of client identifiers** (plausibly maintained in the CIP repository itself). 
3. Preserve **per-block attribution** where the mechanism allows it, and clearly document the trust model where it does not (self-declared, spoofable, non-cryptographic).
4. Keep the mechanism **generic**: Avoid building dedicated, over-fit features, which increase bloat and complexity of Cardano codebases. Client identity could be the first payload, but the channel should accommodate future one-way signals (feature/fork readiness bits, BIP 8/9-style semantics).
5. Guarantee the mechanism is **opt-in, zero cost, and consensus-neutral**: no ledger rule changes, no validity impact, no obligation.
6. Keep **deliberate non-signalling** distinguishable from an absent or default value: not signalling is a valid choice, and no SPO should signal unknowingly. This is especially relevant if the solution is carried within an existing data field (e.g. header minor version).


## Open Questions
- Who assigns and maintains client/version identifiers, and how are collisions and deprecations handled? 
   - CIP-203 provides an answer. 
- Opt-in or on by default? This CPS asks for opt-in; positions raised so far:
   - an optional field, with `nil` for privacy (CIP-0180);
   - on by default, with an explicit opt-out value (CIP-0203, [Amaru](https://github.com/pragma-org/amaru/pull/1446)); cardano-node already sets its release counter in every block;
   - a per-operator switch, as some operators are not allowed to disclose versions ([@gufmar](https://github.com/cardano-foundation/CIPs/pull/1157#issuecomment-4979324073)); exchange teams leave Ethereum graffiti empty for that reason, and only about 40% of graffiti carries client info ([@gufmar](https://discord.com/channels/1202416088776712253/1552017003219259505/1552087085475958831));
   - easy disabling, as exposure aids targeting ([@jeluard](https://github.com/pragma-org/amaru/pull/1446#issuecomment-5925902991), [@coot](https://github.com/IntersectMBO/ouroboros-network/issues/4905#issuecomment-5774239324));
   - public chain data should be available unless there is a heavy security concern ([Porto workshop](https://forum.cardano.org/t/cardano-node-diversity-workshop-in-porto-june-2026/155216)).


## References
- BIP 9: Version bits with timeout and delay; BIP 8: Version bits with lock-in by height (Bitcoin)
- Ethereum block graffiti, its standardised [client codes](https://github.com/ethereum/execution-apis/blob/main/src/engine/identification.md), and client-diversity monitoring
- CIP-0164 (Ouroboros Leios) — future header structure considerations
- CIP-9999 — Cardano Problem Statement process

## Acknowledgements
This CPS collates earlier work rather than originating it. Credit belongs to:
- **Header versions as a signal**: the header major version as the producer's highest supported protocol version ([CIP-0059](../CIP-0059/README.md), @JaredCorduan), long used as the hard-fork readiness metric (Intersect, PoolTool, Cexplorer, @gufmar's deployment charts); the minor version has distinguished cardano-node releases since [1.35](https://github.com/IntersectMBO/cardano-node/commit/98fade4887041c0ae98afe069c96d56ce93be429). Giving it any consensus weight would ruin it as a statistic ([@amesgen](https://discord.com/channels/1136727663583698984/1320626216599945217/1325776887053684767)).
- **Node-to-node handshake**: @coot ([ouroboros-network#3937](https://github.com/IntersectMBO/ouroboros-network/issues/3937)) and @amesgen ([#4905](https://github.com/IntersectMBO/ouroboros-network/issues/4905), closed over targeting concerns).
- **CIP-0180 candidate** ([#1157](https://github.com/cardano-foundation/CIPs/pull/1157)): @disassembler and @Crypto2099 [raised the problem](https://github.com/cardano-foundation/CIPs/pull/1157#issuecomment-4065046995) at the Paris node diversity workshop (2025) and proposed a graffiti-style producer field. Its review surfaced the constraints any solution faces:
  - free-form content invites abuse and storage cost; compact codes suffice (@gufmar, @rphair);
  - block data misses relays and stops when the chain halts (@gufmar);
  - disclosure aids targeting, so operators need a switch (@gufmar);
  - on-chain meaning should stay undefined, as changes need a hard fork (@lehins);
  - headers must stay small (@ch1bo, @colll78);
  - an extensible container for future signals (@gitmachtl);
  - isolation attacks against a signalled client (CIP-0180 security considerations).
- **CIP editor meetings** ([#130](https://discord.com/channels/971785110770831360/971785111030870087/1483501683215564841), [#143](https://discord.com/channels/971785110770831360/971785111030870087/1549451950301384825), [#144](https://discord.com/channels/971785110770831360/971785111030870087/1554533101248716961)): in an emergency, block data beats polls and PoolTool (Kevin Hammond); pool registration parameters as carrier, set aside as paid and not automatic (Ryan Williams, Kevin Hammond); a single byte (Cerkoryn); a general rather than version-only field (Thomas); no per-block marker transactions (Adam Dean).
- **Minor version as client identifier**: suggested by @KtorZ ([#1157](https://github.com/cardano-foundation/CIPs/pull/1157#discussion_r3585499525), and at a node diversity workshop), first shipped by Dingo (@wolf31o2, [dingo#1968](https://github.com/blinklabs-io/dingo/pull/1968)), and formalised by @lehins and @f-f ([cardano-ledger#5763](https://github.com/IntersectMBO/cardano-ledger/issues/5763), [#6084](https://github.com/IntersectMBO/cardano-ledger/pull/6084)).
- **Node diversity workshops** ([Paris 2025](https://forum.cardano.org/t/node-diversity-workshop-april-2025/145248), [Toulouse 2025](https://forum.cardano.org/t/cardano-node-diversity-workshop-2-toulouse-22-23-september-2025/150304), [Porto 2026](https://forum.cardano.org/t/cardano-node-diversity-workshop-in-porto-june-2026/155216)): cross-implementation observability recurred (tracing in Paris, network monitoring in Toulouse); Porto referred exposing the node version in the block header to the CIP-0180 conversation. The Buenos Aires meetup around Buidler Fest (2026) left [no written summary](https://discord.com/channels/981862537513545788/1359518656907837523/1518550417477337118).
- **Network-level observability**: @gufmar (CIP-0202).
- **Review of this CPS** ([#1260](https://github.com/cardano-foundation/CIPs/pull/1260)): @rphair, @yHSJ, @lehins, @Crypto2099.

## Copyright
This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
