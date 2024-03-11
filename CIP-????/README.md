---
CIP: ?
Title: Representing the Script Context as a Sums-of-Products Term
Authors: 
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors: 
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Status: Proposed
Category: Plutus
Created: 2023-04-20
Discussions: 
  - https://github.com/cardano-foundation/CIPs/pull/455
License: CC-BY-4.0
---

## Abstract

Plutus scripts receive information about the transaction currently being validated by being passed an argument containing that information, called the "script context".
The script context is currently represented in Plutus Core using the `Data` builtin type. 
This is slow to process, so we propose to use the support for sums-of-products (SOPs) in Plutus Core (proposed in CIP-85) to represent the script context directly as a term using sums-of-products.

## Motivation: why is this CIP necessary?

### Background

This CIP assumes familiarity with the concepts described in CIP-85, including SOPs and the origin of `Data`.

### The Problem

The problem is:
1. It is slow to perform any kind of manipulation of the script context (see CIP-85 for benchmarking of operations on `Data` versus SOPs)
2. Translating ("decoding") the script context into a native form ([Scott encoding][] or SOPs) is far too slow because of 1 and because script contexts become large

These combine to make decoding real world script contexts prohibitive in many cases:
budget profiling of examples in `plutus-use-cases` that naively decode the script context revealed that many were spending 30-40% of their budget just on the decoding step, which is unacceptable.

In reality, this is well known among developers, and most have moved to _not_ decoding the script context, and instead working directly with the underlying `Data` object.
This is slow and error-prone, but at least provides a workaround.

## Specification

A new Plutus ledger language L is added to the ledger.
The Plutus Core language version 1.1.0 is both allowed and required in L (since the changes to the ledger-script interface will require sums-of-products). 

The ledger-script interface changes in L as follows:
- Instead of the script context argument being a `Data` object, it is now a Plutus Core term.
- The translation of the script context into `Data` is replaced by a translation of the script context into a Plutus Core term.

The full specification of the new translation is to be determined in collaboration with the ledger team, but broadly:
- Integers and bytestrings are translated to Plutus Core integers and bytestrings instead of using the `I` and `B` Data constructors.
- Constructors are translated to Plutus Core `constr` terms instead of using the Data `Constr` constructor.
- Uses of the `Map` and `List` Data constructors will need more specific handling but will be translated in line with their underlying dataype representation in Plutus Core.

## Rationale: how does this CIP achieve its goals?

This CIP solves the problem in the most drastic way possible: it removes it entirely.
With the proposed ledger interface changes the script context is passed across _already decoded_, so there is zero work for the script to do.
It can immediately operate on it efficiently.

### Discussion

#### Is this still worth it if users aren't decoding the script context?

The issues with decoding the script context only apply to users who actually try and decode it; many people have moved on to just using the underlying `Data` object instead.
This is a totally reasonable workaround, but it would still benefit those users to have a SOP script context to operate on instead, because they can do so more efficiently that on `Data` (see CIP-85 for benchmarks of operations on `Data` versus SOPs).

#### Why not also make datums and redeemers SOP terms instead of `Data`?

It is always nice to get rid of things, and this CIP does _not_ let us get rid of `Data` as a Plutus Core builtin type, because `Data` is still used for redeemers and datums.
That begs the question: could we also have redeemers and datums be passed as SOP terms instead of values of type `Data`?

The problem is that, unlike the encoded script context, redeemers and datums are _user facing_.
They appear in the block format, they can be supplied by users (e.g. directly at the CLI!), and they can be inspected in block explorers.
There is therefore a significant benefit to having them in a simpler format that is easier to work with.
If they were Plutus Core terms in generality, we could have all kinds of strange things like people embedding functions in them.

So it still seems beneficial to have redeemers and datums being `Data`.

See "Alternatives: Convert Redeemers and Datums to Sums-of-Products Rather Than Builtin Data" for a variant.

#### What about users who rely on the script context being `Data`?

We know of two cases where it is actively desirable for the script context to be in the form of `Data`:

1. Serialization/hashing, as described in the motivation for CIP-42
2. Equality checking, e.g. searching for a particular output in the transaction output list

It's likely that this CIP will negatively affect these use cases, since it would mean that users would need to either

1. Write a hashing/equality function that operates recursively on the script context object
2. Convert the script context back to `Data` in order to use the builtin operations

Both of these approaches are likely to be much more expensive than using the `Data` builtins today.
We benchmarked a recursive equality function over script contexts and it is indeed over 30x worse.
This is a serious problem without a current workaround and is likely blocking for this proposal until resolved.

#### Do we need an untyped way of interacting with sums-of-products objects?

Today, for users operating in a typed setting, using the raw `Data` representation of the script context has an advantage apart from speed: it avoids needing all the type definitions for the many parts of the script context, instead using only the single builtin type `Data`.
This can lead to lower script sizes, depending on the tooling being used.

One response is to say that this is an optimization problem for said tooling: they should try harder to ensure that everything relating to type definitions gets optimized away in the end.
But we might also want to think about ways to allow people to operate with objects encoded using sums-of-products in a similar untyped way to what they can do with `Data`.

However, this is all a problem for tools that produce Plutus Core, and seems solvable, so we do not need to solve it in this CIP, and can leave it to the tooling authors to solve later.

### Alternatives

#### Convert Redeemers and Datums to Sums-of-Products Rather Than Builtin Data

This proposal changes how the script context is passed to scripts, thus removing one use of the Plutus builtin type `Data`.
However, we still use the builtin `Data` type for passing redeemers and datums, which continue to be `Data` objects in the transaction.[^why-redeemers-datums-data]

[^why-redeemers-datums-data]: See "Why not also make datums and redeemers terms instead of `Data`?" for why we want to keep redeemers and datums as `Data` in transactions themselves.

An alternative would be to encode the `Data` objects for redeemers and datums using sums-of-products instead of the builtin `Data` type.
That would require us to define and specify a stable `dataToTerm :: Data -> Term` function that converts a `Data` object into a term using sums-of-products.
This would be simple for some cases (e.g. `Constr`), but less simple for other cases (notably `Map` and `List`).

This has some costs:
1. We have an additional conversion function that we need to specify.
2. The details of the conversion function would be relevant to script authors, since they would need to know how their `Data` object had been encoded in order to operate on it.
3. The ledger-script interface becomes generally more complex, since instead of passing `Data` objects directly, we now need to encode them.

However, it would have a significant advantage in that we would potentially be able to remove the builtin `Data` type and its associated builtins entirely.
Of course, they would still have to be supported in old ledger languages, so the reduction in implementation complexity would be limited.

Strictly, this could be implemented as a later change, but if we're going to change the ledger-script interface anyway, it would be nice to do it in one go.

## Path to Active

### Acceptance Criteria

- [ ] Resolution or good workaround for the loss of fast hashing and equality builtins
- [ ] `cardano-ledger` changes
    - [ ] Specification, _including_ specification of the script context translation to a Plutus Core term
    - [ ] Implementation of new ledger language, including new ledger-script interface
- [ ] Release
    - [ ] New ledger language supported in a released node version

### Implementation Plan

This CIP will be implemented by Michael Peyton Jones and the Plutus team.

## Appendix: Benchmark results

#### Script context processing 1: basic processing

These are synthetic benchmarks that aim to illustrate the difference between scripts that process script contexts encoded via `Data`, or passed directly as Plutus Core terms.
They are defined in `plutus-benchmark/script-contexts`.
They do this by generating medium-sized script context objects and then performing a few basic operations on them.
They thus aim to show the potential savings for scripts from the new scheme.

- `checkScriptContext1` decodes the script context from `Data`, and then does O(size of script context) work. This represents a somewhat realistic case where the script context is used to a modest degree.
- `checkScriptContext2` decodes the script context from `Data`, and then does constant work. This represents the case where the script context decoding is pure overhead.
- `checkScriptContext3` is the same as `checkScriptContext1`, but passing the script context as a term directly.
- `checkScriptContext4` is the same as `checkScriptContext2`, but passing the script context as a term directly.

The 4/20 variants indicate the size of the generated script context object.

Since the difference here should be visible in how many machine steps are taken, we just give the budget numbers for the different scenarios.
All these benchmarks are run on `sums-of-products`, since the difference lies in the construction of the script, not how it is evaluated.

| Benchmark              | CPU budget usage | Memory budget usage |
|:----------------------:|:----------------:|:-------------------:|
| checkScriptContext1-4  | 137571245        | 447793             |
| checkScriptContext1-20 | 483223997        | 1573169             |
| checkScriptContext2-4  | 131415877        | 426584             |
| checkScriptContext2-20 | 442300997        | 1415128            |
| checkScriptContext3-4  | 12424957         | 47311              |
| checkScriptContext3-20 | 50504589         | 198543             |
| checkScriptContext4-4  | 2175589          | 8302               |
| checkScriptContext4-20 | 6591589          | 27502              |

In both scenarios the budget usage drops by an order of magnitude.
This should not be taken as representative of typical savings for scripts, since these are very synthetic examples and the amount of work apart from decoding the script context is small.
Still, it shows that we do successfully save ourselves from doing the work, and that the work saved is significant.

#### Script context processing 2: equality

These benchmarks compare the cost of computing equality of script contexts in two cases:

1. Script contexts encoded as `Data`, using the `equalsData` builtin
2. Script contexts encoded as terms using SOPs, using equality functions compiled from Haskell

They are defined in `plutus-benchmark/script-contexts`.

| Benchmark                    | CPU budget usage | Memory budget usage |
|:----------------------------:|:----------------:|:-------------------:|
| Script context data equality | 58790597         | 192802              |
| Script context SOP equality  | 632527251        | 2592146             |
| Overhead                     | 43631100         | 189800              |

This is quite bad: the SOP equality case is 39x worse, accounting for the shared overhead.
This is not too surprising, since the builtin case can perform the whole computation in Haskell, and moreover the computation is much simpler (a single recursive function over `Data`).
Whereas the SOP case is jumping between many equality functions defined for different types, and all operating inside the main Plutus Core evaluator.
Still, this is a striking difference.

## Copyright 

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Scott encoding]: https://en.wikipedia.org/wiki/Mogensen%E2%80%93Scott_encoding

