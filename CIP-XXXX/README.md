---
CIP: ????
Title: Ouroboros Tachys - Faster Cardano partner chains
Category: Consensus
Status: Proposed
Authors:
 - Duncan Coutts <duncan@well-typed.com>
 - Philipp Kant <philipp@ensurable.systems>
Implementors:
 - Well-Typed LLP
 - Ensurable Systems Ltd
Discussions: https://github.com/cardano-foundation/CIPs/pull/1149
Created: 2026-02-06
License: CC-BY-4.0
---

## Abstract

This CIP proposes a specification for Ouroboros Tachýs: a variant of the Ouroboros protocol that uses a public slot leader schedule. Compared to Ouroboros Praos, Ouroboros Tachýs would achieve higher transaction throughput and lower transaction finality times. This protocol is not intended for use on the Cardano mainnet, but for use in Cardano-Cardano partner chains: that is partner chains to the Cardano mainnet that reuse Cardano implementations but with different Genesis and protocol parameters.

The advantage of this Ouroboros variant would be a higher block production rate: approximately 4 times higher compared to Ouroboros Praos. This leads directly to 4x higher TPS and substantially lower transaction finality times. Although the protocol is different, for tools and applications that use the blockchain it would remain highly compatible, allowing the reuse of existing and future Cardano tooling.

The main disadvantage of Tachýs compared to Praos would be not having the DDoS resistance that Praos provides. For partner chains intended to have relatively few block producers, the DDoS resistance Praos provides is of limited benefit. Other forms of DDoS resistance are required, and are possible.

This CIP partially addresses [CPS-0017] and [CPS-0018], for the use case of partner chains.

## Motivation: why is this CIP necessary?

Either partner chains or layer 2 (L2) protocols are plausible solutions for a range of use cases. They both provide a way to scale Cardano without increasing throughput at the Layer 1, i.e. the Cardano mainnet. Partner chains can also act as bridges to other systems, and can provide a range of other special services and benefits.

The motivation for this CIP is to give the Cardano community more options for those use cases, by allowing the Cardano implementations and tools to be reused in a higher performance Cardano partner chain.

It is an appealing idea to reuse the code that runs the Cardano mainnet to also run partner chains. This gives a number of benefits:

 * familiarity
 * security
 * quality
 * immediate availability
 * maturity
 * tooling
 * documentation
 * multiple implementations.

The use cases for partner chains and L2s often need or benefit from higher throughput or lower latency. The fully decentralised world-wide mainnet deployment of Cardano has relatively low throughput, but the same code deployed at a smaller scale – fewer nodes and shorter network links – can achieve substantially higher throughput. By increasing the throughput further still –  with a new protocol variant – we can increase the range of use cases that Cardano partner chains can solve.

The primary use case for Ouroboros Tachýs is any Cardano-Cardano partner chain or isolated Cardano chain that can benefit from higher throughput or lower transaction latency.

There are many use cases for partner chains, including:

 * Reserved capacity for specific distributed applications
 * Reserved capacity for smaller user groups (e.g. within a single industry)
 * Lower operational costs for specific applications or user groups (e.g. allowing lower transaction fees)
 * Applications or user groups requiring low latency for transaction finality
 * Applications or user groups requiring an assurance of no transaction front running
 * Bridging to foreign non-Cardano blockchains or other systems (e.g. Bitcoin or Ethereum-based chains)
 * Different legal or governance arrangements required for particular applications or user groups (including DAOs)
 * Different choices of protocol parameters than Cardano mainnet (both static parameters from the blockchain Genesis and dynamic parameters)

The stakeholders for this proposal are individuals, organisations or consortia that wish to gain value from the use of a partner chain or isolated chain. The software engineers who help to maintain the existing Cardano node reference implementation are also stakeholders. This is not because Ouroboros Tachýs would ever be used on mainnet, but because to maximise Cardano community benefit and to minimise long term maintenance costs, the Tachýs protocol would be integrated into Cardano node reference implementation, to provide an option for users.

A crucial motivation for Ouroboros Tachýs is that of ecosystem compatibility. A great benefit of Cardano-Cardano partners chains is the ability to reuse existing tooling. This relies on the implementation being compatible with tools targeting the Cardano mainnet and testnets. In making partner chains high capacity and lower latency, we do not want to sacrifice that compatibility. Another aspect is that we cannot expect users of the Cardano mainnet to change to support improvements for users of Cardano partner chains, especially as partner chains remain in their infancy.

The use cases we identify benefit from increased throughput, but do not require massive throughput. This is the same problem identified (for Cardano mainnet) in [CPS-0018] "Greater Transaction Throughput". Quantitatively, our rough target for these partner chains is 10x higher throughput than Cardano mainnet. Of the 10x target, 4x can be achieved by Ouroboros Tachýs, and the remaining 2.5x (or more) can be achieved by making partner chain networks geographically smaller, with fewer nodes and fewer hops between block producers and then tuning the protocol parameters for block size and block frequency accordingly.

Some of the use cases we identify benefit from reduced time to transaction finality. This is the same problem identified in [CPS-0017] "Settlement Speed". Ouroboros Tachýs addresses this directly by allowing blocks to be created more frequently and thus any required threshold of block confirmations can be achieved in less time. Furthermore, in the partner chain setting there are different trust assumptions that may be reasonable, and some of these lead to dramatically lower settlement times (see the report by [Davies et al]).

A final important motivation is time to deployment. There are useful use cases that would benefit from increased throughput and lower transaction latency soon. Waiting years would lose that value benefit.

### Relationship to other proposed Ouroboros protocols

Ouroboros Phalanx ([CIP-0161])
: This addresses the problem of grinding attacks and in doing so improves security (by making grinding attacks dramatically more costly) and improves time to transaction finality by allowing the finality analysis to assume grinding is less feasible. It works by adding a VDF, a variable delay function, to each block header that takes time to compute but is quick to verify. It changes the consensus block header format and rules and it thus requires a hard fork.

: Since Ouroboros Phalanx is a relatively clean extension of Praos – adding a VDF but keeping the VRF – it should in principle be entirely compatible with Ouroboros Tachýs. In particular though Tachýs does not use the VRF for leader selection, the anti-grinding would still benefit the epoch nonce calculation, which is the basis for leader selection in Tachýs.

Ouroboros Peras ([CIP-0140])
: This addresses the problem of transaction finality. It uses an optimistic mode in which it can achieve finality in fewer blocks, and a mode that falls back to Praos finality guarantees. As such it improves the time to finality that can be observed for submitted transactions in many cases, but it does not improve the guarantee for worst case finality. By contrast, Ouroboros Tachýs improves the worst case and the average case, albeit by a more modest factor.

: Peras is a modification of Praos but only makes additions to the block header and validity rules. As such, Tachýs should be fully compatible with Peras. It may make sense to use Peras with Tachýs in some partner chain uses cases, where the trust assumptions closely resemble those of Cardano mainnet. In these cases, finality could be better than with either technology on its own. Of course there is also the throughput benefit that Tachýs brings, which complements the Peras finality improvements.

Ouroboros Leios ([CIP-0164])
: This addresses the problem of transaction throughput. In its latest incarnation as "Linear Leios" this takes the form of a one-off (rather than scalable) improvement in throughput by dramatically increasing the effective block size. Linear Leios is targeting a throughput improvement of 30x–60x compared to Cardano mainnet. Linear Leios is a substantial change, with a corresponding expected development time and cost. It is intended for deployment on Cardano mainnet. By contrast, Ouroboros Tachýs is more modest in its throughput goals, more modest in its expected development time and cost and is intended for deployment on Cardano partner chains.

: In principle, since Linear Leios is a strict extension of Praos, Tachýs should be fully compatible with it. It should be possible to use Linear Leios with Tachýs giving even higher throughput than either technology on its own. Linear Leios may however result in higher transaction latency than a pure Tachýs deployment, and so for some partner chain use cases it may be preferable to disable Linear Leios.


## Specification

### Naming: Tachýs

Every member of the Ouroboros family needs a name, and by convention a Greek name. The name "praos", or "πραοσ" means "calm" in English, and reflects the quiet periods in the Praos protocol. The authors are not native Greek speakers, but humbly suggest the Greek word "ταχύς". It means "swift", "speedy" or "rapid". The Latin script transliteration is "tachýs". A pronunciation note for English speakers: the emphasis is on the second syllable: "tach ees".

### Introduction: Praos with a public slot leader schedule

The essential idea for Ouroboros Tachýs is to take Ouroboros Praos and make the minimal possible changes to make it use a public rather than a private slot leader schedule. In particular, the epoch structure and nonce computations are exactly the same, and it continues to use both VRF and KES.

The Ouroboros Praos protocol requires both authentication and authorisation of slot leaders.

Authentication
: The authentication is about proving that a participant is who they say they are. The authentication is proved using a KES signature.

Authorisation
: The authorisation is about who is allowed to create a block in a slot. In Praos the authorisation is proved using a VRF output. The proof of VRF output being greater than a known threshold demonstrates authorisation.

In Ouroboros Praos, the VRF is used for three independent things, using three independent outputs from a single VRF:

 1. Slot leader authorisation
 2. Epoch nonce computation
 3. Chain ordering tie-breaker

For Ouroboros Tachýs we replace the authorisation component of the protocol, but we keep the authentication the same, using KES. We therefore do not use the VRF for authorisation, but continue to use the VRF for the other two purposes. The content and representation of block headers remains exactly the same as in Praos. In particular they still contain the VRF proof and KES signature.

In Ouroboros Tachýs, authorisation works as follows. For each epoch there is a slot leader schedule, which gives a unique SPO identity for every slot in the epoch. Authorisation for a slot within an epoch is demonstrated by authentication as the SPO identity for that slot in the epoch as determined by the slot leader schedule for the epoch.

The slot leader schedule is determined by sampling fairly from the stake distribution of the registered SPOs for each slot in the epoch. The sampling algorithm is seeded from the current epoch nonce and uses an independent sample for each slot. The sampling is weighted by stake: the probability of each SPO being leader in each slot is the same as the fraction of stake delegated to that SPO out of the total active delegated stake. 

### Overview of the changes

There are a few parts of the Cardano specification that must be extended or changed for Ouroboros Tachýs:

 1. Parts within the formal rules for blockchain validity:
    1. introduction of a new global protocol parameter;
    2. the authorisation via the slot leader schedule;
    3. the computation of the slot leader schedule; and
    4. the computation of the cumulative stake distribution used for sampling.
 2. The description of when nodes following the consensus algorithm should create new blocks.

No changes are required to the blockchain CDDL schema, because the block header format is not changed.

### Formal specification changes

The document "A Formal Specification of the Cardano Ledger" covers all the validity rules for the blockchain. This includes what is conventionally considered the rules of the ledger, which is about transactions in the block body, but the document also includes the validity rules for the block headers which is conventionally considered to be part of the consensus protocol. So although we are not changing the rules about transactions, just the consensus protocol, we must nevertheless make changes to the ledger formal specification document.

The baseline version for our changes is the [Shelley ledger specification], as amended by the [Babbage era update] (which changed the consensus protocol from Transitional Praos to Praos).

#### A new global protocol parameter

The ledger rules need to be amended to support multiple consensus algorithms. This is done by introducing a new global constant that selects the consensus algorithm.

The global constant takes a value representing a tag for Praos or Tachýs, or unspecified. When unspecified (as will be the case for existing blockchains such as Cardano mainnet), the rules interpret it as Praos.

Note that this is a global or static protocol parameter, not a dynamic one that can be updated by on-chain governance. Making it a dynamic protocol parameter may be desirable in future: it would allow changing the algorithm after the chain has already been started. Like all dynamic protocol parameters, it could be changed by a governance action, with the effect taking place at an epoch boundary. Introducing a new dynamic protocol parameter would require a hard fork however.

#### Authorisation via the slot leader schedule

We change the rules that specify the authorisation checks: this includes whether a block has been created by the correct slot leader. These need to be adapted to introduce the alternative slot leader schedule.

The existing `PRTCL` rule contains checks for both the authentication and authorisation of the block producer. We keep the authentication part, but change the authorisation check. We make the rule conditional: depending on the new global protocol parameter. For Praos (or unspecified) the rule is exactly the same as the existing Praos rule, while for Tachýs we use a new leader check.

This new leader check is very simple. We compute the slot leader SPO identifier for the slot that the block is from (see the next subsection about the slot leader schedule). We compare this to the SPO identifier from the block header. The two SPO identifiers must be equal. 

The SPO identifiers used here are the same kind of SPO identifiers used throughout the existing Cardano ledger specification: a hash of the SPO's cold verification key. The SPO identifier from the block header is already used elsewhere in the specification and is computed by hashing the cold verification key presented in the block header. The existing KES-based authentication checks ensure that the block header really is created by the declared SPO, so we can rely on the SPO identifier from the block header.

Some minor refactoring of the existing rule makes the introduction of a conditional schedule rule clear and simple. The new conditional rule is somewhat analogous to the overlay schedule of the Shelley era, but with a global parameter deciding which rule is applied, instead of applying rules according to the overlay schedule.

#### Computing the slot leader schedule

The Tachýs slot leader schedule assigns a single SPO identity to each slot within an epoch. This can be computed independently for any slot number within the epoch. It works as follows.

For a given epoch with a known epoch nonce, and for a given slot number we compute a pseudo-random sample value. This sample value is used to select from a (cumulative) stake distribution, to determine an SPO identifier.

The pseudo-random sample value is computed as follows. Take the representation of the epoch nonce, and the representation of the slot number; concatenate their representations and take their cryptographic hash. This uses the standard cryptographic hash function used throughout the ledger specification. This produces uniformly distributed samples in the range of 0 to $2^256 - 1$. Finally, the result is interpreted as a fraction between 0 and 1, using a denominator of $2^256$. The use of a cryptographic hash function is overkill but has the merit of being simple, consistent with the rest of the specification and obviously fair.

The cumulative stake distribution associates each SPO identifier with an interval, inclusive below and exclusive above. The width of each SPO's interval is exactly the fraction of total active stake that is delegated to that SPO. The set of intervals are non-overlapping but contiguously cover the range 0 (inclusive) to 1 (exclusive). This uniquely maps any value in [0,1) to an SPO identifier. The interval values can be specified as rationals, using the total active stake as the denominator. Given that the width of each interval is the SPO stake fraction, then this transforms a uniform sample into a stake-weighted sample.

Thus, given a sample in the range [0,1), a unique SPO can be selected from the cumulative stake distribution. This is the slot leader.

A note on efficiency. This selection can be done in log time, in the number of SPOs, using straightforward representations. While the specification is in terms of rational numbers (like other parts of the ledger specification), some simple algebra demonstrates that this can be implemented faithfully using only (big) integer arithmetic.

#### Computing the cumulative stake distribution

Before the beginning of each epoch, the ordinary SPO stake distribution is transformed into a _cumulative_ distribution function (CDF). This CDF partitions the interval [0, 1) of active stake into contiguous subintervals, each associated with one stake pool.

The CDF can be computed relatively straightforwardly from the ordinary SPO stake distribution used in the existing specification. Note that the ordinary stake distribution is still needed.

The existing ordinary SPO stake distribution associates each SPO identifier with a stake fraction. The CDF can be computed iteratively by maintaining a running cumulative stake, and considering each SPO identity from the ordinary stake distribution in order. For each one, we define an interval with an inclusive lower bound of the running cumulative stake, and an (exclusive) upper bound that is greater by the SPO's own stake fraction. The new (exclusive) upper bound of this becomes the running cumulative stake for the next iteration.

This satisfies all the required properties of the CDF set out in the subsection above, and by taking the SPOs in order of the representation of their identifiers, this specifies a unique CDF value (for any starting distribution).

Note that this is a specification, not an implementation. Efficient implementations are possible, using a representation with a single integer value per SPO.

The existing stake pool distribution becomes stable well before the epoch boundary. There is therefore plenty of time to compute the cumulative stake distribution before the epoch boundary for implementations that wish to do so. Even if it is computed only at the epoch boundary, the stake distribution is "small" – being proportional to the number of SPOs – and so simple $O(n)$ transformations on it are quick.

### Consensus protocol changes

The changes to the consensus algorithm are minimal.

The consensus algorithm must of course create blocks that are valid. This includes making blocks only when authorised. The consensus algorithm takes the predicate from the formal specification that states when a block producer is authorised to make a block and reuses that predicate to evaluate at the start of each slot if the block producer should make a block.

This is the only consensus change, and it changes only in that it must use the updated predicate from the formal specification. The updated predicate is conditional: in Praos mode the condition is as before, while in Tachýs mode the predicate tests the slot leader schedule as described above.

Everything else is the same. The block header construction is the same, using a KES signature and VRF proof. It is just the condition when the node decides to forge a block that changes.

### No hard fork

No hard fork is required.

The reason is as follows. The global parameter that is introduced is optional and the rules interpret no value as defaulting to Praos, so there is no change there. When in the Praos mode, the block header validity predicate is semantically equal to the prior version and thus there is no change in block validity.

The Tachýs design should be highly compatible. Firstly, when not in Tachýs mode there will no compatibility impact at all. Secondly, even when in Tachýs mode most software that interacts with Cardano will also be unaffected. In particular, any software that does not interpret the block headers will be completely unaffected. This covers the vast majority of all Cardano tooling, including all smart contracts and wallets. Blockchain analysis tools, submission tools and explorers should also be unaffected.

Tools that do independent validation of blocks, and specifically block headers would need to be updated before being used on a network in Tachýs mode. This would include alternative node implementations, and any data nodes that are fully-validating. Non-validating data nodes would be unaffected.

### Community consensus

[CIP-0001] calls for the presentation of evidence of consensus within the community and discussion of significant objections or concerns raised during the discussion.

At the stage of initial publication of this CIP, the proposed design has only been reviewed by a handful of experts (acknowledged below). We invite review and discussion of this proposed CIP on (or referenced from) the CIP PR itself, and we will endeavour to address reasonable objections, concerns and suggestions.

## Rationale: how does this CIP achieve its goals?

Consider the main motivations:

 * higher transaction throughput (but not massive throughput);
 * lower time to transaction finality;
 * maintain ecosystem compatibility; and
 * reasonable time to deployment.

In this section we explain how these motivations lead us to the proposed design.

The constraint of ecosystem compatibility is a tight one. It means we cannot meaningfully change the block header format. This puts changes like Ouroboros Leios well out of scope. Additionally, the motivation for a relatively short time to deployment, and cost/benefit analysis also rule out large changes.

Thus we looked for ideas requiring limited technical changes that can provide substantial – but not massive – throughput and latency improvements. We identified one such opportunity in the Praos private slot leader schedule.

In summary, the rationale is that:

 * a private slot leader schedule is of little benefit in small networks; and
 * the cost of a private slot leader schedule is that blocks can only be made 1/4 as frequently as they could be with a public slot leader schedule;
 * thus in many small networks a public slot leader schedule would be the better trade-off.

### The purpose of a private slot leader schedule

Ouroboros Praos uses a private slot leader schedule. What this means is that each SPO knows when they themselves are due to make a block, and nobody else does. This secrecy can be a security benefit by helping to resist against distributed denial of service (DDoS) attacks on Cardano. A (successful) denial of service attack on Cardano would be an attack that pauses block production or limits the ability of users to submit transactions or to access new blocks.

An attacker can use a network level attack on nodes in the system to try to overload them. This may be a simple IP-level flooding attack or potentially a more sophisticated attack at the level of the network protocols. If the attacker knows which nodes are due to make blocks and when they are due to make them, then the attacker can target just a few SPO's relays at a time. On the other hand, if the attacker does not know which nodes will make blocks and when, then the attacker has to target all the relays, or at least enough relays to suppress SPOs controlling a substantial portion of stake. In large networks like Cardano mainnet there is a big difference between targeting a handful of relays and having to target most or all of them. It's the difference between e.g. 10 relays and 1,000 or several thousand (depending on how comprehensive the attacker wants to be). The key point is that the resources needed by the attacker is orders of magnitude more in the case of the private slot leader schedule. This makes the attack much harder and more expensive to pull off.

By contrast with Cardano mainnet, an L2 or a partner chain may have only a small handful of active participants. In this case, the difference between targeting one node and targeting them all is not great in absolute terms. And thus the DDoS resistance benefit of Praos is limited. In these "small" use cases, different approaches are needed to resist DDoS attacks. On the other hand, traditional arrangements for DDoS resistance are also easier to implement where there are fewer participants to coordinate.

### The cost of a private slot leader schedule

The cost of the private slot leader schedule in Ouroboros Praos is in terms of block frequency and thus transaction throughput and time to transaction finality.

The security of Ouroboros Praos relies (amongst many other things) on a parameter called $\Delta$ (Delta), which is the maximum number of slots that it can take for a freshly produced block to be relayed across the network to all other block producers. In the Cardano mainnet this is 5 slots, which is 5 seconds. To ensure security, blocks cannot be produced too frequently. The intuition is that by having block production be slow enough, there are sufficiently frequent "quiet" periods where all blocks can finish being relayed and honest nodes can come to consensus, even in the face of a stake-holding adversary. Indeed the name Ouroboros Praos reflects this: the word "praos" ("πραος") translates as "calm", "meek" or "gentle".

The upshot of this in practice – for the level of security chosen for Cardano mainnet – is that there is a factor of 4 between $\Delta$ (the time for blocks to be relayed) and the average time between blocks.

**That is: in the time it takes for Ouroboros Praos to add one more block to the chain, four blocks (back to back) could be relayed by the underlying network layer.**

This is the cost of a private slot leader schedule: the lost opportunity to create blocks.

### The case for a public slot leader schedule

By contrast to the "sparse" slot leader schedule in Praos, one can imagine a scheme with a "dense" slot leader schedule in which:

 * $\Delta$ is 1 slot;
 * the slot length is chosen to be the time to relay blocks (e.g. 5 seconds to be equivalent to mainnet); and
 * there is exactly one valid slot leader in each slot.
 
In this scheme we would produce and relay blocks back-to-back without any extra "quiet" periods. Instead of a ratio of 4 – as in Praos – the time interval between producing successive blocks and the maximum time to relay blocks would be equal.

Note that this is _not_ about improving the maximum time to relay blocks. It is purely about the gaps in the schedule, or the lack of gaps. For _any_ value of the maximum time to relay blocks, the dense schedule has (on average) 4 times more opportunities to create blocks than the sparse schedule.

A dense schedule can be achieved using a public slot leader schedule. A public slot leader schedule means that everyone (following the protocol) knows which SPOs are due to make a block and in which slots, for the whole epoch. The slot leader schedule (for an epoch) simply assigns each slot to an SPO. This has the straightforward property that every slot has exactly one valid slot leader.

Note that because every slot has exactly one valid slot leader then – unlike in Praos – there can be no slot leader battles. There can only be block height battles, and only if blocks are delayed by more than $\Delta$.

### Protocols with public slot leader schedules

It is well known that BFT style protocols have these simple, dense, public slot leader schedules. There is a peer reviewed paper on [Ouroboros BFT], which is an Ouroboros-style take on classic BFT protocols. This is one plausible choice for a protocol for a partner chain.

Another Ouroboros protocol with a public slot leader schedule is [Ouroboros Classic]. Although in Cardano, Ouroboros Classic was only used in a federated setting in the Byron era, the protocol is compatible with SPOs, delegation, and having block production be weighted by stake.

The protocol that this CIP proposes – Ouroboros Tachýs – however is actually a variant of Praos, modified to use a public slot leader schedule.

There are of course a wide range of other consensus protocols out there, but for important practical reasons we have to limit our choices to sufficiently "Ouroboros-like" protocols.

1. The primary reason is ecosystem compatibility: changing the protocol can have far reaching consequences and can easily introduce incompatibilities that would cause a node using the protocol to not work with existing tooling.
2. An important secondary reason is about ease of integration in existing or future Cardano node implementations. In particular the Haskell reference implementation is designed around the various assumptions and "shape" of the Ouroboros family of protocols. Stray too far from Ouroboros and integration and maintenance would become prohibitively difficult and expensive. The same is likely to be true to some greater-or-lesser extent in other alternative Cardano node implementations.

### Trade-offs of Ouroboros protocols

#### Ouroboros BFT

Advantages:

 * It has a peer-reviewed specification.

Disadvantages:

 * It is not compatible with the existing SPO scheme. It would need changes to how SPOs are managed on-chain, which may require transaction format changes.
 * It would require a new block header format.
 * It would not maintain ecosystem compatibility with Cardano using Praos, due to header format changes and possible changes for SPO management.

#### Ouroboros Classic

Advantages:

 * It has a peer-reviewed specification.
 * It is compatible with SPOs and delegation.

Disadvantages:

 * It has complex MPC algorithm to agree the next epoch nonce.
 * MPC is hard to integrate and needs changes to the block body format.
 * It does not use KES.
 * It would not maintain ecosystem compatibility with Cardano using Praos, due to presence of MPC and lack of KES.

#### Ouroboros Tachýs

Advantages

 * It is fully compatible with SPOs and delegation.
 * It has a low complexity of implementation, integration, and maintenance.
 * It would maintain high degree of ecosystem compatibility, due to no changes in the block body or header formats.

Disadvantages:

 * It has no peer-reviewed specification yet. This CIP is the first step towards this.
 * Other disadvantages may become apparent during the review process.


## Path to Active

### Acceptance Criteria

This CIP should move from "Proposed" to "Active" when at least one publicly known Cardano-Cardano partner chain is using Ouroboros Tachýs in a production / mainnet setting (not just a testnet).

For the purpose of this criterion, we define a Cardano-Cardano partner chain to be any chain that uses one or more Cardano-compatible implementations and that is bridged to the Cardano mainnet.

### Implementation Plan

The plan is to implement and integrate Ouroboros Tachýs into the Haskell reference implementation of the Cardano node. The CIP authors will also cooperate with and advise the authors of other Cardano node implementations who wish to implement Ouroboros Tachýs.

The summary of the implementation plan is as follows:

 * This CIP, feedback and design refinement.
 * A detailed document providing the formal specification of Tachýs as a delta against the existing Cardano formal ledger specification. This will comply with [CIP-0084], but see the subsection below.
 * A prototype (and tests) of the Tachýs consensus protocol, using the existing consensus framework from the Haskell node implementation.
 * Investigate in detail how best to integrate the additional protocol within the existing codebase, and solicit public feedback on a proposed strategy.
 * A trial integration of the new protocol within the existing codebase.
 * System test and benchmarks of the trial integration.
 * A full integration phase, based on feedback from other stakeholders about the integration strategy.
 * Improve the code to production standard, including automated CI tests, docs, code review, security self-assessment.
 * Work with other stakeholders to get the code upstream. Work with upstream reviewers to review the code and address reasonable concerns.
 * Assist with stakeholders who wish to demonstrate Tachýs in a testnet setting and partner chain mainnet setting (on the path to active status).

No hard fork is required, because Ouroboros Tachýs will not be used on the Cardano mainnet and the protocol defaults to Ouroboros Praos.

The authors intend to apply to the Cardano treasury (directly or indirectly) for funding to support this plan. A more detailed implementation plan will be included with the funding proposal.

The CIP authors have substantial experience with such core Cardano work: they comprise two of the three original authors of the [Cardano Shelley design], and together they were the architect and technical lead for the node team that implemented the Cardano Byron Reboot, Cardano Shelley, Mary, Alonzo and Babbage.

[Cardano Shelley design]: https://github.com/intersectmbo/cardano-ledger/releases/latest/download/shelley-delegation.pdf

### The lack of consensus on the Consensus specification

One issue where community assistance would help is the issue of clarity on the canonical reference for the Cardano consensus specification.

The current Praos specification is given by the [Shelley ledger specification], as amended by the [Babbage era update]. There is also however a new effort to provide an [Agda consensus formalisation], in much the same way as the ledger has been re-specified in the [Agda ledger formalisation]. The new Agda consensus specification has not been declared canonical in any meaningful way, either by its authors or the wider community.

Unfortunately, there is little clarity on this topic and clarity is needed in this area. [CIP-0161] for example, provides a delta against the Agda specification rather than the currently active Praos specification. [CIP-0001] gives a process for proposals regarding the Cardano ledger ([CIP-0084]), but no corresponding guidance for consensus CIPs.

The implementation plan above says that we will follow [CIP-0084] and produce a delta against the currently active ledger specification document, but arguably it would be better to produce a delta against the Agda formalisation. This only makes sense however if it is clear that the Agda formalisation is ready and can become the canonical consensus specification.

We suggest that it would be desirable to have a CIP to declare it canonical and provide a process for consensus CIPs in the style of [CIP-0084], and to update [CIP-0001] accordingly.

See also [issue #1073](https://github.com/IntersectMBO/formal-ledger-specifications/issues/1073) for the formal ledger specification project.

## Versioning

As a consensus protocol change, after this CIP has stabilised, any future changes or extensions should be made as independent CIPs.

This CIP can be expected to stabilise after a period of review and feedback, following the normal CIP process. Later minor errata or clarifications could be made directly to this CIP, subject to CIP editor approval. The crucial consideration for such minor modifications must be specification and implementation compatibility.

## References

[CIP-0001]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0001
[CPS-0017]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0017
[CPS-0018]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0018
[CIP-0084]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084
[CIP-0140]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0140
[CIP-0161]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0161
[CIP-0164]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0164

[Davies et al]: https://apexfusion.org/download-vector-well-typed-report

[Shelley ledger specification]: https://github.com/intersectmbo/cardano-ledger/releases/latest/download/shelley-ledger.pdf
[Babbage era update]: https://github.com/intersectmbo/cardano-ledger/releases/latest/download/babbage-ledger.pdf
[Agda ledger formalisation]: https://github.com/IntersectMBO/formal-ledger-specifications
[Agda consensus formalisation]: https://github.com/IntersectMBO/ouroboros-consensus/tree/main/docs/agda-spec

[Ouroboros Classic]: https://eprint.iacr.org/2016/889.pdf
[Ouroboros BFT]: https://eprint.iacr.org/2018/1049.pdf

 * Cardano problem statement [CPS-0017] Settlement Speed
 * Cardano problem statement [CPS-0018] Greater Transaction Throughput

 * [CIP-0084] Cardano Ledger Evolution
 * [CIP-0140] Ouroboros Peras - Faster Settlement
 * [CIP-0161] Ouroboros Phalanx - Breaking Grinding Incentives
 * [CIP-0164] Ouroboros Linear Leios - Greater transaction throughput

 * The [Shelley ledger specification]
 * The [Babbage era update] to the ledger specification
 * [Ouroboros Classic]
 * [Ouroboros BFT]
 * [Davies et al] 2025, an analysis of finality on the Vector blockchain

## Acknowledgements

The authors are grateful for review and feedback on drafts of this CIP from:

 * Kevin Hammond <kevin@ensurable.systems>
 * Joris Dral <joris@well-typed.com>
 * Neil Davies <neil.davies@pnsol.com>
 * Filip Blagojevic <filip.blagojevic@hal8.io>

We are also grateful to Alexander Russell for useful discussion on the plausibility of the Tachýs approach.

## Copyright

Copyright © 2026 Duncan Coutts and Philipp Kant. This work is licenced under [CC-BY-4.0].

This work is *written by humans™*. No part is written by AI.

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
