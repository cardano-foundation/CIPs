---
CIP:
Title: Universal Query Layer
Category: Tools
Status: Proposed
Authors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
    - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://discord.gg/MU8vHAgmGy
Created: 2024-05-14
License: CC-BY-4.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

A transport-agnostic query layer specification for use in dApps and wallets.

## Motivation: why is this CIP necessary?

See [CPS-12](https://github.com/cardano-foundation/CIPs/pull/625) for motivation.

## Specification

<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

### Existing Query Layer designs

There are two approaches to Cardano dApp development:

1. **Using customized chain followers**. A chain follower is a program that interacts with cardano-node and processes all incoming transactions, as well as rollbacks, to maintain consistent dApp-specific state. Example: [Carp](https://dcspark.github.io/carp/docs/intro/).

2. **Using general-purpose query layers**. General-purpose query layers allow to query blockchain data using a wide set of APIs that are not built with a particular dApp domain in mind. dApp state has to be constructed based on data returned from the queries. Examples: Blockfrost, Maestro.

The first approach allows for lower runtime resource consumption, but a general-purpose query layer has an advantage of being more easily reusable between dApps.

In this proposal, we are focusing on general-purpose querying only.

#### Handling of rollbacks

Transaction rollbacks are essential to blockchains: local node's view of the chain may be different from other nodes'. During conflict resolution, the node may issue a rollback event, that should be handled by dApps.

Customized chain followers, at least in principle, allow for "live" rollback handling: that is, a user-facing dApp can subscribe to a local view of a part of the UTxO set.

General purpose query layers can also handle rollbacks just fine, but they don't propagate rollback events to dApps, because they do not possess any dApp-specific info to determine if a dApp *needs* to handle a particular rollback. dApps that work with general-purpose query layers follow pull-based architecture, rather than event subscription-based, which means they just request data as needed, instead of reacting to blockchain events.

In the context of this API, rollbacks should be acknowledged as a source of potential inconsistency between data pieces returned by different queries.

#### Error handling

Errors should be divided in two categories:

- domain errors
- transport errors (404, 500, etc)

This document should only cover domain errors.

#### Pagination

In CIP-30, pagination is not reliable, because there is no guarantee that the set of UTxOs does not change between calls. This behavior is not suitable for DeFi: consistency should be prioritized, and pagination should be avoided.

### Transports

The API can be implemented across several transports. The goal is to allow several different clients, possibly written in different languages with it.
For this reason we provide an [Openapi schema](./open-api.json) and a more general [JSON-rcp](./json-rpc.json) one. These are generated from the same set of data, the Openapi one is meant to be a specification for interacting with this API through HTTP, while the JSON-rpc one can be followed with transports such as websockets, or when the API is exposed through an injected javascript object.


### Methods

This section contains transport-agnostic method descriptions & their parameter lists.

The scope of this section is loosely based on a [comparison table for existing Cardano query layers](./Query_Layer_API_Comparison.md).
The goal is to make it so that the API could be implemented via simple adapters that transform requests and responses to the appropriate formats.

The payload formats used below are either references to [CIP-0116 - Standard JSON encoding for Domain Types](https://cips.cardano.org/cip/CIP-0116), which specifies cardano domain types via a JSON schema, or references to the [Query Layer JSON schema](./query-layer.json) which we defined in this CIP to define some types that are not present in the CDDL spec.


#### Utxos

##### Asset

Get all UTxOs that contain some of the specified asset

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_utxos_asset)

###### Request


<details>
<summary>Show Example: </summary>

```
{
  "asset_name": "333333333333",
  "minting_policy_hash": "33333333333333333333333333333333333333333333333333333333"
}
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "utxos": [
    {
      "input": {
        "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
        "index": 858993459
      },
      "output": {
        "address": "stake177stake177",
        "amount": {
          "coin": "0000000000"
        },
        "script_ref": {
          "tag": "plutus_script",
          "value": {
            "language": "plutus_v1/plutus_v1",
            "bytes": "333333333333"
          }
        }
      }
    }
  ]
}
```
</details>

##### Transaction Hash

Get all UTxOs produced by the transaction

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_utxos_transaction_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"3333333333333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "utxos": [
    {
      "input": {
        "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
        "index": 858993459
      },
      "output": {
        "address": "stake177stake177",
        "amount": {
          "coin": "0000000000"
        },
        "script_ref": {
          "tag": "plutus_script",
          "value": {
            "language": "plutus_v1/plutus_v1",
            "bytes": "333333333333"
          }
        }
      }
    }
  ]
}
```
</details>

##### Address

Get all UTxOs present at the address

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_utxos_address)

###### Request


<details>
<summary>Show Example: </summary>

```
"stake177stake177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "utxos": [
    {
      "input": {
        "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
        "index": 858993459
      },
      "output": {
        "address": "stake177stake177",
        "amount": {
          "coin": "0000000000"
        },
        "script_ref": {
          "tag": "plutus_script",
          "value": {
            "language": "plutus_v1/plutus_v1",
            "bytes": "333333333333"
          }
        }
      }
    }
  ]
}
```
</details>

##### Payment Credential

Get all UTxOs present at the addresses which use the payment credential

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_utxos_payment_credential)

###### Request


<details>
<summary>Show Example: </summary>

```
{
  "tag": "pubkey_hash",
  "value": "33333333333333333333333333333333333333333333333333333333"
}
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "utxos": [
    {
      "input": {
        "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
        "index": 858993459
      },
      "output": {
        "address": "stake177stake177",
        "amount": {
          "coin": "0000000000"
        },
        "script_ref": {
          "tag": "plutus_script",
          "value": {
            "language": "plutus_v1/plutus_v1",
            "bytes": "333333333333"
          }
        }
      }
    }
  ]
}
```
</details>

##### Stake Credential

Get all UTxOs present at the addresses which use the stake credential

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_utxos_stake_credential)

###### Request


<details>
<summary>Show Example: </summary>

```
"stake177stake177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "utxos": [
    {
      "input": {
        "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
        "index": 858993459
      },
      "output": {
        "address": "stake177stake177",
        "amount": {
          "coin": "0000000000"
        },
        "script_ref": {
          "tag": "plutus_script",
          "value": {
            "language": "plutus_v1/plutus_v1",
            "bytes": "333333333333"
          }
        }
      }
    }
  ]
}
```
</details>

#### Block

##### Number

Get the block with the supplied block number

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_block_number)

###### Request


<details>
<summary>Show Example: </summary>

```
{
  "block_number": "0000000000"
}
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "block": {
    "auxiliary_data_set": {},
    "header": {
      "body_signature": "33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333",
      "header_body": {
        "block_number": 858993459,
        "slot": "0000000000",
        "prev_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "issuer_vkey": "3333333333333333333333333333333333333333333333333333333333333333",
        "vrf_vkey": "3333333333333333333333333333333333333333333333333333333333333333",
        "vrf_result": {
          "output": "333333333333",
          "proof": "333333333333"
        },
        "block_body_size": 858993459,
        "block_body_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "operational_cert": {
          "hot_vkey": "3333333333333333333333333333333333333333333333333333333333333333",
          "kes_period": 858993459,
          "sequence_number": 858993459,
          "sigma": "33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333"
        },
        "protocol_version": {
          "major": 858993459,
          "minor": 858993459
        }
      }
    },
    "invalid_transactions": [
      858993459
    ],
    "transaction_bodies": [
      {
        "auxiliary_data_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "inputs": [
          {
            "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
            "index": 858993459
          }
        ],
        "outputs": [
          {
            "address": "stake177stake177",
            "amount": {
              "coin": "0000000000"
            },
            "script_ref": {
              "tag": "plutus_script",
              "value": {
                "language": "plutus_v1/plutus_v1",
                "bytes": "333333333333"
              }
            }
          }
        ],
        "fee": "0000000000",
        "mint": [
          {
            "script_hash": "33333333333333333333333333333333333333333333333333333333",
            "assets": [
              {
                "asset_name": "333333333333",
                "amount": "222222222222"
              }
            ]
          }
        ],
        "total_collateral": "0000000000",
        "voting_procedures": [
          {
            "key": {
              "tag": "cc_credential",
              "credential": {
                "tag": "pubkey_hash",
                "value": "33333333333333333333333333333333333333333333333333333333"
              }
            },
            "value": [
              {
                "key": {
                  "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
                  "gov_action_index": "0000000000"
                },
                "value": {
                  "vote": "yes/yes/yes/yes"
                }
              }
            ]
          }
        ]
      }
    ],
    "transaction_witness_sets": [
      {
        "Utc": -60000000,
        "redeemers": [
          {
            "data": {
              "Utc": -60000000,
              "alternative": "0000000000"
            },
            "tag": "mint/mint/mint/mint",
            "index": "0000000000",
            "ex_units": {
              "mem": "0000000000",
              "steps": "0000000000"
            }
          }
        ]
      }
    ]
  }
}
```
</details>

##### Hash

Get the block with the supplied block hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_block_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"3333333333333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "block": {
    "auxiliary_data_set": {},
    "header": {
      "body_signature": "33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333",
      "header_body": {
        "block_number": 858993459,
        "slot": "0000000000",
        "prev_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "issuer_vkey": "3333333333333333333333333333333333333333333333333333333333333333",
        "vrf_vkey": "3333333333333333333333333333333333333333333333333333333333333333",
        "vrf_result": {
          "output": "333333333333",
          "proof": "333333333333"
        },
        "block_body_size": 858993459,
        "block_body_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "operational_cert": {
          "hot_vkey": "3333333333333333333333333333333333333333333333333333333333333333",
          "kes_period": 858993459,
          "sequence_number": 858993459,
          "sigma": "33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333"
        },
        "protocol_version": {
          "major": 858993459,
          "minor": 858993459
        }
      }
    },
    "invalid_transactions": [
      858993459
    ],
    "transaction_bodies": [
      {
        "auxiliary_data_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "inputs": [
          {
            "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
            "index": 858993459
          }
        ],
        "outputs": [
          {
            "address": "stake177stake177",
            "amount": {
              "coin": "0000000000"
            },
            "script_ref": {
              "tag": "plutus_script",
              "value": {
                "language": "plutus_v1/plutus_v1",
                "bytes": "333333333333"
              }
            }
          }
        ],
        "fee": "0000000000",
        "mint": [
          {
            "script_hash": "33333333333333333333333333333333333333333333333333333333",
            "assets": [
              {
                "asset_name": "333333333333",
                "amount": "222222222222"
              }
            ]
          }
        ],
        "total_collateral": "0000000000",
        "voting_procedures": [
          {
            "key": {
              "tag": "cc_credential",
              "credential": {
                "tag": "pubkey_hash",
                "value": "33333333333333333333333333333333333333333333333333333333"
              }
            },
            "value": [
              {
                "key": {
                  "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
                  "gov_action_index": "0000000000"
                },
                "value": {
                  "vote": "yes/yes/yes/yes"
                }
              }
            ]
          }
        ]
      }
    ],
    "transaction_witness_sets": [
      {
        "Utc": -60000000,
        "redeemers": [
          {
            "data": {
              "Utc": -60000000,
              "alternative": "0000000000"
            },
            "tag": "mint/mint/mint/mint",
            "index": "0000000000",
            "ex_units": {
              "mem": "0000000000",
              "steps": "0000000000"
            }
          }
        ]
      }
    ]
  }
}
```
</details>

#### Transaction

##### Hash

Get the transaction with the supplied transaction hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_transaction_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"3333333333333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "auxiliary_data": {},
  "body": {
    "auxiliary_data_hash": "3333333333333333333333333333333333333333333333333333333333333333",
    "inputs": [
      {
        "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
        "index": 858993459
      }
    ],
    "outputs": [
      {
        "address": "stake177stake177",
        "amount": {
          "coin": "0000000000"
        },
        "script_ref": {
          "tag": "plutus_script",
          "value": {
            "language": "plutus_v1/plutus_v1",
            "bytes": "333333333333"
          }
        }
      }
    ],
    "fee": "0000000000",
    "mint": [
      {
        "script_hash": "33333333333333333333333333333333333333333333333333333333",
        "assets": [
          {
            "asset_name": "333333333333",
            "amount": "222222222222"
          }
        ]
      }
    ],
    "total_collateral": "0000000000",
    "voting_procedures": [
      {
        "key": {
          "tag": "cc_credential",
          "credential": {
            "tag": "pubkey_hash",
            "value": "33333333333333333333333333333333333333333333333333333333"
          }
        },
        "value": [
          {
            "key": {
              "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
              "gov_action_index": "0000000000"
            },
            "value": {
              "vote": "yes/yes/yes/yes"
            }
          }
        ]
      }
    ]
  },
  "is_valid": false,
  "witness_set": {
    "Utc": -60000000,
    "redeemers": [
      {
        "data": {
          "Utc": -60000000,
          "alternative": "0000000000"
        },
        "tag": "mint/mint/mint/mint",
        "index": "0000000000",
        "ex_units": {
          "mem": "0000000000",
          "steps": "0000000000"
        }
      }
    ]
  }
}
```
</details>

#### Transactions

##### Block Number

Get all transactions contained in the block with the supplied block number []

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_transactions_block_number)

###### Request


<details>
<summary>Show Example: </summary>

```
{
  "block_number": "0000000000"
}
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "transactions": [
    {
      "body": {
        "auxiliary_data_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "inputs": [
          {
            "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
            "index": 858993459
          }
        ],
        "outputs": [
          {
            "address": "stake177stake177",
            "amount": {
              "coin": "0000000000"
            },
            "script_ref": {
              "tag": "plutus_script",
              "value": {
                "language": "plutus_v1/plutus_v1",
                "bytes": "333333333333"
              }
            }
          }
        ],
        "fee": "0000000000",
        "mint": [
          {
            "script_hash": "33333333333333333333333333333333333333333333333333333333",
            "assets": [
              {
                "asset_name": "333333333333",
                "amount": "222222222222"
              }
            ]
          }
        ],
        "total_collateral": "0000000000",
        "voting_procedures": [
          {
            "key": {
              "tag": "cc_credential",
              "credential": {
                "tag": "pubkey_hash",
                "value": "33333333333333333333333333333333333333333333333333333333"
              }
            },
            "value": [
              {
                "key": {
                  "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
                  "gov_action_index": "0000000000"
                },
                "value": {
                  "vote": "yes/yes/yes/yes"
                }
              }
            ]
          }
        ]
      },
      "is_valid": false,
      "witness_set": {
        "Utc": -60000000,
        "redeemers": [
          {
            "data": {
              "Utc": -60000000,
              "alternative": "0000000000"
            },
            "tag": "mint/mint/mint/mint",
            "index": "0000000000",
            "ex_units": {
              "mem": "0000000000",
              "steps": "0000000000"
            }
          }
        ]
      }
    }
  ]
}
```
</details>

##### Block Hash

Get all transactions contained in the block with the supplied block hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_transactions_block_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"3333333333333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "transactions": [
    {
      "body": {
        "auxiliary_data_hash": "3333333333333333333333333333333333333333333333333333333333333333",
        "inputs": [
          {
            "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
            "index": 858993459
          }
        ],
        "outputs": [
          {
            "address": "stake177stake177",
            "amount": {
              "coin": "0000000000"
            },
            "script_ref": {
              "tag": "plutus_script",
              "value": {
                "language": "plutus_v1/plutus_v1",
                "bytes": "333333333333"
              }
            }
          }
        ],
        "fee": "0000000000",
        "mint": [
          {
            "script_hash": "33333333333333333333333333333333333333333333333333333333",
            "assets": [
              {
                "asset_name": "333333333333",
                "amount": "222222222222"
              }
            ]
          }
        ],
        "total_collateral": "0000000000",
        "voting_procedures": [
          {
            "key": {
              "tag": "cc_credential",
              "credential": {
                "tag": "pubkey_hash",
                "value": "33333333333333333333333333333333333333333333333333333333"
              }
            },
            "value": [
              {
                "key": {
                  "transaction_id": "3333333333333333333333333333333333333333333333333333333333333333",
                  "gov_action_index": "0000000000"
                },
                "value": {
                  "vote": "yes/yes/yes/yes"
                }
              }
            ]
          }
        ]
      },
      "is_valid": false,
      "witness_set": {
        "Utc": -60000000,
        "redeemers": [
          {
            "data": {
              "Utc": -60000000,
              "alternative": "0000000000"
            },
            "tag": "mint/mint/mint/mint",
            "index": "0000000000",
            "ex_units": {
              "mem": "0000000000",
              "steps": "0000000000"
            }
          }
        ]
      }
    }
  ]
}
```
</details>

#### Datum

##### Hash

Get the datum that hashes to the supplied data hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_datum_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"3333333333333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "datum": {
    "Utc": -60000000,
    "alternative": "0000000000"
  }
}
```
</details>

#### Plutus Script

##### Hash

Get the plutus script that hashes to the supplied script hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_plutus_script_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"33333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "plutus_script": {
    "language": "plutus_v1/plutus_v1",
    "bytes": "333333333333"
  }
}
```
</details>

#### Native Script

##### Hash

Get the native script that hashes to the supplied script hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_native_script_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"33333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "native_script": {
    "tag": "all/all/all/all",
    "scripts": [
      {
        "tag": "all/all/all/all",
        "scripts": [
          {
            "tag": "all/all/all/all",
            "scripts": [
              {
                "tag": "all/all/all/all",
                "scripts": []
              }
            ]
          }
        ]
      }
    ]
  }
}
```
</details>

#### Metadata

##### Transaction Hash

Get the metadata present on the transaction with the supplied transaction hash

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_metadata_transaction_hash)

###### Request


<details>
<summary>Show Example: </summary>

```
"3333333333333333333333333333333333333333333333333333333333333333"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "tag": "map",
  "contents": [
    {
      "key": {
        "tag": "list",
        "contents": [
          {
            "tag": "list",
            "contents": [
              {
                "tag": "list",
                "contents": []
              }
            ]
          }
        ]
      },
      "value": {
        "tag": "list",
        "contents": [
          {
            "tag": "list",
            "contents": [
              {
                "tag": "list",
                "contents": []
              }
            ]
          }
        ]
      }
    }
  ]
}
```
</details>

#### Protocol Parameters

##### Latest

Get the latest protocol parameters

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_protocol_parameters_latest)

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "ada_per_utxo_byte": "0000000000",
  "collateral_percentage": 858993459,
  "cost_models": {
    "Utc": -60000000,
    "plutus_v2": [
      "0000000000",
      "0000000000"
    ]
  },
  "d": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "execution_costs": {
    "mem_price": {
      "numerator": "0000000000",
      "denominator": "0000000000"
    },
    "step_price": {
      "numerator": "0000000000",
      "denominator": "0000000000"
    }
  },
  "expansion_rate": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "key_deposit": "0000000000",
  "max_block_body_size": 858993459,
  "max_block_ex_units": {
    "mem": "0000000000",
    "steps": "0000000000"
  },
  "max_block_header_size": 858993459,
  "max_collateral_inputs": 858993459,
  "max_epoch": 858993459,
  "max_tx_ex_units": {
    "mem": "0000000000",
    "steps": "0000000000"
  },
  "max_tx_size": 858993459,
  "max_value_size": 858993459,
  "min_pool_cost": "0000000000",
  "minfee_a": "0000000000",
  "minfee_b": "0000000000",
  "n_opt": "0000000000",
  "pool_deposit": "0000000000",
  "pool_pledge_influence": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "protocol_version": {
    "major": 858993459,
    "minor": 858993459
  },
  "treasury_growth_rate": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "pool_voting_thresholds": [
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    },
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    }
  ],
  "drep_voting_thresholds": [
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    },
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    }
  ],
  "committee_min_size": "0000000000",
  "committee_max_term_length": 858993459,
  "gov_action_lifetime": 858993459,
  "gov_action_deposit": "0000000000",
  "drep_deposit": "0000000000",
  "drep_activity": 858993459,
  "min_fee_ref_script_cost_per_byte": {
    "numerator": "0000000000",
    "denominator": "222222222222"
  }
}
```
</details>

##### Epoch

Get the protocol parameters at the supplied epoch number

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_protocol_parameters_epoch)

###### Request


<details>
<summary>Show Example: </summary>

```
{
  "epoch_number": 858993459
}
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "ada_per_utxo_byte": "0000000000",
  "collateral_percentage": 858993459,
  "cost_models": {
    "Utc": -60000000,
    "plutus_v2": [
      "0000000000",
      "0000000000"
    ]
  },
  "d": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "execution_costs": {
    "mem_price": {
      "numerator": "0000000000",
      "denominator": "0000000000"
    },
    "step_price": {
      "numerator": "0000000000",
      "denominator": "0000000000"
    }
  },
  "expansion_rate": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "key_deposit": "0000000000",
  "max_block_body_size": 858993459,
  "max_block_ex_units": {
    "mem": "0000000000",
    "steps": "0000000000"
  },
  "max_block_header_size": 858993459,
  "max_collateral_inputs": 858993459,
  "max_epoch": 858993459,
  "max_tx_ex_units": {
    "mem": "0000000000",
    "steps": "0000000000"
  },
  "max_tx_size": 858993459,
  "max_value_size": 858993459,
  "min_pool_cost": "0000000000",
  "minfee_a": "0000000000",
  "minfee_b": "0000000000",
  "n_opt": "0000000000",
  "pool_deposit": "0000000000",
  "pool_pledge_influence": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "protocol_version": {
    "major": 858993459,
    "minor": 858993459
  },
  "treasury_growth_rate": {
    "numerator": "0000000000",
    "denominator": "0000000000"
  },
  "pool_voting_thresholds": [
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    },
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    }
  ],
  "drep_voting_thresholds": [
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    },
    {
      "numerator": "0000000000",
      "denominator": "0000000000"
    }
  ],
  "committee_min_size": "0000000000",
  "committee_max_term_length": 858993459,
  "gov_action_lifetime": 858993459,
  "gov_action_deposit": "0000000000",
  "drep_deposit": "0000000000",
  "drep_activity": 858993459,
  "min_fee_ref_script_cost_per_byte": {
    "numerator": "0000000000",
    "denominator": "222222222222"
  }
}
```
</details>

#### Votes

##### Cc Id

Votes cast by the supplied cc credential

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_votes_cc_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"cc_hot177cc_hot177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action177",
      "vote_tx_hash": "3333333333333333333333333333333333333333333333333333333333333333",
      "vote": "yes/yes/yes/yes"
    }
  ]
}
```
</details>

##### Spo Id

Votes cast by the supplied stake pool operator

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_votes_spo_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"pool177pool177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action177",
      "vote_tx_hash": "3333333333333333333333333333333333333333333333333333333333333333",
      "vote": "yes/yes/yes/yes"
    }
  ]
}
```
</details>

##### Drep Id

Votes cast by the supplied DRep

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_votes_drep_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"drep177drep177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action177",
      "vote_tx_hash": "3333333333333333333333333333333333333333333333333333333333333333",
      "vote": "yes/yes/yes/yes"
    }
  ]
}
```
</details>

##### Proposal Id

Votes cast on the supplied proposal

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_votes_proposal_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"gov_action177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action177",
      "vote_tx_hash": "3333333333333333333333333333333333333333333333333333333333333333",
      "vote": "yes/yes/yes/yes"
    }
  ]
}
```
</details>

#### Drep

##### All

Get all the known DReps

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_drep_all)

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "dreps": [
    {
      "drep_id": "drep177drep177",
      "amount": "222222222222",
      "active": false
    }
  ]
}
```
</details>

##### Id

Get a specific Drep by id

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_drep_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"drep177drep177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "drep_id": "drep177drep177",
  "amount": "222222222222",
  "active": false
}
```
</details>

#### Committee

##### All

Get all known committee members

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_committee_all)

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "cc_members": [
    {
      "cc_cold_key": "cc_cold177",
      "cc_hot_key": "cc_hot177cc_hot177",
      "status": "authorised"
    }
  ]
}
```
</details>

##### Id

Get a specific Committee member by id

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_committee_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"cc_hot177cc_hot177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "cc_cold_key": "cc_cold177",
  "cc_hot_key": "cc_hot177cc_hot177",
  "status": "authorised"
}
```
</details>

#### Pool

##### All

Get all known stake pools

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_pool_all)

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "pools": [
    {
      "pool_id": "pool177pool177",
      "status": "active/active",
      "active_stake": "0000000000",
      "live_stake": "0000000000"
    }
  ]
}
```
</details>

##### Id

Get a specific stake pool by id

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_pool_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"pool177pool177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "pool_id": "pool177pool177",
  "status": "active/active",
  "active_stake": "0000000000",
  "live_stake": "0000000000"
}
```
</details>

#### Proposal

##### All

Get all known proposals

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_proposal_all)

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "proposals": [
    {
      "proposal_id": "gov_action177",
      "enacted_epoch": 858993459
    }
  ]
}
```
</details>

##### Id

Get a specific proposal by id

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_proposal_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"gov_action177"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "proposal_id": "gov_action177",
  "enacted_epoch": 858993459
}
```
</details>


## Rationale: how does this CIP achieve its goals?

<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

- [ ] There is at least one protocol adapter for any of the existing query layers that implements this spec, that can be run.
- [ ] There is at least one offchain library that implements a provider interface for this CIP, effectively making it usable with the protocol adapter in production.

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->

- [ ] Build at least one protocol adapter for any of the existing query layers that implements this spec
- [ ] Build at least one offchain library integration

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms.  Uncomment the one you wish to use (delete the other one) and ensure it matches the License field in the header: -->

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
