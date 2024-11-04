# Adapt CIP-30 to JSON

Here we define an API that is exactly the same as the one specified in CIP-30, with the only difference of using the JSON encodings of CDDL types, as defined in [CIP-0116](./link).

We omit the definition of the different functions, or data types, and only provide the updated signatures as the intended behavior is to follow exactly what is specified in CIP-30. The only other change is that we do not support pagination. Errors are updated to reflect that, and some signatures drop the pagination argument.

## Additional Data Types

Other than the types defined in [CIP-0116](./link) we will refer to types defined by the following schemas.

### Data Types

#### Extensions

```
{
  "type": "object",
  "title": "Extensions",
  "properties": {
    "extensions": {
      "type": "array"
      "items": {
          {
            "type": "object",
            "title": "Extension",
            "properties": {
              "cip": {
                "type": "number"
              }
            },
            "required": ["cip"],
            "unevaluatedProperties": false
          }
      }
    }
  },
  "required": ["extensions"],
  "unevaluatedProperties": false
}
```

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#extension)

#### CollateralParams

```
{
  "type": "object",
  "title": "CollateralParams",
  "properties": {
    "params": {
      "type": "object",
      "title": "Amount",
      "properties": {
        "amount": {
          "type": "number"
        }
      },
      "required": ["amount"],
      "unevaluatedProperties": false
    }
  },
  "required": ["params"],
  "unevaluatedProperties": false
}
```

This type is not explicitly defined in CIP-30, but is used as an argument to `getCollateral`.

#### DataSignature

```
{
  "type": "object",
  "title": "DataSignature",
  "properties": {
    "signature": {
      "title": "Ed25519Signature",
      "type": "string",
      "format": "hex",
      "pattern": "^([0-9a-f][0-9a-f]){64}$"
    },
    "key": {
      "title": "Ed25519PublicKey",
      "type": "string",
      "format": "hex",
      "pattern": "^([0-9a-f][0-9a-f]){32}$"
    }
  },
  "required": ["signature", "key"],
  "unevaluatedProperties": false
}
```

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#datasignature)

### Errors

#### APIError

```
{
  "type": "object",
  "title": "APIError",
  "properties": {
    "code": {
      "type": "number",
      "title": "APIErrorCode"
      "enum": [-1, -2, -3, -4]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code", "info"],
  "unevaluatedProperties": false
}
```

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apierror)

#### DataSignError

```
{
  "type": "object",
  "title": "DataSignError",
  "properties": {
    "code": {
      "type": "number",
      "title": "DataSignErrorCode"
      "enum": [1, 2, 3]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code", "info"],
  "unevaluatedProperties": false
}
```

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#datasignerror)

#### TxSendError

```
{
  "type": "object",
  "title": "TxSendError",
  "properties": {
    "code": {
      "type": "number",
      "title": "TxSendErrorCode"
      "enum": [1, 2]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code", "info"],
  "unevaluatedProperties": false
}
```

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#txsenderror)

#### TxSignError

```
{
  "type": "object",
  "title": "TxSignError",
  "properties": {
    "code": {
      "type": "number",
      "title": "TxSignErrorCode"
      "enum": [1, 2]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code", "info"],
  "unevaluatedProperties": false
}
```

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#txsenderror)

## Main APIs

### Wallet connection API

```
notes:

Do we need to repeat this section from cip-30?
```

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage. A shared, namespaced `cardano` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a `wallet` object with the following methods. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardano.{walletName}.enable()` in order for the dApp to read any information pertaining to the user's wallet with `{walletName}` corresponding to the wallet's namespaced name of its choice.

Optional values are marked with a `?`. Refer to the CIP-30 definition for the behavior of the function when a parameter is omitted.

#### `cardano.{walletName}.enable(extensions?: Extensions): Promise<API>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnameenable-extensions-extension----promiseapi)

#### `cardano.{walletName}.isEnabled(): Promise<bool>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnameisenabled-promisebool)

#### `cardano.{walletName}.apiVersion: String`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnameapiversion-string)

#### `cardano.{walletName}.supportedExtensions: Extension[]`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnamesupportedextensions-extension)

#### `cardano.{walletName}.name: String`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnamename-string)

#### `cardano.{walletName}.icon: String`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnameicon-string)

### Wallet own data API

Upon successful connection via `cardano.{walletName}.enable()`, a javascript object we will refer to as `API` (type) / `api` (instance) is returned to the dApp with the following methods. All read-only methods (all but the signing functionality) should not require any user interaction as the user has already consented to the dApp reading information about the wallet's state when they agreed to `cardano.{walletName}.enable()`. The remaining methods `api.signTx()`, `api.signData()` and `api.submitTx()` (Note: Should submit also enforce this constraint?) must request the user's consent in an informative way for each and every API call in order to maintain security.

#### `api.getExtensions(): Promise<Extension[]>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetextensions-promiseextension)

#### `api.getNetworkId(): Promise<number>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetnetworkid-promisenumber)

#### `api.getUtxos(amount?: Value): Promise<TransactionUnspentOutput[] | null>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetutxosamount-cborvalue--undefined-paginate-paginate--undefined-promisetransactionunspentoutput--null)


#### `api.getCollateral(params: CollateralParams): Promise<TransactionUnspentOutput[] | null>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetcollateralparams--amount-cborcoin--promisetransactionunspentoutput--null)


#### `api.getBalance(): Promise<Value>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetbalance-promisecborvalue)


#### `api.getUnusedAddresses(): Promise<Address[]>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetunusedaddresses-promiseaddress)

#### `api.getChangeAddress(): Promise<Address>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetchangeaddress-promiseaddress)

#### `api.getRewardAddresses(): Promise<Address[]>`

Errors: `APIError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apigetrewardaddresses-promiseaddress)

#### `api.signTx(tx: Transaction, partialSign?: bool): Promise<TransactionWitnessSet>`

Errors: `APIError`, `TxSignError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set)

#### `api.signData(addr: Address, payload: ByteString): Promise<DataSignature>`

Errors: `APIError`, `DataSignError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apisigndataaddr-address-payload-bytes-promisedatasignature)


#### `api.submitTx(tx: Transaction): Promise<TransactionHash>`

Errors: `APIError`, `TxSendError`

[Link to definition](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apisubmittxtx-cbortransaction-promisehash32)

### Wallet query layer API

Upon successful connection via `cardano.{walletName}.enable()`, a javascript object we will refer to as `API` (type) / `api` (instance) is returned to the dApp with the following methods.
All methods should not require any user interaction as the user has already consented to the dApp reading information about the wallet's state when they agreed to `cardano.{walletName}.enable()`.

#### Utxos

##### `api.query.utxos.asset(asset_name: AssetName, minting_policy_hash: ScriptHash) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs that contain some of the specified asset

##### `api.query.utxos.transaction_hash(transaction_hash: TransactionHash) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs produced by the transaction

##### `api.query.utxos.address(address: Address) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs present at the address

##### `api.query.utxos.payment_credential(credential: Credential) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs present at the addresses which use the payment credential

##### `api.query.utxos.stake_credential(reward_address: RewardAddress) : Promise<TransactionUnspentOutput[]>`

Get all UTxOs present at the addresses which use the stake credential

#### Block

##### `api.query.block.number(u_int64: UInt64) : Promise<Block>`

Get the block with the supplied block number

##### `api.query.block.hash(block_hash: BlockHash) : Promise<Block>`

Get the block with the supplied block hash

#### Transaction

##### `api.query.transaction.hash(transaction_hash: TransactionHash) : Promise<Transaction>`

Get the transaction with the supplied transaction hash

#### Transactions

##### `api.query.transactions.block_number(u_int64: UInt64) : Promise<Transaction[]>`

Get all transactions contained in the block with the supplied block number []

##### `api.query.transactions.block_hash(block_hash: BlockHash) : Promise<Transaction[]>`

Get all transactions contained in the block with the supplied block hash

#### Datum

##### `api.query.datum.hash(data_hash: DataHash) : Promise<PlutusData>`

Get the datum that hashes to the supplied data hash

#### Plutus Script

##### `api.query.plutus_script.hash(script_hash: ScriptHash) : Promise<PlutusScript>`

Get the plutus script that hashes to the supplied script hash

#### Native Script

##### `api.query.native_script.hash(script_hash: ScriptHash) : Promise<NativeScript>`

Get the native script that hashes to the supplied script hash

#### Metadata

##### `api.query.metadata.transaction_hash(transaction_hash: TransactionHash) : Promise<TransactionMetadatum>`

Get the metadata present on the transaction with the supplied transaction hash

#### Protocol Parameters

##### `api.query.protocol_parameters.latest() : Promise<ProtocolParams>`

Get the latest protocol parameters

##### `api.query.protocol_parameters.epoch(u_int32: UInt32) : Promise<ProtocolParams>`

Get the protocol parameters at the supplied epoch number

#### Votes

##### `api.query.votes.cc_id(cc_hot_id: CCHotId) : Promise<VoteInfo[]>`

Votes cast by the supplied cc credential

##### `api.query.votes.spo_id(pool_pubkeyhash: PoolPubKeyHash) : Promise<VoteInfo[]>`

Votes cast by the supplied stake pool operator

##### `api.query.votes.drep_id(drep_id: DRepId) : Promise<VoteInfo[]>`

Votes cast by the supplied DRep

##### `api.query.votes.proposal_id(proposal_id: ProposalId) : Promise<VoteInfo[]>`

Votes cast on the supplied proposal

#### Drep

##### `api.query.drep.all() : Promise<DRepInfo[]>`

Get all the known DReps

##### `api.query.drep.id(drep_id: DRepId) : Promise<DRepInfo>`

Get a specific DRep by id

##### `api.query.drep.stake_credential(reward_address: RewardAddress) : Promise<DRepInfo>`

Get the DRep that the stake credential has delegated to

#### Committee

##### `api.query.committee.all() : Promise<CCMember[]>`

Get all known committee members

##### `api.query.committee.id(cc_hot_id: CCHotId) : Promise<CCMember>`

Get a specific Committee member by id

#### Pool

##### `api.query.pool.all() : Promise<Pool[]>`

Get all known stake pools

##### `api.query.pool.id(pool_pubkeyhash: PoolPubKeyHash) : Promise<Pool>`

Get a specific stake pool by id

#### Proposal

##### `api.query.proposal.all() : Promise<Proposal[]>`

Get all known proposals

##### `api.query.proposal.id(proposal_id: ProposalId) : Promise<Proposal>`

Get a specific proposal by id

#### Era

##### `api.query.era.summary() : Promise<EraSummary[]>`

Get the start and end of each era along with parameters that can vary between hard forks
