## Preamble

---
* CIP: ?
* Title: Cardano Protocol Parameters
* Authors: Kevin Hammond (<kevin.hammond@iohk.io>)
* Discussions-To: <kevin.hammond@iohk.io>
* Comments-Summary: <summary tone>
* Comments-URI: <links to wiki page for comments>
* Status: Draft
* Type: Standards Track
* Created: 2020-10-14
* License: <abbreviation for approved license(s)>
* License-Code: <abbreviation for code under different approved license(s)>
* Post-History: <dates of postings to Cardano Dev Forum, or link to thread>
* Requires: <CIP number(s)>
* Replaces: <CIP number>
* Superseded-By: <CIP number>
---

## Simple Summary/Abstract

This CIP describes the initial protocol parameter settings for the Shelley era of the Cardano blockchain.

## Motivation

We need to provide a concise description of the initial protocol parameter choices, that can be used as the base for future proposed protocol changes.

## Specification

The initial protocol parameters are given below (in JSON format):

```
{
    "protocolVersion": {
        "major": 2,
        "minor": 0
    },
    "nOpt": 150,
    "a0": 0.3,
    "minPoolCost": 340000000,
    "decentralisationParam": 1.0,
    "maxBlockBodySize": 65536,
    "maxBlockHeaderSize": 1100,
    "maxTxSize": 16384,
    "tau": 0.2,
    "rho": 3.0e-3,
    "poolDeposit": 500000000,
    "keyDeposit": 2000000,
    "minFeeB": 155381,
    "minFeeA": 44,
    "minUTxOValue": 1000000,
    "extraEntropy": {
        "tag": "NeutralNonce"
    },
    "eMax": 18
}
```

The meaning of the fields is:

| Field                 	| Initial Value                                                          	| Description                                                                                                                                                                                                                      	|
|-----------------------	|------------------------------------------------------------------------	|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| protocolVersion       	| ```protocolVersion": {         "major": 2,         "minor": 2     }``` 	| Protocol version.  Minor versions indicate software updates (will generally be 0).  Major version 1 = Byron, 2 = Shelley                                                                                                         	|
| nOpt                  	| 150                                                                    	| "Target number of pools" ("k").  Impacts saturation threshold, encouraging growth in number of stake pools.                                                                                                                                                                  	|
| a0                     	| 0.2                                                                    	| "Influence Factor". Governs how much impact the pledge has on rewards.                                                                                                                                                                                                      	|
| minPoolCost           	| 340000000                                                              	| Minimum Pool Cost per epoch (in lovelace).  Enables pledge effect.                                                                                                                                                               	|
| decentralisationParam 	| 1.0                                                                    	| Level of decentralisation.  Starts at 1.  Block production is fully decentralised when this reaches 0.                                                                                                                           	|
| | |
| maxBlockBodySize      	| 65536                                                                  	| Maximum size of a block body.  Limits blockchain storage size, and communication costs.                                                                                                                                          	|
| maxBlockHeaderSize    	| 1100                                                                   	| Maximum size of the block header.  Should be significantly less than the maximum block size.                                                                                                                                     	|
| maxTxSize             	| 16384                                                                  	| Maximum size of a transaction.  Several transactions may be included in a block.  Must be strictly less than the max. block body size.                                                                                           	|
| | |
| tau                   	| 0.2                                                                    	| Treasury rate (0.2 = 20%).  Proportion of total rewards allocated to treasury each epoch before remaining rewards are distributed to pools.                                                                                                                                                                          |                                          	|
| rho                   	| 3.0e-3                                                                	| Monetary expansion rate per epoch.  Governs the rewards that are returned from reserves to the ecosystem (treasury, stake pools and delegators).                                                                                  |
| | |
| poolDeposit           	| 500000000                                                              	| Pool deposit (in lovelace)                                                                                                                                                                                                       	|
| keyDeposit            	| 2000000                                                                	| Deposit charged for stake keys (in Lovelace).  Ensures that unused keys are returned, so freeing resources.                                                                                                                      	|
| | |
| minFeeB               	| 155381                                                                 	| Base transaction fee (in lovelace).                                                                                                                                                                                              	|
| minFeeA               	| 44                                                                     	| Additional transaction fee per byte of data (in lovelace).                                                                                                                                                                       	|
| | |
| minUTxOValue          	| 1000000                                                                	| Minimum allowed value in a UTxO.  Security-related parameter used to prevent the creation of many small UTxOs that could use excessive resource to process.                                                                      	|
| | |
| extraEntropy          	| ```{         "tag": "NeutralNonce"     }```                            	| Should additional entropy be included in the initial phases.  This provides additional certainty that the blockchain has not been compromised by the seed key holders.  Redundant once the system is sufficiently decentralised. 	|
| eMax                  	| 18                                                                     	| Maximum number of epochs within which a pool can be announced to retire, starting from the next epoch.                                                                                                                 	|


## Rationale

The initial parameter settings were chosen based on information from the Incentivised Testnet, Haskell Testnet, SPOs plus benchmarking etc.  This parameter choice was deliberately conservative,
in order to avoid throttling rewards in the initial stages of the Cardano mainnet, and to support a wide range of possible stake pool operator (professional, amateur, self, etc.).


### Key Behavioural Parameters


The key  parameters that govern the behaviour of the system are ``nOpt``, ``a0``, ``decentralisationParam`` and ``minPoolCost``.
Changes to these parameters need to be considered as a package -- there can be unintended consequences when changing a single parameter in isolation.

It is expected that the following changes to these parameters are likely in the near to medium term:

* increasing ``nOpt`` to align more closely with the number of active pools
* increasing ``a0`` to increase the pledge effect
* decreasing ``minPoolCost`` (e.g. in line with growth with the Ada value)
* decreasing ``decentralisationParam`` to 0 (to enable full decentralisation of block production)

Further adjustments are likely to be required to tune the system as it evolves.


### Economic Parameters

Four parameters govern the economics of the system:  ``tau``, ``rho``, ``minFeeA`` and ``minFeeB``.
The first two concern the rate of rewards that are provided to stake pools, delegators and the treasury.
The others concern transaction costs.


### Transaction and Block Sizes

Three parameters govern block and transaction sizes: ``maxBlockBodySize``, ``maxBlockHeaderSize``, ``maxTxSize``.
Their settings have been chosen to ensure the required levels of functionality, within
constrained resource restrictions (including long-term blockchain size and real-time worldwide exchange of blocks).
Changes to these parameters may impact functionality, network reliability and performance.


## Backward Compatibility

This CIP describes the initial set of protocol parameters, so backwards compatibility is not an issue.
Future CIPs may be proposed to change any or all of these parameters.
A change to the major protocol version indicates a major change in the node software.
Such a change may involve adding/removing parameters or changing their semantics/formats.
In contrast, minor protocol changes are used to ensure key software updates without changing
the meaning of protocol parameters.


## Change Process for Protocol Parameter Changes

### Governance

Changes will affect many stakeholders and must therefore be subject to open community debate and discussion.

Ultimately, the Voltaire protocol voting mechanism will be used to achieve fully automated, decentralised and transparent governance.
In the interim, the CIP process will be used.

### Signalling Protocol Parameter Changes

Changes to the parameters need to be signalled to the community well in advance, so that they can take appropriate action.  For the most significant parameters, a minimum of 4-6 weeks
elapsed time between announcement and enactment is appropriate.  This period must be included in the CIP.  Announcements will be made as soon
as practical after the conclusion of the vote.

### Applying Protocol Parameter Changes

Protocol parameter changes must be submitted within the first 24 hours of the epoch before they are required to come into effect.
Once a change has been submitted, it cannot be revoked.

### Voiding Proposed Protocol Parameter Changes

Once a protocol parameter change has been announced, it can only be overridden through the voting process (CIP, Voltaire etc.).  Any vote must be
completed before the start of the epoch in which the change is to be submitted.


## Test Cases

Not Applicable.

## Implementations

Not applicable.

## Copyright

This CIP is licensed under Apache-2.0
