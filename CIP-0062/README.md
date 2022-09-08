---
CIP: 62
Title: Cardano dApp-Connector Governance extension
Authors: Bruno Martins <bruno.martins@iohk.io>, Steven Johnson <steven.johnson@iohk.io>
Status: Draft
Type: Standards
Created: 2021-06-11
License: CC-BY-4.0
---

# Abstract

This document describe the interface between webpage / web-based stack and cardano wallets. This specifies that API of the javascript object that need to be injected into the web applications in order to support all the Governance features.

These definitions extend [CIP-30 (Cardano dApp-Wallet Web Bridge)](https://cips.cardano.org/cips/cip30/) to provide specific support for vote delegation.

# Motivation

The goal for this CIP is to extend the dApp-Wallet web bridge to enable the construction of transactions containing metadata that conforms to
[CIP-36 (Catalyst/Voltaire Registration Transaction Metadata Format - Updated)](https://cips.cardano.org/cips/cip36/),
enabling new functionality including vote delegation to either private or public representatives (dReps),
splitting or combining of private votes,
the use of different voting keys or delegations
for different purposes (Catalyst etc).

# Specification

## Version

The API Extension specified in this document will count as version 0.2.0 for version-checking purposes below.

## Data Types

### PublicKey

TODO: Define this.

### GovernanceKey

```js
type GovernanceKey = {
  votingKey: string,
  weight: number
}
```

* `votingKey` - Ed25519 pubkey 32 bytes HEX string
* `weight` - Used to calculate the actual voting power using the rules described
  in [CIP-36](https://cips.cardano.org/cips/cip36/).

### Voting Purpose

```js
type enum VotingPurpose = {
  CATALYST = 0
}
```

`VotingPurpose`: Defines the voting purpose of the governance functions. This is used
to limit the scope of the governance functions. For example, a voting purpose
might be a subset of Catalyst proposals, a council election, or even some
private purpose (agreed by convention). Currently, only voting purpose 0 (Zero)
is defined, and it is for Catalyst events.

**IMPORTANT**: The List of purposes in this CIP should be considered the
authoritative list of known purposes, subject to future amendment. Other voting
purposes will be defined as required, by either an update to this CIP or a
future CIP listing currently allocated Voting Purposes.

### BlockDate

```js
interface BlockDate {
  epoch: number
  slot: number
}
```

* epoch - an epoch value on the voting block chain.
* slot - a block slot number on the voting block chain.

#### Proposal

```js
interface Proposal {
  votePlanId: number
  voteOptions: number[]
}
```

Proposal information.

* votePlanId - The unique ID of this proposal in the vote plan.  This will be the same as anchored on voting chain, and is managed by the dApp.
* voteOptions - List of possible "choices" which can be made for this proposal.

### Vote

```js
interface Vote {
  proposal: Proposal,
  choice: number,
  expiration: BlockDate
  purpose: VotingPurpose,
  spendingCounter: number
}
```

An individual raw Unsigned Vote record.

* proposal - The [proposal](#proposal) being voted on.
* choice - This value MUST match one of the available `voteOptions` in the `proposal` element. An `UnknownChoiceError` should be thrown if the value is not one of the valid `voteOptions` of the `proposal`.
* expiration - Voting Chain epoch \& slot for when the vote will expire. This value is supplied and maintained by the dApp, and forms a necessary component of a [Vote](#vote)
* purpose - The [voting purpose](#voting-purpose) being voted on.
* spendingCounter - The spending counter is used to prevent double voting. The spending counter for the vote transaction will be supplied and maintained by the dApp. The dApp will manage supplying this in sequential order, and this should not be enforced by the Wallet.

It is required to attach it to the vote according to [Jormungandr Voting] (<https://input-output-hk.github.io/jormungandr/jcli/vote.html#voting>).

## Delegation

```js
interface Delegation {
    delegations: GovernanceKey[],
    purpose: VotingPurpose
}
```

The record of a voters delegation.

* delegations - List of [Governance Keys](#governancekey) and their voting weight to delegate voting power to.
* purpose - The [Voting Purpose](#voting-purpose) being delegated.  A voter may have multiple active delegations for different purposes, but only 1 active delegation per unique Voting Purpose.

## DelegatedCertificate

```js
interface DelegatedCertificate {
  delegations: GovernanceKey[],
  stakingPub: string,
  rewardAddress: string,
  nonce: number,
  purpose: VotingPurpose
}
```

See [CIP-36](https://cips.cardano.org/cips/cip36/) for an explanation of these fields.  Note: this object is not in exactly the same format as CIP-36, but the information it contains is the same.

## SignedDelegationMetadata

```js
interface SignedDelegationMetadata {
  certificate: DelegatedCertificate,
  signature: string,
  txHash: string
}
```

* certificate: The [Delegation Certificate](#delegatedcertificate) that is signed.
* signature: signature on the CIP-36 delegation certificate.
* txHash: of the transaction that submitted the delegation.

## Error Types

### Extended APIError

```js
APIErrorCode {
  UnsupportedVotingPurpose: -100,
  InvalidArgumentError: -101
  UnknownChoiceError: -102
  InvalidBlockDateError: -103
  InvalidVotePlanError: -104
  InvalidVoteOptionError: -105
}

APIError {
  code: APIErrorCode,
  info: string
  votingPurpose: Purpose[]
}
```

These are the extended API Error Codes used by this specification. See
[CIP-30 Errors](https://cips.cardano.org/cips/cip30/#apierror) for the standard
API Error Codes, which are continue to be valid for this API Extension.

* UnsupportedVotingPurpose - The wallet does not support one of the requested
  voting purposes. The `votingPurpose` element will be present in the `APIError` object and will list all the voting purposes requested, which are unsupported bgy the wallet. Eg:

    If Voting purposes 0,5 and 9 were requested, and only 0 was supported by the
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
* InvalidBlockDateError - If a [block date](#blockdate) is invalid.
* InvalidVotePlanError - If the `votePlanId` is not a valid vote plan.
* InvalidVoteOptionError - If the `index` is not a valid vote option.

#### APIError elements

* code - The `APIErrorCode` which is being reported.
* info - A Human readable description of the error.
* votingPurpose - (*OPTIONAL*) - Only present if the error relates to a voting purpose, and will list all the voting purposes which are involved in the error.  See the individual error code descriptions for more information.
* rejectedVotes - (*OPTIONAL*) - In a voting transaction, there may be multiple votes being signed simultaneously.

### Extended TxSignError

DataSignErrorCode {
 ProofGeneration: 1,
 AddressNotPK: 2,
 UserDeclined: 3,
 VoteRejected: 4,
}

```js
type DataSignError = {
 code: DataSignErrorCode,
 info: String,
 rejectedVotes: number[]
}
```

All TxSignErrors defined in [CIP-30](https://cips.cardano.org/cips/cip30/#txsignerror) are unchanged.

* UserDeclined - Raised when the user declined to sign the entire transaction.
* VoteRejected - On a vote transaction, where there may be multiple votes.  If the user accepted some votes, but rejected others, then this error is raised, AND `rejectedVotes` is present in the Error instance.

## Governance Extension

### cardano.{walletName}.governance.enable(purpose: VotingPurpose[]): Promise\<API>

Errors: [`APIError`](#extended-apierror)

The `cardano.{walletName}.governance.enable()` method is used to enable the
governance API. It should request permission from the wallet to enable the API for the requested purposes.

If permission is granted, the rest of the API will be available. The wallet
should maintain a specific whitelist of allowed clients and voting purposes for
this API. This whitelist can be used to avoid asking for permission every time.

This api, being an extension of
[CIP-30 (Cardano dApp-Wallet Web Bridge)](https://cips.cardano.org/cips/cip30/),
expects that `cardano.{walletName}.enable()` to be enabled and added to CIP-30
whitelist implicitly.

When both this API and [CIP-30](https://cips.cardano.org/cips/cip30/) being
enabled, is up to the wallet to decide the number of prompts requesting
permissions to be displayed to the user.

* `purpose` - this is a list of purposes that the dApp is advising that it will be using on the API.  The wallet must respond with an error if the purpose is not supported by the Wallet.

  Note: There are currently no "purpose specific" functions, all purposes are currently intended to operate equally.

  How the wallet validates the requested list of purposes is Wallet specific.  For example:

  When presented with a list of purposes `[0,1,2]`, and the wallet knows that purpose `0` is Catalyst (as defined above).  Then, when requesting the users permission, it might prompt and say something like :

    ```text
    Allow Voting Purposes:
      Catalyst (0)      [ ]
      Unknown Purpose 1 [ ]
      Unknown Purpose 2 [ ]
    ```

  The user could then select what purposes they would allow, and if it is not
  **ALL** of them, the response would indicate the purposes the use will not
  allow. The dApp may then re-attempt the connection with only the allowed
  purposes, which the wallet would already know are permitted by the user, so
  the wallet would not necessarily be required to re-authorize with the user.

  Alternatively, It would be perfectly permissable, currently, that the Wallet automatically reject any purpose not defined by this CIP.

  This is left up to the Wallet to decide how to handle this during
  authorization, and these are simple illustrative examples, to describe simple
  authorization flows.

### Returns

Upon successful connection via
[`cardano.{walletName}.governance.enable()`](#cardanowalletnamegovernanceenablepurpose-votingpurpose-promiseapi),
a javascript object we will refer to as `API` (type) / `api` (instance) is
returned to the dApp with the following methods.

## Governance API

All methods (all but the signing functionality) should not require any user
interaction as the user has already consented to the dApp reading information
about the wallet's governance state when they agreed to
[`cardano.{walletName}.governance.enable()`](#cardanowalletnamegovernanceenablepurpose-votingpurpose-promiseapi).
The remaining methods
[`api.submitVotes()`](#apisubmitvotesvotes-vote-promisebytes) and
[`api.signData()`](#apisubmitdelegationdelegation-delegation-promisesigneddelegationmetadata)
must request the user's consent in an informative way for each and every API
call in order to maintain security.

The API chosen here is for the mini mum API necessary for dApp <-> Wallet
interactions without convenience functions that don't strictly need the wallet's
state to work.

## api.submitVotes(votes: Vote[]): Promise\<Bytes>[]

Errors: [`APIError`](#extended-apierror), [`TxSignError`](#extended-txsignerror)

* votes - an array of up to 10 votes to be validated with the wallet user, and if valid, signed.

IF the wallet user declines ANY of the votes, a `DataSignError` should be raised, but with the optional

### Returns

`Bytes[]` - An array of the hex-encoded string of the fully encoded and signed vote transaction.  The dApp will submit this vote to the Catalyst Governance Subchain Bridge on behalf of the wallet.

## api.getVotingKeys**(): Promise<cbor<PublicKey\>[]>

Should return a list of all the voting keys for the current wallet.

### Returns

An array with the cbor hex encoded public keys.

## api.rotateVotingKey(): Promise<cbor<PublicKey\>>

This call should explicitly rotate the current in-use voting key. Given the current `address_index` in the derivation path defined in [CIP-36](https://cips.cardano.org/cips/cip36/), it should be incremented by 1.

The key should be derived from the following path.

```text
m / 1694' / 1815' / account' / role' / address_index'
```

`1694` (year Voltaire was born) Sets a dedicated `purpose` in the derivation path for the voting profile.

`address_index` - index of the key to use.

### Returns

cbor hex encoded representation of the [public key](#publickey).

## api.getCurrentVotingKey(): Promise\<cbor<PublicKey\>>

Should return the current in-use voting [public key](#publickey). The wallet should maintain a reference to the current `address_index` counter and return the public key for that index.  This call does NOT rotate the `address_index`.

### Returns

cbor hex encoded representation of the public key.

## api.submitDelegation(delegation: Delegation): Promise\<SignedDelegationMetadata>

Errors: [`APIError`](#extended-apierror),
[`TxSendError`](https://cips.cardano.org/cips/cip30/#txsenderror),
[`TxSignError`](https://cips.cardano.org/cips/cip30/#txsignerror)

This endpoint should construct the cbor encoded delegation certificate according to the specs in [CIP-36 Example](https://github.com/Zeegomo/CIPs/blob/472181b9c69feeedae0b5b2db8b42d0cf4eb1a11/CIP-0036/README.md#example).

It should then sign the certificate with the staking key as described in the same example as above.

The implementation of this endpoint can make use of the already existing [CIP-30](https://cips.cardano.org/cips/cip30/) `api.signData` and `api.submitTx` to perform the broadcasting of the transaction containing the metadata.

Upon submission of the transaction containing the delegation cert as part of metadata, the wallet should store the delegation in its local storage and return an object that contains the delegation cert, the signature and the txhash of the transaction that the certificate was submitted with.

* delegation - the voter registration [delegation](#delegation) record.

This should be a call that implicitly cbor encodes the `delegation` object and uses the already existing [CIP-30](https://cips.cardano.org/cips/cip30/) `api.submitTx` to submit the transaction. The resulting transaction hash should be returned.

This should trigger a request to the user of the wallet to approve the transaction.

### Returns

The [Signed Delegation Metadata](#signeddelegationmetadata) of the voter registration delegation passed in the `delegation` parameter.

# Examples of Message Flows and Processes

## Delegation Cert process

1. **`Get Voting Key`** - dApp call the method [**api.getCurrentVotingKey**](#apigetcurrentvotingkey-promisecborpublickey) to return a ed25519 32 bytes public key (x value of the point on the curve).

2. **`Collect Voting Keys`** - The dApp Collects the dRep keys to delegate voting power to from the Catalyst Voting Center backend, and the user selects the required delegation.

3. **`Submit delegation`** - Submit the metadata transaction to the chain using [**api.submitDelegation**](#apisubmitdelegationdelegation-delegation-promisesigneddelegationmetadata) which implicitly sign and/or can use the already existing [**api.submitTx**](https://cips.cardano.org/cips/cip30/#apisubmittxtxcbortransactionpromisehash32),  available from [CIP-30](https://cips.cardano.org/cips/cip30/)

## Casting a vote

1. The dApp collects the users voting choices for a particular voting proposal.
2. The dApp submits that choice through [api.submitVotes](#apisubmitvotesvotes-vote-promisebytes) which confirms the votes with the user, and signs them.
