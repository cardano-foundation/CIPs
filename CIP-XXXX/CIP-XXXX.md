---
CIP: ????
Title: Bitwise operations
Category: Plutus
Status: Proposed
Authors:
    - Koz Ross <koz@mlabs.city>
Implementors: 
    - Koz Ross <koz@mlabs.city>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-05-16
License: Apache-2.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

## Specification

We describe the proposed operations in several stages. First, we give an
overview of the proposed operations' signatures and costings; second, we
describe the semantics of each proposed operation in detail, as well as some
examples. Lastly, we provide laws that any implementation of the proposed
operations should obey.

Throughout, we make use of the [bit indexing scheme][bit-indexing-scheme]
described in a prior CIP. We also use the notation $x[i]$ to refer to the value
of at bit index $i$ of $x$, and the notation $x\\{i\\}$ to refer to the byte at
byte index $i$ of $x$.

### Operation semantics

Our proposed operations will have the following signatures:

* ``bitwiseShift :: BuiltinByteString -> BuiltinInteger -> BuiltinByteString``
* ``bitwiseRotate :: BuiltinByteString -> BuiltinInteger -> BuiltinByteString``
* ``countSetBits :: BuiltinByteString -> BuiltinInteger``
* ``findFirstSetBit :: BuiltinByteString -> BuiltinInteger``

We assume the following costing, for both memory and execution time:

| Operation | Execution time cost | Memory cost |
|-----------|------|
|`bitwiseShift`| Linear in the `BuiltinByteString` argument | As execution time
|
|`bitwiseRotate` | Linear in the `BuiltinByteString` argument | As execution
time |
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

TODO: Examples

#### `bitwiseRotate`

`bitwiseRotate` takes two arguments; we name and describe them below.

1. The `BuiltinByteString` to be rotated. This is the _data argument_.
2. The rotation, whose sign indicates direction and whose magnitude indicates 
   the size of the rotation. This is the _rotation argument_, and has type
   `BuiltinInteger`.

Let $b$ refer to the data argument, whose length in bytes is $n$, and let $i$
refer to the rotation argument. Let the result of `bitwiseRotate` called with $b$
and $i$ be $b_r$, also of length $n$. 

For all $j \in 0, 1, \ldots 8 \cdot n - 1$, we have $b_r = b[j - i \mod 8 \cdot n]$.

Some examples of the intended behaviour of `bitwiseRotate` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

TODO: Examples

#### `countSetBits`

Let $b$ refer to `countSetBits`' only argument, whose length in bytes is $n$,
and let $r$ be the result of calling `countSetBits` on $b$. Then we have

$$
r = \sum_{i=0}^{8 \cdot n - 1} b[i]
$$

Some examples of the intended behaviour of `countSetBits` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

TODO: Examples

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

TODO: Examples

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

Lastly, `countSetBits` has a relationship to bitwise XOR, regardless of
semantics:

```haskell
countSetBits (bitwiseLogicalXor semantics x x) = 0
```

#### `findFirstSetBit`

`BuiltinByteString`s consisting entirely of zero bytes (including the empty
`BuiltinByteString`, by vacuous truth) always give a `-1` result with
`findFirstSetBit`:

```haskell
findFirstSetBit (replicateByteString n 0x00) = -1
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
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

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
[logic-cip]: https://github.com/mlabs-haskell/CIPs/blob/koz/logic-ops/CIP-XXX/CIP-XXX.md
[include-exclude]: https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle
