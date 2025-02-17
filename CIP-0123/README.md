---
CIP: 123
Title: Bitwise operations over BuiltinByteString
Category: Plutus
Status: Active
Authors:
    - Koz Ross <koz@mlabs.city>
Implementors: 
    - Koz Ross <koz@mlabs.city>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/825
Created: 2024-05-16
License: Apache-2.0
---

## Abstract

We describe the semantics of a set of bitwise operations for Plutus
`BuiltinByteString`s. Specifically, we provide descriptions for:

* Bit shifts and rotations
* Counting the number of set bits (`popcount`)
* Finding the first set bit

We base our work on similar operations described in [CIP-58][cip-58], but use
the bit indexing scheme from [the logical operations cip][logic-cip] for the
semantics. This is intended as follow-on work from both of these.

## Motivation: why is this CIP necessary?

Bitwise operations, both over fixed-width and variable-width blocks of bits, 
have a range of uses. Indeed, we have already proposed [CIP-122][logic-cip],
with some example cases, and a range of primitive operations on
`BuiltinByteString`s designed to allow bitwise operations in the service of
those example cases, as well as many others. These operations form a core of
functionality, which is important and necessary, but not complete. We believe
that the operations we describe in this CIP form a useful 'completion' of the
work in CIP-122, based on similar work done in the [earlier CIP-58][cip-58].

To demonstrate why our proposed operations are useful, we re-use the cases
provided in the [CIP-122][logic-cip], and show why the operations
we describe would be beneficial.

### Case 1: integer set

For integer sets, the [previous description][integer-set] lacks two important,
and useful, operations:

* Given an integer set, return its cardinality; and
* Given an integer set, return its minimal member (or specify it is empty).

These operations have a range of uses. The first corresponds to the notion of
[Hamming weight][hamming-weight], which can be used for operations ranging from
representing boards in chess games to exponentiation by squaring to succinct
data structures. Together with bitwise XOR, it can also compute the [Hamming
distance][hamming-distance]. The second operation also has a [range of
uses][ffs-uses], ranging from succinct priority queues to integer normalization.
It is also useful for [rank-select dictionaries][rank-select-dictionary], a
succinct structure that can act as the basis of a range of others, such as
dictionaries, multisets and trees of different arity.

In all of the above, these operations need to be implemented efficiently to be
useful. While we could use only bit reading to perform all of these, it is
extremely inefficient: given an input of length $n$, assuming that any bit
distribution is equally probable, we need $\Theta(8 \cdot n)$ time in the
average case. While it is
impossible to do both of these operations in sub-linear time in general, the
large constant factors this imposes (as well as the overhead of looping over
_bit_ indexes) is a cost we can ill afford on-chain, especially if the goal is
to use these operations as 'building blocks' for something like a data
structure.

### Case 2: hashing

In our [previously-described][hashing] case, we stated what operations we would
need for the Argon2 family of hashes specifically. However, Argon2 has a
specific advantage in that the number of operations it requires are both
relatively few, and the most complex of which (BLAKE2b hashing) already exists
in Plutus Core as a primitive. However, other hash functions (and indeed, many
other cryptographic primitives) rely on two other important instructions: bit
shifts and bit rotations. As an example, consider SHA512, which is an important
component in several cryptographic protocols (including Ed25519 signature
verification): its implementation requires both shifts and rotations to work. 

Like with Case 1, we can theoretically simulate both rotations and shifts using
a combination of bit reads and bit writes to an empty `BuiltinByteString`.
However, the cost of this is extreme: we would need to produce a list of
index-value pairs of length equal to the Hamming weight of the input, only to
then immediately discard it! To put this into some perspective, for an 8-byte
input, performing a rotation involves allocating an expected 32 index-value
pairs, using _significantly_ more memory than the result. On-chain, we can't
really afford this cost, especially in an operation intended to be used as part
of larger constructions (as would be necessary here).

## Specification

We describe the proposed operations in several stages. First, we give an
overview of the proposed operations' signatures and costings; second, we
describe the semantics of each proposed operation in detail, as well as some
examples. Lastly, we provide laws that any implementation of the proposed
operations should obey.

Throughout, we make use of the [bit indexing scheme][bit-indexing-scheme]
described in a CIP-122. We also re-use the notation $x[i]$ to refer to the value
of at bit index $i$ of $x$, and the notation $x\\{i\\}$ to refer to the byte at
byte index $i$ of $x$: both are specified in CIP-122.

### Operation semantics

Our proposed operations will have the following signatures:

* ``bitwiseShift :: BuiltinByteString -> BuiltinInteger -> BuiltinByteString``
* ``bitwiseRotate :: BuiltinByteString -> BuiltinInteger -> BuiltinByteString``
* ``countSetBits :: BuiltinByteString -> BuiltinInteger``
* ``findFirstSetBit :: BuiltinByteString -> BuiltinInteger``

We assume the following costing, for both memory and execution time:

| Operation | Execution time cost | Memory cost |
|-----------|---------------------|-------------|
|`bitwiseShift`| Linear in the `BuiltinByteString` argument | As execution time|
|`bitwiseRotate` | Linear in the `BuiltinByteString` argument | As execution time |
|`countSetBits` | Linear in the argument | Constant |
|`findFirstSetBit` | Linear in the argument | Constant |

#### `bitwiseShift`

`bitwiseShift` takes two arguments; we name and describe them below.

1. The `BuiltinByteString` to be shifted. This is the _data argument_.
2. The shift, whose sign indicates direction and whose magnitude indicates the
   size of the shift. This is the _shift argument_, and has type
   `BuiltinInteger`.

Let $b$ refer to the data argument, whose length in bytes is $n$, and let $i$
refer to the shift argument. Let the result of `bitwiseShift` called with $b$
and $i$ be $b_r$, also of length $n$. 

For all $j \in 0, 1, \ldots 8 \cdot n - 1$, we have

$$
b_r[j] = \begin{cases}
         b[j - i] & \text{if } j - i \in 0, 1, \ldots 8 \cdot n - 1\\
         0 & \text{otherwise} \\
         \end{cases}
$$

Some examples of the intended behaviour of `bitwiseShift` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Shifting the empty bytestring does nothing
bitwiseShift [] 3 => []
-- Regardless of direction
bitwiseShift [] (-3) => []
-- Positive shifts move bits to higher indexes, cutting off high indexes and
-- filling low ones with zeroes
bitwiseShift [0xEB, 0xFC] 5 => [0x7F, 0x80]
-- Negative shifts move bits to lower indexes, cutting off low indexes and
-- filling high ones with zeroes
bitwiseShift [0xEB, 0xFC] (-5) => [0x07, 0x5F]
-- Shifting by the total number of bits or more clears all bytes
bitwiseShift [0xEB, 0xFC] 16 => [0x00, 0x00]
-- Regardless of direction
bitwiseShift [0xEB, 0xFC] (-16) => [0x00, 0x00]
```

#### `bitwiseRotate`

`bitwiseRotate` takes two arguments; we name and describe them below.

1. The `BuiltinByteString` to be rotated. This is the _data argument_.
2. The rotation, whose sign indicates direction and whose magnitude indicates 
   the size of the rotation. This is the _rotation argument_, and has type
   `BuiltinInteger`.

Let $b$ refer to the data argument, whose length in bytes is $n$, and let $i$
refer to the rotation argument. Let the result of `bitwiseRotate` called with $b$
and $i$ be $b_r$, also of length $n$. 

For all $j \in 0, 1, \ldots 8 \cdot n - 1$, we have 
$b_r = b[(j - i) \text{ } \mathrm{mod} \text { } (8 \cdot n)]$.

Some examples of the intended behaviour of `bitwiseRotate` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Rotating the empty bytestring does nothing
bitwiseRotate [] 3 => []
-- Regardless of direction
bitwiseRotate [] (-1) => []
-- Positive rotations move bits to higher indexes, 'wrapping around' for high
-- indexes into low indexes
bitwiseRotate [0xEB, 0xFC] 5 => [0x7F, 0x9D]
-- Negative rotations move bits to lower indexes, 'wrapping around' for low
-- indexes into high indexes
bitwiseRotate [0xEB, 0xFC] (-5) => [0xE7, 0x5F]
-- Rotation by the total number of bits does nothing
bitwiseRotate [0xEB, 0xFC] 16 => [0xEB, 0xFC]
-- Regardless of direction
bitwiseRotate [0xEB, 0xFC] (-16) => [0xEB, 0xFC]
-- Rotation by more than the total number of bits is the same as the remainder
-- after division by number of bits
bitwiseRotate [0xEB, 0xFC] 21 =>[0x7F, 0x9D]
-- Regardless of direction, preserving sign
bitwiseRotate [0xEB, 0xFC] (-21) => [0xE7, 0x5F]
```

#### `countSetBits`

Let $b$ refer to `countSetBits`' only argument, whose length in bytes is $n$,
and let $r$ be the result of calling `countSetBits` on $b$. Then we have

$$
r = \sum_{i=0}^{8 \cdot n - 1} b[i]
$$

Some examples of the intended behaviour of `countSetBits` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- The empty bytestring has no set bits
countSetBits [] => 0
-- Bytestrings with only zero bytes have no set bits
countSetBits [0x00, 0x00] => 0
-- Set bits are counted regardless of where they are
countSetBits [0x01, 0x00] => 1
countSetBits [0x00, 0x01] => 1
```

#### `findFirstSetBit`

Let $b$ refer to `findFirstSetBit`'s only argument, whose length in bytes is $n$,
and let $r$ be the result of calling `findFirstSetBit` on $b$. Then we have the
following:

1. $r \in -1, 0, 1, \ldots, 8 \cdot n - 1$
2. If for all $i \in 0, 1, \ldots n - 1$, $b\\{i\\} = \texttt{0x00}$, then $r = -1$;
   otherwise, $r > -1$.
3. If $r > -1$, then $b[r] = 1$, and for all $i \in 0, 1, \ldots, r - 1$, $b[i]
   = 0$.

Some examples of the intended behaviour of `findFirstSetBit` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- The empty bytestring has no first set bit
findFirstSetBit [] => -1
-- Bytestrings with only zero bytes have no first set bit
findFirstSetBit [0x00, 0x00] => -1
-- Only the first set bit matters, regardless what comes after it
findFirstSetBit [0x00, 0x02] => 1
findFirstSetBit [0xFF, 0xF2] => 1
```

### Laws

Throughout, we use `bitLen bs` to indicate the number of bits in `bs`; that is,
`sizeOfByteString bs * 8`. We also make reference to [logical
operations][logic-cip] from a previous CIP as part of specifying these laws.

#### Shifts and rotations

We describe the laws for `bitwiseShift` and `bitwiseRotate` together, as they
are similar. Firstly, we observe that `bitwiseShift` and `bitwiseRotate` both
form a [monoid homomorphism][monoid-homomorphism] between natural number 
addition and function composition:

```haskell
bitwiseShift bs 0 = bitwiseRotate bs 0 = bs

bitwiseShift bs (i + j) = bitwiseShift (bitwiseShift bs i) j

bitwiseRotate bs (i + j) = bitwiseRotate (bitwiseRotate bs i) j
```

However, `bitwiseRotate`'s homomorphism is between _integer_ addition and
function composition: namely, `i` and `j` in the above law are allowed to have
different signs. `bitwiseShift`'s composition law only holds if `i` and `j`
don't have opposite signs: that is, if they're either both non-negative or both
non-positive.

Shifts by more than the number of bits in the data argument produce an empty
`BuiltinByteString`:

```haskell
-- n is non-negative

bitwiseShift bs (bitLen bs + n) = 
bitwiseShift bs (- (bitLen bs + n)) = 
replicateByteString (sizeOfByteString bs) 0x00
```

Rotations, on the other hand, exhibit 'modular roll-over':

```haskell
-- n is non-negative
bitwiseRotate bs (binLen bs + n) = bitwiseRotate bs n

bitwiseRotate bs (- (bitLen bs + n)) = bitwiseRotate bs (- n)
```

Shifts clear bits at low indexes if the shift argument is positive, and at high
indexes if the shift argument is negative:

```
-- 0 < n < bitLen bs, and 0 <= i < n
readBit (bitwiseShift bs n) i = False

readBit (bitwiseShift bs (- n)) (bitLen bs - i - 1)  = False
```

Rotations instead preserve all set and clear bits, but move them around:

```
-- 0 <= i < bitLen bs
readBit bs i = readBit (bitwiseRotate bs j) (modInteger (i + j) (bitLen bs))
```

#### `countSetBits`

`countSetBits` forms a [monoid homomorphism][monoid-homomorphism] between
`BuiltinByteString` concatenation and natural number addition:

```haskell
countSetBits "" = 0

countSetBits (x <> y) = countSetBits x + countSetBits y
```

`countSetBits` also demonstrates that `bitwiseRotate` indeed preserves the
number of set (and thus clear) bits:

```haskell
countSetBits bs = countSetBits (bitwiseRotate bs i)
```

There is also a relationship between the result of `countSetBits` on a given
argument and its complement:

```haskell
countSetBits bs = bitLen bs - countSetBits (bitwiseLogicalComplement bs)
```

Furthermore, `countSetBits` exhibits (or more precisely, gives evidence for) the
[inclusion-exclusion principle][include-exclude] from combinatorics, but only
under truncation semantics:

```haskell
countSetBits (bitwiseLogicalXor False x y) = countSetBits (bitwiseLogicalOr
False x y) - countSetBits (bitwiseLogicalAnd False x y)
```

Lastly, `countSetBits` has a relationship to bitwise XOR, regardless 
of semantics:

```haskell
countSetBits (bitwiseLogicalXor semantics x x) = 0
```

#### `findFirstSetBit`

`BuiltinByteString`s where every byte is the same (provided they are not empty)
have the same first bit as a singleton of that same byte:

```haskell
-- 0 <= w8 <= 255, n >= 1
findFirstSetBit (replicateByteString n w8) = 
findFirstSetBit (replicateByteString 1 w8)
```

Additionally, `findFirstSet` has a relationship to bitwise XOR, regardless of
semantics:

```haskell
findFirstSetBit (bitwiseLogicalXor semantics x x) = -1
```

Any result of a `findFirstSetBit` operation that isn't `-1` gives a valid bit
index to a set bit, but any non-negative `BuiltinInteger` less than this will
give an index to a clear bit:

```haskell
-- bs is not all zero bytes or empty
readBit bs (findFirstSetBit bs) = True

-- 0 <= i < findFirstSet bs
readBit bs i = False
```

## Rationale: how does this CIP achieve its goals?

Our four operations, along with their semantics, fulfil the requirements of both
our cases, and are law-abiding, familiar, consistent and straightforward to
implement. Furthermore, they relate directly to operations provided by
[CIP-122][logic-cip], as well as being identical to the equivalent operations in
[CIP-58][cip-58]. At the same time, some alternative choices could have been
made:

* Not implementing these operations at all, instead requiring higher-level APIs
  to implement them atop CIP-122 primitives;
* Providing only some of these four operations;
* Having `findFirstSetBit` return the bit length for an all-zero argument,
  instead of `-1`;
* Including a way of finding the _last_ set bit as well.

We discuss our choices with regards to all the above, and specify why we made
the choices that we did.

While we chose to provide all of these operations as primitives, we could
instead have required higher-level APIs to provide these on the basis
of [CIP-122][logic-cip] bit reads and writes. This is indeed possible:

* `bitwiseShift` and `bitwiseRotate` is a loop over all bits in the data argument, 
  which is used to construct a change list that sets appropriate bits (with the 
  right offset), which then gets applied to a `BuiltinByteString` of the same
  length as the data argument, but full of zero bytes.
* `countSetBits` is a fold over all bit indexes, incrementing an accumulator
  every time a set bit is found.
* `findFirstSetBit` is a fold over all bit indexes, returning the first index
  with a set bit, or (-1) if none can be found.

However, especially for `bitwiseShift` and `bitwiseRotate`, this comes at
significant cost. For shifts and rotations, we have to construct a change list
argument whose length is proportional to the Hamming weight of the data
argument. Assuming that all inputs are equally likely, this is proportional to
the bit length of the data argument: such a change list is likely significantly
larger than the result of the shift or rotation, making the memory cost of such
operations far higher than it needs to be. Given the constraints on memory and
execution time on-chain, at minimum, these two operations would have to be
primitives to make them viable at all: Case 2-style implementations would have
intolerably large memory costs otherwise, as such algorithms often make heavy
use of both shifts and rotations.

The case for `countSetBits` and `findFirstSetBit` is less clear here, as they
wouldn't require nearly as much of a memory cost if implemented atop CIP-122
primitives using folds. However, the cost would still be significant:
`countSetBits` requires looping over every bit index in the argument, and
`findFirstSetBit` (again, assuming any bit distribution in an argument is
equally probable) requires looping over about half this many. This would make
these operations unreasonable even over smaller inputs, which would make
applications like rank-select dictionaries (which expect these operations to be
fast and low-cost) unworkable. As succinct data structures are foremost in our
minds when considering the current primitives, we believe it is important that
`countSetBits` and `findFirstSetBit` are as efficient as they could be, hence
their inclusion.

When designing our operations, we tried to keep them familiar to Haskellers,
namely by having them behave like the similar operations from the `Bits` and
`FiniteBits` type classes. In particular,
`bitwiseShift` and `bitwiseRotate` act similarly given the same shift (or
rotation) argument, as positive values shift left and negative ones shift 
right. The only exception is the choice for `findFirstSetBit` to return `-1`
when no set bits are found, which runs counter to the way `countTrailingZeros`
from `FiniteBits` works, which instead returns the bit length. This is also
different to how this operations [works in hardware][ctz]. Indeed, having
`findFirstSetBit` work this way would not only be more familiar, it would also
provide additional laws:

```haskell
-- Not possible under our current definition
-- bitLen is the bit length of the argument
0 <= popcount bs <= bitLen bs - findFirstSet bs 
```

Under both definitions, the intent is the same: if the argument doesn't contain
any set bits, produce an invalid index. The difference is that we choose to
produce a _negative_ invalid index, whereas the consensus is to produce a
_non-negative_ invalid index instead. However, one task that is likely to come
up frequently when using `findFirstSetBit` is checking whether the index we were
given was valid or not (essentially, whether the argument has any nonzero bytes
in it). Under our definition, all that would be required is

```haskell
let found = findFirstSetBit bs
  in if found < 0
     then weMissed
     else validIndex
```

This is a cheap operation in Plutus Core, requiring only comparing against a
constant. However, if we used the more widely-used definition, we would instead
have to do this:

```haskell
let found = findFirstSetBit bs
    bitLen = 8 * sizeOfByteString bs
  in if found >= bitLen
     then weMissed
     else validIndex
```

This requires us to do considerably more work (finding the length of the
argument, multiplying by 8, then compare against that result), and is also much
more prone to error: users have to remember to use a `>=` comparison, as well as
to multiply the argument length by 8. This is less of an issue with
implementations of this operation in other languages, as their equivalent
operations are designed for fixed-width arguments (indeed, `FiniteBits`
_requires_ this), which makes their bit length a constant. In our case, this
isn't as simple, as `BuiltinByteString`s have variable length, which would make
the cost described above unavoidable. Our solution is both more efficient and
less error-prone: all a user needs to remember is that invalid indexes from
`findFirstSetBit` are negative. On this basis, we decided to vary from
conventional approaches.

One notable omission from our operators is the equivalent of counting _leading_
zeroes: namely, an operation that would find the _last_ set bit. Typically, both
a count of leading _and_ trailing zeroes is provided in both hardware and
software: this is the case for `FiniteBits`, as well as [most hardware
implementations][ctz]. To relate this to our cases, specifically Case 1, this
would allow us to efficiently find the _largest_ element in an integer set. The
reason we omit this operation is because, when compared with counting trailing
zeroes, it is far less useful: while it can be used for computing fast integer
square roots, it lacks many other uses. Counting trailing zeroes, on the other
hand, is essential for rank-select dictionaries (specifically for the `select`
operation), and also enables a range of other uses, which we have already
mentioned. In order to limit the number of new primitives, we decided that
counting leading zeroes can be omitted for now. However, our design doesn't
preclude such an operation from being added later if a use case for it is found
to be useful.

## Path to Active

### Acceptance Criteria

We consider the following criteria to be essential for acceptance:

* A proof-of-concept implementation of the operations specified in this 
  document, outside of the Plutus source tree. The implementation must be in 
  GHC Haskell, without relying on the FFI.
* The proof-of-concept implementation must have tests, demonstrating that it 
  behaves as the specification requires.
* The proof-of-concept implementation must demonstrate that it will 
  successfully build, and pass its tests, using all GHC versions currently 
  usable to build Plutus (8.10, 9.2 and 9.6 at the time of writing), across 
  all [Tier 1][tier-1] platforms.

Ideally, the implementation should also demonstrate its performance 
characteristics by well-designed benchmarks.

- [x] Included within a major haskell cardano-node release
  - https://github.com/IntersectMBO/cardano-node/releases/tag/10.1.1  
- [x] Enabled on Cardano mainnet via a hardfork
  - Enabled by Plomin hardfork

### Implementation Plan

MLabs has begun the implementation of the [proof-of-concept][impl] as required in 
the acceptance criteria. Upon completion, we will send a pull request to 
Plutus with the implementation of the primitives for Plutus Core, mirroring 
the proof-of-concept.

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[tier-1]: https://gitlab.haskell.org/ghc/ghc/-/wikis/platforms#tier-1-platforms
[impl]: https://github.com/mlabs-haskell/plutus-integer-bytestring/tree/koz/milestone-2
[bit-indexing-scheme]: https://github.com/mlabs-haskell/CIPs/blob/koz/logic-ops/CIP-XXX/CIP-XXX.md#bit-indexing-scheme
[monoid-homomorphism]: https://en.wikipedia.org/wiki/Monoid#Monoid_homomorphisms
[logic-cip]: https://github.com/mlabs-haskell/CIPs/blob/koz/logic-ops/CIP-0122/CIP-0122.md
[include-exclude]: https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle
[cip-58]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0058
[integer-set]: https://github.com/mlabs-haskell/CIPs/blob/koz/logic-ops/CIP-XXX/CIP-XXX.md#case-1-integer-set
[hamming-weight]: https://en.wikipedia.org/wiki/Hamming_weight#History_and_usage
[hamming-distance]: https://en.wikipedia.org/wiki/Hamming_distance
[ffs-uses]: https://en.wikipedia.org/wiki/Find_first_set#Applications
[rank-select-dictionary]: https://en.wikipedia.org/wiki/Succinct_data_structure#Succinct_indexable_dictionaries
[hashing]: https://github.com/mlabs-haskell/CIPs/blob/koz/logic-ops/CIP-XXX/CIP-XXX.md#case-2-hashing
[ctz]: https://en.wikipedia.org/wiki/Find_first_set#Hardware_support
