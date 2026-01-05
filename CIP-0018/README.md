---
CIP: 18
Title: Multi-Stake-Keys Wallets 
Status: Proposed
Category: Wallets
Authors:
  - Matthias Benkort <matthias.benkort@iohk.io>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/83
Created: 2020-03-18
License: CC-BY-4.0
---

## Abstract

This document describes how to evolve sequential wallets from Cardano to support multiple stake keys. This proposal is an extension of [CIP-1852] and [CIP-0011].

## Motivation: why is this CIP necessary?

Cardano wallets originally approached stake delegation by considering a single stake key per wallet. While this was beneficial in terms of ease of implementation and simplicity of reasoning, this is unsuitable for many users with large stakes. Indeed, the inability to split out the stake into multiple pools often leads to over-saturation of existing pools in case of delegation. The only workaround so far requires users to split their funds into multiple accounts and manage them independently. This can be quite cumbersome for a sufficiently large number of accounts. 

Even for smaller actors, it can be interesting to delegate to multiple pools to limit risks. Pools may underperform or simply change their parameters from a day to another (for which wallets still do not warn users about). Delegating to more pools can reduce the impact of pool failure (for one or more epochs) or unattended changes in pool fees. It may as well be a matter of choice if users do want to delegate to several independent entities for various other reasons.

Another concern regards privacy leaks coming with the existing wallet scheme. Since the same stake key is associated with every single address of the wallet, it creates a kind of watermark that allows for tracing all funds belonging to the same wallet very easily (it suffices to look at the stake part of addresses). By allowing the wallet to hold multiple stake keys, rotating through them when creating changes does make the traceability a bit harder. One could imagine using a hundred stake keys delegated to the same pool.

## Specification

### Overview

The restriction from [CIP-0011] regarding the derivation index reserved for stake key is rendered obsolete by this specification. That is, one is allowed to derive indexes beyond the first one (index = 0) to effectively administrate multi-stake keys accounts. The creation of new stake keys is however tightly coupled to the registration of associated stake keys to allow wallet software to automatically discover stake keys on-chain. In this design, stake key indexes form **at all time a contiguous sequence with no gap**.

### Key registration

We introduce the concept of _UTxO stake key pointer_ to reliably keep track of stake keys on the blockchain. The gist is to require that every key registration and/or deregistration consume and create a special UTxO which in itself is pointing to the next available stake key of the wallet. Such pointer allows piggybacking on the existing UTxO structure to cope with concurrency issues and rollbacks that are inherent to a distributed system such as Cardano. Plus, this mechanism only demands a low overhead for wallet software and may be recognized as a special spending pattern by hardware devices. 

In more details, we require that beyond the first stake key (index = 0), all registrations must satisfy the following rules:

1. Stake keys must be derived sequentially, from 0 and onwards.
1. Every stake key registration must be accompanied by a matching delegation certificate. 
1. Every registration transaction must create a special output of exactly `minUTxOValue` Ada such that its address is an enterprise address with a single **payment part** using the stake key hash of the next available stake key of the wallet to be registered after processing the registration transaction. 
1. Unless no key beyond the first one is registered, every registration transaction must consume the special UTxO stake key pointer corresponding to the previous key registration (resp. de-registration) for that wallet.
> **Note** The `minUTxOValue` is fixed by the protocol. It is defined as part of the Shelley genesis and can be updated via on-chain protocol updates. At the moment, this equals 1 Ada on the mainnet. 

#### Example

For example, a wallet that has already registered stake keys 0, 1 and 2 have a UTxO for which the payment part is a hash of the stake key at index=3. If the wallet wants to register two new stake keys at index 3 and 4, it'll do so in a single transaction, by consuming the pointer UTxO and by creating a new one for which the payment part would be a hash of the stake key at index=5. 

Note that this only requires two signatures from stake keys at indexes 3 and 4. 

### Key de-registration

Key de-registrations work symmetrically and require that:

1. Stake keys are de-registered sequentially, from the highest and downwards. 
1. Unless the first key of the wallet is being de-registered, every de-registration transaction must create a special output of exactly `minUtxOValue` Ada such that its address is an enterprise address with a single **payment part** using the stake key hash of the next stake key of the wallet after processing the de-registration transaction.
1. Every de-registration must consume the special UTxO stake key pointer corresponding to the previous key de-registration (resp. registration) for that wallet. 

### Backwards Compatibility

As stated in the introduction, this proposal is built on top of [CIP-0011] such that backward compatibility is preserved when a single key is used. In fact, The management of the first stake key at index 0 remains unchanged and does not require any pointer. This preserves backward compatibility with the existing design for a single stake key wallet and offers a design that can be implemented on top, retro-actively. 

Nevertheless, we do assume that existing wallets following [CIP-0011] are already fully capable of discovering addresses using stake keys not belonging to the wallet. Some may even report them as _mangled_.
> **Note** An address is said _mangled_ when it has a stake part, and the stake part isn't recognized as belonging to its associated wallet. That is, the payment part and the stake part appear to come from two different sources. This could be the case if the address has been purposely constructed in such a way (because the stake rights and funds are managed by separate entities), or because the stake part refers to a key hash which is no longer known of the wallet (because the associated key registration was rolled back).

As a result, this extension would not incapacitate existing wallets since the payment ownership is left untouched. However, wallets not supporting the extension may display addresses delegated to keys beyond the first one as mangled and may also fail to report rewards correctly across multiple keys. 

We deem this to be an acceptable and fairly minor consequence but encourage existing software to raise awareness about this behaviour.


## Rationale: how does this CIP achieve its goals?

- Carrying an extra UTxO pointer makes it possible to not worry (too much) about concurrency issues and problems coming with either, multiple instances of the wallet (like many users do between a mobile and desktop wallet) or the usual rollbacks which may otherwise create gaps in the indexes. By forcing all registration (resp. deregistration) transactions to be chained together, we also enforce that any rollbacks do maintain consistency of the index state: if any intermediate transaction is rolled back, then transactions they depend on are also rolled back. 

- The first registration induces an extra cost for the end-user for the wallet needs to create a new UTxO with a minimum value. That UTxO is however passed from registration to registration afterwards without any extra cost. It can also be fully refunded upon de-registering the last stake key. So in practice, it works very much like a key deposit. 

- We do not allow mixing up key registration and key deregistration as part of the same transaction for it makes the calculation of the pointer trickier for wallet processing transactions. A single transaction either move the pointer up or down. 

- There's in principle nothing preventing someone from sending money to the special key-registration tracking address. Wallets should however only keep track of UTxOs created as part of transactions that register stake keys (and have therefore been authorized by the wallet itself). Applications are however encouraged to collect any funds sent to them in an ad-hoc manner on such keys. 

## Path to Active

### Acceptance Criteria

- [ ] There exists one or more reference implementations with appropriate testing illustrating the viability of this approach and specification.

### Implementation Plan

- [ ] Update this proposal to account for the Conway Ledger era, which brings new types of certificates for registering stake keys.

- [ ] Develop the proposed Reference Implementation as suggested when this CIP was originally published (see Discussion link in header for history).
- [ ] Contact wallet and dApp representatives in the community to develop and maintain interest in their support for this specification.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-1852]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852
[CIP-0011]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0011
