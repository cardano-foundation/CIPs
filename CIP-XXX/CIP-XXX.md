---
CIP: ???
Title: Logical operations
Category: Plutus
Status: Proposed
Authors: 
    - Koz Ross <koz@mlabs.city>
Implementors: 
    - Koz Ross <koz@mlabs.city>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-04-30
License: Apache-2.0
---

## Abstract

We describe the semantics of a set of logical operations for Plutus
`BuiltinByteString`s. Specifically, we provide descriptions for:

- Bitwise logical AND, OR, XOR and complement;
- Reading a bit value at a given index;
- Setting bits value at given indices; and
- Replicating a byte a given number of times.

As part of this, we also describe the bit ordering within a `BuiltinByteString`,
and provide some laws these operations should obey.

## Motivation: why is this CIP necessary?

Bitwise operations, both over fixed-width and variable-width blocks of bits,
have a range of uses, including data structures (especially
[succinct][succinct-data-structures] ones) and cryptography. Currently,
operations on individual bits in Plutus Core are difficult, or outright
impossible, while also keeping within the tight constraints required onchain.
While it is possible to some degree to work with individual _bytes_ over
`BuiltinByteString`s, this isn't sufficient, or efficient, when bit
maniputations are required.

To demonstrate where bitwise operations would allow onchain possibilities that
are currently either impractical or impossible, we give the following use cases.

### Case 1: integer set

An _integer set_ (also known as a bit set, bitmap, or bitvector) is a
[succinct][succinct-data-structures] data structure for representing a set of
numbers in a pre-defined range $[0, n)$ for some $n \in \mathbb{N}$. The
structure supports the following operations:

* Construction given a fixed number of elements, as well as the bound $n$.
* Construction of the empty set (contains no elements) and the universe
  (contains all elements).
* Set union, intersection, complement and difference (symmetric and asymmetric).
* Membership testing for a specific element.
* Inserting or removing elements.

These structures have a range of uses. In addition to being used as sets of
bounded natural numbers, an integer set could also represent an array of Boolean
values. These have [a range of applications][bitvector-apps], mostly as
'backends' for other, more complex structures. Furthermore, by using some index 
arithmetic, integer sets can also be used to represent 
[binary matrices][binary-matrix] (in any number of
dimensions), which have an even wider range of uses:

* Representations of graphs in [adjacency-matrix][adjacency-matrix] form
* [Checking the rules for a game of Go][go-binary-matrix]
* [FSM representation][finite-state-machine-4vl]
* Representation of an arbitrary binary relation between finite sets

The succinctness of the integer set (and the other succinct data structures it
enables) is particularly valuable on-chain, due to the limited transaction size
and memory available.

Typically, such a structure would be represented as a packed array of bytes
(similar to the Haskell `ByteString`). Essentially, given a bound $n$, the
packed array has a length in bytes large enough to contain at least $n$ bits,
with a bit at position $i$ corresponding to the value $i \in \mathbb{N}$. This 
representation ensures the succinctness of the structure (at most 7 bits of 
overhead are required if $n = 8k + 1$ for some $k \in \mathbb{N}$), and
also allows all the above operations to be implemented efficiently:

* Construction given a fixed number of elements and the bound $n$ involves
  allocating the packed array, then modifying some bits to be set.
* Construction of the empty set is a packed array where every byte is `0x00`,
  while the universe is a packed array where every byte is `0xFF`.
* Set union is bitwise OR over both arguments.
* Set intersection is bitwise AND over both arguments.
* Set complement is bitwise complement over the entire packed array.
* Symmetric set difference is bitwise XOR over both arguments; asymmetric set
  difference can be defined using a combination of bitwise complement and
  bitwise OR.
* Membership testing is checking whether a bit is set.
* Inserting an element is setting the corresponding bit.
* Removing an element is clearing the corresponding bit.

Given that this is a packed representation, these operations can be implemented
very efficiently by relying on the cache-friendly properties of packed array
traversals, as well as making use of optimized routines available in many
languages. Thus, this structure can be used to efficiently represent sets of
numbers in any bounded range (as ranges not starting from $0$ can be represented
by storing an offset), while also being minimal in space usage.

Currently, such a structure cannot be easily implemented in Plutus Core while
preserving the properties described above. The two options using existing
primitives are either to use `[BuiltinInteger]`, or to mimic the above
operations over `BuiltinByteString`. The first of these is not space _or_
time-efficient: each `BuiltinInteger` takes up multiple machine words of space,
and the list overheads introduced are linear in the number of items stored,
destroying succinctness; membership testing, insertion and removal require
either maintaining an ordered list or forcing linear scans for at least some
operations, which are inefficient over lists; and 'bulk' operations like union,
intersection and complement become very difficult and time-consuming. The second
is not much better: while we preserve succinctness, there is no easy way to
access individual bits, only bytes, which would require a division-remainder
loop for each such operation, with all the overheads this imposes; intersection,
union and symmetric difference would have to be simulated byte-by-byte,
requiring large lookup tables or complex conditional logic; and construction
would require immense amounts of copying and tricky byte construction logic.
While it is not outright impossible to make such a structure using current
primitives, it would be so impractical that it could never see real use.

Furthermore, for sparse (or dense) integer sets (that is, where either most
elements in the range are absent or present respectively), a range of
[compression techniques][bitmap-index-compression] have been developed. All of
these rely on bitwise operations to achieve their goals, and can potentially
yield significant space savings in many cases. Given the limitations onchain
that we have to work within, having such techniques available to implementers
would be a huge potential advantage.

### Case 2: hashing

[Hashing][hashing], that is, computing a fixed-length 'fingerprint' or 'digest'
of a variable-length input (typically viewed as binary) is a common task
required in a range of applications. Most notably, hashing is a key tool in
cryptographic protocols and applications, either in its own right, or as part of
a larger task. The value of such functionality is such that Plutus Core already
contains primitives for certain hash functions, specifically two variants of
[SHA256][sha-256] and [BLAKE2b][blake2b]. At the same time, hash functions
choices are often determined by protocol or use case, and providing individual
primitives for every possible hash function is not a scalable choice. It is much
preferrable to give necessary tools to implement such functionality to users of
Plutus (Core), allowing them to use whichever hash function(s) their
applications require.

As an example, we consider the [Argon2][argon2] family of hash functions. In
order to implement any of this family requires the following operations:

1. Conversion of numbers to bytes
2. Bytestring concatenation
3. BLAKE2b hashing
4. Floor division
5. Indexing bytes in a bytestring
6. Logical XOR

Operations 1 to 5 are already provided by Plutus Core (with 1 being included [in
a recent CIP][conversion-cip]); however, without logical XOR, no function in the
Argon2 family could be implemented. While in theory, it could be simulated with
what operations already exist, much as with Case 1, this would be impractical at
best, and outright impossible at worst, due to the severe limits imposed
on-chain. This is particularly the case here, as all Argon2 variants call
logical XOR in a loop, whose step count is defined by _multiple_ user-specified
(or protocol-specified) parameters.

We observe that this requirement for logical XOR is not unique to the Argon2
family of hash functions. Indeed, logical XOR is widely used for [a variety of
cryptographic applications][xor-crypto], as it is both a low-cost mixing
function that happens to be self-inverting, as well as preserving randomness
(that is, a random bit XORed with a non-random bit will give a random bit).  

## Specification

We describe the proposed operations in several stages. First, we specify a
scheme for indexing individual bits (rather than whole bytes) in a
`BuiltinByteString`. We then specify the semantics of each operation, as well as
giving costing expectations. Lastly, we provide some laws that these operations
are supposed to obey, as well as giving some specific examples of results from
the use of these operations.

### Bit indexing scheme

We begin by observing that a `BuiltinByteString` is a packed array of bytes
(that is, `BuiltinInteger`s in the range $[0, 255]$) according to the API
provided by existing Plutus Core primitives. In particular, we have the ability
to access individual bytes by index as a primitive operation. Thus, we can view
a `BuiltinByteString` as an indexed collection of bytes; for any
`BuiltinByteString` $b$ of length $n$, and any $i \in 0, 1, \ldots, n - 1$, we
define $b\\{i\\}$ as the byte at index $i$ in $b$, as defined by the
`builtinIndexByteString` primitive. In essence, for any `BuiltinByteString` of
length `n`, we have _byte_ indexes as follows:

```
| Index | 0  | 1  | ... | n - 1    |
|-------|----|----| ... |----------|
| Byte  | w0 | w1 | ... | w(n - 1) |
```

To view a `BuiltinByteString` as an indexed collection of _bits_, we must first
consider the bit ordering within a byte. Suppose $i \in 0, 1, \ldots, 7$ is an
index into a byte $w$. We say that the bit at $i$ in $w$ is _set_ when

$$
\left \lfloor \frac{w}{2^{i}} \right \rfloor \mod 2 \equiv 1
$$

Otherwise, the bit at $i$ in $w$ is _clear_. We define $w[i]$ to be $1$ when 
the bit at $i$ in $w$ is set, and $0$ otherwise; this is the _value_ at index
$i$ in $w$.

For example, consider the byte represented by the `BuiltinInteger` 42. By the
above scheme, we have the following:

| Bit index | Set or clear? |
|-----------|---------------|
| $0$       | Clear         |
| $1$       | Set           |
| $2$       | Clear         |
| $3$       | Set           |
| $4$       | Clear         |
| $5$       | Set           |
| $6$       | Clear         |
| $7$       | Clear         |

Put another way, we can view $w[i] = 1$ to mean that the $(i + 1)$ th least significant
digit in $w$'s binary representation is $1$, and likewise, $w[i] = 0$ would mean
that the $i$th least significant digit in $w$'s binary representation is $0$.
Continuing with the above example, $42$ is represented in binary as `00101010`;
we can see that the second-least-significant, fourth-least-significant, and
sixth-least-significant digits are `1`, and all the others are zero. This
description mirrors the way bytes are represented on machine architectures.

We now extend the above scheme to `BuiltinByteString`s. Let $b$ be a
`BuiltinByteString` whose length is $n$, and let $i \in 0, 1, \ldots, 8 \cdot n - 1$. 
For any $j \in 0, 1, \ldots, n - 1$, let $j^{\prime} = n - j - 1$. We say that the bit 
at $i$ in $b$ is set if

$$
b\left\\{\left(\left\lfloor \frac{i}{8} \right\rfloor\right)^{\prime}\right\\}[i\mod 8] = 1
$$

We define the bit at $i$ in $b$ being clear analogously. Similarly to bits in a
byte, we define $b[i]$ to be $1$ when the bit at $i$ in $b$ is set, and $0$
otherwise; similarly to bytes, we term this the _value_ at index $i$ in $b$.

As an example, consider the `BuiltinByteString` `[42, 57, 133]`: that is, the
`BuiltinByteString` $b$ such that $b\\{0\\} = 42$, $b\\{1\\} = 57$ and $b\\{2\\}
= 133$. We observe that the range of 'valid' bit indexes $i$ into $b$ is in 
$[0, 3 \cdot 8 - 1 = 23]$. Consider $i = 4$; by the definition above, this
corresponds to the _byte_ index 2, as $\left\lfloor\frac{4}{8}\right\rfloor =
0$, and $3 - 0 - 1 = 2$ (as $b$ has length $3$). Within the byte $133$, this
means we have $\left\lfloor\frac{133}{2^4}\right\rfloor \mod 2 \equiv 0$. Thus,
$b[4] = 0$. Consider instead the index $i = 19$; by the definition above, this
corresponds to the _byte_ index 0, as $\left\lfloor\frac{19}{8}\right\rfloor =
2$, and $3 - 2 - 1 = 0$. Within the byte $42$, this means we have
$\left\lfloor\frac{42}{2^3}\right\rfloor `mod 2 \equiv 1$. Thus, $b[19] = 1$. 

Put another way, our _byte_ indexes run 'the opposite way' to our _bit_ indexes.
Thus, for any `BuiltinByteString` of length $n$, we have _bit_ indexes relative
_byte_ indexes as follows:

```
| Byte index | 0                              | 1  | ... | n - 1                         |
|------------|--------------------------------|----| ... |-------------------------------|
| Byte       | w0                             | w1 | ... | w(n - 1)                      |
|------------|--------------------------------|----| ... |-------------------------------|
| Bit index  | 8n - 1 | 8n - 2 | ... | 8n - 8 |   ...    | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
```

### Operation semantics

We describe precisely the operations we intend to implement, and their
semantics. These operations will have the following signatures:

* `builtinLogicalAnd :: BuiltinBool -> BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString`
* `builtinLogicalOr :: BuiltinBool -> BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString`
* `builtinLogicalXor :: BuiltinBool -> BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString`
* `builtinLogicalComplement :: BuiltinByteString -> BuiltinByteString`
* `builtinReadBit :: BuiltinByteString -> BuiltinInteger -> BuiltinBool`
* `builtinSetBits :: BuiltinByteString -> [(BuiltinInteger, BuiltinBool)] ->
  BuiltinByteString`
* `builtinReplicate :: BuiltinInteger -> BuiltinInteger -> BuiltinByteString`

#### Padding versus truncation semantics

For the binary logical operations (that is, `builtinLogicalAnd`,
`builtinLogicalOr` and `builtinLogicalXor`), the we have two choices of
semantics when handling `BuiltinByteString` arguments of different lengths. We
can either produce a result whose length is the _minimum_ of the two arguments
(which we call _truncation semantics_), or produce a result whose length is the
_maximum_ of the two arguments (which we call _padding semantics_). As these can
both be useful depending on context, we allow both, controlled by a
`BuiltinBool` flag, on all the operations listed above. 

For example, consider the `BuiltinByteString`s `x = [0x00, 0xF0, 0xFF]` and `y =
[0xFF, 0xF0]`. Under padding semantics, the result of `builtinLogicalAnd`,
`builtinLogicalOr` or `builtinLogicalXor` using these two as arguments would
have a length of 3; under truncation semantics, the result would have a length
of 2 instead. 

#### `builtinLogicalAnd`

`builtinLogicalAnd` takes three arguments; we name and describe them below.

1. Whether padding semantics should be used. If this argument is `False`,
   truncation semantics are used instead. This is the _padding semantics
   argument_, and has type `BuiltinBool`.
2. The first input `BuiltinByteString`. This is the _first data argument_.
3. The second input `BuiltinByteString`. This is the _second data argument_.

Let $b_1, b_2$ refer to the first data argument and the second data
argument respectively, and let $n_1, n_2$ be their respective lengths in bytes.
Let the result of `builtinLogicalAnd`, given $b_1, b_2$ and some padding
semantics argument, be $b_r$, of length $n_r$ in bytes. We use $b_1[i]$ to refer 
to the value at index $i$ of $b_1$ (and analogously for 
$b_2, b_r$); see the [section on the bit indexing scheme](#bit-indexing-scheme)
for the exact specification of this.

If the padding semantics argument is `True`, then we have $n_r = \max \\{ n_1,
n_2 \\}$; otherwise, $n_r = \min \\{ n_1, n_2 \\}$. For all $i \in 0, 1, \ldots 8
\cdot n_r - 1$, we have

$$
b_r[i] = \begin{cases}
         b_0[i] & \text{if } n_1 < n_0 \text{ and } i \geq 8 \cdot \min \\{ n_1, n_2 \\} \\
         b_1[i] & \text{if } n_0 < n_1 \text { and } i \geq 8 \cdot \min \\{ n_1, n_2 \\} \\
         1 & \text{if } b_0[i] = b_1[i] = 1 \\
         0 & \text{otherwise} \\
         \end{cases}
$$

Some examples of the intended behaviour of `builtinLogicalAnd` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- truncation semantics
builtinLogicalAnd False [] [0xFF] => []

builtinLogicalAnd False [0xFF] [] => []

builtinLogicalAnd False [0xFF] [0x00] => [0x00]

builtinLogicalAnd False [0x00] [0xFF] => [0x00]

builtinLogicalAnd False [0x4F, 0x00] [0xF4] => [0x44]

-- padding semantics
builtinLogicalAnd True [] [0xFF] => [0xFF]

builtinLogicalAnd True [0xFF] [] => [0xFF]

builtinLogicalAnd False [0xFF] [0x00] => [0x00]

builtinLogicalAnd False [0x00] [0xFF] => [0x00]

builtinLogicalAnd False [0x4F, 0x00] [0xF4] => [0x44, 0x00]
```

#### `builtinLogicalOr`

`builtinLogicalOr` takes three arguments; we name and describe them below.

1. Whether padding semantics should be used. If this argument is `False`,
   truncation semantics are used instead. This is the _padding semantics
   argument_, and has type `BuiltinBool`.
2. The first input `BuiltinByteString`. This is the _first data argument_.
3. The second input `BuiltinByteString`. This is the _second data argument_.

Let $b_1, b_2$ refer to the first data argument and the second data
argument respectively, and let $n_1, n_2$ be their respective lengths in bytes.
Let the result of `builtinLogicalOr`, given $b_1, b_2$ and some padding
semantics argument, be $b_r$, of length $n_r$ in bytes. We use $b_1[i]$ to refer 
to the value at index $i$ of $b_1$ (and analogously for 
$b_2, b_r$); see the [section on the bit indexing scheme](#bit-indexing-scheme)
for the exact specification of this.

If the padding semantics argument is `True`, then we have $n_r = \max \{ n_1,
n_2 \}$; otherwise, $n_r = \min \{ n_1, n_2 \}$. For all $i \in 0, 1, \ldots 8
\cdot n_r - 1$, we have

$$
b_r[i] = \begin{cases}
         b_0[i] & \text{if } n_1 < n_0 \text{ and } i \geq 8 \cdot \min \\{ n_1, n_2 \\} \\
         b_1[i] & \text{if } n_0 < n_1 \text { and } i \geq 8 \cdot \min \\{ n_1, n_2 \\} \\
         0 & \text{if } b_0[i] = b_1[i] = 0 \\
         1 & \text{otherwise} \\
         \end{cases}
$$

Some examples of the intended behaviour of `builtinLogicalOr` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- truncation semantics
builtinLogicalOr False [] [0xFF] => []

builtinLogicalOr False [0xFF] [] => []

builtinLogicalOr False [0xFF] [0x00] => [0xFF]

builtinLogicalOr False [0x00] [0xFF] => [0xFF]

builtinLogicalOr False [0x4F, 0x00] [0xF4] => [0xFF]

-- padding semantics
builtinLogicalOr True [] [0xFF] => [0xFF]

builtinLogicalOr True [0xFF] [] => [0xFF]

builtinLogicalOr False [0xFF] [0x00] => [0xFF]

builtinLogicalOr False [0x00] [0xFF] => [0xFF]

builtinLogicalOr False [0x4F, 0x00] [0xF4] => [0xFF, 0x00]
```

#### `builtinLogicalXor`

`builtinLogicalXor` takes three arguments; we name and describe them below.

1. Whether padding semantics should be used. If this argument is `False`,
   truncation semantics are used instead. This is the _padding semantics
   argument_, and has type `BuiltinBool`.
2. The first input `BuiltinByteString`. This is the _first data argument_.
3. The second input `BuiltinByteString`. This is the _second data argument_.

Let $b_1, b_2$ refer to the first data argument and the second data
argument respectively, and let $n_1, n_2$ be their respective lengths in bytes.
Let the result of `builtinLogicalXor`, given $b_1, b_2$ and some padding
semantics argument, be $b_r$, of length $n_r$ in bytes. We use $b_1[i]$ to 
refer to the value at index $i$ of $b_1$ (and analogously for 
$b_2, b_r$); see the [section on the bit indexing scheme](#bit-indexing-scheme)
for the exact specification of this.

If the padding semantics argument is `True`, then we have $n_r = \max \{ n_1,
n_2 \}$; otherwise, $n_r = \min \{ n_1, n_2 \}$. For all $i \in 0, 1, \ldots 8
\cdot n_r - 1$, we have

$$
b_r[i] = \begin{cases}
         b_0[i] & \text{if } n_1 < n_0 \text{ and } i \geq 8 \cdot \min \\{ n_1, n_2 \\} \\
         b_1[i] & \text{if } n_0 < n_1 \text { and } i \geq 8 \cdot \min \\{ n_1, n_2 \\} \\
         0 & \text{if } b_0[i] = b_1[i] \\
         1 & \text{otherwise} \\
         \end{cases}
$$

Some examples of the intended behaviour of `builtinLogicalXor` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- truncation semantics
builtinLogicalXor False [] [0xFF] => []

builtinLogicalXor False [0xFF] [] => []

builtinLogicalXor False [0xFF] [0x00] => [0xFF]

builtinLogicalXor False [0x00] [0xFF] => [0xFF]

builtinLogicalXor False [0x4F, 0x00] [0xF4] => [0xBB]

-- padding semantics
builtinLogicalOr True [] [0xFF] => [0xFF]

builtinLogicalOr True [0xFF] [] => [0xFF]

builtinLogicalOr False [0xFF] [0x00] => [0xFF]

builtinLogicalOr False [0x00] [0xFF] => [0xFF]

builtinLogicalOr False [0x4F, 0x00] [0xF4] => [0xBB, 0x00]
```

#### `builtinLogicalComplement`

`builtinLogicalComplement` takes a single argument, of type `BuiltinByteString`;
let $b$ refer to that argument, and $n$ its length in bytes. Let $b_r$ be
the result of `builtinLogicalComplement`; its length in bytes is also $n$. We
use $b[i]$ to refer to the value at index $i$ of $b$ (and analogously for $b_r$); 
see the [section on the bit indexing scheme](#bit-indexing-scheme) for the exact
specification of this.

For all $i \in 0, 1, \ldots , 8 \cdot n - 1$, we have

$$
b_r[i] = \begin{cases}
        0 & \text{if } b[i] = 1\\
        1 & \text{otherwise}\\
        \end{cases}
$$

Some examples of the intended behaviour of `builtinLogicalComplement` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
builtinLogicalComplement [] => []

builtinLogicalComplement [0x0F] => [0xF0]

builtinLogicalComplement [0x4F, 0xF4] => [0xB0, 0x0B]
```

#### `builtinReadBit`

`builtinReadBit` takes two arguments; we name and describe them below.

1. The `BuiltinByteString` in which the bit we want to read can be found. This
   is the _data argument_.
2. A bit index into the data argument, of type `BuiltinInteger`. This is the
   _index argument_.

Let $b$ refer to the data argument, of length $n$ in bytes, and let $i$ refer to
the index argument. We use $b[i]$ to refer to the value at index $i$t of $b$; see 
the [section on the bit indexing scheme](#bit-indexing-scheme) for the exact 
specification of this.

If $i < 0$ or $i \geq 8 \cdot n$, then `builtinReadBit`
fails. In this case, the resulting error message must specify _at least_ the
following information:

* That `builtinReadBit` failed due to an out-of-bounds index argument; and
* What `BuiltinInteger` was passed as an index argument.

Otherwise, if $b[i] = 0$, `builtinReadBit` returns `False`, and if $b[i] = 1$,
`builtinReadBit` returns `True`.

Some examples of the intended behaviour of `builtinReadBit` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Indexing an empty BuiltinByteString fails
builtinReadBit [] 0 => error

builtinReadBit [] 345 => error

-- Negative indexes fail
builtinReadBit [] (-1) => error

builtinReadBit [0xFF] (-1) => error

-- Indexing reads 'from the end'
builtinReadBit [0xF4] 0 => False

builtinReadBit [0xF4] 1 => False 

builtinReadBit [0xF4] 2 => True 

builtinReadBit [0xF4] 3 => False

builtinReadBit [0xF4] 4 => True

builtinReadBit [0xF4] 5 => True

builtinReadBit [0xF4] 6 => True

builtinReadBit [0xF4] 7 => True

-- Out-of-bounds indexes fail
builtinReadBit [0xF4] 8 => error

builtinReadBit [0xFF, 0xF4] 16 => error

-- Larger indexes read backwards into the bytes from the end
builtinReadBit [0xF4, 0xFF] 10 => False 
```

#### `builtinSetBits`

`builtinSetBits` takes two arguments: we name and describe them below.

1. The `BuiltinByteString` in which we want to change some bits. This is the
   _data argument_.
2. A list of index-value pairs, indicating which positions in the data argument
   should be changed to which value. This is the _change list argument_. Each
   index has type `BuiltinInteger`, while each value has type `BuiltinBool`.

Let $C = (i_1, v_1), (i_2, v_2), \ldots , (i_k, v_k)$ refer to the change list
argument, and $b$ the data argument of length $n$ in bytes. Let $b_r$ be the
result of `builtinSetBits`, whose length is also $n$. We use $b[i]$ to refer to
the value at index $i$ of $b$ (and analogously, $b_r$); see the [section on the bit
indexing scheme](#bit-indexing-scheme) for the exact specification of this.

If the change list argument is empty, the result is $b$. If the change list
argument is a singleton, let $(i, v)$ refer to its only index-value pair. If $i
< 0$ or i \geq 8 \cdot n$, then `builtinSetBits` fails. In this case, the
resulting error message must specify _at least_ the following information:

* That `builtinSetBits` failed due to an out-of-bounds index argument; and
* What `BuiltinInteger` was passed as the index part of the index-value pair.

Otherwise, for all $j \in 0, 1, \ldots 8 \cdot n - 1$, we have

$$
b_r[j] = \begin{cases}
         0 & \text{if } j = i \text{ and } b = \texttt{False}\\
         1 & \text{if } j = i \text{ and } b = \texttt{True}\\
         b[j] & \text{otherwise}\\
         \end{cases}
$$

if the change list argument is longer than a singleton, suppose that we can
process a change list argument of length $1 \leq m$, and let $b_m$ be the result
of such processing. There are two possible outcomes for $b_m$:

1. An error. In this case, we define the result of `builtinSetBits` on such a
   change list as that error.
2. A `BuiltinByteString`.

From here, when we refer to $b_m$, we refer to the `BuiltinByteString` option.

We observe that any change list $C^{\prime}$ of length $m +
1$ will have the form of some other change list $C_m$, with an additional
element $(i_{m + 1}, v_{m + 1})$ at the end. We define the result of 
`builtinSetBits` with data argument $b$ and change list argument $C^{\prime}$ 
as the result of `builtinSetBits` with data argument $b_m$ and the change list
argument $(i_{m + 1}, v_{m + 1})$; as this change list is a singleton, we can
process it according to the description above.

Some examples of the intended behaviour of `builtinSetBits` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Writing an empty BuiltinByteString fails
builtinSetBits [] [(0, False)] => error

-- Irrespective of index
builtinSetBits [] [(15, False)] => error

-- And value
builtinSetBits [] [(0, True)] => error

-- And multiplicity
builtinSetBits [] [(0, False), (1, False)] => error

-- Negative indexes fail
builtinSetBits [0xFF] [((-1), False)] => error

-- Even when mixed with valid ones
builtinSetBits [0xFF] [(0, False), ((-1), True)] => error

-- In any position
builtinSetBits [0xFF] [((-1), True), (0, False)] => error

-- Out-of-bounds indexes fail
builtinSetBits [0xFF] [(8, False)] => error

-- Even when mixed with valid ones
builtinSetBits [0xFF] [(1, False), (8, False)] => error

-- In any position
builtinSetBits [0xFF] [(8, False), (1, False)] => error

-- Bits are written 'from the end'
builtinSetBits [0xFF] [(0, False)] => [0xFE]

builtinSetBits [0xFF] [(1, False)] => [0xFD]

builtinSetBits [0xFF] [(2, False)] => [0xFB]

builtinSetBits [0xFF] [(3, False)] => [0xF7]

builtinSetBits [0xFF] [(4, False)] => [0xEF]

builtinSetBits [0xFF] [(5, False)] => [0xDF]

builtinSetBits [0xFF] [(6, False)] => [0xBF]

builtinSetBits [0xFF] [(7, False)] => [0x7F]

-- True value sets the bit
builtinSetBits [0x00] [(5, True)] => [0x20]

-- False value clears the bit
builtinSetBits [0xFF] [(5, False)] => [0xDF]

-- Larger indexes write backwards into the bytes from the end
builtinSetBits [0xF4, 0xFF] [(10, True)] => [0xF0, 0xFF]

-- Multiple items in a change list apply cumulatively
builtinSetBits [0xF4, 0xFF] [(10, True), (1, False)] => [0xF0, 0xFD]

builtinSetBits (builtinSetBits [0xF4, 0xFF] [(10, True)]) [(1, False)] => [0xF0, 0xFD]

-- Order within a changelist is unimportant among unique indexes
builtinSetBits [0xF4, 0xFF] [(1, False), (10, True)] => [0xF0, 0xFD]

-- But _is_ important for identical indexes
builtinSetBits [0x00, 0xFF] [(10, True), (10, False)] => [0x00, 0xFF]

builtinSetBits [0x00, 0xFF] [(10, False), (10, True)] => [0x04, 0xFF]

-- Setting an already set bit does nothing
builtinSetBits [0xFF] [(0, True)] => [0xFF]

-- Clearing an already clear bit does nothing
builtinSetBits [0x00] [(0, False)] => [0x00]
```

#### `builtinReplicate`

`builtinReplicate` takes two arguments; we name and describe them below.

1. The desired result length, of type `BuiltinInteger`. This is the _length
   argument_.
2. The byte to place at each position in the result, represented as a
   `BuiltinInteger` (corresponding to the unsigned integer this byte encodes).
   This is the _byte argument_.

Let $n$ be the length argument, and $w$ the byte argument. If $n < 0$, then
`builtinReplicate` fails. In this case, the resulting error message must specify
_at least_ the following information:

* That `builtinReplicate` failed due to a negative length argument; and
* What `BuiltinInteger` was passed as the length argument.

If $n \geq 0$, and $w < 0$ or $w > 255$, then `builtinReplicate` fails. In this
case, the resulting error message must specify _at least_ the following
information:

* That `builtinReplicate` failed due to the byte argument not being a valid
  byte; and
* What `BuiltinInteger` was passed as the byte argument.

Otherwise, let $b$ be the result of `builtinReplicate`, and let $b\\{i\\}$ be the
byte at position $i$ of $b$, as per [the section describing the bit indexing
scheme](#bit-indexing-scheme). We have:

* The length (in bytes) of $b$ is $n$; and
* For all $i \in 0, 1, \ldots, n - 1$, $b\\{i\\} = w$.

Some examples of the intended behaviour of `builtinReplicate` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Replicating a negative number of times fails
builtinReplicate (-1) 0 => error

-- Irrespective of byte argument
builtinReplicate (-1) 3 => error

-- Out-of-bounds byte arguments fail
builtinReplicate 1 (-1) => error

builtinReplicate 1 256 => error

-- Irrespective of length argument
builtinReplicate 4 (-1) => error

builtinReplicate 4 256 => error

-- Length of result matches length argument, and all bytes are the same
builtinReplicate 0 0xFF => []

builtinReplicate 4 0xFF => [0xFF, 0xFF, 0xFF, 0xFF]
```

### Laws

#### Binary operations

We describe laws for all three operations that work over two
`BuiltinByteStrings`, that is, `builtinLogicalAnd`, `builtinLogicalOr` and
`builtinLogicalXor`, together, as many of them are similar (and related). We
describe padding semantics and truncation semantics laws, as they are slightly
different.

All three operations above, under both padding and truncation semantics, are
[commutative semigroups][special-semigroups]. Thus, we have:

```haskell
builtinLogicalAnd s x y = builtinLogicalAnd s y x

builtinLogicalAnd s x (builtinLogicalAnd s y z) = builtinLogicalAnd s
(builtinLogicalAnd s x y) z

-- and the same for builtinLogicalOr and builtinLogicalXor
```

Note that the semantics (designated as `s` above) must be consistent in order
for these laws to hold. Furthermore, under padding semantics, all the above
operations are [commutative monoids][commutative-monoid]:

```haskell
builtinLogicalAnd True x "" = builtinLogicalAnd True "" x = x

-- and the same for builtinLogicalOr and builtinLogicalXor
```

Under truncation semantics, `""` (that is, the empty `BuiltinByteString`) acts
instead as an [absorbing element][absorbing-element]:

```haskell
builtinLogicalAnd False x "" = builtinLogicalAnd False "" x = ""

-- and the same for builtinLogicalOr and builtinLogicalXor
```

`builtinLogicalAnd` and `builtinLogicalOr` are also [semilattices][semilattice],
due to their idempotence:

```haskell
builtinLogicalAnd s x x = x

-- and the same for builtinLogicalOr
```

`builtinLogicalXor` is instead involute:

```haskell
builtinLogicalXor s x (builtinLogicalXor s x x) = builtinLogicalXor s
(builtinLogicalXor s x x) x = x
```

Additionally, under padding semantics, `builtinLogicalAnd` and
`builtinLogicalOr` are [self-distributive][distributive]:

```haskell
builtinLogicalAnd True x (builtinLogicalAnd True y z) = builtinLogicalAnd True
(builtinLogicalAnd True x y) (builtinLogicalAnd True x z)

builtinLogicalAnd True (builtinLogicalAnd True x y) z = builtinLogicalAnd True
(builtinLogicalAnd True x z) (builtinLogicalAnd True y z)

-- and the same for builtinLogicalOr
```

Under truncation semantics, `builtinLogicalAnd` is only left-distributive over
itself, `builtinLogicalOr` and `builtinLogicalXor`:

```haskell
builtinLogicalAnd False x (builtinLogicalAnd False y z) = builtinLogicalAnd
False (builtinLogicalAnd False x y) (builtinLogicalAnd False x z)

builtinLogicalAnd False x (builtinLogicalOr False y z) = builtinLogicalOr False
(builtinLogicalAnd False x y) (builtinLogicalAnd False x z)

builtinLogicalAnd False x (builtinLogicalXor False y z) = builtinLogicalXor
False (builtinLogicalAnd False x y) (builtinLogicalAnd False x z)
```

`builtinLogicalOr` under truncation semantics is left-distributive over itself
and `bitwiseLogicalAnd`:

```haskell
builtinLogicalOr False x (builtinLogicalOr False y z) = builtinLogicalOr False
(builtinLogicalOr False x y) (builtinLogicalOr False x z)

builtinLogicalOr False x (builtinLogicalAnd False y z) = builtinLogicalAnd False
(builtinLogicalOr False x y) (builtinLogicalOr False x z)
```

If the first and second data arguments to these operations have the same length,
these operations satisfy several additional laws. We describe these briefly
below, with the added note that, in this case, padding and truncation semantics
coincide:

* `builtinLogicalAnd` and `builtinLogicalOr` form a [bounded lattice][lattice]
* `builtinLogicalAnd` is [distributive][distributive] over itself, `builtinLogicalOr` and
  `builtinLogicalXor`
* `builtinLogicalOr` is [distributive][distributive] over itself and `builtinLogicalAnd`

We do not specify these laws here, as they do not hold in general. At the same
time, we expect that any implementation of these operations will be subject to
these laws.

#### `builtinLogicalComplement`

The main law of `builtinLogicalComplement` is involution:

```haskell
builtinLogicalComplement (builtinLogicalComplement x) = x
```

In combination with `builtinLogicalAnd` and `builtinLogicalOr`,
`builtinLogicalComplement` gives rise to the famous [De Morgan laws][de-morgan], irrespective of semantics:

```haskell
builtinLogicalComplement (builtinLogicalAnd s x y) = builtinLogicalOr s
(builtinLogicalComplement x) (builtinLogicalComplement y)

builtinLogicalComplement (builtinLogicalOr s x y) = builtinLogicalAnd s
(builtinLogicalComplement x) (builtinLogicalComplement y)
```

For `builtinLogicalXor`, we instead have (again, irrespective of semantics):

```haskell
builtinLogicalXor s x (builtinLogicalComplement x) = x
```

#### Bit reading and modification

Throughout, we assume any index arguments to be 'in-bounds'; that is, all the
index arguments used in the statements of any law are such that the operation
they are applied to wouldn't produce an error.

The first law of `builtinSetBits` is similar to the [set-twice law of
lenses][lens-laws]:

```haskell
builtinSetBits bs [(i, b1), (i, b2)] = builtinSetBits bs [(i, b2)]
```

Together with `builtinReadBit`, we obtain the remaining two analogues to the lens
laws:

```haskell
-- writing to an index, then reading from that index, gets you what you wrote
builtinReadBit (builtinSetBits bs [(i, b)]) i = b

-- if you read from an index, then write that value to that same index, nothing
-- happens
builtinSetBits bs [(i, builtinReadBit bs i)] = bs
```

Furthermore, given a fixed data argument, `builtinSetBits` acts as a [monoid
homomorphism][monoid-homomorphism] from functions to lists under concatenation:

```haskell
-- identity function corresponds to empty list
builtinSetBits bs [] = bs

-- composition is concatenation of change list arguments
builtinSetBits (builtinSetBits bs is) js = builtinSetBits bs (is <> js)
```

#### `builtinReplicate`

Given a fixed byte argument, `builtinReplicate` acts as a [monoid
homomorphism][monoid-homomorphism] from natural numbers under addition to
`BuiltinByteString`s under concatenation: 

```haskell
builtinReplicate 0 w = ""

builtinReplicate (n + m) w = builtinReplicate n w <> builtinReplicate m w
```

Additionally, for any 'in-bounds' index (that is, any index for which
`builtinIndexByteString` won't error) `i`, we have

```haskell
builtinIndexByteString (builtinReplicate n w) i = w
```

Lastly, we have

```haskell
builtinSizeOfByteString (builtinReplicate n w) = n
```

## Rationale: how does this CIP achieve its goals?

The operations, and semantics, described in this CIP provide a set of
well-defined bitwise logical operations, as well as bitwise access and
modification, to allow cases similar to Case 1 to be performed efficiently and
conveniently. Furthermore, the semantics we describe would be reasonably
familiar to users of other programming languages (including Haskell) which have
provisions for bitwise logical operations of this kind, as well as some way of
extending these operations to operate on packed byte vectors. At the same time,
there are several choices we have made that are somewhat unusual, or could
potentially have been implemented differently based on existing work: most
notably, our choice of bit indexing scheme, the padding-versus-truncation
semantics, and the multiplicitous definition of bit modification. Among existing
work, a particularly important example is [CIP-58][cip-58], which makes
provisions for operations similar to the ones described here, and from which we
differ in several important ways. We clarify the reasoning behind our choices,
and how they differ from existing work, below.

Aside from the issues we list below, we don't consider other operations
controversial. Indeed, `bitwiseLogicalComplement` has a direct parallel to the
implementation in [CIP-58][cip-58], and `builtinReplicate` is a direct wrapper
around the `replicate` function in `ByteString`. Thus, we do not discuss them
further here.

### Bit indexing scheme

The bit indexing scheme we describe here is designed around two
considerations. Firstly, we want operations on these bits, as well as those
results, to be as consistent and as predictable as possible: any individual
familiar with such operations on variable-length bitvectors from another
language shouldn't be surprised by the semantics. Secondly, we want to
anticipate future bitwise operation extensions, such as shifts and rotations,
and have the indexing scheme support efficient implementations (and predictable
semantics) for these. 

While prior art for bit access (and modification) exists
in almost any programming language, these are typically over types of fixed
width (usually bytes, machine words, or something similar); for variable-width
types, these typically are either not implemented at all, or if they are
implemented, this is done in an external library, with varying support for
certain operations. An example of the first is Haskell's `ByteString`, which has
no way to even access, much less modify, individual bits; an example of the
second is the [CRoaring][croaring] library for C, which supports all the
operations we describe in this CIP, along with multiple others. In the second
case, the _exact_ arrangement of bits inside the representation is not something
users are exposed to directly: instead, the bitvector type is opaque, and the
library only guarantees consistency of API. In our case, this is not a viable
choice, as we require bit access _and_ byte access to both work on
`BuiltinByteString`, and thus, some consistency of representation is required.

The scheme for indexing bits within a byte that we describe in [the relevant
section](#bit-indexing-scheme) is the same as the one used by the `Data.Bits`
API in Haskell for `Word8` bit indexing, and mirrors the decisions of most
languages that provide such an API at all, as well as the conventional
definition of such operations as `(w >> i) & 1` for access, `w | (1 << i)` for
setting, and `w & ~(1 << i)` for clearing. We could choose to 'flip' this
indexing, by using a similar operation for 'index flipping' as we currently use
for bytes: essentially, instead of 

$$
\left \lfloor \frac{w}{2^{i}} \right \rfloor \mod 2 \equiv 1
$$

we would instead use

$$
\left \lfloor \frac{w}{2^{8 - i - 1}} \right \rfloor \mod 2 \equiv 1
$$

to designate bit $i$ as set (and analogously for clear). Together with the
ability to choose _not_ to flip the _byte_ index, we get four possibilities,
which have [been described previously][too-many-ways-1]. For clarity, we name,
and describe, them below. Throughout, we use `n` as the length of a given
`BuiltinByteString` in bytes.

The first possibility is that we 'flip' neither bit, nor byte, indexes. We call
this the _no-flip variant_:

```
| Byte index | 0                             | 1                 | ... | n - 1                          |
|------------|-------------------------------|-------------------| ... |--------------------------------|
| Byte       | w0                            | w1                | ... | w(n - 1)                       |
|------------|-------------------------------|-------------------| ... |--------------------------------|
| Bit index  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | 15 | 14 | ... | 8 | ... | 8n - 1 | 8n - 2 | ... | 8n - 8 |
```

The second possibility is that we 'flip' _both_ bit and byte indexes. We call
this the _both-flip variant_:

```
| Byte index | 0                              | ... | n - 2            | n - 1                         |
|------------|--------------------------------| ... |------------------|-------------------------------|
| Byte       | w0                             | ... | w (n - 2)        | w(n - 1)                      |
|------------|--------------------------------| ... |------------------|-------------------------------|
| Bit index  | 8n - 8 | 8n - 7 | ... | 8n - 1 | ... | 8 | 9 | ... | 15 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 
```

The third possibility is that we 'flip' _bit_ indexes, but not _byte_ indexes.
We call this the _bit-flip variant_:

```
| Byte index | 0                             | 1            | ... | n - 1                          |
|------------|-------------------------------|--------------| ... |--------------------------------|
| Byte       | w0                            | w1           | ... | w(n - 1)                       |
|------------|-------------------------------|--------------| ... |--------------------------------|
| Bit index  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | ... | 15 | ... | 8n - 8 | 8n - 7 | ... | 8n - 1 |
```

The fourth possibility is the one we describe in the [bit indexing scheme
section](#bit-indexing-scheme), which is also the scheme chosen by CIP-58. We
repeat it below for clarity:

```
| Byte index | 0                              | 1  | ... | n - 1                         |
|------------|--------------------------------|----| ... |-------------------------------|
| Byte       | w0                             | w1 | ... | w(n - 1)                      |
|------------|--------------------------------|----| ... |-------------------------------|
| Bit index  | 8n - 1 | 8n - 2 | ... | 8n - 8 |   ...    | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
```

On the face of it, these schemes appear equivalent: they are all consistent, and
all have formal descriptions, and quite similar ones at that. However, we
believe that only the one we chose is the correct one. To explain this, we
introduce two notions that we consider to be both intuitive and important,
then specify why our choice of indexing scheme fits those notions better than
any other.

The first notion is _index locality_. Intuitively, this states that if
two indexes are 'close' (in that their absolute difference is small), the values
at those indexes should be 'close' (in that their positioning in memory should
be separated less). We believe this notion to be reasonable, as this is an
expectation from array indexing (and indeed, `BuiltinByteString` indexing), as
well as the reason why packed array data is efficient on modern memory
hierarchies. Extending this notion to bits, we can observe that the both-flip
and no-flip variants of the bit indexing scheme do not preserve index locality:
the separation between a bit at index $0$ and index $1$ is _significantly_
different to the separation between a bit at index $7$ and index $8$ in both
representations, despite their absolute difference being identical. Thus, we
believe that these two variants are not viable, as they are not only confusing
from the point of view of behaviour, they would also make implementation of
future operations (such as shifts or rotations) significantly harder to both do,
and also reason about. Thus, only the bit-flip variant, as well as our choice,
remain contenders.

The second notion is _conversion agreement_. To describe this notion, we first
observe that, according to the definition of the bit indexing scheme given [in
the corresponding section](#bit-indexing-scheme), as well as the corresponding
definition for the bit-flip variant, we view a `BuiltinByteString` of length $n$
as a binary natural number with exactly $8n$ digits, and the value at index $i$
corresponds to the digits whose place value is either $2^i$ (for the bit-flip
variant), or $2^{8n - i - 1}$ (for our chosen method). Put another way, under
the specification for the bit-flip variant, the least significant binary digit
is first, whereas in our chosen specification, the least significant binary
digit is last. 

When viewed this way, we can immediately see a potential problem, as by indexing
a `BuiltinByteString`, we get back a `BuiltinInteger`, which has a numerical
value as a natural number in the range $[0, 255]$. It would thus be sensible
that, given a `BuiltinByteString` that is non-empty, if we were to get the
values at bit indexes $0$ through $7$, and treat them as their corresponding
place value in a summation, we should obtain the same answer as indexing
whichever byte those bits come from. We call this notion _conversion agreement_,
due to its relation to [an existing CIP][conversion-cip], which allows us to
(essentially) view a `BuiltinByteString` as a natural number in base-256.
Indeed, the case is analogous, with the only difference being that we are
concerned with the positioning of base-256 digits, not binary ones.

Consider the `BuiltinByteString` whose only byte is $42$, whose representation 
is as follows:

```
| Byte index | 0        |
|------------|----------|
| Byte       | 00101010 |
```

Under the bit-flip variant, our bit indexes would be as follows:

```
| Byte index | 0                             |
|------------|-------------------------------|
| Byte       | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
|------------|-------------------------------|
| Bit index  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
```

However, this immediately causes a problem: under this indexing scheme, we imply
that the $2^2 = 4$ place value is $1$ in $42$'s binary representation, but
this is not the case. This fails conversion agreement. However, our choice 
produces the correct answer:

```
| Byte index | 0                             |
|------------|-------------------------------|
| Byte       | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
|------------|-------------------------------|
| Bit index  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
```

Here, the $4$ place value is correctly $0$. Indeed, our choice simply 'extends'
the bit ordering (in the place value sense) employed by all machine
architectures for bytes in their sense as natural numbers within a fixed range.
This was also the choice made by [CIP-58][cip-58], for similar reasons.

We also note that conversion agreement matters for Case 2, in the wider context
of the interaction between [conversion primitives][conversion-cip] and logical
XOR. The Argon2 family of hashes use certain inputs (which happen to be numbers)
both as numbers and also as blocks of binary, which means that any inconsistency
would cause strange (and possibly quite surprising) results when implementing
any of those functions. This once again suggests that our choice is the right
one, as it is the only one that would ensure conversion agreement.

While the bit-flip variant has the advantage of 'agreement' between byte and bit
indexes, we believe that conversion agreement is the more important property to
have. Given that the [conversion primitives CIP][conversion-cip] has already
been implemented into Plutus Core, we think that our choice is the only viable
one in light of both this fact, and the Cases we have stated here.

### Padding versus truncation

For the operations defined in this CIP taking two `BuiltinByteString` arguments
(that is, `builtinLogicalAnd`, `builtinLogicalOr`, and `builtinLogicalXor`),
when the two arguments have identical lengths, the semantics are natural,
mirroring the corresponding operations on the 
[Boolean algebra $\mathbb{2}^{8n}$][boolean-algebra-2], where $n$ is the length 
of either argument in bytes. When the arguments do _not_ have matching lengths,
however, the situation becomes more complex, as there are several ways in which
we could define these operations. The most natural possibilities are as follows;
we repeat some of the definitions used [in the corresponding
section](#padding-versus-truncation-semantics).

* Extend the shorter argument with the identity element (1 for
  `builtinLogicalAnd`, 0 otherwise) to match the length of the longer argument,
  then perform the operation as if on matching-length arguments. We call this
  _padding semantics_.
* Ignore the bytes of the longer argument whose indexes would not be valid for
  the shorter argument, then perform the operation as if on matching-length
  arguments. We call this _truncation semantics_.
* Fail with an error whenever argument lengths don't match. We call this
  _match semantics_.

It is not a priori clear which of these we should choose: they are subject to
different laws (as evidenced by the [corresponding
section](#laws-and-examples)), none of which are strict supersets of each other
(at least not for _all_ inputs possible). While [CIP-58][cip-58] chose match
semantics, we believe this was not the correct decision: we use Case 1 to
justify the benefit of having other semantics described above available.

Consider the following operation: given a bound $k$ and an integer set, remove
all elements smaller than $k$ from the set. This can be done using
`bitwiseLogicalAnd` and a mask where the first $k - 1$ bits are clear. However,
under match semantics, the mask would have to have a length equal to the integer
set representation; under padding semantics, the mask would only need to have a
length proportional to $k$. This is noteworthy, as padding the mask would
require an additional copy operation, only to produce a value that would be
discarded immediately.

Consider instead the following operation: given two integer sets with different
(upper) bounds, take their intersection, producing an integer set whose size is
the minimum of the two. This can once again be done using `bitwiseLogicalAnd`,
but under match semantics (or padding semantics for that matter), we would first
have to slice the longer argument, while under truncation semantics, we wouldn't
need to.

Match semantics can be useful for Case 1 as well. Consider the case that a 
representation of an integer set is supplied as an
input datum (in its `Data` encoding). In order to deserialize it, we need to
verify at least whether it has the right length in bytes to represent an integer
set with a given bound. Under padding or truncation semantics, we would have to
check this at deserialization time; under exact match semantics, provided we
were sure that at least one argument is of a known size, we could simply perform
the necessary operations and let the match semantics error if given something
inappropriate.

It is also worth noting that truncation semantics are well-established in the
Haskell ecosystem. Viewed another way, all of the operations under discussion in
this sections are specialized versions of the `zipWith` operation; Haskell
libraries provide this type of operation for a range of linear collections,
including lists, `Vector`s, and mostly notably, `ByteString`s. In all of these
cases, truncation semantics are what is implemented; it would be surprising to
developers coming from Haskell to find that they have to do additional work to
replicate them in Plutus. While we don't anticipate direct use of Plutus Core
primitives by developers (although this is not an unheard-of case), we should
enable library authors to build familiar APIs _on top of_ Plutus Core
primitives, which suggests truncation semantics should be available, at least as
an option.

All the above suggests that no _single_ choice of semantics will satisfy all
reasonable needs, if only from the point of view of efficiency. This suggests,
much as for [conversion primitives][conversion-cip] and endianness issues, that
the primitive should allow a choice in what semantics get used for any given
call. Ideally, we would allow a choice of any of the three options described
above; however, this is awkward to do in Plutus Core. While the choice between
_two_ options is straightforward (pass a `BuiltinBool`), the choice between
_three_ options would either require multiple `BuiltinBool` arguments, or a
`BuiltinInteger` argument with 'designated values' (such as 'negative means
truncation, zero means match, positive means padding'). Neither of these are
ideal choices, as they involve either argument redundancy or additional checks
(and erroring when they don't match). In light of this, we elected to choose
only two of the three semantics and have this choice for any given call be
controlled by a `BuiltinBool` flag.

This naturally leads to the question of which of the three semantics above we
can afford not to have. We believe that match semantics are the right ones to
exclude. Firstly, technically we can still have match semantics by using either
padding or truncation semantics plus a length check beforehand: this is a cheap
operation, unlike simulating padding semantics for example, which would have
non-trivial cost. Secondly, due to the preponderance of truncation semantics in
Haskell, we feel excluding it as an option is wrong. Lastly, we believe that
outside of error checking, exact match semantics give few benefits over padding
or truncation semantics, for performance and otherwise. This combination of
reasoning leads us to naturally consider padding and truncation as the two to
keep, and this guided our implementation choices.

### Bit setting

`builtinSetBits` in our description takes a change list argument, allowing
changing multiple bits at once. This is an added complexity, and an argument can
be made that something similar to the following operation would be sufficient:

```haskell
builtinSetBit :: BuiltinByteString -> BuiltinInteger -> BuiltinBool ->
BuiltinByteString
```

Essentially, `builtinSetBit bs i v` would be equivalent to `builtinSetBits bs
[(i, v)]` as currently defined. This was the choice made by [CIP-58][cip-58],
with the consideration of simplicity in mind. 

At the same time, due to the immutability semantics of Plutus Core, each time
`builtinSetBit` is called, a copy of its `BuiltinByteString` argument would have
to be made. Thus, a sequence of $k$ `builtinSetBit` calls in a fold over a
`BuiltinByteString` of length $n$ would require $\Theta(nk)$ time and
$\Theta(nk)$ space. Meanwhile, if we instead used `builtinSetBits`, the time
drops to $\Theta(n + k)$ and the space to $\Theta(n)$, which is a non-trivial
improvement. While we cannot avoid the worst-case copying behaviour of
`builtinSetBit` (if we have a critical path of read-write dependencies of length
$k$, for example), and 'list packing' carries some cost, we have
[benchmarks][benchmarks-bits] that show not only that this 'packing cost' is
essentially zero, but that for `BuiltinByteString`s of 30 bytes or fewer,
copying completely overwhelms the work required to set the bits in the first
place. This alone is a strong argument for having `builtinSetBits` instead;
indeed, there is prior art for doing this [in the `vector` library][vector], for
the exact reasons we give here.

The argument could also be made whether this design should be extended to other
primitive operations in this CIP which both take `BuiltinByteString` arguments
and also produce `BuiltinByteString` results. We believe that this is not as
justified as in the `builtinSetBits` case, for several reasons. Firstly, for
`builtinLogicalComplement`, it's not even clear what benefit this would have at
all: the only possible signature such an operation would have is
`[BuiltinByteString] -> [BuiltinByteString]`, which in effect would be a
specialized form of mapping. Even the _general_ form of mapping is not
considered suitable as a primitive operation in Plutus Core! 

Secondly, the
benefits to performance wouldn't be nearly as significant in theory, and likely
in practice. Consider this hypothetical operation (with fold semantics):

```haskell
builtinLogicalXors :: BuiltinBool -> [BuiltinByteString] -> BuiltinByteString
```

Simulating this operation as a fold using `builtinLogicalXor`, in the worst
case, irrespective of padding or truncation semantics, requires $\Theta(nk)$
time and space, where $n$ is the size of each `BuiltinByteString` in the
argument list, and $k$ is the length of the argument list itself. Using
`builtinLogicalXors` would reduce the space required to $\Theta(n)$, but not
affect the time complexity at all. 

Lastly, it is questionable whether 'bulk' operations like `builtinLogicalXors`
above would see as much use as `builtinSetBits`. In the context of Case 1,
`builtinLogicalXors` corresponds to taking the symmetric difference of multiple
integer sets; it seems unlikely that the number of sets we'd want to do this
with would be higher than 2 often. However, in the same context,
`builtinSetBits` corresponds to constructing an integer set given a list of
members (or, for that matter, _non_-members): this is an operation that is both
required by the case description, and also unarguably useful often.

On the basis of the above, we believe that choosing to implement
`builtinSetBits` as a 'bulk' operation, but to leave others as 'singular' is the
right choice.

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
  usable to build Plutus (8.10, 9.2 and 9.6 at the time of writing), across all 
  [Tier 1][tier-1-ghc] platforms.

Ideally, the implementation should also demonstrate its performance 
characteristics by well-designed benchmarks.

### Implementation Plan

MLabs has begun the [implementation of the proof-of-concept][mlabs-impl] as 
required in the acceptance criteria. Upon completion, we will send a pull 
request to Plutus with the implementation of the primitives for Plutus 
Core, mirroring the proof-of-concept.

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[mlabs-impl]: https://github.com/mlabs-haskell/plutus-integer-bytestring
[tier-1-ghc]: https://gitlab.haskell.org/ghc/ghc/-/wikis/platforms#tier-1-platforms
[special-semigroups]: https://en.wikipedia.org/wiki/Special_classes_of_semigroups
[commutative-monoid]: https://en.wikipedia.org/wiki/Monoid#Commutative_monoid
[absorbing-element]: https://en.wikipedia.org/wiki/Zero_element#Absorbing_elements
[semilattice]: https://en.wikipedia.org/wiki/Semilattice
[distributive]: https://en.wikipedia.org/wiki/Distributive_property
[lattice]: https://en.wikipedia.org/wiki/Lattice_(order)
[de-morgan]: https://en.wikipedia.org/wiki/De_Morgan%27s_laws
[lens-laws]: https://oleg.fi/gists/posts/2017-04-18-glassery.html#laws:lens
[monoid-homomorphism]: https://en.wikipedia.org/wiki/Monoid#Monoid_homomorphisms
[succinct-data-structures]: https://en.wikipedia.org/wiki/Succinct_data_structure
[adjacency-matrix]: https://en.wikipedia.org/wiki/Adjacency_matrix
[binary-matrix]: https://en.wikipedia.org/wiki/Logical_matrix
[go-binary-matrix]: https://senseis.xmp.net/?BinMatrix
[finite-state-machine-4vl]: https://en.wikipedia.org/wiki/Four-valued_logic#Matrix_machine
[bitvector-apps]: https://en.wikipedia.org/wiki/Bit_array#Applications
[bitmap-index-compression]: https://en.wikipedia.org/wiki/Bitmap_index#Compression
[cip-58]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0058
[croaring]: https://github.com/RoaringBitmap/CRoaring
[too-many-ways-1]: https://fgiesen.wordpress.com/2018/02/19/reading-bits-in-far-too-many-ways-part-1
[conversion-cip]: https://github.com/mlabs-haskell/CIPs/tree/koz/to-from-bytestring/CIP-XXXX
[benchmarks-bits]: https://github.com/mlabs-haskell/plutus-integer-bytestring/blob/koz/logical/bench/naive/Main.hs#L74-L83
[vector]: https://hackage.haskell.org/package/vector-0.13.1.0/docs/Data-Vector.html#v:-47--47-
[boolean-algebra-2]: https://en.wikipedia.org/wiki/Two-element_Boolean_algebra
[hashing]: https://en.wikipedia.org/wiki/Hash_function
[sha256]: https://en.wikipedia.org/wiki/Secure_Hash_Algorithms
[blake2b]: https://en.wikipedia.org/wiki/BLAKE_(hash_function)
[argon2]: https://en.wikipedia.org/wiki/Argon2
[xor-crypto]: https://en.wikipedia.org/wiki/Exclusive_or#Bitwise_operation
