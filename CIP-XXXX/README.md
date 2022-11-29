---
CIP: ?
Title: Merkelised Plutus Scripts
Authors: Las Safin <las@mlabs.city>
Status: Draft
Type: Standards
Created: 2022-11-29
License: <CC-BY-4.0>
---

## Abstract

Currently, the hash of a script is simply the hash of its [serialisation](
https://github.com/input-output-hk/plutus/blob/a645d1ee0dd5efcd7a7da24678461e07396ad26e/plutus-ledger-api/src/PlutusLedgerApi/Common/SerialisedScript.hs#L88).
This CIP proposes changing this such that the hash of a script (term)
is a function of its immediate children's hashes, forming a Merkle Tree from the AST.
This allows one to shallowly verify a script's hash, and is useful on Cardano,
because it allows scripts to **check that a script hash is an instantiation of a parameterised script**.

In addition, a `blake2b_224` built-in function must be added.

This is inspired by [BIP-144](https://github.com/bitcoin/bips/blob/master/bip-0114.mediawiki),
but the motivations are very different.

## Motivation

Given some core logic expressible as a script, it is common to have parameters in
the form of constants, e.g. fees, references to other scripts, magical numbers.

These parameters can either be put in a datum somewhere, or can be put into the
script itself, either by inlining them, or applying the unapplied script to the constants.

On-chain it is currently hard to check that one script is an applied form
of another script. In cases where that is necessary, datums are instead used.

By Merkelising the hashing, we make this possible,
which unlocks checking that a script is an application of another script to some parameter.

Example reasons to apply the parameters to the script:
- Staking validators currently don't support datums, and all staking validators
  share a single rewards account. Allowing checking applied parameters
  makes staking validators much more powerful. (More about this below)
- Constants can be included in reference script, leading to less CPU and memory used,
  since they don't have to be parsed from the adjacent datum (somewhat cheap)
  or the script context (very expensive).
- A script address + datum can't fit in an address,
  if you want that you also need this (or need to change what an address is).

## Specification

The hash of a script will be derived directly from the AST, rather than its serialisation.
Currently, its formed by hashing the serialisation prefixed with a byte that represents its version,  e.g. 0x02 for Plutus V2.

The hash of a script becomes the hash of the prefix version annotation prepended to the hash of the term.

[`Term`](https://github.com/input-output-hk/plutus/blob/a645d1ee0dd5efcd7a7da24678461e07396ad26e/plutus-core/untyped-plutus-core/src/UntypedPlutusCore/Core/Type.hs#L69)
currently has 8 constructors. On-chain, annotations are always the unit type,
and are hence ignored for this algorithm. Each case/constructor is generally handled by
hashing the concatenation of a prefix (single byte corresponding to the
constructor index) along with the hashes of the arguments passed to the constructor.

Similar code can be found [in Plutarch](https://github.com/Plutonomicon/plutarch-plutus/blob/95e40b42a1190191d0a07e3e4e938b72e6f75268/Plutarch/Internal.hs#L100) (for a slightly different AST).

To avoid giving a single script two hashes,
this system must be used (exclusively) since at least a version after Plutus V2.

The algorithm for checking a script hash against a supplied script (of a new version)
in the ledger will change slightly: rather than hashing the supplied serialised
script directly, the decoding of the serialised script must be hashed.
(NB: the hashing and decoding can be fused to avoid intermediary structures.)

To allow computing the hash in scripts, we must support `blake2b-224` in Plutus scripts
as it's what is currently used. This algorithm used might change in the future, but that is
not relevant for this CIP.

### Hashing `Error`

Since there are no children, the hash of the `Error` term is the
hash of the prefix byte for the `Error` constructor.
You could theoretically choose any random number as the hash,
but it has to be proven to be random, hence hashing the prefix byte
is the best option.

In pseudocode: `hash prefix`

### Hashing `Builtin`, `Var`

The hash of a `Builtin` is the hash of the prefix prepended to the base-256 encoded
(i.e. serialised to bytestring) index of the built-in function.
Because there are less than 256 built-ins, this is currently the same
as hashing the prefix byte prepended to the byte containing the index of
the built-in.

`Var` is handled the exact same way (with a different prefix),
but it's in this case feasible for the index to be more than 255.

In pseudocode: `hash $ prefix <> serialiseBase256 index`

### Hashing `Apply`, `Force`, `Delay`

These are hashed by hashing the result of prepending the prefix
byte to the concatenation of the hashes of the children.

In pseudocode: `hash $ foldl' (<>) prefix (hash <$> children)`

### Hashing `LamAbs`

This works the exact same way as above, notably, the _name_ is excluded
as it's a constant in the de-Bruijn encoding.

In pseudocode: `hash $ prefix <> hash body`

### Hashing `Constant`

The universe of types used on-chain is always `DefaultUni`.
Each possible data type is handled differently, with each having
a different prefix. The total number of prefixes does not exceed
255. If it did, the prefix would have to be increased to two bytes.

In addition:
Negative integers and non-negative integers have separate prefixes.
False and True also have separate prefixes.

#### Hashing non-negative integers

The serialisation according to [CIP-58](https://github.com/cardano-foundation/CIPs/blob/a1b9ff0190ad9f3e51ae23e85c7a8f29583278f0/CIP-%3F/README.md#representation-of-builtininteger-as-builtinbytestring-and-conversions),
prefixed with the two-byte prefix, is hashed.

In pseudocode: `hash $ prefix <> prefix' <> serialiseCIP58 n`

#### Hashing negative integers

The same algorithm as above is used, but the number hashed is `1 - n`.

In pseudocode: `hash $ prefix <> prefix' <> serialiseCIP58 (1 - n)`

#### Hashing bytestrings

The bytestring is hashed as-is.
We use the blake2b-256 hash here, such that we can usefully check that
the script refers to a bytestring that we know only the hash of.

In pseudocode: `hash $ prefix <> blake2b_256 bs`

#### Hashing strings

The flat-encoding is hashed.

In pseudocode: `hash $ prefix <> flat x`

#### Hashing lists, pairs

Lists and pairs are hashed like a Merkle tree,
much the same way that terms are.
The children have a known type, and are hashed according to how that
type should be hashed, i.e. with the correct algorithm and prefix.

In pseudocode: `hash $ foldl' (<>) prefix (hash <$> children)`

#### Hashing `()`, `False`, `True`

Each has its own separate prefix, like `Error`, hence:

In pseudocode: `hash prefix`

#### Hashing `Data`

The `CBOR` encoding is used, notably, it must be compatible with the `serialiseData`
built-in to be useful on-chain.
We use the blake2b-256 hash here, such that we can usefully check that
the script refers to a datum that we know only the hash of.
If the hashing algorithm for data changes, we must also change it here.

In pseudocode: `hash $ prefix <> blake2b_256 (serialiseData d)`

## Rationale

Given this minor change, we can now check that one script is the application of another script.
Concretely, given hash `script`, hash `original`, parameter `d` (as data),
intermediate hashes `h0`, `h1`, hashing prefixes `ver_prefix`, `app_prefix`, `const_prefix`, we check:
```
script == blake2b_224 $ ver_prefix <> h0
h0 == blake2b_224 $ app_prefix <> original <> h1
h1 == blake2b_224 $ const_data_prefix <> blake2b_256 (serialiseData d)
```

We essentially open the Merkle tree commitment partially and check that the supplied path is correct.

### Relation with CIP-58

This CIP does not _depend_ on CIP-58, but to hash integers on-chain
the way it's done here, CIP-58's integer-to-bytestring serialisation built-in
must be available in Plutus.

### Relation with BIP-144

BIP144 uses this trick to avoid submitting the parts of the script that aren't used.
Given that reference scripts are common in Haskell, this isn't a big win for efficiency,
but it might be worth implementing for the sake of scripts used only once.
This CIP however doesn't require that that be implemented.

The argument for privacy doesn't apply, private smart contracts can be achieved through
the use of non-interactive zero-knowledge probabilistic proofs.

### Reference scripts

Currently, different instances of the same script will need their own reference inputs
since their hashes are different. It seems feasible to allow sharing of a single reference script,
given the parameters and language version as witnesses, but given the complexity
involved, it is not specified in this CIP.

### Staking

This makes staking validators much more powerful, since a single protocol can
now manage many rewards accounts (by instantiating the script with a numeric identifier).
However, it is arguably not the optimal solution due to the reference
script problem described above. Even if the reference script problem
is solved as described above, it seems logical to allow supplying a datum
to a staking validator, or somehow combining the payment address and staking address for scripts,
and using the same datum for both, while somehow solving the separate accounts problem.

Given the heavy complexity of fixing staking validators, Merkelising script hashing seems much more feasible.

### Alternatives

#### Parameterised Reference Scripts

See https://github.com/cardano-foundation/CIPs/pull/354.

Seemingly, Merkelisation is a less invasive and possibly cleaner change.

#### Changing how constants are hashed

The hashing of constants might not have a clear best solution, but most notably,
it is not clear how much/less to Merkelise the hashing.
E.g., the hashing of data itself could be Merkelised. This is not done in this CIP.
The hashing of a `Data` constant could also prepend the prefix directly to the serialisation,
rather than to the hash of the `Data`. It is not clear what is best.

##### Hashing strings, lists, pairs differently

Strings are not very useful in Plutus.
Hence, the hashing algorithm for them isn't optimised such that
they can be easily verified.

Strings have essentially no purpose on-chain, since they're only used
for tracing, which should not be used in production.

In the context of checking applied parameters, it is likely that only
`Data`, `Integer`, `Bool`, `ByteString`, will be used as parameters,
since they cover all useful behaviour in an efficient way.
If you want to parameterise your script by a pair of integers,
it is likely best to unwrap that into two separate integer parameters
for the sake of efficiency of _running_ the script, which is likely
to be more common that checking the parameters.

Built-in lists and pairs are not commonly used as parameters, but it's plausible
that they might still be the most efficient method in some scenarios.
Hence, they have been included.
They use Merkle-tree hashing since that's the simplest and most useful in this case.

## Path to Active

### Implementation plan

Las Safin will implement this if IOG don't have time.

## Copyright

This CIP is licensed under CC-BY-4.0.
