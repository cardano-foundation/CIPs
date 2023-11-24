---
CIP: ????
Title: Cardano dApp-Wallet Web Bridge
Status: Proposed
Category: Wallets
Authors:
  - Fell-x27
Implementors: N/A
Discussions: N/A
Created: 2023-11-21
License: CC-BY-4.0
---

<!-- TOC -->
  * [Abstract](#abstract)
  * [Motivation: why is this CIP necessary?](#motivation-why-is-this-cip-necessary)
  * [Specification](#specification)
    * [The main idea](#the-main-idea)
    * [Data Types](#data-types)
      * [Auto](#auto)
      * [cbor<T>](#cbort)
      * [JSON](#json)
      * [URI](#uri)
      * [BigIntString](#bigintstring)
      * [HexString](#hexstring)
      * [base58](#base58)
      * [AddressString](#addressstring)
      * [AccountEra](#accountera)
      * [AccountId](#accountid)
      * [NativeToken](#nativetoken)
      * [AssetBundle](#assetbundle)
      * [Certificate](#certificate)
      * [Mint](#mint)
      * [OuterUTxO](#outerutxo)
      * [Datum](#datum)
      * [Movement](#movement)
      * [Delegation](#delegation)
      * [Metadata](#metadata)
      * [RequiredSign](#requiredsign)
      * [TransactionScript](#transactionscript)
      * [DataSignature](#datasignature)
    * [Errors](#errors)
    * [Bridge API](#bridge-api)
      * [Code injection](#code-injection)
      * [CardanoBridge](#cardanobridge)
      * [CardanoWalletAPI](#cardanowalletapi)
        * [connect()](#connectnetworkmagic-number-accountid-accountid-promiseaccountid)
        * [disconnect()](#disconnectaccountid-accountid-promisevoid)
        * [getBalance()](#getbalanceaccountid-accountid-promiseassetbundle)
        * [getDelegation()](#getdelegationaccountid-accountid-promisedelegation)
        * [buildTransaction()](#buildtransactiontx-transactionscript-accountid-accountid-promise-transaction-cbortransaction-txhash-hexstring-)
        * [signTransaction()](#signtransactiontxhash-hexstring-accountid-accountid-outerwitnesses-cborwitnessset-promisecborwitnessset)
        * [submitTransaction()](#submittransactiontxhash-hexstring-accountid-accountid-promisehexstring)
        * [isTransactionAccepted()](#istransactionacceptedtxhash-hexstring-promisenumber)
        * [signData()](#signdatapayload-hexstring-accountid-accountid-withstakekey-boolean-promisedatasignature)
    * [Example](#example)
  * [Rationale: how does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)
  * [Path to Active](#path-to-active)
    * [Acceptance Criteria](#acceptance-criteria)
    * [Implementation Plan](#implementation-plan)
  * [Copyright](#copyright)
<!-- TOC -->

## Abstract

This document describes the reevaluation of the existing approach to connecting Cardano DApps and wallets, as detailed in CIP-30. Its purpose is to simplify the integration of ecosystem products for both sides, and also to ease the development of DApps themselves by simplifying the process without losing any capabilities.
The new approach still relies on code injection, but offers a more transparent API. The main idea is that a DApp should not perform the functions of a wallet.

## Motivation: why is this CIP necessary?

This CIP addresses several issues that complicate the development of the Cardano ecosystem with the current integration standard:

1. **Complexity in Writing Client-Side Logic for DApps**: As they essentially need to implement their own wallet each time, including algorithms for coin selection, UTxO management, UTxO validation, TX building, etc. They shouldn't be doing this. There is already a separately written wallet that connects to their application for this purpose. <br><br>

2. **Integration Difficulties**: This implies complicating the internal logic of wallets, adding endpoints for importing transactions, writing logic for checks/validation of foreign transactions, etc. This could be avoided if the transaction was created and processed natively by the wallet.<br><br>

3. **Privacy Issues**: Currently, the wallet must pass all information to the DApp, including the UTxO set and full addresses on one hand, and trust the user's funds to the transaction building code inside the DApp on the other. This is not obvious to the user, and in case of problems, they will blame the wallet developers.<br><br>

4. **Current Role of Wallets**: At present, the wallet is essentially just a synchronization point for the client side of the DApp with the blockchain. Yes, it generates user signatures, but, for example, if we use a HW-wallet, then the task of the SW-wallet is reduced to 'submit tx'. This is an incorrect design of communication.<br><br>

5. **Scalable Complexity**: Currently, the integration standard implies that the complexity of the solution on the DApp side **must be** unjustifiably high even for elementary things that do not require knowledge of CBOR, CDDL, or an understanding of the difference between bech32 and base58.<br><br>

6. **Reducing Dependencies**: Currently, all DApps developers **must** operate only with CBOR-CDDL entities, making them dependent on third-party libraries such as `cardano_serialization_lib`, and forcing them to integrate these libraries into their projects. This complicates the logic, increases the size of the loaded page, necessitates keeping up with updates, etc., thereby increasing the number of failure factors in the application's logic.<br><br>

7. **Lack of abstraction**: The Cardano ecosystem is actively developing, especially in everything related to Plutus. DApps struggle to keep up with the innovations. Because of this, we encounter a heavy inconsistency in approaches. For example, this concerns everything related to collaterals at the moment. Cardano has long allowed making their use transparent and convenient for the user, but not all DApps support these approaches, forcing wallets to "reserve collateral UTxO" and somehow integrate this into UX. Moreover, the very fact that the DApp operates the collateral, and not the wallet (which only offers collateral but without guarantees that it will be used), makes the user vulnerable.<br><br>

8. **Security**: Currently, DApps are given too much responsibility in the formation of transactions. This could potentially become an attack vector on a user who is confident in their security. Besides the risk of leaking wallet data, including addresses, there is a possibility that a DApp could form a malware transaction. This transaction might include fields not checked by the wallet but still obtain all necessary signatures. For example, the user could unknowingly become part of a criminal scheme or lose funds.<br><br>

9. **Trustful system**: While blockchain is inherently a trustless system, it seems very odd when a wallet unconditionally trusts all user data to a third party at the first request.<br><br>

By solving these problems, we will lower the entry barrier for DApp developers into the ecosystem, while simultaneously enhancing the security of the end-user who has entrusted their funds to a wallet, but should not trust their management to just any application they encounter. The wallet will act as a black box, and the DApp as an extension of its UI, not a replacement of its engine.

Additionally, this approach will simplify the integration of wallets and DApps from the wallet developers' perspective, as it will provide a more natural interface for interaction, easily translatable into native scenarios of interaction with the ordinary user through the wallet's own UI.

## Specification

### The main idea
The main idea is to delegate as many operations as possible to the wallet, which are its core functions. This will greatly simplify the lives of DApps developers. It will also normalize the transaction pipeline, which is currently highly intermingled between the DApp and the wallet.
We are moving away from imperative interaction with the wallet towards a declarative approach, where the DApp does not have to assemble the transaction itself; it should be sufficient to **describe** the desired outcome. Just as a regular wallet user is not required to delve into all the details - they simply specify the address, amount, and press a button. This is literally why software wallets exist.
For example, here is a description of a transaction sending 1 ada to some address in the testnet:

```
{
    outputs:[{
        address: "addr_test1qpy486p7jhq933kay7rf78jz2j6k5ya7u95nnnjetgj9r02dp276p7j8023vmum9wu8gp7q54f3rjke45j0klk3pmwvsgyx4n7",
        value: {
            lovelaces: 1000000
        }
    }]
}
```

Or a description of a delegation transaction to a certain pool:


```
{
    certificates: [{
        type: "stakeDelegation",
        stakeKeyId: 0,
        poolHash: "660f2b816e90e4e826daebf33357d76ab89414f88d57dd7d9f7898fe"
    }]
}
```


This is quite enough. The DApp shouldn't have to calculate change, fees, select inputs, withdrawal rewards and so on. It just needs to **tell the wallet what result it needs**.
Let's understand how this works.

### Data Types

#### `Auto`

Technically, it's not a type, but just a string constant "auto" passed instead of any specific value.

* "auto" can only be used where it is explicitly stated, for example, if a value can be `Movement[] | Auto`;
* When we pass "auto" instead of something, we imply that the wallet should take care of substituting the correct value on its own:
    * For example, `inputs: "auto"` indicates that the wallet should take care of having transaction inputs that cover its tasks;
* Typically, the "auto" value can be found in optional fields, and this is not accidental:
    * "auto" is the default value;
    * If any value was omitted, the wallet should treat it as if it were equal to "auto";

```ts
    type Auto = "auto";
```

#### `cbor<T>`

A hex-encoded string representing [CBOR](https://tools.ietf.org/html/rfc7049) corresponding to `T` defined via [CDDL](https://tools.ietf.org/html/rfc8610) either inside of the [Shelley Multi-asset binary spec](https://github.com/input-output-hk/cardano-ledger-specs/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl) or, if not present there, from the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md).
This representation was chosen when possible as it is consistent across the Cardano ecosystem and widely used by other tools, such as [cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib), which has support to encode every type in the binary spec as CBOR bytes.<br><br>

#### `JSON`

[JavaScript Object Notation](https://json-schema.org/draft/2020-12/json-schema-core) is a lightweight data-interchange format that is easy for humans to read and write, and easy for machines to parse and generate. It is based on a subset of the JavaScript Programming Language and is commonly used for transmitting data in web applications and for storing configuration settings.<br><br>

#### `URI`

A URI image (e.g. data URI base64 or other) for img src for the wallet which can be used inside the dApp for the purpose of asking the user which wallet they would like to connect with.<br><br>

#### `BigIntString`

A BigInt number, stored as a string value. For example, the amount of something. It may be negative (e.g., for token burning).<br><br>

#### `HexString`

Byte data, converted to hex and stored as a string value. For example, the hash of something. Note, this is not the same as cbor<T>, although there is no difference in representation between them, there is a difference at the level of context and use cases!<br><br>

#### `base58`

A base58-encoded hexadecimal value. Typically used for Byron addresses.<br><br>

#### `AddressString`

A string representing an address in either bech32 or base58 format. Not CBOR!<br><br>

#### `AccountEra`

A string indicating whether the account belongs to the `Byron` or `Shelley` eras of Cardano.

```ts
type AccountEra = "Byron" | "Shelley";
```

#### `AccountId`

An arbitrary string that serves as the identifier of the wallet account connected to the DApp, formed by the wallet according to its own rules. The main point is that the wallet understands what is required of it when it receives this identifier in a request.

```ts
type AccountId = string;
```

#### `NativeToken`

A structure describing a `native token` in the Cardano network.

```ts
type NativeToken = {
    policyId: HexString,
    name: HexString | null,
    amount: BigIntString
};

```

* **`policyId`**

  Contains the [hexadecimal](#hexstring) representation of the asset's `policyID`.<br><br>

* **`name`**

  Contains the [hexadecimal](#hexstring) representation of the asset's `name`. If absent, the value should be set to `null`.<br><br>

* **`amount`**

  Contains the quantity of the asset [without a decimal part](#bigintstring). That is, if we want to describe 1 token with a decimal part of 6 digits, the amount should be set to 1,000,000, i.e., 1 * 10^6. Setting the value to 1 would be equivalent to 0.000001!<br><br>


#### `AssetBundle`

A structure describing the value being transferred in the Cardano network.

```ts
type AssetBundle = {
    lovelaces: BigIntString,
    nativeTokens?: NativeToken[]
};
```

* **`lovelaces`**

  The amount of ada, in [lovelaces](#bigintstring).<br><br>

* **`nativeTokens`**

  Is an array of [`NativeToken`](#nativetoken), optional. If the presence of tokens is not implied, it can be equal to an empty array, or omitted.<br><br>


#### `Certificate`

A structure describing user certificates in the Cardano network.

```ts
type Certificate = {
    type: "stakeRegistration" | "stakeDeregistration" | "stakeDelegation",
    stakeKeyId: number,
    poolHash?: HexString
};
```

* **`type`**

  Takes one of three preset values, describing the type of the certificate, and is mandatory.<br><br>

* **`stakeKeyId`**

  Indicates the user's staking key number in the derivation path. To ensure the key belongs to the user, we only inform the wallet of its ordinal number. By default, for wallets without multi-delegation, it is 0.<br><br>

* **`poolHash`**

  Points to the [hexadecimal](#hexstring) representation of the stakepool identifier, optional. Do not confuse it with `bech32 poolId`!<br><br>


#### `Mint`

A structure describing minting or burning for native tokens in the Cardano network.

```ts
type Mint = {
    nativeScript: cbor<NativeScript>,
    tokens: nativeToken[]
};
```

* **`nativeScript`**

  Contains a [CBOR](#cbort)-serialized hex-encoded NativeScript associated with the tokens being created.<br><br>

* **`tokens`**

  Contains an array of [`nativeToken`](#nativetoken), describing the tokens that will be minted or burned. If we plan to burn tokens, the `amount` should be negative.<br><br>

#### `OuterUTxO`

A structure describing an external UTxO that should be included by the wallet in a future transaction. Note that this refers to an external UTxO, which does not belong to the current wallet. For example, a smart contract's UTxO. It is assumed that the signature for it will also be provided externally.

```ts
type OuterUTxO = {
    hash: HexString,
    index: number,
    value: AssetBundle  
};
```

* **`hash`**

  Contains the [hash](#hexstring) of the UTxO.<br><br>

* **`index`**

  Accordingly, contains its index.

  > **Note:** that there are no "#" symbols here, which can be found in the usual notation of hash#index.

* **`value`**

  Describes the [assets](#assetbundle) associated with this UTxO. Since this is a UTxO not belonging to the wallet, we must inform it of these details to enable the calculation of change.<br><br>

#### `Datum`

The structure describing the data passed along with the transaction output, necessary for working with smart contracts. Note that it has 2 alternative forms: `hash` and `inline`.

```ts
Datum: {
    type: "hash",
    data: cbor<DataHash>
} | {
    type: "inline",
    data: cbor<PlutusData>
}
```

* **`type`**

  Specifies the type of data being transmitted. It can be either a `hash` or an `inline` representation. Depending on it, the content of the `data` field changes. <br><br>

* **`data`**

  Contains the transmitted data.

  If the `hash` type was previously specified, then it contains a [CBOR](#cbort)-serialized hex-encoded `CDDL dataHash` object, calculated for a PlutusData.
  If the `inline` type was previously specified, then it contains a [CBOR](#cbort)-serialized hex-encoded `CDDL PlutusData` object itself.<br><br>


#### `Movement`

A structure describing the movement of value in the Cardano network.

```ts
type Movement = {
    value: AssetBundle,
    address?: AddressString | Auto,
    datum?: Datum
};
```

* **`value`**

  Represents an instance of [`AssetBundle`](#assetbundle).<br><br>

* **`address`**

  Must contain a bech32 or base58 [address](#addressstring) of the receiver. If omitted or `"auto"`, it means the wallet can choose which address to make it to (for example, a change address).<br><br>

* **`datum`**

  Contains [data](#datum) for smart contract operation, or their hash. Can be omitted.<br><br>


#### `Delegation`

A structure describing the state of delegation in the Cardano network.

```ts
type Delegation = {
	poolHash: HexString,
	stakeKeyId: number
}
```

* **`poolHash`**

  Points to the [hexadecimal](#hexstring) representation of the stakepool identifier, optional. Do not confuse it with `bech32 poolId`!<br><br>

* **`stakeKeyId`**
  Contains the index number of the staking key used in delegation.<br><br>

#### `Metadata`

A structure describing the metadata of a transaction in the Cardano network.

```ts
type Metadata = {
    metadatum: JSON,
    schema: number
};
```

* **`metadatum`**

  Contains custom [JSON](#json).<br><br>

* **`schema`**

  Indicates the number of the "schema", in most cases, it is acceptable to specify 0.<br><br>

#### `RequiredSign`

A structure describing the required additional signatures for a transaction.

```ts
type RequiredSign = {
    inner: boolean,
    keyType: "payment" | "stake",
    keyHash: cbor<Ed25519KeyHash>
};
```

* **`inner`**

  Indicates whether this signature is client-side. If `true`, it means that the wallet must provide it during the signing phase. If `false`, the wallet only needs to add the requirement for its presence.<br><br>

* **`keyType`**

  This field is usually required if `inner` equals `true`, and it indicates the type of key to guide the wallet on which address chain to look for it.<br><br>

* **`keyHash`**

  Contains a [CBOR](#cbort)-serialized hex-encoded representation of CDDL Ed25519KeyHash, for which we are requesting a signature.<br><br>

#### `TransactionScript`

A structure describing a transaction in the Cardano network. Note, all fields are optional. It's not necessary to form it completely every time.
Also, there are no fields for specifying change, fees and withdrawal, as this is the responsibility of the wallet.
Our task is to explain to the wallet **what we want as a result**, not **what it should do to achieve it**.

```ts
type TransactionScript = {
    inputs?: OuterUTxO[] | Auto,
    outputs?: Movement[] | Auto,
    collateralNeeded: boolean | Auto,
    certificates?: Certificate[],
    mintings?: Mint[],
    metadata?: {body: Metadata[], hash?: HexString | Auto},
    additionalSigns?: RequiredSign[],
    scriptDataHash?: cbor<ScriptDataHash>,
    dataHash?: cbor<DataHash>,
    validFrom?: BigIntString | Auto,
    validUntil?: BigIntString | Auto
};
```

* **`inputs`**

  Describes **external** [inputs](#outerutxo) of the transaction that we would like to include. Note, we **should not** specify UTxO directly related to the user's wallet here, as UTxO management is the responsibility of the wallet. Typically, additional inputs provided directly by the DApp are listed here. If the transaction only implies the use of the user's UTxO, the section can be set to `"auto"`, omitted or contain an empty array.<br><br>

* **`outputs`**

  Describes **explicit** [outputs](#movement) of the transaction, if required. Note, this only concerns those transaction outputs that reflect our intentions. Implicit outputs, such as change, are not our responsibility, as change management is the wallet's duty. If the transaction does not contain explicit outputs (e.g., a delegation transaction), the field can be set to `"auto"`, omitted or contain an empty array.<br><br>

* **`collateralNeeded`**

  Informs the wallet whether it needs to add a collateral input for the transaction or not. The decision on which specific input to use is made by the wallet.<br><br>

* **`certificates`**

  Describes [certificates](#certificate) that should be added to the transaction. It may contain an empty array or be omitted if not required.<br><br>

* **`mintings`**

  Describes [minting](#mint) and burning operations within the current transaction.<br><br>

  >**Note:** if you create a new token, you must add it to `outputs` to specify the destination address. You must also specify the minimum required amount of lovelaces for it there. If you do not provide Inputs for this, the wallet will have to provide them on behalf of the user. If you are burning an existing user token, you are not required to specify `outputs`, as this is part of change management, which should be handled by the wallet. It may contain an empty array or be omitted if not required.

* **`metadata`**

  An object describing a set of [metadata](#metadata) that you want to include in the transaction. It may contain an empty array or be omitted if not required.
  
  Consists of two fields:
  
  * `body`
  
    Describes the directly transmitted set of [metadata](#metadata). This is a mandatory field for this object.
    
    > **Note:** The data provided here are not included in the txBody; they will be included in the auxularyData section of the created transaction. 
  
  * `hash`
  
    Describes an explicitly specified [hash](#hexstring) of the metadata, that will be included in the txBody. This is an optional parameter - it can be set to "auto", or omitted if you want the wallet to calculate the required hash itself.
    
    > **Note:** `hash` is not required to be associated with the provided `body` at the time of **signing**. If `hash` does not refer to `body`, we expect that the DApp providing such a data set plans to replace the `body` just before sending the transaction. This can be useful, for example, for organizing NFT lotteries.
    

* **`additionalSigns`**

  Describes an array of additional signatures [required](#requiredsign) beyond the mandatory ones (associated with UTxO or certificates). It may contain an empty array or be omitted if not required.<br><br>

* **`scriptDataHash`**

  Contains a [CBOR](#cbort)-serialized hex-encoded representation of CDDL ScriptDataHash, necessary for working with smart contracts. Optional.<br><br>

* **`dataHash`**

  Contains a [CBOR](#cbort)-serialized hex-encoded representation of CDDL DataHash, necessary for working with smart contracts. Optional.<br><br>

* **`validFrom`**

  Describes the slot from which the interval begins, during which the transaction can be submitted successfully. Optional.  It can be set to `"auto"` or omitted if not required.<br><br>

* **`validUntil`**

  Describes the slot at which the interval ends, during which the transaction can be submitted successfully. Optional.  It can be set to `"auto"` or omitted if not required.<br><br>

#### `DataSignature`

A structure describing a signature according to the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md).

```ts
type DataSignature = {
    signature: cbor<COSE_Sign1>,
    key: cbor<COSE_Key>,
    address: AddressString
};
```

* **`signature`**

  Contains the digital signature itself as a [CBOR](#cbort)-serialized hex-encoded representation of `CDDL COSE_Sign1`.<br><br>

* **`key`**

  Contains the public key associated with the signature, also in a CBOR-serialized hex-encoded representation of `CDDL COSE_Key` structure with the following headers set:
    * `kty` (1) - must be set to `OKP` (1)
    * `kid` (2) - Optional, if present must be set to the same value as in the `COSE_Sign1` specified above.
    * `alg` (3) - must be set to `EdDSA` (-8)
    * `crv` (-1) - must be set to `Ed25519` (6)
    * `x` (-2) - must be set to the public key bytes of the key used to sign the `Sig_structure`<br><br>

* **`address`**

  Contains the [textual](#addressstring) representation of the address, the key of which was used to form the signature - the wallet should select it independently.<br><br>

### Errors

A simplified error system is proposed, without division into classes, simply describing an enumeration of permissible values. This system can be expanded in the future.
This approach simplifies the support and maintenance of failover code.

```ts
enum Error {
    UnsupportedNetwork,
    DeclinedByUser,
    BadAccountId,
    BadTransactionScript,
    BadTxHash,
    SubmitError,
    Refused
}
```

Let's take a closer look at the errors:

* **`UnsupportedNetwork`**

  The wallet may throw this error if the DApp tries to connect to a network not supported by the wallet.<br><br>

* **`DeclinedByUser`**

  The operation requested was cancelled by the user.<br><br>

* **`BadAccountId`**

  The AccountId to which the DApp is referring in its request is unavailable for some reason.<br><br>

* **`BadTransactionScript`**

  The description of the transaction that the DApp requested from the wallet does not meet the TransactionScript type.<br><br>

* **`BadTxHash`**

  The transaction hash passed in the request refers to a transaction that is unknown to the wallet.<br><br>

* **`SubmitError`**

  The request to send the transaction ended with an error.<br><br>

* **`Refused`**

  The request was rejected by the wallet for some reason. For example - your DApp has been blocked by the user.<br><br>


It is assumed that errors will be transmitted in the form of ErrorMessage:

```ts
type ErrorMessage = {
    error: Error,
    message?: string
}
```

* **`error: Error`**

  The actual "error code".<br><br>

* **`message?: string`**

  Optional free-form accompanying text for ease of debugging. Optional.<br><br>

### Bridge API

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage. A shared, namespaced `cardano` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a `wallet` object with the following methods. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardano.{walletName}.enable()` in order for the dApp to read any information pertaining to the user's wallet with `{walletName}` corresponding to the wallet's namespaced name of its choice.


####  `Code injection`

The interface of the DApp bridge is quite succinct and describes the minimal necessary level of interaction that ensures both parties have sufficient functionality. At the same time, it "protects" them from each other and allows for mutual control of honesty.
There is no main and subordinate here, just two parties, each performing their role.

Each element will be described in detail below.

CIP-0030 suggested implementing an object in the DApp space at the path `window.cardano.{walletName}`, but this does not provide enough flexibility, as we are essentially reserving the entire namespace for the DApp bridge.
In this regard, it is proposed to add another level of nesting - `cip????`, where `????` is the number of the implemented standard.

```ts
window.cardano.{walletName}.cip???? = CardanoBridge;
```

> **Note:** Naturally, this document should specify the CIP number of this CIP, but as long as it is not assigned, "????" will appear.


#### `CardanoBridge`

Wallet connector to DApp.

```ts
type CardanoBridge = {
    cip: number,
    walletName: string,
    walletIcon: URI,
    api: CardanoWalletAPI
}
```

Fields:

* **`cip: number`**

  Contains the number of the CIP implemented by this bridge. Its sole purpose is to simplify integration, especially in a dynamic mode, if the bridge-object was created separately:

  ```js
  window.cardano.{walletName}.{CardanoBridge.cip} = CardanoBridge;
  ```

* **`walletName: string`**

  Serves essentially the same purpose as the `cip` field:

  ```js
  window.cardano.{CardanoBridge.walletName}.{CardanoBridge.cip} = CardanoBridge;
  ```

  > **Note:** The `walletName: string` field is just a bit of abstract sugar. Since the key in the object can be **any string**, there is no sense in separating the wallet name at the injection point and the wallet name inside the bridge-object.
  Additionally, this helps avoid confusion when these names differ and encourages DApp developers not to hardcode wallets, but to read them directly from `window.cardano`, as the name is not a set of eternally static bytes. It can change over time.



* **`walletIcon: URI`**

  Logo or icon of the wallet in a[ browser-friendly format](#uri).<br><br>

* **`api: CardanoWalletAPI`**

  The object that directly implements the wallet API interface. The interface [description](#cardanowalletapi) is below.<br><br>


#### `CardanoWalletAPI`

An interface describing the wallet API. Note that all methods in it are asynchronous and return a `Promise`.

```ts
interface CardanoWalletAPI {
    connect(networkMagic: number, accountId?: AccountId): Promise<{accountId: AccountId, accountEra: AccountEra, stakeKeysCount: number}>;
    disconnect(accountId: AccountId): Promise<void>;
    getBalance(accountId: AccountId): Promise<AssetBundle>;
    getDelegation(accountId: AccountId): Promise<Delegation[]>;
    buildTransaction(tx: TransactionScript, accountId: AccountId): Promise<{ transaction: cbor<Transaction>; txHash: HexString }>;
    signTransaction(txHash: HexString, accountId: AccountId, outerWitnesses?: cbor<WitnessSet>): Promise<cbor<WitnessSet>>;
    submitTransaction(txHash: HexString, accountId: AccountId): Promise<HexString>;
    isTransactionAccepted(txHash: HexString): Promise<number>;
    signData(payload: HexString, accountId: AccountId, withStakeKey: boolean): Promise<DataSignature>;
}
```
<br>

##### `connect(networkMagic: number, accountId?: AccountId): Promise<AccountId>`

* **Description:**
    * A method that initiates the connection of the wallet to the DApp. This is where everything starts. We must pass the `networkMagic` to the wallet, so it knows exactly which network the DApp operates in and can respond correctly.
      At this stage, the wallet should:

        1. Ensure that it is ready to operate;
        2. Notify the user about the connection attempt and ask for their consent;
        3. Decide which account should be used for interaction with the DApp;

      If everything is fine, the user has confirmed the requests and decided on the account to connect, the wallet should return the associated `AccountId`. The DApp should remember this AccountID at least for the duration of the session.
      This approach solves the following problems:

        1. The operation of the DApp now does not depend on what the user is doing in the wallet, as it can directly interact with the necessary account;
        2. The wallet can track which DApps have authorization for which accounts, manage them, and revoke if necessary;

    * **It is mandatory** to call this method before starting operations to obtain the wallet's authorization for further operations;<br><br>

* **Parameters:**
    * `networkMagic: number`

      A number describing the networkMagic of the network in which the DApp operates;

    * `accountId?: AccountId`

      The [identifier of the account](#accountid) to which the DApp wants to connect if it is already known, optional. Note that the wallet is not obliged to connect the DApp to this particular account. Sometimes this may not be possible. However, providing an "incorrect" `accountId` will **not cause an error return** at this stage.<br><br>

* **Return Value:**
    * ` Promise<{ accountId: AccountId, accountEra: AccountEra, stakeKeysCount: number }>`

      An object describing the account to which the wallet has connected the DApp:

        * **`accountId`**

          The [identifier of the account](#accountid) to which the wallet has connected. It does not have to be the same as the `accountId` passed in the parameters. The DApp **must** save this value for use in other API calls.

          A difference in the returned `accountId` from the one passed in the parameters is not an error; it only means that either the requested account is unavailable or the user decided to connect another one.

        * **`accountEra`**

          The [era](#accountera) to which the account's addresses belong.

        * **`stakeKeysCount`**

          The number of staking keys associated with the account.<br><br>


* **Errors([full list](#errors)):**
    * UnsupportedNetwork
    * DeclinedByUser
    * Refused<br><br>

##### `disconnect(accountId: AccountId): Promise<void>`

* **Description:**
    * A method informing the wallet that the DApp wants to disconnect. For example, the user pressed the corresponding button in the DApp interface.
    * The wallet can now revoke the DApp's authorization for the specified account and send an error if the DApp tries to access it without requesting `Connect()` first.
    * The DApp is not obliged to explicitly disconnect from the wallet. This is just an option to improve UX and add the possibility of two-way response to user actions in the DApp.<br><br>

* **Parameters:**
    * `accountId: AccountId`

      The [identifier of the account](#accountid) from which the DApp wants to disconnect.<br><br>

* **Return Value:**

    * `Promise<void>`

      Since this endpoint serves a notification function, there is nothing to return. It's enough to simply wait for the wallet's response. Either way, the session is over.<br><br>

* **Errors([full list](#errors)):**
    * Does not return errors.<br><br>


##### `getBalance(accountId: AccountId): Promise<AssetBundle>`

* **Description:**
    * A method that requests the balance of a specific account from the wallet. Note that this is not a list of UTxOs, but the actual balance. It is assumed that the wallet will form it independently and return it as a single object.
    * The DApp should understand that the data provided might be intentionally incorrect. It's worth noting that even a list of UTxOs wouldn't guarantee that it belongs to a specific wallet.
    * This approach gives the wallet the opportunity to finely tune the exposed balance.
    * Note, the `AssetBundle` type includes not just `ada` but also `nativeTokens`!<br><br>

* **Parameters:**
    * `accountId: AccountId`

      The [identifier of the account](#accountid) whose balance the DApp wants to request. **Must** match the one provided by the wallet upon connection. Otherwise, the wallet is entitled to disconnect with an error.<br><br>

* **Return Value:**
    * `Promise<AssetBundle>`

      The wallet account's balance in the [`AssetBundle`](#assetbundle) format.

        * Wallets with automatic reward withdrawals may add the amount of rewards to the ada amount if they deem it necessary;
        * The wallet is not obliged to disclose the full balance, this applies to both the amount of ada and the set of tokens;
        * The balance is returned as a single value, as if it belonged to one UTxO, without breakdowns into groups of tokens, etc. It has a purely informational role, so the DApp knows what it is dealing with.<br><br>


* **Errors([full list](#errors)):**
    * DeclinedByUser;
    * BadAccountId;
    * Refused;<br><br>


##### `getDelegation(accountId: AccountId): Promise<Delegation[]>`

* **Description:**
    * A method requesting the delegation status of a specific account.
    * Remember, Byron accounts cannot participate in delegation!<br><br>

* **Parameters:**
    * `accountId: AccountId`

      The [identifier of the account](#accountid) whose delegation status the DApp wants to request. **Must** match the one provided by the wallet upon connection. Otherwise, the wallet is entitled to disconnect with an error.<br><br>

* **Return Value:**
    * `Promise<Delegation[]>`

      An array of [`Delegation`](#delegation), containing a list of the latest registered delegations for the specified account. That is, if the wallet is in the process of transitioning from pool "A" to pool "B", the wallet should indicate pool "B" in its response.<br><br>

* **Errors([full list](#errors)):**
    * DeclinedByUser;
    * BadAccountId;
    * Refused;<br><br>


##### `buildTransaction(tx: TransactionScript, accountId: AccountId): Promise<{ transaction: cbor<Transaction>; txHash: HexString }>`

* **Description:**
    * A method that allows the DApp to request the wallet to assemble a transaction with specified parameters;

      At this stage:
        * The DApp can compare `txHash` and the hash of the transmitted transaction to ensure they are identical, if needed;
        * The DApp can check the transaction inputs and validate that such UTxOs exist, if needed;
        * The DApp can review the other components of the transaction to ensure they match what it requested, if needed;
        * The DApp can generate the necessary signatures from its side, if needed;
        * The wallet should create a transaction that would satisfy all the requirements in the submitted request, if possible;
        * The wallet should **save the created transaction**, as it will be needed later;<br><br>

* **Parameters:**
    * `tx: TransactionScript`

      An object of type [`TransactionScript`](#transactionscript), describing the desired action;

    * `accountId: AccountId`

      The [identifier of the account](#accountid) for which the DApp is requesting the transaction. **Must** match the one provided by the wallet upon connection. Otherwise, the wallet is entitled to disconnect with an error.<br><br>

* **Return Value:**
    * `Promise<{ transaction: cbor<Transaction>; txHash: HexString }>`

      An object containing fields:
        * `transaction: cbor<Transaction>` - [CBOR](#cbort)-serialized hex-encoded representation of `CDDL Transaction`;
        * `txHash: HexString` - a string containing the [hash](#hexstring) of the created transaction;<br><br>


* **Errors([full list](#errors)):**
    * DeclinedByUser;
    * BadAccountId;
    * BadTransactionScript;
    * Refused;<br><br>

##### `signTransaction(txHash: HexString, accountId: AccountId, outerWitnesses?: cbor<WitnessSet>): Promise<cbor<WitnessSet>>`

* **Description:**
    * A method that allows the DApp to request the wallet to sign a previously assembled transaction;

      At this stage:
        * The DApp can pass its signatures to the wallet, if necessary, to be included in the transaction;
        * The wallet should sign everything in the transaction that depends on it;        
          <br>

      >**Note:** The method's parameters do not include the transaction itself, but only its hash, implying that the transaction is saved in the wallet. This way, we protect the user from the transaction being substituted by the DApp, assuming both parties already have an identical copy of it.

* **Parameters:**
    * `txHash: HexString`

      The [hash](#hexstring) of the transaction for which signing is requested;

    * `accountId: AccountId`

      The [identifier of the account](#accountid) for which the DApp is requesting the transaction signing. **Must** match the one provided by the wallet upon connection. Otherwise, the wallet is entitled to disconnect with an error.

    * `outerWitnesses?: cbor<WitnessSet>`

      [CBOR](#cbort)-serialized hex-encoded representation of `CDDL WitnessSet`, containing signatures generated by the DApp side, if necessary. This is an optional parameter.<br><br>

* **Return Value:**
    * `Promise<cbor<WitnessSet>>`

      [CBOR](#cbort)-serialized hex-encoded representation of `CDDL WitnessSet`, containing the set of signatures generated by the wallet on its side, excluding signatures passed to it by the DApp.
      Now both parties have:

        * The formed transaction;
        * The set of signatures from the DApp side;
        * The set of signatures from the wallet side;

      Each party is now in a position to independently assemble a transaction ready for submitting.

      This approach allows DApps to solve the problem of scaling throughput, as technically, they can now use their own gateways to send transactions, not relying on the wallet's mempool and not overloading it.

      This will allow DApps to guarantee users a better UX and be independent of wallet developers.

      Wallets, in this scenario, receive a reduction in load.

      However, of course, the option to send the transaction through the wallet will still remain.<br><br>


* **Errors([full list](#errors)):**
    * DeclinedByUser;
    * BadAccountId;
    * BadTxHash;
    * Refused;<br><br>



##### `submitTransaction(txHash: HexString, accountId: AccountId): Promise<HexString>`

* **Description:**
    * A method that allows the DApp to request the wallet to send a previously assembled and signed transaction;
      <br>

      >**Note:** The method's parameters do not include the transaction itself, but only its hash, implying that the transaction is saved in the wallet. This way, we protect the user from the transaction being substituted by the DApp, assuming both parties already have an identical copy of it.

* **Parameters:**
    * `txHash: HexString`

      The [hash](#hexstring) of the transaction for which sending is requested;

    * `accountId: AccountId`

      The [identifier of the account](#accountid) for which the DApp is requesting the transaction submitting. **Must** match the one provided by the wallet upon connection. Otherwise, the wallet is entitled to disconnect with an error.<br><br>

* **Return Value:**
    * `Promise<HexString>`

      The [hash](#hexstring) of the sent transaction, if the sending was successful. It should match the hash passed as an argument.<br><br>

* **Errors([full list](#errors)):**
    * DeclinedByUser;
    * BadTxHash;
    * SubmitError;
    * Refused;<br><br>


##### `isTransactionAccepted(txHash: HexString): Promise<number>`

* **Description:**
    * A method that allows the DApp to request the wallet for the status of a transaction by its hash;

      If the hash of the requested transaction does not belong to the list of wallet transactions, the wallet has the right to return an error, or -1;<br><br>

* **Parameters:**
    * `txHash: HexString`

      The [hash](#hexstring) of the transaction for which the status is requested;<br><br>

* **Return Value:**
    * `Promise<number>`

      A value describing the `depth` of the transaction in the blockchain, i.e., the number of blocks on top of the block in which it was added:
        * `-1`, if the transaction is still in the mempool;
        * `0`, if the current block is the block in which the requested transaction was added;
        * `n` in all other cases;<br><br>

* **Errors([full list](#errors)):**
    * BadTxHash;
    * Refused;<br><br>


##### `signData(payload: HexString, accountId: AccountId, withStakeKey: boolean): Promise<DataSignature>`

* **Description:**
  This endpoint utilizes the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md) for standardization/safety reasons. It allows the dApp to request the user to sign a payload conforming to said spec. The user's consent should be requested and the message to sign shown to the user. The payment key from `addr` will be used for base, enterprise and pointer addresses to determine the EdDSA25519 key used. The staking key will be used for reward addresses.

  This key will be used to sign the `COSE_Sign1`'s `Sig_structure` with the following headers set:

    * `alg` (1) - must be set to `EdDSA` (-8)
    * `kid` (4) - Optional, if present must be set to the same value as in the `COSE_key` specified below. It is recommended to be set to the same value as in the `"address"` header.
    * `"address"` - must be set to the raw binary bytes of the address as per the binary spec, without the CBOR binary wrapper tag<br><br>

* **Parameters:**
    * `payload: HexString`

      A [hexadecimal](#hexstring) string describing the byte array that needs to be signed.
      The payload is not hashed and no `external_aad` is used.

    * `accountId: AccountId`

      The [identifier of the account](#accountid) for which the DApp is requesting the payload signing. **Must** match the one provided by the wallet upon connection. Otherwise, the wallet is entitled to disconnect with an error.

    * `withStakeKey: boolean`
      Indicates whether the wallet should use one of the `stakeKey` for signing. If `false` is passed, the wallet should select a `paymentKey` to sign the `payload`.<br><br>

* **Return Value:**
    * `Promise<DataSignature>`

      An object containing the [signature, public key, and associated address](#datasignature).

      Note that in this case, the address is chosen by the wallet, not the DApp.<br><br>

* **Errors([full list](#errors)):**
    * DeclinedByUser;
    * BadAccountId;
    * Refused;<br><br>


### Example

```js
// We will work in the testnet
const networkMagic = 1;
const walletName = 'Some awesome cardano wallet with long name';

// Minimal function for working with transactions, without special checks
async function performTransaction(txScript, networkMagic, walletName) {
    // select the wallet
    const cBridge  = window.cardano[walletName].cipNNNN;
    try {
        // Connect to the wallet, create a transaction, request signing, then submit it and close the session
        const accountData = await cBridge.connect(networkMagic);
        const builtTx = await cBridge.buildTransaction(txScript, accountData.accountId);
        const signedTx = await cBridge.signTransaction(builtTx.txHash, accountData.accountId);
        await cBridge.submitTransaction(builtTx.txHash, accountData.accountId);
        await cBridge.disconnect(accountData.accountId);
    } catch (error) {
        // Error handling
        console.error(error);
    }
}
```
```js
// Here is an example of a transaction script that sends the user 5 ada from the Dapp account.
// Note, the output is the same amount as the input, assuming that the user, not the DApp, should cover the commission
let txScript =  {
    inputs: [{
        hash: "1c32527089b7a226021c6829518d7284283e3c91b9820362f0c5aed0ad5e5074",
        index: 0,
        value: {
            lovelaces: 5000000
        }
    }],
    outputs: [{
        value: {
            lovelaces: 5000000
        },
        address: "auto"
    }]
};
performTransaction(txScript, networkMagic, walletName);
```
```js
// Now let's send a little funds from the user's wallet to some address:
txScript = {
    outputs:[{
        address: "addr_test1qpy486p7jhq933kay7rf78jz2j6k5ya7u95nnnjetgj9r02dp276p7j8023vmum9wu8gp7q54f3rjke45j0klk3pmwvsgyx4n7",
        value: {
            lovelaces: 1000000
        }
    }]
};
performTransaction(txScript, networkMagic, walletName);
```
```js
// And ask the user's wallet to delegate:
txScript = {
    certificates: [{
        type: "stakeDelegation",
        stakeKeyId: 0,
        poolHash: "660f2b816e90e4e826daebf33357d76ab89414f88d57dd7d9f7898fe",
    }]
};
performTransaction(txScript, networkMagic, walletName);
```
Of course, we are not obliged to connect and disconnect every time, and this is just an example. Ideally, we should connect at the beginning of the session, work, and optionally finish it sometime later, instead of doing a full cycle on each transaction.

At the same time, we are not required to use low-level libraries to solve simple tasks. It's sufficient to just generate JSONs.

For more complex tasks related to working with smart contracts, the DApp should use more low-level solutions for generating redeemers and dataHashes. However, this will be part of the DApp's direct logic, necessary for its operation, rather than redundant logic that mimics a full-fledged wallet with coinSelection algorithms, etc. In other words, the complexity of the code will simply correspond to the complexity of the task.

## Rationale: how does this CIP achieve its goals?

This CIP addresses the issues described in the `Motivation` section:

1. **Complexity in Writing Client-Side Logic for DApps**: The minimal amount of code required for DApp to interact with the wallet has been dramatically reduced.<br><br>

2. **Integration Difficulties**: The interaction between DApp and wallet is now easily mapped onto the logic of the wallet's interaction with the end user. Declarative rather than imperative.<br><br>

3. **Privacy Issues**: The wallet is no longer obliged to disclose all information and decides for itself what data can be published and what cannot. Now it is responsible for managing UTxO and other crucial aspects, as it should be.<br><br>

4. **Current Role of Wallets**: The wallet now acts as a wallet, not a "submit endpoint," and the DApp acts as its client, not a substitute.<br><br>

5. **Scalable Complexity**: The complexity of the code on the DApp side now precisely matches the complexity of the tasks it solves. Nothing superfluous.<br><br>

6. **Reducing Dependencies**: DApp developers are no longer required to use libraries for working with Cardano CDDL to interact with the wallet, if there is no need for them. The pipeline has become smooth and sequential, reducing the number of failure points.<br><br>

7. **Lack of abstraction**: DApps no longer need to adapt to every low-level change in Cardano. They now have an **abstraction layer** that solves this problem once and for all.<br><br>

8. **Security**: The creation of transactions is now fully controlled by the user's wallet and does not leave its confines. Users can be confident that third parties are not involved in managing their funds.<br><br>

9. **Trustful system**: Users no longer have to trust DApps and can safely connect their wallets to new applications without the risk of misuse on their part.<br><br>


## Path to Active

### Acceptance Criteria

- [] The interface is implemented and supported by various wallet providers.
- [] The interface is used by DApps to interact with wallet providers.

### Implementation Plan

- [] Provide some reference implementation of wallet providers
- [] Provide some reference implementation of the dapp connector

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

