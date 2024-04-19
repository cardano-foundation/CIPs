---
CIP: 83
Title: Encrypted Transaction message/comment metadata (Addendum to CIP-0020)
Status: Active
Category: Metadata
Authors:
    - Martin Lang <martin@martinlang.at>
    - Ola Ahlman <ola@ahlnet.nu>
    - Andrew Westberg <andrewwestberg@gmail.com>
    - Adam Dean <adam@crypto2099.io>
Implementors:
    - Cardano Explorer <https://cexplorer.io>
    - StakePoolOperator Scripts <https://github.com/gitmachtl/scripts>
    - AdaStat.net <https://adastat.net>
    - Eternl Wallet <https://eternl.io>
    - CNTools <https://cardano-community.github.io/guild-operators/#/Scripts/cntools>
    - JorManager <https://bitbucket.org/muamw10/jormanager/>
    - Cardanoscan.io <https://cardanoscan.io>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/394
Created: 2022-12-08
License: CC-BY-4.0
---


## Abstract

This CIP is an addendum to the original [CIP-0020](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0020), which is active since mid 2021 and widely used across many entities.
It describes the JSON schema to add encrypted messages/comments/memos as transaction metadata. It is fully backwards compatible and requires no changes in existing tools, explorers, wallets. 
Tools/Wallets that do not have an implementation to decrypt this format will just show the encrypted base64 as the message, but it will not break any existing processes.

## Motivation: why is this CIP necessary?

### Current state of transaction messages

Transaction messages/comments/memos via CIP-0020 are widely used across the Cardano Blockchain. For example DEXs are using it to comment there payouts to the customers.
Individual users are using it to send funds across the network to other users with attached information about it. Users are buying goods and pay directly in ADA, attaching payment informations
via an added message.

Theses and many other usecases are actively happening on the blockchain right now and are a valuable addition to the core functions.

### What is the issue with the current implementation?

Metadata is attached as a CBOR bytearray in the auxiliary dataset of a transaction. So the encoding is just done from UTF8-Text to Hex-Code/Bytes and after that it is sent in plaintext over the network/blockchain.
To seek further adoption of blockchain usage, privacy features are a must in the future. Having cleartext information in a TCP packet might not be an issue for many things, but it is an issue if you wanna convince 
users to use the blockchain and their transaction feature like users using it now with bank transfers.

It is easy for 3rd-party entities like Internet Service Providers, Datacenters or basically any Man-In-The-Middle to collect data that is sent in cleartext. 
Data such as bank-account-numbers, email-addresses, telephone numbers, etc. which are parts of transaction messages.

### What benefits/features would this CIP have on transaction messages?

As pointed out above, everyone that is having access to the datastream and of course the publicly distributed ledger can extract the cleartext data of the transaction messages.
Because there must not even be a specific approach to get such transaction message data out of a TCP stream, just a simple filter for email addresses (example) is enough. 
Even with a simple encryption of such messages - and publicly known passphrase - it is much more complicated for the Man-In-The-Middle listener to collect data on the fly. 

**Targeted benefits:**
   - By using a default passphrase, Man-In-The-Middle "sniffer" cannot extract/parse data like email-addresses, invoice-numbers on the fly that easily. They would need to search for a cardano-node transmission and decrypt each message. Public explorers like Cexplorer.io, Cardanoscan, etc. can still show the decrypted message content via there https connection to the user. So no cleartext transmission at all.
   - Different users can transfer funds with encrypted messages attached between each other, using a preshared passphrase. Only theses users need to know the content. Example: A user buys goods from an online-store, the store provides a preshared-passphrase to the user on their website or via email, the user sends the payment with payment-information encrypted with this passphrase to the store.
   - Keeping the usecase of a transaction private does not only belong to different entities, but to a single user too. Example: If a user sends funds to a Dex or wants to lend some fund to a friend, he just can add information like 'Sent xxx ADA to bob for xxx' to the outgoing transaction as a documentation using an own choosen private passphrase. This information is stored on the chain and so in the wallet, only the user itself can review the use case of these transactions.
   - Backwards compatible with CIP-0020
   - Easy implementation by using well known tools like OpenSSL

### What this CIP is not trying to do

This addition to the original CIP-0020 should not be seen as the end-all-be-all security solution for privacy on the blockchain. There's better options and upcoming Midnight for that. The transaction messages are also not intended to act like chat messages on the chain.

# Specification - Encrypted message

The specification update for encrypted messages takes advantage of the simple original design, which is leaving room for additional json-keys not affecting the parsing of the content at all. The only outcome if a receiver does not process the encrypted content is, that the encrypted message is shown instead of an maybe autodecrypted one. But even the encrypted base64 strings fit into the max. 64char long string restriction. So it does not break any tools. More on the autodecryption later. 

### Format:
``` json
{ 
  "674":
         { 
           "enc": "<encryption-method>",
           "msg": 
                  [ 
                    "base64-string 1", "base64-string 2", "base64-string 3" ...
                  ]
         }
}
```
The format is identical to the original one, with a simple addition of the `enc` (encryptionmode) entry.

The value given in the `enc` field references the type of encryption is used. Starting with a simple implementation named `basic`. There is room to add additional encryption method in the future like using ChaCha20/Poly1305 or using public/private key encryption. Also there is the possibility to not encode the metadata in the standard JSON format, but using CBOR encoding instead.

  
### Encryption methods:

#### **plain** - no encryption at all
  
  | Parameter | Value |
  | :--- | :--- |
  | method | **plain** |
  |description|plaintext, no encryption|

  This is not really an encryption mode, but included as a backwards compatible entry to signal this message as an unencrypted one. The entry is not needed and fully optional for unencrypted messages.

#### **basic** - aes-256-cbc salted symmetric encryption via passpharse (+default passphrase)

  | Parameter | Value |
  | :--- | :--- |
  | method | **basic** |
  | description | symmetrical encryption via openssl and a passphrase |
  | default passphrase | cardano |
  | type | openssl |
  | cipher | aes-256-cbc (salted) |
  | digest | pdkdf2 |
  | padding | PKCS#7 |
  | iterations | 10000 (default) |
  | key + iv | 32 bytes key + 16 bytes iv |
  | salt | 8 bytes |
  | prefix | `Salted__` |
  | encoding | base64|

OpenSSL was choosen, because its fast and widely available also for all kind of different platforms, web frontends, etc. Encryption algo is **AES-256-CBC** (salted) using `pdkdf2` to derive the key from the given passphrase. 10000 Iterations is the default value for this encryption method. The format of the encoded output is base64 format.

The encryption is based on a given passphrase, which can be choosen by the user. However, a default-passphrase "cardano" should be used to encrypt/decrypt if no other passphrase is provided or known.
  
OpenSSL uses [PKCS#7](https://datatracker.ietf.org/doc/html/rfc5652#section-6.3) as padding. The adopted cipher accepts only multiple of 16-byte blocks. Not fitting messages to be encrypted are filled with the number of padding bytes that are needed to form multiple of 16-bytes. So if 1 byte of padding is required, the padding "01" is added. If 2 bytes of padding are needed, "02 02" is added. If no padding is required, an extra block of 0x10 bytes is added, meaning sixteen "10" bytes. In order to be interoperable with OpenSSL this kind of padding is a requirement.  
  
##### Why a default passphrase?
  
As pointed out above, its way harder for man-in-the-middle listeners, to decrypt every single message on the fly. So by using a default passphrase, tools can encrypt messages and explorers/wallets can autodecrypt such messages trying to use the default passphrase. In that way, the displayed message is automatically readable to the user. If a more protected communication is needed, the sender can choose a custom passphrase and communicate that to the receiver as a preshared passphrase.

What part is uses for the encryption?
  
The **whole content** of the unencrypted normal transaction **metadata `msg:` key is used**, thats the array with the message string(s). (Example below)

##### Is there sample code?  
  
Yes, example implementations for node.js, PHP, bash, etc. can be found in the [codesamples](./codesamples/) folder. They are showing how to encrypt/decrypt text with the right parameters set for this basic mode.
  
**warning**

Message decryption should be done on the user frontend if possible, not via server callbacks.**

#### Encryption/Decryption example on the console - basic mode

First, generate a normal metadata transaction message. 

**normal-message-metadata.json**:
``` json
{
  "674": {
    "msg": ["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]
  }
}
```

The **encryption** is done on the **whole content of the `msg:` key**, so this is
  
`["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]`
 
in our example.
  
**Encrypt** this content via openssl, the default passprase **cardano**, iteration set to 10000 and key-derivation via pbkdf2:
``` console
echo -n '["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]' | openssl enc -e -aes-256-cbc -pbkdf2 -iter 10000 -a -k "cardano"
```

The encrypted result are the **base64 encoded strings**:
```
U2FsdGVkX1/5Y0A7l8xK686rvLsmPviTlna2n3P/ADNm89Ynr1UPZ/Q6bynbe28Y
/zWYOB9PAGt+bq1L0z/W2LNHe92HTN/Fwz16aHa98TOsgM3q8tAR4NSqrLZVu1H7
```

Compose the JSON by **using the base64 encoded encrypted strings now for the `msg:` part**.
                                                                
Also add the value `basic` for the `enc:` key, to mark this transaction message as encrypted with basic mode. 

**encrypted-message-metadata.json**:
``` json
{ 
  "674":
         { 
           "enc": "basic",
           "msg": 
                 [ 
                   "U2FsdGVkX1/5Y0A7l8xK686rvLsmPviTlna2n3P/ADNm89Ynr1UPZ/Q6bynbe28Y",
                   "/zWYOB9PAGt+bq1L0z/W2LNHe92HTN/Fwz16aHa98TOsgM3q8tAR4NSqrLZVu1H7"
                 ]
         }
}
```

Console one-liner:
``` console
jq ".\"674\".msg = [ $(jq -cjrM .\"674\".msg normal-message-metadata.json | openssl enc -e -aes-256-cbc -pbkdf2 -iter 10000 -a -k "cardano" | awk {'print "\""$1"\","'} | sed '$ s/.$//') ]" <<< '{"674":{"enc":"basic"}}' | tee encrypted-message-metadata.json | jq
``` 

---
  
A **decryption** can be done in a similar way:
``` console
jq -crM ".\"674\".msg[]" encrypted-message-metadata.json | openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -a -k "cardano"
```

Which results in the original content of the **msg** key:
  
`["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]`

## Rationale

This design is simple, so many tools on the cardano blockchain can adopt it easily and a few have already started to implement it.
The original CIP-0020 design allowed the addition of new entries like the `"enc":` key for encrypted messages in this CIP. Therefore the encoding format of the encrypted message was choosen to be UTF-8 instead of bytearrays, because it would break the backwards compatibility to CIP-0020. But maybe more important, it gives the user a simple text-format to handle such messages. Users can copy and paste the base64 encoded string(s) using there own tools for creation and verification. For example, a user can simply copy the encrypted format from an explorer and verify it with an external own local tool. Such messages are usally pretty short. Yes, the benefit of using bytearrays is to have less data (around -33% over base64), but the decision was made to sacrifice this benefit in favor of the base64 format for the reasons pointed out before.

There is also for example [CIP-8](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0008), but CIP-8 doesn't really fulfill the simplicity of just providing encrypted messages. CIP-8 is focused on Signing, which is not needed for encryption. The method to generate encrypted messages here is not intended to verify the owner of a message via signing. There is no need that everything on Cardano must be difficult. Also using such CBOR encoded structures would break all currently implemented transaction message solutions. This CIP uses openssl and base64 encoding, and endusers could even copy&paste such text into other tools, etc. Future updates may include the option to mix encrypted and unencrypted messages by adding another key like `msgclear` to support such a mixed message style format.

### Implementation suggestions
 
Wallets/Tools can implement an autodecryption attempt with the default passphrase on such messages, to give the user a more streamlined experience. The communication should be done via https or similar to make sure the message cleartext is not exposed again during the transmission.
Additionally the Tools can prompt for an input and decrypt the message once the user has requested it, this decryption should be done on the user frontend for further security.

### Handling ill-formed 674 metadata ##

Like with CIP-0020, it is up to the wallet-/display-/receiver-implementor to parse and check the provided metadata. As for the current state, its not possible to have the same label "674" more than once in a cardano transaction. So a check about that can be ignored at the moment. This CIP provides the correct implementation format, the parsing should search for the "674" metadata label, the "msg" and the "enc" key underneath it. There should also be a check, that the provided data within that "msg" key is an array. All other implementations like a missing "msg" key, or a single string instead of an array, should be marked by the display-implementor as "invalid". Additional keys within the "674" label should not affect the parsing of the "msg" and the "enc" key. As written above, we will likely see more entries here in the future like a "version" key for example, so additional keys should not harm the parsing of the "msg" and "enc" key. 

### Implementation conclusion ##

An encrypted transaction message should be considered valid if the following apply:

* Label = 674.
* has property "enc".
* enc property contains a supported method like `basic`
* has property "msg".
* msg property contains an array of strings, even for a single-line message.
* Each line has a maximum length of 64 characters.
* If there are additional properties, they don't invalidate the message. They can just be ignored.

If any of the above is not met, ignore the metadata as an encrypted transaction message. Can still be displayed as general metadata to the transaction.

The implementation format in this CIP should be the ground base for encrypted transaction messages/comments/memos and should be respected by creator-/sender-implementations as well as in wallet-/receiver-/display-implementations.

## Path to Active

### Acceptance Criteria

The acceptance criteria to be `Active` should already have been met, because the following Implementors using this CIP on the Cardano Blockchain:

* Cardano Explorer (https://cexplorer.io)
* StakePoolOperator Scripts (https://github.com/gitmachtl/scripts)
* AdaStat.net (https://adastat.net)
* Eternl Wallet (https://eternl.io)

#### Integration examples for encrypted messages

**Cexplorer.io**: With the implementation of the **encrypted message decoding**.
![image](https://user-images.githubusercontent.com/47434720/204560392-f45bbe4f-7f78-48fa-9e47-4d3b104685bf.png)

**StakePool Operator Scripts**: It works on the commandline like any other script of the collection by just adding the `"enc: basic"` parameter, you can provide an individual passphrase by using the `"pass:<passphrase>"` parameter. This automatically generates the needed metadata.json structure with the encrypted message in it and attaches it to the transaction itself.
![image](https://user-images.githubusercontent.com/47434720/205442737-748a7fb0-90fc-4cc3-898c-98b06894a900.png)

**Eternl.io**:
![image](https://user-images.githubusercontent.com/47434720/210166917-8af475fe-5cda-46f5-bd8d-3fc4c2c12482.png)
    
**AdaStat.net**: With the implementation of the **encrypted message decoding** using a pure **frontend solution**.
![image](https://user-images.githubusercontent.com/47434720/206574191-22aa490a-5870-4853-906b-443284458987.png)
![image](https://user-images.githubusercontent.com/47434720/206574354-5dd81551-efc6-4f69-a2aa-282bb40e5084.png)


### Implementation Plan

The following Projects have committed to also implement it:

* CNTools (https://cardano-community.github.io/guild-operators/#/Scripts/cntools)
* JorManager (https://bitbucket.org/muamw10/jormanager/)
* Cardanoscan.io (https://cardanoscan.io)

The plan is to reach out to other projects - which already supporting the normal transaction messages - too. And of course also to new ones.

There are various **code samples available** in the [**codesamples**](codesamples/) folder to make it as easy as possible for integrators to implement it.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
