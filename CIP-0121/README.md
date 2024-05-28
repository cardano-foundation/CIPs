---
CIP: 121
Title: Integer-ByteString conversions
Category: Plutus
Status: Active
Authors:
    - Koz Ross <koz@mlabs.city>
    - Ilia Rodionov <ilia@mlabs.city>
    - Jeff Cheah <jeff@mlabs.city>
Implementors:
    - Koz Ross <koz@mlabs.city>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/624
Created: 2023-11-17
License: CC-BY-4.0
---

## Abstract

Plutus Core primitive operations to convert `BuiltinInteger` to
`BuiltinByteString`, and vice-versa. Furthermore, the `BuiltinInteger`
conversion allows different endianness for the encoding (most-significant-first
and most-significant-last), as well as padding with zeroes based on a requested
length if required.

## Motivation: why is this CIP necessary?

Plutus Core creates a strong abstraction boundary between the concepts of
'number' (represented by `BuiltinInteger`) and 'blob of bytes' (represented by
`BuiltinByteString`), defining different sets of (largely non-overlapping)
operations for each. This is, in principle, a good practice, as these concepts
are distinct in (most of) the operations that make sense on them. However,
sometimes, being able to 'move between' these two 'worlds' is important: namely,
the ability to represent a given `BuiltinInteger` as a `BuiltinByteString`, as
well as to convert between this representation and the `BuiltinInteger` it
represents. Currently, no such capability exists: while [CIP-0058][cip-0058]
proposed such a capability (among others), to date, this has not been
implemented into Plutus Core.

To see why such a capability would be beneficial, we give two motivating use
cases.

### Case 1: signing bids

Consider the following code snippet:

```haskell
validBidTerms :: AuctionTerms -> CurrencySymbol -> BidTerms -> Bool
validBidTerms AuctionTerms {..} auctionID BidTerms {..}
  | BidderInfo {..} <- bt'Bidder =
  validBidderInfo bt'Bidder &&
  -- The bidder pubkey hash corresponds to the bidder verification key.
  verifyEd25519Signature at'SellerVK
    (sellerSignatureMessage auctionID bi'BidderVK)
    bt'SellerSignature &&
  -- The seller authorized the bidder to participate
  verifyEd25519Signature bi'BidderVK
    (bidderSignatureMessage auctionID bt'BidPrice bi'bidderPKH)
    bt'BidderSignature
  -- The bidder authorized the bid

bidderSignatureMessage
  :: CurrencySymbol
  -> Integer
  -> PubKeyHash
  -> BuiltinByteString
bidderSignatureMessage auctionID bidPrice bidderPKH =
  toByteString auctionID <>
  toByteString bidPrice <>
  toByteString bidderPKH

sellerSignatureMessage
  :: CurrencySymbol
  -> BuiltinByteString
  -> BuiltinByteString
sellerSignatureMessage auctionID bidderVK =
  toByteString auctionID <>
  bidderVK
```

Here, we attempt to verify (using the Curve25519) that a bid at an auction was
signed by a particular bidder. The message to verify must include the bid
placed, represented using `Integer` here (which translates to `BuiltinInteger`
onchain). However, the `verifyEd25519Signature` primitive can only accept
`BuiltinByteString`s as messages to verify. Thus, we have a problem: how to
include the placed bid into the bid message to be verified?

More generally, constructing messages to sign usually consists of 
concatenating together some primitives represented as `BuiltinByteString`s. 
We currently have a way to do this for (some) strings using `encodeUtf8`, 
but no way to do this for `BuiltinInteger`s.

### Case 2: finite fields

[Finite fields][finite-field], also known as Galois fields, are a common
algebraic structure in cryptographic constructions. Many, if not most, common
constructions in cryptography use finite fields as their basis, including
[Curve25519][curve-25519], [Curve448][curve-448] and the [Pasta
curves][pasta-curves], to name but a few. Elements in a finite field are
naturally representable as `BuiltinInteger`s of bounded size onchain, but for
applications like the constructions specified above (and indeed, anything built
atop such constructions), we need to be able to perform the following tasks
efficiently:

* Verify that a particular value belongs to the field; and
* Perform bitwise (that is, non-numerical) operations on such values, possibly
  together with numerical ones.

Furthermore, Case 2 presents two further challenges: _endianness_ and
_padding_. Due to many cryptographic algorithms being designed for use over the
network, their specifications assume a big-endian byte ordering in their
implementations. Likewise, due to the finiteness of a finite field's elements,
they can be encoded in a fixed-length form, which implementations make use of, 
both for convenience and efficiency.

[cip-0058]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0058
[finite-field]: https://en.wikipedia.org/wiki/Finite_field
[curve-25519]: https://en.wikipedia.org/wiki/Curve25519
[curve-448]: https://en.wikipedia.org/wiki/Curve448
[pasta-curves]: https://electriccoin.co/blog/the-pasta-curves-for-halo-2-and-beyond/

--- 

While it is not outright impossible to perform conversions from `BuiltinInteger`
to `BuiltinByteString` currently, it is unreasonably difficult and
resource-intensive: `BuiltinInteger` to `BuiltinByteString` involves a repeated
combination of division-with-remainder in a loop, while `BuiltinByteString` to
`BuiltinInteger` involves repeated multiplications by large constants and
accumulations. Aside from these both requiring looping (with the overheads this
imposes), both of these are effectively quadratic operations with current
primitives: the only means we have to accumulate `BuiltinByteString`s is by
consing or appending (which are both quadratic due to `BuiltinByteString` being
a counted array), and any `BuiltinInteger` operation is linear in the size of
its arguments. This makes even Case 1 far more effort, both for the developer and
the node, than it should be, and Case 2 ranges from difficult to impossible once
we factor in the limited available primitive operations and the endianness and
padding problems.

We propose that two primitives be added to Plutus Core: one for converting
`BuiltinInteger`s to `BuiltinByteString`s, the other for converting
`BuiltinByteString`s to `BuiltinInteger`s. The first of these primitives would
allow for specifying an endianness for the result, as well as to perform padding
to a required length if necessary; the second primitive is able to operate on
padded or unpadded encodings, in either endianness.

Additionally, we state the following goals that any implementation of such
primitives must have.

### No metadata

The representation produced by the `BuiltinInteger` to `BuiltinByteString`
conversion should be 'minimal', representing only the number being given to it,
and no other information besides. It would be tempting to, for example, encode
the endianness requested into the `BuiltinByteString`, but ultimately, this
information could be added later by users if they want it, while removing it
would be trickier. Additionally, metadata-related concerns would complicate both
the specification and implementation of the primitives, for arguably marginal
benefit.

### Internals-independence

Users of these primitives should not need to know how _exactly_
`BuiltinInteger`s are represented to use them successfully. This is beneficial
to both users (as they now don't have to concern themselves with
platform-specific implementation issues) and Plutus Core maintainers (as changes
in the representation of `BuiltinInteger` aren't going to affect these
primitives).

### No support for negative numbers

While for fixed-size numbers, [two's-complement][twos-complement] is the default
choice for negative number representations, for arbitrary-size numbers, there is
no agreed-upon choice. Furthermore, indicating the 'negativity' of a number
would require making representations larger or more complex regardless of which
representation we chose, while also complicating both the primitives we want to
define, and any user-defined operations on such representations, possibly in
ways that users do not want. Lastly, for our cases, negative values are not
really needed, and if the ability to encode negative numbers was necessary,
users could still define whichever one(s) they needed themselves, with little
effort or computational cost.

[twos-complement]: https://en.wikipedia.org/wiki/Two%27s_complement

---

This CIP partially supercedes [CIP-0058][cip-0058]: specifically, the
specifications here replace the `integerToByteString` and `byteStringToInteger`
primitives specified in CIP-0058, as improved, and more general, solutions.

## Specification

We describe the specification of two Plutus Core primitives, which will have the
following signatures:

* `builtinIntegerToByteString :: BuiltinBool -> BuiltinInteger -> BuiltinInteger
  -> BuiltinByteString`
* `builtinByteStringToInteger :: BuiltinBool -> BuiltinByteString ->
  BuiltinInteger`

To describe the semantics of these primitives, we first specify how we represent
a `BuiltinInteger` as a `BuiltinByteString`; after that, we describe the two
primitives, as well as giving some properties they must follow.

### Representation

Our `BuiltinByteString` representations of non-negative `BuiltinInteger`s treat
the `BuiltinInteger` being represented as a sequence of digits in base-256.
Thus, any byte in the `BuiltinByteString` representation corresponds to a single
base-256 digit, whose digit value is equal to its value as an 8-bit unsigned
integer. For example, the byte `0x80` would have digit value 128, while the byte
`0x03` would have digit value 3.

To determine place value, we define two possible arrangements of digits in such
a representation: _most-significant-first_, and _most-significant-last_. In the
most-significant-first representation, the first digit (that is, the byte at
index 0) has the highest place value; in the most-significant-last
representation, the first digit instead has the _lowest_ place value. These
correspond to the notions of [big-endian and little-endian][endianness]
respectively.

For any positive `BuiltinInteger` `i`, let 

$$i_0 \times 256^0 + i_1 \times 256^1 + \ldots + i_k \times 256^k$$

be its [base-256 form][base-256-form]. Then, for the most-significant-first
representation, the `BuiltinByteString` encoding for `i` is the
`BuiltinByteString` `b` such that $\texttt{indexByteString bs j} = i_{k - j}$. For
the most-significant-last encoding, we instead have 
$\texttt{indexByteString bs j} = i_j$.

[base-256-form]: https://en.wikipedia.org/wiki/Numeral_system#Positional_systems_in_detail

For example, consider the number `123_456`. Its base-256 form is 

```
64 * 256 ^ 0 + 226 * 256 ^ 1 + 1 * 256 ^ 2
```

Therefore, its most-significant-first representation would be

```
[ 0x01, 0xE2, 0x40 ]
```

while its most-significant-last representation would be

```
[ 0x40, 0xE2, 0x01 ]
```

For `0`, in line with the above definition, both its most-significant-first and
most-significant-last representation is `[]` (that is, the empty
`BuiltinByteString`).

To represent any given non-negative `BuiltinInteger` `i` as above, we require 
a minimum number of base-256 digits. For positive `i`, this is 
$\max \\{1, \lceil \log_{256}(\texttt{i}) \rceil \\}$; for `i = 0`, we define this to be
$0$. We can choose to represent `i` with more digits than this minimum, by the
use of _padding_. Let $k$ be the minimum number of digits to represent `i`, and
let $j$ be a positive number: to represent `i` using $k + j$ digits in the
most-significant-first encoding, we set the first $j$ bytes of the encoding as
`0x0`; for the most-significant-last encoding, we set the _last_ $j$ bytes of
the encoding as `0x0` instead.

[endianness]: https://en.wikipedia.org/wiki/Endianness

To extend our previous example, a five-digit, most-significant-first 
representation of `123_456` is

```
[ 0x00, 0x00, 0x01, 0xC2, 0x80 ]
```

while the most-significant-last representation would be

```
[ 0x80, 0xC2, 0x01, 0x00, 0x00 ]
```

We observe that these extra digits do not change what exact `BuiltinInteger` is
represented, as any zero digit has zero place value.

### `builtinIntegerToByteString`

We can now describe the semantics of the `builtinIntegerToByteString` 
primitive. The `builtinIntegerToByteString` function takes three arguments; we
specify (and name) them below:

1. Whether the most-significant-first encoding should be used. This is the
   _endianness argument_, which has type `BuiltinBool`.
2. The number of bytes required in the output (if such a requirement exists).
   This is the _length argument_, which has type `BuiltinInteger`.
3. The `BuiltinInteger` to convert. This is the _input_.

If the input is negative, `builtinIntegerToByteString` fails. In this case, the
resulting error message must specify _at least_ the following information:

* That `builtinIntegerToByteString` failed due to a negative conversion attempt;
  and
* What negative `BuiltinInteger` was passed as the input.

If the length argument is outside the closed interval $(0, 2^{29} - 1)$,
`builtinIntegerToByteString` fails. In this case, the resulting error message
must specify _at least_ the following information:

* That `builtinIntegerToByteString` failed due to an invalid length argument;
  and
* What `BuiltinInteger` was passed as the length argument.

If the input is `0`, `builtinIntegerToByteString` returns the
`BuiltinByteString` consisting of a number of zero bytes equal to the length
argument.

If the input is positive, and the length argument is also positive, let `d` be
the minimum number of digits required to represent the input (as per the
representation described above). If `d` is greater than the length argument,
`builtinIntegerToByteString` fails. In this case, the resulting error message
must specify _at least_ the following information: 

* That `builtinIntegerToByteString` failed due to the requested length being
  insufficient for the input;
* What `BuiltinInteger` was passed as the length argument; and
* What `BuiltinInteger` was passed as the input.

If `d` is equal to, or greater, than the length argument,
`builtinIntegerToByteString` returns the `BuiltinByteString` encoding the input.
This will be the most-significant-first encoding if the endianness argument is
`True`, or the most-significant-last encoding if the endianness argument is
`False`. The resulting `BuiltinByteString` will be padded to the length
specified by the padding argument if necessary. 

If the input is positive, and the length argument is zero,
`builtinIntegerToByteString` returns the `BuiltinByteString` encoding the input.
Its length will be minimal (that is, no padding will be done). If the endianness
argument is `True`, the result will use the most-significant-first encoding, and
if the endianness argument is `False`, the result will use the
most-significant-last encoding.

We give some examples of the intended behaviour of `builtinIntegerToByteString`
below:

```haskell
 -- fails due to negative input
builtinIntegerToByteString False 0 (-1) -- => ERROR
-- endianness argument doesn't affect this case
builtinIntegerToByteString True 0 (-1) -- => ERROR
-- length argument doesn't affect this case
builtinIntegerToByteString False 100 (-1) -- => ERROR
-- zero case, no padding
builtinIntegerToByteString False 0 0 -- => []
-- endianness argument doesn't affect this case
builtinIntegerToByteString True 0 0 -- => []
-- length argument adds more zeroes, but endianness doesn't matter
builtinIntegerToByteString False 5 0 -- => [ 0x00, 0x00, 0x00, 0x00, 0x00 ]
builtinIntegerToByteString True 5 0 -- => [ 0x00, 0x00, 0x00, 0x00, 0x00 ]
-- length argument too large (2^29)
builtinIntegerToByteString False 536870912 0 -- => ERROR
-- endianness doesn't affect this case
builtinIntegerToByteString True 536870912 0 -- => ERROR
-- fails due to insufficient digits (404 needs 2)
builtinIntegerToByteString False 1 404 -- => ERROR
-- endianness argument doesn't affect this case
builtinIntegerToByteString True 1 404 -- => ERROR
-- zero length argument is exactly the same as requesting exactly the right
-- digit count
builtinIntegerToByteString False 2 404 -- => [ 0x94, 0x01 ] 
builtinIntegerToByteString False 0 404 -- => [ 0x94, 0x01 ]
-- switching endianness argument reverses the result
builtinIntegerToByteString True 2 404 -- => [ 0x01, 0x94 ]
builtinIntegerToByteString True 0 404 -- => [ 0x01, 0x94 ]
-- padding for most-significant-last goes at the end
builtinIntegerToByteString False 5 404 -- => [ 0x94, 0x01, 0x00, 0x00, 0x00 ]
-- padding for most-significant-first goes at the start
builtinIntegerToByteString True 5 404 -- => [ 0x00, 0x00, 0x00, 0x01, 0x94 ]
```

We also describe properties that any implementation of `builtinIntegerToByteString` must
have. Throughout, `q` is not negative, `p` is positive, `d` is in the closed
interval $(0, 2^{29} - 1)$, `k` is in the closed interval $(1, 2^{29} - 1)$, 
`0 <= j < k`, and `1 <= r <= 255`. We also define `singleton x = consByteString
x emptyByteString`.

1. `lengthOfByteString (builtinIntegerToByteString e d 0) = d`
2. `indexByteString (builtinIntegerToByteString e k 0) j = 0`
3. `lengthOfByteString (builtinIntegerToByteString e 0 p) > 0`
4. `builtinIntegerToByteString False 0 (multiplyInteger p 256) = consByteString 0
   (builtinIntegerToByteString False 0 p)`
5. `builtinIntegerToByteString True 0 (multiplyInteger p 256) = appendByteString
   (builtinIntegerToByteString True 0 p) (singleton 0)`
6. `builtinIntegerToByteString False 0 (plusInteger (multiplyInteger q 256) r) =
   appendByteString (builtinIntegerToByteString False 0 r)`
   (builtinIntegerToByteString False 0 q)`
7. `builtinIntegerToByteString True 0 (plusInteger (multiplyInteger q 256) r) =
   appendByteString (builtinIntegerToByteString False 0 q)
   (builtinIntegerToByteString False 0 r)`

### `builtinByteStringToInteger`

The `builtinByteStringToInteger` primitive takes two arguments. We specify, and
name, these below:

1. Whether the input uses the most-significant-first encoding. This is the
   _stated endianness argument_, which has type `BuiltinBool`.
2. The `BuiltinByteString` to convert. This is the _input_.

If the input is the empty `BuiltinByteString`, `builtinByteStringToInteger`
returns 0. If the input is non-empty, `builtinByteStringToInteger` produces the
`BuiltinInteger` encoded by the input. The encoding is treated as
most-significant-first if the stated endianness argument is `True`, and
most-significant-last if the stated endianness argument is `False`. The input
encoding may be padded or not.

We give some examples of the intended behaviour of `builtinByteStringToInteger`
below:

```haskell
-- empty input gives zero
builtinByteStringToInteger False emptyByteString => 0
-- stated endianness argument doesn't affect this case
builtinByteStringToInteger True emptyByteString => 0
-- if all the bytes are the same, stated endianness argument doesn't matter
builtinByteStringToInteger False (consByteString 0x01 (consByteString 0x01
emptyByteString) -- => 257
builtinByteStringToInteger True (consByteString 0x01 (consByteString 0x01
emptyByteString) -- => 257
-- most-significant-first padding is at the start
builtinByteStringToInteger True (consByteString 0x00 (consByteString 0x01
(consByteString 0x01 emptyByteString))) -- => 257
builtinByteStringToInteger False (consByteString 0x00 (consByteString 0x01
(consByteString 0x01 emptyByteString))) -- => 65792
-- most-significant-last padding is at the end
builtinByteStringToInteger False (consByteString 0x01 (consByteString 0x01
(consByteString 0x00 emptyByteString) -- => 257
builtinByteStringToInteger True (consByteString 0x01 (consByteString 0x01
(consByteString 0x00 emptyByteString) -- => 65792
```

We also describe properties that any `builtinByteStringToInteger` implementation 
must have. Throughout, `q` is not negative and `0 <= w8 <= 255`.

1. `builtinByteStringToInteger b (builtinIntegerToByteString b 0 q) = q`
2. `builtinByteStringToInteger b (consByteString w8 emptyByteString) = w8`
3. `builtinIntegerToByteString b (lengthOfByteString bs) (builtinByteStringToInteger b bs) =
   bs`

## Rationale: how does this CIP achieve its goals?

We believe that these operations address both of the described cases well, while
also meeting the goals stated at the start of this CIP. Our specified primitives
address both the problems of endianness and padding specified in Case 2, while
also ensuring that use cases like Case 1 (where bounding length isn't important)
are not made more difficult than necessary. The representation we have chosen is
metadata-free, doesn't depend on any representation choices (current or future)
of `BuiltinInteger`, while also being flexible enough to satisfy both cases
where endianness and padding matter, and when they don't.

### Alternative possibilities

As part of this proposal, we considered two alternative possibilities:

1. Use the [CIP-0058][cip-0058] versions of these operations; and
2. Have a uniform treatment of the length argument for
   `builtinIntegerToByteString` (always minimum or always maximum).

[CIP-0058][cip-0058] defines a sizeable collection of bitwise primitive
operations for Plutus Core, mostly for use over `BuiltinByteString`s. As part of
these, it also defines conversion functions similar to
`builtinIntegerToByteString` and `builtinByteStringToInteger`, which are named
`integerToByteString` and `byteStringToInteger` respectively. Unlike the
operations specified in this CIP, the CIP-0058 operations do not address the
problems of either padding or endianness: more precisely, the representations
constructed are always minimally-sized, and use a big-endian encoding. While in
the context they are being presented in, these choices are defensible, they do
not adequately address Case 2, and in
particular, many cryptographic constructions used with finite fields. Users of
the CIP-0058 primitives who needed to ensure a minimum length of a converted
`BuiltinInteger` would have to pad manually, which CIP-0058 gives no additional
support for; additionally, if a little-endian representation was required, the
`BuiltinByteString` result would have to be reversed, which has quadratic cost
if using only Plutus Core primitives. Thus, we consider these implementations to
be a good attempt, but not suited to even their intended use, much less more
general applications.

An alternative possibility for the length argument of
`builtinIntegerToByteString` would be to treat the argument as either a minimum,
or a maximum, rather than our more hybrid approach. Specifically, for any input
`i`, let `d` be the minimum number of digits required to represent `i` as per
the description of our representation, and let `k` be the length argument.
Then:

* The _minimum length argument_ approach would produce a result of size 
  $\min \\{ \texttt{d}, \texttt{k} \\}$; that is, if the length argument is
  smaller than the minimum required digits, the minimum would be used instead.
* The _maximum length argument_ approach would produce a result of size `k`,
  and would error if $\texttt{d} > \texttt{k}$.

Both the minimum length argument, and the maximum length argument, approaches
have merits. The maximum length argument approach in particular is useful for Case 2:
in such a setting, we already know the maximum size of
any element's representation, and if we somehow ended up with a larger
representation than this, it would be a mistake, which the maximum length
argument would catch immediately. For the minimum length argument approach, the
advantage would be more for Case 1: where the length of the
representation is not known (and the user isn't particularly concerned anyway).
In such a situation, the user could pass any argument and know that the
conversion would still work.

However, both of these approaches have disadvantages as well. The minimum
length argument approach would be more tedious to use with Case 2, as each 
conversion would require a size check of the resulting
`BuiltinByteString`. While this is not expensive, it is annoying, and given the
complexity of the constructions that would be built atop of any finite field
implementations, it feels unreasonable to require this from users. Likewise, the
maximum length argument approach is unreasonable for situations like Case 1: the only
way to establish how many digits would be required involves performing an
integer logarithm in base 256, which is inefficient and error-prone. Our hybrid
approach gives the benefits of both the minimum length argument and maximum
length argument approaches, without the downsides of either: we observe that,
for situations like Case 1, the length argument would be `0` in practically all
cases, which is a value that would not be useful in any situation where the maximum 
length argument approach would be used. This observation allows our approach to work 
equally well for both Case 1 and 2, with minimal friction.

## Path to Active

### Acceptance Criteria

We consider the following criteria to be essential for acceptance:

* A proof-of-concept implementation of the operation specified here must exist,
  outside of the Plutus source tree. The implementation must be in Haskell.
* The proof-of-concept implementation must have tests, demonstrating that it
  behaves as the specification requires, and that the representations it
  produces match the described representation in this CIP.
* The proof-of-concept implementation must demonstrate that it will successfully
  build, and pass its tests, using all GHC versions currently usable to build
  Plutus (8.10, 9.2 and 9.6 at the time of writing), across all [Tier 1][tier-1]
  platforms.

Ideally, the implementation should also demonstrate its performance
characteristics by well-designed benchmarks.

[tier-1]: https://gitlab.haskell.org/ghc/ghc/-/wikis/platforms#tier-1-platforms

### Implementation Plan

MLabs have completed the implementation of the proof of concept as required
(located [here](https://github.com/mlabs-haskell/plutus-integer-bytestring).
This implementation has been merged into Plutus Core, and will be released in
the upcoming V3 release.

## Copyright

This CIP is licensed under the [Apache-2.0][Apache-2.0] license.

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
