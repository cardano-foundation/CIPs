---
CIP: 19
Title: Cardano Addresses
Status: Active
Category: Ledger
Authors:
  - Matthias Benkort <matthias.benkort@cardanofoundation.org>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/78
Created: 2020-03-25
License: CC-BY-4.0
---

## Abstract

This specification describes the structure of addresses in Cardano, covering both addresses introduced in the Shelley era and the legacy format from the Byron era.

## Motivation: why is this CIP necessary?

Document design choices for posterity. Most applications interacting with the Cardano blockchain will likely not have any need for this level of details, however, some might. This CIP is meant to capture this knowledge. 

## Specification

### Introduction

In Cardano, an address is a **sequence of bytes** that conforms to a particular format, which we describe below.

However, users will typically come into contact with addresses only after these addresses have been **encoded** into sequences of human-readable characters. In Cardano, the [Bech32][] and [Base58][] encodings are used to encode addresses, as opposed to standard hexadecimal notation (Base16, example `0x8A7B`). These encoded sequence of characters have to be distinguished from the byte sequences that they encode, but lay users will (and should) perceive the encoded form as "the" address.

### User-facing Encoding

By convention, **Shelley** and stake addresses are encoded using **[Bech32][]**, with the exception that Cardano does not impose a length limit on the sequence of characters. The human-readable prefixes are defined in [CIP-0005][]; the most common prefix is `addr`, representing an address on mainnet. Bech32 is the preferred encoding, as its built-in error detection may protect users against accidental misspellings or truncations.

Again by convention, **Byron** addresses are encoded in **[Base58][]**.

Historically, Byron addresses were introduced before the design of Bech32, which solves various issues of the Base58 encoding format (see [Bech32's motivation](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki#motivation) for more detail). Byron addresses were however kept as Base58 to easily distinguish them from new addresses introduced in Shelley, massively making use of Bech32 for encoding small binary objects.

Cave: In principle, it is possible for a Shelley address to be encoded in Base58 and a Byron address to be encoded in Bech32 (without length limit). However, implementations are encouraged to reject addresses that were encoded against convention, as this helps with the goal that lay users only encounter a single, canonical version of every address.

Examples of different addresses encoded in different eras:

| Address Type | Encoding | Example                                                                                                              |
| ---          | ---      | ---                                                                                                                  |
| Byron        | Base58   | `37btjrVyb4KDXBNC4haBVPCrro8AQPHwvCMp3RFhhSVWwfFmZ6wwzSK6JK1hY6wHNmtrpTf1kdbva8TCneM2YsiXT7mrzT21EacHnPpz5YyUdj64na` |
| Shelley      | bech32   | `addr1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5eg0yu80w`                                                         |
| stake        | bech32   | `stake1vpu5vlrf4xkxv2qpwngf6cjhtw542ayty80v8dyr49rf5egfu2p0u`                                                        |

### Binary format

In Cardano, the sequence of bytes (after decoding with Bech32 or Base58) that represents an address  comprises two parts, a one-byte **header** and a **payload** of several bytes. Depending on the header, the interpretation and length of the payload varies. 

In the header-byte, bits [7;4] indicate the type of addresses being used; we'll call these four bits the **header type**. The remaining four bits [3;0] are either unused or refer to what we'll call the **network tag**. There are currently 11 types of addresses in Cardano which we'll divide into three categories: [Shelley addresses], [stake addresses], and [Byron addresses]. 

```
  1 byte     variable length   
 <------> <-------------------> 
┌────────┬─────────────────────┐
│ header │        payload      │
└────────┴─────────────────────┘
    🔎                          
    ╎          7 6 5 4 3 2 1 0  
    ╎         ┌─┬─┬─┬─┬─┬─┬─┬─┐ 
    ╰╌╌╌╌╌╌╌╌ │t│t│t│t│n│n│n│n│ 
              └─┴─┴─┴─┴─┴─┴─┴─┘ 
```

See also the more detailed [ABNF grammar in annex].

#### Network Tag

Except for [Byron addresses] (type 8 = `1000`), the second half of the header (bits [3;0]) refers to the network tag which can have the following values and semantics. Other values of the network tag are currently reserved for future network types. In the case of [Byron addresses], bits [3;0] have a completely separate definition detailed in the section below.

Network Tag (`. . . . n n n n`)   | Semantic
---                               | ---
`....0000`                        | Testnet(s) 
`....0001`                        | Mainnet


#### Shelley Addresses 

There are currently 8 types of Shelley addresses summarized in the table below:

Header type (`t t t t . . . .`) | Payment Part     | Delegation Part
---                             | ---              | ---
(0) `0000....`                  | `PaymentKeyHash` | `StakeKeyHash`
(1) `0001....`                  | `ScriptHash`     | `StakeKeyHash`
(2) `0010....`                  | `PaymentKeyHash` | `ScriptHash`
(3) `0011....`                  | `ScriptHash`     | `ScriptHash`
(4) `0100....`                  | `PaymentKeyHash` | `Pointer`
(5) `0101....`                  | `ScriptHash`     | `Pointer`
(6) `0110....`                  | `PaymentKeyHash` | ø
(7) `0111....`                  | `ScriptHash`     | ø

- `PaymentKeyHash` and `StakeKeyHash` refer to `blake2b-224` hash digests of Ed25519 verification keys. How keys are obtained is out of the scope of this specification. Interested readers may look at [CIP-1852] for more details.

- `ScriptHash` refer to `blake2b-224` hash digests of serialized monetary scripts. How scripts are constructed and serialized is out of the scope of this specification.

- `Pointer` is detailed in the section below.

##### Payment part

Fundamentally, the first part of a Shelley address indicates the ownership of the funds associated with the address. We call it the **payment part**. Whoever owns the payment parts owns any funds at the address. As a matter of fact, in order to spend from an address, one must provide a witness attesting that the address can be spent. In the case of a `PaymentKeyHash`, it means providing a signature of the transaction body made with the signing key corresponding to the hashed public key (as well as the public key itself for verification). For monetary scripts, it means being able to provide the source script and meet the necessary conditions to validate the script. 

##### Delegation part

The second part of a Shelley address indicates the owner of the stake rights associated with the address. We call it the **delegation part**. Whoever owns the delegation parts owns the stake rights of any funds associated with the address. In most scenarios, the payment part and the delegation part are owned by the same party. Yet it is possible to construct addresses where both parts are owned and managed by separate entities. We call such addresses **mangled addresses** or **hybrid addresses**. 

Some addresses (types 6 and 7) carry no delegation part whatsoever. Their associated stake can't be delegated. They can be used by parties who want to prove that they are not delegating funds which is typically the case for custodial businesses managing funds on the behalf of other stakeholders. Delegation parts can also be defined in terms of on-chain [pointers]. 

##### Pointers

> **Note**
> From the Conway ledger era, new pointer addresses cannot be added to Mainnet.

In an address, a **chain pointer** refers to a point of the chain containing a stake key registration certificate. A point is identified by 3 coordinates:

- An absolute slot number 
- A transaction index (within that slot)
- A (delegation) certificate index (within that transaction)

These coordinates form a concise way of referring to a stake key (typically half the size of a stake key hash). They are serialized as three variable-length positive numbers following the ABNF grammar here below:

```abnf
POINTER = VARIABLE-LENGTH-UINT ; slot number
        | VARIABLE-LENGTH-UINT ; transaction index
        | VARIABLE-LENGTH-UINT ; certificate index

VARIABLE-LENGTH-UINT = (%b1 | UINT7 | VARIABLE-LENGTH-UINT) 
                     / (%b0 | UINT7)

UINT7 = 7BIT 
```

#### Stake Addresses

Like [Shelley addresses], stake addresses (also known as **reward addresses**) start with a single header byte identifying their type and the network, followed by 28 bytes of payload identifying either a stake key hash or a script hash. 

Header type (`t t t t . . . .`) | Stake Reference
---                             | ---
(14) `1110....`                  | `StakeKeyHash`
(15) `1111....`                  | `ScriptHash`

- `StakeKeyHash` refers to `blake2b-224` hash digests of Ed25519 verification keys. How keys are obtained is out of the scope of this specification. Interested readers may look at [CIP-1852] for more details.

- `ScriptHash` refers to `blake2b-224` hash digests of serialized monetary scripts. How scripts are constructed and serialized is out of the scope of this specification.

#### Byron Addresses

Before diving in, please acknowledge that a lot of the supported capabilities of Byron addresses have remained largely unused. The initial design showed important trade-offs and rendered it unpractical to sustain the long-term goals of the network. A new format was created when introducing Shelley and Byron addresses were kept only for backward compatibility. Byron addresses are also sometimes called **bootstrap addresses**.


Like many other objects on the Cardano blockchain yet unlike Shelley addresses, Byron addresses are [CBOR]-encoded binary objects. Conveniently enough, the first 4 bits of their first byte are always equal to `1000....` which allows us to land back on our feet w.r.t to the address type. Their internal structure is however vastly different and a bit unusual. 

```
┌────────┬──────────────┬────────┐
│  root  │  attributes  │  type  │
└────────┴──────────────┴────────┘
  ╎        ╎              ╎ 
  ╎        ╎              ╰╌╌ Standard   
  ╎        ╎              ╰╌╌ Redeem
  ╎        ╎ 
  ╎        ╰╌╌ Derivation Path
  ╎        ╰╌╌ Network Tag    
  ╎
  ╎                   ┌────────┬─────────────────┬──────────────┐
  ╰╌╌╌╌ double-hash ( │  type  │  spending data  │  attributes  │ )
                      └────────┴─────────────────┴──────────────┘
                                 ╎        
                                 ╰╌╌ Verification Key
                                 ╰╌╌ Redemption Key
```

The address `root` uniquely identifies the address and is a double-hash digest (SHA3-256, and then Blake2b-224) of the address type, spending data, and attributes. 

Then comes the address attributes which are both optional. The network tag is present only on test networks and contains an identifier that is used for network discrimination. The [derivation path] (detailed below) was used by legacy so-called random wallets in the early days of Cardano and its usage was abandoned with the introduction of Yoroi and so-called **Icarus addresses**. 

Finally, the address type allows for distinguishing different sub-types of Byron addresses. **Redeem addresses** are used inside the Byron genesis configuration and were given to early investors who helped to fund the project. 

A full and more detailed [CDDL specification of Byron addresses] is given in the annex to the CIP. 

##### Derivation path 

Historically, Cardano wallets have been storing information about the wallet structure directly within the address. This information comes in the form of two derivation indexes (in the sense of child key derivation as defined in [BIP-0032]) which we call **derivation path**. To protect the wallet's anonymity, the derivation path is stored encrypted using a ChaCha20/Poly1305 authenticated cipher. 

### Test Vectors

All test vectors below use the following payment key, stake key, script and pointer:

- `addr_vk1w0l2sr2zgfm26ztc6nl9xy8ghsk5sh6ldwemlpmp9xylzy4dtf7st80zhd`
- `stake_vk1px4j0r2fk7ux5p23shz8f3y5y2qam7s954rgf3lg5merqcj6aetsft99wu`
- `script1cda3khwqv60360rp5m7akt50m6ttapacs8rqhn5w342z7r35m37`
- `(2498243, 27, 3)`

```yaml
mainnet:
    type-00: addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3n0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgse35a3x
    type-01: addr1z8phkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gten0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgs9yc0hh
    type-02: addr1yx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzerkr0vd4msrxnuwnccdxlhdjar77j6lg0wypcc9uar5d2shs2z78ve
    type-03: addr1x8phkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gt7r0vd4msrxnuwnccdxlhdjar77j6lg0wypcc9uar5d2shskhj42g
    type-04: addr1gx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer5pnz75xxcrzqf96k
    type-05: addr128phkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gtupnz75xxcrtw79hu
    type-06: addr1vx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzers66hrl8
    type-07: addr1w8phkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gtcyjy7wx
    type-14: stake1uyehkck0lajq8gr28t9uxnuvgcqrc6070x3k9r8048z8y5gh6ffgw
    type-15: stake178phkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gtcccycj5

testnet:
    type-00: addr_test1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3n0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgs68faae
    type-01: addr_test1zrphkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gten0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgsxj90mg
    type-02: addr_test1yz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzerkr0vd4msrxnuwnccdxlhdjar77j6lg0wypcc9uar5d2shsf5r8qx
    type-03: addr_test1xrphkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gt7r0vd4msrxnuwnccdxlhdjar77j6lg0wypcc9uar5d2shs4p04xh
    type-04: addr_test1gz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer5pnz75xxcrdw5vky
    type-05: addr_test12rphkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gtupnz75xxcryqrvmw
    type-06: addr_test1vz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzerspjrlsz
    type-07: addr_test1wrphkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gtcl6szpr
    type-14: stake_test1uqehkck0lajq8gr28t9uxnuvgcqrc6070x3k9r8048z8y5gssrtvn
    type-15: stake_test17rphkx6acpnf78fuvxn0mkew3l0fd058hzquvz7w36x4gtcljw6kf
```
## Rationale: how does this CIP achieve its goals?

As stated in [Motivation](#motivation-why-is-this-cip-necessary) this CIP is provided for informational purposes regarding a single deliberate design. Further rationale and motivation for this design are available in the [Design Specification for Delegation and Incentives in Cardano - Section 3.2 :: Addresses & Credentials ](https://github.com/intersectmbo/cardano-ledger/releases/latest/download/shelley-delegation.pdf).

### Reference Implementation(s)

- [IntersectMBO/cardano-addresses (Byron & Shelley)](https://github.com/IntersectMBO/cardano-addresses)

- [IntersectMBO/cardano-ledger-specs (Byron)](https://github.com/IntersectMBO/cardano-ledger-specs/blob/d5eaac6c4b21a8e69dc3a5503a72e3c3bfde648e/byron/ledger/impl/src/Cardano/Chain/Common/Address.hs)

- [IntersectMBO/cardano-ledger-specs (Shelley)](https://github.com/IntersectMBO/cardano-ledger-specs/blob/1e7e6e03a46e8118b318ed105214767aec0f3976/shelley/chain-and-ledger/executable-spec/src/Shelley/Spec/Ledger/Address.hs)

## Path to Active

### Acceptance Criteria

- [x] Confirmation by consensus, with no reported dispute since publication, that this document fully descibes how Cardano addresses are universally implemented.

### Implementation Plan

- [x] Publish this documentation for confirmation that it accurately describes conventionals of universal use.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[ABNF grammar in annex]: https://raw.githubusercontent.com/cardano-foundation/CIPs/master/CIP-0019/CIP-0019-cardano-addresses.abnf
[base58]: https://tools.ietf.org/id/draft-msporny-base58-01.html
[bech32]: https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
[BIP-0032]: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
[Byron addresses]: #byron-addresses
[CBOR]: https://www.rfc-editor.org/rfc/rfc8949
[CDDL specification of Byron addresses]: https://raw.githubusercontent.com/cardano-foundation/CIPs/master/CIP-0019/CIP-0019-byron-addresses.cddl
[CIP-0005]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0005
[CIP-1852]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852
[derivation path]: #derivation-path
[pointers]: #pointers
[Shelley addresses]: #shelley-addresses
[Stake addresses]: #stake-addresses
