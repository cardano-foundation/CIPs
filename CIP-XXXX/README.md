---
CIP: <?>  
Title: <Parameterized Reference Scripts>  
Authors: <Micah Kendall <micahk.me@icloud.com>>    
Comments-Summary: <No comments>  
Comments-URI: <>  
Status: <Draft>  
Type: <Standards>  
Created: <2022-10-17>  
License: <CC-BY-4.0>  
Requires: <CIP-33>  
---

## Abstract

Scripts which mint proof that a script could be generated from, by accepting parameters. The minted proof may also be used as a reference script.

## Motivation

It is difficult to verify that a Plutus script fits certain requirements. It is more difficult than that to then prove this generally on-chain. A very easy way to generate scripts which always do fit requirements is through parameterisation; you could pass arbitrary script logic as a parameter, or constant values like public keys. If you could prove that your script is the result of parameterisation on-chain, then it would be simple to create and verify complex protocols.

An example is NFTs which are minted through the parameterisation of an UTXO. This can be done off-chain of course, by evaluating some plutus core with a certain parameters. However this requires some complex backend systems. It would be much simpler to check for a 'parameterization output' which exists at the script address.

## Specification

This CIP would overload the field for plutus introduced by CIP-33. A parameterised script mints a reference script, which stores the hash of the parameterised script, and the parameters used to generate it. The minted script would be equivalent to as if you had done the parameterisation off-chain. The parameterised script itself is not necessarily a reference input, however in order to use the minted script as a reference input, the parameterised script would have to also be somehow provided (lending itself to being provided as a reference input in most cases).

A parameterised script with many parameters could be partially evaluated, giving a new reference parameterised script which has the hash of the original parameterised script, and the arguments provided so far. Then, a script which uses those same parameters, could be provided both the original parameterised script, and partially parameterised script in order to validate. This leads to a 'chain of dependencies' for validating complex scripts. If the original parameterised script is a reference script on-chain, then this can all be done automatically.

A script which is not originally parameterised could have the same plutus-core as the output of providing parameters to some more general script. Then, old scripts can be provided the minted proof that they fit some protocol, allowing backwards compatibility.

## Rationale

We specify overloading of the reference scripts field because they share the same data type, plutus core, and always have mutually exclusive types, so may be differentiated (reference scripts Redeemer -> Datum? -> ScriptContext -> exists a. a., and parameterised scripts any script which results in that).