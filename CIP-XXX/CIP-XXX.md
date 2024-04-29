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
         b_0[i] & n_1 < n_0 \text{ and } n_r > \min { n_1, n_2 } \\
         b_1[i] & n_0 < n_1 \text { and } n_r > \min { n_1, n_2 } \\
         1 & b_0[i] = b_1[i] = 1 \\
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
         b_0[i] & n_1 < n_0 \text{ and } n_r > \min { n_1, n_2 } \\
         b_1[i] & n_0 < n_1 \text { and } n_r > \min { n_1, n_2 } \\
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
         b_0[i] & n_1 < n_0 \text{ and } n_r > \min { n_1, n_2 } \\
         b_1[i] & n_0 < n_1 \text { and } n_r > \min { n_1, n_2 } \\
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

#### `builtinSetBits`

#### `builtinReplicate`

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
