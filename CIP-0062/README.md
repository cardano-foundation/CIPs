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

## Rationale

To provide governance specific functionality to wallet's and expose such API to the dApps (i.e Voting Centers).

This also addresses some short-comings of [CIP-30](https://cips.cardano.org/cips/cip30/); which signData can only be done by known an address; This signature is not relevant to a specific address, nor the dApp will know an address attached to the voting key. The voting key derivation is defined in [CIP-36](https://cips.cardano.org/cips/cip36/).

Perhaps [CIP-30](https://cips.cardano.org/cips/cip30/) could be expanded to also know how to perform `signData` from a given public key from a specific derivation path; instead of doing so only by known address.

The other reason for this specification is to have a specific, but optional, namespace for governance specific wallet functionality. As such, wallet providers might choose not to implement this specification on top of [CIP-30](https://cips.cardano.org/cips/cip30/).

# Specification

## Version

The API Extension specified in this document will count as version 0.2.0 for version-checking purposes below.

## Data Types

### PublicKey

TODO: Define this.

### GovernanceKey

```ts
type GovernanceKey = {
  votingKey: string
  weight: number
}
```

* `votingKey` - Ed25519 pubkey 32 bytes HEX string
* `weight` - Used to calculate the actual voting power using the rules described
  in [CIP-36](https://cips.cardano.org/cips/cip36/).

### Voting Purpose

```ts
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

```ts
interface BlockDate {
  epoch: number
  slot: number
}
```

* epoch - an epoch value on the voting block chain.
* slot - a block slot number on the voting block chain.

#### Proposal

```ts
interface Proposal {
  votePlanId: string;
  proposalIndex: number;
  voteOptions?: number[];
  voteEncKey?: string;
}
```

Proposal information.

* votePlanId - Hex encoded string to represent vote plan unique identifier. This will be the same as anchored on voting chain, and is managed by the dApp.
* proposalIndex  - The index of the proposal within the vote plan.
* voteOptions - *Optional*. Total number of vote options.  Only present in a private/encrypted vote.
* voteEncKey - *Optional*. If this vote is Private, this field is present and contains the key used to encrypt the vote.  When the vote is public, this key is absent from the proposal.

### Vote

```ts
interface Vote {
  proposal: Proposal;
  choice: number;
  expiration: BlockDate;
  purpose: VotingPurpose;
  spendingCounter?: number;
  spendingCounterLane?: number;
}
```

An individual raw Unsigned Vote record.

* proposal - The [proposal](#proposal) being voted on.
* choice - This value MUST match one of the available `voteOptions` in the `proposal` element. An `UnknownChoiceError` should be thrown if the value is not one of the valid `voteOptions` of the `proposal`.
* expiration - Voting Chain epoch \& slot for when the vote will expire. This value is supplied and maintained by the dApp, and forms a necessary component of a [Vote](#vote)
* purpose - The [voting purpose](#voting-purpose) being voted on. (Currently always 0).
* spendingCounter - Optional, but if present, the spending counter is used to prevent double voting. The spending counter for the vote transaction will be supplied and maintained by the dApp. The dApp will manage supplying this in the correct order, and this should not be enforced by the Wallet.
* spendingCounterLane - Optional, if not present but required defaults to 0.  The spending counter may be spread across multiple lanes, this field defines which lane the spending counter relates to.

Note: `spendingCounter` and `spendingCounterLane` are fully managed by the voting dApp and if present are used to create the vote fragment for proper submission to the voting system.  The wallet should simply use the values defined, and does not need to track them.

## Delegation

```ts
interface Delegation {
    delegations: GovernanceKey[]
    purpose: VotingPurpose
}
```

The record of a voters delegation.

* delegations - List of [Governance Keys](#governancekey) and their voting weight to delegate voting power to.
* purpose - The [Voting Purpose](#voting-purpose) being delegated.  A voter may have multiple active delegations for different purposes, but only 1 active delegation per unique Voting Purpose.

## DelegatedCertificate

```ts
interface DelegatedCertificate {
  delegations: GovernanceKey[]
  stakingPub: string
  rewardAddress: string
  nonce: number
  purpose: VotingPurpose
}
```

See [CIP-36](https://cips.cardano.org/cips/cip36/) for an explanation of these fields.  Note: this object is not in exactly the same format as CIP-36, but the information it contains is the same.

## SignedDelegationMetadata

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

## Error Types

### Extended APIError

```ts
type enum APIErrorCode {
  UnsupportedVotingPurpose = -100
  InvalidArgumentError = -101
  UnknownChoiceError = -102
  InvalidBlockDateError = -103
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

## Governance Extension to CIP-30

### cardano.{walletName}.governance.apiVersion: String

The version number of the Governance Extension API that the wallet supports.

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

  Note: Currently only voting purpose 0 (Catalyst) is defined. The wallet should reject any other purpose requested.

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
[`api.signVotes()`](#apisignvotesvotes-vote-promisebytes) and
[`api.signData()`](#apisubmitdelegationdelegation-delegation-promisesigneddelegationmetadata)
must request the user's consent in an informative way for each and every API
call in order to maintain security.

The API chosen here is for the minimum API necessary for dApp <-> Wallet
interactions without convenience functions that don't strictly need the wallet's
state to work.

## api.signVotes(votes: Vote[], settings: string): Promise\<Bytes>[]

Errors: [`APIError`](#extended-apierror), [`TxSignError`](#extended-txsignerror)

* `votes` - an array of up to 10 votes to be validated with the wallet user and, if valid, signed.
* `settings` - *Optional*. Settings which are universally applicable to all `votes` being signed.  This is a json string.  The fields within the settings json string depend on the format of the vote record.  The wallet does not need to interpret this field and should pass it unchanged to the logic used to format the vote transaction.  However, to support multiple future vote transaction formats, the `settings` must contain at least:
  `'{"purpose":<number>,"ver":<number>,...}'`

  * `"purpose"` is the purpose of the vote transaction, which defines its format. It is a number and matches the defined [voting purposes](#voting-purpose).
  * `"ver"` is the version of the vote transaction, which also defines its format. It is a number.
  * `...` Variable fields defined by the vote transaction type being formatted and signed.

    These two fields allow the transaction format to be changed to accommodate future voting systems using this CIP standard.  The wallet can inspect these two fields to ensure the correct vote format is being signed.  It is legal for voting purposes to reuse or share vote formats.

    Vote transaction formats are defined by the [voting purposes](#voting-purpose), and are not documented in this CIP.

### List of known vote transaction formats

| `"purpose"` | `"ver"` | Vote Format | Specification | Example Settings String |
| --- | --- | --- | --- | --- |
| 0 | 0 | Project Catalyst vote: V0 | [Catalyst Core Specifications](https://input-output-hk.github.io/catalyst-core/) | `{"purpose":0,"ver":0,"fees":{"constant":10,"coefficient":2,"certificate":100},"discrimination":"production","block0_initial_hash":{"hash":"baf6b54817cf2a3e865f432c3922d28ac5be641e66662c66d445f141e409183e"},"block0_date":1586637936,"slot_duration":20,"time_era":{"epoch_start":0,"slot_start":0,"slots_per_epoch":180},"transaction_max_expiry_epochs":1}` |

IF the wallet user declines SOME of the votes, a [`TxSignError`](#extended-txsignerror) should be raised with `code` set to `VoteRejected` and the optional `rejectedVotes` array specifying the votes rejected.

However, if the wallet user declines the entire set of votes, the wallet should raise a [`TxSignError`](#extended-txsignerror) with the `code` set to `UserDeclined`.

If the `purpose` and `ver` of the vote transaction format as defined by the `settings` field is unknown to the wallet, a [`TxSignError`](#extended-txsignerror) should be raised with the `code` set to `UnsupportedVoteFormat`.

In all cases, where an error occurs, no signed votes are returned.

### Returns

`Bytes[]` - An array of the hex-encoded strings of the fully encoded and signed vote transactions.  The dApp will submit these votes on behalf of the wallet.

## api.getVotingKey(): Promise\<cbor<PublicKey\>\>

Should return the voting [public key](#publickey). The wallet should use `address_index`= 0 and return the public key for that index.

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

1. **`Get Voting Key`** - dApp call the method [**api.getVotingKey**](#apigetvotingkey-promise-cborpublickey) to get the voting public key.

2. **`Collect Voting Keys`** - The dApp Collects the dRep keys to delegate voting power to from the Catalyst Voting Center backend, and the user selects the required delegation.

3. **`Submit delegation`** - Submit the metadata transaction to the chain using [**api.submitDelegation**](#apisubmitdelegationdelegation-delegation-promisesigneddelegationmetadata) which implicitly sign and/or can use the already existing [**api.submitTx**](https://cips.cardano.org/cips/cip30/#apisubmittxtxcbortransactionpromisehash32),  available from [CIP-30](https://cips.cardano.org/cips/cip30/)

## Casting a vote

1. The dApp collects the users voting choices for a particular voting proposal.
2. The dApp submits that choice through [api.signVotes](#apisignvotesvotes-vote-promisebytes) which confirms the votes with the user, and signs them.

## **Test Vectors**

### ***keys***

`payment verification key`:

```json
{
    "type": "PaymentVerificationKeyShelley_ed25519",
    "description": "Payment Verification Key",
    "cborHex": "58203bc3383b1b88a628e6fa55dbca446972d5b0cd71bcd8c133b2fa9cd3afbd1d48"
}

```

`payment secret key`:

```json
{
    "type": "PaymentSigningKeyShelley_ed25519",
    "description": "Payment Signing Key",
    "cborHex": "5820b5c85fa8fb2d8cd4e4f624c206946652b6764e1af83034a79b32320ce3940dd9"
}
```

`staking verification key`:

```json
{
    "type": "StakeVerificationKeyShelley_ed25519",
    "description": "Stake Verification Key",
    "cborHex": "5820b5462be6a8a8ec0c4d6ee6edb83794a03df1bca43edc72b380df2ad3a982a555"
}
```

`staking secret key`:

```json
{
    "type": "StakeSigningKeyShelley_ed25519",
    "description": "Stake Signing Key",
    "cborHex": "58202f669f45365099666940922d47b29563d2c9f885c88a077bfea17631a7579d65"
}
```

### ***Delegation Certificate***

`Delegation certificate sample`:

```json
{
  "1":[["1788b78997774daae45ae42ce01cf59aec6ae2acee7f7cf5f76abfdd505ebed3",1],["b48b946052e07a95d5a85443c821bd68a4eed40931b66bd30f9456af8c092dfa",3]],
  "2":"93bf1450ec2a3b18eebc7acfd311e695e12232efdf9ce4ac21e8b536dfacc70f",

  "3":"e1160a9d8f375f8e72b4bdbfa4867ca341a5aa6f17fde654c1a7d3254e",
  "4":5479467,
  "5":0
}
```

`Delegation certificate after signature`:

```json
{
  "61284":{
    "1":[["1788b78997774daae45ae42ce01cf59aec6ae2acee7f7cf5f76abfdd505ebed3",1],["b48b946052e07a95d5a85443c821bd68a4eed40931b66bd30f9456af8c092dfa",3]],
    "2":"93bf1450ec2a3b18eebc7acfd311e695e12232efdf9ce4ac21e8b536dfacc70f",
    "3":"e1160a9d8f375f8e72b4bdbfa4867ca341a5aa6f17fde654c1a7d3254e",
    "4":5479467,
    "5":0
  },
  "61285":"0x3c25da29d43e70fb331c93b1197863e0d0a2e1cf7048994c580b0fc974f16bbb18c389aee380a66c0e7b6141f1df77b5db132dc228dbae9167238d96d4c4a80a"
}
```
