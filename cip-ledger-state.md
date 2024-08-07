---
CIP: 78
Title: Extended Local Chain Sync Protocol
Authors: Erik de Castro Lopo <erikd@mega-nerd.com>
Discussions-To: Erik de Castro Lopo <erikd@mega-nerd.com>
Comments-Summary: Extend Local Chain Sync Protocol
Comments-URI:
Status: Draft
Type: ?
Created: 2022-11-15
License: CC-BY-4.0
---
## Abstract

Modify the `cardano-node` (and underlying code) to provide an extended version of the existing
local chain sync protocol.

## Motivation

Applications that provide insight into the Cardano block chain (like db-sync, exporters, Kupo, and
smart contracts reacting to events) often need access to the current state of the Cardano ledger
(stake distribution, reward and wallet balances etc). This information is known to the node, partly
on the block chains and partly in what is referred to as ledger state (described more fully below).
Extracting block chain data is relatively easy, but ledger state data is not. Currently these
applications have to recreate and maintain ledger state themselves based on the block information
they stream from the node over the local chain sync protocol. Recreation and maintenance of the
ledger state is not only complex and a source of bugs but more importantly requires significant
resources, specifically RAM. Ledger state in memory currently consumes 10 Gig of RAM and that is
growing. In situations where the node and any such application run on the same machine, the machine
ends up with twice the resource usage. The following proposal hopes to reduce resource usage and
complexity for chain following applications like db-sync.

### Current Situation

Currently there is a local chain sync protocol which is really just the peer-to-peer protocol
using a local domain socket rather than the TCP/IP socket normally used for P2P transport.

The data transported over this local chain sync protocol is limited to block chain data. However, a
Cardano node also maintains ledger state which includes:

* The current UTxO state.
* Current amount of ADA delegated to each stake pool.
* Which stake address is currently delegated to each pool.
* Rewards account balances for each stake address.
* Current protocol parameters.

The first of these ledger state components is by far the largest component and is probably not
needed outside the node (and definitely not needed by db-sync). However the others are needed and
stored by `cardano-db-sync` which gets these data sets by maintaining its own copy of ledger state
and periodically extracting the parts required.

This means that when `node` and `db-sync` are run on the same machine (which is the recommended
configuration) that machine has two basically identical copies of ledger state. Ledger state is a
*HUGE* data structure and the mainnet version currently consumes over 10 Gigabytes of memory.
Furthermore, maintaining ledger state duplicates code functionality that is in `ouroboros-consensus`
and the maintenance of ledger state has been the cause of about 90% of the bugs in `db-sync` over
the last two years. The maintenance of ledger state also makes updating, running and maintaining
`db-sync` by operators more difficult than it should be. Finally, if `db-sync` did not have to
maintain ledger state, the size of the `db-sync` code base would probably decrease by about 50% and
the bits removed are some of the most complicated parts.


## Specification

The proposed solution is an enhanced local chain sync protocol that would only be served over a
local domain socket. The enhanced chain chain sync protocol would include the existing block chain
data as well as events containing the ledger data that db-sync needs. This enhanced local chain
sync protocol is useful for many applications other than just db-sync.

Smart contract developers would like an application that turns block chain and ledger state changes
into an event stream. With this enhanced local chain sync protocol, generating an easily consumable
event stream simply requires a conversion of the binary enhanced local chain sync protocol into
JSON.

This enhanced local chain sync protocol is basically the data that would be provided by the
proposed Scientia program (which as far as I am aware has been dropped).

The ledger state data that would provided over the extended chain sync protocol is limited to:

* Per epoch stake distribution (trickle fed in a deterministic manner).
* Per epoch rewards (trickle fed in a deterministic manner).
* Per epoch protocol parameters (tiny so provide in a single event)
* Per epoch reaped pool list (single event).
* Per epoch MIR distribution (single event).
* Per epoch pool deposit refunds (single event).

The small bits of data above are sent as single per epoch events. Large bits of data like the epoch
stake distribution map (which can have millions of entries) are tickle fed as they are calculated
by the ledger. Its deterministic in that give the same ledger state LS, with the same block B, the
events generated will always be identical. This is so that if the consumer is stopped and restarted
and needs to rollback a block or two, the replay will be identical.


## Rationale

THe recommended configuration for `db-sync` is to run it on the same machine as the `node`.
Currently this means that there are two copies of the *HUGE* ledger state data structure (each being
at least 10G in size) on the machine. In addition, `db-sync` and other applications only need about
1% of that data. The rest is


## Test Cases



## Implementations


## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
