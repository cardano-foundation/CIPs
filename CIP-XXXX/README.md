---
CIP: ?
Title: Babel Fee Offers — Off-Chain Transmission and Service Layer for Nested Transactions
Category: Network
Status: Proposed
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>
    - William Wolff <william.wolff@iohk.io>
    - Dana Alibrandi <dana.alibrandi@iohk.io>
    - Nicolas Henin <nicolas.henin@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/779   # CPS-0015 "Intents for Cardano"
    - https://github.com/cardano-foundation/CIPs/pull/880   # CIP-0131 "Transaction swaps"
    - https://github.com/cardano-foundation/CIPs/pull/466   # CIP-0089 beacon tokens
    # TODO before submission: this proposal's own PR, and the CIP-118 thread it
    # follows from.
Created: 2026-08-14
License: CC-BY-4.0
---

## Table of contents

- [Abstract](#abstract)
- [Motivation: Why is this CIP necessary?](#motivation-why-is-this-cip-necessary)
- [Specification](#specification)
  - [Architecture](#architecture)
  - [Terminology](#terminology)
    - [Imported from CIP-118, not redefined by this CIP](#imported-from-cip-118-not-redefined-by-this-cip)
    - [Defined by this CIP](#defined-by-this-cip)
  - [Offer envelope](#offer-envelope)
  - [Network topology and roles](#network-topology-and-roles)
  - [Transport bindings](#transport-bindings)
    - [Binding A — HTTPS](#binding-a--https)
    - [Binding B — libp2p gossipsub](#binding-b--libp2p-gossipsub)
    - [Further bindings](#further-bindings)
  - [Validation](#validation)
    - [Transport-binding checks — imposed by the binding](#transport-binding-checks--imposed-by-the-binding)
    - [Stateless checks — performed by publishers, relays, services](#stateless-checks--performed-by-publishers-relays-services)
    - [Chain-state checks — performed by publishers, services](#chain-state-checks--performed-by-publishers-services)
    - [Pre-inclusion checks — performed by services](#pre-inclusion-checks--performed-by-services)
  - [Routing and filtering](#routing-and-filtering)
    - [Forwarding](#forwarding)
    - [Filter-key kinds](#filter-key-kinds)
    - [Routing keys](#routing-keys)
  - [Constraint language](#constraint-language)
  - [Protocol constants](#protocol-constants)
  - [Offer lifecycle](#offer-lifecycle)
  - [Batch construction](#batch-construction)
  - [Liquidity strategy](#liquidity-strategy)
  - [On-chain registration of relays and services](#on-chain-registration-of-relays-and-services)
  - [Service profile](#service-profile)
  - [Price hints](#price-hints)
  - [Security considerations](#security-considerations)
- [Rationale: How does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)
  - [Components built](#components-built)
  - [What this makes possible](#what-this-makes-possible)
  - [Work blocked on prerequisites](#work-blocked-on-prerequisites)
  - [Alternatives, prior art and compatibility](#alternatives-prior-art-and-compatibility)
- [Path to Active](#path-to-active)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Implementation Plan](#implementation-plan)
- [Versioning](#versioning)
- [References](#references)
  - [Cardano Improvement Proposals and Problem Statements](#cardano-improvement-proposals-and-problem-statements)
  - [External standards](#external-standards)
  - [Academic and cryptographic references](#academic-and-cryptographic-references)
  - [Prior art and related implementations](#prior-art-and-related-implementations)
  - [Internal documents](#internal-documents)
- [Copyright](#copyright)

## Abstract

[CIP-118][] lets a user author a sub-transaction 
that does not balance on its own, e.g.
having more of a user-defined token in the inputs than the outputs, and vice-versa
for ADA (such type of sub-transaction is called a *babel fee offer*). 
Another party can include this sub-transaction in a fully valid 
top-level transaction, which can then be posted on-chain. 
The Nested Transactions CIP specifies the required ledger changes to support
this, but the ledger rules alone are not enough to use it: a sub-transaction
that does not balance cannot be posted as-is, so the feature does nothing
until some other party finds it, judges it worth completing, and builds the
top-level transaction that carries it. That party, and the means of reaching it, are
entirely off-chain, and no such mechanism exists.
This CIP specifies such a mechanism, including all the relevant on-chain 
infrastructure: the offer- and interest-communication protocol, service discovery and customization, 
and batch construction.
For each of these functionalities, we indicate what functions each of the three roles 
involved in this infrastructure performs. The three roles (which a single party may combine) are:
anonymous publishers of sub-transactions (wallets), services 
(babel aggregators of sub-txs into top-level txs), and relay nodes. 


## Motivation: Why is this CIP necessary?

[CIP-118][] defines ledger changes needed to support a specific kind of 
transaction batching. 
Incomplete transactions (e.g. unable to pay fees in ADA) are not propagated 
across the Cardano network. 
Off-chain infrastructure is needed to build 
valid batches called *top-level transactions* out of partially 
valid sub-txs. These batches can then be posted 
on-chain. Building such a mechanism can allow the experience of 
submitting sub-transactions to reach the 
level of the experience of submitting a complete transaction: create a 
transaction, send it across a network, see it on-chain quickly. It would
introduce the following new business opportunities:

- **Users holding no ADA can transact**, paying in whatever asset they have,
  removing the onboarding obstacle of not having ADA (including supporting 
  paying fees in non-ADA tokens, i.e. *babel fee offers*).
- **Multi-user, multi-UTxO swaps get cheaper, faster and less contended**: each
  party signs their own sub-transaction rather than serialising through one batcher.
- **New business becomes viable** for individual users, for markets and DEXs
  quoting across assets, and for DApps sponsoring their users' fees.
- **Arbitrary intents come within reach.** An offer is already a signed
  statement of what a user wants and will pay for it. We propose 
  a possible intent fulfilling protocol for clients that do not have chain state access.


## Specification

Such a mechanism requires the components we describe in this CIP, which can be 
roughly classified into support for the following functions (performed by 
services, publishers, and relays) expected from the 
infrastructure:

- **off-chain network protocol for offer and interest communication** — the
  [envelope](#offer-envelope) an offer travels in, the
  [topology](#network-topology-and-roles) and [transport
  bindings](#transport-bindings) it travels over, the
  [validation](#validation) each party owes, the [routing and
  filtering](#routing-and-filtering) that decides where it goes, and the
  [lifecycle](#offer-lifecycle) that says what became of it;
- **service registration for discovery** —
  [on-chain registration](#on-chain-registration-of-relays-and-services);
- **batch construction** — [batch construction](#batch-construction), the
  [constraint language](#constraint-language) a service plans against, and the
  [liquidity strategy](#liquidity-strategy) that funds it;
- **service customization** — the [service profile](#service-profile) and
  [price hints](#price-hints) an operator publishes, within the
  [protocol constants](#protocol-constants) everyone shares.

### Architecture

Boxes are machines. What shares a box is expected to share a host. A service
must run beside a full
node and talks to it locally. Nothing else needs a node: a relay is required to
hold no chain state, and a wallet publisher may be light.

```text
  ┌─ USER'S MACHINE ─────────┐        ┌─ RELAY HOST ──────────────┐
  │                          │        │  no chain state, beside   │
  │  wallet / publisher      │        │  nothing                  │
  │  builds and signs one    │        │                           │
  │  sub-transaction         │        │  relay                    │
  │                          │        │  stateless checks, dedup, │
  │                          │        │  rate limit, forward      │
  └────┬──────────────┬──────┘        └──┬─────────────────┬──────┘
       │              │                  │                 │
       │              └── gossipsub ─────┤                 └─► other relays,
       │                 topic = a       │                     drawn from the
  HTTPS│                 routing key     │ gossipsub           registry each
  POST /offers                           │                     epoch
  GET  /offers/{id}                      │
       │            ┌────────────────────┘
       ▼            ▼
  ┌─ SERVICE OPERATOR'S MACHINE ────────────────────────┐
  │                                                     │
  │  babel fee service                                  │── HTTPS GET /offers/stream ─► other services
  │  verifies, selects, builds the batch, submits it    │
  │           │                     ▲                   │
  │           │ resolve inputs,     │ blocks, rollbacks,│
  │           │ protocol params,    │ the registry      │
  │           ▼ submit              │                   │
  │      ┌────┴─────────────────────┴────┐              │
  │      │  cardano-node (full)          │              │
  │      │  local socket, or cardano-cli │              │
  │      └───────────────┬───────────────┘              │
  └──────────────────────┼──────────────────────────────┘
                         │ node-to-node
                         ▼
                   Cardano chain
        registrations, batches, and the answer
        to "did my offer land"
```

A publisher reaches a service directly over HTTPS, or reaches services it has
never heard of by publishing to the mesh. Relays carry offers and nothing else:
they never build batches, never hold chain state, and never decide what any
service wants. Services also source from each other over HTTPS, which is a pull
path a silently-dropping relay cannot cut.

### Terminology

#### Imported from CIP-118, not redefined by this CIP

*sub-transaction*, *top-level transaction*, *batch*, *guard*, *required top-level
guards*, *isolation mode*. 

#### Defined by this CIP

**envelope** — The wire container for exactly one offer: `[envelope_version,
era_tag, subtx_bytes]`. 

**offer** — A published envelope-wrapped sub-transaction.

**offer identity** — The sub-transaction's TxId. Distinct from the **transport
dedup key**, a hash over the complete envelope bytes.

**pool** — The offers a party is holding (whether batched or not)

**candidate** — An offer a service has verified and could put in a batch. Which
candidates it actually selects is its own business and is not specified here.

**imbalance** — Amount of each asset a sub-transaction gives its batch and takes from it.

**binding** — A concrete transport for carrying offers: how an envelope travels,
and what the transport itself checks before handing it over. 

**message** — What a binding carries when it carries an offer. Its payload is
then always an envelope; a binding may carry
other traffic of its own. On a transport that routes by topic, a message is a topic
and a payload together, and the topic is not part of the envelope; see
[Forwarding].

**topic** — On a binding that routes by topic, the address a message travels
under: a [routing key](#routing-keys) written out, and nothing more. 

**publisher** — Any party that emits an envelope. 

**service** (equivalently **aggregator**, **babel fee service**) — A party that
ingests offers, verifies them, selects a jointly satisfiable set,
builds a top-level transaction, and submits it.

**relay** — A party that ingests offers, 
deduplicates, and forwards, without building batches. 

**peer** — Whoever a binding connects a party to. Not a role: on a mesh
publishers, relays and services are all peers, and what a peer *is* belongs to
the binding rather than to this specification. Rate limits and drops are counted
against peers, so they act on links rather than on parties.

**mesh** — A gossip network in which every peer forwards what it accepts to its
neighbours, rather than one in which designated parties forward to designated
recipients. 

**backbone** / **open edge** — The two halves of the topology. The **backbone** is
the set of services and relays, which may register. The **open edge** is
everything else — wallets and other publishers — which never register and reach
the backbone through any provider or open relay.

**interest filter** — A service's advertised intake specification: either a set
of filter keys it accepts or the marker *all*, together with a set it rejects,
rejection taking precedence.

**filter key** / **routing key** — A **filter key** is a value deterministically
derived from an offer and used to decide whether a service wants it. A **routing
key** is the wire encoding of a filter key for topic-based transports. 

**service profile** — The operator-authored specification a service follows:
its accept and reject sides as filter keys, rate source, budgets, supported
constraint-language versions, and two disclosures. A relay has none. 

**satisfier** — The search a service runs to find out whether it can complete a
batch that makes a constraint hold, and what to add if so. 

**registration** / **registry** — A **registration** is the on-chain record of a
service or relay: one UTxO, one NFT, and a registration record as its datum. The
**registry** is all of them together, and is both how a party is discovered and
the set peers are drawn from. 

**declared constraint** — A constraint expressed in this CIP's constraint language
(constraint DSL)
and carried in a guard datum. 

**interpreter guard** — A published script that evaluates DSL-specified constraint
on-chain. 


### Offer envelope

**Structure**

```cddl
envelope =
  [ envelope_version : uint                     ; this specification's revision
  , era_tag          : uint                     ; ledger era whose CDDL subtx_bytes conforms to
  , subtx_bytes      : #6.24(bytes .cbor subtx) ; the sub-transaction, verbatim
  ]
```

`subtx_bytes` is a byte string carrying encoded CBOR, wrapped in CBOR tag 24 
(the same construction Cardano uses for inline
datums and script references). 
Values for `envelope_version` and `era_tag` are
given in [Protocol constants].

**Offer identity.** The envelope carries no identity field. An offer's identity
is the TxId of the sub-transaction inside `subtx_bytes`, which every recipient
derives from the payload it already holds and which the publisher can compute at
construction time. Field 23 is itself keyed by TxId, so this is the identity the
ledger will use.

**Transport dedup key** 
An envelope's transport dedup key is Blake2b-256 over its bytes exactly as
received, witness set included. It is computed locally and not transmitted 
as part of the envelope. 
Two
witness-mutated copies of one offer have *different* dedup keys and the *same*
offer identity.

### Network topology and roles

The goal this design aims to achieve is that every offer must reach at least one honest
service whose profile matches it before its validity bound, and no service should 
be systematically starved of offers.
Useful offer volume is
bounded by what batches can land: on the order of tens of offers per second
across the whole network, each between roughly 1 and 16 KB. Anything beyond that
is spam by definition and belongs to [Validation]. A topology here should
therefore buy robustness and censorship resistance with throughput it does not
need.

**Open edge vs. backbone.**
Publishers are many, anonymous, short-lived and mostly offline.
Services and relays are few, long-lived, and addressable.
These populations want different treatment. The network has an **open edge**
of publishers, which never registers and reaches the network through any
service or open entry point. It also has a **backbone** of services and relays that
maintain standing links to each other.

**Roles.** Each is defined by its obligations, and they nest: a service does
everything a relay does and more. On a mesh, publishers, relays and services are
all just peers — forwarding is something every peer does, so it does not
distinguish them.

| Role | Must |
|---|---|
| Publisher | Construct offers that pass the [offer checks](#stateless-checks--performed-by-publishers-relays-services), and derive their own keys, which needs chain state a wallet has anyway. No identity, no registration, nothing ongoing. |
| Relay | Every [stateless check](#stateless-checks--performed-by-publishers-relays-services), deduplication by transport dedup key, and per-peer rate limits. Forward what passes; drop peers on the grounds below. Never required to hold chain state. |
| Service | Every relay obligation, including peer drops, plus the [chain-state](#chain-state-checks--performed-by-publishers-services) and [pre-inclusion](#pre-inclusion-checks--performed-by-services) checks, and honouring its own [advertised interest](#routing-and-filtering). |

A relay may also drop an offer that reached it on a topic the offer does not
belong on, judged from the offer alone without consulting the chain.

**Full node usage**
A service must be able to resolve inputs, run
scripts, follow rollbacks, etc. For this reason, it must run beside a full node
at all times (using the node's CLI frequently).
A relay can run anywhere, and does not earn fees. However, to register, 
some user must submit a transaction registering it on-chain (to enable discovery).


**Registration** is for the backbone, optional, and requires an on-chain deposit.
Only services and relays (but not publishers) may register an endpoint and a 
profile on-chain. 
The registry is a discovery aid and the base set for peer selection
below; what a registration contains is in
[Service profile](#service-profile). Running an unregistered service or
relay is possible. 

**Non-forwarding adversaries.** 
Adversarial relays may fail to forward offers, either maliciously or not.
We do not provide guarantees that a relay will forward all offers, but 
we provide three communication options, in order of least likely to most 
likely that a non-malicious relay will forward the relevant offers:

1. subscription to a gossip topic, where flow is push within the mesh;
2. a consumer-initiated stream, where the consumer opens the connection but the
   sender still decides what to send;
3. true pull, where the consumer asks which offers exist and then fetches the
   ones it wants;

**Peer selection.** Each backbone member — service or relay — maintains links
to *k* (see [Protocol constants]) others, drawn uniformly from the registry using on-chain
randomness, so that anyone can recompute the draw and nobody can steer it. 

**Dropping a peer.** Dropping peers is a component of our protocol that is 
orthogonal to dropping offers they send. Peers are dropped for the 
following reasons:

- exceeding the [per-peer rate](#protocol-constants);
- sending offers that fail the [stateless
  checks](#stateless-checks--performed-by-publishers-relays-services);
- sending on a topic the recipient never subscribed to, or altering the topic
  an offer arrived on.

A dropped peer is not replaced. The peer set, which is local to whoever drew
it, runs short until the next epoch's draw refills it. Drops are temporary
rather than permanent. Replacing a peer on demand would be a way to steer the
peer set composition. The value *k* must be chosen with
this in mind. There is no globally shared peer blacklist or reputation record.

Dropping a peer does not identify a publisher. On a mesh a publisher is a peer
like any other and may be dropped like any other, but what is dropped is a
transport link rather than an identity, and nothing is learned about who was
behind it.

**Fairness.** Two things have to hold. No offer may be systematically starved,
and the network must not hand any service a systematic first look at them. The
unsteerable draw above is what buys the second: no service can position itself
nearer the flow than the draw allows. Discovery must not produce a hub that
offers pass through, and each publisher should reach at least two independent
operators. 

**Running on DMQ.** If a [CIP-0137][] message queue carries offers, there are
two ways to arrange it:

*Bundle* into the DMQ network stake pools already run: offers reach every node
that is already there, so the relay population is large from the first day, and
nobody is obligated to use infrastructure. The cost is that those operators 
may end up carrying anonymous, unmetered traffic, and spam (which we 
do attempt to mitigate here) lands on them.

*Separate*, as its own instance with its own network magic: the spam is
confined to operators who opted into it, and the parameters are ours to set.
The cost is inverted — a relay population that has to be recruited, and which
starts small.

This decision is unresolved.


### Transport bindings

This specification defines two bindings, with room for more.
No binding may require publisher identity. 
An offer's own witnesses are the
only authentication the protocol can potentially access.

#### Binding A — HTTPS

A service running this binding is an HTTPS server. Each row below is one request
it answers, named by an *endpoint*: an HTTP method and a path.

| Endpoint | |
|---|---|
| `POST /offers` | Submit one envelope. `202` once accepted for verification, which is asynchronous — acceptance is not a promise to batch. A resubmission of a known offer is also `202`; replay is idempotent. |
| `GET /offers/{offer_id}` | The offer's state. |
| `GET /interest` | The advertised interest filter: accept side, reject side, and whether it accepts everything. |
| `GET /profile` | The [service profile](#service-profile), off chain — the same policy the (optional) on-chain registration carries. |
| `GET /hints` | The service's current price hints: what it would indicatively charge to carry an offer, quoted per accepted asset. |
| `GET /offers/stream` | A feed of accepted offers, so services can source from each other rather than only from publishers. |
| `GET /` | Name, network, and the versions a counterparty needs before it builds: the API version, the [protocol revision](#versioning), the interpreter hashes it can satisfy, and any wire versions it accepts beyond what its revision implies. Also the oldest offer bound it still answers about, which is the one local limit nobody can discover by reaching it. |

Price hints are an endpoint because nothing here can quote back: a
sub-transaction's imbalance *is* its price, fixed when the publisher signs, and
asking a service for a quote first would mean a session and so an identity. A
service instead states indicative terms in advance, and a wallet reads them and
does its own arithmetic. See [Price hints].

`/interest` is made up of the accept and reject sides of the profile. A service advertising
an interest is expected to honour it.
See [Routing and filtering] for
when each part of a filter applies.

Nothing on this binding relays, so an offer reaches exactly the services its
publisher sends it to.

A **relay** answers only to `GET /`, giving its registration names an endpoint. A party
drawn to it has to be able to read the protocol revision and accepted versions
it runs.

#### Binding B — libp2p gossipsub

This mesh binding allows an offer reach
services its publisher does not choose, possibly via intermediate relays.

| | |
|---|---|
| Topic | A routing key |
| Message payload | Envelope bytes |
| Message identifier | Blake2b-256 of the envelope bytes (the same value as the transport dedup key, so identical arrivals collapse without anyone parsing them) |
| Signing mode | `StrictNoSign` - no signatures accepted |
| Maximum message size | [Protocol constants] |

A peer re-announces offers it holds that have not expired. Gossip keeps
nothing, so without re-announcement a service that joins late sees only what is
published after it arrives.

Nothing may be assumed about ordering or delivery. Mesh parameters — degree,
heartbeat, scoring — are the operator's, and libp2p's.

#### Further bindings

A transport qualifies if it can carry anonymous publishers, carry an envelope
whole, and let a consumer tell that it has missed something. The last is the one
that decides between candidates, because it is what distinguishes a quiet
network from one that is cutting a service off.

A candidate under consideration is a message-queue binding built on the Cardano
network stack. Adopting it would mean a separate instance rather
than a configuration: its authentication would have to be dropped for the
invariant above to hold, and its message bodies are smaller than an envelope.

It also distributes one unfiltered stream, so [routing keys](#routing-keys)
would carry nothing and every subscriber would pull everything. That is a
priced trade rather than a defect. Useful offer volume is bounded by what
batches can land — [tens of offers per second across the whole
network](#network-topology-and-roles), each 1 to 16 KB — so the entire firehose
is still small enough to take and filter locally. What is bought in
exchange is the strongest gap detection of any arrangement here: a consumer
that asks what exists and then fetches can tell silence from suppression, which
a mesh cannot.


### Validation

#### Transport-binding checks — imposed by the binding

These are properties of the binding rather than of the offer, performed by
whatever software terminates the protocol — a `dmq-node`, a gossipsub
implementation. An implementation inherits whichever set belongs to the
transport it uses, and they neither replace nor satisfy any check below.

A message-queue binding of the kind under consideration in
[Transport bindings] would contribute:

- **Message well-formed** under the instance's CDDL.
- **`expiresAt` not passed**, and no further ahead than the instance's maximum
  TTL, which is the same ceiling as the maximum offer TTL in
  [Protocol constants].
- **Body size** within the per-instance cap.
- **Network magic** matches the instance.

A binding may carry a TTL of its own, as this is what DMQ's `expiresAt` does.
It is useful because a
transport has to discard stale messages without parsing a sub-transaction to
learn when they expire. It is derived from the sub-transaction's validity
upper bound and never set independently: set shorter it drops offers that are
still good, set longer it keeps ones already dead. This is a rule for whoever
publishes, not a check the binding performs.

An HTTPS binding contributes nothing about the offer — only transport framing,
which the checks below do not depend on.

A gossipsub binding contributes:

- **No author signature fields present.** StrictNoSign rejects messages
  carrying `from`, `signature`, or `seqno`.
- **Message size** within the binding maximum.


#### Stateless checks — performed by publishers, relays, services

Publishers must construct offers satisfying every offer check. Relays and
services must apply the offer checks before storing or forwarding an offer, and
must also perform the recipient checks. None require chain state.

**Offer checks** 

- **Envelope well-formed.** Envelope deserialization fully succeeds
- **Era.** `era_tag` must name an era the recipient can read. A decoder that ignores it reads every offer under whatever era it implements.
- **Sub-transaction deserializes** under the CDDL for the era named by
  `era_tag`
- **Size.** `subtx_bytes` must NOT exceed the sub-transaction size ceiling in
  [Protocol constants]. Implementations may impose a stricter local bound.
- **Validity interval** present, internally consistent, and with a finite upper
  bound not exceeding the maximum offer TTL in [Protocol constants]. An offer
  whose bound is already behind the current slot may be rejected here: slot
  arithmetic is static configuration rather than chain state, and once the
  clock is past the bound no later block can carry the offer. The `expired`
  lifecycle state is the tip-relative one, and answers a different question.
- **Network.** `network_id` must match the network the recipient serves.
- **Signatures** verify against the sub-transaction body hash.
- **Guard-constraint shape caps.** A declared constraint exceeding the maximum
  depth, node count, or backtracking budget in [Protocol constants], or
  containing an empty `All` or `AnyOf`, must be rejected here, before the offer
  reaches a pool.
- **At least one spend input** is required for offers diffused over an open
  transport. 

**Recipient checks** — obligations of whoever receives the offer:

- **Duplicate.** An arrival whose transport dedup key the recipient is currently
  suppressing must not be forwarded or stored again. Every party suppresses the
  keys of the offers it currently holds, and a service also suppresses those the
  chain has settled. An offer dropped for any other reason loses its key with
  it, and is readmitted on re-arrival — see [Offer lifecycle]. 
- **Peer rate.** Offers from a peer exceeding the per-peer submission rate in
  [Protocol constants] must be rejected. Repeatedly exceeding it is grounds for
  dropping the peer; see [Network topology and roles].
- **Filter-key policing (optional for relays).** A routing key is an address
  and never evidence. On transports where the publisher chooses where
  to send an offer, a relay may re-derive the keys that need no chain state — guard, ExUnits
  band, and the two feature keys — and drop an offer whose [arrival
  topic](#routing-keys) is not among them. An offer a relay keeps travels on the
  topic it arrived on.


#### Chain-state checks — performed by publishers, services

Relays are not required to perform these as they may not have access to chain state.

These are the phase-1 rules that bind a sub-transaction in isolation, together
with phase-2 evaluation of its own scripts (not top-level guards).

- **Inputs currently unspent**.
- **Reference inputs exist**, where used.
- **Witness set complete.** 
- **Validity interval covers the current tip.** 
- **Min-UTxO floors** 
- **Output, transaction, and value sizes**, and **declared ExUnits**, within current protocol
  parameter limits.
- **Script integrity hash** Compute it and check against the field.
- **Cost-model cliff.** Is the cost model scheduled to change
  before its validity upper bound?
- **Sub-transaction scripts succeed** under phase-2 evaluation
- **Imbalance derivation.** `consumed − produced` per asset: a positive entry is
  what the sub-transaction offers its batch, a negative entry what it needs from
  it. Resolving the inputs is what makes this a chain-state check.
  **Consumed** is the resolved spend inputs, withdrawals, minted quantities, and
  deposits refunded by unregistration certificates; **produced** is the outputs,
  direct deposits, the treasury donation, burned quantities, deposits locked by
  registration certificates, and governance proposal deposits. An asset whose
  sides cancel is absent rather than zero. The list is exhaustive because
  everything routes on the result: two recipients disagreeing about what counts
  would derive different keys for one offer, and each would read the other's
  honest placement as a lie. Note that stake-pool registration and retirement
  take their deposit from a protocol parameter rather than carrying it, so they
  are the one case the imbalance cannot be read from the body and inputs
  alone.
- **Filter-key policing.** On a binding where the publisher chooses where to
  send an offer, a service re-derives **every** one of the offer's keys and
  drops it if the arrival topic is not among them. 

#### Pre-inclusion checks — performed by services

1. Phase-2 validation of guard scripts must be evaluated for amount of ExUnits used. 
2. Sufficient fee and collateral is included to cover the total (size- and ExUnits-based) fee 
3. Full phase-1 validation must be performed on the assembled top-level
transaction before submitting it for block inclusion. 

**Bounding execution units**
In (1), a service stops once script execution exceeds its own
[`max_ex_units_*` budget](#service-profile) and drops the guard-requiring
sub-transaction from the batch. The author's own
[`Bounds::ex_units`](#constraint-language) is a separate bound on the 
same guards, specified via the constraint language. Whichever of the two is
lower binds.
The [ExUnits band](#filter-key-kinds) a service subscribes to 
keeps most of what the service would
refuse from reaching it at all. Relays 
that do not follow this (or any) filtering policy may be dropped or blacklisted.

### Routing and filtering

Services take only the offers they want, and can check an offer is what it was
sent as. Three separate things do that work (see details below)
- A **filter key** is a label computed locally from an offer. Filter keys divide in two:
  some can be derived from the signed body alone, the rest need the inputs
  resolved;
- An **interest filter** is what a service says it wants, using the same syntax as for filter keys;
- A **routing key** is a filter key written as a string.

What each role does with each:

| | Publisher | Relay | Service |
|---|---|---|---|
| Declare a filter key | never | never | never |
| Derive body-only keys | its own | may | yes |
| Derive chain-state keys | its own | not required to — a relay never has to hold chain state | yes |
| Check the arrival topic against the offer's keys | — | may, body-only keys | must, all keys |
| Choose which topics to publish on | yes | forwards on the arrival topic | forwards on the arrival topic |
| Subscribe to topics | — | yes | yes, its accept side |
| Define an interest filter | — | — | yes |
| Advertise one | — | — | yes, both sides |
| Apply one | — | — | body-derivable keys at ingest, the rest once inputs resolve |
| Post filter keys on-chain | — | never — a relay's registration carries no keys | may, as its registered accept side |

A dash means the activity is not part of that role at all.

Posting keys on-chain is advertisement and never subscription. 
What actually makes offers arrive is the subscription a peer announces
to its neighbours over the gossip protocol. 

What is relayed across what type of network:

| | HTTPS | Gossip mesh | Unfiltered stream | On-chain |
|---|---|---|---|---|
| Filter key | never | never | never | never |
| Routing key | as the advertised accept side | as the message topic | never — no topics | in a registered profile, as advertisement only |
| Interest filter | both sides, from `GET /interest` | never | never | both sides of a registered profile |
| Envelope | request body | message payload | message payload | never (its sub-transaction may end up on-chain later) |

Routing keys and topics exist only on bindings that route by topic; interest
filters, as the HTTPS column shows, do not depend on them.


#### Forwarding

Forwarding happens on bindings where peers pass offers to one another. Gossip
and an unfiltered stream both do. On HTTPS a publisher sends straight to a
service it chose, so nothing below applies to that path — though services may
still feed each other over it, which [Transport bindings] covers.

A *gossip message* pairs `(topic, envelope)`. The envelope is the payload.
A mesh peer forwards on the topic it
received, to its neighbours subscribed to that topic, without checking it — the
topic is an address as far as routing is concerned, so forwarding never depends
on it being true. Whether it was placed honestly is a separate question, asked
later and by someone else. Relays and services both do this, a
relay simply does nothing else. Peers announce and withdraw subscriptions as part
of the gossip protocol, which is how a peer knows where to send. That belongs to
libp2p and is out of scope: this specification defines what rides on a
mesh, not the mesh.

What a service subscribes to is the accept side of its interest filter, and
the reject side is advertised too, but never subscribed to — a subscriber
cannot unsubscribe from part of a topic, so rejection is applied on ingest. Subscribing is an announcement to its
neighbours, carried by the gossip protocol itself rather than published to any
topic. Registering the same
keys on-chain advertises what it would accept and routes nothing.

Where a binding has no topics there is nothing to route by, so a peer forwards
everything that survived the stateless checks, to everyone it is connected to.

No forwarding decision consults what any service wants. Whether an offer is
wanted is settled by the service that receives it. A relay's only use for filter
keys is the [optional placement
check](#stateless-checks--performed-by-publishers-relays-services),
which asks whether the publisher placed it honestly, not whether anyone wants it.


#### Filter-key kinds

Each kind below is read off the sub-transaction body, or off the body together
with its resolved inputs. Nothing in the envelope names them: a recipient works
out which kinds apply and derives a key for each. The kinds are:

| Code name | Kind | Carries | Derived from | Needs chain state |
|---|---|---|---|---|
| `OfferedPolicy` | Offered policy | a `policy_id` | a policy on the positive side of the imbalance | yes |
| `NeededPolicy` | Needed policy | a `policy_id` | a policy on the negative side | yes |
| `PureBabel` | Pure babel | nothing | needs only ADA | yes |
| `SponsorshipOnly` | Sponsorship only | nothing | balanced; needs only fee and collateral | yes |
| `Priority` | Priority | nothing | needs nothing and offers value: paying for inclusion rather than asking for it | yes |
| `Guard` | Guard | a `credential`, key or script | a credential in required top-level guards | no |
| `ExUnits` | ExUnits band | one of `none`, `low`, `medium`, `high` | declared execution units, banded | no |
| `UsesDirectDeposits` | Direct deposits | nothing | uses direct deposits | no |
| `UsesAccountBalanceIntervals` | Balance intervals | nothing | uses account balance intervals | no |

A key that carries nothing is one value; the other three are families, one key
per distinct payload. `ExUnits` carries a *band* rather than a number of
execution units, because a topic has to be a name a subscriber can write down in
advance, and there are only so many bands. The
[routing-key grammar](#routing-keys) is the wire spelling of exactly these
payloads.

A relay can verify only the kinds marked as not needing chain state, since it is
never required to have any. The three class kinds (`PureBabel`, `SponsorshipOnly`, `Priority`) are mutually exclusive.

Several kinds usually apply to one offer, and it is published under all of
them:

```
offer: offers TokenX, needs only ADA, no scripts

filter keys                topics published to
───────────────────────────────────────────────────────────
OfferedPolicy(X)     →     subtx/v1/mainnet/offered/{X}
PureBabel            →     subtx/v1/mainnet/class/pure-babel
ExUnits(NoScripts)   →     subtx/v1/mainnet/exunits/none
```

Deduplication by offer
identity is mandatory. Subscription is always a union.

#### Routing keys

A routing key is a filter key written as a topic name, together with the two
pieces of context a topic needs and a filter key does not carry: which network,
and which version of this grammar. 
It is a string, used verbatim as the topic identifier:

```abnf
routing-key = "subtx/v1/" network "/" kind

network     = "mainnet" / "preprod" / "preview"

kind        = "offered/" policy-id
            / "needed/" policy-id
            / "class/pure-babel"
            / "class/sponsorship"
            / "class/priority"
            / "guard/key/" hash28
            / "guard/script/" hash28
            / "exunits/" band
            / "feature/direct-deposits"
            / "feature/balance-intervals"

band        = "none" / "low" / "medium" / "high"
policy-id   = 56lc-hex
hash28      = 56lc-hex
lc-hex      = DIGIT / %x61-66          ; 0-9 a-f, lower case only
```

Every character is ASCII and lower case, including hex digits; there is no
trailing separator. For example `subtx/v1/mainnet/class/pure-babel`, or
`subtx/v1/preprod/offered/` followed by 56 hex characters.

The `subtx/v1` prefix is fixed by this specification. Its version segment covers
the routing-key grammar itself — which kinds exist and how each is spelled — so
a later revision that adds or respells keys publishes under `subtx/v2`, and
subscribers to one version never receive keys shaped for another.

The `network` segment puts each network on its own topics, so a mainnet subscriber never
receives a preprod offer at all. This does not replace the `network_id` check on
the body.

An offer whose keys span several kinds is published under every corresponding
routing key; subscribers deduplicate by offer identity.

**Not every binding has routing keys.** A binding distributing one unfiltered
stream — as DMQ does by design — has no topics to address, so a service derives
filter keys as usual and applies its interest filter locally on ingest.
Whether a relay polices placement does not arise on such a
binding: every relay forwards whatever passes the stateless checks.


**Firehose**. There is no catch-all routing key. A service wanting everything
subscribes to the union of the keys it wants. Connecting to a relay that polices
nothing does not substitute: it declines to drop, but it still only
carries the topics it subscribed to. 

**Interest filters.** An interest filter is an accept side — either a set of
filter keys or the marker **all** — and a set of rejected keys. An offer is
ingested when none of its keys is rejected, and either the accept side is *all*
or at least one of its keys is accepted. Offers on HTTP 
allow the publisher to learn about their offer's rejection from the `POST /offers` 
response. On a gossip network, rejection is silent.

**Further refinement.** Services can
implement additional local filters that can be posted on-chain 
as part of their [service profile](#service-profile), as well as without any 
announcement strategy. Relay nodes are not aware of these 
filters. 


### Constraint language

As part of this CIP,
we provide a small constraint language.
A constraint is a predicate over a candidate batch, provided by a 
publisher as a way to constrain the top-level tx over which 
their sub-transaction has otherwise no control. The constraint language 
is a tool we provide to enable constructing script-datum pairs that 
encode the DSL's constraints and are checked on-chain.

**Evaluation**
We provide an encoder (and corresponding decoder) for the constraint 
language. It takes a DSL
expression and returns a `Datum`. A Plutus script is to be provided
that acts as an interpreter for the (specific version of) the 
constraint language. When a top-level tx is constructed, the interpreter
Plutus script is included as a guard, and the encoded DSL expression 
is included as its datum. The result of the on-chain evaluation of the guard+datum 
pair on the top-level tx should be the same as the result of checking 
the constraint DSL on the top-level tx directly. Guards and their datums
can be specified by sub-txs.

**Constraints**
A constraint has two parts, and the split is syntactic rather than a
convention:

```
constraint = bounds + requirement
```

**Bounds** are ceilings on the batch as a whole. The two scalar bounds may
each appear at most once; net-outflow bounds are keyed, as the table says:

| Code name | Bound | Holds when |
|---|---|---|
| `Bounds::ex_units` | execution units | the batch's total execution units are at most the bound. Enforced by the service among the [pre-inclusion checks](#pre-inclusion-checks--performed-by-services), never by the guard. |
| `Bounds::tx_size` | serialised size | the batch's size in bytes is at most the bound. Enforced by the service among the [pre-inclusion checks](#pre-inclusion-checks--performed-by-services), never by the guard. |
| `Bounds::net_outflow` | net outflow | for a named credential set and asset, value consumed from those credentials minus value returned to them is at most the bound. Spends from credentials outside the set are not counted. One bound per (credential set, asset). |

The net-outflow bound lets users add safeguards of their own, and is the one
bound a guard can enforce: the other two cannot be read from a script context,
so an author writing them buys a service's cooperation rather than enforcement.
There are no ExUnits caps on guards travelling with a particular sub-transaction,
so running them on the top-level batch is limited only by the service's own
`max_ex_units_*` [budget](#service-profile), which each operator sets
experimentally against its hardware and risk tolerance.

**Requirements** are what a completing batch must contain. These compose:

| Requirement | Holds when |
|---|---|
| `PaidAtLeast { address, asset, amount, datum }` | the sum of `asset` paid to `address` across counted batch outputs is at least `amount`. With `datum` present, only outputs whose inline datum serialises to exactly those bytes are accepted; absent, every output at the address is accepted. |
| `Guards(credential)` | `credential` is among the batch's top-level guards. Key credentials only (see Known gaps) |
| `All(children)` | every child holds, must be non-empty. |
| `AnyOf(children)` | at least one child holds, tried in the given order, must be non-empty. |
| `True` | always. The only way to state "no requirement", since the two combinators cannot be empty. |

The same thing as CDDL, since a datum is on-chain data and this is what a second
implementation encodes against:

```cddl
constraint  = #6.121([bounds, requirement])
bounds      = #6.121([maybe<ex_units>, maybe<uint>, [* net_outflow]])
ex_units    = #6.121([mem : uint, steps : uint])
net_outflow = #6.121([[+ credential], asset, amount : uint])

credential  = #6.121([hash28])      ; key
            / #6.122([hash28])      ; script
asset       = #6.121([])            ; ada
            / #6.122([policy : hash28, name : bytes .size (0..32)])

requirement = #6.121([address : bytes, asset, amount : uint, maybe<datum>])
            / #6.122([credential])              ; guards
            / #6.123([[+ requirement]])         ; all
            / #6.124([[+ requirement]])         ; any-of
            / #6.125([])                        ; true

maybe<a>    = #6.121([]) / #6.122([a])
datum       = bytes                 ; the datum's own encoding, carried verbatim
hash28      = bytes .size 28
```

Constructor alternatives 0 through 6 are tags 121 to 127, so the tags above are
`Constr n` with `n = tag − 121`. `maybe` follows PlutusTx's `Maybe`: absent is
alternative 0, present is alternative 1.

**Shape caps**
A requirement tree exceeding any of these is rejected among the stateless
checks, before an offer reaches a pool. Bounds are flat and need no caps:

| Code name | Cap | Ranges over |
|---|---|---|
| `MAX_CONSTRAINT_DEPTH` | Maximum depth | nesting |
| `MAX_CONSTRAINT_NODES` | Maximum node count | total size |
| `MAX_BACKTRACKING_BUDGET` | Maximum backtracking budget | the product of `AnyOf` branch counts |

Maximum backtracking budget is calculated by multiplying, not summing, the
branch counts of every `AnyOf` in the tree, because a satisfier may have to try
every branch of each one against every combination of the others: four `AnyOf`
nodes of four branches apiece cost 256 attempts, not 16.
Values are in [Protocol constants].

What a guard costs to run is not a function of the constraint alone. 
It is a function of the full transaction which contains it (including its sub-txs).
For this reason, shape caps cannot directly be translated to ExUnits caps.

**Misbehaviour**
A server that does not drop offers that do not satisfy its interest filters is
considered to be 
misbehaving, which could be grounds for (local) blacklisting by other parties
that implement blacklists.


**Evolution**
The constraint language's version is its interpreter's script hash. 
Anyone may publish an interpreter, on-chain as a reference script, so a batcher
can name it without carrying its bytes. A new interpreter records the hash of its
predecessor in its publication record, described below. Multiple versions may be published simultaneously, and 
the resulting succession graph is not necessarily linear.

Batching across dialects is out of scope. One batch may in principle carry
constraints naming different interpreters, but satisfying them together is not
specified here.

**The language is pluggable.** This specification fixes 
the interface — a constraint is a datum, an interpreter evaluates it, a
satisfier proposes an augmentation and `evaluate` decides. The AST below is a prototype
implementation of that interface. Another may replace it via a hash-substitution.
The interpreter is named by hash and adopted by whoever finds
it worth adopting.

The constraint
language specified here is deliberately small: it is what a satisfier can plan
against today.
A more comprehensive transaction construction DSL such as [Tx3][] can be adjusted 
to operate on Dijkstra transactions for both constraint checking and satisfaction,
but this is out of scope here.

An interpreter defines evaluation completely. 
A satisfier cannot be obtained the same way.
An interpreter's publication record should name the source it was built from, by
repository and commit, alongside its predecessor's hash. The adherence of the satisfier code to 
the interpreter semantics, 
as well as its persistence, cannot be trusted. However, it is in the interest of 
the publisher to ensure both of these aspects, as their sub-txs will not make 
it on-chain otherwise. 

Conformance vectors (a constraint, a candidate batch, and the verdict the
interpreter returns) may accompany that record, for implementations that will
not rebuild the source. They demonstrate agreement on a known set rather than
establishing it in general, and are checkable by running the
published script.

**Encoding**
A constraint travels as a guard datum, so its encoding is PlutusData. 
Written below as `Constr n [fields]`, `I` for integers, `B` for byte strings,
and `List` for lists. An absent optional value is `Constr 0 []` and a present
one `Constr 1 [value]`. This assignment is fixed by this specification and is
not inherited from any library: Plutus Tx orders `Maybe` as `Nothing | Just`,
which agrees; Aiken orders `Option` as `Some | None`, which does not, so a
decoder that assumes its own language's convention reads every optional field
inverted.

| Value | Encoding |
|---|---|
| `constraint` | `Constr 0 [bounds, requirement]` |
| `bounds` | `Constr 0 [maybe ex-units, maybe tx-size, List [net-outflow]]` |
| `ex-units` | `Constr 0 [I mem, I steps]` |
| `tx-size` | `I bytes` |
| `net-outflow` | `Constr 0 [List [credential], asset, I amount]` |
| `credential` (key) | `Constr 0 [B hash]` |
| `credential` (script) | `Constr 1 [B hash]` |
| `asset` (ada) | `Constr 0 []` |
| `asset` (other) | `Constr 1 [B policy, B name]` |
| `requirement` | one of the five constructors below |
| `PaidAtLeast` | `Constr 0 [B address, asset, I amount, maybe (B datum)]` |
| `Guards` | `Constr 1 [credential]` |
| `All` | `Constr 2 [List [requirement]]` |
| `AnyOf` | `Constr 3 [List [requirement]]` |
| `True` | `Constr 4 []` |

Credential and asset tags follow the ledger's encoding of those types.
Two net-outflow bounds over the same credential set and asset are a malformed
constraint rather than a stricter one, and a decoder MUST reject them.

Tags are assigned positionally and never reused. A new requirement takes
the next free tag.
Adhering to a canonical encoding allows publishers to recognize 
reuse of constraints.

**Known gaps**

  - Predicates over datum *contents* beyond exact-bytes equality are out of scope.
  - A guard requirement may name only a key credential. A key hash appears
  in the script context as a signatory; a script credential does not, and
  whether Dijkstra's script context lets a guard read the transaction's guards
  set is an open upstream question. 
  - The Plutus guard script written as the draft of the constraint 
  interpreter is not audited or tested
  - There is no way to check that a given Plutus guard script really implements
  the constraint-language version it claims.

**Satisfying DSL constraints.**
The reference implementation provides a satisfier, which searches for an
augmentation making a constraint hold, and a two-step planning pipeline over
sets of candidate offers.

Its operation relies on the fact that every requirement is monotone: a satisfier only ever adds
outputs and guards, and nothing it adds can un-satisfy a requirement that
already holds. So it walks the tree, computes each leaf's shortfall against
what the batch already has, and draws it from the pool of value and credentials
the builder controls. `All` sums the shortfalls of its children and checks the
pool once, since they draw from the same pool; `AnyOf` tries its branches in
order and backtracks — on a breached bound as well as an unmet requirement,
since which branch is taken can decide whether a bound holds. The search is
bounded by the branch counts the author wrote, which is what the backtracking
cap fixes. Bounds are only ever checked, never built toward.

**Custom guards** name a DApp's own script hash instead, carry no constraint
datum, and are expected to be deployed on-chain as reference scripts. Supporting
one is optional, as a service may not hold the script (or a reference to it),
or may not have a satisfying strategy for the custom guard.

### Protocol constants

**Envelope and offers.**

| Code name | Constant | Value | Basis |
|---|---|---|---|
| `ENVELOPE_VERSION` | `envelope_version` | 1 | The first revision of this specification. |
| — | `era_tag` values | TBD | Needed to know what CDDL a sub-transaction conforms to |
| `MAX_SUBTX_BYTES` | Sub-transaction size ceiling | TBD | Must leave room for several sub-transactions plus the top-level body and guard witnesses inside `maxTxSize` |
| `MAX_OFFER_TTL` | Maximum offer TTL | TBD | Long enough for a service to see an offer, plan, and submit; short enough that an abandoned offer clears without intervention |
| `MAX_ENVELOPE_OVERHEAD_BYTES` | Maximum envelope overhead in bytes | Proposed `16` | The envelope is two small integers and a tag-24 wrapper, so its cost over `subtx_bytes` is bounded. Fixing it makes the largest gossip message computable |

All of these are released with the (versioned) specification revision and enforced by the
[stateless checks](#stateless-checks--performed-by-publishers-relays-services).
An offer breaching one stops at the first
recipient rather than travelling. 

**Constraint language.**

| Code name | Constant | Value | Basis |
|---|---|---|---|
| `MAX_CONSTRAINT_DEPTH` | Maximum constraint depth | Proposed `16` | Bounds nesting |
| `MAX_CONSTRAINT_NODES` | Maximum constraint node count | Proposed `128` | Bounds total size|
| `MAX_BACKTRACKING_BUDGET` | Maximum backtracking budget | Proposed `1024` | The product of `AnyOf` branch counts |

Also released with the specification revision, and also enforced among the
stateless checks.

**Diffusion, pool and service.** 

`MAX_GOSSIP_MESSAGE_BYTES`, `RELAY_REANNOUNCE_INTERVAL`, `HINT_TTL`,
`PEER_FAN_OUT`, `PEER_SET_EPOCHS` and `REGISTRATION_DEPOSIT` must be agreed
network-wide: the first three because a party applying a different one refuses
what others accept, the last three because they define one shared draw and are
meaningless held separately. The rest are internal to the party that sets them
(the two rate limits, `MAX_LIVE_OFFERS_PER_UTXO`, the pool ceilings,
`MAX_CONCURRENT_BATCHES`, `MAX_CATCH_UP_WINDOW` and `STATUS_RETENTION`),
bounding either what a party spends on itself or what it
will accept from others.
This CIP fixes values for the first kind and floors for the second.

**Activation is read off the registry rather than announced.** Every
[registration](#on-chain-registration-of-relays-and-services) carries the
[protocol revision](#versioning) its holder runs. A
revision's values take effect once most of the registry has upgraded to it,
counted by the number of valid registrations and checked at each epoch boundary. Nobody announces a date
and nobody has to be watching on the day. What is not policed is whether a party
runs the revision it registered.

| Code name | Constant | Basis | How announced | How enforced |
|---|---|---|---|---|
| `PEER_OFFERS_PER_MINUTE` | Number of offers a peer may send per minute | Limits what one sender costs a recipient | Not announced | By the recipient |
| `SERVICE_OFFERS_PER_MINUTE` | Number of offers a service may send another per minute | The same limit, between services | Not announced | By the recipient |
| `MAX_LIVE_OFFERS_PER_UTXO` | Number of live offers allowed per UTxO | Only one can ever land, so a higher cap only allows re-pricing | Not announced; the refusal says when to try again | By the recipient |
| `POOL_MAX_OFFERS`, `POOL_MAX_BYTES` | Number of offers a pool may hold, and their total size in bytes | When the pool starts evicting | Not announced | By the holder |
| `RELAY_REANNOUNCE_INTERVAL` | Amount of time between repeats of an offer by a relay | Lets a service that joined late still see it | Released with the specification revision | Not enforced |
| `MAX_REGISTRATION_BYTES` | Size in bytes of the largest registration datum | Two parties with different ceilings enumerate different registries and draw different peers | Released with the specification revision | By every reader |
| `MAX_GOSSIP_MESSAGE_BYTES` | Size in bytes of the largest gossip message | The sub-transaction ceiling plus the envelope overhead, both above | Released with the specification revision | By the binding |
| `MAX_CATCH_UP_WINDOW` | Amount of time a service may catch up over | How far back it may ask after reconnecting | Not announced | By whoever serves the catch-up, which truncates a longer request |
| `MAX_CONCURRENT_BATCHES` | Number of batches a service may have in flight | Each holds offers and wallet inputs out of circulation | Not announced | By the service |
| `PEER_FAN_OUT` | Number of backbone peers a service pulls from | Must outrun the share of the registry an attacker can afford to own | Released with the specification revision, in force once most of the registry has upgraded | Not enforced |
| `PEER_SET_EPOCHS` | Number of epochs a drawn peer set lasts | One epoch unless raised. Bounds how long an unlucky draw can isolate a service | Released with the specification revision | Not enforced |
| `REGISTRATION_DEPOSIT` | Amount of ADA a service or relay deposits to register | Registration deposit amount | Released with the specification revision | On chain, by the minting policy |
| `HINT_TTL` | Amount of time before a price hint expires | After this, a quote is not worth using. | Released with the specification revision | By the wallet, which treats an older hint as absent. A service cannot extend it |
| `STATUS_RETENTION` | Amount of time a service answers about a finished offer | Until this, status is still available | Not announced | Not enforced; a 404 in response to an offer query mean "forgotten" rather than "never seen" |


### Offer lifecycle

**States**
Four internal states record one service's progress through its own work for each offer 
in its pool:

| State | Holds when |
|---|---|
| received | passed the stateless checks; waiting on chain-state verification |
| verified | passed the chain-state and pre-inclusion checks — an eligible candidate |
| included in batch | selected into a batch being built |
| submitted | that batch went to the mempool |

Three more are settled by the chain, and any party with a chain view derives
the same answer at the same time:

| State | Holds when |
|---|---|
| confirmed | the sub-transaction's TxId appears in an on-chain batch |
| expired | the validity upper bound is behind the tip |
| invalidated | one of its spend inputs is no longer unspent, etc. |

**Rollback**
A rollback can un-confirm a batch, make a spent input unspent again, and
put the tip back behind a validity bound it had already passed. So a service
holds these provisionally until its chain view has settled to the depth it
trusts, and when a rollback undoes the event behind one of them, it puts the
offer back. A rolled-back confirmation returns the offer to verified, not to
anything new. A settled offer's dedup key is
suppressed, so a service that un-settles an offer also un-suppresses it, see
Re-arrival.

**Superseded** is what a service calls an offer when it
holds a newer one spending the same input (but not with the same TxId). 
The service
still answers about the older offer and its dedup key still suppresses repeats. 
For offers passing chain-state verification, arrival order
decides. A computable
concept of "offer value"
defined internally by the service (see [batching](#batch-construction)) 
would allow for additional adjudication 
strategies.

**Is my offer posted on-chain?**
A publisher is expected to follow the chain to observe whether its offer has 
been posted. The `GET /offers/{offer_id}` queries service-specific state,
and does not provide a reliable answer to whether the offer has been posted.
There is no possible way to partially fulfil an offer.

**Cancellation and re-pricing**
There is no cancel message in our protocol. Cancellation is done by the 
publisher by spending an input of its sub-transaction before it makes 
it on-chain.
Re-pricing is the same mechanism: issue a new offer spending an input the old
one spends. Both are live, at most one can ever land, and a service holding
both marks the older superseded.

**Offer competition.**
For any offer, the first batch containing it on-chain wins, and any other batch 
containing it becomes invalid. The service constructing the invalidated batch 
is not compensated for their work batching that offer.

A service tracks the batches it has submitted. Each
submitted batch is held in one of three states:

| State | Holds when |
|---|---|
| submitted | sent to the mempool, not yet seen on chain |
| included | seen in a block, at that slot |
| superseded | a different batch carrying one of its offers was included, at that slot — so this one can never be valid |

A batch leaves that set only when it expires, which is what keeps inclusion,
supersession and rollback trackable.

**Multiple batches.**
Services can build up to [`MAX_CONCURRENT_BATCHES`](#protocol-constants) at a
time. They must not conflict. 
The `included in batch` state is what marks an offer as claimed, so 
all such offers need to be checked for conflict with any offer 
being evaluated for inclusion, as well as the service's own inputs, 
collateral, etc. 

**Leaving the pool and re-arrival**
Services may drop offers, and peers may repeat offers they hold, 
possibly repeating dropped offers.
A party (relay, service) suppresses reception of the dedup keys of the offers it
currently holds, and some dropped ones (not all offer drops delete the associated 
dedup key, see below). 
If a dedup key is dropped, there is no 
record that a relay or service has ever seen this offer.
The following points specify the conditions of offer drops and dedup key erasure by
services and relays:

1. A service drops an offer because of chain state changes (i.e. offer expired, became
invalidated or confirmed, or because of a scheduled cost-model change).
We call such an offer a *dead* offer. 
The service keeps the dedup key of a dead offer and does not
readmit it, until point 4 below retires the key, and it keeps answering about
the offer for the [status-retention period](#protocol-constants). A rollback that undoes the
settling undoes both, and the offer is an ordinary candidate again.

2. A service may also drop an offer for local or transient reasons: pool pressure, a
cap on how many live offers share one spend input, or a narrowing of its
profile (see Local drop strategies, below). In such cases, dedup keys are deleted, and 
the corresponding offers are readmitted on re-arrival.

3. A relay drops only on
expiry, which is derivable from the body, and its own buffer running full. The
second is a local drop, so the dedup key goes with the offer.

4. The dedup key is erased by each party once the offer's validity upper bound
is behind the best clock that party has: the tip for anyone holding chain state,
local time for a relay, which is never required to hold any. A rollback makes
the offer live again, so retiring the key at expiry is what allows the revived
offer to be accepted again. Clock skew only shifts when a party readmits an
offer it would refuse on its own merits anyway.

**What a relay tracks.** 
A relay tracks what offers it holds, and *no* records of which services have been 
sent the offers it holds (or held). This is why the
rule above is stated over holdings rather than over deliveries, and why a
service seeing the same offer from three relays is normal.
However, a binding may run its own message-level duplicate cache, 
as gossipsub does.

**Local drop strategies**
When the pool is over its [ceiling](#protocol-constants), a service drops the
offers a batch would earn least from per byte they occupy, oldest first on a
tie — ranked by the same
[`ValueFunction`](#batch-construction) that ranks them for inclusion, since a
service evicting by one rule and batching by another throws away what it was
about to use. Settled offers are never chosen: they are held to answer about,
and dropping one would readmit a dead offer. 


### Batch construction

**Value Function**
To define a batching strategy, a service needs to specify its 
own `ValueFunction`.
This function takes an offer and calculates a `u64` output 
representing the value 
it provides to the service which defined it. This value function is pluggable.
The default is `UniformValue`, which returns the same number for every offer.

**Batch construction** requires the following two actions:

1. *Selection is which offers go in.*
We give a deterministic strategy that is not optimal.
For `select_compatible_subset`, the v1 reference implementation
uses greedy value density: rank each offer by its `ValueFunction` output
divided by
the larger fraction it consumes of either the serialised size or the execution
units budget. Offers are taken in that order, and 
any that would exceed a budget or
share a spend input with one already taken are skipped. 
Ties break by offer identity, so
the same pool always yields the same batch.

A service with the default `ValueFunction` selects by cost alone:
smallest and cheapest first, which is the most offers served per batch. 

Selection here is the knapsack solution from the
original Babel Fees paper with two capacities rather than one.
The optimal solution of the exact problem is
NP-hard, so the packing algorithm is pluggable.
Greedy density is a default that works.

2. *Construction is turning the chosen set into a valid transaction.*

**Sub-transactions go in verbatim.** No re-encoding is done.

**The batch balances.** Each sub-tx contributes an imbalance,
the builder supplies inputs and outputs absorbing the sum, and whatever is left
over is the builder's margin. What shape the
remainder goes back in is [liquidity strategy](#liquidity-strategy). 

**The batch pays the fee and posts the collateral.** A sub-transaction body has
no fee field and no collateral.

**Every required top-level guard must be satisfied.** The builder supplies the
guard redeemers and their execution units. Custom approaches are required for 
more sophisticated functionality. 

**No two sub-transactions may share a spend input.** `NoOverlappingSpendInputs`
is a ledger rule over the whole batch.

**Re-simulate against the tip immediately before submitting.** That is, 
perform the pre-inclusion checks.

The following pseudocode fixes the required order without fixing a particular
packing algorithm or wallet implementation:

```text
build_batch(candidates, tip, protocol_parameters):
    live = revalidate_inputs_and_validity(candidates, tip)
    selected = select_compatible_subset(live, protocol_parameters)
    require no_duplicate_offer_ids(selected)
    require no_overlapping_spend_inputs(selected)

    field_23 = map_each_txid_to_original_subtx_bytes(selected)
    constraints = decode_required_top_level_guards(selected)
    augmentation = satisfy(constraints, selected, service_liquidity)
    require evaluate(constraints, selected + augmentation)

    body = assemble_top_level_body(field_23, augmentation)
    repeat:
        fee = compositional_min_fee(body, selected, protocol_parameters)
        funding = select_service_inputs(sum_imbalance(selected), fee, collateral)
        next_body = balance(body, funding, fee, change)
    until serialise(next_body) and fee are unchanged

    tx = add_guard_redeemers_and_witnesses(next_body)
    require serialised_size(tx) <= maxTxSize
    require execution_units(tx) <= maxTxExUnits
    require phase_1_and_phase_2_validate(tx, latest_tip)
    submit(tx)
```


**Dijkstra dependencies**
The exact (field-23) encoding, compositional minimum-fee calculation, collateral
accounting, script context, execution-unit accounting, and final ledger
validation call are blocked on the final CIP-118/Dijkstra ledger interface.


### Liquidity strategy

A service pays for every batch it builds, so it has to hold the value it pays
with. A liquidity strategy is how it redistributes that value across the UTxOs and
accounts it controls — input selection, how many outputs to itself, which assets in which, how
much to keep liquid against how much to consolidate. 

**Where the value comes from**
The `select_service_inputs` step of [batch
construction](#batch-construction) is ordinary coin selection, a problem
wallets already solve, and this document delegates it to whichever wallet a
service runs rather than specifying one. In addition to the usual input 
selection process, an input chosen for a
batch still being built must be held out of selection until that build finishes
or abandons, and collateral is kept apart from spendable
funds. The reference implementation settles one asset at a time in a fixed
order, with lovelace first. For each asset, a service draws at random from the set 
of UTxOs it owns containing that asset until a
sufficient quantity of the asset is added to the consumed side of 
the top-level tx being constructed. 

**Where the value goes**
The budgets in a
[service profile](#service-profile) can be specified to constrain what a service will expose at
once so an author can tell whether its offer is even in range.

**Using accounts**
A key liquidity constraint is that a specific UTxO may be present in exactly 
one batch. However, value held in an account is not divided
into UTxOs at all, and using a single account makes for smaller transactions.
For a service
paying many small amounts, that is the difference between a floor per payment
and no floor at all. An author can constrain what a batch does to an account
through the ledger's own balance intervals, which is why offers that use either
carry a [filter key](#filter-key-kinds) saying so: a service that has not
implemented them can decline the whole class rather than discover one mid-batch.

**The default** is: consolidate, keep as many spendable holdings as the
concurrency an operator wants, keep collateral separate, and let accounts absorb
whatever does not need to be a UTxO (see [batch
construction](#batch-construction)).

**Configurability.** The layout rule is replaceable whole, as the [value
function and the packing algorithm](#batch-construction) are. The rule 
is also configurable
without replacing it wholesale. The
reference implementation lets an operator say how much lovelace each change
destination should hold, in what ratio UTxOs to accounts, and a ceiling on how
many. The result is as follows:

- Lovelace splits across every destination, evenly, remainder on the first.
- Native assets can go only to UTxOs. They round-robin across the UTxOs and each
  asset stays *whole*
- A fresh address is generated per change UTxO
- Accounts are only updated, never created


### On-chain registration of relays and services

Registration is optional for both relays and services, and is what allows 
for their discovery.

**What a registration is.** One UTxO, holding one NFT, carrying the record as
its datum. The NFT is retained across updates to the `registration`. 

An NFT that correctly identifies a party is minted under a 
**single shared policy**, which requires:
- a record of the unique UTxO entry spent to forge it (`TxIn`), which is what makes the name unmintable twice
- the role of the party (service vs relay), which prefixes that name and so is fixed for the registration's life
- the hash of the public key of the party that must sign it at the time of minting and burning (full PK can be obtained from monitoring the chain)
- enforcement of deposit (the ADA held in the same output must be at least the deposit)
- the datum (see below) is present and decodes as expected
- the address credential is the same public key hash as the one that signs the minting, and
is the only address at which this NFT can be placed upon being spent

**The datum.**

```cddl
registration =
  #6.121([ schema_version    : uint
         , protocol_revision : uint
         , accepts           : accepted_versions
         , endpoint          : text
         , standing
         ])

; Whether the holder is in the draw, and its profile if it is a service
standing     = #6.121([maybe<service_profile>])   ; in the draw
             / #6.122([])                         ; withdrawn

service_profile =
  #6.121([ accept              : accept
         , rejected_keys       : [* filter_key]
         , rate_source
         , budgets
         , constraint_versions : [* hash28]
         , priority_sales      : disclosure
         , block_producer_arrangements : disclosure
         ])

; Wire formats accepted BEYOND what the protocol revision implies. Empty
; means "exactly what the revision implies", not "nothing".
accepted_versions =
  #6.121([ envelope_versions       : [* uint]
         , era_tags                : [* uint]
         , routing_namespaces      : [* text]
         , profile_schema_versions : [* uint]
         ])

accept       = #6.121([]) / #6.122([[* filter_key]])  ; all / these keys

; The nine kinds under Filter-key kinds
; alternatives 7 and 8 are tags 1280 and 1281, not 128 and 129.
filter_key   = #6.121([hash28]) / #6.122([hash28])  ; offered / needed policy
             / #6.123([]) / #6.124([]) / #6.125([]) ; pure babel / sponsorship / priority
             / #6.126([credential])                 ; guard
             / #6.127([band])                       ; ExUnits band
             / #6.1280([]) / #6.1281([])            ; the two feature markers
band         = #6.121([]) / #6.122([]) / #6.123([]) / #6.124([])
                                              ; none / low / medium / high

disclosure   = #6.121([basis, maybe<text>])   ; the note is for humans only
basis        = #6.121([]) / #6.122([]) / #6.123([]) / #6.124([])
                                              ; none / auction / fixed-fee / bilateral

rate_source  = #6.121([])                       ; self-quoted
             / #6.122([reference : text])       ; a named feed

budgets      = #6.121([ max_value_exposure : { * asset => uint }
                      , max_ex_units_mem   : uint
                      , max_ex_units_steps : uint
                      , max_collateral     : uint
                      ])

; credential, asset and hash28 are the productions given under the Constraint language
maybe<a>     = #6.121([]) / #6.122([a])
```

The two text fields (the endpoint and a disclosure's note) are UTF-8 carried
as byte strings.

A **relay** registers the purpose of peer selection, which draws from the registry, so
an unregistered relay can never be drawn. Its registration
does carry versions, which is why `protocol_revision` and `accepts` sit on
the registration rather than in the profile. A relay forwards envelopes and
subscribes to routing namespaces, so this information must be accessible.

**The datum must be readable from the chain alone.** 
Either inline, or supplied
with the transaction that created it, so that anyone following the chain has it
without asking anyone. 

**Updating a registration.** Spend the UTxO holding the NFT and re-create it
with the new datum. That one mechanism covers every change a registration
admits: a new profile, stepping out of the draw, and coming back. The role is
not among them — it is in the asset name, and changing it would mean minting a
different registration.

**The deposit is TBD.** Specifying a reasonable deposit affects peer selection,
and is one of the [Security considerations](#security-considerations) we discuss.
Peer selection draws only from registrations carrying a sufficient deposit.

*A fixed deposit amount needs a better way to change in future versions.* Currently it is 
released with a software update, which requires on- and off-chain coordination.
Every operator below the new figure must top up by a deadline nothing on chain 
enforces, and whoever is not watching leaves the draw without being told. 
We propose instead deriving the floor from the deposits of valid registrations. 
The alternatives are a 
floor each service sets for itself, a floor announced through a new protocol 
constant, or an on-chain vote. 

Note that *voting on updates* (either via an off-chain mechanism 
processing the registry, or on-chain directly) requires a thorough design that is out of scope.

**An unregistered party** is a normal party. It is reachable by anyone who knows
its address and invisible to everyone else, which is a reasonable position for
an operator serving one wallet or one DApp.

### Service profile

A **service profile** is a service's announced configuration of the policy of 
what offers it intends to engage with. It is different from its [interest filter](#routing-and-filtering), 
because relays are not obligated to act on this information.
How a service chooses among the offers it accepts, including whether it does so
differently from the default design, is not specified anywhere in this document
and may be private. It can be changed 
at any time by posting on-chain, potentially resulting in the service dropping 
some of its offers.

**Contents.** Every registration carries a schema version, the
[protocol revision](#versioning) its holder runs, an endpoint, and which of the
two things it is. The service profile fields are as follows:

| Code name | Field | |
|---|---|---|
| `accept` | accept side | What the service will take: a set of [filter keys](#filter-key-kinds), or the marker meaning everything. Keys rather than assets, since six of the nine kinds are not assets: a service taking only scriptless offers, or only offers guarded by one DApp. |
| `rejected_keys` | rejected keys | Exclusions, which win over the accept side however it is set. |
| `rate_source` | rate source | Where rates come from (not what they are): either quoted by the service itself, meaning read them from `GET /hints`, or a named feed it prices off.  |
| `budgets` | budgets | The operator's risk limits, published so an author can tell whether its offer is even in range. `max_value_exposure` is the most of an asset the service will find **for one offer**, per asset with ADA included, keyed by asset rather than by filter key. `max_ex_units_mem` and `max_ex_units_steps` are ceilings on **the whole batch**, so an offer exceeding one alone can never be included, while an offer under them may still be refused for what it would have to share a batch with. `max_collateral` is what it will post. |
| `constraint_versions` | constraint-language versions | The interpreter script hashes it can satisfy. An offer naming any other is excluded rather than attempted. |
| `priority_sales` | priority sales | Whether the service sells inclusion priority, and on what basis. A structured `basis` : none, auction, fixed fee, or bilateral, with an optional free-text note beside it. |
| `block_producer_arrangements` | block-producer arrangements | Whether it pays for faster inclusion, and to whom, in the same shape. |



### Price hints

A hint is what a service would indicatively charge, published in advance
because [nothing in this protocol can quote back](#binding-a--https). It has two
components, and the reason there are two is that a sub-transaction's cost to a
service has two independent parts.

**1. The rate** is effective lovelace per unit of the token, as a fraction, with
the service's margin already folded in. 
Every service quotes its accepted tokens against ADA, and may additionally quote
**direct pairs** for the ones it makes a market in. 

A hint is served over HTTP and never registered: it carries a number, and
numbers move. What the service registers is the [rate
source](#service-profile) it derives them from, which does not.

**2. The fee-coverage terms** are what the service quotes for carrying the
sub-transaction, shaped like the ledger's own minimum fee: an intercept, a
per-byte term, and per-execution-
unit terms. 

**Arithmetic is the wallet's.** A wallet computes what it must cover — its own
outputs, plus the fee terms applied to its own size and declared execution units
— and converts at the rate to decide what to put on the offered side. 

**Every hint carries when it was produced**, and a wallet should treat an old
one as absent rather than as current. Rates move, and a service has no way to
push a correction to a wallet it does not know exists. A service should drop its
own stale hints rather than serve them, for the same reason from the other side:
a wallet that receives no hint asks elsewhere, where one that receives a stale
hint may sign against it, and a signed offer cannot be taken back.

**Rates set manually.** A service announces its rate hints, but this announcement 
is not fixed to any chain or oracle data.

**Hints bind nothing.** A service that publishes a rate has promised nothing and
may decline any offer quoted against it. 

### Security considerations

**Spam.** Publishers are anonymous
and offers cost nothing to make, so an open network carries junk.
The mitigations are not foolproof, but effective. 
Offers on an open transport must spend at
least one input which must be theirs (this is proved by adding a valid signature). 
Badly signed sub-txs are dropped by relays immediately. More generally, 
stateless check-failing envelopes are dropped, along with those not meeting 
the parties' interest filters. The bad-faith offers still not dropped after
those checks cannot accumulate indefinitely, as they are either eventually evicted by 
incoming offers (pool size is bounded) or expire (because all offers must satisfy
TTL requirement). Finally, we impose limits on the frequency of peer-peer 
envelope transmission, and allow dropping peers at-will.

**Collateral griefing.** A sub-transaction whose scripts
fail at phase 2 validation wastes the service's resources. We address this with
the service's own `max_ex_units_*` budget, which bounds what it will spend
pre-executing before giving up; the ExUnits band additionally lets a service
subscribe away from the offers it does not want to try at all.
Script validation is done once, and the frequency
of incoming transactions is limited by a service's own parameter.
For this reason it is sensible to expect that phase-2 invalid sub-txs,
while not actually paid for, will not significantly interfere with the service's
operations.

As for guards, the limits on the constraint structure are a proxy for 
limiting ExUnits of the execution of the guard Plutus script on the 
constraints encoded as its datum. The service is expected to have 
enough computational power to execute guards sufficiently fast 
given that it sets its own parameters on the constraints it is willing to accept.

**Satisfier attacks.** A satisfier attack forces the satisfier to run for 
so long that it interferes with the service's operations. We address this 
by using caps on the shape of the constraints passed to the guard.

**Non-canonical constraint datums.** 
Refusing anything but the canonical encoding removes associated problems 
such as wasted work by the service.

**Malleability.** A sub-transaction's TxId covers the body, so a third party can
produce a different envelope (with different dedup key) carrying the same offer. 
What lies outside that hash is the witness set and the auxiliary data, and
either can be altered. Adding to either costs the batcher more fee, so an
incoming offer with the same TxId but smaller in size always replaces a
previously seen bigger one. 

**Front-running.** An
offer diffused over a public mesh is visible to everyone before it lands, which
exposes an underlying or future opportunity. An author who cares
can submit to one service
over HTTPS instead of broadcasting.

**Hint baiting**: hints bind nothing, so a
service can advertise attractive terms purely to attract signed offers it never
intends to include, harvesting them as intelligence. A reputation system
may be useful to address this in the future. 

**Priority brokers**: a service may sell
inclusion priority, because a prohibition would be unenforceable. 
To declare it, a service announces 
`priority_sales` in its service profile, whose `basis` is
machine-readable for exactly this reason. Subscribing to the relevant filter 
key, `Priority`, is what gets such offers sent to it.

**Flash-loan-shaped batches.** Flash-loan attacks are expected to be addressed 
at the ledger level.

**Sybil attacks on the registry.**
Peers are drawn uniformly from the registry, so an attacker's chance of
surrounding a given service is its share of registry entries (i.e. on-chain 
registration tokens). 
Too high a deposit excludes the small operators
that make the market competitive. Too low allows the attack to happen.
The required deposit and the number of peers drawn are dependent variables in this
calculation, and neither means anything chosen alone.

**Replay.** Replay is possible and indistinguishable from normal operation 
of parties. The dedup keys allow parties to refuse offers they already 
have.

**Parameter changes.** A scheduled cost-model change that lands before an
offer's validity bound is too much risk for a service provider to take on, 
so such offers are dropped.

**Arithmetic.** A planner adds up numbers an attacker chose, so overflow must
resolve to "does not fit" rather than wrapping into a small number that does.
The reference implementation saturates everywhere.

**Possible extensions.** 

1. A service could
keep a configurable temporary local blacklist of offer signing keys, on whatever grounds
it finds useful, e.g. repeated bad signatures, or several envelopes carrying one
offer identity. 

2. Offers
could be required to carry a signature over the whole envelope by the same
keys that signed the body, which would make a mutated copy invalid. However, 
choosing the smaller valid version of the two envelopes appears to be a better approach.

**Censorship.** We address systematic censorship of certain kinds of transactions by 
certain parties, and censorship of parties by other parties via our peer selection 
process. We propose selecting a fresh set of peers every epoch. 

**Eclipse and partition attacks.** Registry-based peer selection does not prove
that a selected endpoint is independent, reachable, or forwarding. A service
must use diverse transports and network paths where possible, detect prolonged
silence, and permit direct publication to independently chosen services. The
deposit, peer count, draw algorithm, and recovery procedure must be fixed before
this mitigation can be evaluated.

**Untrusted registration data.** Endpoints, profiles, and reference-script
locations read from the registry are attacker-controlled. Implementations must
bound datum and response sizes, validate schemes and addresses, apply connection
timeouts, and prevent access to loopback, link-local, and private infrastructure
unless explicitly configured. Registry discovery must not become an SSRF path.

**Resource exhaustion below the rate limit.** Many identities, slow HTTP bodies,
large SSE backlogs, decompression, CBOR nesting, signature checks, input
resolution, and script evaluation can exhaust different resources independently.
Implementations must impose byte and time limits before allocation, bound all
queues and concurrent work, and isolate expensive validation from intake. A
single per-peer message rate is not sufficient.

**Offer privacy and linkage.** Offers reveal intended trades, inputs, validity
bounds, guards, and signing keys before inclusion. Routing topics reveal asset
interest to observers, while status and streaming endpoints can reveal service
inventory. Implementations should minimize logs and retention, avoid exposing
pool contents through status errors or streams, and document that HTTPS protects
only the hop to the chosen service, not that service itself.

**Conflicting offers and batch races.** Re-pricing and cancellation deliberately
create conflicting offers. An attacker can also race a service by spending an
input after pre-execution or by submitting the same offer through another
service. Builders must re-resolve every selected input and reserve their own
funding and collateral immediately before submission; failures must release all
local reservations. This bounds wasted work but cannot remove the race.

**Silent cuts.** A service can
detect silent cuts by publishing offers (called *canaries*) through and watching for them at
its own other endpoints. Such an offer must be indistinguishable from a 
real offer, and will be posted on-chain (paying fees, etc.) if successfully 
processed. A future revision could make a canary a `Priority` offer — one that
needs nothing and offers a little ADA.

**Auxiliary data has no separate cap.** The envelope can contain extra unused data 
and still be valid. A dedicated cap in the future may be a way to address this.

## Rationale: How does this CIP achieve its goals?

The [Specification](#specification) requires four main components for 
an off-chain mechanism to support, and we discuss here how each turned out.

#### Components built

**Off-chain network protocol for offer and interest communication** 
We discussed the possible [transport bindings](#transport-bindings) for the 
off-chain network across which offers are communicated. We gave options
(`libp2p gossipsub`, HTTPS, etc.), 
which are not mutually exclusive, and indicated which ones are the 
best options for the different use cases of our mechanism.
Peers are drawn at random from an on-chain
[registry](#on-chain-registration-of-relays-and-services) for the `libp2p
gossipsub` binding, and must be known in advance for the HTTPS binding.
We defined the [envelope](#offer-envelope) an offer travels in across the network(s), which 
can be submitted by an anonymous publisher, outlining why its 
contents are necessary and sufficient for both security and expressiveness. 
Offer deduplication and modification is also addressed.
To ensure that offers being communicated get to the recipients interested in 
filling them (more on this below), as well as to reduce spam, we provided support for [routing and
filtering](#routing-and-filtering) on relevant transport bindings. 
Services and relays are expected to perform different levels of tx and 
offer [validation](#validation) 
based on their access to chain state, and at different points in its lifecycle.
We also discuss tracking the offer across the various stages of its 
[lifecycle](#offer-lifecycle), including inclusion, supersession, cancellation, and rollbacks.

**Service registration for discovery**
Service and relay registration is tracked via optional
[on-chain registration](#on-chain-registration-of-relays-and-services). 
The registration requires posting a UTxO containing an NFT with a specific policy,
uniquely identifying (in the registry) the holder of the key it specifies, the party's 
role (service vs. relay), and an optional datum.

**Batch construction** 
Tx selection and
liquidity management strategies, as well as assessment of value-to-service for 
tx's incoming to a service's pool may require bespoke solutions.
We provide a scaffold of a batching protocol with a core that is useful to most if not 
all services, together with support for substituting [selection](#batch-construction), 
[liquidity](#liquidity-strategy), and [value function](#batch-construction)
specifications. Such kind of service customization may be kept fully private. 
We also provide simplistic default strategies for each.

The publisher of an offer has some say about what kind of batch their offer 
can go into. They can specify constraints on the container batch via 
the [constraint language](#constraint-language). Constraints are specified 
as expressions in a (versioned) DSL, and encoded as datums to a single (versioned) 
guard script, which is then checked on-chain. We describe a basic satisfier that allows the 
service to build the batch against these constraints, as well as a mechanism 
for updating the DSL version (multiple versions may be in use even within a single service).


**Service customization**.
We provide support for publicly customizing 
services both off-chain and on-chain. Setting an [interest filter](#routing-and-filtering)
ensures that well-behaved parties will forward the service only the types of 
offers configured in the interest filter.
The [service profile](#service-profile) is an on-chain
schema with operator-authored contents, stating further constraints on
what offers an operator is willing to entertain. Parties relaying offers are not aware of the constraints in the service profile. 
It is announced via the *datum of the registration UTxO*, and 
can also be queried off-chain. 
Prices services will accept are deliberately not in the on-chain registry: 
registration requires a transaction, and
a rate moving faster than a block should not be fixed on-chain. Instead they are served
off-chain via HTTPS, see [price hints](#price-hints). 

We also discuss
[protocol constants](#protocol-constants). Some are 
fixed at the time of service implementation release (as they are required for 
interoperability), some are or kept private as they are not relevant to 
other users or un-enforcable. Some constants can be queries via HTTPS.

**Security** We outline possible full 
or partial defences to additional [security considerations](#security-considerations).


#### What this makes possible

One of the main goals of nested transactions was
to support babel fees, and the ledger rules they add are necessary for that
without being sufficient: the feature does nothing until some off-chain
infrastructure exists to disseminate, process, 
and batch sub-transactions. As we specify such infrastructure here, the
opportunities we discussed in 
[Motivation](#motivation-why-is-this-cip-necessary) become viable:

**Users holding no ADA can transact**. A sub-transaction does not pay fees or 
collateral, and implicitly asks for its min-UTxO values to be covered. Such a sub-tx 
may spend some user-defined tokens, but no ADA itself.
As such, it can reach the chain without further work by
the author: a wallet publishes it and waits for someone to batch it. Offering 
non-ADA tokens as payment/in exchange to this batching service makes such a sub-tx 
a *babel fees offer*. The resulting experience is similar to paying 
fees/min-UTxO in non-ADA tokens without a global exchange rates registry.

**Multi-user, multi-UTxO swaps get cheaper, faster and less contended** 
Multi-user, multi-UTxO swaps usually require either an exchange to be managing 
users' funds (which may be too much of a risk for some users), 
or a protocol for generating the required signature set (potentially slowing 
down the exchange significantly, or requiring sophisticated cryptographic primitives). 
Infrastructure for building batches we propose here allows users to remain 
in control of their funds, and uses only the signatures already in use on-chain. 
It also reduces the communication overhead required. Moreover, because our 
protocol allows multiple offers from multiple users to be included in a single 
transaction, managing contention and liquidity becomes easier: the liquidity provided 
by the service is shared across all offers in a batch. Size-based and per-transaction 
costs reduce because witness sets are shared across sub-tx's in a batch, and batches 
contain multiple offers that previously would have had to each be in a separate transaction.

**New business becomes viable** 
Because being a service needs no permission and
no integration, the barrier to entry is low. Services enter the ecosystem
by installing software and registering on-chain, where they can be immediately 
discovered by users/publishers. Distributed batching infrastructure streamlines communicating
opportunities and partnerships between users, with no need for centralization. Services are free 
to communicate the opportunities via the public customizations we enable, 
and further align their operations with their goals by private choices of strategies (offer 
selection, liquidity, etc), 
bringing their business models online.

**Arbitrary intents** 
The fulfilment of generalized intents is something this CIP paves the way for.
A service takes a signed statement of what someone wants, works out a
transaction that delivers it, and gets paid for the work. Babel fees is one
instance of that shape, and it motivates others beyond what the nested-transaction
ledger and this design directly support — intent-based light clients, for
example, which we discuss below as a possible extension. 

A *light client* (LC) protocol built on the same infrastructure 
can take the same shape, but requires some extra steps.

[Cavefish][] describes such an LC protocol. A client (locally) defines 
a constraint, then compiles it into a guard datum. An LC that does not keep 
track of the chain (possibly not even its own current wallet state) cannot build 
even a valid sub-transaction. 
To enable the additional steps required to support this 
type of client, the following functionality must be added/modified in the protocol we propose
in this CIP:

1. Likely a stronger constraint language
1. Envelopes that carry data other than what we specify here (e.g. only guards and signatures)
1. Additional service profiles, interest filters, and protocol constants constraining this type of LC traffic

To enable LC functionality, an additional item must be supported that is entirely 
outside this protocol CIP:

- A trusted/audited UI for LC's intent (guard/constraint) construction

A thoroughly audited constraint encoder and decoder matters more here than
anywhere else, since a light client has no other way to tell what it signed.
An additional item, one which is the reason for the cryptographic complexity of Cavefish, 
may be required:

- A cryptographic or incentive-based way to guarantee that an LC cannot build a new, fully valid
top-level transaction out of the sub-transaction the service provider has constructed to satisfy 
their intent 

It is possible that an LC that does not follow the chain is also not capable of 
modifying the sub-transaction they receive in response to their intent 
in a way that allows it to ever be placed into a valid top-level transaction. For example, 
it may be unable to correctly modify the sub-transaction without access to the resolved 
inputs. If this is the case, 
the cryptographic complexity of the resulting protocol is significantly reduced.

#### Work blocked on prerequisites

- Batch construction beyond selection: the field-23 encoding, compositional
      minimum fee, collateral accounting, script context and execution-unit
      accounting all wait on the final CIP-118/Dijkstra ledger interface.
- Test vectors for that interface 
- Whether a guard requirement may name a script credential
- The [cost-model cliff](#chain-state-checks--performed-by-publishers-services)
      check, which needs the scheduled cost models the chain observer does not
      yet expose.
- Recognising one's own batch, or one of one's offers, in a block: the
      [submitted-batch states](#offer-lifecycle) and their rollback behaviour
      are settled, but reading block contents is not something the chain
      interface exposes yet. 

#### Alternatives, prior art and compatibility

Alternatives are argued where the
decision they bear on is made, rather than gathered here: declared economics
against derived filter keys under [Routing and
filtering](#routing-and-filtering), reservations against races under [Offer
lifecycle](#offer-lifecycle), request-for-quote against non-binding hints under
[Price hints](#price-hints), a shared reputation record against local drops
under [Security considerations](#security-considerations), and a fourth envelope
field against the fixed three, also there. Prior art is in the References, and
the two pieces that shaped the design are named where they bear: the original
Babel Fees paper's packing result under [Batch construction](#batch-construction)
and Cavefish in the light-client discussion at the end of this section.

Backward compatibility does not arise. This specifies an off-chain layer that
does not exist yet, over a ledger feature that is itself new, so there is no
deployed behaviour to preserve.

## Path to Active

### Acceptance Criteria

- [ ] CIP-118 is Active and the Dijkstra CDDL is final on a public network.
- [ ] Two implementations built independently interoperate: an offer built by
      one wallet, published to a service from the other implementation, is
      batched and lands on-chain.
- [ ] A published set of test vectors, and both implementations agree on all of
      them. See the Implementation Plan for what the set contains.
- [ ] A relay built from this document alone passes the obligation floor: it
      forwards what passes the stateless checks, deduplicates, rate-limits, and
      drops peers, without holding chain state.
- [ ] An interpreter guard exists, is audited, and evaluates the published
      conformance vectors identically to an off-chain evaluator.
- [ ] Every protocol constant has a value and a stated basis
- [ ] A devnet demonstration in which an offer is published, batched by a
      service that did not author it, and confirmed — with a second service
      losing the race and recovering.

### Implementation Plan

- [x] envelope wire format (encoder, decoder, byte-level test vectors)
- [x] sub-transaction reading and imbalance derivation, against the Dijkstra CDDL
- [x] the stateless checks, shared by services and relays
- [x] the relay obligation floor (transport-independent; mesh shell outstanding)
- [x] v1 selection (greedy value density)
- [x] constraint wire format (PlutusData encoding, tags pinned by test)
- [ ] interpreter guard prototype audit/testing
- [ ] constraint encoder/decoder audit/testing
- [ ] registration minting policy prototype audit/testing
- [x] publish the test vectors (`test-vectors/`, envelope and constraint datum;
      the batch-construction ones wait on the ledger interface)
- [ ] profile/hints schema finalization
- [ ] constants finalization
- [ ] settle registration deposit
- [ ] settle TBD constraint values
- [ ] settle restrictions of assets supported in initial release (e.g. only certain stablecoins) 
- [ ] upstream ledger dependencies (blocker list; filed flags)
- [ ] ecosystem coordination (wallets, explorers, db-sync)
- [ ] network transports: the HTTPS client and the gossip mesh shell are held
      by a toolchain constraint in the reference implementation rather than by
      anything in this specification


## Versioning

The following things carry a version, and each travels with the thing it versions: 
- the protocol revision (the release that fixes the network-wide
  [protocol constants](#protocol-constants)). It is carried in every registration and
  answered at [`GET /`](#binding-a--https),
- the envelope `envelope_version`,
- `era_tag` (on-chain era of the sub-tx)
- the `subtx/v1` prefix in every routing key, 
- the interpreter script hash in every declared constraint, 
- `schema_version` in every registration, and 
- an API version at `GET /`.

Some additional notes on versioning :
- a party meeting a version it does not recognise drops that thing (including schema, guard, etc.);
- `schema_version` exclusion may be loosened in the future;
- a relay carries the protocol revision and accepted versions in its registration
  as a service does, and answers them at `GET /`; 
- on-chain and `GET /` -obtained versions are not policed;
- `accepts` is the only evidence that crosses a revision;


## References

### Cardano Improvement Proposals and Problem Statements

- [CIP-0001][] — CIP process and document structure; this proposal follows its
  format requirements.
- [CIP-118][] "Nested Transactions" (Ledger, Proposed) — the ledger feature this
  proposal supplies an off-chain layer for; source of sub-transactions, guards,
  and fields 23/24.
- [CPS-0015][] "Intents for Cardano" (unmerged, PR #779) — problem framing:
  price discovery, fulfilment status, spam and MEV concerns.
- CIP-0131 "Transaction swaps" (PR #880) — sibling design; source of the
  construction-time-computable offer identity argument.
- [CIP-0137][] "Decentralized Message Queue" — candidate future transport
  binding; pull-based diffusion, and the precedent for the Network category.
- CIP-0089 — Beacon tokens (PR #466) — on-chain discovery by token; cited in the
  discovery appendix.
- CIP-0159 — Accounts and direct deposits; interacts with imbalance derivation
  and the direct-deposits filter key.
- CIP-0112 — [verify title and relevance; appears in no design note]
- CIP-0133 — references Mithril certificate verification; context only.

### External standards

- [RFC 8949][] — CBOR. Tag 24 (encoded CBOR data item, §3.4.5.1) frames the
  sub-transaction payload in the envelope.
- [RFC 2119][] and [RFC 8174][] — requirement keywords.
- [RFC 5234][] — ABNF, used for the routing-key grammar.

### Academic and cryptographic references

- Chakravarty, Coretti, Fitzi, Gaži, Kant, Kiayias, Russell, Vinogradova.
  *Babel Fees via Limited Liabilities*. ACNS 2022. [arXiv:2106.01161][]. The
  original construction this proposal serves.
- *Cavefish: Communication-Optimal Light Client Protocol for UTxO Ledgers*.
  Preprint, 2026. Light-client intent fulfilment with blind-signed,
  input-hidden transactions; discussed under Rationale.
- Fuchsbauer and Wolf. *Predicate Blind Signatures*. Eurocrypt 2024. The
  primitive Cavefish's construction adapts.
- Mithril — stake-based threshold multi-signature. [Documentation][mithril-doc],
  [implementation][mithril-repo]. Specified outside the CIP process; relevant as
  the deployment precedent for a service layer running beside the node.

### Prior art and related implementations

- IOG `babel-fees` prototype (2024) — earlier broker/gossip implementation;
  source of the gossipsub configuration precedent.
- [Decentralized Message Queue implementation overview][dmq-impl] —
  `dmq-node` architecture and deployment model.
- Anoma Resource Machine — intent and enforcement-predicate architecture.
- Bitcoin [Miniscript][] — the tractability requirement for a constraint
  language: non-Turing-complete, satisfier succeeds whenever a solution exists.
- [Tx3][] — transaction description language; candidate surface for a future
  constraint language, see Evolution.
- [ERC-7521][] — generalised intents for smart contract accounts. Considered and
  rejected as a model.
- Radix transaction manifests — pointer only.
- [cardano-ledger issue #5123][ledger-5123] — Dijkstra era tracking.

### Internal documents

*Not for publication; prune before submission.*

- `cip-draft.md` — design-notes companion. Decisions D1–D28, blockers B1–B11,
  verification items, and all discussion notes referenced from this document.
- Internal Babel Fees PRD — scope mandate, balance-free onboarding, worked
  rate examples.
- Statement of Work — a first-release supported-token restriction, which is
  an operator's profile setting and not a property of this specification.
- Ecosystem interviews — anonymised; participants not named.

[CIP-0001]: https://cips.cardano.org/cip/CIP-0001
[CIP-118]: https://cips.cardano.org/cip/CIP-0118
[CPS-0015]: https://github.com/cardano-foundation/CIPs/pull/779
[CIP-0137]: https://cips.cardano.org/cip/CIP-0137
[RFC 8949]: https://www.rfc-editor.org/rfc/rfc8949
[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
[RFC 8174]: https://www.rfc-editor.org/rfc/rfc8174
[RFC 5234]: https://www.rfc-editor.org/rfc/rfc5234
[Tx3]: https://docs.txpipe.io/tx3
[arXiv:2106.01161]: https://arxiv.org/abs/2106.01161
[Cavefish]: #academic-and-cryptographic-references
[pbs]: #academic-and-cryptographic-references
[mithril-doc]: https://mithril.network/doc/
[mithril-repo]: https://github.com/IntersectMBO/mithril
[dmq-impl]: https://github.com/IntersectMBO/ouroboros-network/wiki/Decentralized-Message-Queue-(DMQ)-Implementation-Overview
[Miniscript]: https://bitcoin.sipa.be/miniscript/
[ERC-7521]: https://eips.ethereum.org/EIPS/eip-7521
[ledger-5123]: https://github.com/IntersectMBO/cardano-ledger/issues/5123


## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Transport bindings]: #transport-bindings
[Forwarding]: #forwarding
[Routing and filtering]: #routing-and-filtering
[Validation]: #validation
[Price hints]: #price-hints
[Protocol constants]: #protocol-constants
[Network topology and roles]: #network-topology-and-roles
[Offer lifecycle]: #offer-lifecycle
[Security considerations]: #security-considerations
