
#### Utxos

##### Asset

Get all UTxOs that contain some of the specified asset

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_utxos_asset)

###### Request


<details>
<summary>Show Example: </summary>

```
{
  "asset_name": "",
  "minting_policy_hash": "fa055f570e99cfd65e86a5e4488220f5a2cfd8f2be90d98f54d3eafa"
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
        "transaction_id": "eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686",
        "index": 4201022945
      },
      "output": {
        "address": "stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u",
        "amount": {
          "coin": "0"
        }
      }
    },
    {
      "input": {
        "transaction_id": "eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686",
        "index": 1609920239
      },
      "output": {
        "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
        "amount": {
          "coin": "0"
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
"fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91"
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
        "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
        "index": 940381344
      },
      "output": {
        "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
        "amount": {
          "coin": "0"
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
"stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u"
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
        "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
        "index": 1477617979
      },
      "output": {
        "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
        "amount": {
          "coin": "175253"
        }
      }
    },
    {
      "input": {
        "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
        "index": 4056981757
      },
      "output": {
        "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
        "amount": {
          "coin": "0"
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
  "value": "cbc69eb73a694e55425ed0c15f6674a33e8f2f7236b52cba5fd30129"
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
        "transaction_id": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
        "index": 2697252292
      },
      "output": {
        "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
        "amount": {
          "coin": "0"
        }
      }
    },
    {
      "input": {
        "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
        "index": 3633155075
      },
      "output": {
        "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
        "amount": {
          "coin": "7"
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
"stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u"
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
        "transaction_id": "fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91",
        "index": 2129548537
      },
      "output": {
        "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
        "amount": {
          "coin": "81751092945"
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
  "block_number": "0"
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
      "body_signature": "136c77da7cc6f02fc1af792625a5b75d8f2d83a71b27635ba228ff7c4bf13e8e9e0318e1aea7cced706c828404377d0991de77a75325c0651b5a45099dd72032c7647d8a1b76e96b8fd823198d199f3663caf27847384974b3f0a2eaaa2ad85e443bcc028ce4be9465858260e9dd1f437991aef8e43aaceab1c051ede06630ec4210f2150abc8a1ac01408061ac8867a5930f0051ade40a2d79eaa06aab715e9a9ea7af88b69a677c3314d91d15ee434bdd51e8c46aa97b1bf185cc60c48ef63324ffa914fbb1abd55d46c68cba8cd8077da8f88a6cdebc84f937bfa375505dcb95d243844b7fd08e0bc34bc083a2ad090c6b6cfd6beaec2064fc15d57540f80d93f378319dafda2668ea330d59d0ae7efd1b5f015a37eed6bcd21cd794675ebe52e31709f15e69b2ca3903acf1006c746a0b32ae7f5f469884c70a8b01d744c086474d3bbc8b86e19e1d0cff76509a143bb1bd16c6ca6a0d6020c746629485f222d649c99db064f8c9b66c199f12cc46a693437895242a01915b4f958f6ac4587706f62762e6e45f20394ad6cf93f04e0de89b5525099ed6e40d3b46ac25e1a4ddb714b34d0d27978ca16aa43d32f190029b17ef50856ba8288fb3059398204",
      "header_body": {
        "block_number": 795642744,
        "slot": "0",
        "issuer_vkey": "165767b4ab5815811983109a23250978bde372be3a36cd0bf4e6d936b2d23d08",
        "vrf_vkey": "f517f9db8eb29964be142f29fd85d86b320175067198b0e9f867bbba511c42ee",
        "vrf_result": {
          "output": "9f1be1c3",
          "proof": "f370"
        },
        "block_body_size": 3194471960,
        "block_body_hash": "3ee393fd2a52c0a909af1814ee5764f02ed3b85d9d3247badea629da066ad244",
        "operational_cert": {
          "hot_vkey": "8272bd2deeafc2d91b2b16796b50960457c20aa5fadedcaa9e1bce26d9d965fb",
          "kes_period": 518134050,
          "sequence_number": 1254271129,
          "sigma": "0e003769525373e7214d716fb4a02d1a0da0fdcbaa8fdd03295d577747e8854cc37dde5784f0d0d0172b67efb9e284e250bdb0b847dd70b72d6e161b0eae9409"
        },
        "protocol_version": {
          "major": 3571437749,
          "minor": 1179319841
        }
      }
    },
    "invalid_transactions": [
      1049628808
    ],
    "transaction_bodies": [
      {
        "inputs": [
          {
            "transaction_id": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
            "index": 3734755317
          }
        ],
        "outputs": [
          {
            "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
            "amount": {
              "coin": "0"
            }
          },
          {
            "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
            "amount": {
              "coin": "0"
            }
          }
        ],
        "fee": "54969"
      },
      {
        "inputs": [
          {
            "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
            "index": 3792213977
          }
        ],
        "outputs": [
          {
            "address": "stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u",
            "amount": {
              "coin": "0"
            }
          },
          {
            "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
            "amount": {
              "coin": "208074"
            }
          }
        ],
        "fee": "0"
      }
    ],
    "transaction_witness_sets": []
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
"e9096ec2733dfb25be098b8ab96ff8f598f9dc9b57b7ecf43b6f215073306755"
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
      "body_signature": "618b6723c85ac208a076aaed1403cb2e1defe348df9c0a29b2320096dcb99c8e7b1caaeacb48b6c649f7c3b5ff472368a3cc358144977e04630659c92a1f013a83b2290f7ed85e414220eea362cd8c6b257cf91db67e4c6925f1a3dfda5b436a06c5ea8fc7f31d1d350c15b058cd8ece85ca5ce04d093b0072908905f4549fdaaeebb5b70fbb933ef4c58c8dcc1fbfe410b8e0dc590a146f040a392962f99c5c0022f7b3185ac21cd663abe019c7e356340348853e65c96064f014c2a02243431abf30516068a4ac8fde6d13c5e7f24d39f2bf2ad384590cd655f2487448db4b000039aa046b90d61e0bb05c1a92a8982d87774b92d21dde8d4df2349e853561fef6e8d82e5894836bc6912d13df16823ffc36aa2bab392e7dabc37931f879c750cb1fae261821c26f3350dd687efce8411aeedbdd9e94777c27ffe9579778cf444f82597995c7a96cd7913166d1e1786eb976958328969af10c814e0a0eb5fbddef29482057dfa9366599acdc4977f3938e62cfed90cadf5ca0813f84c2580a6a2be36944e415d81582dc15c4858c319fcadeb1705abf753f781242cebdb83ae69e313cfd66a241bd5f0d447c77672ca878a1fbbc2f66e1e1c0edf9c7283582",
      "header_body": {
        "block_number": 3044719066,
        "slot": "63441",
        "issuer_vkey": "47d9426dba32ee6800bd6042ecb31162c26a5f9d4548d6b898be3696663cb1e9",
        "vrf_vkey": "2659846f2ec75dab36fb08b59e4b15a61cc7fbad655f4d8cd6dc5871335321e3",
        "vrf_result": {
          "output": "8f7b6d7a61b9",
          "proof": "605199ad5a52f09e63"
        },
        "block_body_size": 3287206835,
        "block_body_hash": "fea424dee30c903d27100067c73b54517467886bedfcf6b2752025a74c86b28d",
        "operational_cert": {
          "hot_vkey": "4ba98524fc74be4c9801a279602cbdd25c1b8c864da36e46110653d46cfc773b",
          "kes_period": 2895629300,
          "sequence_number": 3801291659,
          "sigma": "c0d9a3eccedbc707724c5e2e6052e8f6cb7c35c7f9bb283535d10f45f37ba188737583bec3bf3e8c97c5f016ea89bd2e907a948ec0a2394bf2411fb2494d613f"
        },
        "protocol_version": {
          "major": 2583355968,
          "minor": 1095517331
        }
      }
    },
    "invalid_transactions": [
      3906487169
    ],
    "transaction_bodies": [
      {
        "inputs": [
          {
            "transaction_id": "eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686",
            "index": 1586486251
          },
          {
            "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
            "index": 3307196019
          }
        ],
        "outputs": [
          {
            "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
            "amount": {
              "coin": "6"
            }
          }
        ],
        "fee": "356709740"
      },
      {
        "inputs": [
          {
            "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
            "index": 1277654959
          }
        ],
        "outputs": [
          {
            "address": "stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u",
            "amount": {
              "coin": "0"
            }
          },
          {
            "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
            "amount": {
              "coin": "0"
            }
          }
        ],
        "fee": "207293551"
      }
    ],
    "transaction_witness_sets": []
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
"eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "body": {
    "inputs": [
      {
        "transaction_id": "fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91",
        "index": 2711013252
      },
      {
        "transaction_id": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
        "index": 1026523974
      }
    ],
    "outputs": [
      {
        "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
        "amount": {
          "coin": "82519"
        }
      }
    ],
    "fee": "0"
  },
  "is_valid": true,
  "witness_set": {}
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
  "block_number": "0"
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
        "inputs": [
          {
            "transaction_id": "eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686",
            "index": 1290535197
          },
          {
            "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
            "index": 1270916115
          }
        ],
        "outputs": [
          {
            "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
            "amount": {
              "coin": "6"
            }
          },
          {
            "address": "stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u",
            "amount": {
              "coin": "0"
            }
          }
        ],
        "fee": "8721093"
      },
      "is_valid": false,
      "witness_set": {}
    },
    {
      "body": {
        "inputs": [
          {
            "transaction_id": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
            "index": 2137591745
          },
          {
            "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
            "index": 3073661304
          }
        ],
        "outputs": [
          {
            "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
            "amount": {
              "coin": "0"
            }
          },
          {
            "address": "addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w",
            "amount": {
              "coin": "76294560"
            }
          }
        ],
        "fee": "0"
      },
      "is_valid": true,
      "witness_set": {}
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
"3f18df12b07c2f4c2393c43d24189d9d40e005cf66060e1473948d061c6b03ee"
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
        "inputs": [
          {
            "transaction_id": "7420a723bf4ee4417ec1aa2262ff60921270681e7a9d537132cbcc82917e8006",
            "index": 2411299684
          }
        ],
        "outputs": [
          {
            "address": "37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na",
            "amount": {
              "coin": "0"
            }
          },
          {
            "address": "stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u",
            "amount": {
              "coin": "0"
            }
          }
        ],
        "fee": "0"
      },
      "is_valid": true,
      "witness_set": {}
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
"58c9a67f503ff9d29c332ccda2d4eaf77a9288d43b01d967a0b61726c81cfe80"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "datum": {
    "tag": "bytes",
    "value": "b800b0aba8"
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
"40573c6246b667ab2cf4ea16b2d5b8a71fd6c220e11fdb5f3484f043"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "plutus_script": {
    "language": "plutus_v3",
    "bytes": "7d65fb385b3d0101"
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
"02a5b9b9c750f691ed46f591b8170c3fd26f9d184ec8dd35bdba3c75"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "native_script": {
    "tag": "timelock_expiry",
    "slot": "39"
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
"fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91"
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
        "tag": "string",
        "value": "N{10-64}"
      },
      "value": {
        "tag": "int",
        "value": "-1"
      }
    },
    {
      "key": {
        "tag": "bytes",
        "value": "0d42e22b22d2289c"
      },
      "value": {
        "tag": "map",
        "contents": [
          {
            "key": {
              "tag": "bytes",
              "value": "de6376415b58717f55b9d009f55cfcd99c74214162c42cd321af83472287ded28aae95a6eb10e0bede337da89f8c6b55ef1716e5a685"
            },
            "value": {
              "tag": "string",
              "value": "q{10-64}"
            }
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
  "ada_per_utxo_byte": "0",
  "collateral_percentage": 1977868629,
  "cost_models": {},
  "d": {
    "numerator": "0",
    "denominator": "805976"
  },
  "execution_costs": {
    "mem_price": {
      "numerator": "3760847615",
      "denominator": "0"
    },
    "step_price": {
      "numerator": "0",
      "denominator": "0"
    }
  },
  "expansion_rate": {
    "numerator": "742373",
    "denominator": "6022896"
  },
  "key_deposit": "9048062",
  "max_block_body_size": 1554557657,
  "max_block_ex_units": {
    "mem": "5357594652",
    "steps": "378123732"
  },
  "max_block_header_size": 2541100256,
  "max_collateral_inputs": 1479508029,
  "max_epoch": 615951496,
  "max_tx_ex_units": {
    "mem": "2",
    "steps": "3142149"
  },
  "max_tx_size": 635858960,
  "max_value_size": 1711671777,
  "min_pool_cost": "0",
  "minfee_a": "67527890493",
  "minfee_b": "0",
  "n_opt": "0",
  "pool_deposit": "71472732409",
  "pool_pledge_influence": {
    "numerator": "7133030",
    "denominator": "0"
  },
  "protocol_version": {
    "major": 74433822,
    "minor": 2402460520
  },
  "treasury_growth_rate": {
    "numerator": "0",
    "denominator": "45"
  },
  "pool_voting_thresholds": [
    {
      "numerator": "0",
      "denominator": "562830"
    },
    {
      "numerator": "108",
      "denominator": "0"
    }
  ],
  "drep_voting_thresholds": [
    {
      "numerator": "0",
      "denominator": "0"
    },
    {
      "numerator": "0",
      "denominator": "33570"
    }
  ],
  "committee_min_size": "56901",
  "committee_max_term_length": 2564267198,
  "gov_action_lifetime": 3079468872,
  "gov_action_deposit": "0",
  "drep_deposit": "0",
  "drep_activity": 2514896276,
  "min_fee_ref_script_cost_per_byte": {
    "numerator": "8113262729",
    "denominator": "81689650"
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
  "epoch_number": 3533825275
}
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "ada_per_utxo_byte": "9789470",
  "collateral_percentage": 1606006169,
  "cost_models": {},
  "d": {
    "numerator": "918",
    "denominator": "5933250"
  },
  "execution_costs": {
    "mem_price": {
      "numerator": "0",
      "denominator": "0"
    },
    "step_price": {
      "numerator": "848900193",
      "denominator": "0"
    }
  },
  "expansion_rate": {
    "numerator": "880",
    "denominator": "0"
  },
  "key_deposit": "67",
  "max_block_body_size": 2763174108,
  "max_block_ex_units": {
    "mem": "0",
    "steps": "4607565"
  },
  "max_block_header_size": 1271393601,
  "max_collateral_inputs": 652898174,
  "max_epoch": 3872817619,
  "max_tx_ex_units": {
    "mem": "0",
    "steps": "30"
  },
  "max_tx_size": 607826262,
  "max_value_size": 1460004229,
  "min_pool_cost": "706681812",
  "minfee_a": "25",
  "minfee_b": "6733225",
  "n_opt": "41875",
  "pool_deposit": "0",
  "pool_pledge_influence": {
    "numerator": "0",
    "denominator": "78388171"
  },
  "protocol_version": {
    "major": 426143910,
    "minor": 1794405185
  },
  "treasury_growth_rate": {
    "numerator": "0",
    "denominator": "871793417"
  },
  "pool_voting_thresholds": [
    {
      "numerator": "0",
      "denominator": "2"
    },
    {
      "numerator": "8129",
      "denominator": "353734147"
    }
  ],
  "drep_voting_thresholds": [
    {
      "numerator": "45850967477",
      "denominator": "0"
    },
    {
      "numerator": "0",
      "denominator": "0"
    }
  ],
  "committee_min_size": "0",
  "committee_max_term_length": 223674158,
  "gov_action_lifetime": 3722567539,
  "gov_action_deposit": "42149850",
  "drep_deposit": "0",
  "drep_activity": 3795950329,
  "min_fee_ref_script_cost_per_byte": {
    "numerator": "68173841",
    "denominator": "82"
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
"cc_hot1qgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvcdjk7"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
      "vote": "abstain"
    },
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686",
      "vote": "yes"
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
"pool12a39rkzfylvn9wfe8j6y8ucq6g2l4mw4azj70y0gd8ejczznyj2"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
      "vote": "no"
    },
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91",
      "vote": "yes"
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
"drep1ygqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq7vlc9n"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "c6726192662abeab149098095eabe004ecbec47f5e564748ab0d394affca47d9",
      "vote": "yes"
    },
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91",
      "vote": "abstain"
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
"gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "votes": [
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "eca40340fa6e65d964915ba4bc8bd811a0493d263ffe95875291114cbb2d0686",
      "vote": "no"
    },
    {
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf",
      "vote_tx_hash": "fbc1da46d62a431e69855ad48a6b49b0e2aaafc6fd3dc4a066c6851b7bd31a91",
      "vote": "yes"
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
      "drep_id": "drep1ygqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq7vlc9n",
      "amount": "30090",
      "active": false
    }
  ]
}
```
</details>

##### Id

Get a specific DRep by id

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_drep_id)

###### Request


<details>
<summary>Show Example: </summary>

```
"drep1ygqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq7vlc9n"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "drep_id": "drep1ygqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq7vlc9n",
  "amount": "5",
  "active": true
}
```
</details>

##### Stake Credential

Get the DRep that the stake credential has delegated to

[Link to OpenApi endpoint](https://mlabs-haskell.github.io/query-layer-impl/index.html#/default/get_drep_stake_credential)

###### Request


<details>
<summary>Show Example: </summary>

```
"stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "drep_id": "drep1ygqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq7vlc9n",
  "amount": "82127699945",
  "active": true
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
      "cc_cold_key": "cc_cold1zvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6kflvs",
      "cc_hot_key": "cc_hot1qgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvcdjk7",
      "status": "resigned"
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
"cc_hot1qgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvcdjk7"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "cc_cold_key": "cc_cold1zvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6kflvs",
  "cc_hot_key": "cc_hot1qgqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvcdjk7",
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
      "pool_id": "pool12a39rkzfylvn9wfe8j6y8ucq6g2l4mw4azj70y0gd8ejczznyj2",
      "status": "retired",
      "active_stake": "0",
      "live_stake": "0"
    },
    {
      "pool_id": "pool12a39rkzfylvn9wfe8j6y8ucq6g2l4mw4azj70y0gd8ejczznyj2",
      "status": "active",
      "active_stake": "745258045",
      "live_stake": "671000150"
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
"pool12a39rkzfylvn9wfe8j6y8ucq6g2l4mw4azj70y0gd8ejczznyj2"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "pool_id": "pool12a39rkzfylvn9wfe8j6y8ucq6g2l4mw4azj70y0gd8ejczznyj2",
  "status": "active",
  "active_stake": "0",
  "live_stake": "44"
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
      "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf"
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
"gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf"
```
</details>

###### Response


<details>
<summary>Show Example: </summary>

```
{
  "proposal_id": "gov_action1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpzklpgpf"
}
```
</details>
