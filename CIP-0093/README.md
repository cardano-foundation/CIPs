---
CIP: 93
Title: Authenticated Web3 HTTP requests
Category: Tools
Status: Proposed
Authors:
    - Juan Salvador Magán Valero <jmaganvalero@gmail.com>
    - Óscar Nájera <hi@arsmagna.xyz>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/442
Created: 2022-12-27
License: CC-BY-4.0
---

## Abstract

The proposed Cardano Improvement Proposal (CIP) outlines a conventional structure for data payloads that are signed by wallets, which can be used by decentralized application (dApp) servers to authenticate user requests. By leveraging the Cardano blockchain as an identity provider, dApp servers can securely and trustlessly verify user identities without relying on centralized servers or third-party services. This CIP aims to provide a standard approach for implementing wallet signature authentication in dApps, improving the security and reliability of user interactions with decentralized systems.

## Motivation: Why is this CIP necessary?

The cardano wallets have the ability to sign arbitrary piece of data as we can see in the [Message signing CIP-0008](./CIP-0008/README.md). All wallets implement the method ```api.signData(addr: Address, payload: Bytes): Promise<DataSignature>``` defined in [Cardano dApp-Wallet Web Bridge CIP-0030](./CIP-0030/README.md).

dApps generate arbitrary payloads as byte arrays. These payloads are signed and included in the protected headers of the signatures. The wallets are responsible for showing the payload data to the user, who will proceed to sign or reject the payload. It's a common practice to encode a string or a JSON string but there isn't any standard for the way to construct and to show this data.

The current implementations for web3 applications use static strings. This is dangerous because if a bad actor intercepts the signed message then it can be used in a replay attack by the bad actor. That's why it is very important to produce a dynamic payload rather a static string.

Another problem with the current approach is how the wallets show the information contained in the payload. The payload is a encoded byte array and it could contain anything. If Alice want to call an endpoint and Bob has the ability to change the message before Alice gets it. Alice must be notified somehow that she is signing a potentially malicious payload. A simple hex-encoded representation of the payload isn't enough to ensure a safe interaction.

## Specification

This specification involves multiple parties: Wallet/Client, dApp Server and Blockchain. 

1. **Wallet/Client**: The Wallet/Client is responsible for managing the user's cryptographic keys. Anyone can create a wallet using the CIP-0030 API interface, but it may produce invalid or malicious data sent to the dApp. This CIP aims to validate the ownership and veracity of the data provided by wallets. Additionally, it establishes guidelines for mitigating common wallet attacks, improving security for user interaction.

2. **dApp Server**: The dApp Server represents the server-side infrastructure that supports decentralized applications (dApps). It communicates with the blockchain to retrieve stored data and validate wallet status. It must enforce minimum payload requirements to ensure authenticity and protect users from malicious actors.

3. **Blockchain**: The Blockchain is the underlying distributed ledger technology that forms the foundation of decentralized systems. It is a decentralized and immutable ledger that securely records all transactions and data in a chronological and transparent manner. The Blockchain can be utilized for authentication, providing user identity, and for authorization, tracking user history and current status.

```
+-----------+               +---------------+              +----------------+
|  Wallet/  |               |  dApp Server  |              |   Blockchain   |
|  Client   |               |               |              |                |
+-----------+               +---------------+              +----------------+
      |                              |                                |
      |                              |                                |
      | 1. Request nonce             | Issue and bind nonce to action |
      |----------------------------->+------------+                   |
      |             Create payload   |            |                   |
      |<-----------------------------+<-----------+                   |
      |                              |                                |
      | 2. Request signature         |                                |
      |------------+                 |                                |
      |            |                 |                                |
      |<-----------+                 |                                |
      |                              |                                |
      | 3. Send signed payload       |                                |
      |----------------------------->|                                |
      |                              | 4. Verify signature            |
      |                              |------------+                   |
      |                              |            |                   |
      |                              |<-----------+                   |
      |                              |                                |
      |                              | 5. Check blockchain (optional) |
      |                              |------------------------------->|
      |                              |<-------------------------------|
      | 6. Return session token      |                                |
      |<-----------------------------|                                |
```

### Requirement Levels 

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

### Payload structure

The payload MUST be encoded as a JSON string. JSON strings are semi-structured data that are human-readable. So that with a straightforward decoding into text, it will be understandable for the readers. This feature also allows the users to debug it in an easy manner, for example, with the browser debugger tools.

The content of the payload will be included in the protected header of the COSESign1 signature, hence the content effects directly the behavior and security of the system. The payload MUST have the following fields: 

1. The field `uri` MUST contain the full path to the endpoint, where the payload will be processed.

2. Sometimes, the endpoint `uri` field is not enough to determine its purpose. The user should understand perfectly the objective of the payload which he or she is signing. That's why the payload MUST contain an `action` field with a descriptive text containing the purpose of the payload. For example, if someone calls the endpoint `/users` without an action field, they can create or delete users. However, by including the action field in the payload, it not only provides additional clarity but also effectively limits the scope of the payload.

3. In order to improve globalization, the payload MAY include an `actionText` field that represents the action in the locale of the user. When present, the wallet MUST display this field to the user. By including the `actionText` field, the wallet facilitates the processing of the action field, eliminating the need for the server to be aware of the user's locale and the possible variants of the action text.

4. The server MUST issue a `nonce` bound to a specific `action` value before the signing request is made. The nonce-issuance response MUST include the expected `action`. The wallet MUST echo this `action` value unchanged in the signed payload. The server MUST reject any payload whose signed `action` does not match the value it committed to at nonce-issuance time, regardless of whether the signature is otherwise valid.

This gives the `action` field a dual role: it is the human-readable display string shown to the user by the wallet (per the wallet specification), and it is also the server's tamper-evident commitment to purpose, checked cryptographically via the signature rather than by convention alone.

5. The payload MUST include either a UNIX `timestamp` or a `slot` number. The `slot` field represents a specific time in the blockchain and serves as a reference for synchronization between the client and the server. The `timestamp` or `slot` number is also used as a nonce and serves as an indicator for payload expiration in case the payload is compromised.

Additional fields MAY be included in the payload, and these fields can be string fields or objects. Depending on the specific process or use case, including additional fields in the protected header of the signature can provide valuable functionality and security enhancements. For example, in a registration request, it may be useful to include the email information as an additional field in the protected header. By doing so, the payload can be uniquely associated with that specific email, ensuring its integrity and preventing tampering.

#### JSON Schema
```JSON
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "uri": {
      "type": "string",
      "format": "uri"
    },
    "action": {
      "type": "string"
    },
    "nonce": { "type": "string" },
    "actionText": {
      "type": "string"
    },
    "timestamp": {
      "anyOf": [
        {
          "type": "integer"
        },
        { "type": "string", "pattern": "^\\d+$" }
      ]
    },
    "slot": {
      "anyOf": [
        {
          "type": "integer"
        },
        { "type": "string", "pattern": "^\\d+$" }
      ]
    }
  },
  "required": ["uri", "action", "nonce"],
  "oneOf": [{ "required": ["timestamp"] }, { "required": ["slot"] }],
  "additionalProperties": {
    "type": ["string", "object"]
  }
}
```
#### Minimum payload:

```JSON
{
    "uri": "http://example.com/signin",
    "action": "Sign in",
    "nonce": "aaaaaaaaaaaaaa"
    "timestamp": 1673261248,
}
```
#### Sign up payload examples:
```JSON
{
    "uri": "http://example.com/signup",
    "action": "Sign up",
    "nonce": "aaaaaaaaaaaaaa"
    "timestamp": "1673261248",
    "email": "email@example.com"
}

{
    "uri": "http://example.com/signup",
    "action": "SIGN_UP",
    "nonce": "aaaaaaaaaaaaaa"
    "actionText": "Registrar",
    "slot": 94941399
}
```

### Wallet specification

The wallets can improve the overall security implementing the following guidelines. We RECOMMEND to show in a structured way the payload information for sake of clarity. This information should be well understood by the users before the payload is signed.  

The `uri` field provides information about the hostname of the application. The wallet allow-list for `signData` requests SHOULD be seeded from the origin captured during the CIP-0030 `api.enable()` call that established the current dApp connection. If the `uri` field's hostname does not match the origin of the active CIP-0030 connection, the wallet MUST refuse the signing request, not merely display a warning. This converts a skippable advisory into a hard check, using information the wallet already holds from the existing handshake — no new infrastructure is required.

The wallet SHOULD update the `timestamp` field to the current time just before the signature. This field ideally should match the moment just before the signature such that the server receives fresh payload. 

Wallets SHOULD maintain a recognized vocabulary of standard `action` values, at minimum: `"Sign in"`, `"Sign up"`, `"Reauthenticate"`. When the `action` field matches a recognized value, the wallet MAY render a standard, calm signing prompt. When the `action` field does not match any recognized value, the wallet MUST render a visually distinct, higher-friction warning — for example, a differently colored prompt and an explicit notice such as "This is not a standard sign-in request." The unrecognized-action state MUST be visually distinguishable from the standard signing prompt; it MUST NOT be rendered identically to a routine login.

### dApp Server processing

The server has ultimate responsibility of processing correctly the requests. The server MUST process a signed payload request in the following order, rejecting on the first failure:

1. Parse the `COSESign1` structure (CIP-0008) and recover the protected headers
   and signed payload bytes.
2. Recover the public key from the accompanying `COSEKey` and recompute the
   Cardano address. Confirm the recovered address matches the address type
   expected by this endpoint (see Section 4 — Address Selection).
3. Confirm the `nonce` is known to this server, has not been used before, and
   was issued for the address being authenticated.
4. Confirm the `timestamp` or `slot` falls within the server's acceptable
   freshness window. The server SHOULD NOT accept payloads older than 5 minutes
   (300 seconds). Services with elevated security requirements MAY reduce this
   window.
5. Confirm the `uri` matches the endpoint receiving this request, including
   hostname.
6. Confirm the signed `action` matches the value committed at nonce-issuance
   time for this nonce (per Amendment 1 above).
7. Verify the `COSESign1` signature against the recovered public key.
8. On success: mark the nonce consumed, issue a session credential, and write
   an audit record (see below).

**Step ordering rationale:** Cheap structural checks (steps 1–2) precede
database checks (step 3) which precede cryptographic verification (step 7).
This ordering minimizes resource expenditure on malformed or expired requests.

#### Audit logging

On successful authentication, the server SHOULD retain the full verified
payload — including `uri`, `action`, `timestamp`/`slot`, and any additional
fields — as its authentication audit record, alongside the recovered address
and the time of verification. Because the payload is signed, this record
constitutes tamper-evident proof of which address authenticated, for which
declared purpose, at which time, against which endpoint. A leak of this audit
log does not compromise future authentications: reproducing a past valid
signature is not sufficient to construct a new one.

> **Rationale:** The structured payload makes a materially richer audit record
> possible compared to a bare nonce. Making this explicit in the specification
> encourages implementations to retain it, which supports both security
> incident analysis and compliance use cases.

### Address Selection

In CIP-0030's `signData` the COSE_Sign1 protected headers include the address used, and the accompanying COSE_Key allows verification without prior knowledge of the key. The cryptographic address binding is therefore established by the COSE structure, not by the payload. Any address field in the JSON payload serves only to inform the wallet's display — it is not what proves the binding.

**For general sign-in use cases,** the stake (reward) address is RECOMMENDED as the default. It remains stable across the payment-address rotation wallets perform internally, and most wallets track account identity at the stake-key level. Using the stake address as the stable identity anchor avoids inconsistency when the same user authenticates from a wallet that has rotated its active payment address since a previous session.

**Services MAY request a specific payment address instead** when the use case requires it. Legitimate reasons include:

- Proving control of a specific UTXO-holding address, where the stake-level
  identity is not what is being attested to.
- Authenticating as a particular sub-account in a multi-account wallet, where
  different payment addresses serve deliberately separated purposes.
- Governance or DRep key signing under CIP-0095, which introduces a third key
  type (DRep key) outside the payment/stake pair.

Whatever address type a given endpoint accepts, the server MUST be consistent about its expectation and SHOULD document it. Silently accepting whichever address type the client supplies makes server-side identity resolution fragile.

> **Rationale:** Neither mandating stake addresses nor leaving the choice
> entirely unspecified serves implementors well. A stated default with explicit
> carve-outs for legitimate deviations gives services a clear starting point
> while preserving flexibility for advanced use cases.

## Rationale: How does this CIP achieve its goals?

CIP-0008 enhances authentication by enabling individuals to prove ownership of addresses, identities, and off-chain data through message signing. It provides a reliable means of authentication by allowing individuals to attach a public key to their data and sign messages associated with that data, thereby establishing ownership and ensuring the integrity of the authentication process.

Additionally, This specification provides the general guidelines and necessary recommendations for performing secure authenticated web3 requests in the Cardano ecosystem. It covers the two main desired characteristics for a secure payload: It must expire and it must be non-static. Moreover, the signature method proposed in this CIP does not require users to spend funds in a transaction, which further lowers the cost and barriers to entry for users.

Another important aspect for security is how wallets process the payload. They can improve the security using the data inside the payload to warn the users about possible malicious interactions. This specification emphasizes the importance of informing users clearly about the purpose of the payloads and how wallets can use the URI field to apply allow-lists and/or cross-domain policies. It establishes also the requirements and recommendations for server side processing. The server must also ensure the validity of the signature and the payload, as well as of its purpose in order to accomplish the authentication. 

In addition to the aforementioned aspects, this CIP also aims to promote decentralization and enhance security and privacy by enabling users to sign and verify transactions without relying on external servers or third parties. By allowing users to create and sign their own payloads, this specification reduces the dependency on centralized authorities and enhances the security and privacy of the transactions.

### Alternative implementations

During discussions about this specification, the possibility of modifying CIP-0008 to incorporate the standards defined here was considered. However, a thorough evaluation revealed that this approach would require extensive modifications to CIP-0008 and CIP-0030, leading to significant changes in the Cardano wallet API. Moreover, it would result in a lengthy waiting period for browser wallet developers to implement the necessary requirements. This could potentially bypass important security measures outlined in this CIP, such as the requirement for human readability.

While this alternative approach brings advantages, such as defining the payload in CBOR, which aligns well with Cardano, it also presents challenges. JSON and CBOR offer different levels of expressiveness, and the choice between the two depends on the specific needs of the application. JSON provides a more flexible and widely supported data format, whereas CBOR offers a more compact and efficient representation, particularly beneficial when working with the blockchain.

Considering these factors, it was concluded that deploying this standard as it currently stands, while coexisting with a future version that allows users to choose between JSON and CBOR payloads, would be the most practical approach. This would provide sufficient time for modifying CIP-0008 and CIP-0030, enabling browser wallet developers to fulfill the requirements for human readability and make necessary adjustments to the wallet API. Consequently, a version 3 of this CIP can be introduced, incorporating COSESign and CBOR, accommodating both realms, and ensuring broad support.

### Common usage

The payload signature ensures wallet ownership without incurring transaction fees. However, requiring the user to enter their spending password for every authenticated request can be inconvenient for the user experience. To address this, it is recommended to restrict the use of the payload signature to only important requests such as login, sign up, or other critical operations depending on the dApp requirements.

A common practice is to request the user's signature for the login process, and once authenticated, the dApp can issue a session token, such as a JSON Web Token (JWT), to manage the session. By implementing this approach, future non-critical requests can be performed using standard web 2.0 methods, eliminating the need to enter the spending password for each step. This significantly enhances the usability of the application, providing a smoother user experience.


### Version history

| Version | Date       | Author                     | Rationale               |
|:-------:|------------|----------------------------|-------------------------|
|   v1    | 2022-12-27 | Juan Salvador Magán Valero | Initial release         |
|   v2    | 2026-09-01 | Óscar Nájera               | Strengthen Payload Specification & server verification |


### Reference implementation

* [jmagan/passport-cardano-web3](https://github.com/jmagan/passport-cardano-web3)
* [jmagan/cardano-express-web3-skeleton](https://github.com/jmagan/cardano-express-web3-skeleton)
* [jmagan/cardano-nextjs-web3-skeleton](https://github.com/jmagan/cardano-nextjs-web3-skeleton)

## Path to Active

### Acceptance Criteria

- [X] At least one library should implement this authentication method.
- [ ] The 80% users should have wallets implementing the following requirements:
    1. It MUST detect when the payload is formatted using this specification.
    2. The information contained in the payload MUST be parsed and formatted in the signing pop-up.
    3. The wallet SHOULD update the timestamp just before the payload is signed.
    4. The wallet MUST detect if the URI is in the allow list.
    5. The wallet SHOULD warn the user against cross-domain requests.
- [ ] A detailed documentation about web3 standards should be published. This documentation will include this standard and further best practices for web3 technologies.

### Implementation Plan

- [X] Create a library for processing payload according to this specification.
- [X] Open a conversation about this specification and its possible improvements.
- [X] Talk about further web3 standards and new specifications. 
- [ ] Write the documentation for web3 developers.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
