---
CIP: 20
Title: Transaction message/comment metadata
Authors: Martin Lang <martin@martinlang.at>, Ola Ahlman <ola@ahlnet.nu>, Andrew Westberg <andrewwestberg@gmail.com>
Comments-URI: no comments yet
Status: Active
Type: Informational
Created: 2021-06-13
Updated: 2022-11-29
License: CC-BY-4.0
---

# Abstract

This CIP describes a basic JSON schema to add messages/comments/memos as transaction metadata by using the metadatum label **674**.
Adding **informational text, invoice-numbers or similar** to a transaction on the cardano blockchain.

# Motivation

We have the utilities on the cardano blockchain now since the introduction of the "allegra-era". A simple consens about adding messages, comments or memos to transactions is still missing.
So the CIP authors came together to form a first implementation of this. It is straight and simple, additional keys and content can be added later.
The IOG main wallet `Daedalus` can now also directly show attached metadata information in the transaction details view. This CIP is the missing link to bring it together.

Current Tools/Sites/Explorers that have implemented it already or have plans to implement it:
* [CNTools](https://cardano-community.github.io/guild-operators/#/Scripts/cntools)
* [JorManager](https://bitbucket.org/muamw10/jormanager/)
* [StakePoolOperator Scripts](https://github.com/gitmachtl/scripts)
* [Cardanoscan.io](https://cardanoscan.io)
* [AdaStat.net](https://adastat.net)
* [CardanoCommunityWallet](https://ccwallet.io)
* [CardanoWall](https://cardanowall.com)
* [CNFT](https://cnft.io)

# Specification

The specification for the individual strings follow the general design specification for JSON metadata, which is already implemented and in operation on the cardano blockchain.
The used metadatum label is **`"674":`**, this number was choosen because it is the T9 encoding of the string "msg".
The message content has the key **`"msg":`** and consists of an **array** of individual **message-strings**. 
The number of theses **message-strings** must be at least one for a single message, more for multiple messages/lines. Each of theses individual **message-strings** array entries must be at most 64 bytes when UTF-8 encoded.

### Format:
``` 
{ 
  "674":
         { 
           "msg": 
                  [ 
                    "message-string 1" //Optional: ,"message-string 2","message-string 3" ...
                  ]
         }
}
```

### Example for a single message/comment/memo:
``` json
{ 
  "674":
         { 
           "msg": 
                  [ 
                    "This is a comment for the transaction xyz, thank you very much!"
                  ]
         }
}
```

### Example for multiple messages/comments/memos:
``` json
{ 
  "674":
         { 
           "msg": 
                  [ 
                    "Invoice-No: 1234567890",
                    "Customer-No: 555-1234",
                    "P.S.: i will shop again at your store :-)"
                  ]
         }
}
```

&nbsp;<p>

# Specification - Encrypted message

This is an addition to the original CIP-0020, which is active since mid 2021 and widely used across many entities. It is fully backwards compatible and requires no changes in existing tools, explorers, wallets. 

Why do we need this? Metadata is sent unencrypted and in plaintext over the networks, a 3rd-party or man-in-the-middle can easily collect data such as bank-account-numbers, email-addresses, etc. out of such messages. With even a simple encryption of such a message - and publicly known passphrasw - it is much more complicated for the man-in-the-middle listener to collect data on the fly.

The specification update for encrypted messages takes advantage of the simple original design, which is leaving room for additional json-keys not affecting the parsing of the content at all. The only outcome if a receiver does not process the encrypted content is, that the encrypted message is shown istead of an maybe autodecrypted one. More on the autodecryption later. 

### Format:
``` 
{ 
  "674":
         { 
           "enc": "<encryptionmode>",
           "msg": 
                  [ 
                    "encrypted-string 1" //Optional: ,"encrypted-string 2","encyrpted-string 3" ...
                  ]
         }
}
```
The format is identical to the normal one, with a simple addition of the `enc` (encryptionmode) entry.

The value given in the `enc` field references an entry in the [Encryption Mode Json](cip0020-encryption-modes.json) file, which collects different encryption methods and there parameters. Starting with a simple implementation named `basic`. This reference file is just a collection and should be seen as a look-up-file about the methods. This file can also be updated and extended with new encryption methods - like with public/private key encryption - easily in future updates.

### Encryption modes:

* **plain** - no encryption at all

This is not really an encryption mode, but included as a backwards compatible entry to signal this message as an unencrypted one. The entry is not needed and fully optional for unencrypted messages.

* **basic** - aes-256-cbc based salted symmetric encryption via passpharse (+default passphrase)

Lets list the entry from the [Encryption Mode Json](cip0020-encryption-modes.json) file first for the basic method:
``` json
   "basic": {
      "desc": "symmetrical encryption via openssl and a passphrase (default=cardano)",
      "type": "openssl",
      "cipher": "aes-256-cbc",
      "digest": "pdkdf2",
      "iter": 10000,
      "encode": "base64" }
```

OpenSSL was choosen, because its fast and widely available also for all kind of different platforms, web frontends, etc. Encryption algo is AES-256-CBC (salted) using `pdkdf2` to derive the key from the given passphrase. 10000 Iterations is the default value for this encryption method. The format of the encoded output is base64 format.

The encryption is based on a given passphrase, which can be choosen by the user. However, a default-passphrase "cardano" should be used to encrypt/decrypt if no other passphrase is provided or known. Why a default passphrase? As pointed out above, its way harder for man-in-the-middle listeners, to decrypt every single message on the fly. So by using a default passphrase, tools can encrypt messages and explorers/wallets can autodecrypt such messages trying to use the default passphrase. In that way, the displayed message is automatically readable to the user. If a more protected communication is needed, the sender can choose a custom passphrase and communicate that to the receiver as a preshared passphrase.

The part that is encrypted/decrypted is the value of the **msg** key from a normal transaction metadata json, the array with the message(s) string(s).

Example implementations for node.js, PHP, etc. can be found in the [codesamples](codesamples/) folder.

### Encryption/Decryption example on the console - basic mode

First, generate a normal metadata transaction message. There is no difference yet.

**normal-message-metadata.json**:
``` json
{
  "674": {
    "msg": ["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]
  }
}
```

Encrypt the message via openssl and the default passprase **cardano**:
``` console
openssl enc -e -aes-256-cbc -pbkdf2 -iter 10000 -a -k "cardano" <<< '["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]'
```

Result are the base64 encoded strings:
```
U2FsdGVkX1/5Y0A7l8xK686rvLsmPviTlna2n3P/ADNm89Ynr1UPZ/Q6bynbe28Y
/zWYOB9PAGt+bq1L0z/W2LNHe92HTN/Fwz16aHa98TOsgM3q8tAR4NSqrLZVu1H7
```

Compose the JSON by using the base64 encoded encrypted strings now for the `msg:` part. Also add the value `basic` for the `enc:` key.

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
jq ".\"674\".msg = [ $(jq -crM .\"674\".msg normal-message-metadata.json | openssl enc -e -aes-256-cbc -pbkdf2 -iter 10000 -a -k "cardano" | awk {'print "\""$1"\","'} | sed '$ s/.$//') ]" <<< '{"674":{"enc":"basic"}}' | tee encrypted-message-metadata.json | jq
``` 

---
  
A **decryption** can be done in a similar way:
``` console
jq -crM ".\"674\".msg[]" encrypted-message-metadata.json | openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -a -k "cardano"
```

Which results in the original content of the **msg** key:
`["Invoice-No: 123456789","Order-No: 7654321","Email: john@doe.com"]`

&nbsp;<p>

# Some Integration examples

**Daedalus** shows the metadata text (could be improved if CIP is implemented):
![image](https://user-images.githubusercontent.com/47434720/121822100-85b38a80-cc9d-11eb-9d13-1869746a69b2.png)

**Cardanoscan.io**, **Adastat.net** and other tools implemented it already, to show messages along transactions:
![image](https://user-images.githubusercontent.com/47434720/124379245-1f2af680-dcb6-11eb-97b7-10f70d840e88.png)
![image](https://user-images.githubusercontent.com/47434720/124381343-3ff94900-dcc2-11eb-8d03-8fbacd3322b0.png)

**ccwallet.io** has added it with a message field on the sending-page, and shows it also on the transactions-page:
![image](https://user-images.githubusercontent.com/47434720/127367420-b360972d-c6e0-4002-865e-df070904bd30.png)
![image](https://user-images.githubusercontent.com/47434720/127367228-339ac059-007a-40fd-a6c0-97f890e93964.png)
![image](https://user-images.githubusercontent.com/47434720/127368912-c85dc9f0-6ee3-4cc1-a24b-9716a20f27d3.png)

**StakePool Operator Tools**: It works on the commandline like any other script of the collection by just adding the "msg: ..." parameter to a transaction. This automatically generates the needed metadata.json structure and attaches it to the transaction itself.
![image](https://user-images.githubusercontent.com/47434720/129110626-6bc5b3c3-102d-4793-b508-7d4190b31cf7.png)

**CNTools**:<br>
![image](https://user-images.githubusercontent.com/47434720/130353491-fc0f3a69-1937-4e72-b680-c04cc069b5c4.png)

# Rationale

This design is simple, so many tools on the cardano blockchain can implement it easily. The array type was choosen to have consistency, no need to switch between a string or
an array format, or testing against a string or array format. Updates in the future are possible, like adding a versioning key `"ver":`, adding a key `"utxo":` to provide specific data for every tx-out#idx in the transaction, making subarrays in the message-strings, etc. But for now, we need a common agreement to provide general messages/comments/memos with this CIP. The starting design war choosen as simple as possible to keep the additional transaction fees as low as possible.

## Wallet Implementation

Would be a good idea to hide the message/comment/note behind a "show unmoderated content" button/drop-down. Like the Metadata display on the Cardano Explorer. Also, it should be displayed as plain-text non-clickable. To enhance security further, URLs could be automatically deleted or hidden from such comments, to not welcome bad actors with phishing attempts. Another solution to start with would be to really limit the character space for display in Wallets, like limiting it to `a-zA-z0-9` and a handful of special chars like `+-_#()[]:` without a `.<>"/\` chars, so a domain or html code would not work. Last points are worth for discussions of course, because it would also filter out unicode.

## Handling ill-formed 674 metadata ##

It is up to the wallet-/display-/receiver-implementor to parse and check the provided metadata. As for the current state, its not possible to have the same label "674" more than once in a cardano transaction. So a check about that can be ignored at the moment. This CIP provides the correct implementation format, the parsing should search for the "674" metadata label and the "msg" key underneath it. There should also be a check, that the provided data within that "msg" key is an array. All other implementations like a missing "msg" key, or a single string instead of an array, should be marked by the display-implementor as "invalid". Additional keys within the "674" label should not affect the parsing of the "msg" key. As written above, we will likely see more entries here in the future like a "version" key for example, so additional keys should not harm the parsing of the "msg" key. 

## Implementation conclusion ##

A transaction message should be considered valid if the following apply:

* Label = 674.
* has property "msg".
* msg property contains an array of strings, even for a single-line message.
* Each line has a maximum length of 64 characters.
* If there are additional properties, they don't invalidate the message. They can just be ignored.

If any of the above is not met, ignore the metadata as a transaction message. Can still be displayed as general metadata to the transaction.

_Optional to consider for the implementer:_

* For message creation both single-line and multi-line input should be considered valid. The wallet/tool isn't required to support multi-line input.
* Message display in explorers/wallets should however preferably support multi-line messages even if it only supports single-line on creation. Not a requirement but should at least indicate that there are more data if only the first line is displayed. Maybe a link to explorer etc in the case it's not possible to solve in UI in a good way.

The implementation format in this CIP should be the ground base for transaction messages/comments/memos and should be respected by creator-/sender-implementations as well as in wallet-/receiver-/display-implementations.

# Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
