---
CIP: 1854
Title: Multi-signatures HD Wallets
Status: Active
Category: Wallets
Authors:
  - Matthias Benkort <matthias.benkort@cardanofoundation.org>
  - Pawel Jakubas <pawel.jakubas@cardanofoundation.org>
Implementors:
  - Round Table wallet
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/69
Created: 2021-02-23
License: CC-BY-4.0
---

## Abstract

This document describes how to realize multi-parties transactions in Cardano. It is defined as an alternative to [CIP-1852] for Cardano HD wallets. This specification does not cover the transport and sharing of partially signed transactions which is / will be covered in another document.

## Motivation: Why is this CIP necessary?

### Overview 

Term     | Definition
---      | ---
HD       | Hierarchical Deterministic, refers to wallets as described in [BIP-0032].
Multisig | Shorthand for Multi-party signature scheme. 

Multisig wallets are Cardano wallets capable of providing and tracking keys involved in multi-parties transactions. Such transactions are used to move funds from addresses where (typically) more than one user must sign transactions for its funds to be spent. A simple analogue is a joint bank account where two account holders must approve withdrawals from the account. Cardano has native support for multi-signature schemes: funds at a multi-signature script address are owned by a monetary script, which specifies one or more combinations of cryptographic signatures which must be present to unlock funds at the address (see the [Formal Ledger Spec, Figure 4: Multi-signature via Native Scripts][ledger-spec.pdf]). In a similar fashion, Cardano multisig scripts can also be used to capture stake rights on a particular address, shared between different parties.

In the Shelley era, Cardano offers six (partially overlapping) primitives for constructing monetary scripts which are summarized as the following grammar:

```abnf
SCRIPT 
  = SIGNATURE KEY-HASH
  | ALL-OF 1*SCRIPT
  | ANY-OF 1*SCRIPT
  | N-OF UINT 1*SCRIPT
  | AFTER SLOT-NO
  | BEFORE SLOT-NO

KEY-HASH = 28OCTET

SLOT-NO = UINT
```

Scripts are thereby recursive structures which can contain scripts themselves. For example, a joint account between two parties which specifies that any of the two members can spend from it would be defined in pseudo-code as:

```abnf
JOINT-ACCOUNT := ANY-OF [SIGNATURE key-hash#1, SIGNATURE key-hash#2]
```

In order to spend from such script, one would have to provide a witness showing ownership of the key associated with either of `key-hash#1` or `key-hash#2` (or possibly, both).

### Creation of a Multisig Script/Address

The creation of a multisig address will not be covered in this document. Such addresses are described in [Shelley design specification - section 3.2 - Addresses and Credentials][delegation_design.pdf] and are obtained by serializing and hashing a multisig script. This functionality is assumed to be available through existing tooling or piece of software in a variety of ways.

### Spending From a Multisig Address

In order to spend from a multisig address, one must provide a special witness in the spending transaction called a "multisig witness". Such witness must be the exact script used as an input for creating the hash part of the multisig address. Then, any additional required verification key signatures specified by the script must be provided as separate verification key witnesses (i.e. signatures of the hashed transaction body for each signing key).

This means that a wallet software has access to the full script to validate and also identify verification key hashes present in transactions, but only does so when funds are being spent from a multisig address! From the Allegra era and beyond, it is also possible to include script pre-image in transaction auxiliary data. Softwares may use this to communicate scripts ahead of time. 
 
## Specification

### HD Derivation

We consider the following HD derivation paths similarly to [CIP-1852]:

```
m / purpose' / coin_type' / account_ix' / role / index
```

To associate multi-signature keys to a wallet, we reserve however `purpose=1854'` to distinguish multisig wallets from standard wallets. The coin type remains `coin_type=1815'` to identify Ada as registered in [SLIP-0044]. The account index (`account_ix`) may vary across the whole hardened domain. `role=0` is used to identify payment keys, whereas `role=2` identifies stake keys. `role=1` is left unused for multisig wallets. Finally, the last `index` may vary across the whole soft domain, but according to the following rules:

- Wallet must derive multisig key indexes sequentially, starting from 0 and up to 2^31-1
- Wallet must prevent the creation of new multisig keys before past keys are seen in an on-chain script.
- Wallet should yet always provide up-to 20 consecutive unused multisig keys.

We can summarize the various paths and their respective domain in the following table:

| `purpose` | `coin_type` | `account_ix`       | `role`     | `index`         |
| ---       | ---         | ---                | ---        | ---             |
| `1854'`   | `1815'`     | `[2^31 .. 2^32-1]` | `0` or `2` | `[0 .. 2^31-1]` |

#### Examples

- `m/1854’/1815’/0’/0/0`
- `m/1854’/1815’/0’/2/14`
- `m/1854’/1815’/0’/2/42`
- `m/1854’/1815’/0’/0/1337`

### User-facing encoding

Multi-signatures payment verification and signing keys (`role=0`) with chain code should be presented bech32-encoded using `addr_shared_xvk` and `addr_shared_xsk` prefixes respectively, as specified in [CIP-5]. When represented without chain-code, `addr_shared_vk` and `addr_shared_sk` should be used instead.

Similarly we use `stake_shared_xvk`, `stake_shared_xsk`, `stake_shared_vk` and `stake_shared_sk` for multi-signatures stake verification and signing keys (`role=2`).

#### Examples

```yaml=
- base16: | 
    179be1ac9e63abb5fe4666df03007b07
    33a3b63cdd08cd3635b8d364e16aaf26
    49856f2ba513786afdbe5c7a07565c02
    9ba7a4290d20aa3c80ecc1835841ed78
  bech32:
    addr_shared_xvk1z7d7rty7vw4mtljxvm0sxqrmque68d3um5yv6d34hrfkfct24unynpt09wj3x7r2lkl9c7s82ewq9xa85s5s6g928jqwesvrtpq767qs66fnu
```

### Multisig Wallets

#### Templates

To define a multisig wallet, participants must provide: 

- A payment script template.
- A delegation script template (possibly null).
- All the cosigners role=0 and role=2 (4th level) public keys involved in templates. Alternatively, cosigners may also share their account public key (3rd level) directly. 

A script template is a script where key hashes are replaced by a cosigner tag which captures the relation between the cosigners. 

> **NOTE 1**: How an application represents tags is an implementation detail. Only the instantiated script appears on the blockchain. 
>
> **NOTE 2**: As a reminder, a Cardano address is made of two parts: a payment part and a delegation part. The latter is optional and so is the delegation script template. If none is provided then the address does not contain any delegation part. Wallet softwares should decide whether they want to allow or forbid this but this proposal does not take position. 

There must be a strict one-to-one mapping between the tags used in the template and the cosigner account keys provided. When a new address is needed, the software must instantiate the script by using keys derived from the relevant account. To instantiate a script from a template, a wallet software must abide by the following rules:

1. When deriving new keys, the same indexes must be used for all account involved in the template.
2. If a tag appears in multiple place in the script, then the same index must also be used for all instances of that tag.

(1) and (2) implies that a given instance of a script is associated to one and only one derivation index. 

> **NOTE 3**: Wallet software should not authorize users to update the script templates after an address has been used. 

For example, considering the joint-account example from above, an example of payment template can simply be:

```abnf
JOINT-ACCOUNT-TEMPLATE := ANY-OF 
    [ SIGNATURE cosigner#1
    , SIGNATURE cosigner#2
    ]
```

and an instantiation of that template for e.g. an index equals to 1 could be:

```abnf
JOINT-ACCOUNT := ANY-OF 
    [ SIGNATURE addr_shared_vkh1rcw47lrnczf8d4gt7d8vp6z95l8effslyejszez7069z6fa469v
    , SIGNATURE addr_shared_vkh1f8vd0s83hr7y2r96gct785e4d0d77ep9jn5wqfa4d6r4kqzxd65
    ]
```

Keys used in the instantiated template all come from the same derivation index for all cosigners. This allows all wallets to easily find back what indexes other cosigners used to derive a particular key (the same as they use for a particular address). 

### Sending Transactions

In case the wallet needs a change address internally, it must use the smallest unused indexes known, in ascending order. An index is considered unused if there's no transaction in the ledger with a script using its corresponding key hash. When constructing a transaction, a wallet should use UTxOs associated with script addresses only (hybrid transactions using non-shared UTxOs are forbidden). 

Once constructed, a transaction must be signed with all required private keys from the initiator. The initiator must also include all instances of scripts necessary (typically one per input) and then either broadcast the transaction to its cosigners or submits it to the network if valid. The mean by which the transaction is broadcast is out of the scope of this specification. 

Upon receiving a partially signed transaction, wallets must for each input:

1. Find the script associated with the input in the transaction witnesses
2. Verify that the script matches the wallet's template(s)
3. Identify the derivation index used to instantiate the script from its known keys
4. Derive the public keys of each other co-signers from that same derivation index and the cosigners parent keys
5. Verify that there's at least one signature from another co-signer
6. Verify all signatures provided by co-signers with their associated public keys

> **NOTE** The step (5) is crucial and implies that wallets initiating transactions have to sign them before broadcasting them as a proof of provenance. Otherwise it is possible for attackers to broadcast a "fake" transaction to all cosigners who may not pay attention to its details. 


When valid, the wallet should prompt the user for signing. The transaction can be submitted by any of the cosigners who deems it valid (it could be that only a subset of the cosigners is required to sign). Several cosigners may submit the transaction concurrently without issue, the ledger will ensure that only one transaction eventually get through.

> **NOTE:** The management of change addresses is an implementation detail of the wallet so long as all change addresses abide by the rules described earlier in this section. A wallet may choose to generate a single change address per transaction, while another may chose to generate many. 

### Foreign Script Discovery 

Wallets should warn users when discovering known keys in scripts which non-matching templates. Such addresses should not be included as part of the wallet's UTxO and should be treated as anomalies in the wallet. As a matter of facts, everything described in this document is a mere convention between wallets. There's however nothing at the protocol level that enforces that this specification is followed. It is therefore very much possible for advanced users to use their multisig keys in scripts that are different from the template. So long as indexes used are discoverable by the wallet, then such scripts are also discoverable. 

However, because such scripts / addresses would not have been created by the wallet, they are considered not being part of the it altogether and would not count towards the wallet's balance. Software should however as much as possible alert users about the existence of such anomalies. 

### Example

For example, if Alice and Bob wants to share a wallet by requiring a signature from each other on every payment, they can define the following payment script template:

```
ALL-OF (SIGNATURE alice) (SIGNATURE bob) 
```

After exchanging their corresponding public keys, both wallets should be initialized and present to Alice and Bob exactly `20` identical addresses, where each address is associated with exactly one derivation index. The first address will use one key from Alice's wallet at path `m/1854’/1815’/0’/0/0` and a key from Bob's at exactly the same path. The next address will use keys at path `m/1854’/1815’/0’/0/1` and so forth. 

When Alice initiates a transaction from this wallet, she'll construct the transaction body, sign it with her corresponding private key, include an instance of the script as witness and broadcast the transaction to Bob via Telegram. Upon reception, Bob is able to verify that the transaction was indeed signed by Alice using her private key at index #0 (Bob has indeed Alice's parent public key in its possession and is therefore able to derive a child key at index #0 to verify the signature on the transaction). Bob proceeds with the payment by signing the transaction in return and submitting it. 

## Rationale: How does this CIP achieve its goals?

- Multisig keys are scoped to accounts, which allows wallet's owners to separate their activity easily.

- We use a different purpose for mainly two reasons:

  - It prevents mixing up standard wallets with shared wallets, which would be undesirable and become rapidly a nightmare for software to maintain. In particular, it also makes it possible to share an intermediary account key with co-signers without disclosing any information about non-shared keys in our wallet. 

  - It makes it easier to extend any of the 1852' or 1854' in a similar manner. The addition of a new role can be done in both scheme very consistently. 

  Using a different purpose also fits well the use-case on hardware wallets who can still rely on a single root seed to manage many types of wallets. 

- One or many keys can be created from a parent public key via soft-derivation. This allows participant to easily share their multisig keys to participate in a multisig script without having to fetch for their hardware device. The device is still required for signing.

### Related Work

Description                                  | Link
---                                          | ---
BIP-0032 - HD Wallets                        | https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
CIP-5 - Common Bech32 Prefixes               | https://github.com/cardano-foundation/CIPs/tree/master/CIP-0005
CIP-1852 - Cardano HD Wallets                | https://github.com/cardano-foundation/CIPs/tree/master/CIP-1852
A Formal Specification of the Cardano Ledger | https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf

## Path to Active

### Acceptance Criteria

- [x] Document at least one case of a community adopted CIP-1852 compliant multisig wallet:
  - [x] [Round Table wallet](https://round-table.vercel.app)

### Implementation Plan

- [x] Community developed reference implementation: [github:ADAOcommunity/round-table](https://github.com/ADAOcommunity/round-table)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[rfc8610]: https://tools.ietf.org/html/rfc8610
[rfc8152]: https://tools.ietf.org/html/rfc8152
[BIP-0032]: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
[CIP-5]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0005
[CIP-1852]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852
[CIP-11]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0011
[ledger-spec.pdf]: https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf
[SLIP-0044]: https://github.com/satoshilabs/slips/blob/master/slip-0044.md
