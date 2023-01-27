---
CIP: 62
Title: Cardano dApp-Connector Governance extension
Status: Proposed
Category: Wallets
Authors:
    - Bruno Martins <bruno.martins@iohk.io>
    - Steven Johnson <steven.johnson@iohk.io>
    - Ryan Williams <ryan.williams@iohk.io>
Implementors:
 - Begin <https://begin.is/>
 - Eternl <https://eternl.io/>
 - Flint <https://flint-wallet.com/>
 - GeroWallet <https://www.gerowallet.io/>
 - NuFi <https://nu.fi/>
 - Lace <https://www.lace.io/> 
 - Typhon <https://typhonwallet.io/>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/296
Created: 2021-06-11
License: CC-BY-4.0
---

# CIP-0062: Cardano dApp-Connector Governance extension

## Abstract

This document describes an interface between webpage/web-based stacks and Cardano wallets. This specification defines the API of the javascript object that needs to be injected into web applications in order to support [CIP-36](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0036) style governance functionality.

These definitions extend [CIP-30 (Cardano dApp-Wallet Web Bridge)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030).

## Motivation

The goal for this CIP is to extend the dApp-Wallet web bridge to enable the construction of transactions containing metadata that conforms to
[CIP-36 (Catalyst/Voltaire Registration Transaction Metadata Format - Updated)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0036),
enabling new functionality including vote delegation to either private or public representatives (dReps),
splitting or combining of private votes,
the use of different voting keys or delegations
for different purposes (Catalyst etc).

## Specification

### Version

The API Extension specified in this document will count as version `0.2.0` for version-checking purposes below.

### Data Types

#### PublicKey

A hex string representing a 32 byte Ed25519 public key.

#### WeightedKey

```ts
type WeightedKey = {
  voteKey: PublicKey
  weight: number
}
```

* `voteKey` - A vote `PublicKey` used to represent the target of the delegation.
* `weight` - Used to calculate the actual voting power using the rules described
  in [CIP-36](https://cips.cardano.org/cips/cip36/).

#### Voting Purpose

```ts
type enum VotingPurpose = {
  CATALYST = 0
}
```

`VotingPurpose`: Defines the voting purpose of the governance functions. This is used
to limit the scope of the governance functions. For example, a voting purpose
might be a subset of Catalyst proposals, a council election, or even some
private purpose (agreed by convention). Currently, only voting purpose 0 (Zero)
is defined, and it is for Catalyst events. As described in [CIP-36](https://cips.cardano.org/cips/cip36/).

**IMPORTANT**: The list of purposes in this CIP should be considered the
authoritative list of known purposes, subject to future amendment. Other voting
purposes will be defined as required, by either an update to this CIP or a
future CIP listing currently allocated Voting Purposes.

#### VotingCredentials
```ts
interface VotingCredentials {
  voteKey: PublicKey
  stakingCredential: PublicKey
}
```
Information used to represent a wallet's voting credentials.

* voteKey - Derivation as described within [CIP-0036](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0036), wallets should use `address_index` = 0.
* stakingCredential - At the moment, the only supported staking credential is a public staking key. This is used to represent the wallet's staked ADA.

#### Proposal

```ts
interface Proposal {
  votePublic: boolean // false
  votePlanId: string
  proposalIndex: number
  voteOptions: number
  voteEncKey: string
  }|{
  votePublic: boolean // true
  votePlanId: string
  proposalIndex: number
  }
```

Proposal information.

* votePublic - Boolean flag for if this `Proposal` should be included in a public or private vote. Additional fields are required in the `Proposal` for private votes (`votePublic = false`). IF the incorrect fields are provided based on `votePublic` then a `InvalidProposalError` should be thrown.
* votePlanId - Hex encoded string to represent vote plan unique identifier. This will be the same as anchored on voting blockchain, and is managed by the dApp. This is present in both public and private settings.
* proposalIndex  - The index of the `Proposal` within the vote plan. This is present in both public and private settings.
* voteOptions - Total number of vote options. Only present in a private/encrypted vote.
* voteEncKey - This field contains the election public key used to encrypt every private vote, this is part of an [ElGamal encryption scheme](https://en.wikipedia.org/wiki/ElGamal_encryption). Further information can be seen in [Jormungandr Voting](https://input-output-hk.github.io/jormungandr/jcli/vote.html). When the vote is public, this field is absent from the `Proposal`. 

#### Vote

```ts
interface Vote {
  proposal: Proposal;
  choice: number;
  purpose: VotingPurpose;
}
```

An individual raw Unsigned Vote record.

* proposal - The [Proposal](#proposal) being voted on.
* choice - This value MUST match one of the available `voteOptions` in the `proposal` element. An `UnknownChoiceError` should be thrown if the value is not one of the valid `voteOptions` of the `proposal`.
* purpose - The [voting purpose](#voting-purpose) being voted on. (Currently always 0).

#### Delegation

```ts
interface Delegation {
  delegations: WeightedKey[]
  purpose: VotingPurpose
}
```

The record of a voters delegation.

* delegations - List of [Weighted Keys](#WeightedKey) denoting the `voteKey` and `weight` of each delegation.
* purpose - The associated [Voting Purpose](#voting-purpose). A voter may have multiple active delegations for different purposes, but only once active delegation per unique `Voting Purpose`.

#### DelegatedCertificate

```ts
interface DelegatedCertificate {
  delegations: WeightedKey[]
  stakingPub: string
  paymentAddress: string
  nonce: number
  purpose: VotingPurpose
}
```

See [CIP-36](https://cips.cardano.org/cips/cip36/) for an explanation of these fields.  Note: this object is not in exactly the same format as CIP-36, but the information it contains is the same.

#### SignedDelegationMetadata

```ts
interface SignedDelegationMetadata {
  certificate: DelegatedCertificate
  signature: string
  txHash: string
}
```

* certificate: The [Delegation Certificate](#delegatedcertificate) that is signed.
* signature: signature on the CIP-36 delegation certificate.
* txHash: of the transaction that submitted the delegation.

### Error Types

#### Extended APIError

```ts
type enum APIErrorCode {
  UnsupportedVotingPurpose = -100
  InvalidArgumentError = -101
  UnknownChoiceError = -102
  InvalidProposalError = -103
  InvalidVotePlanError = -104
  InvalidVoteOptionError = -105
}

interface APIError {
  code: APIErrorCode,
  info: string
  votingPurpose: Purpose[]
}
```

These are the extended API Error Codes used by this specification. See
[CIP-30 Errors](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apierror) for the standard
API Error Codes, which are continue to be valid for this API Extension.

* UnsupportedVotingPurpose - The wallet does not support one of the requested voting purposes. The `votingPurpose` element will be present in the `APIError` object and will list all the voting purposes requested, which are unsupported bgy the wallet. Eg:

    If voting purposes 0,5 and 9 were requested, and only 0 was supported by the
    wallet. Then the errors will be:

    ```js
    {
      code: -100,
      info: "Unsupported Voting Purpose 5 & 9",
      votingPurpose: [5,9]
    }
    ```

* InvalidArgumentError - Generic error for errors in the formatting of the arguments.
* UnknownChoiceError - If a `choice` is not within the
  [`proposal`](#proposal) option set.
* InvalidProposalError - If the incorrect fields are provided based on if a `Proposal` is meant to be public or private.
* InvalidVotePlanError - If the `votePlanId` is not a valid vote plan.
* InvalidVoteOptionError - If the `index` is not a valid vote option.

##### APIError elements

* code - The `APIErrorCode` which is being reported.
* info - A Human readable description of the error.
* votingPurpose - (*OPTIONAL*) - Only present if the error relates to a voting purpose, and will list all the voting purposes which are involved in the error.  See the individual error code descriptions for more information.
* rejectedVotes - (*OPTIONAL*) - In a voting transaction, there may be multiple votes being signed simultaneously.

#### Extended TxSignError

```ts
type enum TxSignErrorCode {
  ProofGeneration = 1,
  UserDeclined = 2,
  VoteRejected = 3,
  UnsupportedVoteFormat = 4,
}
```

```ts
interface TxSignError = {
  code: TxSignErrorCode,
  info: String,
  rejectedVotes: number[]
}
```

All TxSignErrors defined in [CIP-30](https://cips.cardano.org/cips/cip30/#txsignerror) are unchanged.

* UserDeclined - Raised when the user declined to sign the entire transaction, in the case of a vote submission, this would be returned if the user declined to sign ALL of the votes.
* VoteRejected - On a vote transaction, where there may be multiple votes.  If the user accepted some votes, but rejected others, then this error is raised, AND `rejectedVotes` is present in the Error instance.

### Governance Extension to CIP-30

#### cardano.{walletName}.governance.apiVersion: String

The version number of the Governance Extension API that the wallet supports.

#### cardano.{walletName}.governance.enable(purpose: VotingPurpose[]): Promise\<API>

Errors: [`APIError`](#extended-apierror)

The `cardano.{walletName}.governance.enable()` method is used to enable the
governance API. It should request permission from the wallet to enable the API for the requested purposes.

If permission is granted, the rest of the API will be available. The wallet
should maintain a specific whitelist of allowed clients and voting purposes for
this API. This whitelist can be used to avoid asking for permission every time.

This api, being an extension of
[CIP-30](https://cips.cardano.org/cips/cip30/),
expects that `cardano.{walletName}.enable()` to be enabled and added to CIP-30
whitelist implicitly.

When both this API and [CIP-30](https://cips.cardano.org/cips/cip30/) being
enabled, is up to the wallet to decide the number of prompts requesting
permissions to be displayed to the user.

* `purpose` - this is a list of purposes that the dApp is advising that it will be using on the API.  The wallet must respond with an error if the purpose is not supported by the Wallet.

  Note: Currently only voting purpose 0 (Catalyst) is defined. The wallet should reject any other purpose requested.

##### Returns

Upon successful connection via
[`cardano.{walletName}.governance.enable()`](#cardanowalletnamegovernanceenablepurpose-votingpurpose-promiseapi),
a javascript object we will refer to as `API` (type) / `api` (instance) is
returned to the dApp with the following methods.

### Governance API

Except `signVotes`, no other method should require any user
interaction as the user has already consented to the dApp reading information
about the wallet's governance state when they agreed to
[`cardano.{walletName}.governance.enable()`](#cardanowalletnamegovernanceenablepurpose-votingpurpose-promiseapi).
The remaining methods
[`api.signVotes()`](#apisignvotesvotes-vote-promisebytes) and
[`api.signData()`](#apisubmitdelegationdelegation-delegation-promisesigneddelegationmetadata)
must request the user's consent in an informative way for each and every API
call in order to maintain security.

The API chosen here is for the minimum API necessary for dApp <-> Wallet
interactions without convenience functions that don't strictly need the wallet's
state to work.

#### api.signVotes(votes: Vote[], settings: string): Promise\<Bytes>[]

Errors: [`APIError`](#extended-apierror), [`TxSignError`](#extended-txsignerror)

* `votes` - an array of up to 10 votes to be validated with the wallet user and, if valid, signed.
* `settings` - *Optional*. Settings which are universally applicable to all `votes` being signed.  This is a json string.  The fields within the settings json string depend on the format of the vote record.  The wallet does not need to interpret this field and should pass it unchanged to the logic used to format the vote transaction.  However, to support multiple future vote transaction formats, the `settings` must contain at least:
  `'{"purpose":<number>,"ver":<number>,...}'`

  * `"purpose"` is the purpose of the vote transaction, which defines its format. It is a number and matches the defined [voting purposes](#voting-purpose).
  * `"ver"` is the version of the vote transaction, which also defines its format. It is a number.
  * `...` Variable fields defined by the vote transaction type being formatted and signed.

    These two fields allow the transaction format to be changed to accommodate future voting systems using this CIP standard.  The wallet can inspect these two fields to ensure the correct vote format is being signed.  It is legal for voting purposes to reuse or share vote formats.

    Vote transaction formats are defined by the [voting purposes](#voting-purpose), and are not documented in this CIP.

##### List of known vote transaction formats

| `"purpose"` | `"ver"` | Vote Format | Specification | Example Settings String |
| --- | --- | --- | --- | --- |
| 0 | 0 | Project Catalyst vote: V0 | [Catalyst Core Specifications](https://input-output-hk.github.io/catalyst-core/) | `{"purpose":0,"ver":0,"fees":{"constant":10,"coefficient":2,"certificate":100},"discrimination":"production","block0_initial_hash":{"hash":"baf6b54817cf2a3e865f432c3922d28ac5be641e66662c66d445f141e409183e"},"block0_date":1586637936,"slot_duration":20,"time_era":{"epoch_start":0,"slot_start":0,"slots_per_epoch":180},"transaction_max_expiry_epochs":1}` |

IF the wallet user declines SOME of the votes, a [`TxSignError`](#extended-txsignerror) should be raised with `code` set to `VoteRejected` and the optional `rejectedVotes` array specifying the votes rejected.

However, if the wallet user declines the entire set of votes, the wallet should raise a [`TxSignError`](#extended-txsignerror) with the `code` set to `UserDeclined`.

If the `purpose` and `ver` of the vote transaction format as defined by the `settings` field is unknown to the wallet, a [`TxSignError`](#extended-txsignerror) should be raised with the `code` set to `UnsupportedVoteFormat`.

In all cases, where an error occurs, no signed votes are returned.

##### Returns

`Bytes[]` - An array of the hex-encoded strings of the fully encoded and signed vote transactions.  The dApp will submit these votes on behalf of the wallet.

#### api.getVotingCredentials(): Promise\<VotingCredentials\>

Should return the in use voting credentials of the wallet.


##### Returns

The [VotingCredentials](#votingcredentials) of the wallet, which contain it's voting key and associated staking credential used for [CIP-36](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0036) style governance.

#### api.submitDelegation(delegation: Delegation): Promise\<SignedDelegationMetadata>

Errors: [`APIError`](#extended-apierror),
[`TxSendError`](https://cips.cardano.org/cips/cip30/#txsenderror),
[`TxSignError`](https://cips.cardano.org/cips/cip30/#txsignerror)

This endpoint should construct the cbor encoded delegation certificate according to the specs in [CIP-36 example](https://github.com/Zeegomo/CIPs/blob/472181b9c69feeedae0b5b2db8b42d0cf4eb1a11/CIP-0036/README.md#example).

It should then sign the certificate with the staking key as described in the same example as above.

The implementation of this endpoint can make use of the already existing [CIP-30](https://cips.cardano.org/cips/cip30/) `api.signData` and `api.submitTx` to perform the broadcasting of the transaction containing the metadata.

Upon submission of the transaction containing the delegation cert as part of metadata, the wallet should store the delegation in its local storage and return an object that contains the delegation cert, the signature and the txhash of the transaction that the certificate was submitted with.

* delegation - the voter registration [delegation](#delegation) record.

This should be a call that implicitly cbor encodes the `delegation` object and uses the already existing [CIP-30](https://cips.cardano.org/cips/cip30/) `api.submitTx` to submit the transaction. The resulting transaction hash should be returned.

This should trigger a request to the user of the wallet to approve the transaction.

##### Returns

The [Signed Delegation Metadata](#signeddelegationmetadata) of the voter registration delegation passed in the `delegation` parameter.

### Examples of Message Flows and Processes

#### Delegation

Recall from [CIP-36](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0036) a registration is a self-delegation, allocating one's voting power to one's own voting key.

1. **Get Voting Key** - dApp calls the method `api.getVotingCredentials()` to return the connected wallet account's public `voteKey`.

2. **Construct Delegation** - The dApp constructs `Delegation` using the Wallet's public `voteKey`, `weight` of 1 and choice of `VotingPurpose`.

3. **Submit Delegation** - The dApp passes the `Delegation` object to the Wallet to build a metadata transaction and submit this to Cardano blockchain. Wallets are able employ the already existing [`api.submitTx()`](https://cips.cardano.org/cips/cip30/#apisubmittxtxcbortransactionpromisehash32), available from [CIP-30](https://cips.cardano.org/cips/cip30/).

#### Voting

TODO

## Rationale

To provide [CIP-36](https://cips.cardano.org/cips/cip36/) style governance specific functionality to wallet's and expose such API to the dApps (i.e Voting Centers).

This also addresses some short-comings of [CIP-30](https://cips.cardano.org/cips/cip30/); which signData can only be done by known an address; This signature is not relevant to a specific address, nor the dApp will know an address attached to the voting key. The voting key derivation is defined in [CIP-36](https://cips.cardano.org/cips/cip36/).

Perhaps [CIP-30](https://cips.cardano.org/cips/cip30/) could be expanded to also know how to perform `signData` from a given public key from a specific derivation path; instead of doing so only by known address.

The other reason for this specification is to have a specific, but optional, namespace for governance specific wallet functionality. As such, wallet providers might choose not to implement this specification on top of [CIP-30](https://cips.cardano.org/cips/cip30/).

## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented and supported by various wallet providers.
- [ ] The interface is used by DApps to interact with wallet providers.

### Implementation Plan

- [x] Provide javascript package for Catalyst vote signing
  -  [wallet-wasm-js](https://www.npmjs.com/package/@catalyst-core/wallet-wasm-js)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).