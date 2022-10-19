---
CPS: 1
Title: DApps Metadata Registration, Discovery and Trust
Authors: Bruno Martins <bruno.martins@iohk.io>
Status: Proposed
Type: Standards
Category: Wallets | Metadata | Plutus
Proposed Solutions: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026,
https://github.com/cardano-foundation/CIPs/pull/355
Created: 2022-19-10
---

## **Abstract**
This document attempts to describe the problem in the cardano ecocystem where there are many different types of applications being developed and there's a need to associate metadata with them. This metadata can be used to describe the application, its purpose, its version, its author, which scripts it uses, certifications and information about it's developer or publisher. This metadata can be used to provide information to the user about the application and its trustworthiness. This metadata can also be used to provide information to the wallet about the application and how to interact with it.

## **Goals**
- Uncensorable and decentralized metadata registration
- Define how metadata can be associated with the a subject (i.e dapp)
- Define how a DApp metadata can be registered in the ecosystem for the purpose of discovery (i.e dapp stores)
- Associate some form of identity to the metadata claim
- Provide standard for certification of the dapp metadata claim, scripts and code
- Offer a trust model for the wallets to make an informed decision wheter to trust a dapp or not
- Standard to find metadata for a given subject (dapp, script, etc)

## **Problem**
**`Dapp Discovery`**: There's no standard way to discover dapps in the ecosystem. A Dapp being a collection of scripts and metadata, a dapp store for instance has no defined mechanism to index a "dapp publication" claim. This claim can be made by the dapp developer or by a third party. The dapp store can then use this claim to index the dapp and make it available for the user to browse. 

**`Certification`**: Any actor of the ecosystem may see other actors as more trustworthy than others. Metadata certification can be used to provide a way for the user to make an informed decision about the trustworthiness of the dapp and it's provided information.  This claim can be made by a third party, such as a dapp store, a auditor, a known  developer, a community member, etc. The certification claim can be used to provide a trust model for the wallet to make an informed decision about the trustworthiness of the dapp. 

**`Identity`**: In order to anchor some form of trust to the dapp metadata claim, there's a need to associate some form of identity to it's publisher. This should be cryptographically verifiable.

**`Verify correctness of metadata`**: For a given metadata structure we need to be able to verify that the metadata is correct in it's structure and that the data is correct. Given the uncensorable nature and goal for a healthy ecosystem, there can be multiple claims against the same subject and the concept of "correct" is therefore subjective and should be attached in some way to the *identity* of the publisher.

**`Metadata discovery`**: When provided with specific pieces of information such as script addresses, we need to be able to find the metadata associated with it. This is useful for the wallet to be able to provide the user with information about the dapp, other related scripts and potential certifications or identity information about parties that made claims about that subject.

## **Open Questions**
- Is this a combination of problems and should be split into multiple CPS?
- Does this englobes all the problems related to dapp metadata?
- Is this just a problem for dapps or should this be more generic? 