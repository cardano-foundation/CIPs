---
CIP: ?
Title: Authenticated Web3 HTTP requests
Category: Tools
Status: Proposed
Authors:
    - Juan Salvador Magán Valero <jmaganvalero@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2022-12-27
License: CC-BY-4.0
---

# CIP-XXXX: Authenticated Web3 HTTP requests

## Abstract

The cardano wallets have the ability to sign arbitrary pieces of data as we can see in the [Message signing CIP-0008](/CIP-0008/README.md). All wallets implement the method ```api.signData(addr: Address, payload: Bytes): Promise<DataSignature>``` defined in [Cardano dApp-Wallet Web Bridge CIP-0030](/CIP-0030/README.md).

An important use case for web3 sites is calling HTTP endpoints using authenticated requests signed by the private keys of the users' wallets. In this way, the servers can perform actions using onchain and offchain data. 


## Motivation

dApps generate arbritary payloads as byte arrays. These payloads are signed and included in the protected headers of the signatures. The wallets are responsible for showing the payload data to the user, who will proceed to sign or reject the payload. It's a common practice to encode a string or a JSON string but there isn't any standard for the way to construct and to show this data.

The current implementations for web3 applications use static strings. This is dangerous because if a bad actor intercepts the signed message then it can be used in a replay attack by the bad actor. That's why it is very important to produce a dynamic payload rather a static string.

Another problem with the current approach is how the wallets show the information contained in the payload. The payload is a enconded byte array and it could contain anything. If Alice want to call an endpoint and Bob has the ability to change the message before Alice gets it. Alice must be notified somehow that she is signing a potentially malicious payload. A simple hex-encoded representation of the payload isn't enough to ensure a safe interaction.

## Specification

This specification involves multiple parties. We split this specification in three parts: server processing, payload structure and wallet specification.

### Requirement Levels 

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

### Payload structure

The payload MUST be encoded as a JSON string. JSON strings are semi-structured data that are human-readable. So that with a straightforward decoding into text, it will be understandable for the readers. This feature also allows the users to debug it in an easy manner, for example, with the browser debugger tools.

The content of the payload will be included in the protected header of the COSESign1 signature, hence the content effects directly the behavior and security of the system. The payload MUST have the following fields: 

1. The field ```url``` MUST contain the full path to the endpoint, where the payload will be processed.

2. Sometimes, the endpoint ```url``` field is not enough to determine its purpose. The user should understand perfectly the objective of the payload which he or she is signing. That's why the payload MUST contain an ```action``` field with a descriptive text containing the purpose of the payload. 

3. The payload MUST include a UNIX timestamp. The ```timestamp``` field is used as a nonce and a mark for the payload expiration. This field is very imporant in case the payload is compromised.

Additional fields MAY be included in the payload. Depending on the process, it could be useful to include some aditional fields in the protected header of the signature. For example, the email information should be included in the protected header in a registration request. In that way, this payload can be used only to register that specific email and it can not be tampered. 

```JSON
{
    "url": "http://example.com/signup",
    "action": "Sign up",
    "timestamp": 1673261248,
    ["email": "email@example.com"] <- Optional
}
```

### Wallet specification

The wallets can improve the overall security implementing the following guidelines. We RECOMMEND to show in a structured way the payload information for shake of clarity. This information should be well understanded by the users before the payload is signed.  

The ```url``` field provides information about the hostname of the application. This hostname MUST be included in the wallet allow list. If a known domain A tries to sign a payload for an unknown domain B, you will be prompted with permission popup making more obvious the cross-domain interaction. When possible, the wallet SHOULD warn the user if a payload is for a different domain.

The wallet SHOULD update the ```timestamp``` field to the current time just before the signature. This field ideally should match the moment just before the signature, thereby the server recieves the more updated payload possible. 

### Server processing

The server has ultimate responsibility of processing correctly the requests. We use the content to validate the payload. The request will be processed with the following steps:

1. The server MUST check the action and the endpoint included in the request. Each route to an endpoint MUST have an associated action and a URL. The first step is to check that they match with the parameterized action.

2. The server MUST check the expiration of the payload. The expiration SHOULD be enough to give time to the user to introduce the wallet password but it SHOULD NOT be too long, we RECOMMEND not more than 5 minutes.

3. The server MUST validate the COSESign1 signature and check that the address inside the protected map of the signature corresponds to the public key in the COSEKey. 

Additionally the server COULD extract the payload content and pass it through the server logic.

## Rationale: how does this CIP achieve its goals?

This specification provides the general guidelines and necessary recommendations for performing secure authenticated web3 requests in the Cardano ecosystem. It covers the two main desired characteristics for a secure payload: It must expire and it must be non-static.

Another important aspect for security is how wallets process the payload. They can improve the security using the data inside the payload to warn the users about possible malicious interactions. This specification emphasizes the importance of informing users clearly about the purpose of the payloads and how wallets can use the URL field to apply allow-lists and/or cross-domain policies.

Finally, it establishes the requirements and recommendations for server side processing. The server must also ensure the validity of the signature and the payload, as well as of its purpose in order to accomplish the authentication. 


### Reference implementation

* [jmagan/passport-cardano-web3](https://github.com/jmagan/passport-cardano-web3)
* [jmagan/cardano-express-web3-skeleton](https://github.com/jmagan/cardano-express-web3-skeleton)
## Path to Active

### Acceptance Criteria

- [X] At least one library should implement this authentication method.
- [ ] The 80% users should have wallets implementing the following requirements:
    1. It MUST detect when the payload is formatted using this specification.
    2. The information contained in the payload MUST be parsed and formatted in the signing pop-up.
    3. The wallet SHOULD update the timestamp just before the payload is signed.
    4. The wallet MUST detect if the URL is in the allow list.
    5. The wallet SHOULD warn the user against cross-domain requests.
- [ ] A detailed documentation about web3 standards should be published. This documentation will include this standard and further best practices for web3 technologies.

### Implementation Plan

- [X] Create a library for processing payload according to this specification.
- [ ] Open a conversation about this specification and its possible improvements.
- [ ] Talk about further web3 standards and new specifications. 
- [ ] Write the documentation for web3 developers.

## Copyright

This CIP is licensed under [CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
