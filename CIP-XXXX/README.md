---
CIP: <?>  
Title: <Parameterized Reference Scripts>  
Authors: Cardano DeFi Alliance <info@cardanodefialliance.org>, Cody Butz <cbutz@indigo-labs.io>, Jonas Lindgren <jonas@charli3.io>
Comments-Summary: <No comments>  
Comments-URI: <>  
Status: <Draft>  
Type: <Standards>  
Created: <2022-10-20>  
License: <CC-BY-4.0>
---

## Abstract

This proposal defines a data standard for oracles to follow when placing data on-chain, as well as consumers to read the datum of produced oracle feeds.

## Motivation

Oracles provide a way for real-world data to be provided to a blockchain or smart contract to allow interaction with external data sources. Oracle's query, verify, and authenticate external data and then relay it to the blockchain. Oracles can provide multiple types of data feeds, for example: asset spot price, access to indexes, and statistics data for a particular blockchain.

Oracles act as a data provider to the blockchain. As a data provider, it makes sense for the data feeds to be standardized so that they can be reused by multiple different projects, reducing fee overhead and decreasing feed setup overhead.

Data consumers, who are reading the price data from an oracle, want to be able to support multiple data feeds from different providers for fall-back mechanisms and additional decentralization. If each oracle solution is providing a different datum/metadata structure, these particular data structures have to be supported by the data consumers' smart contracts and/or applications. By having a standard data structure for each particular data feed type, as a data consumer I can write my smart contracts/application to support that standard and expect the oracle to support that particular standard.

Data consumers that share a common format for the data feeds they consume, may also be able to collaborate to provide more well-secured and frequently updated data feeds to share together, than they would otherwise be able to accomplish by each using their own standard.

## Specification

Oracles are responsible for providing multiple types of off-chain data to the blockchain. This proposal outlines an on-chain datum standard for Oracle producers to submit to the blockchain and Oracle consumers to read from the blockchain in a standardized format.

Such a standard should accomplish a number of somewhat contradictory objectives

* Data provided by the feed should be possible to alter over time, to add more detailed data or remove parts of the data, without major disruption to existing users of the data feed
* Data provided in the feed should be stored in an efficient manner, to avoid data duplication and excessive transaction costs
* The standard should be flexible enough to capture the majority of use-cases, even those that may not yet be conceived of at the writing of this document
* The standard should provide room for individual data providers to add their own data fields to a feed, without interfering with the common standard


### Data Format

The basis for this standard is the Concise Binary Object Representation (CBOR) data format, for which more information can be found here: [https://www.rfc-editor.org/rfc/rfc8949.html](https://www.rfc-editor.org/rfc/rfc8949.html) 

A central aspect of the CBOR standard that is used extensively is the concept of a Tag, which allows data consumers to identify and consume the types of data that they expect, and gracefully ignore other pieces of data that they are not interested in.

Similar to the CBOR standard this CIP will also propose a CBOR Tags Registry. Data providers are able to provide data according to the formats provided in this registry, and data consumers can discern the different available formats to pick the exact kind of data they need out of a feed.

To maintain compatibility with the main CBOR Tags Registry, the tags proposed in this are defined as an offset from Base Oracle Datum CIP Tag Number, which is defined later in this document. For example, Tag +5 would correspond to the actual number OracleDatumCipTagNumber + 5.


#### Detailed Format

Any data feed datum matching this standard must adhere to the following overall structure. Each of these individual elements is a Tag defined further later on.

The data structure consists of a list of Tags. This list is itself surrounded by a tag versioned to this major version of CIP. A later CIP may thus build on top of this standard by adding further datum after the initial one, using a different tag that allows older users of this CIP to disregard this new data.

There are 3 major categories of Tags, described in further detail later on, SharedData, GenericData and ExtendedData. In the list the ordering is defined as [ ? SharedData, 1* GenericData, ? ExtendedData ]. Or in plain english, a SharedData may optionally come first, then 1 or more GenericData in no particular order, and finally an ExtendedData may optionally come last.


### CIP CBOR Tags Registry

As additional use cases and data fields become necessary, this Tags Registry should be amended and updated to add new Tags and fields inside specific tags. Care should be taken to not change or remove existing Tags and fields inside specific tags, so as to maintain backwards compatibility to as great an extent as possible.

Tags are optional; data providers may provide multiple different tags covering the same data. The standard permits oracle feed providers to be flexible about what data they provide, while adhering to the standard. This allows feed consumers to programmatically discover what information is on the feed, while ignoring information that is not relevant to their use case.


### SharedData(Tag +0)

Data stored in this tag is considered to be auxiliary or supportive of the rest of the tags in the datum..

Data inside this tag is stored as a CBOR Mapping, the keys defined as positive integers and the values being defined on a per-case basis. The keys are defined here as enums, to give users of the standard a common understanding of what data is stored where. Each field in the mapping is optional.


*Keys-value mappings*


<table>
  <tr>
   <td><strong>Key</strong>
   </td>
   <td><strong>Value Data Type</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>0
   </td>
   <td>PriceMap
   </td>
   <td>Default values for any non-overridden PriceMap values
   </td>
  </tr>
  <tr>
   <td>1
   </td>
   <td>KYCList
   </td>
   <td>Default values for any non-overridden KYCList values
   </td>
  </tr>
</table>



### ExtendedData(Tag +1)

This tag is intended to store data provider specific data, where each data provider can define their own fields with a minimum of interference. Serves a similar purpose to SharedData, but is used for “global” data that isn’t considered broad enough in use to be defined in SharedData but still is considered valuable by a data provider.

Please note that a data provider may instead define their own tag to provide some specific type of data, if no existing registered tags are appropriate for the use case. Avoid putting such data in ExtendedData if possible, if instead the PriceData standard may be extended with the new tag, for example.

Key indices 0-100 are considered to be reserved for data entries defined by this CIP and future iterations of this CIP, but key indices 101 and above are considered free for any oracle provider to define as they wish. For use-cases that rely on a specific oracle providers custom data indices, please first check to ensure the ExtendedData is provided by the expected oracle provider by use of index 0 or 3.

Data inside this tag is stored as a CBOR Mapping, the keys defined as positive integers and the values being defined on a per-case basis. The keys are defined here as enums, to give users of the standard a common understanding of what data is stored where. Each field in the mapping is optional.


*Keys-value mappings*


<table>
  <tr>
   <td><strong>Key</strong>
   </td>
   <td><strong>Value Data Type</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>0
   </td>
   <td>Integer
   </td>
   <td>An index of the oracle provider providing this datum, see separately included registry in this CIP.
   </td>
  </tr>
  <tr>
   <td>1
   </td>
   <td>Integer
   </td>
   <td>The number of data sources involved in calculating the oracle data.
   </td>
  </tr>
  <tr>
   <td>2
   </td>
   <td>Integer
   </td>
   <td>The number of data provider nodes involved in verifying or signing the oracle data.
   </td>
  </tr>
  <tr>
   <td>3
   </td>
   <td>String
   </td>
   <td>POSSIBLE FUTURE ADDITION: A signature from the provider for oracle identity verification, where applicable. They must sign some data unique to this transaction that is verifiable by a datum / datum hash. Please define implementation.
   </td>
  </tr>
</table>



### PriceMap(Tag +2)

This tag represents a single price sample at a specific point in time.

Data inside this tag is stored as a CBOR Mapping, the keys defined as positive integers and the values being defined on a per-case basis. The keys are defined here as enums, to give users of the standard a common understanding of what data is stored where. Each field in the mapping is optional.

*Keys-value mappings*

<table>
  <tr>
   <td><strong>Key</strong>
   </td>
   <td><strong>Value Data Type</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>0
   </td>
   <td>Integer
   </td>
   <td>Price, or how many Quoted Currency is received per Base Currency spent
   </td>
  </tr>
  <tr>
   <td>1
   </td>
   <td>Integer
   </td>
   <td>POSIX Timestamp related to the time that the data was aggregated. 
   </td>
  </tr>
  <tr>
   <td>2
   </td>
   <td>Integer
   </td>
   <td>POSIX Timestamp related to the time that the oracle deems the data stale and/or expired.
   </td>
  </tr>
  <tr>
   <td>3
   </td>
   <td>Integer
   </td>
   <td>Decimals of Price
   </td>
  </tr>
  <tr>
   <td>4
   </td>
   <td>Integer
   </td>
   <td>ID of Base Currency
   </td>
  </tr>
  <tr>
   <td>5
   </td>
   <td>Integer
   </td>
   <td>ID of Quoted Currency
   </td>
  </tr>
  <tr>
   <td>6
   </td>
   <td>String
   </td>
   <td>Symbol of Base Currency
   </td>
  </tr>
  <tr>
   <td>7
   </td>
   <td>String
   </td>
   <td>Symbol of Quoted Currency
   </td>
  </tr>
  <tr>
   <td>8
   </td>
   <td>String
   </td>
   <td>Name of Base Currency
   </td>
  </tr>
  <tr>
   <td>9
   </td>
   <td>String
   </td>
   <td>Name of Quoted Currency
   </td>
  </tr>
</table>



### KYCList(Tag +3)

This tag represents 0-X Cardano addresses and what country the controlling user is KYC’ed as being a citizen or tax resident of.

Data inside this tag is stored as a CBOR Mapping, the keys defined as bytes representing Cardano addresses and the values being defined as a list of country codes as strings. Multiple country codes are to be interpreted as the address potentially belonging to any one of those.


```
cardano_public_key        = tstr
nationality               = tstr
whitelisted               = uint
```

<table>
  <tr>
   <td>

<strong>Key</strong>
   </td>
   <td><strong>Value Data Type</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>0
   </td>
   <td>String
   </td>
   <td>Cardano Address Public Key
   </td>
  </tr>
  <tr>
   <td>1
   </td>
   <td>String
   </td>
   <td>Nationality
   </td>
  </tr>
  <tr>
   <td>2
   </td>
   <td>Integer (boolean)
   </td>
   <td>Address is whitelisted for sale
   </td>
  </tr>
</table>

## Rationale

This CIP is ready to be made active; since it is a process standard, it requires no implementation.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
