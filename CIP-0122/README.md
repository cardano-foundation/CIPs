---
CIP: 122
Title: Logical operations over BuiltinByteString
Category: Plutus
Status: Active
Authors: 
    - Koz Ross <koz@mlabs.city>
Implementors: 
    - Koz Ross <koz@mlabs.city>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/806
Created: 2024-05-03
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
[SHA256][sha256] and [BLAKE2b][blake2b]. At the same time, hash functions
choices are often determined by protocol or use case, and providing individual
primitives for every possible hash function is not a scalable choice. It is much
preferrable to give necessary tools to implement such functionality to users of
Plutus (Core), allowing them to use whichever hash function(s) their
applications require.

As an example, we consider the [Argon2][argon2] family of hash functions. In
order to implement any variant of this family requires the following operations:

1. Conversion of numbers to bytes
2. Bytestring concatenation
3. BLAKE2b hashing
4. Floor division
5. Indexing bytes in a bytestring
6. Logical XOR

Operations 1 to 5 are already provided by Plutus Core (with 1 being included [in
CIP-121][conversion-cip]); however, without logical XOR, no function in the
Argon2 family could be implemented. While in theory, it could be simulated with
what operations already exist, much as with Case 1, this would be impractical at
best, and outright impossible at worst, due to the severe limits imposed
on-chain. This is particularly the case here, as all Argon2 variants call
logical XOR in a loop, whose step count is defined by _multiple_ user-specified
(or protocol-specified) parameters.

We observe that this requirement for logical XOR is not unique to the Argon2
family of hash functions. Indeed, logical XOR is widely used for [a variety of
cryptographic applications][xor-crypto], as it is a low-cost mixing
function that happens to be self-inverting, as well as preserving randomness
(that is, a random bit XORed with a non-random bit will give a random bit).  

## Specification

We describe the proposed operations in several stages. First, we specify a
scheme for indexing individual bits (rather than whole bytes) in a
`BuiltinByteString`. We then specify the semantics of each operation, as well as
giving costing expectations and some examples. Lastly, we provide some laws that 
any implementation of these operations is expected to obey.

### Bit indexing scheme

We begin by observing that a `BuiltinByteString` is a packed array of bytes
(that is, `BuiltinInteger`s in the range $[0, 255]$) according to the API
provided by existing Plutus Core primitives. In particular, we have the ability
to access individual bytes by index as a primitive operation. Thus, we can view
a `BuiltinByteString` as an indexed collection of bytes; for any
`BuiltinByteString` $b$ of length $n$, and any $i \in 0, 1, \ldots, n - 1$, we
define $b\\{i\\}$ as the byte at index $i$ in $b$, as defined by the
`indexByteString` primitive. In essence, for any `BuiltinByteString` of
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
$\left\lfloor\frac{42}{2^3}\right\rfloor\mod 2 \equiv 1$. Thus, $b[19] = 1$. 

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

* `bitwiseLogicalAnd :: BuiltinBool -> BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString`
* `bitwiseLogicalOr :: BuiltinBool -> BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString`
* `bitwiseLogicalXor :: BuiltinBool -> BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString`
* `bitwiseLogicalComplement :: BuiltinByteString -> BuiltinByteString`
* `readBit :: BuiltinByteString -> BuiltinInteger -> BuiltinBool`
* `writeBits :: BuiltinByteString -> [(BuiltinInteger, BuiltinBool)] ->
  BuiltinByteString`
* `replicateByteString :: BuiltinInteger -> BuiltinInteger -> BuiltinByteString`

We assume the following costing, for both memory and execution time:

| Operation | Cost |
|-----------|------|
| `bitwiseLogicalAnd` | Linear in longest `BuiltinByteString` argument |
| `bitwiseLogicalOr` | Linear in longest `BuiltinByteString` argument |
| `bitwiseLogicalXor` | Linear in longest `BuiltinByteString` argument |
| `bitwiseLogicalComplement` | Linear in `BuiltinByteString` argument |
| `readBit` | Constant |
| `writeBits` | Additively linear in both arguments |
| `replicateByteString` | Linear in the _value_ of the first argument |

#### Padding versus truncation semantics

For the binary logical operations (that is, `bitwiseLogicalAnd`,
`bitwiseLogicalOr` and `bitwiseLogicalXor`), the we have two choices of
semantics when handling `BuiltinByteString` arguments of different lengths. We
can either produce a result whose length is the _minimum_ of the two arguments
(which we call _truncation semantics_), or produce a result whose length is the
_maximum_ of the two arguments (which we call _padding semantics_). As these can
both be useful depending on context, we allow both, controlled by a
`BuiltinBool` flag, on all the operations listed above. 

In cases where we have arguments of different lengths, in order to produce a
result of the appropriate lengths, one of the arguments needs to be either
padded or truncated. Let `short` and `long` refer to the `BuiltinByteString`
argument of shorter length, and of longer length, respectively. The following
table describes what happens to the arguments before the operation:

| Semantics | `short` | `long` |
|-----------|---------|--------|
| Padding   | Pad at high _byte_ indexes | Unchanged |
| Truncation | Unchanged | Truncate high _byte_ indexes |

We pad with different bytes depending on operation: for `bitwiseLogicalAnd`, we
pad with `0xFF`, while for `bitwiseLogicalOr` and `bitwiseLogicalXor` we pad
with `0x00` instead. We refer to arguments so changed as 
_semantics-modified_ arguments.

For example, consider the `BuiltinByteString`s `x = [0x00, 0xF0, 0xFF]` and `y =
[0xFF, 0xF0]`. The following table describes what the semantics-modified
versions of these arguments would become for each operation and each semantics:

| Operation | Semantics | `x` | `y` |
|-----------|-----------|-----|-----|
| `bitwiseLogicalAnd` | Padding | `[0x00, 0xF0, 0xFF]` | `[0xFF, 0xF0, 0xFF]` |
| `bitwiseLogicalAnd` | Truncation | `[0x00, 0xF0]` | `[0xFF, 0xF0]` |
| `bitwiseLogicalOr` | Padding | `[0x00, 0xF0, 0xFF]` | `[0xFF, 0xF0, 0x00]` |
| `bitwiseLogicalor` | Truncation | `[0x00, 0xF0]` | `[0xFF, 0xF0]` |
| `bitwiseLogicalXor` | Padding | `[0x00, 0xF0, 0xFF]` | `[0xFF, 0xF0, 0x00]` |
| `bitwiseLogicalXor` | Truncation | `[0x00, 0xF0]` | `[0xFF, 0xF0]` |

Based on the above, we observe that under padding semantics, the result of any
of the listed operations would have a byte length of 3, while under truncation
semantics, the result would have a byte length of 2 instead.

#### `bitwiseLogicalAnd`

`bitwiseLogicalAnd` takes three arguments; we name and describe them below.

1. Whether padding semantics should be used. If this argument is `False`,
   truncation semantics are used instead. This is the _padding semantics
   argument_, and has type `BuiltinBool`.
2. The first input `BuiltinByteString`. This is the _first data argument_.
3. The second input `BuiltinByteString`. This is the _second data argument_.

Let $b_1, b_2$ refer to the semantics-modified first data argument and
semantics-modified second data argument respectively, and let $n$ be either of 
their lengths in bytes; see the 
[section on padding versus truncation semantics](#padding-versus-truncation-semantics) 
for the exact specification of this. Let the result of `bitwiseLogicalAnd`, given 
$b_1, b_2$ and some padding semantics argument, be $b_r$, also of length $n$ 
in bytes. We use $b_1\\{i\\}$ to refer to the byte at index $i$ in $b_1$ (and
analogously for $b_2$, $b_r$); see the [section on the bit indexing
scheme](#bit-indexing-scheme) for the exact specification of this.

For all $i \in 0, 1, \ldots, n - 1$, we have 
$b_r\\{i\\} = b_0\\{i\\} \text{ }\\& \text{ } b_1\\{i\\}$, where $\\&$ refers to a 
[bitwise AND][bitwise-and].

Some examples of the intended behaviour of `bitwiseLogicalAnd` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- truncation semantics
bitwiseLogicalAnd False [] [0xFF] => []

bitwiseLogicalAnd False [0xFF] [] => []

bitwiseLogicalAnd False [0xFF] [0x00] => [0x00]

bitwiseLogicalAnd False [0x00] [0xFF] => [0x00]

bitwiseLogicalAnd False [0x4F, 0x00] [0xF4] => [0x44]

-- padding semantics
bitwiseLogicalAnd True [] [0xFF] => [0xFF]

bitwiseLogicalAnd True [0xFF] [] => [0xFF]

bitwiseLogicalAnd True [0xFF] [0x00] => [0x00]

bitwiseLogicalAnd True [0x00] [0xFF] => [0x00]

bitwiseLogicalAnd True [0x4F, 0x00] [0xF4] => [0x44, 0x00]
```

#### `bitwiseLogicalOr`

`bitwiseLogicalOr` takes three arguments; we name and describe them below.

1. Whether padding semantics should be used. If this argument is `False`,
   truncation semantics are used instead. This is the _padding semantics
   argument_, and has type `BuiltinBool`.
2. The first input `BuiltinByteString`. This is the _first data argument_.
3. The second input `BuiltinByteString`. This is the _second data argument_.

Let $b_1, b_2$ refer to the semantics-modified first data argument and
semantics-modified second data argument respectively, and let $n$ be either of 
their lengths in bytes; see the 
[section on padding versus truncation semantics](#padding-versus-truncation-semantics) 
for the exact specification of this. Let the result of `bitwiseLogicalOr`, given 
$b_1, b_2$ and some padding semantics argument, be $b_r$, also of length $n$ 
in bytes. We use $b_1\\{i\\}$ to refer to the byte at index $i$ in $b_1$ (and
analogously for $b_2$, $b_r$); see the [section on the bit indexing
scheme](#bit-indexing-scheme) for the exact specification of this.

For all $i \in 0, 1, \ldots, n - 1$, we have 
$b_r\\{i\\} = b_0\\{i\\} \text{ } \| \text{ } b_1\\{i\\}$, where $\|$ refers to 
a [bitwise OR][bitwise-or].

```
-- truncation semantics
bitwiseLogicalOr False [] [0xFF] => []

bitwiseLogicalOr False [0xFF] [] => []

bitwiseLogicalOr False [0xFF] [0x00] => [0xFF]

bitwiseLogicalOr False [0x00] [0xFF] => [0xFF]

bitwiseLogicalOr False [0x4F, 0x00] [0xF4] => [0xFF]

-- padding semantics
bitwiseLogicalOr True [] [0xFF] => [0xFF]

bitwiseLogicalOr True [0xFF] [] => [0xFF]

bitwiseLogicalOr True [0xFF] [0x00] => [0xFF]

bitwiseLogicalOr True [0x00] [0xFF] => [0xFF]

bitwiseLogicalOr True [0x4F, 0x00] [0xF4] => [0xFF, 0x00]
```

#### `bitwiseLogicalXor`

`bitwiseLogicalXor` takes three arguments; we name and describe them below.

1. Whether padding semantics should be used. If this argument is `False`,
   truncation semantics are used instead. This is the _padding semantics
   argument_, and has type `BuiltinBool`.
2. The first input `BuiltinByteString`. This is the _first data argument_.
3. The second input `BuiltinByteString`. This is the _second data argument_.

Let $b_1, b_2$ refer to the semantics-modified first data argument and
semantics-modified second data argument respectively, and let $n$ be either of 
their lengths in bytes; see the 
[section on padding versus truncation semantics](#padding-versus-truncation-semantics) 
for the exact specification of this. Let the result of `bitwiseLogicalXor`, given 
$b_1, b_2$ and some padding semantics argument, be $b_r$, also of length $n$ 
in bytes. We use $b_1\\{i\\}$ to refer to the byte at index $i$ in $b_1$ (and
analogously for $b_2$, $b_r$); see the [section on the bit indexing
scheme](#bit-indexing-scheme) for the exact specification of this.

For all $i \in 0, 1, \ldots, n - 1$, we have 
$b_r\\{i\\} = b_0\\{i\\} \text{ } \wedge \text{ } b_1\\{i\\}$, where $\wedge$ refers to 
a [bitwise XOR][bitwise-xor].

Some examples of the intended behaviour of `bitwiseLogicalXor` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- truncation semantics
bitwiseLogicalXor False [] [0xFF] => []

bitwiseLogicalXor False [0xFF] [] => []

bitwiseLogicalXor False [0xFF] [0x00] => [0xFF]

bitwiseLogicalXor False [0x00] [0xFF] => [0xFF]

bitwiseLogicalXor False [0x4F, 0x00] [0xF4] => [0xBB]

-- padding semantics
bitwiseLogicalOr True [] [0xFF] => [0xFF]

bitwiseLogicalOr True [0xFF] [] => [0xFF]

bitwiseLogicalOr True [0xFF] [0x00] => [0xFF]

bitwiseLogicalOr True [0x00] [0xFF] => [0xFF]

bitwiseLogicalOr True [0x4F, 0x00] [0xF4] => [0xBB, 0x00]
```

#### `bitwiseLogicalComplement`

`bitwiseLogicalComplement` takes a single argument, of type `BuiltinByteString`;
let $b$ refer to that argument, and $n$ its length in bytes. Let $b_r$ be
the result of `bitwiseLogicalComplement`; its length in bytes is also $n$. We
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

Some examples of the intended behaviour of `bitwiseLogicalComplement` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
bitwiseLogicalComplement [] => []

bitwiseLogicalComplement [0x0F] => [0xF0]

bitwiseLogicalComplement [0x4F, 0xF4] => [0xB0, 0x0B]
```

#### `readBit`

`readBit` takes two arguments; we name and describe them below.

1. The `BuiltinByteString` in which the bit we want to read can be found. This
   is the _data argument_.
2. A bit index into the data argument, of type `BuiltinInteger`. This is the
   _index argument_.

Let $b$ refer to the data argument, of length $n$ in bytes, and let $i$ refer to
the index argument. We use $b[i]$ to refer to the value at index $i$ of $b$; see 
the [section on the bit indexing scheme](#bit-indexing-scheme) for the exact 
specification of this.

If $i < 0$ or $i \geq 8 \cdot n$, then `readBit`
fails. In this case, the resulting error message must specify _at least_ the
following information:

* That `readBit` failed due to an out-of-bounds index argument; and
* What `BuiltinInteger` was passed as an index argument.

Otherwise, if $b[i] = 0$, `readBit` returns `False`, and if $b[i] = 1$,
`readBit` returns `True`.

Some examples of the intended behaviour of `readBit` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Indexing an empty BuiltinByteString fails
readBit [] 0 => error

readBit [] 345 => error

-- Negative indexes fail
readBit [] (-1) => error

readBit [0xFF] (-1) => error

-- Indexing reads 'from the end'
readBit [0xF4] 0 => False

readBit [0xF4] 1 => False 

readBit [0xF4] 2 => True 

readBit [0xF4] 3 => False

readBit [0xF4] 4 => True

readBit [0xF4] 5 => True

readBit [0xF4] 6 => True

readBit [0xF4] 7 => True

-- Out-of-bounds indexes fail
readBit [0xF4] 8 => error

readBit [0xFF, 0xF4] 16 => error

-- Larger indexes read backwards into the bytes from the end
readBit [0xF4, 0xFF] 10 => False 
```

#### `writeBits`

`writeBits` takes two arguments: we name and describe them below.

1. The `BuiltinByteString` in which we want to change some bits. This is the
   _data argument_.
2. A list of index-value pairs, indicating which positions in the data argument
   should be changed to which value. This is the _change list argument_. Each
   index has type `BuiltinInteger`, while each value has type `BuiltinBool`.

Let $b$ refer to the data argument of length $n$ in bytes. We define `writeBits`
recursively over the structure of the change list argument. Throughout, we use
$b_r$ to refer to the result of `writeBits`, whose length is also $n$. We use
$b[i]$ to refer to the value at index $i$ of $b$ (and analogously, $b_r$); see
the [section on the bit indexing scheme](#bit-indexing-scheme) for the exact
specification of this.

If the change list argument is empty, we return the data argument unchanged.
Otherwise, let $(i, v)$ be the head of the change list argument, and $\ell$ its
tail. If $i < 0$ or $i \geq 8 \cdot n$, then `writeBits` fails. In this case,
the resulting error message must specify at _least_ the following information:

* That `writeBits` failed due to an out-of-bounds index argument; and
* What `BuiltinInteger` was passed as $i$.

Otherwise, for all $j \in 0, 1, \ldots 8 \cdot n - 1$, we have

$$
b_r[j] = \begin{cases}
         0 & \text{if } j = i \text{ and } v = \texttt{False}\\
         1 & \text{if } j = i \text{ and } v = \texttt{True}\\
         b[j] & \text{otherwise}\\
         \end{cases}
$$

Then, if we did not fail as described above, we repeat the `writeBits`
operation, but with $b_r$ as the data argument and $\ell$ as the change list
argument.

Some examples of the intended behaviour of `writeBits` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Writing an empty BuiltinByteString fails
writeBits [] [(0, False)] => error

-- Irrespective of index
writeBits [] [(15, False)] => error

-- And value
writeBits [] [(0, True)] => error

-- And multiplicity
writeBits [] [(0, False), (1, False)] => error

-- Negative indexes fail
writeBits [0xFF] [((-1), False)] => error

-- Even when mixed with valid ones
writeBits [0xFF] [(0, False), ((-1), True)] => error

-- In any position
writeBits [0xFF] [((-1), True), (0, False)] => error

-- Out-of-bounds indexes fail
writeBits [0xFF] [(8, False)] => error

-- Even when mixed with valid ones
writeBits [0xFF] [(1, False), (8, False)] => error

-- In any position
writeBits [0xFF] [(8, False), (1, False)] => error

-- Bits are written 'from the end'
writeBits [0xFF] [(0, False)] => [0xFE]

writeBits [0xFF] [(1, False)] => [0xFD]

writeBits [0xFF] [(2, False)] => [0xFB]

writeBits [0xFF] [(3, False)] => [0xF7]

writeBits [0xFF] [(4, False)] => [0xEF]

writeBits [0xFF] [(5, False)] => [0xDF]

writeBits [0xFF] [(6, False)] => [0xBF]

writeBits [0xFF] [(7, False)] => [0x7F]

-- True value sets the bit
writeBits [0x00] [(5, True)] => [0x20]

-- False value clears the bit
writeBits [0xFF] [(5, False)] => [0xDF]

-- Larger indexes write backwards into the bytes from the end
writeBits [0xF4, 0xFF] [(10, False)] => [0xF0, 0xFF]

-- Multiple items in a change list apply cumulatively
writeBits [0xF4, 0xFF] [(10, False), (1, False)] => [0xF0, 0xFD]

writeBits (writeBits [0xF4, 0xFF] [(10, False)]) [(1, False)] => [0xF0, 0xFD]

-- Order within a change list is unimportant among unique indexes
writeBits [0xF4, 0xFF] [(1, False), (10, False)] => [0xF0, 0xFD]

-- But _is_ important for identical indexes
writeBits [0x00, 0xFF] [(10, True), (10, False)] => [0x00, 0xFF]

writeBits [0x00, 0xFF] [(10, False), (10, True)] => [0x04, 0xFF]

-- Setting an already set bit does nothing
writeBits [0xFF] [(0, True)] => [0xFF]

-- Clearing an already clear bit does nothing
writeBits [0x00] [(0, False)] => [0x00]
```

#### `replicateByteString`

`replicateByteString` takes two arguments; we name and describe them below.

1. The desired result length, of type `BuiltinInteger`. This is the _length
   argument_.
2. The byte to place at each position in the result, represented as a
   `BuiltinInteger` (corresponding to the unsigned integer this byte encodes).
   This is the _byte argument_.

Let $n$ be the length argument, and $w$ the byte argument. If $n < 0$, then
`replicateByteString` fails. In this case, the resulting error message must specify
_at least_ the following information:

* That `replicateByteString` failed due to a negative length argument; and
* What `BuiltinInteger` was passed as the length argument.

If $n \geq 0$, and $w < 0$ or $w > 255$, then `replicateByteString` fails. In this
case, the resulting error message must specify _at least_ the following
information:

* That `replicateByteString` failed due to the byte argument not being a valid
  byte; and
* What `BuiltinInteger` was passed as the byte argument.

Otherwise, let $b$ be the result of `replicateByteString`, and let $b\\{i\\}$ be the
byte at position $i$ of $b$, as per [the section describing the bit indexing
scheme](#bit-indexing-scheme). We have:

* The length (in bytes) of $b$ is $n$; and
* For all $i \in 0, 1, \ldots, n - 1$, $b\\{i\\} = w$.

Some examples of the intended behaviour of `replicateByteString` follow. For
brevity, we write `BuiltinByteString` literals as lists of hexadecimal values.

```
-- Replicating a negative number of times fails
replicateByteString (-1) 0 => error

-- Irrespective of byte argument
replicateByteString (-1) 3 => error

-- Out-of-bounds byte arguments fail
replicateByteString 1 (-1) => error

replicateByteString 1 256 => error

-- Irrespective of length argument
replicateByteString 4 (-1) => error

replicateByteString 4 256 => error

-- Length of result matches length argument, and all bytes are the same
replicateByteString 0 0xFF => []

replicateByteString 4 0xFF => [0xFF, 0xFF, 0xFF, 0xFF]
```

### Laws

#### Binary operations

We describe laws for all three operations that work over two
`BuiltinByteStrings`, that is, `bitwiseLogicalAnd`, `bitwiseLogicalOr` and
`bitwiseLogicalXor`, together, as many of them are similar (and related). We
describe padding semantics and truncation semantics laws, as they are slightly
different.

All three operations above, under both padding and truncation semantics, are
[commutative semigroups][special-semigroups]. Thus, we have:

```haskell
bitwiseLogicalAnd s x y = bitwiseLogicalAnd s y x

bitwiseLogicalAnd s x (bitwiseLogicalAnd s y z) = bitwiseLogicalAnd s
(bitwiseLogicalAnd s x y) z

-- and the same for bitwiseLogicalOr and bitwiseLogicalXor
```

Note that the semantics (designated as `s` above) must be consistent in order
for these laws to hold. Furthermore, under padding semantics, all the above
operations are [commutative monoids][commutative-monoid]:

```haskell
bitwiseLogicalAnd True x "" = bitwiseLogicalAnd True "" x = x

-- and the same for bitwiseLogicalOr and bitwiseLogicalXor
```

Under truncation semantics, `""` (that is, the empty `BuiltinByteString`) acts
instead as an [absorbing element][absorbing-element]:

```haskell
bitwiseLogicalAnd False x "" = bitwiseLogicalAnd False "" x = ""

-- and the same for bitwiseLogicalOr and bitwiseLogicalXor
```

`bitwiseLogicalAnd` and `bitwiseLogicalOr` are also [semilattices][semilattice],
due to their idempotence:

```haskell
bitwiseLogicalAnd s x x = x

-- and the same for bitwiseLogicalOr
```

`bitwiseLogicalXor` is instead involute:

```haskell
bitwiseLogicalXor s x (bitwiseLogicalXor s x x) = bitwiseLogicalXor s
(bitwiseLogicalXor s x x) x = x
```

Additionally, under padding semantics, `bitwiseLogicalAnd` and
`bitwiseLogicalOr` are [self-distributive][distributive]:

```haskell
bitwiseLogicalAnd True x (bitwiseLogicalAnd True y z) = bitwiseLogicalAnd True
(bitwiseLogicalAnd True x y) (bitwiseLogicalAnd True x z)

bitwiseLogicalAnd True (bitwiseLogicalAnd True x y) z = bitwiseLogicalAnd True
(bitwiseLogicalAnd True x z) (bitwiseLogicalAnd True y z)

-- and the same for bitwiseLogicalOr
```

Under truncation semantics, `bitwiseLogicalAnd` is only left-distributive over
itself, `bitwiseLogicalOr` and `bitwiseLogicalXor`:

```haskell
bitwiseLogicalAnd False x (bitwiseLogicalAnd False y z) = bitwiseLogicalAnd
False (bitwiseLogicalAnd False x y) (bitwiseLogicalAnd False x z)

bitwiseLogicalAnd False x (bitwiseLogicalOr False y z) = bitwiseLogicalOr False
(bitwiseLogicalAnd False x y) (bitwiseLogicalAnd False x z)

bitwiseLogicalAnd False x (bitwiseLogicalXor False y z) = bitwiseLogicalXor
False (bitwiseLogicalAnd False x y) (bitwiseLogicalAnd False x z)
```

`bitwiseLogicalOr` under truncation semantics is left-distributive over itself
and `bitwiseLogicalAnd`:

```haskell
bitwiseLogicalOr False x (bitwiseLogicalOr False y z) = bitwiseLogicalOr False
(bitwiseLogicalOr False x y) (bitwiseLogicalOr False x z)

bitwiseLogicalOr False x (bitwiseLogicalAnd False y z) = bitwiseLogicalAnd False
(bitwiseLogicalOr False x y) (bitwiseLogicalOr False x z)
```

If the first and second data arguments to these operations have the same length,
these operations satisfy several additional laws. We describe these briefly
below, with the added note that, in this case, padding and truncation semantics
coincide:

* `bitwiseLogicalAnd` and `bitwiseLogicalOr` form a [bounded lattice][lattice]
* `bitwiseLogicalAnd` is [distributive][distributive] over itself, `bitwiseLogicalOr` and
  `bitwiseLogicalXor`
* `bitwiseLogicalOr` is [distributive][distributive] over itself and `bitwiseLogicalAnd`

We do not specify these laws here, as they do not hold in general. At the same
time, we expect that any implementation of these operations will be subject to
these laws.

#### `bitwiseLogicalComplement`

The main law of `bitwiseLogicalComplement` is involution:

```haskell
bitwiseLogicalComplement (bitwiseLogicalComplement x) = x
```

In combination with `bitwiseLogicalAnd` and `bitwiseLogicalOr`,
`bitwiseLogicalComplement` gives rise to the famous [De Morgan laws][de-morgan], irrespective of semantics:

```haskell
bitwiseLogicalComplement (bitwiseLogicalAnd s x y) = bitwiseLogicalOr s
(bitwiseLogicalComplement x) (bitwiseLogicalComplement y)

bitwiseLogicalComplement (bitwiseLogicalOr s x y) = bitwiseLogicalAnd s
(bitwiseLogicalComplement x) (bitwiseLogicalComplement y)
```

For `bitwiseLogicalXor`, we instead have (again, irrespective of semantics):

```haskell
bitwiseLogicalXor s x (bitwiseLogicalComplement x) = x
```

#### Bit reading and modification

Throughout, we assume any index arguments to be 'in-bounds'; that is, all the
index arguments used in the statements of any law are such that the operation
they are applied to wouldn't produce an error.

The first law of `writeBits` is similar to the [set-twice law of
lenses][lens-laws]:

```haskell
writeBits bs [(i, b1), (i, b2)] = writeBits bs [(i, b2)]
```

Together with `readBit`, we obtain the remaining two analogues to the lens
laws:

```haskell
-- writing to an index, then reading from that index, gets you what you wrote
readBit (writeBits bs [(i, b)]) i = b

-- if you read from an index, then write that value to that same index, nothing
-- happens
writeBits bs [(i, readBit bs i)] = bs
```

Furthermore, given a fixed data argument, `writeBits` acts as a [monoid
homomorphism][monoid-homomorphism] lists under concatenation to functions:

```haskell
writeBits bs [] = bs

writeBits bs (is <> js) = writeBits (writeBits bs is) js
```

#### `replicateByteString`

Given a fixed byte argument, `replicateByteString` acts as a [monoid
homomorphism][monoid-homomorphism] from natural numbers under addition to
`BuiltinByteString`s under concatenation: 

```haskell
replicateByteString 0 w = ""

replicateByteString (n + m) w = replicateByteString n w <> replicateByteString m w
```

Additionally, for any 'in-bounds' index (that is, any index for which
`indexByteString` won't error) `i`, we have

```haskell
indexByteString (replicateByteString n w) i = w
```

Lastly, we have

```haskell
lengthByteString (replicateByteString n w) = n
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
implementation in [CIP-58][cip-58], and `replicateByteString` is a direct wrapper
around the `replicate` function in `ByteString`. Thus, we do not discuss them
further here.

### Relationship to CIP-58 and CIP-121

Our work relates to both [CIP-58][cip-58] and [CIP-121][cip-121]. Essentially,
our goal with both this CIP and CIP-121 is to both break CIP-58 into more
manageable (and reviewable) parts, and also address some of the design choices
in CIP-58 that were not as good (or as clear) as they could have been. In this
regard, this CIP is a direct continuation of CIP-121; CIP-121 dealt with
conversions between `BuiltinByteString` and `BuiltinInteger`, while this CIP
handles bit indexing more generally, as well as 'parallel' logical operations
that operate on all the bits of a `BuiltinByteString` in bulk. 

We describe how our work in this CIP relates to (and in some cases, supercedes)
CIP-58, as well as how it follows on from CIP-121, in more detail below.

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

The second notion is _most-significant-first conversion agreement_. This notion
refers to the [CIP-121 concept of the same name][cip-121-big-endian], and
ensures that (at least for the most-significant-first arrangement), the
following workflow doesn't produce unexpected results:

1. Convert a `BuiltinInteger` to `BuiltinByteString` using
   `builtinIntegerToByteString` with the most-significant-first endianness
   argument.
2. Manipulate the bits of the result of step 1 using the operations specified 
   here.
3. Convert the result of step 2 back to a `BuiltinInteger` using
   `builtinByteStringToInteger` with the most-significant-first endianness
   argument.

This workflow is directly relevant to Case 2. The Argon2 family of hashes use
certain inputs (which happen to be numbers) both as numbers (meaning, for
arithmetic operatons) and also as blocks of binary (specifically for XOR). This
is not unique to Argon2, or even hashing, as a range of operations (especially
in cryptographic applications) use similar approaches, whether for performance,
semantics or both. In such cases, users of our primitives (both logical and
conversion) must be confident that their changes 'translate' in the way they
expect between these two 'views' of the data. 

The choice of most-significant-first as the arrangement that we must agree with
seems somewhat arbitrary at a glance, for two reasons: firstly, it's not clear
why we must pick a single arrangement to be consistent with; secondly, the
reasoning for the choice of most-significant-first over most-significant-last 
as the arrangement to agree with isn't immediately apparent. To see why this is
the only choice that we consider reasonable, we first observe that, according 
to the definition of the bit indexing scheme given [in
the corresponding section](#bit-indexing-scheme), as well as the corresponding
definition for the bit-flip variant, we view a `BuiltinByteString` of length $n$
as a binary natural number with exactly $8n$ digits, and the value at index $i$
corresponds to the digits whose place value is either $2^i$ (for the bit-flip
variant), or $2^{8n - i - 1}$ (for our chosen method). Put another way, under
the specification for the bit-flip variant, the least significant binary digit
is first, whereas in our chosen specification, the least significant binary
digit is last. CIP-121's conversion primitives mirror this reasoning: the
most-significant-first arrangement corresponds to our chosen method, while the
most-significant-last arrangement corresponds to the bit-flip variant instead.
The difference is the digit value: for us, the digit value is (effectively) 2,
while for CIP-121's conversion primitives, it is 256 instead.

We also observe that, when we index a `BuiltinByteString`'s _bytes_, we get back
a `BuiltinInteger`, whic has a numerical value as a natural number in the range
$[0, 255]$. Putting these two observations together, we consider it sensible
that, given a non-empty `BuiltinByteString`, if we were to get the values at bit
indexes $0$ through $7$, then sum their corresponding place values (treating
clear bits as $0$ and set bits as the appropriate place value), we should get
the same result as indexing whichever byte those bits came from.

Consider the `BuiltinByteString` whose only byte is $42$, whose representation 
is as follows:

```
| Byte index | 0        |
|------------|----------|
| Byte       | 00101010 |
```

We note that, if we index this `BuiltinByteString` at byte position $0$, we get
back the answer $42$. Furthermore, if we use `builtinByteStringToInteger` from
CIP-121 with such a `BuiltinByteString`, we get the result $42$ as well,
regardless of the endianness argument we choose.

Under the bit-flip variant, the bit indexes of this `BuiltinByteString` would be
as follows:

```
| Byte index | 0                             |
|------------|-------------------------------|
| Byte       | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
|------------|-------------------------------|
| Bit index  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
```

However, we immediately see a problem: under this indexing scheme, the $2^2 = 4$
place value is $1$, which would suggest that in the binary representation of
$42$, the corresponding digit is also $1$. However, this is not the case. Under
our scheme of choice however, we get the correct answer:

```
| Byte index | 0                             |
|------------|-------------------------------|
| Byte       | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
|------------|-------------------------------|
| Bit index  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
```

Here, the $4$ place value is correctly $0$. This demonstrates that of the two
indexing scheme possibilities that preserve index locality, only one can be
consistent with _any_ choice of byte arrangement, whether most-significant-first
or most-significant-last: the one we chose. This implies that we cannot be
consistent with both arrangements while also preserving index locality.

Let us now consider a larger example `BuiltinByteString`:

```
| Byte index | 0        | 1        |
|------------|----------|----------|
| Byte       | 00101010 | 11011011 |
```

This would produce two different results when converted with
`builtinByteStringToInteger`, depending on the choice of endianness argument:

* For the most-significant-first arrangement, the result is $42 * 256 + 223 =
  10975$.
* For the most-significant-last arrangement, the result is $223 * 256 + 42 =
  57130$.

These have the following 'breakdowns' in base-2:

* $10975 = 8096 + 2048 + 512 + 256 + 32 + 16 + 8 + 4 + 2 + 1 = 2^13 + 2^11 + 2^9 + 2^8 + 2^5 + 2^4 + 2^3 + 2^2 + 2^1 + 2^0$
* $57130 = 32768 + 16386 + 4096 + 2048 + 1024 + 512 + 256 + 32 + 8 + 2 = 2^15 + 2^14 + 2^12 + 2^11 + 2^10 + 2^9 + 2^8 + 2^5 + 2^3 + 2^1$

Under the bit-flip variant, the bit indexes of this `BuiltinByteString` would be
as follows:

```
| Byte index | 0                             | 1                                   |
|------------|-------------------------------|-------------------------------------|
| Byte       | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0  | 1  | 1  | 0  | 1  | 1  |
|------------|-------------------------------|-------------------------------------|
| Bit index  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
```

We immediately see a problem, as in this representation, it suggests that the
$2^1 = 2$ place value has zero digit value. This is true of _neither_ $10975$
nor $57130$'s base-2 forms, which have the $2$ place value with a $1$ digit
value. This suggests that the bit-flip variant cannot agree with _either_ choice
of arrangement in general.

However, if we view the bit indexes using our chosen scheme:

```
| Byte index | 0                                   | 1                             |
|------------|-------------------------------------|-------------------------------|
| Byte       | 0  | 0  | 1  | 0  | 1  | 0  | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 |
|------------|-------------------------------------|-------------------------------|
| Bit index  | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
```

the $2$ place value is correctly shown as having a digit value of 1. 

Combining these observations, we note that, assuming we value index locality,
choosing our scheme gives us consistency with the most-significant-first
arrangement, as well as consistency with byte indexing digit values, but
choosing the bit-flip variant gives us _neither_. As we need both index locality
_and_ consistency with at least one arrangement, our choice is the correct one.
The fact that we also get byte indexing digit values being consistent is another
reason for our choice.

### Padding versus truncation

For the operations defined in this CIP taking two `BuiltinByteString` arguments
(that is, `bitwiseLogicalAnd`, `bitwiseLogicalOr`, and `bitwiseLogicalXor`),
when the two arguments have identical lengths, the semantics are natural,
mirroring the corresponding operations on the 
[Boolean algebra][boolean-algebra-2] $\textbf{2}^{8n}$, where $n$ is the length 
of either argument in bytes. When the arguments do _not_ have matching lengths,
however, the situation becomes more complex, as there are several ways in which
we could define these operations. The most natural possibilities are as follows;
we repeat some of the definitions used [in the corresponding
section](#padding-versus-truncation-semantics).

* Extend the shorter argument with the identity element (all-1s for
  `bitwiseLogicalAnd`, all-0s otherwise) to match the length of the longer argument,
  then perform the operation as if on matching-length arguments. We call this
  _padding semantics_.
* Ignore the bytes of the longer argument whose indexes would not be valid for
  the shorter argument, then perform the operation as if on matching-length
  arguments. We call this _truncation semantics_.
* Fail with an error whenever argument lengths don't match. We call this
  _match semantics_.

Furthermore, for both padding and truncation semantics, we can choose to pad (or
truncate) _low_ index bytes or _high_ index bytes. To illustrate the difference,
consider the two `BuiltinByteString`s (written as arrays of bytes for
simplicity) `[0xFF, 0x0F, 0x00]` and `[0x8F, 0x99]`. Under padding semantics,
padding low index bytes would give us `[0x00, 0x8F, 0x99]` (or `[0xFF, 0x8F,
0x99]` depending on operation), while padding high index bytes would give us
`[0x8F, 0x99, 0x00]` (or `[0x8F, 0x99, 0xFF]` depending on operation). Under
truncation semantics, truncating low index bytes would give us `[0x0F, 0x00]`,
while truncating high index bytes would give us `[0xFF, 0x0F]`.

It is not a priori clear which of these we should choose: they are subject to
different laws (as evidenced by the [corresponding
section](#laws-and-examples)), none of which are strict supersets of each other
(at least not for _all_ inputs possible). While [CIP-58][cip-58] chose match
semantics, we believe this was not the correct decision: we use Case 1 to
justify the benefit of having other semantics described above available.

Consider the following operation: given a bound $k$, a 'direction' (larger or
smaller), and an integer set, remove all elements indicates by the direction and
$k$ (that is, either smaller than $k$ or larger than $k$, as indicated by the
direction). This could be done using a `bitwiseLogicalAnd` and a mask. However,
under match semantics, this mask would have to have a length equal to the
integer set representation; under padding semantics, the mask would potentially
only need $\Theta(k)$ length, depending on direction. This is noteworthy, as
padding the mask would require an additional copy operation, only to produce a
value that would be discarded immediately.

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
much as for [CIP-121 primitives][conversion-cip] and endianness issues, that
the primitive should allow a choice in what semantics get used for any given
call. Ideally, we would allow a choice of any of the three options described
above (along with a choice of low or high index padding or truncation); 
however, this is awkward to do in Plutus Core. While the choice between
_two_ options is straightforward (pass a `BuiltinBool`), the choice between
more than this number would require something like a `BuiltinInteger` argument
with 'designated values' ('0 means match', '1 means low-index padding', etc).
This is not ideal, as they involve additional checks, argument redundancy, or
both. In light of this, we made the following decisions:

1. We would choose only two of the three semantics, and have this choice
   controlled for any given call be controlled by a `BuiltinBool` flag; and
2. For padding or truncation semantics, we would _always_ use either low or high
   index padding (or truncation).

This leads naturally to two questions: which of the three semantics above we can
afford to exclude, and whether low or high index padding should be chosen. We
believe that the correct choices are to exclude match semantics, and to use
high index padding and truncation, for several reasons. 

Firstly, we can simulate
match semantics with either padding or truncation semantics, together with a
length check. While we could also simulate padding semantics via match semantics
similarly, the amount of effort (both developer and computational) required is
significantly more in that case: a length check is a constant-time operation,
while manually padding is linear at best (and even then, it requires operations
only this CIP provides, as it would be quadratic otherwise), and on top of that,
manual padding is much fiddlier and easier to get wrong. 

Secondly, truncation semantics are common enough in Haskell that we believe
excluding them as an option is both surprising and wrong. Any developer familiar
with Haskell has interacted with various `zipWith` operations, and having our
primitives behave differently to this at minimum creates friction for
implementers of higher-level abstractions atop the primitives in this CIP. While
Haskellers are not exclusive users of Plutus primitives (directly or not), there
are definitely enough of them that _not_ having truncation semantics available
would create a lot of unnecessary friction.

Thirdly, outside of error checking, match semantics give few benefits,
performance or otherwise. The examples above demonstrate cases where padding and
truncation semantics lead to better performance, less fiddly implementations, or
both: finding such a case for match semantics outside of error checking is
difficult at best.

This combination of reasoning leads us to consider padding and truncation as the
two semantics we should retain, and this guided our implementation choices
accordingly. With regard to padding (or truncating) low or high indexes, given
that we pad (or truncate) whole bytes by necessity, it makes the corresponding
operations (effectively) operate over bytes, or rather, they view
`BuiltinByteString`s as linear collections of bytes, rather than bits. When
viewed this way, the `zipWith` analogy with Haskell suggests that truncating
high is the correct choice: truncating low would be quite surprising to a
Haskeller familiar with how `zipWith`-style operations behave. Furthermore, as
having padding low and truncating high would be confusing (and arguably quite
strange), padding high seems like the correct choice. Thus, we decided to both
pad and truncate high in light of this. 

### Bit setting

`writeBits` in our description takes a change list argument, allowing
changing multiple bits at once. This is an added complexity, and an argument can
be made that something similar to the following operation would be sufficient:

```haskell
writeBit :: BuiltinByteString -> BuiltinInteger -> BuiltinBool ->
BuiltinByteString
```

Essentially, `writeBit bs i v` would be equivalent to `writeBits bs
[(i, v)]` as currently defined. This was the choice made by [CIP-58][cip-58],
with the consideration of simplicity in mind. 

At the same time, due to the immutability semantics of Plutus Core, each time
`writeBit` would be called, we would have to copy its `BuiltinByteString` 
argument. Thus, a sequence of $k$ `setBit` calls in a fold over a
`BuiltinByteString` of length $n$ would require $\Theta(nk)$ time and
$\Theta(nk)$ space. Meanwhile, if we instead used `writeBits`, the time
drops to $\Theta(n + k)$ and the space to $\Theta(n)$, which is a non-trivial
improvement. While we cannot avoid the worst-case copying behaviour of
`setBit` (if we have a critical path of read-write dependencies of length
$k$, for example), and 'list packing' carries some cost, we have
[benchmarks][benchmarks-bits] that show not only that this 'packing cost' is
essentially zero, but that for `BuiltinByteString`s of 30 bytes or fewer,
copying completely overwhelms the work required to modify the bits specified in
the change list argument. This alone is good evidence for having `writeBits` instead;
indeed, there is prior art for doing this [in the `vector` library][vector], for
the exact reasons we give here.

The argument could also be made whether this design should be extended to other
primitive operations in this CIP which both take `BuiltinByteString` arguments
and also produce `BuiltinByteString` results. We believe that this is not as
justified as in the `writeBits` case, for several reasons. Firstly, for
`bitwiseLogicalComplement`, it's not clear what benefit this would have at
all: the only possible signature such an operation would have is
`[BuiltinByteString] -> [BuiltinByteString]`, which in effect would be a
specialized form of mapping. While an argument could be made for a _general_
form of mapping as a Plutus Core primitive, it wouldn't be reasonable for an
operation like this to be considered for such.

Secondly, the performance benefits of such an operation aren't nearly as 
significant in theory, and likely wouldn't be in practice either. Consider 
this hypothetical operation (with fold semantics):

```haskell
bitwiseLogicalXors :: BuiltinBool -> [BuiltinByteString] -> BuiltinByteString
```

Simulating this operation as a fold using `bitwiseLogicalXor`, in the worst
case, irrespective of padding or truncation semantics, requires $\Theta(nk)$
time and space, where $n$ is the size of each `BuiltinByteString` in the
argument list, and $k$ is the length of the argument list itself. Using
`bitwiseLogicalXors` instead would reduce the space required to $\Theta(n)$, 
but would not affect the time complexity at all. 

Lastly, it is questionable whether 'bulk' operations like `bitwiseLogicalXors`
above would see as much use as `writeBits`. In the context of Case 1,
`bitwiseLogicalXors` corresponds to taking the symmetric difference of multiple
integer sets; it seems unlikely that the number of sets we'd want to do this
with would frequently be higher than 2. However, in the same context,
`writeBits` corresponds to constructing an integer set given a list of
members (or, for that matter, _non_-members): this is an operation that is both
required by the case description, and also much more likely to be used often.

On the basis of the above, we believe that choosing to implement
`writeBits` as a 'bulk' operation, but to leave others as 'singular' is the
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

- [x] Included within a major haskell cardano-node release
  - https://github.com/IntersectMBO/cardano-node/releases/tag/10.1.1  
- [x] Enabled on Cardano mainnet via a hardfork
  - Enabled by Plomin hardfork

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
[conversion-cip]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0121/README.md
[benchmarks-bits]: https://github.com/mlabs-haskell/plutus-integer-bytestring/blob/main/bench/naive/Main.hs#L74-L83
[vector]: https://hackage.haskell.org/package/vector-0.13.1.0/docs/Data-Vector.html#v:-47--47-
[boolean-algebra-2]: https://en.wikipedia.org/wiki/Two-element_Boolean_algebra
[hashing]: https://en.wikipedia.org/wiki/Hash_function
[sha256]: https://en.wikipedia.org/wiki/Secure_Hash_Algorithms
[blake2b]: https://en.wikipedia.org/wiki/BLAKE_(hash_function)
[argon2]: https://en.wikipedia.org/wiki/Argon2
[xor-crypto]: https://en.wikipedia.org/wiki/Exclusive_or#Bitwise_operation
[cip-121]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0121/README.md
[cip-121-big-endian]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0121/README.md/#representation
[bitwise-and]: https://en.wikipedia.org/wiki/Bitwise_operation#AND
[bitwise-or]: https://en.wikipedia.org/wiki/Bitwise_operation#OR
[bitwise-xor]: https://en.wikipedia.org/wiki/Bitwise_operation#XOR
