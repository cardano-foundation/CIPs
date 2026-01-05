---
CIP: 34
Title: Chain ID Registry
Status: Proposed
Category: Tools
Authors:
  - Sebastien Guillemot <seba@dcspark.io>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/158
  - https://github.com/cardano-foundation/CIPs/pull/332
  - https://github.com/cardano-foundation/CIPs/pull/412
Created: 2021-11-24
License: CC-BY-4.0
---

## Abstract

Currently Cardano has two easily-usable networks: "mainnet" and "testnet". However, in the future, we expect more networks to exist and so we need some way to refer to these networks to be able to write better multi-network applications and systems.

## Motivation: why is this CIP necessary?

Cardano currently has three ways to refer to a network:
- The "network ID" included in every address and also optionally present in the transaction body. This only stores 16 possibilities (4 bits)
- The "network magic" used for Byron addresses and in the handshake with other nodes in the network layer. This is a random 32-bit number
- The genesis block hash (a 28-byte number)

Blockchains can have multiple deployments of the same codebase. For example:

1. Test networks where the base asset has no value (so devs can test at no cost)
1. Test networks where the protocol is simplified for ease of testing (ex: Cardano but with a Proof of Authority consensus for stable block production in testing)
1. Test networks for new features
    1. Plutus Application Backend (PAB) testnet
    2. Shelley incentivized testnet
1. Forks that diverge in feature set (the many forks of Bitcoin and Ethereum)

dApps may be deployed on specific testnets that match their criteria and wallets need to know about these networks to know how to behave.

Additionally, having a standardized registry for networks allows easy integration into the broader crypto ecosystem via standards like [CAIP-2](https://github.com/ChainAgnostic/CAIPs/blob/master/CAIPs/caip-2.md)

## Specification

We create a machine-readable registry of networks

All entries in this registry should have the following entries:

- User-friendly name
- Network ID
- Network magic
- Genesis hash

When representing these networks in a human-readable string, the following format shall be used:

```
cip34:NetworkId-NetworkMagic
```

## Rationale: how does this CIP achieve its goals?

We pick this format for the following reason:
- The network ID is too small to be used by itself. You can see from [chainlist](https://chainlist.org/) that 16 possibilities is too few
- The genesis hash is too long and user-unfriendly to be used.

## Path to Active

### Acceptance Criteria

- [ ] There are at least two (from different providers) wallets, libraries, CLI packages, or other tools which use this standard for network identification.

### Implementation Plan

- [x] Develop and publish reference implementation: [CIP34-JS](https://www.npmjs.com/package/@dcspark/cip34-js)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
