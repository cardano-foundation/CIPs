---
CIP: ?
Title: Deterministic universal almost-unique Plutus Constructors
Category: Plutus
Status: Proposed
Authors:
    - Niels Mündler <niels@opshin.dev>
Implementors: [Niels Mündler <niels@opshin.dev>]
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/608
Created: 2023-10-20
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

Note: I will use record / Plutus Data exchangibly throughout the document.

## Abstract
Plutus Data on Cardano represent product types and are usually identified on chain by a combination of a constructor ID and their fields, 
i.e. for `type OptionalInt = None | Some (x:Integer)` we would get Plutus Data representing `None` with constructor ID 0 and no fields as well as Plutus Data representing `Some n` with constructor ID 1 and a single field with value `n` (an integer).
The existence and declaration of these constructor IDs are currently heavily focused around their origin in Haskell. They are usually used to distinguish different constructors of a single declared datatype.
In contrast, one may introduce universally recognized datatypes that are identified by a unique constructor id and can be expected to behave in a specified way (i.e. contain specific fields with specific types).
For this purpose, we introduce a generic way to compute an almost unique, deterministic and universal constructor id for objects based on their name and field types.
Note that it is not expected that every language adopts this standard as a default (i.e. for Haskell-like languages there might not be much use of it).
However, it is rather a recommendation for a choice in case interoperable datatypes with unique constructor ids are useful to an application (i.e. oracles) or language design (i.e. imperative languages).

## Motivation: why is this CIP necessary?

The current approach to constructor ids is heavily focused around the Haskell-ish way of defining record types.
An object can be one of a set of predefined set of entities, distinguished by constructor ids. I.e. the optional Redeemer type is either `Some Redeemer` or `None`.
Because we know that anything of optional integer type can be either two of these, only two numbers (0/1) are required to distinguish them.
If we introduce a third constructor (i.e. `Some Datum`), potentially all other constructors change and the two implementations are not compatible anymore.

Moreover there are other Plutus language frontends that allow freely declaring objects and mixing them into Union types (such as OpShin), which is akin to the imperative style of declaring classes.
This allows for example to declare a universally accepted type `Nothing` that can be freely mixed with `Redeemer` and `Datum` into `Union[Nothing, Redeemer, Datum]`.
The only requirement to ensure that this works properly is that all records that are mixed into the Union have distinct contstructor ids.
This is currently implemented manually, which is tedious and a potential source of errors.

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned. If a proposal defines structure of on-chain data it must include a CDDL schema in it's specification.-->
The deterministic, universal and almost-unique Plutus constructors are computed recursively based on the type definition of a record.
We first compute a string `ustr(X)` based on the type definition of X. Then we perform a sha256 hash on the UTF8 encoding of this string and interpret the resulting hex digest as a big endian encoded integer.
The integer is taken modulo 2^32. The resulting integer is the almost-unique, universal, deterministic constructor id of the plutus datum.

The following function describes how to compute `ustr(X)` for a type recursively.

```
ustr(bytes) := "bytes"
ustr(integer) := "int"
// This covers the case where the structure of the object is now known from the perspective of the class, i.e. when any BuiltinData is allowed
ustr(PlutusData) := "any"
  // This covers the case where the type of the elements in the list are not known in advance
ustr(list) := "list"

ustr(list<X>) := "list<" + ustr(X) + ">

ustr(map<X,Y>) := "map<" + ustr(X) + "," + ustr(Y) + ">"

ustr(union<X,Y,...,Z>) := "union<" + ustr(X) + "," + ustr(Y) + "," + ... + "," + ustr(Y) + ">"

ustr(constr(name)<id, fields[f1:X,f2:Y,...,fn:Z]>) :=
    "cons[" + name + "](" + str(id) + ";"
    + f1 + ":" + ustr(X) + "," + f2 + ":" + ustr(Y) + "," + ... + "," + fn + ":" + ustr(Z) +
    ")"
```

Where `name` and `f1` to `fn` refer to the name of the record and the names of its fields respectively.
Since the constructor id of a records is not known when computing its constructor id, the constructor id string is set to `_` for this computation.
As an example, the constructor id of record `A` with fields `b` (record `B`, constructor id 5 with one integer field `i`) and `c` (integer) would result in `ustr(A) = ustr(constr(A)<_,fields[b:B,c:integer]>) = "cons[A](_;b:" + ustr(constr(B)<5,fields[i:integer]>) + ",c:int)" = "cons[A](_;b:cons[B](i:int),c:int)"`.

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->
We definetly want a few properties on the CONSTR_IDs

- _small_: ideally the constr_id integer should be as small as possible, as smaller integers are encoded more efficiently in CBOR and save the end user minutxo and txfees (constr_ids are encoded as the cbor tag up to 7 bit size, after that encoded as generic integer)
- _unique_: There should be as little overlap with other values as possible, so that we can group together classes in unions without having to worry about setting/overwriting the constr id. This is reflected by the unique choice of identifiers in `ustr` and rules out the traditional Haskell approach.
- _deterministic_: Datatypes that are defined in libraries may be imported in arbitrary contexts. the constr_id must therefore not depend on i.e. what other Unions the datatype is being used in or what other datatypes are declared in its surroundings. This rules out any automatically incrementing global counters.

Note that the implementation first computes a `ustr` in human readable form and then transforms it into an integer. This is intentional, since the alternatives (directly computing a large unique number or similar approaches) are much more difficult to debug.

To ensure that there is no accidental overlap in constructor ids due to having same fields in different applications (i.e. `NegInfPosixTime` and `PosInfPosixTime` without any fields), names of records are taken into account for the computation of the constructor id.

There is no issue with backwards compatability when adopting this implementation as an opt-in choice for users.
PlutusTx and most other languages allow explicitly setting the constructor id of objects anyways.
Note that due to determinism, types defined this way can be supported in third party languages as well by hard coding the computed constructor id and overwriting the default of the implementation language.


## Path to Active

### Acceptance Criteria
- Implementation in at least one Smart Contract Language

### Implementation Plan
- Implementation in pycardano / OpShin. See the reference implementation [here](https://github.com/Python-Cardano/pycardano/pull/272).

## Copyright

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)


