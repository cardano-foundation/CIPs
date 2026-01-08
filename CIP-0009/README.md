---
CIP: 9
Title: Protocol Parameters (Shelley Era)
Status: Active
Category: Ledger
Authors:
  - Kevin Hammond <kevin.hammond@iohk.io>
Implementors:
  - IOG <https://iog.io/>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/45
Created: 2021-01-29
License: Apache-2.0
---

## Abstract

This CIP is an informational CIP that describes the initial protocol parameter settings for the Shelley era of the Cardano blockchain, plus the changes that have been made.
It is intended to serve as a historic record, allowing protocol parameter changes to be tracked back to the original settings.

## Motivation: Why is this CIP necessary?

We need to provide a concise description of the initial protocol parameter choices, that can be used by the community as the base for future proposed protocol changes,
and that document the chain of changes to the parameters.


## Specification

### Proposing Protocol Parameter Changes

This CIP records only the changes to the protocol parameters that have actually been made.  Suggested changes to protocol parameters should be proposed by preparing and submitting a new CIP, rather than editing this CIP.  The following information should be included.

| Name of the Parameter   | New Parameter (Y/N)  | Deleted Parameter (Y/N) | Proposed Value   | Summary Rationale for Change |
|-----------------------  |--------------------  |------------------------ |---------------   | ---------------------------- |

Where necessary, the summary rationale should be supported by a few paragraphs of text giving the full rationale, plus references to any external documents that are needed to understand the proposal.

Protocol parameters are used to affect the operation of the Cardano Protocol.  They may be either **updatable** or **non-updatable**.
Updatable parameters can be tuned to vary the operation of the block producing protocol, impacting the proportion of pools that are federated/non-federated,
how much influence the "pledge" has etc.  Non-updatable parameters affect the fundamentals of the blockchain protocol, including defining the
genesis block, basic security properties etc.  Some non-updatable parameters may be embedded within the source code or implemented as software.
Each major protocol version defines its own sets of updatable/non-updatable parameters.


### Updatable Protocol Parameters

The initial **updatable** protocol parameter values are given below (in JSON format).  Any of these parameters may be changed by submitting
a parameter update proposal.  A change to the major protocol parameter version triggers a "hard fork" event.  This will require stake pool operators to
upgrade to a new software version that complies with the new chain production protocol as well as being able to verify the construction of the chain.

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
| a0                     	| 0.3                                                                    	| "Influence Factor". Governs how much impact the pledge has on rewards.                                                   v                                                                                                                                                   	|
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

### Non-Updatable Parameters

The initial non-updatable protocol parameters are given below (in JSON format):

```
  "activeSlotsCoeff": 0.05,
  ...
  "genDelegs": {
    "ad5463153dc3d24b9ff133e46136028bdc1edbb897f5a7cf1b37950c": {
      "delegate": "d9e5c76ad5ee778960804094a389f0b546b5c2b140a62f8ec43ea54d",
      "vrf": "64fa87e8b29a5b7bfbd6795677e3e878c505bc4a3649485d366b50abadec92d7"
    },
    ...
    }
  },
  "updateQuorum": 5,
  "networkId": "Mainnet",
  "initialFunds": {},
  "maxLovelaceSupply": 45000000000000000e,
  "networkMagic": 764824073,
  "epochLength": 432000,
  "systemStart": "2017-09-23T21:44:51Z",
  "slotsPerKESPeriod": 129600,
  "slotLength": 1,
  "maxKESEvolutions": 62,
  "securityParam": 2160
}
```

The meaning of the fields is:

| Field                 	| Initial Value                                                          	| Description
|-----------------------	|------------------------------------------------------------------------	|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| activeSlotsCoeff                  	| 0.05                                                                     	| The fraction of the total number of slots that will, on average, be selected to include a block in the chain.  Smaller numbers increase security, but reduce efficiency.                                                                                                                 	|
| genDelegs                  	| ...                                                                     	| Details of the public keys that have been selected by each of the genesis keys to act as a delegate for signing protocol updates etc. |
| updateQuorum                  	| 5                                                                     	| How many of the genesis delegate keys must endorse an update proposal.  |
| networkId                  	| "Mainnet"                                                                     	| Is this a testnet or mainnet  |
| initialFunds                  	|  {} | initial distribution of funds to addresses. |
| maxLovelaceSupply                  	| 45000000000000000                                                                    	| The limit on the maximum number of lovelace that can be in circulation. |
| networkMagic                  	| 764824073                                                                    	| A magic number used to distinguish different networks. |
| epochLength                  	|  432000                                                                   	| The number of slots in an epoch. |
| SystemStart                  	|  "2017-09-23T21:44:51Z"                                                                   	| When did the system originally start operation. |
| slotsPerKESPeriod             | 129600                                                                   	| After how many slots will a pool's operational key pair evolve (Key Evolving Signatures). |
| slotLength             | 1                                                                   	| The length of each slot (in seconds). |
| maxKESEvolutions             | 62                                                                   	| What is the maximum number of times a KES key pair can evolve before a new KES key pair must be generated from the master keys. |
| securityParam             | 2160                                                                   	| After how many blocks is the blockchain considered to be final, and thus can no longer be rolled back (i.e. what is the maximum allowable length of any chain fork).  |



### Pre-Shelley Protocol Parameters

The original protocol parameters are given in the Byron genesis file.  These parameters need to be included in any operational stake pool so that the Byron portion
of the chain can be verified, but they can no longer be altered.

```
{
    "avvmDistr": {
    ...
    },
    "blockVersionData": {
    ...
    },
    "ftsSeed": "76617361206f7061736120736b6f766f726f64612047677572646120626f726f64612070726f766f6461",
    "protocolConsts": {
    ...
    },
    "startTime": 1506203091,
    "bootStakeholders": {
    ...
    },
    "heavyDelegation": {
    ...
    }
    },
    "nonAvvmBalances": {},
    "vssCerts": {
    ...
    }
```

### Process for Making Changes to Protocol Parameters

#### Governance

Changes will affect many stakeholders and must therefore be subject to open community debate and discussion.

Ultimately, the Voltaire protocol voting mechanism will be used to achieve fully automated, decentralised and transparent governance.
In the interim, the CIP process will be used.


#### Signalling Protocol Parameter Changes

Changes to the parameters need to be signalled to the community well in advance, so that they can take appropriate action.  For the most significant parameters, a minimum of 4-6 weeks
elapsed time between announcement and enactment is appropriate.  This period must be included in the CIP.  Announcements will be made as soon
as practical after the conclusion of the vote.


#### Applying Protocol Parameter Changes

Protocol parameter changes must be submitted and endorsed within the first 24 hours of the epoch before they are required to come into effect.
For example, a change that is intended for epoch 300 must be submitted and endorsed in the first 24 hours of epoch 299.
Once a change has been submitted and endorsed by a sufficient quorum of keyholders (currently 5 of the 7 genesis keys), it cannot be revoked.

#### Voiding Proposed Protocol Parameter Changes

Once a protocol parameter change has been announced, it can only be overridden through the voting process (CIP, Voltaire etc.).  Any vote must be
completed before the start of the epoch in which the change is to be submitted.

### Change Log

#### Changes to the Updatable Parameters since the Shelley Hard Fork Event

Following the Shelley hard fork event, the ``decentralisationParam`` parameter has been gradually decreased from ``1.0`` to ``0.3``, with the goal of ultimately decreasing it to ``0`` (at which point
it can be removed entirely as an updatable parameter).  This has gradually reduced the impact of the federated block producing nodes, so ensuring that the network moves to become a distributed collection of increasingly decentralised stake pools.
The parameter was frozen at ``0.32`` between epochs 234 and 240.   The ``nOpt`` parameter was changed from ``150`` to ``500`` in epoch 234.


| Epoch |  Date       | Decentralisation | nOpt|
| ----- |  ---------- | ---------------- | ---- |
| 208 |	2020-07-29 |	1 |	150|
| 209 |	2020-08-03 |	1 |	150|
| 210 |	2020-08-08 |	1 |	150|
| 211 |	2020-08-13 |	0.9 |	150|
| 212 |	2020-08-18 |	0.8 |	150|
| 213 |	2020-08-23 |	0.78 |	150|
| ... |	... 	   |	... |	...|
| 227 |	2020-11-01 |	0.5 |	150|
| ... |	... 	   |	... |	...|
| 233 |	2020-12-01 |	0.38 |	150|
| 234 |	2020-12-06 |	0.32 |	500|
| 235 |	2020-12-11 |	0.32 |	500|
| ... |	... 	   |	... |	...|
| 239 |	2020-12-31 |	0.32 |	500|
| 240 |	2021-01-05 |	0.32 |	500|
| 241 |	2021-01-10 |	0.3 |	500|
| ... | ...	   |	... |	...|


#### The Allegra Hard Fork Event

The Allegra Hard Fork Event on 2020-12-16 (epoch 236) introduced token locking capabilities plus some other small changes to the protocol.  No parameters were
added or removed.

```
{
    "poolDeposit": 500000000,
    "protocolVersion": {
        "minor": 0,
        "major": 3
    },
    "minUTxOValue": 1000000,
    "decentralisationParam": 0.32,
    "maxTxSize": 16384,
    "minPoolCost": 340000000,
    "minFeeA": 44,
    "maxBlockBodySize": 65536,
    "minFeeB": 155381,
    "eMax": 18,
    "extraEntropy": {
        "tag": "NeutralNonce"
    },
    "maxBlockHeaderSize": 1100,
    "keyDeposit": 2000000,
    "nOpt": 500,
    "rho": 3.0e-3,
    "tau": 0.2,
    "a0": 0.3
}
```

#### The Mary Hard Fork Event

The Mary Hard Fork Event will introduce multi-asset token capability.  It is not expected that any parameter will be added or removed.

```
{
    "poolDeposit": 500000000,
    "protocolVersion": {
        "minor": 0,
        "major": 4
    },
    "minUTxOValue": 1000000,
    "decentralisationParam": 0.32,
    "maxTxSize": 16384,
    "minPoolCost": 340000000,
    "minFeeA": 44,
    "maxBlockBodySize": 65536,
    "minFeeB": 155381,
    "eMax": 18,
    "extraEntropy": {
        "tag": "NeutralNonce"
    },
    "maxBlockHeaderSize": 1100,
    "keyDeposit": 2000000,
    "nOpt": 500,
    "rho": 3.0e-3,
    "tau": 0.2,
    "a0": 0.3
}
```

#### The Alonzo Hard Fork Event

See [CIP-0028: Protocol Parameters (Alonzo Era)](../CIP-0028).


## Rationale: How does this CIP achieve its goals?

The initial parameter settings were chosen based on information from the Incentivised Testnet, the Haskell Testnet, Stake Pool Operators plus benchmarking and security concerns.  This parameter choice was deliberately conservative,
in order to avoid throttling rewards in the initial stages of the Cardano mainnet, and to support a wide range of possible stake pool operator (professional, amateur, self, etc.).
Some parameter choices (``systemStart``, ``securityParam``) were required to be backwards compatible with the Byron chain.


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


### Backward Compatibility

This CIP describes the initial set of protocol parameters and the changes to date, so backwards compatibility is not an issue.
Future proposals may change any or all of these parameters.
A change to the major protocol version indicates a major change in the node software.
Such a change may involve adding/removing parameters or changing their semantics/formats.
In contrast, minor protocol changes are used to ensure key software updates without changing
the meaning of any protocol parameters.

## Path to Active

### Acceptance Criteria

- [x] The Shelley ledger era is activated.
- [x] Documented parameters are in operational use by Cardano Node and Ledger.

### Implementation Plan

- [x] Original (Shelley) and subsequent ledger era parameters are deemed correct by working groups at IOG.

## Copyright

This CIP is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0). 
