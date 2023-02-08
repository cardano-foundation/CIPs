---
CPS: 1
Title: Metadata Discoverability and Trust
Authors: 
    - Bruno Martins <bruno.martins@iohk.io>
Status: Open
Category: Metadata
Proposed Solutions: 
Created: 2022-10-19
---

## **Abstract**
This document attempts to describe the problem in the Cardano ecosystem where there are many different types **subjects** or *chain entities* and there's a need to associate metadata with them. This metadata can be used to describe scripts, stake pools, script hashes, token policies and applications. This metadata can be used to provide information to the user on it's applications, it's trustworthiness and how to interact with it.

## **Problem**
**`Discoverability`**: Means to discover the different metadata claims associated with a subject. Discoverability is important for wallets, applications (i.e dapps, stores, etc) and users to be able to find the different metadata claims associated with a subject. This is important for the user to be able to make an informed decision on how to interact with a subject.

**`Correctness`**: Lack of mechanism to assert that a given metadata claim is correct. Anybody and any service can provide metadata structures, but it's necessary to attest for the correctness of this metadata so that the user (or applications) are be able to make an informed decision in accepting, rejecting or how to interact with a subject.

**`Trust`**: There's no standard mechanism to assert that the metadata is coming from a legitimate source. This is important for the user to be able to make an informed decision on how to interact with a subject. This is also important for applications to be able to provide a better user experience.

## **Use Cases**
- Find scripts used by a dApp
- Discover general information of a dApp (i.e name, description, icons, etc)
- Find the different metadata claims associated with a subject
- Associate some form of identity to a claim's owner so that it can be verified cryptographically
- Offer mechanism to attest for the correctness of a given metadata object that can be fetched by wallets and applications from off-chain sources (i.e [CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) complaint servers)
- Discover datum schemas used by a script in a specific context or dApp use cases
- A wallet receiving a request to connect to a dApp, it can verify the authenticity of the dApp and the metadata associated with it

### **Proposed Solutions Discussion**
As it stands this problem statement casts a wide net; thus many CIPs/proposals have touched and partly addressed the underlying issues. 

We organize these proposed solutions by their metadata **subjects** in the table below.

Name | Metadata **Subjects** |
---- | --------------------- |
[CIP-06](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0006) | Stake Pools |
[CIP-77?](https://github.com/cardano-foundation/CIPs/pull/361) | Stake Pools |
[CIP-0989?](https://github.com/cardano-foundation/CIPs/pull/241) | Stake Pools |
[CIP-25](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025) | Tokens |
[CIP-68](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068) | Tokens |
[#137](https://github.com/cardano-foundation/CIPs/pull/137) | Tokens |
[#430](https://github.com/cardano-foundation/CIPs/pull/430) | Tokens |
[CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) | Scripts |
[#185](https://github.com/cardano-foundation/CIPs/pull/185) | Scripts |
[CIP-43?](https://github.com/cardano-foundation/CIPs/pull/319) | Addresses |
[CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) | Generic |

#### **Stake Pools**
There are currently three proposals aimed at linking metadata to stake pools, extending the [SMASH](https://github.com/input-output-hk/smash/) system. Trust is asserted through these proposals by metadata being anchored to on-chain to stake pool registration certificates, which are signed. [CIP-0989?](https://github.com/cardano-foundation/CIPs/pull/241) and [CIP-77?](https://github.com/cardano-foundation/CIPs/pull/361) add to this by associating DIDs allowing for further trust to be associated. Correctness can be checked by the [SMASH](https://github.com/input-output-hk/smash/) system as the on-chain components contain a hash of the off-chain metadata. A chain follower can be used for discovery, following the chain for stake pool operator registration certificates, then performing correctness and trust checks.

#### **Tokens**
Starting with [CIP-25](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025) there have been three further proposals for attaching metadata to tokens. All of these proposals assert trust in the claim via the token issuer, e.g. if you trust minter you trust their claims. Correctness of claims is largely unaddressed in these proposals. The ability to discover metadata for these is linked to token's policy ID and minting, meaning clients chain followers can easily index such data.

#### **Scripts**
There are two proposals which aim to attach metadata to scripts/dApps, those being [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) and [#185](https://github.com/cardano-foundation/CIPs/pull/185). Each of these is quite different, [#185](https://github.com/cardano-foundation/CIPs/pull/185) is just focussed on attaching software licenses, whereas [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) facilitates more generic metadata. Trust is asserted for [#185](https://github.com/cardano-foundation/CIPs/pull/185) through attachment to the transaction deploying the script. The assumption is that the owner of the script will publish a trustworthy metadata claim. [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) places the burden of trust upon the client through the supplied signature, meaning that clients should choose which metadata claims they trust based on what entity signed it. But there is no proposed framework for how clients should choose their trusted metadata claim publishers. Correctness is enforced through a hash of the off-chain data in [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355), [#185](https://github.com/cardano-foundation/CIPs/pull/185) uses a similar hashing mechanism, but it optional. Discoverability for [#185](https://github.com/cardano-foundation/CIPs/pull/185) is achieved via chain followers searching for transactions containing scripts and claims. Whereas discovery in [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) requires additional steps where claims are followed, verified and stored then they are able to be indexed.

#### **Addresses**
[CIP-43?](https://github.com/cardano-foundation/CIPs/pull/319) is the only proposal attempting to add metadata to addresses. although it should be noted that there are centralized solutions such as [ADA Handle](https://adahandle.com/). Since this has a very limited scope with only attaching a domain to an address, thus this is too niche to consider here.

#### **Generic Solutions**
[CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) is the only *truly* generic metadata solution presented, allowing for a range of **subjects**. Correctness is not explicitly enforced by any mechanism, beyond trusting the signing entity. Trust can be asserted via the signature included on the claim, but this is not enforced. Discovery is requires a client application to maintain verified mappings of subjects and claims, from which indexing can happen.

##### **Summary**
The vast majority of these proposals take advantage of the *free* anchor of trust and attach their metadata claims directly to their subjects in unique ways. This is great for their respective use cases because it halves the burden of discovery, but makes their wider application unsuitable. Only [CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) and [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) allow for a variety of **subjects**. 

The drawback of generic solutions is that discovery becomes more cumbersome, with the need for metadata clients and servers; this adds complexity. Although both CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) and [CIP-72?](https://github.com/cardano-foundation/CIPs/pull/355) do allow for greater correctness and trust to be built in their claims.

TODO: 
  - does this problem want a general solution or specific to each subject?
  - do these match what is needed in the proposed solutions

## **Goals**
- Define how metadata can be associated with a subject (i.e. dApp, stake pool, token policy, etc.)
- Metadata should be discoverable by wallets and applications
- Wallets and applications should be able to verify the correctness of metadata claims
- Associate some form of identity to a metadata claim

## **Open Questions**
- Is this a combination of problems and should be split into multiple CPS?
- Does this englobes all the problems related to metadata?
- Trust can be anchored to the owner's metadata or also third-parties that attest for the correctness of the metadata. How to handle this?
- How to associate identity to a metadata claim?
- How to handle the case where a subject has multiple metadata claims associated with it?
- How to handle the case where a subject has multiple metadata claims associated with it and the user wants to select a specific one?