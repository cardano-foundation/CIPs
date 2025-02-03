## TS API

In this document we list the API endpoints as methods of an Typescript object called `api`. Implementations are free to add further namespaces, as long as they implement an object with the following methods:

### Utxos

#### `api.query.utxos.asset(asset_name: AssetName, minting_policy_hash: ScriptHash) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs that contain some of the specified asset

#### `api.query.utxos.transaction_hash(transaction_hash: TransactionHash) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs produced by the transaction

#### `api.query.utxos.address(address: Address) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs present at the address

#### `api.query.utxos.payment_credential(credential: Credential) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs present at the addresses which use the payment credential

#### `api.query.utxos.stake_credential(reward_address: RewardAddress) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs present at the addresses which use the stake credential

### Block

#### `api.query.block.number(u_int64: UInt64) : Promise<Block>`

Get the block with the supplied block number

#### `api.query.block.hash(block_hash: BlockHash) : Promise<Block>`

Get the block with the supplied block hash

### Transaction

#### `api.query.transaction.hash(transaction_hash: TransactionHash) : Promise<Transaction>`

Get the transaction with the supplied transaction hash

#### `api.query.transaction.block_number(u_int64: UInt64) : Promise<Transaction[]>`

Get all transactions contained in the block with the supplied block number []

#### `api.query.transaction.block_hash(block_hash: BlockHash) : Promise<Transaction[]>`

Get all transactions contained in the block with the supplied block hash

### Datum

#### `api.query.datum.hash(data_hash: DataHash) : Promise<PlutusData>`

Get the datum that hashes to the supplied data hash

### Plutus Script

#### `api.query.plutus_script.hash(script_hash: ScriptHash) : Promise<PlutusScript>`

Get the plutus script that hashes to the supplied script hash

### Native Script

#### `api.query.native_script.hash(script_hash: ScriptHash) : Promise<NativeScript>`

Get the native script that hashes to the supplied script hash

### Metadata

#### `api.query.metadata.transaction_hash(transaction_hash: TransactionHash) : Promise<TransactionMetadatum>`

Get the metadata present on the transaction with the supplied transaction hash

### Protocol Parameters

#### `api.query.protocol_parameters.latest() : Promise<ProtocolParams>`

Get the latest protocol parameters

#### `api.query.protocol_parameters.epoch(u_int32: UInt32) : Promise<ProtocolParams>`

Get the protocol parameters at the supplied epoch number

### Votes

#### `api.query.votes.cc_id(cc_hot_id: CCHotId) : Promise<VoteInfo[]>`

Votes cast by the supplied cc credential

#### `api.query.votes.spo_id(pool_pubkeyhash: PoolPubKeyHash) : Promise<VoteInfo[]>`

Votes cast by the supplied stake pool operator

#### `api.query.votes.drep_id(drep_id: DRepId) : Promise<VoteInfo[]>`

Votes cast by the supplied DRep

#### `api.query.votes.proposal_id(proposal_id: ProposalId) : Promise<VoteInfo[]>`

Votes cast on the supplied proposal

### DRep

#### `api.query.drep.all() : Promise<DRepInfo[]>`

Get all the known DReps

#### `api.query.drep.id(drep_id: DRepId) : Promise<DRepInfo>`

Get a specific DRep by id

#### `api.query.drep.stake_credential(reward_address: RewardAddress) : Promise<DRepInfo>`

Get the DRep that the stake credential has delegated to

### Committee

#### `api.query.committee.all() : Promise<CCMember[]>`

Get all known committee members

#### `api.query.committee.id(cc_hot_id: CCHotId) : Promise<CCMember>`

Get a specific Committee member by id

### Pool

#### `api.query.pool.all() : Promise<Pool[]>`

Get all known stake pools

#### `api.query.pool.id(pool_pubkeyhash: PoolPubKeyHash) : Promise<Pool>`

Get a specific stake pool by id

### Proposal

#### `api.query.proposal.all() : Promise<Proposal[]>`

Get all known proposals

#### `api.query.proposal.id(proposal_id: ProposalId) : Promise<Proposal>`

Get a specific proposal by id

### Era

#### `api.query.era.summary() : Promise<EraSummary[]>`

Get the start and end of each era along with parameters that can vary between hard forks
