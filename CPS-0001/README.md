---
CPS: 1
Title: Metadata Discoverability and Trust
Authors: 
    - Bruno Martins <bruno.martins@iohk.io>
Status: Open
Category:  Metadata
ProposedSolutions: 
    - https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026
    - https://github.com/cardano-foundation/CIPs/pull/355
    - https://github.com/cardano-foundation/CIPs/pull/85
    - https://github.com/cardano-foundation/CIPs/pull/112
    - https://github.com/cardano-foundation/CIPs/pull/137
    - https://github.com/cardano-foundation/CIPs/pull/299
Created: 2022-19-10
---

## **Abstract**
This document attempts to describe the problem in the Cardano ecocystem where there are many different types **subjects** or *chain entities* and there's a need to associate metadata with them. This metadata can be used to describe an script, stake pools, script hashes, token policies and applications. This metadata can be used to provide information to the user on it's applications, it's trustworthiness and how to interact with it.

## **Problem**
**`Discoverability`**: Means to discover the different metadata claims associated with a subject. Discoverability is important for wallets, applications (i.e dapps, stores, etc) and users to be able to find the different metadata claims associated with a subject. This is important for the user to be able to make an informed decision on how to interact with a subject.

**`Correctness`**: Lack of mechanism to assert that a given metadata claim is correct. Anybody and any service can provide metadata structures, but it's necessary to attest for the correctness of this metadata so that the user (or applications) are be able to make an informed decision in accepting, rejecting or how to interact with a subject.

**`Trust`**: There's no standard mechanism to assert that the metadata is coming from a legitimate source. This is important for the user to be able to make an informed decision on how to interact with a subject. This is also important for applications to be able to provide a better user experience. 

## **Use Cases**
- Find scripts used by a dApp
- Discover general information of a dApp (i.e name, description, icons, etc)
- Find the different metadata claims associated with a subject
- Associate some form of identity to a claim's owner so that it can be verified cryptographically
- Offer mechanism to attest for the correctness of a given metadata object that can be fetched by wallets and applications from off-chain sources (i.e CIP-26 complaint servers)
- Discover datum schemas used by a script in a specific context or dApp use cases
- An wallet receiving a request to connect to a dApp, it can verify the authenticity of the dApp and the metadata associated with it.

## **Goals**
- Define how metadata can be associated with the a subject (i.e dapp, stake pool, token policy, etc)
- Metadata should be discoverable by wallets and applications
- Associate some form of identity to a metadata claim

## **Open Questions**
- Is this a combination of problems and should be split into multiple CPS?
- Does this englobes all the problems related to metadata?
- Trust can be anchored to the owner's metadata or also third-parties that attest for the correctness of the metadata. How to handle this?
- How to associate identity to a metadata claim?
- How to handle the case where a subject has multiple metadata claims associated with it?
- How to handle the case where a subject has multiple metadata claims associated with it and the user wants to select a specific one?