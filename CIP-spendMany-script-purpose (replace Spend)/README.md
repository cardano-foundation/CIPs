---
CIP: ????
Title: SpendMany script purpose 
Category: Plutus
Status: Proposed
Authors:
    - Matteo Coppola <m.coppola.mazzetti@gmail.com>
Implementors: 
    - 
Discussions:
    - 
Created: 2024-07-13
License: Apache-2.0
---

## Abstract

This CIP proposes to replace the current Spend purpose with another one called SpendMany, removing the need of computational waste and higher fees when a transaction validates multiple inputs coming from the same script.

SpendMany is executed only once for the whole transaction and it comes with 2 parameters:
- The current script hash
- The list of the indexes of the inputs that are being spent from this script  
The second parameter is used to easily identify all the current script inputs in the script Context.

As this change could take a while to be implemented, this CIP proposes also another quick workaround:
we add in the Context a Map<Hash, List<InputIndex>> where the keys are the transaction's script hashes and the values are lists containing the indexes of the Inputs that come from these scripts.

## Motivation: why is this CIP necessary?

After years of Cardano smart contract development and sharing the experience with different teams, we came to the conclusion that there's no smart contract - except for trivial cases - that needs to validate each script utxo separately.
Even when a single utxo must be validated, all the recent smart contracts allow composability, permitting multiple inputs from the same script to be validated in the same transaction. When this is done for each utxo separately, developers need to add important redundant security checks to avoid double spending vulnerabilities.

Additionally, most of the times, the smart contract should also validate conditions of the transaction as a whole, for example the validity range or the sum of the Values of all the Inputs.
Validating N inputs separately means wasting a lot of resources (computational and transaction fees) because these conditions must be checked N times.
To circumvent this and get more performant smart contracts, the development community came up with the "Withdraw Zero" trick, which consists in using a separated WithdrawFrom script that will be executed only once for the full transaction. While this is a dirty hack used to circumvent the current status of the validator specification, it also still requires to check that the WithdrawFrom script is present for each script Input.

These problems have been briefly discussed in CPS-0004.

It is therefore necessary to replace the existing Spend purpose with a new one that I called SpendMany.
Please note that the name doesn't necessarily need to be changed, but we will use SpendMany here to refer to this CIP changes.


TODO

TODO Alternative

## Specification

TODO

## Rationale: how does this CIP achieve its goals?

TODO

## Path to Active

TODO

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).