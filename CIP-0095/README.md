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
[CIP-1694? | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/pull/380)
focussed web-based stacks. Here we aim to support the requirements of both Ada
holders' and DReps' interactions with such web-based stacks.

> **Note** This proposal assumes knowledge of the ledger governance model as
> outlined within
> [CIP-1694?](https://github.com/cardano-foundation/CIPs/pull/380).

## Motivation: why is this CIP necessary?

CIP-1694 introduces many new concepts, entities and actors to Cardano;
describing their implementation at the ledger level. Yet, for most ecosystem
participants low level details are abstracted away by tools, such as wallets.
This creates a need for tooling to be able support the utilization of ledger
features. This specification allows for creation of web-based tools for the
utilization of CIP-1694's governance features.

This proposal enables Ada holders and DReps to engage web-based tooling through
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
> model matures. It is likely the precise data structures outlined here will be
> need to be adjusted.

### DRep Key

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

`m / 1718' / 1815' / account' / chain / address_index`

> **Note** `1718` was the year that François-Marie adopted the pseudonym
> Voltaire.

We strongly suggest that a maximum of one set of DRep credentials should be
associated with one wallet account, this can be achieved by setting `chain=0`
and `address_index=0`. Thus avoiding the need for DRep Key discovery.

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
we only inherit:

- [cbor\<T>](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#cbort)

#### DRepID

```ts
type DRepID = string;
```

A hex string representing a registered DRep's ID which is a 32-byte Blake2b-224
hash digest of a 32 byte Ed25519 public key, as described in
[CIP-1694 Registered DReps](https://github.com/JaredCorduan/CIPs/blob/voltaire-v1/CIP-1694/README.md#registered-dreps).

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

#### UnsignedTransaction

```ts
type UnsignedTransaction = string;
```

A hex-encoded string representing a CBOR transaction that is completely unsigned
(has an empty transaction witness set).

This data model is used to represent transactions which contain, for example:
DRep registration certificates and the client wishes the wallet inspect, add
signatures (with payment and DRep key) and submit.

#### SubmittedTransaction

```ts
interface SubmittedTransaction {
  tx: cbor<transaction>;
  txHash: string;
  witness: string;
}
```

This interface represents a transaction that has been submitted to chain.

- `tx`: A hex-encoded string representing CBOR transaction, which was submitted
  to chain.
- `txHash`: A string containing the hash of the transaction which contained this
  certificate that was submitted to chain and included in a block. This is to be
  used by clients to track the status of the delegation transaction on-chain.
- `witness`: A string containing the witnesses attached to the transaction.

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

Methods contained in this section on invocation should request the user to
review and to consent to signature and submission. The exceptions to this are
`.getActiveStakeKeys()` and `.getDRepKey()`, user consent should not be needed
to share public key information.

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

#### `api.submitVoteDelegation([tx: UnsignedTransaction, stakeKey: PubStakeKey]): Promise<SubmittedTransaction[]>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to inspect, sign and submit transaction(s)
containing vote delegation certificates. The wallet should articulate this
request from client application in a explicit and highly informative way. Users
must be shown the target of the delegation (DRepID or a predefined DRep
identifier) and must be informed which of their stake keys are being used. For
the case of multiple delegations at once, the user may only be asked for
permission to authorize all at once, but this can depend on wallet's
implementation.

If user grants permission, each transaction must be signed by the secret key of
the provided public stake key, with the signature and key to be added to the
transaction witness set before submission.

By allowing clients to supply the stake key we are placing the burden of
"multi-governance-delegation" management onto the client, reducing the
complexity for wallet implementations. By forcing wallets to inspect these
certificates it allows the user to catch malicious client applications
attempting to insert their own delegation targets.

##### Errors

One `TxSignError` should be returned if there is a signature error with any of
the certificates.

##### Returns

This returns an array of `SubmittedTransaction` objects which contain the
details of the submitted delegation certificates, for the client to confirm. The
returned `txHash`s can be used by the client to track the status of the
transactions containing the certificates on Cardano.

#### `api.submitDRepRegistration(tx: UnsignedTransaction, dRepKey: PubDRepKey): Promise<SubmittedTransaction>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to inspect, sign and submit a transaction
containing a DRep registration certificate. The wallet should articulate this
request from client application in a explicit and highly informative way. Users
should be made aware of the type of certificate, associated DRepID, metadata
anchor and deposit amount.

If user grants permission, the transaction must be signed by the secret key of
the provided public DRep Key, with the signature and key to be added to the
transaction witness set before submission.

By allowing clients to supply the DRep Key and choose UTxOs we are placing the
burden of managing a user's DRep registration deposit on the application. By
forcing wallets to inspect these certificates it allows the user to catch
malicious client applications attempting to insert their own data into the
certificate.

##### Errors

One `TxSignError` should be returned if there is a signature error with any of
the certificates.

##### Returns

This returns a `SubmittedTransaction` object which contains all the details of
the submitted registration certificate, for the client to confirm. The returned
`txHash` can be used by the client to track the status of the transaction
containing the certificate on Cardano.

#### `api.submitDRepRetirement: UnsignedTransaction, dRepKey: PubDRepKey): Promise<SubmittedTransaction>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to inspect, sign and submit a transaction
containing a DRep retirement certificate. The wallet should articulate this
request from client application in a explicit and highly informative way. Users
should be made aware of the type of certificate, associated DRepID and metadata
anchor.

If user grants permission, the transaction must be signed by the secret key of
the provided public DRep Key, with the signature and key to be added to the
transaction witness set before submission.

By forcing wallets to inspect these certificates it allows the user to catch
malicious client applications attempting to insert their own data into the
certificate.

##### Errors

One `TxSignError` should be returned if there is a signature error with any of
the certificates.

##### Returns

This returns a `SubmittedTransaction` object which contains all the details of
the submitted retirement certificate, for the client to confirm. The returned
`txHash` can be used by the client to track the status of the transaction
containing the certificate on Cardano.

#### `api.submitVote([tx: UnsignedTransaction, dRepKey: PubDRepKey]): Promise<SubmittedTransaction>[]`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to inspect, sign and submit transaction(s)
containing votes. The wallet should articulate this request from client
application in a explicit and highly informative way. For each vote, users must
be shown the governance action ID, vote choice (yes, no, abstain) and metadata
anchor. For the case of multiple votes at once, the user may only be asked for
permission to authorize all at once, but this can depend on wallet's
implementation.

If user grants permission, each transaction must be signed by the secret key of
the provided public stake key, with the signature and key to be added to the
transaction witness set before submission.

By forcing wallets to inspect these votes it allows the user to catch malicious
client applications attempting to alter the vote's contents.

##### Errors

One `TxSignError` should be returned if there is a signature error with any of
the transactions.

##### Returns

This returns an array of `SubmittedTransaction` objects which contain the
details of the submitted votes, for the client to confirm. The returned
`txHash`s can be used by the client to track the status of the transactions
containing the certificates on Cardano.

#### `api.submitGovernanceAction(tx: UnsignedTransaction): Promise<SubmittedTransaction>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to inspect, sign and submit a transaction
containing a governance action. The wallet should articulate this request from
client application in a explicit and highly informative way. For the governance
action the user must be shown the amount of ADA to be locked as deposit,
governance action type and the metadata anchor.

If user grants permission, the transaction must be signed using the wallets
payment key and submitted.

By allowing clients to choose UTxOs, we are placing the burden of managing the
deposit on the application. By forcing wallets to inspect these transactions it
allows the user to catch malicious client applications attempting to insert
their own data into the governance action.

##### Errors

One `TxSignError` should be returned if there is a signature error with any of
the transactions.

##### Returns

This returns a `SubmittedTransaction` object which contains all the details of
the submitted governance action, for the client to confirm. The returned
`txHash` can be used by the client to track the status of the transaction
containing the certificate on Cardano.

### Examples of Flows

#### Connection and Login

This describes a potential flow of connection between CIP-95 compatible client
application and wallet then a subsequent login.

1. **Connection:** User indicates to the client their intent to connect, causing
   client offer a list of supported wallets, user selects their desired wallet.
   The client will then invoke `.{wallet-name}.enable({ "cip": 95 })` from the
   shared `cardano` namespace.
2. **Wallet Confirmation:** The wallet indicates through its UI the clients
   intent to connect, the user grants permission.
3. **Share Credentials:** The client invokes both `.getActivePubStakeKeys()` and
   `.getDRepKey()`, causing the connected wallet to share relevant credentials.
4. **Chain Lookup:** The client uses a chain indexer to work out the governance
   state of the provided credentials.

#### Vote Delegation

Assume a "DRep Aggregator/Explorer" specialized client, who aggregates DRep
metadata from on-chain registration certificates to show to prospective
delegators. Assume that connection to a users wallet has already been made via
`cardano.{wallet-name}.enable({ "cip": 95})`.

1. **Choose DRep:** User browses DReps and selects one which align's with their
   values and chooses which stake credential they wish to use for delegation.
2. **Construct Delegation:** The client application uses CIP-30 endpoints to
   query the wallet's UTxO set and payment address. Using this information and
   the selected DRep ID constructs a transaction containing a vote delegation
   certificate. Likely using a helper support library.
3. **Submit Invocation:** Using one of the wallet's stake keys obtained via
   `.getActivePubStakeKeys()` the client passes the transaction and stake key to
   the wallet via `.submitVoteDelegation()`.
4. **Inspect, sign and submit:** The wallet inspects the content of the
   transaction, showing the user the target of the delegation (DRep ID) and the
   stake key being used. If the user confirm that they accepts this then the
   wallet should sign and submit the transaction.
5. **Feedback to user:** The wallet returns a `SubmittedTransaction` and the
   client uses the `txHash` field to track the status of the transaction
   on-chain, providing feedback to the user.

#### DRep Registration

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
   on-chain, providing feedback to the user.

## Rationale: how does this CIP achieve its goals?

The principle aim for this design is to reduce the complexity for wallet
implementors. This is motivated by the necessity for users to be able to
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

### Why Web-based Stacks

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

### Why DReps and Ada Holders?

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
majority of participants thus we aim to cast a wide net with this specification.

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

By placing the burden of submission onto wallets we prevent malicious clients
from being able to censor which transactions are submitted to chain. This is of
particular concern due to the potential political impact of transactions being
handled by this API. We thus deem it necessary for wallets to bare this burden.

One argument against this design is that, if wallets are required to be able to
inspect and thus understand these application specific transactions then they
may as well build the transaction. For this reason I have placed this back into
the

### Extension Design

Whilst CIP-30 facilitated the launch of dApp client development on Cardano, it's
functionality is limited in scope. Although it does offer generic functions,
these cannot satisfy the problem that this proposal tackles. Thus extending it's
functionality is a necessity.

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

### DRep Key

We chose to introduce the concept of a DRep Key, building on top of CIP-1694,
this we see as a necessary step for wallet implementors. By setting a
(hierarchical) deterministic derivation path it enables restorability from a
seed phrase.

With this definition we aim to standard for tooling to be able to derive DRep
credentials from mnemonics, not only those wallets who support this web-bridge.
This standard brings all the benefits of the application of generic ecosystem
standards.

- TODO: why not reuse Catalyst's CIP-36 key?

### Multi-stake Key Support

Although
[multi-stake key wallets](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0018)
are not widely adopted across Cardano, we make an effort to support them here.
This is because a single stake key can delegate to a single DRep. By allowing
users to spread stake across multiple stake keys it allows different weighted
delegation to different DReps, this could be a very desirable feature.

### Types of wallets

This specification does not cater for wallets who manage non-key-based stake
credentials and those who wish to handle non-key-based DRep credentials. This
does limit the usefulness of this specification, but we believe the added
complexity of supporting these types of wallet. This means that we are likely
excluding tooling for DAOs from being supported through this standard. The
argument could be made that such entities generally prefer to use more advanced
wallet tooling which is not dependent on web-based stacks.

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
  - This has been moved from the wallet to the application.
  - Since wallets still have to be able to be able to inspect these
    transactions, its not far away from just generating the transaction itself.
- Move DRep key definitions into a CIP which is dedicated to describing CIP-1694
  related credentials? or CIP-1852?
- Is it necessary to provide a method to prove ownership of DRep key? and can
  CIP-30's `api.signData()` be used to prove ownership of multi-stake keys?
- Is it sensible to place multi-stake key burden onto clients?
- <s>Does supporting governance action submission a necessary burden for the
  scope of this proposal?</s>
  - Since moving burden of transaction construction from wallet to app, this
    becomes much less of an issue as the complex error checking should now be
    done by the application.
- Should this proposal cater for non-key-based stake credential?
  - We could just change all references of keys to credentials to allow this?
- Should there be a more elegant way for the optional sharing of governance
  state?
- should provide support for combination certificates?

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
- [ ] Author to setup regular discussion forums to support wallet implementors.

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
