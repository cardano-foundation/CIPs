---
CIP: 95
Title: Cardano dApp-Wallet Web Bridge Governance Extension
Category: Wallets
Status: Proposed
Authors:
  - Ryan Williams <ryan.williams@iohk.io>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/509
  - https://discord.com/channels/826816523368005654/1101547251903504474/1101548279277309983
Created: 2022-02-24
License: CC-BY-4.0
---

## Abstract

This document describes an interface between webpage/web-based stacks and
Cardano wallets. This specification defines the API of the javascript object
that needs to be injected into web applications.

These definitions extend
[CIP-30 | Cardano dApp-Wallet Web Bridge](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030)
to provide support for
[CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md)
focussed web-based stacks. Here we aim to support the requirements of the Conway
Ledger era, this specification is based on the
[Draft Conway Ledger Era Specification](https://github.com/input-output-hk/cardano-ledger/tree/master/eras/conway/test-suite/cddl-files).

> **Note** This proposal assumes knowledge of the ledger governance model as
> outlined within
> [CIP-1694](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md).

<details>
  <summary><strong>Wallets and Tooling Hackathon</strong></summary>

On 2023.07.13 a online and in person community hackathon took place, aims of
this event included maturation of the design of this specification.

We would like to thank the following attendees for providing their valuable
insights:

- Piotr Czeglik - Lace
- Mircea Hasegan - Lace
- Alex Apeldoorn - Lace
- Michal Szorad - Yoroi
- Javier Bueno - Yoroi
- Vladimir Volek - Five Binaries
- Marek Mahut - Five Binaries
- Markus Gufler - Cardano Foundation
- Michal Ciborowski - BinarApps

</details>

## Motivation: why is this CIP necessary?

CIP-1694 introduces many new concepts, entities and actors to Cardano;
describing their implementation at the ledger level. Yet, for most ecosystem
participants low level details are abstracted away by tooling. This creates a
need for such tooling to be able support the utilization of ledger features.
This specification allows for creation of web-based tools for the utilization of
CIP-1694's governance features.

Whilst CIP-30 facilitated the launch of dApp client development on Cardano, it's
functionality is limited in scope. It was written well before the emergence of
the Conway Ledger Era and thus lacks the required methods to support full user
interaction. We believe that expecting existing CIP-30 implementors to upgrade
implementations is unfeasible, thus we must extend it's functionality with this
API.

This proposal enables Ada holders, and DReps to engage web-based tooling through
wallets. Thus the primary stakeholders for this proposal are tool developers and
wallet providers. Here we aim to outline all endpoints needed to be exposed to
web based tools to support all the needs Ada holders and DReps to engage with
CIP-1694's governance design.

## Specification

We define the following section as an extension to the specification described
within CIP-30.

To access these functionalities a client application must present this CIP
extension object:

```ts
{ "cip": 95 }
```

This extension object is provided during the initial handshake procedure as
described within
[CIP-30's Initial API](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cardanowalletnameenable-extensions-extension----promiseapi).

> **Note** This specification will evolve as the proposed ledger governance
> model matures.

### DRep Key

// TODO: Move this into a separate CIP.

CIP-1694 does not define a derivation path for registered DRep credentials, here
we propose the introduction of DRep Keys to act as DRep credentials for
registered DReps.

The methods described here should not be considered the only definitive method
of generating DRep credentials. Rather these methods should be employed to
derive keys for non-script registered DReps.

#### Derivation

Here we describe DRep Key derivation as it attains to Cardano wallets who follow
the
[CIP-1852 | HD (Hierarchy for Deterministic) Wallets for Cardano](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852/README.md)
standard.

To differentiate DRep credentials from other Cardano keys the derivation path
must follow:

`m / 1694' / 1815' / account' / 1718 / address_index`

> **Note** `1718` was the year that François-Marie adopted the pseudonym
> Voltaire.

We strongly suggest that a maximum of one set of DRep credentials should be
associated with one wallet account, this can be achieved by only ever setting
`address_index=0`. This avoids the need for DRep Key discovery.

We believe the overhead that would be introduced by "multi-DRep" accounts is an
unjustified expense. Future iterations of this specification may expand on this,
but at present this is seen as unnecessary.

#### Tooling

Supporting tooling should clearly label these key pairs as "CIP-95 DRep Keys".

Bech32 prefixes of `drep_sk` and `drep_vk` should be used, as described in
[CIP-0005](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0005/README.md).

Examples of acceptable `keyType`s for supporting tools:

| `keyType`                          | Description           |
| ---------------------------------- | --------------------- |
| `CIP95DRepSigningKey_ed25519`      | DRep Signing Key      |
| `CIP95DRepVerificationKey_ed25519` | DRep Verification Key |

For hardware implementations:

| `keyType`                          | Description                    |
| ---------------------------------- | ------------------------------ |
| `CIP95DRepVerificationKey_ed25519` | Hardware DRep Verification Key |
| `CIP95DRepHWSigningFile_ed25519`   | Hardware DRep Signing File     |

### Data Types

From
[CIP-30's Data Types](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#data-types)
we inherit:

- [Address](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#address).
- [Bytes](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#bytes).
- [cbor\<T>](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cbort).
- [DataSignature](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#bytes).
- [Extension](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#extension).

#### PubDRepKey

```ts
type PubDRepKey = string;
```

A hex-encoded string representing 32 byte Ed25519 DRep public key, as described
in [DRep Key](#DRep-key).

#### PubStakeKey

```ts
type PubStakeKey = string;
```

A hex-encoded string representing 32 byte Ed25519 public key used as a staking
credential.

### Error Types

This specification inherits all Error Types defined in CIP-30.

// todo: add more + avoid collisions with CIP-62?

#### Extended APIError

Here we define extensions to
[CIP-30's Error Types](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#error-types).

```ts
type enum APIErrorCode {
 // CIP-30 error codes
 InvalidArgumentError = -5
 UnknownChoiceError = -6
 UnknownKey = -7
 InvalidKey = -8
}

interface APIError {
  code: APIErrorCode,
  info: string
}
```

- `InvalidArgumentError` - Generic error for errors in the formatting of the
  arguments.
- `UnknownChoiceError` - client supplies an unknown choice in a `Vote`.
- `UnknownKey` - client supplies an unknown public key (DRep or Stake) with the
  expectation of signature.
- `InvalidKey` - client supplies a public key that does not match another
  supplied credential. This could be for DRep Keys not matching DRepID in
  Retirement Certificate or, could be when the incorrect role is supplied in a
  vote with a DRep key.

##### APIError elements

- `code`: The `APIErrorCode` which is being reported.
- `info` - A human readable description of the error.

#### Extended TxSignError

Here we add additional error codes to CIP-30's
[TxSignError](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#txsignerror).

```ts
type enum TxSignErrorCode {
  ProofGeneration = 1,
  UserDeclined = 2,
}

interface TxSignError = {
  code: TxSignErrorCode,
  info: string,
}
```

- `ProofGeneration` - Raised when there is an error during witness/proof
  generation.
- `UserDeclined` - Raised when the user declined to sign one or many items.

### Full Governance API

#### `api.getPubDRepKey(): Promise<PubDRepKey>`

Errors: `APIError`

The connected wallet account provides the account's public DRep Key, derivation
as described in [DRep Key](#DRep-key).

##### Returns

The wallet account's DRep Key.

#### `api.getActivePubStakeKeys(): Promise<PubStakeKey[]>`

Errors: `APIError`

The connected wallet account's active public stake keys (with keys which are
being used for staking), if the wallet tracks the keys that are used for
governance then only those keys shall be returned.

These are used by the client to identify the user's on-chain CIP-1694
interactions. Here we allow for multiple stake credentials to provided at once
for the case of
[multi-stake key wallets](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0018).

##### Returns

An array of the connected user's active stake keys.

#### `api.signTx(tx: cbor<transaction>, partialSign: bool = false): Promise<cbor<transaction_witness_set>>`

Errors: `APIError`, `TxSignError`

This endpoint requests the wallet to inspect and provide appropriate witnesses
for a supplied transaction. The wallet should articulate this request from
client application in a explicit and highly informative way.

Here we supersede
[CIP-30's `.signTx()`](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set)
and replace it. To allow signatures with `voting_credential` and recognition of
Conway ledger era transaction fields and certificates.

**CIP-30 is not descriptive** in what supporting implementors should be able to
recognize and sign, we believe this adds unneeded ambiguity. For this extension
we wish to remedy this by defining explicitly what wallets have to support.

##### Expected Support

As read from
[cardano-ledger Conway _draft_ specification](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl).

Supporting wallets should be able to correctly witness all certificates and data
contained in transaction body, in any combination.

| Supported Pre-Conway Certificates |
| --------------------------------- |
| `stake_registration`              |
| `stake_deregistration`            |
| `stake_delegation`                |

| Supported Conway Certificates |
| ----------------------------- |
| `reg_cert`                    |
| `unreg_cert`                  |
| `vote_deleg_cert`             |
| `stake_vote_deleg_cert`       |
| `stake_reg_deleg_cert`        |
| `vote_reg_deleg_cert`         |
| `stake_vote_reg_deleg_cert`   |
| `reg_drep_cert`               |
| `unreg_drep_cert`             |

| Conway Transaction Field Data |
| ----------------------------- |
| `voting_procedure`            |
| `proposal_procedure`          |

##### Not Supported

Without inspecting all CIP-30 implementations it is not possible to know what
certifies they support, from surveying a couple implementors, the following is
reasonable. Even if current CIP-30 implementations support the following
certificates, when the CIP-95 flag is enabled they should not.

| Unsupported Pre-Conway Certificates                      |
| -------------------------------------------------------- |
| `pool_registration`                                      |
| `pool_retirement`                                        |
| `genesis_key_delegation` (deprecated in Conway)          |
| `move_instantaneous_rewards_cert` (deprecated in Conway) |

| Unsupported Conway Certificates |
| ------------------------------- |
| `reg_committee_hot_key_cert`    |
| `unreg_committee_hot_key_cert`  |

##### Returns

The portions of the witness set that were signed as a result of this call are
returned to encourage dApps to verify the contents returned by this endpoint
while building the final transaction.

##### Errors

If `partialSign` is true, the wallet only tries to sign what it can. If
`partialSign` is false and the wallet could not sign the entire transaction,
`TxSignError` shall be returned with the `ProofGeneration` code. Likewise if the
user declined in either case it shall return the `UserDeclined` code.

#### `api.signData(addr: Address, payload: Bytes): Promise<DataSignature>`

Errors: `APIError`, `DataSignError`

This endpoint requests the wallet to inspect and provide a signature for a
supplied data. The wallet should articulate this request from client application
in a explicit and highly informative way.

Here we supersede
[CIP-30's `.signData()`](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigndataaddr-address-payload-bytes-promisedatasignaturet)
and replace it. To allow for signatures using `voting_credential`.

This endpoint utilizes the
[CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/CIP-0008.md)
for standardization/safety reasons. It allows the dApp to request the user to
sign a payload conforming to said spec.

##### Supported Credentials

Here we define how each key is identified by an `Address` in relation to
[CIP-0019 | Cardano Addresses](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/README.md),
these are all Shelley key-hash-based addresses.

To construct an address for DRep Key, the client application should construct a
[type 6 address](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L7C8-L7C93).
Using an appropriate
[Network Tag](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L13)
and a hash of the DRep Key.

// TODO: Change how to identify DRep Key?

| Key         | Identifying `addr`                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Payment Key | Address types: [0](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L1), [2](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L3), [4](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L5), [6](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L7C27-L7C72). |
| Stake Key   | Address type: [14](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L10).                                                                                                                                                                                                                                                                                                                                    |
| DRep Key    | Denoted by constructed of type [6](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/CIP-0019-cardano-addresses.abnf#L7C27-L7C72).                                                                                                                                                                                                                                                                                                            |

These key will be used to sign the `COSE_Sign1`'s `Sig_structure` with the
following headers set:

- `alg` (1) - must be set to `EdDSA` (-8)
- `kid` (4) - Optional, if present must be set to the same value as in the
  `COSE_key` specified below. It is recommended to be set to the same value as
  in the `"address"` header.
- `"address"` - must be set to the raw binary bytes of the address as per the
  binary spec, without the CBOR binary wrapper tag

The payload is not hashed and no `external_aad` is used.

##### Returns

The return shall be a `DataSignature` with `signature` set to the hex-encoded
CBOR bytes of the `COSE_Sign1` object specified above and `key` shall be the
hex-encoded CBOR bytes of a `COSE_Key` structure with the following headers set:

- `kty` (1) - must be set to `OKP` (1).
- `kid` (2) - Optional, if present must be set to the same value as in the
  `COSE_Sign1` specified above.
- `alg` (3) - must be set to `EdDSA` (-8).
- `crv` (-1) - must be set to `Ed25519` (6).
- `x` (-2) - must be set to the public key bytes of the key used to sign the
  `Sig_structure`.

##### Errors

If the payment key for `addr` is not a P2Pk address then `DataSignError` will be
returned with code `AddressNotPK`. `ProofGeneration` shall be returned if the
wallet cannot generate a signature (i.e. the wallet does not own the requested
payment private key), and `UserDeclined` will be returned if the user refuses
the request.

### Examples of Flows

#### Connection and Login

This describes a potential flow of connection between CIP-95 compatible client
application and wallet, then a subsequent _login_.

1. **Connection:** User indicates to the client their intent to connect, causing
   client offer a list of supported wallets, user selects their desired wallet.
   The client will then invoke `.{wallet-name}.enable({ "cip": 95 })` from the
   shared `cardano` namespace, ensuring to pass in the CIP-95 extension object.
2. **Wallet Confirmation:** The wallet indicates through its UI the clients
   intent to connect, the user should then grant permission.
3. **Share Credentials:** The client invokes both `.getActivePubStakeKeys()` and
   `.getPubDRepKey()`, causing the connected wallet to share relevant
   credentials.
4. **Chain Lookup:** The client uses a chain indexer to work out the governance
   state of the provided credentials. The results of the lookup are then shown
   to the user, acting as a `login`.

#### Vote Delegation

Assume a "DRep Aggregator/Explorer" specialized client app, who aggregates DRep
metadata from DRep registration certificates and renders this metadata to show
prospective delegators. Assume that connection to a users wallet has already
been made via `cardano.{wallet-name}.enable({ "cip": 95})`.

1. **Choose DRep:** User browses DReps and selects one which align's with their
   values to delegate too. It is up to the client application to choose and
   manage which stake key should be used for this delegation, this could be with
   or without user input.
2. **Construct Delegation:** The client application uses CIP-30 endpoints to
   query the wallet's UTxO set and payment address. A DRep delegation
   certificate
   ([`vote_deleg_cert`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L293C1-L293C16))
   is constructed by the app using the chosen DRep's ID and wallet's stake
   credential. A transaction is constructed to send 1 ADA to the wallet's
   payment address with the certificate included in the transaction body.
3. **Inspect and Sign:** The app passes the transaction to the wallet via
   `.signTx()`. The wallet inspects the content of the transaction, informing
   the user of the client app's intension. If the user confirms that they are
   happy to sign, the wallet returns the appropriate witnesses.
4. **Submit:** The app will add the provided witnesses into the transaction body
   and then pass the witnessed transaction back to the wallet for submission via
   `.submitTx()`.
5. **Feedback to user:** The wallet returns a `SubmittedTransaction` and the
   client uses the `txHash` field to track the status of the transaction
   on-chain, providing feedback to the user.

// TODO: give example flow of DRep reg and Voting.

<!-- #### DRep Registration

Assume that connection has already been established via
`cardano.{wallet-name}.enable({ "cip": 95})` to a DRep registration focussed
client.

1. **User Indicates Intent:** User indicates to the client that they wish to
   register as a DRep. The client asks the user to provide metadata anchor, this
   is bundled with DRepID the client derives from the wallets DRepKey provided
   via `.getPubDRepKey()`.
2. **Build Transaction**: The client application bundles the wallet's DRep ID
   and metadata anchor into a DRep registration certificate. Using CIP-30
   endpoints the client constructs a unsigned transaction and includes the DRep
   certificates, before passing this to the wallet via
   `.submitDRepRegistration()`.
3. **Inspect, sign and submit:** The wallet inspects the content of the
   transaction, showing the user associated certificate's DRepID, metadata
   anchor and deposit amount. If the user confirm that they accepts this then
   the wallet should sign and submit the transaction.
4. **Feedback to user:** The wallet returns a `SubmittedTransaction` and the
   client uses the `txHash` field to track the status of the transaction
   on-chain, providing feedback to the user. -->

## Rationale: how does this CIP achieve its goals?

// TODO: redo and add in rationale from hackathon changes

The principle aim for this design is to reduce the complexity for wallet
implementors whilst maintaining backwards compatibility with CIP-30
implementations. This is motivated by the necessity for users to be able to
interact with the age of Voltaire promptly, by keeping the wallet's providers
ask small we aim to reduce implementation time.

This design aims to make the tracking of a user's governance state an optional
endeavour for wallet providers. This is achieved by placing the responsibility
on clients to track a user's governance state, i.e. if a wallet user is a DRep,
what DRep a wallet user has delegated to, etc.

Despite only defining the minimal set of endpoints required, we do not wish to
discourage the creation of subsequent CIPs with a wider range of governance
functionality. Nor does this specification aim to discourage wallet providers
from fully integrating governance features, side-stepping the necessity for this
API and client applications (matching how staking is achieved).

### Why Web-based Stacks?

Web-based stacks, with wallet connectivity, are a familiar place for users to be
able to interact with Cardano. These tools lower the technical bar to engage
with the ecosystem. Thus we believe encouraging further adoption of this
approach is beneficial.

The primary alternative approach to this is wallet providers integrating this
functionality fully inside of wallet software, matching how staking is often
implemented. We deem this approach as preferable from a security standpoint for
combined functionality and would encourage wallet providers to pursue this. But
we understand that this adds significant overhead to wallet designs, so we offer
this API as an alternative.

<!-- ### Why DReps and Ada Holders?

This proposal only caters to two types of governance actor described in
CIP-1694; Ada holders and DReps, this decision was three fold. Primarily, this
is to allow these groups to utilize a web-based client to participate in
Cardano's governance. These groups are likely less comfortable utilizing
command-line interfaces than other groups, thus making alternatives from them is
a priority. Secondly, the other types of actor (Constitution Committee member
and SPOs) are identified by different credentials than Ada holders and DReps,
making their integration in this specification complex. These alternative
credentials are unlikely to be stored within standard wallet software which may
interface with this API. Thirdly, Ada holders and DReps likely represent the
majority of participants thus we aim to cast a wide net with this specification. -->

### The Role of the Wallet

The endpoints specified here aim to maintain the role of the wallet as: sharing
public keys, transaction inspecting, transaction signing and transaction
submission.

By not placing the burden of transaction construction onto the wallet, we move
the application specific complexity from wallet implementations and onto
applications. This has a number of benefits, primarily this should lower the bar
for wallet adoption. But this also helps in the creation of iterative updates,
all wallet implementers do not need to update if the format of these
transactions is adjusted during development.

<!-- By placing the burden of submission onto wallets we prevent malicious clients
from being able to censor which transactions are submitted to chain. This is of
particular concern due to the potential political impact of transactions being
handled by this API. We thus deem it necessary for wallets to bare this burden. -->

One argument against this design is that, if wallets are required to be able to
inspect and thus understand these application specific transactions then they
may as well build the transaction. For this reason I have placed this back into
the [Open Questions](#open-questions).

### CIP-30 Reuse

Whilst CIP-30 facilitated the launch of dApp client development on Cardano, it's
functionality is limited in scope. Although it does offer generic functions,
these cannot satisfy the problem that this proposal tackles in a backwards
compatible manner. Thus extending it's functionality is a necessity.

#### Backwards Compatibility

The primary issue with just using CIP-30 to inspect, sign and submit Conway
transactions/certificates is that wallet implementations are likely
incompatible. This is because such certificates/transactions were not part of
the ledger design at time of original CIP-30 implementation. Furthermore, CIP-30
was written and implemented before voting credentials were defined and thus it
would be impossible to provide signatures with this credential to votes, DRep
registrations and DRep retirements.

Although it is likely that some of the capabilities of this API can be achieved
by existing CIP-30 implementations it is not certain how much. We would like to
avoid the potential mismatching of capabilities between CIP-30 implementations,
as this creates unpredictable wallet behavior for client applications. Such
behavior was a primary motivator to introduce such an extendability mechanism to
CIP-30.

<!-- #### Functionality Differences

In this proposal we specify the precise information that must be shown to the
user at time of signature and submission for transactions. This is not possible
with current CIP-30 implementations, rather CIP-30's
[`.signTx()`](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set)
only requires that "must request the user's consent in an informative way".

In the case of political transactions we think it should be explicit and
unambiguous what information the user must be shown. This is to prevent
politically motivated malicious client applications from attempting to sign and
submit malicious transactions. -->

<!-- ### Explicit Singular Endpoints

// TODO: change to explain pivot

This API explicitly separates all our transaction inspect, sign and submit
endpoints. A reasonable alternative to this could be to group endpoints together
by which keys (stake or DRep) are needed to witness the
certificate/transactions. Here we chose to avoid any potential complexity on the
behalf of a wallet, to figure out what type of transaction/certificate they have
to inspect. This in particularly important for cases of transactions containing
multiple governance artifacts, for example: a vote, a governance action and DRep
registration certificate in one transaction. By separating the signing and
submission of each transaction/certificate we avoid the need for wallets to have
to deal with such edge cases.

One downside of this approach is that it limits how much can be done in a single
transaction. These methods do not allow multiple certificates to be supplied at
once. Thus users are limited to a single governance artifact per transaction.
This is limiting as it means users have to submit multiple transactions to
achieve what is possible in one. We do recognize this as a legitimate drawback
of our design. Later CIPs which replace this one may choose a more compact
design to allow such transactions, but for this we aim to keep wallet
implementations more straight forward. -->

### Extension Design

// TODO: add in explanation for replacing CIP30 endpoints

With this specification we chose to extend CIP-30's functionalities. There would
be two competing designs to this approach. One; move to have this specification
included within CIP-30. Two; deploy this specification as it's own standalone
web-bridge.

It would be undesirable to include this functionality within the base CIP-30 API
because it would force all wallets supporting CIP-30 to support this API. This
is undesirable because not all client apps or wallet will have the need or
desire to support this specification thus forcing cooperation would not
desirable.

The reason we chose to not deploy this specification on its own is because it is
unlikely that clients implementing this API will not want to also use the
functionality offered by CIP-30. Additionally, CIP-30 offers a extensibility
mechanism meaning that the initial handshake connection is defined and thus wont
be needed to be defined within this specification.

- TODO: moves multi-stake key issues to wallet by reusing signTx
- TODO: CIP95 extension tag clearly allows for dApps to know if these functions
  are allowed

<!-- ### DRep Key

We chose to introduce the concept of a DRep Key, building on top of CIP-1694,
this we see as a necessary step for wallet implementors. By setting a
(hierarchical) deterministic derivation path it enables restorability from a
seed phrase.

With this definition we aim to standard for all ecosystem tooling to be able to
derive DRep credentials from mnemonics. This brings the benefits ecosystem
standards. -->

#### Why not reuse [CIP-36 Vote Keys](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0036/README.md#voting-key)?

CIP-36 defines derivation path for a key pair to be used within CIP-36 style
governance. The most notable user of this standard is
[Project Catalyst](projectcatalyst.io), where CIP-36 vote keys are used to sign
vote transactions on the Jormungandr side-chain.

One suggestion is to reuse this key pair instead of defining a new key pair in
DRep key. The benefits to this would be that it is easier for users and tools to
manage a single key pair to be used for any projects following the CIP-36
standard and for use in this API. This would mean a single key could be used to
sign Catalyst votes and CIP-1694 DRep votes.

Reusing keys comes with the downside of possible confusion for users and
tooling. This is why we have attempted to assign the DRep keys clear and
explicit naming and usage to avoid confusion with CIP-36 vote keys. Furthermore,
the keys described here are used for more than just vote signing just the
"CIP-36 vote key" naming may be a cause of confusion.

> **Note** The derivation path used for CIP-36 vote keys includes `1694` as the
> `purpose`, this is a perhaps misleading reality and hints to the original
> intension of using CIP-36 vote keys for Cardano's Voltaire.

### Multi-stake Key Support

Although
[multi-stake key wallets](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0018)
are not widely adopted across Cardano, we make an effort to support them here.
This is because a single stake key can delegate to a single DRep. By allowing
users to spread stake across multiple stake keys it allows different weighted
delegation to different DReps, this could be a very desirable feature.

### Types of credential

This specification does not cater for wallets who manage non-key-based stake
credentials and those who wish to handle non-key-based DRep credentials. This
does limit the usefulness of this specification. But the complexities that would
be introduced by generalization this specification to these credentials is
unlikely to yield much benefit since these types of wallet are not prevalent in
Cardano.

Although this means that we are likely excluding tooling for DAOs from being
supported through this standard. The argument could be made that such entities
generally prefer to use more advanced wallet tooling rather than relying on
interaction with web-based stacks, thus it is not even certain DAOs would want
to use such a standard.

- TODO: why not support CC certs / pool certs

### Backwards Compatibility

This proposal should not effect the backwards compatibility of either clients or
wallet implementors.

#### CIP-62?

[CIP-62? | Cardano dApp-Wallet Web Bridge Catalyst Extension](https://github.com/cardano-foundation/CIPs/pull/296)
is another extension to the CIP-30 API, this proposal is independent of this.
This specification does not rely on any of the implementation defined in
CIP-62?. We have attempted to avoid any collisions of naming between these
proposals, this was done to make wallet implementations more straight forward
for wallets implementing both APIs.

### Open Questions

- <s>The burden of transaction building to be placed on dApps or wallets?</s>
  - As we are replacing CIP-30's signTx it makes sense to follow the same flow
    and place the burden on the client applications.
- <s>Move DRep key definitions into a CIP which is dedicated to describing
  CIP-1694 related credentials? or CIP-1852?</s>
  - Yes, this is a cleaner approach, as we keep the purity of this proposal to
    being a wallet web bridge.
- <s>Does supporting governance action submission a necessary burden for the
  scope of this proposal?</s>
  - Since moving burden of transaction construction from wallet to app, this
    becomes much less of an issue as the complex error checking should now be
    done by the application.
- <s>should provide support for combination certificates?</s>
  - Yes we will support ALL conway ledger era Tx/Certs, this will allow for
    CIP95 to be "the Conway compatible" wallet web bridge.
- <s>Is it necessary to provide a method to prove ownership of DRep key?</s>
  - Yes, this will be a useful add.
- <s>Is it sensible to place multi-stake key burden onto clients?</s>
  - Yes, seems like a reasonable approach. If wallets want to manage it, they
    can only provide the keys they wish.
- <s>Do we need to share stake keys or can we just reuse reward addresses?</s>
  - Reusing CIP30's `.getRewardAddresses()` may act as an alternative, but it is
    unclear how implementors have supported this function and thus its reuse
    maybe a mistake.
  - It is a more reasonable approach to share public key material instead of
    addresses as it gives the client application more freedom.
- <s>Should this proposal cater for non-key-based stake credential?</s>
  - We can leave this for a future iteration.
- Should there be a way for the optional sharing of governance state, from
  wallet to client?

## Path to Active

### Acceptance Criteria

- [ ] Resolve all [open questions](#open-questions).
- [ ] The interface is implemented and supported by various wallet providers.
- [ ] The interface is used by clients to interact with wallet providers.

### Implementation Plan

- [x] Provide a public Discord channel for open discussion of this
      specification.
  - See
    [`gov-wallet-cip`](https://discord.com/channels/826816523368005654/1101547251903504474/1101548279277309983)
    channel in the [IOG Technical Discord](https://discord.gg/inputoutput) under
    the `🥑BUILD` section (to view you have to opt-in to the Builders group).
- [x] Author to engage with wallet providers for feedback.
- [x] Author to run a hackathon workshop with wallet providers.
  - In person and online hackathon run 2023.07.13, outcomes presented here.
    TODO: add outcomes summary.
- [x] Author to provide a reference client application for wallet implementors
      to be able to test against.
  - See:
    [Ryun1/cip95-cardano-wallet-connector](https://github.com/Ryun1/cardano-wallet-connector).

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
