---
CIP: 95
Title: Web-Wallet Bridge - Conway ledger era
Category: Wallets
Status: Active
Authors:
  - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors:
  - Eternl <https://eternl.io/>
  - GeroWallet <https://gerowallet.io>
  - Lace <https://www.lace.io/>
  - Mesh <https://meshjs.dev/>
  - mLabs <https://mlabs.city/>
  - NuFi <https://nu.fi/>
  - Ryan Williams <ryan.williams@intersectmbo.org>
  - Typhon <https://typhonwallet.io/>
  - Lido Nation <https://www.lidonation.com/>
  - Vespr <https://vespr.xyz/>
  - Yoroi <https://yoroi-wallet.com/>
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/509
  - https://discord.com/channels/826816523368005654/1101547251903504474/1101548279277309983
  - https://discord.com/channels/826816523368005654/1143258005354328156/1143272934966837309
Created: 2022-02-24
License: CC-BY-4.0
---

## Abstract

This document describes an interface between webpage/web-based stacks and
Cardano wallets. This specification defines the API of the javascript object
that needs to be injected into web applications.

These definitions extend
[CIP-30 | Cardano dApp-Wallet Web Bridge](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030/README.md)
to provide support for
[CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md)
focussed web-based stacks. Here we aim to support the requirements of Ada
holders and DReps in the Conway Ledger era, this specification is based on the
[Conway Ledger Era Specification](https://github.com/IntersectMBO/cardano-ledger/blob/dcacf044c8d38362edc57a761e027953aab3f335/eras/conway/impl/cddl-files/conway.cddl).

For the many contributors to this proposal, see [Acknowledgements](#acknowledgements).

## Motivation: why is this CIP necessary?

CIP-1694 introduces many new concepts, entities and actors to Cardano;
describing their implementation at the ledger level. This creates the need for
new tooling with respect to governance. For the average ecosystem participant,
the details should be abstracted away, enabling them to leverage the new ledger
features more effectively. This specification allows for creation of web-based
tools for the utilization of CIP-1694's governance features.

Whilst CIP-30 facilitated the launch of dApp development on Cardano, it's
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
within CIP-30. Although currently CIP-30 acts as the defacto Cardano dApp-wallet
connector, this specification could be applied to similar standards.

> **Note** This specification will evolve as the proposed ledger governance
> model is finalized.

### Data Types

#### CIP-30 Inherited Data Types

From
[CIP-30's Data Types](https://github.com/cardano-foundation/CIPs/tree/master/CIP-003/README.md#data-types)
we inherit:

##### [Address](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#address)

A string representing an address in either bech32 format, or hex-encoded bytes.
All return types containing `Address` must return the hex-encoded bytes format,
but must accept either format for inputs.

##### [Bytes](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#bytes)

A hex-encoded string of the corresponding bytes.

##### [cbor\<T>](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cbort)

A hex-encoded string representing [CBOR](https://tools.ietf.org/html/rfc7049)
corresponding to `T` defined via [CDDL](https://tools.ietf.org/html/rfc8610)
either inside of the
[Shelley Multi-asset binary spec](https://github.com/IntersectMBO/cardano-ledger-specs/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl)
or, if not present there, from the
[CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/CIP-0008.md).
This representation was chosen when possible as it is consistent across the
Cardano ecosystem and widely used by other tools, such as
[cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib),
which has support to encode every type in the binary spec as CBOR bytes.

##### [DataSignature](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#datasignature)

```ts
type DataSignature = {|
  signature: cbor<COSE_Sign1>,
  key: cbor<COSE_Key>,
|};
```

##### [Extension](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#extension)

An extension is an object with a single field `"cip"` that describe a CIP number
extending the API (as a plain integer, without padding). For example:

```ts
{ "cip": 30 }
```

#### CIP-95 Data Types

##### DRepID

```ts
type DRepID = string;
```

A hex-encoded string representing a Blake2b-224 hash digest of a 32 byte
Ed25519 public DRep key.

##### PubDRepKey

```ts
type PubDRepKey = string;
```

A hex-encoded string representing 32 byte Ed25519 DRep public key, as described
in [CIP-0105 | Conway Era Key Chains for HD Wallets](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md).

##### PubStakeKey

```ts
type PubStakeKey = string;
```

A hex-encoded string representing 32 byte Ed25519 public key used as a staking
credential.

### Error Types

For the methods described in
[Governance Extension API](#governance-extension-api), we inherit APIError,
DataSignError and TxSignError from
[CIP-30's Error Types](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#error-types).

> **Note** We choose to reword some descriptions from CIP-30, to improve
> clarity.

#### [APIError](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apierror)

We repurpose this error type from CIP-30, extending it's functionality. We
extend the `Refused` error code to also include the case of the extension no
longer being enabled.

```ts
APIErrorCode {
	InvalidRequest: -1,
	InternalError: -2,
	Refused: -3,
	AccountChange: -4,
}
type APIError {
	code: APIErrorCode,
	info: string
}
```

- `InvalidRequest` - Inputs do not conform to this specification or are
  otherwise invalid.
- `InternalError` - An internal wallet error occurred during execution of this
  API call.
- `Refused` - The request was refused due to lack of access - e.g. wallet
  disconnects or extension is no longer enabled.
- `AccountChange` - The account has changed. The client application should call
  `wallet.enable()` to reestablish connection to the new account. The wallet
  should not ask for confirmation as the user was the one who initiated the
  account change in the first place.

#### [TxSignError](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#txsignerror)

We repurpose this error type from CIP-30, extending it's functionality. We
extend the `ProofGeneration` error code to also include cases where DRep secret
key is not available. We also add one new error code `DeprecatedCertificate`.

```ts
TxSignErrorCode = {
  ProofGeneration: 1,
  UserDeclined: 2,
  DeprecatedCertificate: 3,
};
type TxSignError = {
  code: TxSignErrorCode;
  info: String;
};
```

- `ProofGeneration` - User has accepted the transaction sign, but the wallet was
  unable to sign the transaction. This is because the wallet does have some of
  the private keys required.
- `UserDeclined` - User declined to sign the transaction.
- `DeprecatedCertificate` - Returned regardless of user consent if the
  transaction contains a deprecated certificate.

#### [DataSignError](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#datasignerror)

We repurpose this error type from CIP-30, extending it's functionality. We
extend the `ProofGeneration` error code to also include cases where DRep secret
key is not available.

```ts
DataSignErrorCode {
	ProofGeneration: 1,
	AddressNotPK: 2,
	UserDeclined: 3,
}
type DataSignError = {
	code: DataSignErrorCode,
	info: String
}
```

- `ProofGeneration` - Wallet could not sign the data; because the wallet does
  not have the secret key to the associated with the address or DRep ID.
- `AddressNotPK` - Address was not a P2PK address and thus had no SK associated
  with it.
- `UserDeclined` - User declined to sign the data.

### Governance Extension API

These are the CIP-95 methods that should be returned as part of the API object,
namespaced by `cip95` without any leading zeros.

For example: `api.cip95.getPubDRepKey()`

To access these functionalities a client application must present this CIP-95
extension object, as part of the extensions object passed at enable time:

```ts
cardano.{wallet-name}.enable({ extensions: [{ cip : 95 }]})
```

#### `api.cip95.getPubDRepKey(): Promise<PubDRepKey>`

The connected wallet account provides the account's public DRep Key, derivation
as described in [CIP-0105](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md).

These are used by the client to identify the user's on-chain CIP-1694
interactions, i.e. if a user has registered to be a DRep.

##### Returns

The wallet account's public DRep Key.

##### Errors

<!-- prettier-ignore-start -->
| Error Type   | Error Code       | Return Condition                                                                          |
| ------------ | ---------------- | ----------------------------------------------------------------------------------------- |
| `APIError`   | `InvalidRequest` | Returned if a input parameter is passed.                                                  |
| `APIError`   | `InternalError`  | Returned if there is a generic internal error occurred during execution of this API call. |
| `APIError`   | `Refused`        | Returned if there is a refusal, could be wallet disconnection or extension is revoked.    |
| `APIError`   | `AccountChange`  | Returned if wallet has changed account, meaning connection should be reestablished.       |
<!-- prettier-ignore-stop -->

#### `api.getRegisteredPubStakeKeys(): Promise<PubStakeKey[]>`

The connected wallet account's registered public stake keys. These keys may or may not control any Ada, but they must all have been registered via a stake key registration certificate. This includes keys which the wallet knows are in the process of being registered (already included in a pending stake key registration certificate).

If none of the wallets stake keys are registered then an empty array is returned.

These keys can then be used by the client to identify the user's on-chain CIP-1694
interactions, and also create vote delegation certificates which can be signed via `.signTx()`.

##### Returns

An array of the connected user's registered public stake keys.

##### Errors

<!-- prettier-ignore-start -->
| Error Type   | Error Code       | Return Condition                                                                          |
| ------------ | ---------------- | ----------------------------------------------------------------------------------------- |
| `APIError`   | `InvalidRequest` | Returned if a input parameter is passed.                                                  |
| `APIError`   | `InternalError`  | Returned if there is a generic internal error occurred during execution of this API call. |
| `APIError`   | `Refused`        | Returned if there is a refusal, could be wallet disconnection or extension is revoked.    |
| `APIError`   | `AccountChange`  | Returned if wallet has changed account, meaning connection should be reestablished.       |
<!-- prettier-ignore-stop -->

#### `api.cip95.getUnregisteredPubStakeKeys(): Promise<PubStakeKey[]>`

The connected wallet account's unregistered public stake keys. These keys may or may not control any Ada. This includes keys which the wallet knows are in the process of becoming unregistered (already included in a pending stake key unregistration certificate).

If the wallet does not know the registration status of it's stake keys then it should return them as part of this call. If all of the wallets stake keys are registered then an empty array is returned.

These keys can then be used by the client to identify the user's on-chain CIP-1694
interactions, i.e if a user has delegated to a DRep.

##### Returns

An array of the connected user's unregistered stake keys.

##### Errors

<!-- prettier-ignore-start -->
| Error Type   | Error Code       | Return Condition                                                                          |
| ------------ | ---------------- | ----------------------------------------------------------------------------------------- |
| `APIError`   | `InvalidRequest` | Returned if a input parameter is passed.                                                  |
| `APIError`   | `InternalError`  | Returned if there is a generic internal error occurred during execution of this API call. |
| `APIError`   | `Refused`        | Returned if there is a refusal, could be wallet disconnection or extension is revoked.    |
| `APIError`   | `AccountChange`  | Returned if wallet has changed account, meaning connection should be reestablished.       |
<!-- prettier-ignore-stop -->

#### `api.signTx(tx: cbor<transaction>, partialSign: bool = false): Promise<cbor<transaction_witness_set>>`

This endpoint requests the wallet to inspect and provide appropriate witnesses
for a supplied transaction. The wallet should articulate this request from
client application in a explicit and highly informative way.

Here we extend the capabilities of
[CIP-30's `.signTx()`](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set).
To allow signatures with `drep_credential` and recognition of Conway ledger
era transaction fields and certificates.

##### Expected Inspection Support

As read from
[cardano-ledger Conway _draft_ specification](https://github.com/IntersectMBO/cardano-ledger/blob/dcacf044c8d38362edc57a761e027953aab3f335/eras/conway/impl/cddl-files/conway.cddl).

Supporting wallets should be able to recognize and inspect
all the following certificates and data contained in transaction bodies, in any
combination.

| Index | Supported Pre-Conway Certificates |
| ----- | --------------------------------- |
|   0   | `stake_registration`              |
|   1   | `stake_deregistration`            |
|   2   | `stake_delegation`                |
|   3   | `pool_registration`               |
|   4   | `pool_retirement`                 |

| Index | Supported Conway Certificates   |
| ----- | ------------------------------- |
|   5   | `reg_cert`                      |
|   6   | `unreg_cert`                    |
|   7   | `vote_deleg_cert`               |
|   8   | `stake_vote_deleg_cert`         |
|   9   | `stake_reg_deleg_cert`          |
|  10   | `vote_reg_deleg_cert`           |
|  11   | `stake_vote_reg_deleg_cert`     |
|  12   | `auth_committee_hot_cert`       |
|  13   | `resign_committee_cold_cert`    |
|  14   | `reg_drep_cert`                 |
|  15   | `unreg_drep_cert`               |
|  16   | `update_drep_cert`              |

| Transaction Index | Supported Conway Transaction Field Data |
| ----------------- | --------------------------------------- |
|        19         | `voting_procedure`                      |
|        20         | `proposal_procedure`                    |
|        21         | `coin`         (current treasury value) |
|        22         | `positive_coin`          (new donation) |

All other potential transaction field inclusions
[0-18](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L54-#L69),
should be able to be recognized by supporting wallets.

##### Unsupported Inspection

In the Conway ledger era two certificate types are deprecated `genesis_key_delegation` and `move_instantaneous_rewards_cert`.
If the wallet receives a transaction containing a deprecated certificate it should return a `TxSignError` with an error code of `DeprecatedCertificate`.

| Index | Unsupported Pre-Conway Certificates |
| ----- | ----------------------------------- |
|   5   | `genesis_key_delegation`            |
|   6   | `move_instantaneous_rewards_cert`   |

##### Expected Witness Support

Although constitutional committee certificates and stake pool certificates should be able to be recognized they should not be able to be correctly witnessed by wallets following this API.
Wallet's should only support witnesses using payment, stake and DRep keys.

##### Returns

The portions of the witness set that were signed as a result of this call are
returned. This encourages client apps to verify the contents returned by this
endpoint before building the final transaction.

##### Errors

<!-- prettier-ignore-start -->
| Error Type    | Error Code               | `partialSign`     | Return Condition                                                                                                                  |
| ------------- | ------------------------ | ----------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `APIError`    | `InvalidRequest`         | `true` or `false` | Returned if an erroneous parameter is passed, wrong type or too many etc.                                                         |
| `APIError`    | `InternalError`          | `true` or `false` | Returned if there is a generic internal error occurred during execution of this API call.                                         |
| `APIError`    | `Refused`                | `true` or `false` | Returned if there is a refusal, could be wallet disconnection or the extension is revoked.                                        |
| `APIError`    | `AccountChange`          | `true` or `false` | Returned if wallet has changed account, meaning connection should be reestablished.                                               |
| `TxSignError` | `ProofGeneration`        | `false`           | Returned if user has accepted transaction to sign, but the wallet is unable to sign because it does not have the required key(s). |
| `TxSignError` | `UserDeclined`           | `true` or `false` | Returned if user has declined to sign the transaction.                                                                            |
| `TxSignError` | `DeprecatedCertificate` | `true` or `false` | Returned regardless of user consent if the transaction contains a deprecated certificate.                                        |
<!-- prettier-ignore-stop -->

If `partialSign` is `true`, the wallet only tries to sign what it can. If
`partialSign` is `false` and the wallet could not sign the entire transaction,
`TxSignError` shall be returned with the `ProofGeneration` code.

#### `api.cip95.signData(addr: Address | DRepID, payload: Bytes): Promise<DataSignature>`

Errors: `APIError`, `DataSignError`

This endpoint requests the wallet to inspect and provide a DataSignature for the supplied data. The wallet should articulate this request from client application
in a explicit and highly informative way.

Here we extend the capabilities of
[CIP-30's `.signData()`](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigndataaddr-address-payload-bytes-promisedatasignaturet).
To allow for signatures using DRep keys. 

This endpoint utilizes the
[CIP-0008 | Message Signing](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md)
for standardization/safety reasons. It allows the client app to request the user to
sign a payload conforming to said spec.

##### Supported Credentials

We allow for `DRepID` to be passed in the `addr` field to signal signature using the associated DRep key.

The DRep hash [CIP-5](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0005/README.md#hashes) should be used in the `"address"` field of `COSE_Sign1`'s `Sig_structure` header.

### Versioning

Whilst this CIP is in it's unmerged proposed state, it remains very fluid and
substantial changes can happen, so we would advise against any implementation.
Once more feedback is received, maturing this design, implementations can safely
emerge, alongside this proposal's merger into the CIPs repository. Once merged
only small necessary changes should be made, ideally in backwards compatible
fashion.

This, in tandem with, maturing implementations should move this proposal to an
active state where only small backwards compatible changes can be made. If any
large changes are needed once active then a new proposal should be made to
replace this one. This we believe aligns with the (new) extendibility design of
CIP-0030.

### Examples of Flows

#### Connection and Login

This describes a potential flow of connection between CIP-95 compatible client
application and wallet, then a subsequent _login_.

1. **Connection:** User indicates to the client their intent to connect, causing
   client offer a list of supported wallets, user selects their desired wallet.
   The client will then invoke
   `.{wallet-name}.enable({extensions: [{ "cip": 95 }]})` from the shared
   `cardano` namespace, ensuring to pass in the CIP-95 extension object.
2. **Wallet Confirmation:** The wallet indicates through its UI the clients
   intent to connect, the user should then grant permission.
3. **Share Credentials:** The client invokes both `.getRegisteredPubStakeKeys()`
   and `.getPubDRepKey()`, causing the connected wallet to share relevant
   credentials.
4. **Chain Lookup:** The client uses a chain indexer to work out the governance
   state of the provided credentials. The results of the lookup are then shown
   to the user, acting as a `login`.

#### Vote Delegation

Assume a _DRep Aggregator and Delegation_ specialized client app, that
aggregates DRep metadata from DRep registration certificates and renders this
metadata to show prospective delegators. Assume that connection to a users
wallet has already been made via
`cardano.{wallet-name}.enable({extensions: [{ cip: 95 }]})`.

1. **Choose DRep:** User browses DReps and selects one which align's with their
   values to delegate too. It is up to the client application to choose and
   manage which stake key should be used for this delegation, this could be with
   or without user input.
2. **Construct Delegation:** The client application uses CIP-30 endpoints to
   query the wallet's UTxO set and payment address. A DRep delegation
   certificate
   ([`vote_deleg_cert`](https://github.com/IntersectMBO/cardano-ledger/blob/1beddd3d9f10d8fcb163b5e83985c4bac6b74be7/eras/conway/test-suite/cddl-files/conway.cddl#L303))
   is constructed by the app using the chosen DRep's ID and wallet's stake
   credential. A transaction is constructed to send 1 ADA to the wallet's
   payment address with the certificate included in the transaction body.
3. **Inspect and Sign:** The app passes the transaction to the wallet via
   `.signTx()`. The wallet inspects the content of the transaction, informing
   the user of the client app's intension. If the user confirms that they are
   willing to sign, the wallet returns the appropriate witnesses, of payment key
   and stake key.
4. **Submit:** The app will add the provided witnesses into the transaction body
   and then pass the witnessed transaction back to the wallet for submission via
   `.submitTx()`.
5. **Feedback to user:** The wallet returns the submitted transaction's hash,
   the app can use this to track the status of the transaction on-chain and
   provide feedback to the user.

#### DRep Registration

Assume a _DRep Registration_ specialized client app, that allows people to
register as a DRep. Assume that connection to a users wallet has already been
made via `cardano.{wallet-name}.enable({extensions: [{ cip: 95 }]})` and that
the user is not a registered DRep.

1. **User Indicates Intent:** User indicates to the client that they wish to
   register as a DRep. The client asks the user to provide metadata anchor, this
   is bundled with DRepID the client generates from the wallet's public DRep Key
   provided via `.getPubDRepKey()`.
2. **Construct Registration**: The client application uses CIP-30 endpoints to
   query the wallet's UTxO set and payment address. A DRep registration
   certificate
   ([`reg_drep_cert`](https://github.com/IntersectMBO/cardano-ledger/blob/1beddd3d9f10d8fcb163b5e83985c4bac6b74be7/eras/conway/test-suite/cddl-files/conway.cddl#L312))
   is constructed by the app using the wallet's DRep ID and the provided
   metadata anchor. A transaction is constructed to send 1 ADA to the wallet's
   payment address with the certificate included in the transaction body.
3. **Inspect and sign:** The app passes the transaction to the wallet via
   `.signTx()`. The wallet inspects the content of the transaction, informing
   the user of the client app's intension. If the user confirms that they are
   happy to sign, the wallet returns the appropriate witnesses, of payment key
   and DRep key (`drep_credential`).
4. **Submit:** The app will add the provided witnesses into the transaction body
   and then pass the witnessed transaction back to the wallet for submission via
   `.submitTx()`.
5. **Feedback to user:** The wallet returns the submitted transaction's hash,
   the app can use this to track the status of the transaction on-chain and
   provide feedback to the user.

## Rationale: how does this CIP achieve its goals?

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
API (matching how staking is achieved).

### Why Web-based Stacks?

Web-based stacks, with wallet connectivity, are a familiar place for users to be
able to interact with Cardano. These tools lower the technical bar to engage
with the ecosystem. Thus we believe encouraging further adoption of this
approach is beneficial.

The primary alternative approach is for wallet providers to integrate this
functionality fully inside of wallet software, matching how staking is often
implemented. We deem this approach as preferable from a security standpoint, we
would encourage wallet providers to pursue this. But we understand that this
adds significant overhead to wallet designs, so we offer this API as an
alternative.

### Why DReps and Ada Holders?

This proposal only caters to two types of governance actor described in
CIP-1694; Ada holders and DReps, this decision was three fold. Primarily, this
is to allow these groups to utilize a web-based client to participate in
Cardano's governance. These groups are likely less comfortable utilizing
command-line interfaces than other groups, thus making alternatives from them is
a priority. Secondly, the other types of actor (constitutional committee members
and SPOs) are identified by different credentials than Ada holders and DReps,
making their integration in this specification more complex. These alternative
credentials are unlikely to be stored within standard wallet software which may
interface with this API. Thirdly, Ada holders and DReps likely represent the
majority of participants thus we aim to cast a wide net with this specification.

#### Unsupported Items

In this specification we have placed explicit boundaries on what should not be
supported with `.signTx()`. Those being not witnessing
[stake pool](https://github.com/IntersectMBO/cardano-ledger/blob/1beddd3d9f10d8fcb163b5e83985c4bac6b74be7/eras/conway/test-suite/cddl-files/conway.cddl#L294C1-L295C43)
or
[constitutional committee](https://github.com/IntersectMBO/cardano-ledger/blob/1beddd3d9f10d8fcb163b5e83985c4bac6b74be7/eras/conway/test-suite/cddl-files/conway.cddl#L310C1-L311C61),
certificates and not inspecting genesis key delegation or MIR certificates.

From speaking to CIP-30 implementors it seems reasonable that there does not
exist implementations or motivation to support witnessing stake pool
certificates via wallet web bridges. This is because stake pool operators much
prefer the utility and security advantages not operating via light wallets. Due
to the [Lack of Specificity](#lack-of-specificity) of CIP-30 we felt it
necessary to explicitly state the lack of support in this extension.

[Constitutional committee certificates](https://github.com/IntersectMBO/cardano-ledger/blob/1beddd3d9f10d8fcb163b5e83985c4bac6b74be7/eras/conway/test-suite/cddl-files/conway.cddl#L310C1-L311C61)
are not supported by this specification's `.signTx()` for two reasons. First,
this specification is only focussed on the need's of Ada holders and DReps.
Secondly, the credentials used by the constitutional committee, are a hot and
cold key setup. Hot and cold keys are not suited for standard light wallets.

Genesis key delegation and move instantaneous reward certificates (see in
[Shelley spec](https://github.com/IntersectMBO/cardano-ledger/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl#L117#L118))
are not supported here because they have been deprecated in the Conway ledger
era. Furthermore, due to the lack of accessibility (require access to genesis
keys) for these certificates it is extremely unlikely any CIP-30 implementations
supported these.

### The Role of the Wallet

The endpoints specified here aim to maintain the role of the wallet as: sharing
public keys, transaction inspecting, transaction signing and transaction
submission.

#### Transaction Inspection

In a previous design we had stipulated the precise information that must be
shown to user by wallets at signature time. This was discussed during the
wallets and tooling hackathon and consensus was reached that is not the place of
these APIs to prescribe such details to wallets. Rather this specification
should be describing the interface between web-based stacks and wallets and not
telling wallets what UI elements should be used. It is in a wallet's best
interest to always adequately inform the user, with varying levels of detail
based on the wallet's discretion.

#### Transaction Construction

By not placing the burden of transaction construction onto the wallet, we move
the application specific complexity from wallet implementations and onto
applications. This has a number of benefits, primarily this should lower the bar
for wallet adoption. But this also helps in the creation of iterative updates,
all wallet implementers do not need to update if the format of these
transactions is adjusted during development.

Here we also benefit from imitating the existing flows which have been utilized
by CIP-30 compliant systems. Reusing existing flows is beneficial for developer
adoption as it enables straight forward code reuse.

One argument against this design is that, if wallets are required to be able to
inspect and thus understand these application specific transactions then they
may as well build the transaction. Ultimately, we have taken the design decision
to leave transaction construction to the applications.

### CIP-30 Reuse

Whilst CIP-30 facilitated the launch of dApp client development on Cardano, it's
functionality is limited in scope. Although it does offer generic functions,
these cannot satisfy the problem that this proposal tackles in a backwards
compatible manner. Thus extending it's functionality is a necessity.

#### Lack of Specificity

The CIP-30 specification has required amendments to add clarification to it's
ambiguity. There is further ambiguity around what is and is not supported via
`.signTx()`. The specification does not explicitly list the transaction
artifacts wallets has to be able to inspect and witness. Whilst for most use
cases this is likely fine and has served the community well. We forsee issues
around large ledger upgrades which introduce new types of transaction fields and
certificate. Without explicit mention of what is and is not supported deltas
between expected and actual functionality become common and hazardous. This is
why we choose to explicitly list those items that wallet have to support when
complying with this API.

#### Extension Design

With this specification we chose to extend CIP-30's functionalities. There would
be two competing designs to this approach. One; move to have this specification
included within CIP-30. Two; deploy this specification as it's own standalone
web-bridge.

It would be undesirable to include this functionality within the base CIP-30 API
because it would force all wallets supporting CIP-30 to support this API. This
is undesirable because not all client apps or wallets will have the need or
desire to support this specification.

The reason we chose to not deploy this specification on its own is because it is
unlikely that clients implementing this API will not want to also use the
functionality offered by CIP-30. Additionally, CIP-30 offers a extensibility
mechanism meaning that the initial handshake connection is defined and thus wont
be needed to be defined within this specification.

Furthermore, another benefit of utilizing the CIP-30 extensibility mechanism is
the potential for siloing of wallet capabilities between client apps. By having
to request access to each extension wallets and users are able to silo which
extensions they allow to each client application. An example of this could be
only allowing the CIP-95 API with governance related applications and not
decentralized extensions.

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

#### Namespacing

In this specification we have chosen to explicitly namespace all endpoint except
`.signTx()` where we omit the namespacing. By not namespacing `.signTx()` we
intend to offer client apps an override of the CIP-30 `.signTx()`. We chose to
do this because this `.signTx()` extends the CIP-30 functionality in a backwards
compatible way. All other endpoints are namespaced to avoid possible collisions
with other future extensions.

#### Inheriting Endpoints

In this design we chose to extend the capabilities of CIP-30's `.signTx()` and
`.signData()` rather than introducing new endpoints for signing and submission.
This was a result of community discussion at the wallets and tooling hackathon,
leading to a more straight forward design. Originally we had individual
endpoints for sign and submitting of DRep registration, DRep retirement, votes,
governance actions and vote delegations.

Whilst individual endpoints seem like a simpler solution they would likely
introduce more complexities for wallet implementors. As constraining what
transactions an endpoint would require additional validation complexities and
error handling from wallets. For example; what should a wallet do if it is
passed a DRep registration certificate via `.signTx()`? should it witness or
reject and only witness with a dedicated DRep registration endpoint?

Furthermore individual restrictive endpoints limit how much can be done in a
single transaction. These methods would not allow multiple certificates to be
supplied at once. Thus client apps would be limited to a single governance
artifact per transaction. This is limiting as it means users have to submit
multiple transactions to achieve what is possible in one.

#### CIP-95 as a Conway Flag

By providing _updated_ CIP-30 endpoints we essentially use the CIP-95 extension
object as a flag to signal to apps at connection time a wallet's compatibility
with Conway leger era. This goes against how past ledger feature upgrades have
rolled out. Rather in the past, existing CIP-30 implementors have just updated
their implementations, we believe this to be an error prone approach. This
undoubted introduces deltas between what a client application expects a wallet
to be able to do and what it can do. There is no way for a client application to
know what a wallet is capable of.

Despite this we do not discourage CIP-30 implementors from updating their
implementations to support Conway artifacts to `.signData()` and `.signTx()`.
But if so they must support the CIP-95 object flag at connection time, so that
clients are aware of this functionality.

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

#### Encoding

Unlike the CIP-30 specification we have made an decision, where possible to
represent keys as raw hex rather than encoded representations. We believe that
it is not the role of the wallet to encode such credentials, encoding needs
should be at the application's discretion. Introducing different encodings into
this API would add unneeded complexity.

Furthermore, in this API we chose to return public keys over key-hashes or
addresses. Again we believe wallets should just serve public key information and
it is up to the application to encode and derive addresses as needed. This
simplifies the overall design and makes implementations easier for wallets.

### Splitting of Stake Key endpoint

For stake keys we have chosen to implement two endpoints where wallets can share
registered and unregistered stake keys. Originally we had a single endpoint
which only allowed sharing of registered stake keys. This was problematic for
wallets which had no registered stake keys, and thus the second endpoint was
introduced.

We chose to keep a single endpoint for DRep keys, although it would have been
possible to introduce a second to allow for wallets to activity of their DRep
keys. This was just for the simplicity of the API. Furthermore, due to the
design of this proposal it is unlikely that wallets will implement methods to
track a user's DRep state.

### Backwards Compatibility

This proposal should not effect the backwards compatibility of either clients or
wallet implementors.

#### CIP-62?

[CIP-62? | Cardano dApp-Wallet Web Bridge Catalyst Extension](https://github.com/cardano-foundation/CIPs/pull/296)
is another extension to the CIP-30 API, this proposal is independent of CIP-95.
The CIP-95 specification does not rely on any of the implementation defined in
CIP-62?. We have attempted to avoid any collisions of naming between these
proposals, this was motivated by a desire to make wallet implementations more
straight forward for wallets implementing both APIs.

### Open Questions

- <s>The burden of transaction building to be placed on dApps or wallets?</s>
  - As we are replacing CIP-30's signTx it makes sense to follow the same flow
    and place the burden on the client applications.
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
- <s>Move DRep key definitions be moved into another CIP?</s>
  - Yes, this is a cleaner approach, as we keep the purity of this proposal to
    being a wallet web bridge.
- <s>Should there be a way for the optional sharing of governance state, from
  wallet to client?</s>
  - We leave this for future CIPs.
- <s>Should DRep key be moved into CIP-1852?</s>
  - Yes it will be moved to it's own CIP with reference added to
    CIP-1852.

## Path to Active

### Acceptance Criteria

- [x] The interface is supported by three wallet providers.
  - [Nufi](https://assets.nu.fi/extension/sanchonet/nufi-cwe-sanchonet-latest.zip)
  - [Lace](https://github.com/input-output-hk/lace)
  - [Yoroi](https://github.com/Emurgo/yoroi)
  - [demos wallet](https://github.com/Ryun1/cip95-demos-wallet)
- [x] The interface is used by one web application to allow users to engage with
      the Conway ledger design.
  - [SanchoNet GovTool](https://sanchogov.tools)
  - [GovTool](https://gov.tools)
  - [cip95-cardano-wallet-connector](https://github.com/Ryun1/cip95-cardano-wallet-connector/tree/master)
  - [drep-campaign-platform](https://github.com/IntersectMBO/drep-campaign-platform)
- [x] The interface is supported via libraries.
  - [Cardano JS-SDK](https://github.com/input-output-hk/cardano-js-sdk)
  - [purescript-cip95](https://github.com/mlabs-haskell/purescript-cip95)
  - [Mesh SDK](https://github.com/MeshJS/mesh)

### Implementation Plan

- [x] Provide a public Discord channel for open discussion of this
      specification.
  - See
    [`wallets-sanchonet`](https://discord.com/channels/826816523368005654/1143258005354328156/1143272934966837309)
    channel in the [IOG Technical Discord](https://discord.gg/inputoutput) under
    (to view you have to opt-in to the Sanchonet group in the start-here
    channel).
- [x] Author to engage with wallet providers for feedback.
- [x] Author to run a hackathon workshop with wallet providers.
  - In person and online hackathon run 2023.07.13, outcomes presented here:
    [CIP-95 pull request comment](https://github.com/cardano-foundation/CIPs/pull/509#issuecomment-1636103821).
- [x] Resolve all [Open Questions](#open-questions).
- [x] Author to provide test dApp to test against.
  - See
    [cip95-cardano-wallet-connector](https://github.com/Ryun1/cip95-cardano-wallet-connector/tree/master).
- [x] Author to provide a reference wallet implementation.
  - See [cip95-demos-wallet](https://github.com/Ryun1/cip95-demos-wallet/).
- [ ] Author to produce a set of test vectors for wallets to test against.
- [x] Author to move DRep key definitions to a separate CIP.
  - via the addition of [CIP-105 | Conway era Key Chains for HD Wallets](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md) via [CIPs PR #597](https://github.com/cardano-foundation/CIPs/pull/597). 

## Acknowledgments

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
  - Ed Eykholt - Blocktrust
  - Vladimir Volek - Five Binaries
  - Marek Mahut - Five Binaries
  - Markus Gufler - Cardano Foundation
  - Michal Ciborowski - BinarApps

</details>

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
