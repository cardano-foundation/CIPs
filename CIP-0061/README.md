---
CIP: 61
Title: Stake-based Protocol Governance Restrictions
Authors: Matthias Benkort <matthias.benkort@cardanofoundation.org> 
Discussions-To: 
Comments-Summary: A simple, transitional, veto power for ada holders until decentralized governance.  
Comments-URI:  
Status: Proposed 
Type: Standards Track 
Created: 2022-06-25
License: CC-BY-4.0
---

## Abstract

The Cardano journey was divided into several phases, the last of which relates to the decentralization of the network governance. We call this last phase: 'Voltaire'. While Voltaire is in the making, some aspects of the protocol remain relatively centralized and under the control of a few entities. This proposal improves on the current status quo by adding a layer of control to the Stake Pool Operators (a.k.a. SPOs) and by extension, to delegators. This proposal is fairly lightweight and can be implemented without a hard fork. 

## Motivation

Decentralized governance is a hard topic and it is likely to take some time to get to a point where Cardano has a fully working decentralized governance. In the meantime, while tolerated until now, the current status quo is judged unacceptable by many. As of today, the number of entities that can control the current set of governance operations is limited. Those operations include:

- Protocol parameters updates
- Protocol versions updates
- Transfers to and from the reserve (a.k.a MIR transfers)
- Transfers to and from the treasury (a.k.a MIR transfers)

At this stage, any such operation can be performed if and only if a [quorum of _5 out of 7_](https://github.com/input-output-hk/cardano-configurations/blob/master/network/mainnet/genesis/shelley.json#L57)<sup>\*</sup> genesis members is reached. Genesis members represent here keys that were assigned to the three founding entities: Input Output, Emurgo and the Cardano Foundation. Because the current quorum limit is 5 and because of the current distribution of the genesis key (3 - 2 - 2), it suffices for only 2 out of the 3 funding entities to perform such an operation. 

Over the past months and years, this topic has been at the centre of many vigorous debates. We thus think that the current status quo has to change.

> \* This ratio is currently configurable via a protocol parameter.

## Specification

We propose to modify the current ledger rules and node configuration to, by default, reject any update proposal or MIR transfer unless they have been explicitly referenced in the node configuration. We propose to make this behaviour optional and only enforced on block-producing nodes (so that, downstream applications such as full-node wallets are not affected unless they desire to). 

More concretely, the node's configuration will be extended to contain a list of pre-authorized transaction ids. Upon validating transactions in blocks, containing either:

- Protocol parameter updates proposals;
- MIR certificates

the ledger will check for the existence of the carrying transaction in the pre-authorized set. Unless present, the transaction will be deemed (phase-1) invalid.

## Rationale

- By doing this, we force any sensitive operation such as update proposals or MIR transfers to be endorsed by a majority (by stake) of block producers. Indeed, only nodes that have endorsed the operation in their configuration will produce and recognize chains containing the operation. This also means that in a situation of no consensus, the network will inevitably fork between those who endorse the update and those who don't. Ultimately, the longest chain rule will apply and the chain that can produce the most blocks will eventually be adopted. That chain will be the one which is endorsed by the most stake (since the block production is roughly proportional to the stake).

- This mechanism means that it'll be impossible to endorse an update unless accepted by the majority of nodes (weighted by the stake they _"control"_). It is important to remark that this mechanism is highly asymmetric: 
  - If the majority of the nodes are NOT endorsing an update, then the network will fork until the majority successfully produce a longer and denser chain than the minority. Then, since that chain would still be valid from the point of view of the minority, it'll eventually be adopted following the longest chain rule. This effectively prevents the founding entities from rolling out updates by themselves, without the endorsement of the majority of the network. 

  - However, if the majority of the nodes are endorsing an update, then, in the case where there exists a minority, it will be impossible for the minority to ever adopt the longest chain produced by the majority unless they also in turn accept the update. In case they don't, they would seemingly be unable to produce new blocks; resulting in a segregated network being formed. If the minority is too large (e.g. 40% vs 60%), this may also drastically reduce the active stake for the rest of the network maintained by the majority and decrease the overall efficiency of the network. 

  It'll be therefore ill-advised for the founding entities to push an update that isn't endorsed by a crushing majority. 

- An immediate consequence of this is that power is also implicitly given to delegators. Because the block production is ultimately determined by stake; should there be a disagreement between an SPO endorsement and its delegators', they would have the opportunity to re-delegate and move their stake away from the SPO, and effectively reduce its influence in the network. 

- This change can be implemented by adding extra validations to the ledger. This would consequently _diminish_ the number of blocks that are considered valid and thus, do not require a hard fork. In fact, a hard fork is required when the number of valid blocks is made _greater_. The proposal also does not change any of the existing binary formats or even, any of the existing procedures when it comes to updates. This seemingly means that updates can still only be issued by the founding members. Yet, it forces them to bring them for discussion and approval before. 

- While this proposal makes it slightly more complicated for the founding entities to create updates (as they are now required to (a) coordinate with the community and (b) pre-create the transaction in a deterministic manner), the technical complexity of endorsing an update for SPOs boils down to adding a line in a configuration file. It is also easy to verify that the added line indeed corresponds to the update since it is a mere transaction id. 

  In particular, Catalyst funds distribution is done through MIR transfers, and this proposal would require every ada-holder (through their SPO) to endorse every MIR transfer coming from Catalyst. In practice, the full list of transfers can be pre-constructed by the founding entities and shared as one configuration file which can be verified manually at first, and automated afterwards. 

## Backward Compatibility

- Any previous protocol parameter update, hard-fork proposals or MIR transfers can be found on-chain and listed in the configuration, to make the existing chain _valid_;
- Or, we could only enable the restrictions after a certain slot, removing the need for specifying any past governance operation (and thus, trimming down a bit the configuration).

## Path To Active

- [x] Discuss feasibility and consequences of the proposal with the core networking, consensus and ledger teams;
- [ ] Discuss the proposal with the ada holder community as well as Stake Pool Operators;
- [ ] Implement the new configuration scheme in the ledger & cardano-node;
- [ ] Roll out a new soft update to activate the mechanism on all nodes of the network

## Copyright

This CIP is licensed under CC-BY-4.0
