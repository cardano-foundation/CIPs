---
CIP: 21
Title: Transaction requirements for interoperability with hardware wallets
Status: Active
Category: Wallets
Authors:
  - Gabriel Kerekes <gabriel.kerekes@vacuumlabs.com>
  - Rafael Korbas <rafael.korbas@vacuumlabs.com>
  - Jan Mazak <jan.mazak@vacuumlabs.com>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/107
Created: 2021-06-15
License: CC-BY-4.0
---

## Abstract

This CIP describes all the restrictions applicable to Cardano transactions which need to be signed by hardware wallets.

## Motivation: Why is this CIP necessary?

Due to certain limitations of hardware (abbrev. HW) wallets, especially very small memory and a limited set of data types supported by Ledger, HW wallets are not able to process all valid transactions which are supported by Cardano nodes.

The limitations also result in an inability of HW wallets to see the whole transaction at once. Transaction data are streamed into HW wallets in small chunks and they compute a rolling hash of the transaction body which is signed at the end. Consequently, a HW wallet only provides witness signatures, and the transaction body which was signed has to be reconstructed by the client. We thus need a common transaction serialization format which will allow no ambiguity. In addition, the format must define ordering of map keys in such a way that it’s possible to check for duplicate keys by HW wallets.

Several of the restrictions also stem from security or UX concerns, e.g. the forbidden combination of pool registration certificates and withdrawals in a single transaction (see reasoning below).

To ensure interoperability, SW wallets and other tools working with HW wallets should only use transactions which conform to the following rules.

## Specification

Certain transaction elements, described as allowed in this document, might not be supported by some HW wallets. Support also depends on HW wallet firmware or app versions. If transaction signing fails for a transaction which is built according to this specification, make sure to check the documentation of the HW wallet you are using.

> **Note:** It might take some time for recent Cardano ledger spec changes to be implemented for HW wallets. Thus it might happen that further restrictions might apply on top of the restrictions mentioned in this CIP until the changes are implemented on HW wallets.

### Canonical CBOR serialization format

Transactions must be serialized in line with suggestions from [Section 3.9 of CBOR specification RFC](https://datatracker.ietf.org/doc/html/rfc7049#section-3.9). In particular:

- Integers must be as small as possible.
- The expression of lengths in major types 2 through 5 must be as short as possible.
- The keys in every map must be sorted from lowest value to highest.
- Indefinite-length items must be made into definite-length items.

See the RFC for details.

### Tags in sets

Conway introduced optional 258 tags in certain items that are considered sets semantically but encoded as arrays in CBOR. HW wallets will support this optional encoding, but it must be consistent across the transaction: either there are no tags 258 in sets, or there are such tags everywhere (as described in the CDDL specification).

### Transaction body

#### Unsupported entries

The following transaction body entries must not be included:
* `6 : update`
* `20 : proposal procedures`

#### Integers

HW wallets support at most `int64` for signed integers and `uint64` for unsigned integers i.e. larger integers are not supported overall. Additionally, any integer value must fit in the appropriate type.

#### Numbers of transaction elements

The number of the following transaction elements individually must not exceed `UINT16_MAX`, i.e. 65535:

- inputs in transaction body
- outputs in transaction body
- asset groups (policy IDs) in an output or in the mint field
- tokens (asset names) in an asset group
- certificates in transaction body
- pool owners in a pool registration certificate
- pool relays in a pool registration certificate
- withdrawals in transaction body
- collateral inputs in transaction body
- required signers in transaction body
- reference inputs in transaction body
- the total number of witnesses

For voting procedures, it is only allowed to include a single voter with a single voting procedure.

#### Optional empty lists and maps

Unless mentioned otherwise in this CIP, optional empty lists and maps must not be included as part of the transaction body or its elements.

Since Conway, the [CDDL specification](https://github.com/intersectmbo/cardano-ledger/tree/master/eras/conway/impl/cddl-files) is stricter, so many arrays are now treated as non-empty sets, and some maps are required to be non-empty. HW wallets enforce this in many cases.

#### Outputs

A new, "post Alonzo", output format has been introduced in the Babbage ledger era which uses a map instead of an array to store the output data. For now, both the "legacy" (array) and "post Alonzo" (map) output formats are supported by HW wallets but we encourage everyone to migrate to the "post Alonzo" format as support for the "legacy" output format might be removed in the future. Both formats can be mixed within a single transaction, both in outputs and in the collateral return output.

##### Legacy outputs

Outputs containing no multi-asset tokens must be serialized as a simple tuple, i.e. `[address, coin, ?datum_hash]` instead of `[address, [coin, {}], ?datum_hash]`.

##### Post Alonzo outputs

If the `data` of `datum_option` is included in an output, it must not be empty. `script_ref` (reference script) must also not be empty if it is included in an output.

#### Multiassets

Since multiassets (`policy_id` and `asset_name`) are represented as maps, both need to be sorted in accordance with the specified canonical CBOR format. Also, an output or the mint field must not contain duplicate `policy_id`s and a policy must not contain duplicate `asset_name`s.

#### Certificates

Certificates of the following types are not supported and must not be included:
* `genesis_key_delegation`
* `move_instantaneous_rewards_cert`
* `stake_vote_deleg_cert`
* `stake_reg_deleg_cert`
* `vote_reg_deleg_cert`
* `stake_vote_reg_deleg_cert`

If a transaction contains a pool registration certificate, then it must not contain:

- any other certificate;
- any withdrawal;
- mint entry;
- any output containing datum, datum hash or reference script;
- script data hash;
- any collateral input;
- any required signer;
- collateral return output;
- total collateral;
- reference inputs;
- voting procedures;
- treasury value;
- donation value.

It is allowed to arbitrarily combine other supported certificate types.

#### Withdrawals

Since withdrawals are represented as a map of reward accounts, withdrawals also need to be sorted in accordance with the specified canonical CBOR format. A transaction must not contain duplicate withdrawals.

#### Auxiliary data

HW wallets do not serialize auxiliary data because of their complex structure. They only include the given auxiliary data hash in the transaction body. The only exception is Catalyst voting registration because it requires a signature computed by the HW wallet.

In this exceptional case, auxiliary data must be encoded in their "tuple" format:

```
[ transaction_metadata: { * transaction_metadatum_label => transaction_metadatum }, auxiliary_scripts: [ * native_script ]]
```

The `auxiliary_scripts` must be an array of length 0.

## Rationale: How does this CIP achieve its goals?

### Canonical CBOR serialization format

As HW wallets don't return the whole serialized transaction, a common CBOR serialization is needed so that software wallets and other tools interacting with HW wallets are be able to deterministically reproduce the transaction body built and signed by the HW wallet.

The specified canonical CBOR format is consistent with how certain other data are serialized (e.g. Plutus script data in Alonzo) and allows the use of standard CBOR libraries out of the box.

### Transaction body

#### Credentials

Generally, HW wallets require that any key hash credential (and withdrawal address too) is given by the derivation path of the key (otherwise the user will not be aware that the key belongs to his wallet). This does not apply to Plutus transactions where HW wallets instead aim for maximum flexibility at the cost of users being potentially misled. (It is very hard to foresee how Plutus script authors would use various transaction elements and any restriction applied by HW wallets might break a use case which is otherwise perfectly sound and safe.)

When signing a transaction, Ledger and Trezor use a _transaction signing mode_ that describes upfront what the intent is
(the software wallet is responsible for choosing an appropriate mode). The transaction is then validated according to the mode.
There are, in principle, four options:
* _Stake pool registration transaction_. Stake pool registration certificates are signed on their own, the transaction should contain nothing that is not necessary.
* _Ordinary transaction_. Credentials must be given as key paths.
* _Multisig transaction_. Credentials must be script hashes; only [multisig keys](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1854/README.md) are allowed.
* _Plutus transaction_. The only mode that allows elements related to running Plutus scripts (script data hash etc.). No extra restrictions on transaction elements or their combinations. The drawback is that more is shown to the user (e.g. witnesses are not hidden as in ordinary transactions). Please only use this mode if no other mode is sufficient.

This brief description does not aim to capture the full complexity of signing modes; always verify that transactions you aim to construct are supported by other tools you will rely on (hardware wallets, software wallets, command-line tools like [`cardano-hw-cli`](https://github.com/vacuumlabs/cardano-hw-cli) etc.).

#### Multiassets

Allowing duplicate `policy_id`s (or `asset_name`s) might lead to inconsistencies between what is displayed to the user and how nodes and other tools might interpret the duplicate keys, i.e. all policies (or asset names) would be shown to the user, but nodes and other tools might eventually interpret only a single one of them.

#### Certificates

Combining withdrawals and pool registration certificates isn't allowed because both are signed by staking keys by pool owners. If it was allowed to have both in a transaction then the witness provided by a pool owner might inadvertently serve as a witness for a withdrawal for the owner's account.

#### Withdrawals

Similarly to multiassets, allowing duplicate withdrawals might lead to inconsistencies between what is displayed to the user and how nodes and other tools might interpret the duplicate keys.

#### Auxiliary data

The specified auxiliary data format was chosen in order to be compatible with other Cardano tools, which mostly use this serialization format.

### Stake key signing vs other keys

A DRep witness can serve for both certificates and votes at the same time. Unlike with stake keys (where combining pool registration with e.g. withdrawals is forbidden), no restriction is imposed on the combination of certificates and votes.
We think that votes and DRep certificates are rare and substantially distinguished parts of a transaction, signed by DRep keys which are likely to only be used by users with deep enough understanding (and, unlike stake keys, are always visible when providing witnesses). A single vote or a DRep certificate is unlikely to have a major effect (esp. not on the loss of funds). If submitting unintended votes turns out to be a problem, it is likely better to solve it on the level of Cardano blockchain ledger by providing a mechanism allowing for replacing or cancelling votes.

## Path to Active

### Acceptance Criteria

- [x] Confirmation (by default if no ongoing incompatibilities) since Alonzo ledger era that this interoperability between software and hardware wallets has been generally achieved.

### Implementation Plan

- [x] Tools exist which can be used to validate or transform transactions into a HW wallet compatible format if possible:
  - [x] [`cardano-hw-interop-library`](https://github.com/vacuumlabs/cardano-hw-interop-lib)
  - [x] [`cardano-hw-cli`](https://github.com/vacuumlabs/cardano-hw-cli) (which uses the interop library)

## Restrictions for specific hardware devices

The following list of features with missing support on particular hardware devices is subject to occasional changes. Some features might be added, but some could also be removed (e.g. if they take too much space needed for other features).

#### Ledger: Nano S Plus, Nano X, Stax

Everything described here as allowed should (eventually) work on these devices.

#### Ledger: Nano S

Missing features:
- signing operational certificates
- derivation of native script hashes
- stake pool registration and retirement
- display of certain details of Byron addresses (though addresses themselves are supported)

#### Trezor

Missing features:
- derivation of stake pool cold keys
- signing operational certificates
- signing pool registration certificates as operator (only as owner is allowed)
- derivation of DRep and constitutional committee keys
- DRep certificates (registration, retirement, update)
- constitutional committee certificates
- voting procedures
- treasury and donation elements of transactions

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
