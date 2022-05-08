---
CIP: ?
Title: Standard for light wallet backend connection
Authors: Miguel Angel Cabrera Minagorri <devgorri@gmail.com>
Comments-URI: 
Status: Draft
Type: Standards Track 
Created: 2022-05-08
License: CC-BY-4.0
---

# **Summary**

Wallets and backend services should consume/expose standard endpoints in order to make wallets work across Cardano networks.

# **Abstract**

Currently each light wallet uses a different backend and most of them do not offer a way to configure the backend host. Each backend exposing a different API makes it really difficult to be able to configure the backend host into the wallet settings.
Being able to configure the backend host is really important to connect a wallet to a different Cardano network, so anyone can deploy a backend for the new network and connect the wallet to it.

# **Motivation**

As the Cardano ecosystem grows, more Cardano networks start to appear. Leading a project called Shareslake, I deployed a Cardano mainnet, finding that allowing people to connect existing wallets to this new network is really complex.

To illustrate the problem let’s use Nami wallet as example. It allows to configure the transaction submit endpoint, nevertheless, it uses Blockfrost to read on-chain data such us the funds on the wallet address. So, even though you can change the submit endpoint, the wallet won’t show the address funds or transactions to the user.

This CIP is created to suggest a standard on how wallets obtain the on-chain information from the backend, allowing people to easily edit the light wallet connection settings to connect it to a different Cardano network.
What we are looking to achieve with this CIP is already possible into the Ethereum ecosystem. Let's think on a wallet called Metamask that you can easily connect to different Ethereum networks.

# **Rationale**

Focusing this CIP on the communication between backends indexing the ledger and the light wallets we should be able to suggest a bunch of standard endpoints that allows light wallet's users to just change the backend host and the creators of a new network to deploy a backend knowing that it will work with most of the light wallets.

Cardano mainnet addresses do not include the network magic allowing to use the same address and keys between Cardano networks, so just changing of the backend host on the wallet settings is enough. Testnet addresses are different, they include the network magic, requiring to create a new address per network.

There are two different points to standardise here:

1. Endpoints used to read the on-chain data from the backend.
2. Endpoints used to submit transactions to the network.

The proposal must be agnostic to the wallet and backend implementations or programming languages so we will be defining REST endpoints that will be exposed by the backends and consumed by the wallets.

To define those endpoints using [OpenAPI](https://swagger.io/specification/) seems ideal as it is widely used to specify RESTful APIs and there are several tools for automatically generating APIs code.

About the first point, we could follow `cardano-db-sync` REST endpoints as standard for consuming on-chain data, but they were deprecated.

The endpoints proposed into the specification are based on the required by Nami wallet, which is an open source widely used Cardano light wallet that at the date of writting this CIP is using Blockfrost as backend.

About submitting transactions to the network, `cardano-submit-api` already offers a solution, so we suggest to use it instead of re-invent the wheel.

# **Specification**

> This is an incompleted specification to provide an example until we reach consensus on how it should be.

```
openapi: 3.0.0
info:
  description: Schema for Cardano light wallets on-chain data
  version: 1.0.0
  contact:
    email: devgorri@gmail.com
  license:
    name: Apache 2.0
    url: http://www.apache.org/licenses/LICENSE-2.0.html
basePath: /v0
tags:
  - name: accounts
    description: Information about stake accounts


schemes:
  - https
  - http
paths:
  /accounts/{address}:
    get:
      parameters:
        - in: path
          name: address
          schema:
            type: string
          required: true
          description: Stake address
      responses:
        '400':
          description: Invalid address supplied
        '404':
          description: Address not found
        '200':
          description: Success
          schema:
            $ref: '#/definitions/Account'
  /pool/{pool_id}/metadata:
    get:
      parameters:
        - in: path
          name: pool_id
          schema:
            type: string
          required: true
          description: Pool metadata
      responses:
        '400':
          description: Invalid pool ID supplied
        '404':
          description: Pool not found
        '200':
          description: Success
          schema:
            $ref: '#/definitions/Pool'
  /pools:
    get:
      responses:
        '200':
          description: Success
          schema:
            type: array
            items:
              $ref: '#/definitions/Pool'
  /addresses/{address}:
    get:
      parameters:
        - in: path
          name: address
          schema:
            type: string
          required: true
          description: Address information
      responses:
        '400':
          description: Invalid addr supplied
        '404':
          description: Address not found
        '200':
          description: Success
          schema:
            $ref: '#/definitions/Address'
      
          
definitions:
  Account:
    type: object
    properties:
      active:
        type: booelan
        default: false
      rewards:
        type: integer
        format: int64
      pool_id:
        type: string
      withdrawable:
        type: integer
        format: int64
      withdrawn:
        type: integer
        format: int64
    xml:
      name: Account
  Pool:
    type: object
    properties:
      homepage:
        type: string
      tocker:
        type: string
      description:
        type: string
      name:
        type: string
    xml:
      name: Account
  Address:
    type: object
    properties:
      amount: 
        type: array
        items:
          $ref: '#/definitions/Amount'
      stake_address:
        type: string
      type:
        type: string
      script:
        type: boolean
  Amount:
    type: object
    properties:
      unit:
        type: string
      quantity:
        type: integer
        format: int64
      decimals:
        type: integer
        format: int32
```

# **Copyright**

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
