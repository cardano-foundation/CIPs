---
CIP: 155
Title: SRV registry
Status: Proposed
Category: Network
Authors:
  - Marcin Szamotulski <marcin.szamotulski@iohk.io>
Implementors: N/A
Discussions: 
  - Submission: https://github.com/cardano-foundation/CIPs/pull/1033
Created: 2025-04-22
License: CC-BY-4.0
---

## Abstract

This CIP defines the procedure for assigning Service Record (SRV) prefixes for Cardano applications (like `cardano-node`, `mithril`, etc.).

This creates a means of sharing authoritative information between SPOs who deploy services and _decentralised protocol_ developers who write them.

## Motivation: why is this CIP necessary?

The **Cardano Ledger** allows the use of SRV records in the **SPO** registration certificate (see [register-stake-pool]).

Having access to the ledger (either directly or through tools like `cardano-cli`) will allow decentralised protocols developers to construct networks based on registered relays. 

In this CIP, we propose to make them usable by decentralised applications running on `Cardano`.


All involved parties (SPOs, decentralised protocol developers, etc) need to agree on SRV prefixes used by various decentralised protocols and thus a public registry governed by a public CIP process is required to foster decentralised protocols that co-exist with the **Cardano** network, like **Mithril** (see [CIP#137]).

We consider decentralised protocols as applications, which construct their own network and relay on ledger peers published on the block-chain. This include node implementations, overlay networks like Mithril, or Layer 2 protocols like Hydra.

### Problem

Bootstraping networks requires sharing information about available services.

Historically, this was done by sharing IP or DNS names and PORT numbers (note that `A` or `AAAA` records do not contain PORT numbers), but this approach has its limitations.
SRV records were designed to make deployment independent of hard-coded service end-points (see [RFC#2782] or [cloudflare documentation][srv]).  They include PORT numbers together with a DNS name (point to an `A` or `AAAA` record) together with `TTL`, priority, weight, and some other data.
Thus they can be instrumental in `Cardano`, since relays are registered on the blockchain through the registration certificate.

By using SRV records in the registration certificate (which is supported by the `cardano-ledger`, but not by `cardano-node`), we wish to solve this problem not just for `Cardano` node implementation, but also for any decentralised protocol that requires constructing its own network.

SRV provides a mechanism for exposing decentralised protocols co-deployed with a node, like **mithril** or **hydra**.

Making such services discoverable is one of the key features addressed by this CIP.

In this CIP, we propose prefixes for both **Cardano** and **Mithril**; in the future, other services can be registered through a CIP process, thus starting a registry of prefixes used by the **Cardano** ecosystem.

SPOs who deploy services need to configure their system according to the registry, e.g. SPO's cardano relays node MUST be available at `_cardano._tcp.<SPO_DOMAIN_NAME>`, as other nodes on the system will be looking at this address.

Decentralised protocol developers SHOULD submit proposals to the SRV Prefix Registry, so SPOs, who deploy them, can have an authoritative information how to do it.

## Specification

### SRV Prefix Registry

The registry is available in `JSON` format [registry.json].

### SRV Prefix Semantics

When a **cardano** node implementation reads an SRV record from a ledger, it must add the _cardano_ prefix from the table above before making a DNS lookup, e.g. it should do a DNS query for `_cardano._tcp.<srv-record-from-ledger>`.

This design allows decentralised protocols to use SRV records registered in the ledger for different purposes, e.g. a **mithril** node can use them to learn about end-points of its network.

Each prefix SHOULD start with `_cardano._tcp` or `_cardano._udp`, to avoid clashes with services not related to `Cardano`.

#### SRV Registry Rules

* Each decentralised protocol can have at most one entry in the registry.
* A CIP process assigns new entries to [registry.json], after a careful consideration and consultation with all the involved parties (see #acceptance-criteria below).
* Entries cannot be removed, but can be revoked by assigning a `Revoked` status.
  This can only happen if a decentralised protocol is no longer supported.

### Example

When registering a cardano pool on `example.com` domain using an `SRV` record, one should use:
```shell
cardano-cli latest stake-pool ... --multi-host-pool-relay example.com
```
(see [register-stake-pool]); and configure SRV record at `_cardano._tcp.example.com` to point to **Cardano** relays, `_mithril._tcp.example.com` to point to **Mithril** relays (see [srv], currently under development).

A **Cardano** node implementation, when retrieving information from a registration certificate from the ledger, will receive `example.com`, and it must prepend the `_cardano._tcp` prefix to make an SRV query.  Such a query might return:

```
_cardano._tcp.example.com 86400 IN SRV 10 5 3001 cardano.example.com
```
From this, we learn that a Cardano node is available on port `3001` on IPs resolved by a regular DNS query to `cardano.example.com`.
Refer to the [Cloudflare documentation][srv] for a deeper understanding of other fields.


## Rationale: how does this CIP achieve its goals?

This CIP constructs a process to maintain SRV registry, and thus provides authritative information for SPOs and decentralised protocol developers.


## Path to Active

### Acceptance Criteria

The CIP should be accepted by:

* [ ] [**Technical Steering Committee**][tsc]

And when there's no major objection from one of the currently involved parties:

* [ ] [**Amaru Team**][amaru] accepts the proposal
* [ ] [**Cardano-Node Team**][cardano-node] accepts the proposal
* [ ] [**Gouroboros Team**][gouroboros] accepts the proposal
* [ ] [**Hydra Team**][hydra] accepts the proposal
* [ ] [**Mithril Team**][mithril] accepts the proposal

### Implementation Plan

Each **Cardano** node implementation or other tools which rely on SRV records stored in the ledger should comply with this proposal,
e.g. whenever obtaining _multi-pool relay information_ one needs to prepend a registered prefix before making an SRV query.


## Copyright

This CIP is licensed under [CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode

[CIP#137]: ../CIP-0137
[register-stake-pool]: https://developers.cardano.org/docs/operate-a-stake-pool/register-stake-pool
[RFC#2782]: https://datatracker.ietf.org/doc/html/rfc2782 
[srv]: https://www.cloudflare.com/en-gb/learning/dns/dns-records/dns-srv-record/

[amaru]: https://github.com/pragma-org/amaru
[cardano-node]: https://github.com/IntersectMBO/cardano-node
[mithril]: https://github.com/input-output-hk/mithril
[gouroboros]: https://github.com/blinklabs-io/gouroboros
[tsc]: https://docs.intersectmbo.org/intersect-overview/intersect-committees/technical-steering-committee-tsc
[hydra]: https://github.com/cardano-scaling/hydra
[register-stake-pool]: https://developers.cardano.org/docs/operate-a-stake-pool/register-stake-pool/#generate-the-stake-pool-registration-certificate

[registry.json]: ./registry.json
