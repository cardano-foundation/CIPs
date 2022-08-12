---
CIP: "???"
Title: optimized UPLC serialization  
Authors: Michele Nuzzi <michele.nuzzi.2014@gamil.com> 
Discussions-To: TBD
Comments-Summary: TBD  
Comments-URI: TBD  
Status: Draft  
Type: Standards Track  
Created: <date created on, in ISO 8601 (yyyy-mm-dd) format>  
License: CC-BY-4.0  
License-Code: Apache-2.0  
Post-History: <dates of postings to Cardano Dev Forum, or link to thread>  
---

## Abstract

this document describes the parts of the current serialization algorithm that can be improved and provides the specification and documentation needed in order to implement an optimized version of this one.

## Motivation

all Untyped Plutus Core Programs do need to be serialized in order to be included in a transaction (therefore stored on-chain);

the current serialization algorithm is based on the [flat](http://quid2.org/docs/Flat.pdf) algorithm;

this allows for a bit-oriented serialized program; but there are aspects that can be improved to further reduce the size of the serialized program;

the major benefit of a uplc-optimized algorithm is the possibility to store more complex logic (or more in general, more complex transactions) on chain without the need to increase the transaction size limit.

## Specification

### Table of contents

- [```pad0``` should add nothing](#pad0)
- [constant's types list should work as Integer ones](#constT)
- [remove the "type application" tag for constant types](#tyApp)
- [```ByteString```s encoded as unsinged integer followed by the bytes](#ByteStrings)
- [```data``` serialization
](#data)

<a name="pad0"></a>

### ```pad0``` should add nothing rather than an entire byte

sometimes it is necessary to allign the serialized program (partial or total) to fit into a byte;

in order to do so, some padding is added based on the current bit-length of the program;

the needed padding can be obtained as follows
```ts
pad( 8 - (currBitLength % 8) )
```
where the ```pad``` function could be defined as follows in typescript
```ts
pad( missingBits: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 ): string
{
    switch( missingBits )
    {
        case 0: return "00000001";
        case 1: return "1";
        case 2: return "01";
        case 3: return "001";
        case 4: return "0001";
        case 5: return "00001";
        case 6: return "000001";
        case 7: return "0000001";
    }
}
```
the case in which the ```missingBits``` is 0 implies that the current serialized program is already byte-alligned and, since this padding carries no usefull informations, the current ```pad( 0 )``` adds a useless byte each time a padding is needed and the number of used bits is a multiple of 8.

An alternative implementation would be
```ts
pad( missingBits: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 ): string
{
    switch( missingBits )
    {
        case 0: return "";
        case 1: return "1";
        case 2: return "01";
        case 3: return "001";
        case 4: return "0001";
        case 5: return "00001";
        case 6: return "000001";
        case 7: return "0000001";
    }
}
```

this modification would make the padding deserialization contex-dependent (just like the serialization already is) but saves a byte 1 time every 8 ( probably more ofthen due to the high presence of tags and items of which serialization has a bit-length of a multiple of 4 )

<a name="constT"></a>

### constant's types list should work as Integer ones

citing the draft plutus core specification paper of june 2022 

> (Appendix D, Section D.3.3, page 31 )
> We define the encoder and decoder for [ constant ] types by combining 𝖾 𝗍𝗒𝗉𝖾 and 𝖽 𝗍𝗒𝗉𝖾 with 𝖤 and decoder for lists of four-bit integers (See section D.2)

> (Appendix D, Section D.2.2, page 31 )
> Suppose that we have a set 𝑋 for which we have defined an encoder 𝖤 𝑋 and a decoder 𝖣 𝑋 ; we define an 𝑋 which encodes lists of elements of 𝑋 by emitting the encodings of the elements of the list, encoder 𝖤 each preceded by a 𝟷 bit, then emitting a 𝟶 bit to mark the end of the list.

from what cited above we can understand that the current constant's types serialization works exactly as the list one, in particoular a list of 4 bit values.

this encoding takes care also of the "empty list" case which is never the case for well formed list of types.

this means that an empty list encodes as ```0``` (nil constructor + no data) and a generic (simple) type encodes as ```1 xxxx 0``` ( cons construcotr + tag + nil constructor )

for lists that are non empty ( such as 7 bits lists used for unsigned integers serialization ) the constructor always carries data (since of course is non-empty) and this allows to remove the last bit.

the same should be applied to constant's types so that a generic (simple) type serializes as ```0 xxxx```( nil construcotr + tag )

#### some examples

```
int ->   0 0000 
# before 1 0000 0
```

> **NOTE**: see "[remove the "type application" tag for constant types](#tyApp)" below
```
list int -> 1 0101 0 0000 
# before    1 0111 1 0101 0 0000
```

> **NOTE**: see "[remove the "type application" tag for constant types](#tyApp)" below
```
pair int bytestring -> 1 0110 1 0000 0 0001
# before               1 0111 1 0111 1 0110 1 0000 1 0001 0
```

<a name="tyApp"></a>

### remove the "type application" tag for constant types

as per specification constant terms are typed using tags.

these tags are serialized as 4 bits and currently so 16 options ( 0 to 15 inclusive ) of wich 9 are used as follows

type        | binary | decimal
------------|--------|--------
integer     | 0000   | 0
bytestring  | 0001   | 1
string      | 0010   | 2
unit        | 0011   | 3
bool        | 0100   | 4
list        | 0101   | 5
pair        | 0110   | 6
type app    | 0111   | 7
data        | 1000   | 8

tags from ```integer``` to ```bool``` and the ```data``` one are directly followed by the respective value encoding;

tags ```list``` and ```pair``` are the only reason the ```type application``` tag is presente, and those tags always require some other type in order to be valid, so the type application is implcit and it should be removed.

during serialization this saves 4 bits for each ```lsit``` tag ( ```0111 0101``` becomes ```0101``` ) and 8 bits for pair tags which requires 2 type applications to be satisfied ( ```0111 0111 0110``` becomes ```0110``` )

to help backwards compatibitlity with exsisting serializaations algoritms the new table would look like

type        | binary | decimal
------------|--------|--------
integer     | 0000   | 0
bytestring  | 0001   | 1
string      | 0010   | 2
unit        | 0011   | 3
bool        | 0100   | 4
list        | 0101   | 5
pair        | 0110   | 6
data        | 1000   | 8

even if the remotion of the tag  would allow to reduce the size of every tag, further reducing the size of constants by 1 bit per constant at the cost of missing bits for expansion in the evenience new constant types will be added

if the cost is acceptable ( needs to be discussed with the comunity ) an even better soultion would be to encode constant types as follows

type        | binary | decimal
------------|--------|--------
integer     | 000    | 0
bytestring  | 001    | 1
string      | 010    | 2
unit        | 011    | 3
bool        | 100    | 4
list        | 101    | 5
pair        | 110    | 6
data        | 111    | 7

<a name="ByteStrings"></a>

### ```ByteString```s encoded as unsinged integer followed by the bytes

ByteStrings are probably the values that have the most important impact on the serialized output;

Bytestrings are used to represent a wide variety of types (```TokenName```, ```ValidatorHash```, ```PubKeyHash```, ```CurrencySymbol```, etc. are all ```ByteString``` wrappers ) ence widely used in smart contracts.

citing the plutus core specificaiton draft released in june 2022 (latest specification at the time of writing)

> Bytestrings are encoded by dividing them into nonempty blocks of up to 255 bytes and emitting each block in sequence.
>
> Each block is preceded by a single unsigned byte containing its length, and the end of the encoding is marked by a zero-length block (so the empty bytestring is encoded just as a zero-length block).
>
> Before emitting a bytestring, the preceding output is padded so that its length (in bits) is a multiple of 8;
>
> if this is already the case a single padding byte is still added; this ensures that contents of the bytestring are aligned to byte boundaries in the output.

given the importance of bytestrings too much hoverhead is introduced; currently a ```ByteString``` serializes as

```
1) some padding that, depending on the context, may take up to 1 byte
2) 1 (byte * chunk) indicating how many bytes are in the very next chunk
3) 0 to 255 meaningful (bytes * chunk)
4) 1 useless byte indicating no more chiunks are following
```
this implies ```(~1) + #chunks + 1``` meaningless bytes are added per ```ByteString```

in the descripton above
- step ```1``` allows for an easy serialization and deserialization but doesn't carries any meaningful informations; given the importance of ByteStrings it should be removed at the cost of an added shift while serializing/deserializing the value
- step ```4``` can be removed as it is simply useless
- step ```3``` can be optimized using unsigned integer encoding

the new algorithm for ```ByteString``` serialization would consist of two parts:
```
1) Unsigned (indefinite length) Integer indicating how many bytes ( or chunks of 8 bits ) are following
2) as many bytes as specified in the Unsigned Integer at step 1
```

using the new algorithm the ```ByteString``` serialization space complexity goes form ```O(n)``` to ```O(log n)``` where ```n``` is the number of bytes in the ```ByteString``` 

<a name="data"></a>

### ```data``` serialization

All the effort of minimizing the size of on-chain scripts by prefering ```flat``` over ```CBOR``` serialization are ignored when it comes to ```data``` serialization.

citing the june 2022 plutus core specification ( Appendix B, Section B.2, Note 1; page 23 )

> The ```serialiseData``` function takes a 𝚍𝚊𝚝𝚊 object and converts it into a CBOR (Bormann and Hoffman [2020]) object. The encoding is based on the Haskell Data type described in Section A.1.
> 
> A detailed description of the encoding will appear here at a later date, but for the time being see the Haskell code in 
> [plutus-core/plutus-core/src/PlutusCore/Data.hs](https://github.com/input-output-hk/plutus/blob/master/plutus-core/plutus-core/src/PlutusCore/Data.hs) ([```encodeData``` line](https://github.com/input-output-hk/plutus/blob/9ef6a65067893b4f9099215ff7947da00c5cd7ac/plutus-core/plutus-core/src/PlutusCore/Data.hs#L139))
> in the [Plutus GitHub repository](https://github.com/input-output-hk/plutus) IOHK [2019] for a definitive implementation.

so currently ```Data``` types are encoded by converting the value to ```CBOR``` and the using the ```ByteString``` encoder [using chunks of 64 bytes max each](https://github.com/input-output-hk/plutus/blob/9ef6a65067893b4f9099215ff7947da00c5cd7ac/plutus-core/plutus-core/src/PlutusCore/Data.hs#L84)

this implementation is very inconvinient considering that ```Data``` has only [5 construtors](https://github.com/input-output-hk/plutus/blob/9ef6a65067893b4f9099215ff7947da00c5cd7ac/plutus-core/plutus-core/src/PlutusCore/Data.hs#L40).

```hs
data Data =
      Constr Integer [Data]
    | Map [(Data, Data)]
    | List [Data]
    | I Integer
    | B ByteString
```

a more efficient implementation could be obtained by introducing some tags for the various construcors, each taking 3 bits:

data constructor | binary | decimal
-----------------|--------|--------
Constr           | 000    | 0
Map              | 001    | 1
List             | 010    | 2
I                | 011    | 3
B                | 100    | 4

directly followed by the respective serialized value; in particoular

- ```Constr``` is followed by an **unsigned** integer and the a list of ```Data```
- ```Map``` is followed by a list of ```Data``` pairs; where the paris are serialized as in the constant pair specification (only the value)
- ```List``` is folloed by a list of ```Data``` elements
- ```I``` is followed by a **signed** integer
- ```B``` is followed by a ```ByteString``` 

An important **alternative design** that should be considered and discussed with the comunity would see the ```Data``` type requiring only 4 tags which would then be:

data tag  | binary | decimal
----------|--------|--------
data-pair | 00     | 0
data-list | 01     | 1
data-int  | 10     | 2
data-bs   | 11     | 3

and the constructors would map to:

- ```Constr``` becomes a ```data-pair``` expecting an unsigned integer and a list of ```Data```
- ```Map``` becomes a ```data-list``` containing 2 ```Data``` per element
- ```List``` becomes a ```data-list``` containing 1 ```Data``` per element
- ```I``` becomes a ```data-int``` tag expecting a signed integer
- ```B``` becomes a ```data-bs``` tag expecting a ```ByteString```

this design is unambigous since ```data-list``` that maps back to two of the constructors contains different values depending on what Constructor is intended.

the only edge case for the ```data-list``` constructor is the empty list, but the problem can be easly solved by expecting one single bit only in the case of the empty list indicating the intended constructor.

so the empty ```Map``` would serialize as
```
01 # data-list tag
0  # list nil construcor ( empty list )
0  # bit indicating Map data constructor
```
and the empty ```List``` as
```
01 # data-list tag
0  # list nil construcor ( empty list )
1  # bit indicating List data constructor
```

the second design also implies no more ```Data``` constructors will be added in the future, or that for those added it will be possible to find an unambigous representation using the ones specified.

## Rationale

This proposal suggest ways to reduce serialized scripts size.

the changes where designed to keep the bit oriented style of flat minimizing the number of required bits for values where possible.

## Backward Compatibility

the proposed changes to the algorithm will cause the same UPLC Abstract Syntaxt Tree to serialize in a different way based on the algorithm used;

In order to allow the deserializaton process to handle the old serialization algorithm the version of the program sholud be chcked first.

since the new algorithm introduces changes that are breaking the major number in the version should change;

in particoular programs using versions that match ```0.*.* <= version <= 1.*.*``` will be serialized using the old specification, while programs with version ```2.*.* <= version``` will be serialized using the modifications specified in this CIP.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
