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

TODO: Add case for integer set

TODO: Another 1-2 example uses

## Specification

We describe the proposed operations in several stages. First, we specify a
scheme for indexing individual bits (rather than whole bytes) in a
`BuiltinByteString`. We then specify the semantics of each operation, as well as
giving costing expectations. Lastly, we provide some laws that these operations
are supposed to obey, as well as giving some specific examples of results from
the use of these operations.

### Bit indexing scheme

TODO: Specify

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

TODO: Example

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
to the $i$th bit of $b_1$ (and analogously for 
$b_2, b_r$); see the [section on the bit indexing scheme](#bit-indexing-scheme)
for the exact specification of this.

If the padding semantics argument is `True`, then we have $n_r = \max \{ n_1,
n_2 \}$; otherwise, $n_r = \min \{ n_1, n_2 \}$. For all $i \in 0, 1, \ldots 8
\cdot n_r - 1$, we have

$$
b_r[i] = \begin{cases}
         b_0[i] & \text{if } n_1 < n_0 \text{ and } i \geq 8 \cdot \min \{ n_1, n_2 \} \\
         b_1[i] & \text{if } n_0 < n_1 \text { and } i \geq 8 \cdot \min \{ n_1, n_2 \} \\
         1 & \text{if } b_0[i] = b_1[i] = 1 \\
         0 & \text{otherwise} \\
         \end{cases}
$$

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
to the $i$th bit of $b_1$ (and analogously for 
$b_2, b_r$); see the [section on the bit indexing scheme](#bit-indexing-scheme)
for the exact specification of this.

If the padding semantics argument is `True`, then we have $n_r = \max \{ n_1,
n_2 \}$; otherwise, $n_r = \min \{ n_1, n_2 \}$. For all $i \in 0, 1, \ldots 8
\cdot n_r - 1$, we have

$$
b_r[i] = \begin{cases}
         b_0[i] & \text{if } n_1 < n_0 \text{ and } i \geq 8 \cdot \min \{ n_1, n_2 \} \\
         b_1[i] & n_0 < n_1 \text { and } i \geq 8 \cdot \min \{ n_1, n_2 \} \\
         0 & b_0[i] = b_1[i] = 0 \\
         1 & \text{otherwise} \\
         \end{cases}
$$

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
refer to the $i$th bit of $b_1$ (and analogously for 
$b_2, b_r$); see the [section on the bit indexing scheme](#bit-indexing-scheme)
for the exact specification of this.

If the padding semantics argument is `True`, then we have $n_r = \max \{ n_1,
n_2 \}$; otherwise, $n_r = \min \{ n_1, n_2 \}$. For all $i \in 0, 1, \ldots 8
\cdot n_r - 1$, we have

$$
b_r[i] = \begin{cases}
         b_0[i] & \text{if } n_1 < n_0 \text{ and } i \geq 8 \cdot \min \{ n_1, n_2 \} \\
         b_1[i] & \text{if } n_0 < n_1 \text { and } i \geq 8 \cdot \min { n_1, n_2 } \\
         0 & b_0[i] = b_1[i] \\
         1 & \text{otherwise} \\
         \end{cases}
$$

#### `builtinLogicalComplement`

`builtinLogicalComplement` takes a single argument, of type `BuiltinByteString`;
let $b$ refer to that argument, and $n$ its length in bytes. Let $b_r$ be
the result of `builtinLogicalComplement`; its length in bytes is also $n$. We
use $b[i]$ to refer to the $i$th bit of $b$ (and analogously for $b_r$); see the
[section on the bit indexing scheme](#bit-indexing-scheme) for the exact
specification of this.

For all $i \in 0, 1, \ldots , 8 \cdot n - 1$, we have

$$
b_r[i] = \begin{cases}
        0 & b[i] = 1\\
        1 & \text{otherwise}\\
        \end{cases}
$$

#### `builtinReadBit`

`builtinReadBit` takes two arguments; we name and describe them below.

1. The `BuiltinByteString` in which the bit we want to read can be found. This
   is the _data argument_.
2. A bit index into the data argument, of type `BuiltinInteger`. This is the
   _index argument_.

Let $b$ refer to the data argument, of length $n$ in bytes, and let $i$ refer to
the index argument. We use $b[i]$ to refer to the $i$th bit of $b$; see the 
[section on the bit indexing scheme](#bit-indexing-scheme) for the exact 
specification of this.

If $i < 0$ or $i \geq 8 \cdot n$, then `builtinReadBit`
fails. In this case, the resulting error message must specify _at least_ the
following information:

* That `builtinReadBit` failed due to an out-of-bounds index argument; and
* What `BuiltinInteger` was passed as an index argument.

Otherwise, if $b[i] = 0$, `builtinReadBit` returns `False`, and if $b[i] = 1$,
`builtinReadBit` returns `True`.

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
the $i$th bit of $b$ (and analogously, $b_r$); see the [section on the bit
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
         0 & \text{if } j = i \text{ and } b = \texttt{False}//
         1 & \text{if } j = i \text{ and } b = \texttt{True}//
         b[j] & \text{otherwise}//
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

Otherwise, let $b$ be the result of `builtinReplicate`, and let $b[i]$ be the
byte at position $i$ of $b$, as per `builtinIndexByteString`. We have:

* The length (in bytes) of $b$ is $n$; and
* For all $i \in 0, 1, \ldots, n - 1$, $b[i] = w$.

### Laws and examples

TODO: Make some

## Rationale: how does this CIP achieve its goals?

TODO: Explain goals relative examples, give descriptions of non-existent
alternatives

## Path to Active

### Acceptance Criteria

TODO: Fill these in (lower priority)

### Implementation Plan

These operations will be implemented by MLabs, to be merged into Plutus Core
after review.

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
