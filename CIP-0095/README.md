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

We define the following specification as an extension to the specification
described within CIP-30.

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

We strongly suggest that a maximum of one set of DRep credentials should be
associated with one wallet account, this can be achieved by setting `chain=0`
and `address_index=0`. Thus avoiding the need for DRep Key discovery.

We believe the overhead that would be introduced by "multi-DRep" accounts is an
unjustified expense. Future iterations of this specification may expand on this,
but at present this is seen as unnecessary.

> **Note** `1718` was the year that François-Marie adopted the pseudonym
> Voltaire.

#### Tooling

Supporting tooling should clearly label these key pairs as "CIP-95 DRep Keys".

Bech32 prefixes of `drep_sk` and `drep_vk` should be used.

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

A hex string representing 32 byte Ed25519 DRep public key, as described in
[DRep Key](#DRep-key).

#### PubStakeKey

```ts
type PubStakeKey = string;
```

A hex string representing 32 byte Ed25519 public key used as a staking
credential.

#### MetadataAnchor

```ts
interface MetadataAnchor {
  metadataURL: string;
  metadataHash: string;
}
```

This interface represents a metadata anchor which can be related to particular
on-chain entities.

- `metadataURL`: A string containing the URL-to-plaintext version of the
  metadata.
- `metadataHash`: A string containing a Blake2b-256 hash of the metadata
  plaintext, which is stored at the metadataURL. This hash allows clients to
  verify the correctness of data presented at metadataURL.

> **Note** This specification is not concerned with how metadata hosted.

#### DelegationCertificate

```ts
interface DelegationCertificate {
  target: DRepID | "Abstain" | "No Confidence";
  stakeKey: PubStakeKey;
}
```

This interface represents a vote delegation certificate that has been submitted
to chain and included within a block.

- `target`: The target of the delegation, DRep ID provided if the delegation was
  to a
  [registered DRep](https://github.com/JaredCorduan/CIPs/blob/voltaire-v1/CIP-1694/README.md#registered-dreps).
  If delegating to a
  [pre-defined DRep](https://github.com/JaredCorduan/CIPs/blob/voltaire-v1/CIP-1694/README.md#pre-defined-dreps)
  then the name.
- `stakeKey`: The public stake key acting as the stake credential of the Ada
  holder who has submitted the delegation.

#### SignedDelegationCertificate

```ts
interface SignedDelegationCertificate {
  certificate: DelegationCertificate;
  txHash: string;
  witness: string;
}
```

This interface represents a vote delegation certificate that has been submitted
to chain and included within a block.

- `certificate`: Contains the `DRepRegistrationCertificate` object.
- `txHash`: A string containing the hash of the transaction which contained this
  certificate that was submitted to chain and included in a block. This is to be
  used by clients to track the status of the delegation transaction on-chain.
- `witness`: A string containing the stake credential witness attached to the
  certificate.

#### DRepRegistrationCertificate

```ts
interface DRepRegistrationCertificate {
  dRepKey: PubDRepKey;
  metadataAnchor?: MetadataAnchor;
  depositAmount?: number;
  // reward address for deposit return TBC
}
```

This interface represents a DRep registration certificate as described in
[CIP-1698 Delegated Representatives](https://github.com/JaredCorduan/CIPs/blob/voltaire-v1/CIP-1694/README.md#delegated-representatives-DReps).
//todo: link CDDL

- `dRepKey`: The public side of the DRep Key pair used for witnessing the
  certificate and to be hashed to provide DRep ID.
- `metadataAnchor`: Optionally allows the linking of off-chain metadata.
- `depositAmount`: Optionally supplied by the client, if the user is registering
  for the first time a deposit amount is supplied.

#### SignedDRepRegistrationCertificate

```ts
interface SignedDRepRegistrationCertificate {
  certificate: DRepRegistrationCertificate;
  txHash: string;
  witness: string;
}
```

This is returned from the wallet back to the client once a DRep registration
certificate is submitted to chain and included in a block.

- `certificate`: Contains the `DRepRegistrationCertificate` object.
- `txHash`: A string containing the hash of the transaction which contained this
  certificate that was submitted to chain and included in a block. This is to be
  used by dApps to track the status of the transaction on-chain.
- `witness`: A string containing the DRep credential witness attached to the
  certificate.

#### DRepRetirementCertificate

```ts
interface DRepRetirementCertificate {
  dRepKey: PubDRepKey;
  expirationEpoch: number;
}
```

This data structure is used to represent a DRep retirement certificate as
described in
[CIP-1698 Delegated Representatives](https://github.com/JaredCorduan/CIPs/blob/voltaire-v1/CIP-1694/README.md#delegated-representatives-DReps).
//todo: link CDDL

- `dRepKey`: The public side of the DRep Key pair used for witnessing the
  certificate and to be hashed to obtain the required DRep ID.
- `expirationEpoch`: An integer representing the Cardano epoch number after
  which the DRep will retire.

#### SignedDRepRetirementCertificate

```ts
interface SignedDRepRetirementCertificate {
  certificate: DRepRetirementCertificate;
  txHash: String;
  witness: string;
}
```

This is returned from the wallet back to the client once a DRep retirement
certificate is submitted to chain and included in a block.

- `certificate`: Contains the `DRepRetirementCertificate` object.
- `txHash`: A string containing the hash of the transaction which contained this
  certificate that was submitted to chain and included in a block. This is to be
  used by clients to track the status of the transaction on-chain.
- `witness`: A string containing the dRep credential witness attached to the
  certificate.

#### Governance Action Types

Here we outline interfaces for each governance action which need to support
additional data to the ledger

##### NewCommittee

```ts
interface NewCommittee {
  keyHashes: string[];
  quorum: number;
}
```

Interface representing a governance action to introduce a new committee/quorum,
as described in
[Conway ledger specification `new_commitee`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L126).

- `keyHashes`: A string list representing the 28-byte Blake2b-224 hash digests
  of the new committee's keys.
- `committeeSize`: A number representing the needed quorum for the new
  committee.

##### UpdateConstitution

```ts
interface UpdateConstitution {
  constitutionHash: string;
}
```

Interface representing a governance action to update the Cardano Constitution
document, as described in
[Conway ledger specification `new_constitution`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L128).

- `constitutionHash`: A string containing the 32-byte Blake2b-256 hash digest of
  the new constitution document.

##### HardForkInit

```ts
interface HardForkInit {
  protocolVer: number;
}
```

Interface representing a governance action to initiate a Hard-Fork, as described
in
[Conway ledger specification `hard_fork_initiation_action`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L120).

- `protocolVer`: A number representing the new major protocol version too
  hard-fork to.

##### UpdateParameters

```ts
interface UpdateParameters {
  params: {
    key: string;
    newValue: number;
  }[];
}
```

// todo: make a better representation for this Interface representing a
governance action to update values of protocol parameters, as described in
[Conway ledger specification `parameter_change_action`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L118).

- `params`: An array of objects representing the parameters to be adjusted and
  their new values.
- `key`: The protocol parameter to be adjusted.
- `newValue`: A string array of each parameters new value.

##### TreasuryWithdrawal

```ts
interface TreasuryWithdrawal {
  mappings: {
    recipient: string;
    amount: number;
  }[];
}
```

Interface representing a governance action to withdraw funds from the Cardano
treasury, as described in
[Conway ledger specification `treasury_withdrawals_action`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L122).

- `mappings`: An array of objects representing reward addresses and amounts in
  Ada.
- `recipient`: A string representing a reward account address.
- `amount`: A number representing the amount of Lovelace to send to the
  corresponding recipient.

#### GovernanceActionID

```ts
interface GovernanceActionID {
  transactionID: string;
  govActionIndex: number;
}
```

Interface representing a governance action ID, as described in
[Conway ledger specification `governance_action_id`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L145).

- `transactionID`: A 32-byte Blake2b-256 hash digest of the transaction
  containing the governance action.
- `govActionIndex`: The index within the transaction body pointing to the
  governance action.

#### GovernanceAction

```ts
interface GovernanceAction {
  actionType:
    | "MotionOfNoConfidence" // no payload
    | NewCommittee
    | UpdateConstitution
    | HardForkInit
    | UpdateParameters
    | TreasuryWithdrawal
    | "Info"; // no payload
  lastAction: GovernanceActionID;
  depositAmount: number;
  rewardAddress: string;
  metadataAnchor: MetadataAnchor;
}
```

Interface representing a governance action proposal to be submitted in a
transaction, to chain, as described in
[Conway ledger specification `proposal_procedure`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#97).

- `actionType`: The governance action type, with needed additional payload data.
- `lastAction`: A `GovernanceActionID` object identifying the preceding
  governance action of this type.
- `depositAmount`: A number representing the number of Lovelace deposited for
  this action.
- `rewardAddress`: A string containing the address where the deposit will be
  returned to.
- `metadataAnchor`: Used to allow the linking of off-chain metadata.

#### SignedGovernanceAction

```ts
interface SignedGovernanceAction {
  action: GovernanceAction;
  governanceActionID: GovernanceActionID;
}
```

Interface representing a governance action which has been successfully submitted
to chain and included in a block.

- `action`: Contains the submitted `GovernanceAction` object.
- `governanceActionID`: A `GovernanceActionID` object representing the ID of the
  submitted governance action.

> **Note** Unlike other 'signed' data structures we omit a witness field, this
> is because verification from client applications is not necessary.

#### Vote

```ts
interface Vote {
  DRepKey: PubDRepKey;
  governanceActionID: GovernanceActionID;
  choice: "Yes" | "No" | "Abstain";
  metadataAnchor?: MetadataAnchor;
}
```

An interface used to represent an unsigned vote transaction, as described in
[Conway ledger specification `voting_procedure`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#89).

- `DRepKey`: The public side of the DRep Key pair used for witnessing the vote.
- `governanceActionID`: A `GovernanceActionID` object representing the target
  governance action for this vote.
- `choice`: A string representing the user's choice for the governance action
  vote, must be either 'Yes', 'No' or 'Abstain'.
- `metadataAnchor`: Optionally used to allow the linking of off-chain metadata
  in a way to ensure correctness.

> **Note** This interface does not map directly to the
> [Conway ledger specification `voting_procedure`](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L79),
> this is because this specification only caters for DRep role.

#### SignedVote

```ts
interface SignedVote {
  vote: Vote;
  txHash: string;
  witness: string;
}
```

Interface representing a vote transaction which has been successfully submitted
to chain and included in a block.

- `vote`: Contains the `Vote` object representing the submitted vote.
- `txHash`: A string containing the hash of the transaction which contained this
  submitted vote.
- `witness`: The governance credential witness for this vote.

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

#### `api.getDRepKey(): Promise<PubDRepKey>`

Errors: `APIError`

The connected wallet account provides the account's public DRep Key, derivation
as described in [DRep Key](#DRep-key).

##### Returns

The wallet account's DRep Key.

#### `api.getActiveStakeKeys(): Promise<PubStakeKey[]>`

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

#### `api.submitDelegation(DelegationCertificate[]): Promise<SignedDelegationCertificate[]>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to build, sign and submit vote delegation
certificates for a supplied DRepID and public stake key. These certificates are
described **todo: add CDDL when available**. This must be signed by the secret
key of the provided public stake key.

By allowing clients to supply the stake key we are placing the burden of
multi-governance-delegation management onto the client, reducing the complexity
for wallet implementations.

The user's permission to sign must be requested by the wallet, additionally
wallets may wish to display the contents of the certificate to the user to
check. This allows for the user to catch malicious clients attempting to alter
the certificate's contents. It is up to the wallet to decide if user
permission's is required for each signature or one permission granted to sign
all.

One `TxSignError` should be returned if there is a signature error with any of
the certificates.

##### Returns

This returns an array of `SignedDelegationCertificate` objects which contains
all the details of the submitted delegation certificate, for the client to
confirm. The returned `txHash`s can be used by the client to track the status of
the transactions containing the certificates on Cardano.

#### `api.submitDRepRegistration(certificate: DRepRegistrationCertificate): Promise<signedDRepRegistrationCertificate>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to build, sign and submit a DRep registration
certificate as described **todo: add CDDL when available**. The wallet must sign
the certificate using the secret side of the supplied DRep public key presented
in the `DRepKey` field.

The user's permission to sign this transaction must be requested for by the
wallet, additionally wallets may wish to display the contents of the certificate
to the user to check.

Wallets should be responsible for handling the payment of deposit required with
the submission of this certificate shown by the `depositAmount` field.

##### Returns

This returns a `signedDRepRegistrationCertificate` object which contains all the
details of the submitted registration certificate, for the client to confirm.
The returned `txHash` can be used by the client to track the status of the
transaction containing the certificate on Cardano.

#### `api.submitDRepRetirement(certificate: DRepRetirementCertificate): Promise<SignedDRepRetirementCertificate>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to build, sign and submit a DRep retirement
certificate as described in CIP-1694 **todo: add CDDL when available**. The
wallet must sign the certificate using the secret side of the supplied dRep
public key presented in the `DRepKey` field.

The user's permission to sign this transaction must be requested for by the
wallet, additionally wallets may wish to display the contents of the certificate
to the user to check.

##### Returns

This returns a `SignedDRepRetirementCertificate` object which contains all the
details of the submitted retirement certificate, for the client to confirm. The
returned `txHash` can be used by the client to track the status of the
transaction containing the certificate on Cardano.

#### `api.submitVote(votes: Vote[]): Promise<SignedVote>[]`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to build, sign and submit transaction(s)
containing supplied data in the vote field as described in the
[ledger conway specification](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L79).
The wallet must create and attach a governance credential witness using the
secret side of the supplied public DRep key. Wallets using this API should
always fill in the the role field with DRep.

The user's permission to sign must be requested by the wallet, additionally
wallets should display the contents of the vote transaction to the user to
check. This allows for the user to catch malicious clients attempting to alter
the vote's contents. It is up to the wallet to decide if user permission's is
required for each signature or one permission granted to sign all.

One `TxSignError` should be returned if there is a signature error with any of
the transactions.

##### Returns

This returns an array of `SignedVote` objects, matching each `Vote` passed at
invocation. The returned `txHash` fields can be used by the client to track the
status of the submitted vote transactions.

#### `api.submitGovernanceAction(action: GovernanceAction): Promise<SignedGovernanceAction>`

Errors: [APIError](#extended-apierror), [`TxSignError`](#extended-txsignerror)

This endpoint requests the wallet to build, sign and submit a transaction
containing supplied data in the governance action field as described in the
[ledger conway specification](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/conway/test-suite/cddl-files/conway.cddl#L94).

Wallets should be responsible for handling the payment of deposit required with
the submission of this certificate. This is in accordance with the
`depositAmount` field.

##### Returns

This returns a `SignedGovernanceAction` object which contains all the details of
the submitted governance action submission, for the client to confirm. The
returned `txHash` can be used by the client to track the status of the
transaction on Cardano.

### Examples of Flows

#### Login

1. **Connection:** User indicates to the client their intent to connect, causing
   client offer a list of supported wallets, user selects their wallet causing
   the client to invoke `.{wallet-name}.enable({ "cip": ?})` from the shared
   cardano `namespace`.
2. **Wallet Confirmation:** The wallet indicates through its UI the clients
   intent to connect, the user grants permission.
3. **Share Credentials:** The client invokes both `.getActiveStakeKeys()` and
   `.getDRepKey()`, causing the connected wallet to share relevant credentials.
4. **Chain Lookup:** The client uses a chain indexer to work out the governance
   state of the provided credentials.

#### Vote Delegation

Assume a "DRep Aggregator/Explorer" specialized client, who aggregates DRep
metadata from on-chain registration certificates to show to prospective
delegators. Assume that connection has already been made via
`.{wallet-name}.enable({ "cip": ?})`.

1. **Choose DRep:** User browses DReps and selects one which align's with their
   values and chooses which stake credential they wish to use for delegation.
2. **Construct Delegation:** The client passes the chosen DRep's ID and the
   connected wallet's chosen stake key to the wallet in a
   `api.submitDelegation()` call.
3. **Submit Delegation:** The wallet uses the provided details from the client
   to construct a delegation certificate, the wallet confirms the contents of
   the certificate with the user when asking for signature permission, wallet
   submits transaction through it's infrastructure.
4. **Feedback to user:** The wallet returns a `SignedDelegationCertificate` and
   the client uses the `txHash` to track the status of the transaction on-chain,
   providing feedback to the user.

#### DRep Registration

Assume that connection has already been established via
`.{wallet-name}.enable({ "cip": ?})`.

1. **User Indicates Intent:** User indicates to the client that they wish to
   register as a DRep. The client asks the user to provide metadata anchor, this
   is bundled with DRepID the client derives from the wallets DRepKey provided
   via `.getDRepKey()`. This information is passed to the wallet via
   `.submitDRepRegistration()`.
2. **Sign and Submit:** The wallet uses the data provided to generate a DRep
   registration certificate, signing it with the matching key to the key hash
   provided in the certificate. This is then submitted to chain and included in
   a block.
3. **Feedback to user:** The wallet returns a
   `SignedDRepRegistrationCertificate` and the client uses the `txHash` to track
   the status of the transaction on-chain, providing feedback to the user.

## Rationale: how does this CIP achieve its goals?

The principle aim for this design is to reduce the complexity for wallet
implementors. This is motivated by the necessity for users to be able to
interact with the age of Voltaire promptly, by keeping the wallet's providers
ask small we aim to reduce implementation time.

This design aims to make the tracking of a user's governance state an optional
endeavour for wallet providers. This is achieved by placing the responsibility
on clients to track a user's governance state, i.e. if a wallet user is a DRep,
what DRep a wallet holder has delegated to, etc.

Despite only defining the minimal set of endpoints required, we do not wish to
discourage the creation of subsequent CIPs with a wider range of governance
functionality. Nor does this specification aim to discourage wallet providers
from fully integrating CIP-1694 governance, side-stepping the necessity for this
API and client applications.

### Why Web-based Stacks

Web-based stacks, with wallet connectivity, are a familiar place for users to be
able to interact with Cardano. These tools lower the technical bar to engage
with the ecosystem. Thus we believe encouraging further adoption of this
approach is beneficial.

The primary alternative approach to this is wallet providers integrating this
functionality fully inside of wallet software, matching how staking is often
implemented. We deem this approach as preferable from a security standpoint for
combined functionality and would encourage wallet providers to pursue this. But
we understand that this may add overhead to wallet designs so offer this API as
an alternative.

### Why these DReps and Ada Holders

This proposal only caters to two types of actor described in CIP-1694; Ada
holders and DReps, this decision was three fold. Primarily this is to allow
these groups to utilize a client to participate in Cardano's governance. These
groups are likely less comfortable utilizing command-line interfaces than other
groups, thus making alternatives from them is a priority. Secondly, the other
types of actor (Constitution Committee member and SPOs) are identified by
different credentials than Ada holders and DReps. Thirdly, these groups
represent the majority of participants. These alternative credentials are
unlikely to be stored within standard wallet software which may interface with
this API.

### Transaction Burden

Endpoints defined here require wallets to generate, sign and submit transactions
to chain. The possible minimum ask for wallets is to just sign transactions this
is because signing keys should always remain within the wallet's control. This
alternative approach moves the complexity of transaction building and submission
onto client applications.

The design outlined here aims to improve the security by placing the burden of
submission onto wallets. This prevents malicious clients from being able to
censor which transactions are submitted to chain. This is of particular concern
due to the potential political impact of transactions being handled by this API.
We thus deem it necessary for wallets to bare this burden.

Furthermore by passing typescript interfaces to wallets rather than serialized
transactions we make inspection of transaction elements as easy as possible for
wallet's. This improves security as it avoids the need for wallets to
deserialize transactions to inspect their contents.

#### The role of the wallet

Relying on wallets for transaction construction and submission has precedent
from the approach of
[CIP-62?](https://github.com/cardano-foundation/CIPs/pull/296). This abstracts
clients from the need to manage core wallet functionality such as UTxO handling.
This approach allows client developers to focus on their domain rather than
having to be involved in wallet function management.

### Extension Design

Whilst CIP-30 facilitated the launch of client development on Cardano, it's
functionality is limited in scope. Although it does offer generic functions,
these cannot satisfy the problem that this proposal tackles. Thus extending it's
functionality is a necessity.

With this specification we chose to extend CIP-30's functionalities. There would
be two competing designs to this approach. One; move to have this specification
included within CIP-30. Two; deploy this specification as its own standalone
web-bridge.

It would be undesirable to include this functionality within the base CIP-30 API
because it would force all clients and wallets supporting CIP-30 to support this
API. This is because not all client apps or wallet will have the need or desire
to support this specification thus forcing cooperation would not desirable.

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

- The burden of transaction building to be placed on dApps or wallets?
- Move DRep key definitions into a CIP which is dedicated to describing CIP-1694 related credentials?
- Is it necessary to provide a method to prove ownership of DRep key? and can
  CIP-30's `api.signData()` be used to prove ownership of multi-stake keys?
- Is it sensible to place multi-stake key burden onto clients?
- Does supporting governance action submission a necessary burden for the scope
  of this proposal?
- Should this proposal cater for non-key-based stake credential?
- Should there be a more elegant way for the optional sharing of governance
  state?

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
