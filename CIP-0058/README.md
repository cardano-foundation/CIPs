---
CIP: 58
Title: Plutus Bitwise Primitives
Category: Plutus
Authors:
    - Koz Ross <koz@mlabs.city>
    - Maximilian König <maximilian@mlabs.city>
Implementors:
    - Las Safin <me@las.rs>
Status: Proposed
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/283
    - https://github.com/input-output-hk/plutus/issues/4252
    - https://github.com/input-output-hk/plutus/pull/4733
Created: 2022-05-27
License: Apache-2.0
---

# Abstract

Add primitives for bitwise operations, based on `BuiltinByteString`, without 
requiring new data types.

# Motivation

Bitwise operations are one of the most fundamental building blocks of algorithms
and data structures. They can be used for a wide variety of applications,
ranging from representing and manipulating sets of integers efficiently, to
implementations of cryptographic primitives, to fast searches. Their wide
availability, law-abiding behaviour and efficiency are the key reasons why they
are widely used, and widely depended on.

At present, Plutus lacks meaningful support for bitwise operations, which
significantly limits what can be usefully done on-chain. While it is possible to
mimic some of these capabilities with what currently exists, and it is always
possible to introduce new primitives for any task, this is extremely
unsustainable, and often leads to significant inefficiencies and duplication of
effort. 

We describe a list of bitwise operations, as well as their intended semantics,
designed to address this problem.

## Example applications

We provide a range of applications that could be useful or beneficial on-chain,
but are difficult or impossible to implement without some, or all, of the
primitives we propose.

### Finite field arithmetic

[Finite field arithmetic](https://en.wikipedia.org/wiki/Finite_field_arithmetic)
is an area with many applications, ranging from [linear block
codes](https://en.wikipedia.org/wiki/Block_code) to [zero-knowledge
proofs](https://en.wikipedia.org/wiki/Zero-knowledge_proof) to scheduling and
experimental design. Having such capabilities on-chain is useful in for a wide
range of applications. 

A good example is multiplication over the [Goldilocks
field](https://blog.polygon.technology/introducing-plonky2) (with characteristic
$2^64 - 2^32 + 1$). To perform this operation requires 'slicing' the
representation being worked with into 32-bit chunks. As finite field
representations are some kind of unsigned integer in every implementation, in
Plutus, this would correspond to `Integer`s, but currently, there is no way to
perform this kind of 'slicing' on an `Integer` on-chain.

Furthermore, finite field arithmetic can gain significant performance
optimizations with the use of bitwise primitive operations. Two good examples
are power-of-two division and computing inverses. The first of these (useful
even in `Integer` arithmetic) replaces a division by a power of 2 with a shift;
the second uses a count trailing zeroes operation to compute a multiplicative
finite field inverse. While some of these operations could theoretically be done
by other means, their performance is far from guaranteed. For example, GHC does
not convert a power-of-two division or multiplication to a shift, even if the
divisor or multiplier is statically-known. Given the restrictions on computation
resources on-chain, any gains are significant.

Having bitwise primitives, as well as the ability to convert `Integer`s into a
form amenable to this kind of work, would allow efficient finite field
arithmetic on-chain. This could enable a range of new uses without being
inefficient or difficult to port.

### Succinct data structures

Due to the on-chain size limit, many data structures become impractical or
impossible, as they require too much space either for their elements, or their
overheads, to allow them to fit alongside the operations we want to perform on
them. [Succinct data
structures](https://en.wikipedia.org/wiki/Succinct_data_structure) could serve 
as a solution to this, as they represent data in an amount of space much 
closer to the entropy limit and ensure only constant overheads. There are 
several examples of these, and all rely on bitwise operations for their 
implementations.

For example, consider wanting to store a set of `BuiltinInteger`s
on-chain. Given current on-chain primitives, the most viable option involves
some variant on a `BuiltinList` of `BuiltinInteger`s; however,
this is unviable in practice unless the set is small. To see why, suppose that
we have an upper limit of $k$ on the `BuiltinInteger`s we want to store;
this is realistic in practically all cases. To store $n$
`BuiltinInteger`s under the above scheme requires 

$$n \cdot \left( \left\lceil \frac{\log_2(k)}{64} \right\rceil \cdot 64  + c\right)
$$

bits, where $c$ denotes the constant overhead for each cons cell of
the `BuiltinList` holding the data. If the set being represented is dense
(meaning that the number of entries is a sizeable fraction of $k$), this cost
becomes intolerable quickly, especially when taking into account the need to
also store the operations manipulating such a structure on-chain with the script
where the set is being used.

If we instead represented the same set as a
[bitmap](https://en.wikipedia.org/wiki/Bit_array) based on
`BuiltinByteString`, the amount of space required would instead be 

$$\left\lceil \frac{k}{8} \right\rceil \cdot 8 + \left\lceil
\frac{\log_2(k)}{64} \right\rceil \cdot 64
$$

bits. This is significantly better unless $n$ is small. Furthermore,
this representation would likely be more efficient in terms of time in practice,
as instead of having to crawl through a cons-like structure, we can implement
set operations on a memory-contiguous byte string:

- The cardinality of the set can be computed as a population count. This
can have terrifyingly efficient implementations: the
[Muła-Kurz-Lemire](https://lemire.me/en/publication/arxiv161107612/)
algorithm (the current state of the art) can process four kilobytes per loop
iteration, which amounts to over four thousand potential stored integers.
- Insertion or removal is a bit set or bit clear respectively.
- Finding the smallest element uses a count leading zeroes.
- Finding the last element uses a count trailing zeroes.
- Testing for membership is a check to see if the bit is set.
- Set intersection is bitwise and.
- Set union is bitwise inclusive or.
- Set symmetric difference is bitwise exclusive or.

A potential implementation could use a range of techniques to make these
operations extremely efficient, by relying on
[SWAR](https://en.wikipedia.org/wiki/SWAR)
techniques if portability is desired, and
[SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) 
instructions for maximum speed. This would allow both potentially large 
integer sets to be represented on-chain without breaking the size limit, and 
nodes to efficiently compute with such, reducing the usage of resources by the 
chain. Lastly, in practice, if compression techniques are used (which also 
rely on bitwise operations!), the number of required bits can be reduced 
considerably in most cases without compromising performance: the current 
state-of-the-art ([Roaring Bitmaps](https://roaringbitmap.org/)) can be
used as an example of the possible gains.

In order to make such techniques viable, bitwise primitives are mandatory.
Furthermore, succinct data structures are not limited to sets of integers, but
*all* require bitwise operations to be implementable.

### Binary representations and encodings

On-chain, space comes at a premium. One way that space can be saved is with binary
representations, which can potentially represent something much closer to the
entropy limit, especially if the structure or value being represented has
significant redundant structure. While some possibilities for a more efficient
'packing' already exist in the form of `BuiltinData`, it is rather
idiosyncratic to the needs of Plutus, and its decoding is potentially quite
costly. 

Bitwise primitives would allow more compact binary encodings to be defined,
where complex structures or values are represented using fixed-size
`BuiltinByteString`s. The encoders and decoders for these could also be
implemented more efficiently than currently possible, as there exist numerous
bitwise techniques for this.

### On-chain vectors

For linear structures on-chain, we are currently limited to `BuiltinList`
and `BuiltinMap`, which don't allow constant-time indexing. This is a
significant restriction, especially when many data structures and algorithms
rely on the broad availability of a constant-time-indexable linear structure,
such as a C array or Haskell `Vector`. While we could introduce a primitive 
data type like this, doing so would be a significant undertaking, and would 
require both implementing and costing a large API.

While for variable-length data, we don't have any alternatives if constant-time
indexing is a goal, for fixed-length (or limited-length at least) data, there is
a possibility, based on a similar approach taken by the
[`finitary`](https://hackage.haskell.org/package/finitary)
library. Essentially, given finitary data, we can transform any item into a
numerical index, which is then stored by embedding into a byte array. As the
indexes are of a fixed maximum size, this can be done efficiently, but only if
there is a way of converting indices into bitstrings, and vice versa. Such a
construction would allow using a (wrapper around) `BuiltinByteString` as
a constant-time indexable structure of any finitary type. This is not much of a
restriction in practice, as on-chain, fixed-width or size-bounded types are
preferable due to the on-chain size limit.

Currently, all the pieces to make this work already exist: the only missing
piece is the ability to convert indices (which would have to be
`BuiltinInteger`s) into bit strings (which would have to be
`BuiltinByteString`s) and back again. With this capability, it would be
possible to use these techniques to implement something like an array or vector
without new primitive data types.

## Goals

To ensure a focused and meaningful proposal, we specify our goals below.

### Useful primitives

The primitives provided should enable implementations of algorithms and data
structures that are currently impossible or impractical. Furthermore, the
primitives provided should have a high power-to-weight ratio: having them should
enable as much as possible to be implemented.

### Maintaining as many algebraic laws as possible

Bitwise operations, via [Boolean
algebras](https://en.wikipedia.org/wiki/Boolean_algebra_(structure)), have a 
long and storied history of algebraic laws, dating back to important results 
by the like of de Morgan, Post and many others. These algebraic laws are 
useful for a range of reasons: they guide implementations, enable easier 
testing (especially property testing) and in some cases much more efficient 
implementations. To some extent, they also formalize our intuition about how 
these operations 'should work'. Thus, maintaining as many of these laws in our 
implementation as possible, and being clear about them, is important.

### Allowing efficient, portable implementations

Providing primitives alone is not enough: they should also be efficient. This is
not least of all because many would associate 'primitive operation' with a
notion of being 'close to the machine', and therefore fast. Thus, it is on us to
ensure that the implementations of the primitives we provide have to be
implementable in an efficient way, across a range of hardware.

### Clear indication of failure

While totality is desirable, in some cases, there isn't a sensible answer for us
to give. A good example is a division-by-zero: if we are asked to do such a
thing, the only choice we have is to reject it. However, we need to make it as
easy as possible for someone to realize why their program is failing, by
emitting a sensible message which can later be inspected.

## Non-goals

We also specify some specific non-goals of this proposal.

### No metaphor-mixing between numbers and bits

A widespread legacy of C is the mixing of treatment of numbers and blobs of
bits: specifically, the allowing of logical operations on representations of
numbers. This applies to Haskell as much as any other language: according to the
[Haskell
Report](https://www.haskell.org/onlinereport/haskell2010/haskellch15.html#x23-20800015), 
it is in fact *required* that any type implementing
`Bits` implement `Num` first. While GHC Haskell [only mandates
`Eq`](https://hackage.haskell.org/package/base-4.16.1.0/docs/Data-Bits.html#t:Bits), 
it still defines `Bits` instances for types clearly meant to
represent numbers. This is a bad choice, as it creates complex situations and
partiality in several cases, for arguably no real gain other than easier
translation of bit twiddling code originally written in C.

Even if two types share a representation, their type distinctness is meant to be
a semantic or abstraction boundary: just because a number is represented as a
blob of bits does not necessarily mean that arbitrary bit manipulations are
sensible. However, by defining such a capability, we create several semantic
problems:

- Some operations end up needing multiple definitions to take this into
account. A good example are shifts: instead of simply having left or right
shifts, we now have to distinguish *arithmetic* versus *logical*
shifts, simply to take into account that a shift can be used on something
which is meant to be a number, which could be signed. This creates
unnecessary complexity and duplication of operations.
- As Plutus `BuiltinInteger`s are of arbitrary precision, certain
bitwise operations are not well-defined on them. A good example is bitwise
complement: the bitwise complement of $0$ cannot be defined sensibly, and in
fact, is partial in its `Bits` instance.
- Certain bitwise operations on `BuiltinInteger` would have quite
undesirable semantic changes in order to be implementable. A good example
are bitwise rotations: we should be able to 'decompose' a rotation left or
right by $n$ into two rotations (by $m_1$ and $m_2$ such that $m_1 + m_2 = n$)
without changing the outcome. However, because trailing zeroes are not
tracked by the implementation, this can fail depending on the choice of
decomposition, which seems needlessly annoying for no good reason.
- Certain bitwise operations on `BuiltinInteger` would require
additional arguments and padding to define them sensibly. Consider bitwise
logical AND: in order to perform this sensibly on `BuiltinInteger`s
we would need to specify what 'length' we assume they have, and some policy
of 'padding' when the length requested is longer than one, or both,
arguments. This feels unnecessary, and it isn't even clear exactly how we
should do this: for example, how would negative numbers be padded?

These complexities, and many more besides, are poor choices, owing more to the
legacy of C than any real useful functionality. Furthermore, they feel like a
casual and senseless undermining of type safety and its guarantees for very
small and questionable gains. Therefore, defining bitwise operations on
`BuiltinInteger` is not something we wish to support.

There are legitimate cases where a conversion from `BuiltinInteger` to
`BuiltinByteString` is desirable; this conversion should be provided, and
be both explicit and specified in a way that is independent of the machine or
the implementation of `BuiltinInteger`, as well as total and
round-tripping. Arguably, it is also desirable to provide built-in support for
`BuiltinByteString` literals specified in a way convenient to their
treatment as blobs of bytes (for example, hexadecimal or binary notation), but
this is outside the scope of this proposal.

# Specification

## Proposed operations

We propose several classes of operations. Firstly, we propose two operations for
inter-conversion between  `BuiltinByteString` and `BuiltinInteger`:

```haskell
integerToByteString :: BuiltinInteger -> BuiltinByteString
```

Convert a non-negative number to its bitwise representation, erroring if given a
negative number.

---
```haskell
byteStringToInteger :: BuiltinByteString -> BuiltinInteger
```

Reinterpret a bitwise representation to its corresponding non-negative number.

---
We also propose several logical operations on `BuiltinByteString`s:

```haskell
andByteString :: BuiltinByteString -> BuiltinByteString -> BuiltinByteString
```
Perform a bitwise logical AND on arguments of the same
length, producing a result of the same length, erroring otherwise.

---
```haskell
iorByteString :: BuiltinByteString -> BuiltinByteString -> BuiltinByteString
```
Perform a bitwise logical IOR on arguments of the same
length, producing a result of the same length, erroring otherwise.

---
```haskell
xorByteString :: BuiltinByteString -> BuiltinByteString -> BuiltinByteString
```
Perform a bitwise logical XOR on arguments of the same
length, producing a result of the same length, erroring otherwise.

---
```haskell
complementByteString :: BuiltinByteString -> BuiltinByteString
```
Complement all the bits in the argument, producing a
result of the same length.

---
Lastly, we define the following additional operations:

```haskell
shiftByteString :: BuiltinByteString -> BuiltinInteger -> BuiltinByteString
```
Performs a bitwise shift of the first argument by a number of bit positions
equal to the absolute value of the second argument. A positive second argument
indicates a shift towards higher bit indexes; a negative second argument
indicates a shift towards lower bit indexes.

---
```haskell
rotateByteString :: BuiltinByteString -> BuiltinInteger -> BuiltinByteString
```
Performs a bitwise rotation of the first argument by a number of bit positions
equal to the absolute value of the second argument.  A positive second argument
indicates a rotation towards higher bit indexes; a negative second argument
indicates a rotation towards lower bit indexes.

---
```haskell
popCountByteString :: BuiltinByteString -> BuiltinInteger
```
Returns the number of $1$ bits in the argument.

---
```haskell
testBitByteString :: BuiltinByteString -> BuiltinInteger -> BuiltinBool
```
If the position given by the second argument is not in
bounds for the first argument, error; otherwise, if the bit given by that
position is $1$, return `True`, and `False` otherwise.

---
```haskell
writeBitByteString :: BuiltinByteString -> BuiltinInteger -> BuiltinBool -> BuiltinByteString
```
If the position given by the second argument is not in bounds for the first 
argument, error; otherwise, set the bit given by that position to $1$ if the 
third argument is `True`, and $0$ otherwise.

---
```haskell
countLeadingZeroesByteString :: BuiltinByteString -> BuiltinInteger
```

Counts the initial sequence of 0 bits in the argument (that is, starting from
index 0). If the argument is empty, this returns 0.

---
```haskell
countTrailingZeroesByteString :: BuiltinByteString -> BuiltinInteger
```

Counts the final sequence of 0 bits in the argument (that is, starting from the
1 bit with the highest index). If the argument is empty, this returns 0.

## Semantics

### Preliminaries

We define $\mathbb{N}^{+} = \\{ x \in \mathbb{N} \mid x \neq 0 \\}$. We assume
that `BuiltinInteger` is a faithful representation of $\mathbb{Z}$, and will
refer to them (and their elements) interchangeably. A *byte* is some 
$x \in \\{ 0,1,\ldots,255 \\}$.

We observe that, given some *base* $b \in \mathbb{N}^{+}$, any 
$n \in \mathbb{N}$ can be viewed as a sequence of values in $\\{0,1,\ldots, b - 1\\}$.
We refer to any such sequence as a *base* $b$ *sequence*. In such a 'view', given 
a base $b$ sequence $S = s_0 s_1 \ldots s_k$, we can compute its corresponding 
$m \in \mathbb{N}^+$ as 

$$\sum_{i \in \\{0,1,\ldots,k\\}} b^{k - i} \cdot s_i$$

If $b > 1$ and $Z$ is a base $b$ sequence consisting only of zeroes, we observe 
that for any other base $b$ sequence $S$, $Z \cdot S$ and $S$ correspond to the 
same number, where $\cdot$ is sequence concatenation.

We use *bit sequence* to refer to a base 2 sequence, and *byte sequence* to
refer to a base 256 sequence. For a bit sequence $S = b_0 b_1 \ldots b_n$, we
refer to $\\{0,1,\ldots,n \\}$ as the *valid bit indices* of $S$; analogously,
for a byte sequence $T = y_0 y_1 \ldots y_m$, we refer to $\\{0,1,\ldots,m\\}$
as the *valid byte indices* of $T$. We observe that the length of $S$ is $n + 1$
and the length of $T$ is $m + 1$; we refer to these as the *bit length* of $S$
and the *byte length* of $T$ for clarity. We write $S[i]$ and $T[j]$ to
represent $b_i$ and $y_j$ for valid bit index $i$ and valid byte index $j$
respectively.

We describe a 'view' of bytes as bit sequences. Let $y$ be a byte; its
corresponding bit sequence is $S_y = y_0 y_1 y_2 y_3 y_4 y_5 y_6 y_7$ such that

$$\sum_{i \in \\{0,1,\ldots,7\\}} 2^{7 - i} \cdot y_i = y$$

For example, the byte $55$ has the corresponding byte sequence $00110111$. For
any byte, its corresponding byte sequence is unique. We use this to extend our
'view' to byte sequences as bit sequences. Specifically, let 
$T = y_0 y_1 \ldots y_m$ be a byte sequence. Its corresponding bit sequence 
$S = b_0b_1 \ldots b_m b_{m + 1} \ldots b_{8(m + 1) - 1}$ such that for any valid bit index $j$ of $S$,
$b_j = 1$ if and only if $T[j / 8][j \mod 8] = 1$, and is $0$ otherwise. 

Based on the above, we observe that any `BuiltinByteString` can be a bit
sequence or a byte sequence. Furthermore, we assume that `indexByteString` and 
`sliceByteString` 'agree' with valid byte indices. More precisely, suppose 
`bs` represents a byte sequence $T$; then `indexByteString bs i` is seen as 
equivalent to $T[\mathtt{i}]$; we extend this notion to `sliceByteString` 
analogously. Throughout, we will refer to `BuiltinByteString`s and their 'views'
as bit or byte sequences interchangeably.

### Representation of `BuiltinInteger` as `BuiltinByteString` and conversions

We describe the translation of `BuiltinInteger` into `BuiltinByteString`, which
is implemented as the `integerToByteString` primitive. Let $i$ be the argument
`BuiltinInteger`; if this is negative, we produce an error, specifying at least
the following:

- The fact that specifically the `integerToByteString` operation failed;
- The reason (given a negative number); and 
- What exact number was given as an argument.

Otherwise, we produce the `BuiltinByteString` corresponding to the base 256
sequence which represents $i$.

We now describe the reverse operation, implemented as the `byteStringToInteger`
primitive. This treats its argument `BuiltinByteString` as a base 256 sequence,
and produces its corresponding number as a `BuiltinInteger`. We note that this
is necessarily non-negative.

We observe that `byteStringToInteger` 'undoes' `integerToByteString`:

```haskell
byteStringToInteger . integerToByteString = id
```

The other direction does not necessarily hold: if the argument to
`byteStringToInteger` contains a prefix consisting only of zeroes, and we
convert the resulting `BuiltinInteger` `i` back to a `BuiltinByteString` using
`integerToByteString`, that prefix will be lost.

### Bitwise logical operations on `BuiltinByteString`

Throughout, let $S = s_0 s_1 \ldots s_n$ and $T = t_0 t_1 \ldots t_n$ be byte 
sequences, and let $S^{\prime}$ and $T^{\prime}$ be their corresponding bit
sequences, with bit lengths $n^{\prime} + 1$ and $m^{\prime} + 1$ respectively.
Whenever we specify a *mismatched length error* result, its error message 
must contain at least the following information:

- The name of the failed operation;
- The reason (mismatched lengths); and
- The byte lengths of the arguments.

For any of `andByteString`, `iorByteString` and `xorByteString`, given inputs
$S$ and $T$, if $n \neq m$, the result is an error which must contain at least
the following information:

- The name of the failed operation;
- The reason (mismatched lengths); and
- The byte lengths of the arguments.

If $n = m$, the result of each of these operations is the bit sequence 
$U = u_0u_1 \ldots u_{n^{\prime}}$, such that for all $i \in \\{0, 1, \ldots, n^{\prime}\\}$,
$U[i] = 1$ under the following conditions:

- For `andByteString`, when $S^{\prime}[i] = T^{\prime}[i] = 1$;
- For `iorByteString`, when at least one of $S^{\prime}[i], T^{\prime}[i]$ is
  $1$;
- For `xorByteString`, when $S^{\prime}[i] \neq T^{\prime}[i]$.

Otherwise, $U[i] = 0$.

We observe that, for length-matched arguments, each of these operations
describes a commutative and associative operation. Furthermore, for any given
byte length $k$, each of these operations has an identity element:

- For `andByteString` and `xorByteString`, the byte sequence of length $k$ where
  each element is zero; and
- For `iorByteString`, the byte sequence of length $k$ where each element is
  255.

Lastly, `andByteString` and `iorByteString` have an absorbing element for each
byte length $k$, which is the byte sequence of length $k$ where each element is
zero and 255 respectively.

We now describe the semantics of `complementByteString`. For input $S$, the
result is the bit sequence $U = u_0 u_1 \ldots u_{n^{\prime}}$ such that for all
$i \in \{0, 1, \ldots, n^{\prime}\}$, we have $U[i] = 0$ if $S^{\prime}[i] = 1$ 
and $1$ otherwise.

We observe that `complementByteString` is self-inverting. We also note
the following equivalences hold assuming `b` and `b'` have the
same length; these are [De Morgan's
laws](https://en.wikipedia.org/wiki/De_Morgan%27s_laws):

```haskell
complementByteString (andByteString b b') = iorByteString (complementByteString b) (complementByteString b')
```

```haskell
complementByteString (iorByteString b b') = andByteString (complementByteString b) (complementByteString b')
```

### Mixed operations

Throughout, let $S = s_0 s_1 \ldots s_n$ be a byte sequence, and let 
$S^{\prime}$ be its corresponding bit sequence with bit length $n^{\prime} + 1$.

We describe the semantics of `shiftByteString` and `rotateByteString`.
Informally, both of these are 'bit index modifiers': given a positive $i$, the
index of a bit in the result 'increases' relative to the argument, and given a
negative $i$, the index of a bit in the result 'decreases' relative to the
argument. This can mean that for some bit indexes in the result, there is no
corresponding bit in the argument: we term these *missing indexes*.
Additionally, by such calculations, a bit index in the argument may be projected
to a negative index in the result: we term these *out-of-bounds indexes*. How we
handle missing and out-of-bounds indexes is what distinguishes `shiftByteString`
and `rotateByteString`:

* `shiftByteString` sets any missing index to $0$ and ignores any data at
  out-of-bounds indexes.
* `rotateByteString` uses out-of-bounds indexes as sources for missing indexes
  by 'wraparound'.

We describe the semantics of `shiftByteString` precisely. Given arguments $S$
and some $i \in \mathbb{Z}$, the result is the bit sequence 
$U = u_0 u_1 \ldots u_{n^{\prime}}$ such that for all 
$j \in \\{0, 1, \ldots, n^{\prime}\\}$, we have $U[j] = S^{\prime}[j - i]$ if 
$j - i$ is a valid bit index for $S^{\prime}$ and $0$ otherwise.

Let $k, \ell \in \mathbb{Z}$ 
such that either 
$k$ or $\ell$ is $0$, or 
$k$ and $\ell$ have the same sign. 
We observe that, for any `bs`, we have


```haskell
shiftByteString (shiftBytestring bs k) l = shiftByteString bs (k + l)
```

We now describe the semantics of `rotateByteString` precisely; we assume the
same arguments as for `shiftByteString` above. The result is the bit sequence 
$U = u_0 u_1 \ldots u_{n^{\prime}}$ such that for all 
$j \in \\{0, 1, \ldots, n^{\prime}\\}$, we have $U[j] = S^{\prime}[n^{\prime} + j - i \mod n^{\prime}]$.

We observe that for any $k, \ell$, and any
`bs`, we have

```haskell
rotateByteString (rotateByteString bs k) l = rotateByteString bs (k + l)
```

We also note that

```haskell
rotateByteString bs 0 = shiftByteString bs 0 = bs
```

Lastly, we note that

```haskell
rotateByteString bs k = rotateByteString bs (k `remInteger` (lengthByteString bs * 8))
```

For `popCountByteString` with argument $S$, the result is 

$$\sum_{j \in \\{0, 1, \ldots, n^{\prime}\\}} S^{\prime}[j]$$

Informally, this is just the total count of $1$ bits. We observe that 
for any `bs` and `bs'`, we have

```haskell
popCountByteString bs + popCountByteString bs' = popCountByteString (appendByteString bs bs')
```

We now describe the semantics of `testBitByteString` and `writeBitByteString`. 
Throughout, whenever we specify an *out-of-bounds error* result, its error 
message must contain at least the following information:

- The name of the failed operation;
- The reason (out of bounds access);
- What index was accessed out-of-bounds; and
- The valid range of indexes.

For `testBitByteString` with arguments $S$ and some $i \in \mathbb{Z}$, if $i$
is a valid bit index of $S^{\prime}$, the result is `True` if 
$S^{\prime}[i] = 1$, and `False` if $S^{\prime}[i] = 0$. If $i$ is not a valid 
bit index of $S^{\prime}$, the result is an out-of-bounds error.

For `writeBitByteString` with arguments $S$, some $i \in \mathbb{Z}$ and some
`BuiltinBool` $b$, if $i$ is not a valid bit index for $S^{\prime}$, the result
is an out-of-bounds error. Otherwise, the result is the bit sequence 
$U = u_0 u_1 \ldots u_{n^{\prime}}$ such that for all $j \in \\{0, 1, \ldots, n\\}$, we
have:

- $U[j] = 1$ when $i = j$ and $b$ is `True`;
- $U[j] = 0$ when $i = j$ and $b$ is `False`;
- $U[j] = S^{\prime}[j]$ otherwise.

Lastly, we describe the semantics of `countLeadingZeroesByteString` and
`countTrailingZeroesByteString`. Given the argument $S$,
`countLeadingZeroesByteString` gives the result $k$ such that all of the
following hold:

- $0 \leq k < n^{\prime} + 1$;
- For all $0 \leq i < k$, $S^{\prime}[i] = 0$; and
- If $n^{\prime} \neq 0$, then $S^{\prime}[k] = 1$.

Given the same argument, `countTrailingZeroesByteString` instead gives the
result $k$ such that all of the following hold:

- $0 \leq k < n^{\prime} + 1$;
- For all $k \leq i < n^{\prime}$, $S^{\prime}[i] = 0$; and
- If $k /neq n^{\prime} + 1$, then $S^{\prime}[n^{prime} - k] = 1$.

Let `zeroes` be a `BuiltinByteString` consisting only of zero bytes of length
`len`. We observe that

```haskell
countTrailingZeroesByteString zeroes = countLeadingZeroesByteString zeroes = len
* 8
```

Furthermore, for two `BuiltinByteString`s `bs` and `bs'`, we have

```haskell
countLeadingZeroesByteString (iorByteString bs bs') = 
  min (countLeadingZeroesByteString bs) (countLeadingZeroesByteString bs')

countTrailingZeroesByteString (iorByteString bs bs') = 
  min (countTrailingZeroesByteString bs) (countTrailingZeroesByteString bs')
```

where `min` is the minimum value function.

### Costing

All of the primitives we describe are linear in one of their arguments. For a
more precise description, see the table below.

Primitive | Linear in
--- | ---
`integerToByteString` | Argument (only one)
`byteStringToInteger` | Argument (only one)
`andByteString` | One argument (same length for both)
`iorByteString` | One argument (same length for both)
`xorByteString` | One argument (same length for both)
`complementByteString` | Argument (only one)
`shiftByteString` | `BuiltinByteString` argument
`rotateByteString` | `BuiltinByteString` argument
`popCountByteString` | Argument (only one)
`testBitByteString` | `BuiltinByteString` argument
`writeBitByteString` | `BuiltinByteString` argument
`countLeadingZeroesByteString` | Argument (only one)
`countTrailingZeroesByteString` | Argument (only one)

# Rationale

## Why these operations?

For work in finite field arithmetic (and the areas it enables), we frequently
need to move between the 'worlds' of `BuiltinInteger` and `BuiltinByteString`.
This needs to be consistent, and allow round-trips. We simplify this by only
requiring conversions work on non-negative integers: this means that the
translations can be simpler and more efficient, and also avoids representational
questions for negative numbers.

Our choice of logical AND, IOR, XOR and complement as the primary logical 
operations is driven by a mixture of prior art, utility and convenience. These
are the typical bitwise logical operations provided in hardware, and in most
programming languages; for example, in the x86 instruction set, the following
bitwise operations have existed since the 8086:

- `AND`: Bitwise AND.
- `OR`: Bitwise IOR.
- `NOT`: Bitwise complement.
- `XOR`: Bitwise XOR.

Likewise, on the ARM instruction set, the following bitwise operations have
existed since ARM2:

- `AND`: Bitwise AND.
- `ORR`: Bitwise IOR.
- `EOR`: Bitwise XOR.
- `ORN`: Bitwise IOR with complement of the second argument.
- `BIC`: Bitwise AND with complement of the second argument.

Going 'up a level', the C and Forth programming languages (according to C89 and
ANS Forth respectively) define bitwise AND (denoted `&` and `AND` 
respectively), bitwise IOR (denoted `|` and `OR` respectively), bitwise XOR 
(denoted ` ^` and `XOR` respectively) and bitwise complement (denoted `~` and 
`NOT` respectively) as primitive bitwise operations. These choices are mirrored 
by basically all 'high-level' languages; for example, Haskell's `Bits` type
class defines these same four operations as `.&.`, `.|.`, `xor` and `complement`
respectively.

This ubiquity in choices leads to most algorithm descriptions that rely on 
bitwise operations to assume that these specific four operations are 
'primitive', implying that they are constant-time and constant-cost. While we
could reduce the number of primitive bitwise operations (and, in fact, due to
Post, we know that there exist two operations that can implement all of them),
this would be both inconvenient and inefficient. As an example, consider
implementing XOR using AND, IOR and complement: this would translate `x XOR y`
into 

```
(COMPLEMENT x AND y) IOR (x AND COMPLEMENT y)
```

This is both needlessly complex, and also inefficient, as it requires copying
the arguments twice, only to then throw away both copies. This is less of a
concern if copying is 'cheap', but given that we need to operate on
variable-width data (specifically `BuiltinByteString`s), this seems needlessly
wasteful.

Like our 'baseline' bitwise operations above, shifts and rotations are widely
used, and considered as primitive. For example, x86 platforms have had the
following available since the 8086:

- `RCL`: Rotate left.
- `RCR`: Rotate right.
- `SHL`: Shift left.
- `SHR`: Shift right.

Likewise, ARM platforms have had the following available since ARM2:

- `ROR`: Rotate right.
- `LSL`: Shift left.
- `LSR`: Shift right.

While C and Forth both have shifts (denoted with `<<` and `>>` in C, and 
`LSHIFT` and `RSHIFT` in Forth), they don't have rotations; however, many 
higher-level languages do: Haskell's `Bits` type class has `rotate`, which 
enables both left and right rotations.

While `popCountByteString` could in theory be simulated using 
`testBitByteString` and a fold, this is quite inefficient: the best way to 
simulate this operation would involve using something similar to the 
Harley-Seal algorithm, which requires a large lookup table, making it 
impractical on-chain. Furthermore, population counting is important for several
classes of succinct data structure (particularly rank-select dictionaries and
bitmaps), and is in fact provided as part of the `SSE4.2` x86 instruction set 
as a primitive named `POPCNT`.

In order to usefully manipulate individual bits, both `testBitByteString`
and `writeBitByteString` are needed. They can also be used as part of 
specifying, and verifying, that other bitwise operations, both primitive and
non-primitive, are behaving correctly. They are also particularly essential for
binary encodings.

`countLeadingZeroesByteString` and `countTrailingZeroesByteString` is an
essential primitive for several succinct data structures: both Roaring Bitmaps
and rank-select dictionaries rely on them for much of their usefulness. For
finite field arithmetic, these instructions are also beneficial to have
available as efficiently as possible. Furthermore, this operation is provided 
in hardware by several instruction sets: 
on x86, there exist (at least) `BSF`, `BSR`, `LZCNT` and `TZCNT`, while on ARM, 
we have `CLZ` for counting leading zeroes. These instructions also exist in higher-level 
languages: for example, GHC's `FiniteBits` type class has `countTrailingZeros` 
and `countLeadingZeros`. Lastly, while they can be emulated by
`testBitByteString`, this is tedious, error-prone and extremely slow.

# Backwards compatibility 

At the Plutus Core level, implementing this proposal introduces no
backwards-incompatibility: the proposed new primitives do not break any existing
functionality or affect any other builtins. Likewise, at levels above Plutus
Core (such as `PlutusTx`), no existing functionality should be affected.

On-chain, this requires a hard fork, as this introduces new primitives.

# Path to Active

MLabs will implement these primitives, as well as tests for these. Costing will
have to be done after this is complete, but must be done by the Plutus Core
team, due to limitations in how costing is performed.

# Copyright

This CIP is licensed under Apache-2.0.
