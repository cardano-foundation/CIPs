---
CIP: 20
Title: Transaction message/comment metadata
Status: Active
Category: Metadata
Authors:
    - Martin Lang <martin@martinlang.at>
    - Ola Ahlman <ola@ahlnet.nu>
    - Andrew Westberg <andrewwestberg@gmail.com>
Implementors:
    - CNTools <https://cardano-community.github.io/guild-operators/#/Scripts/cntools>
    - JorManager <https://bitbucket.org/muamw10/jormanager/>
    - StakePoolOperator Scripts <https://github.com/gitmachtl/scripts>
    - Cardanoscan.io <https://cardanoscan.io>
    - AdaStat.net <https://adastat.net>
    - Eternl Wallet <https://eternl.io>
    - CardanoWall <https://cardanowall.com>
    - Nami Wallet <https://namiwallet.io>
    - CNFT <https://cnft.io>
    - Cardano Explorer <https://cexplorer.io>
    - SundaeSwap <https://https://sundaeswap.finance/>
    - Minswap <https://minswap.org/>
    - MuesliSwap <https://muesliswap.com/>
    - DripDropz.io <https://dripdropz.io/>
    - Typhon Wallet <https://typhonwallet.io/>
    - Ledger Live <https://www.ledger.com/>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/100
    - https://github.com/cardano-foundation/CIPs/pull/394
Created: 2021-06-13
License: CC-BY-4.0
---

## Abstract

This CIP describes a basic JSON schema to add messages/comments/memos as transaction metadata by using the metadatum label **674**.
Adding **informational text, invoice-numbers or similar** to a transaction on the cardano blockchain.

## Motivation

We have the utilities on the cardano blockchain now since the introduction of the "allegra-era". A simple consens about adding messages, comments or memos to transactions is still missing.
So the CIP authors came together to form a first implementation of this. It is straight and simple, additional keys and content can be added later.
The IOG main wallet `Daedalus` can now also directly show attached metadata information in the transaction details view. This CIP is the missing link to bring it together.

Some of the current Tools/Sites/Explorers that have implemented it already:
* [CNTools](https://cardano-community.github.io/guild-operators/#/Scripts/cntools)
* [JorManager](https://bitbucket.org/muamw10/jormanager/)
* [StakePoolOperator Scripts](https://github.com/gitmachtl/scripts)
* [Cardanoscan.io](https://cardanoscan.io)
* [AdaStat.net](https://adastat.net)
* [Eternl Wallet](https://eternl.io)
* [CardanoWall](https://cardanowall.com)
* [Nami Wallet](https://namiwallet.io)
* [CNFT](https://cnft.io)
* [Cardano Explorer](https://cexplorer.io)
* [SundaeSwap](https://https://sundaeswap.finance/)
* [Minswap](https://minswap.org/)
* [MuesliSwap](https://muesliswap.com/)
* [DripDropz.io](https://dripdropz.io/)
* [Typhon Wallet](https://typhonwallet.io/)
* [Ledger Live](https://www.ledger.com/)

## Specification

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

### Some Integration examples

**Ledger Live** is offering a memo field
![image](https://user-images.githubusercontent.com/47434720/204649383-c34ae733-e136-41b8-8fa8-619dde978621.png)

**Daedalus** shows the metadata text (could be improved if CIP is implemented):
![image](https://user-images.githubusercontent.com/47434720/121822100-85b38a80-cc9d-11eb-9d13-1869746a69b2.png)

**Cardanoscan.io**, **Adastat.net** and other tools implemented it already, to show messages along transactions:
![image](https://user-images.githubusercontent.com/47434720/204633595-d865c7ee-0c30-4af1-bb55-3c0ad323b58c.png)
![image](https://user-images.githubusercontent.com/47434720/204634111-256c6c18-974a-41f5-a6e4-b9edee8f9d62.png)

**eternl.io** has added it with a message field on the sending-page, and shows it also on the transactions-page:
![image](https://user-images.githubusercontent.com/47434720/204632224-5be33098-00f6-41da-a2f0-7c138b28354f.png)
![image](https://user-images.githubusercontent.com/47434720/204632802-33f1afa5-d9b2-494f-84fe-d7f0594a7f1b.png)

**StakePool Operator Scripts**: It works on the commandline like any other script of the collection by just adding the "msg: ..." parameter to a transaction. This automatically generates the needed metadata.json structure and attaches it to the transaction itself.
![image](https://user-images.githubusercontent.com/47434720/129110626-6bc5b3c3-102d-4793-b508-7d4190b31cf7.png)

**CNTools**:<br>
![image](https://user-images.githubusercontent.com/47434720/130353491-fc0f3a69-1937-4e72-b680-c04cc069b5c4.png)


## Rationale

This design is simple, so many tools on the cardano blockchain can implement it easily. The array type was choosen to have consistency, no need to switch between a string or
an array format, or testing against a string or array format. Updates in the future are possible, like adding a versioning key `"ver":`, adding a key `"utxo":` to provide specific data for every tx-out#idx in the transaction, adding the `"enc":` key like for encrypted messages, making subarrays in the message-strings, etc. But for now, we need a common agreement to provide general messages/comments/memos with this CIP. The starting design war choosen as simple as possible to keep the additional transaction fees as low as possible.

### Wallet Implementation

Would be a good idea to hide the message/comment/note behind a "show unmoderated content" button/drop-down. Like the Metadata display on the Cardano Explorer. Also, it should be displayed as plain-text non-clickable. To enhance security further, URLs could be automatically deleted or hidden from such comments, to not welcome bad actors with phishing attempts. Another solution to start with would be to really limit the character space for display in Wallets, like limiting it to `a-zA-z0-9` and a handful of special chars like `+-_#()[]:` without a `.<>"/\` chars, so a domain or html code would not work. Last points are worth for discussions of course, because it would also filter out unicode.

### Handling ill-formed 674 metadata

It is up to the wallet-/display-/receiver-implementor to parse and check the provided metadata. As for the current state, its not possible to have the same label "674" more than once in a cardano transaction. So a check about that can be ignored at the moment. This CIP provides the correct implementation format, the parsing should search for the "674" metadata label and the "msg" key underneath it. There should also be a check, that the provided data within that "msg" key is an array. All other implementations like a missing "msg" key, or a single string instead of an array, should be marked by the display-implementor as "invalid". Additional keys within the "674" label should not affect the parsing of the "msg" key. As written above, we will likely see more entries here in the future like a "version" key for example, so additional keys should not harm the parsing of the "msg" key.

### Implementation conclusion

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

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
