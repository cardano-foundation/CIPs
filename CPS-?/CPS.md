---
CPS: TBD
Title: Post-quantum signatures
Category: Plutus
Status: Open
Authors: Koz Ross <koz@mlabs.city>
Proposed Solutions: []
Discussions: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-01-39
License: Apache-2.0
---

## Abstract

Post-quantum cryptography, specifically with regard to digital signatures, is
important at all levels of the Cardano chain, including for script and dApp
developers. There is no current way to do this short of implementing such
functionality yourself, which is difficult, inefficient and risky. This is in
contrast to pre-quantum signature schemes, which exist as easy-to-use and
efficient builtins.

## Problem

[Quantum computing][quantum-computing] is a realizable approach to computation
that threatens to turn a lot of existing security-oriented algorithms on their
heads. In particular, the existence of [Shor's algorithm][shors-algorithm] means
that a quantum computer with sufficient resources could break any existing
cryptographic scheme that relies on integer factorization or discrete logarithms 
for its hardness. As many currently-used public-key cryptography systems rely on
the hardness of one of these problems, this is a looming concern. In the world
of blockchain, concerns over quantum computing are also being taken seriously: 
the Ethereum Foundation has elevated post-quantum
security to a [top strategic priority][ethereum-top-priority] this year, and
Algorand have [been taking proactive steps][algorand-steps] around post-quantum 
security since at least 2022. In the Cardano ecosystem, The Intersect Product 
Committee's [Cardano 2030 Strategic Framework][2030-strategic-framework]
describes 'post-quantum readiness' as a focus area for security and resilience.

The number of problems posed by the looming arrival of quantum computing is
large, and covers many areas relating to the operation of a blockchain: a single
CPS could not possibly cover them all. Thus, we examine a specific problem, in a
specific context, which can be scoped precisely. One particular area affected
strongly by quantum computing breaking several previously-hard problems are
_digital signatures_, for which specific primitive operations exist on Cardano.
Currently, script developers have access to builtin operations verifying
signatures using the following schemes:

* Edwards-curve digital signature algorithm over the Ed25519 elliptic curve; 
* Edwards-curve digital signature algorithm over the SECP256k1 elliptic curve;
  and
* Schnorr signatures over the SECP256k1 elliptic curve.

Practical quantum computing using Shor's algorithm would render all of these
insecure. This is a significant issue for script and dApp developers who want to
future-proof the security of their work. While extensions such as CIPs
[121][cip-121], [122][cip-122] and [123][cip-123] make implementing the logic of
a different signature verification possible, as shown by projects such as
[Grumplestiltskin][grumplestiltskin] and the [SHA512 hashing][plutus-sha512] and
[Ed25519 verification][plutus-ed25519] benchmarks in Plutus, even implementing
the underlying primitives to support such schemes is a challenging task in
itself, before we consider performance and the old adage about not 'rolling your
own crypto'. 

Part of the efforts to make Cardano 'post-quantum ready' must extend such
capabilities to developers of scripts and dApps to be meaningful. Currently, no
such possibilities exist in a practically usable way.

## Use cases

The chief use case today for such capabilities are script or dApp developers
whose work currently relies on digital signatures. A good example of this would
be an auction system, where bids are signed by the bidders. Concretely, consider
the following validator code snippet:

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

The snippet uses `verifyEd25519Signature` to check signatures on bids. If a dApp
developer wanted to make this future-proof against quantum computing attacks
against the security of these signatures, they currently have no way of doing
this short of implementing it themselves, with all the downsides previously
talked about. Even if they had the skills and time to implement a different
signature scheme verification as part of their script, it would be much less
efficient than a single builtin call, to say nothing of the security
implications.

Another important use case is that, in the event of a quantum breakthrough,
post-quantum smart-contract-driven wallets can secure Cardano without having to
modify the ledger directly. While this is very much a worst-case scenario,
having this possibility available would be an additional layer of defence
against quantum computing compromising the chain. Post-quantum digital
signatures would be required to make this possible, and having such builtins
would allow it to be implemented easily if the need ever arose.

## Goals

Ultimately, the goal would be to make one (or possibly several) post-quantum
signature schemes available to dApp developers as UPLC builtins, similar to the
existing builtins for pre-quantum schemes. These should be chosen carefully, as
the space of post-quantum digital signature schemes has received much less
scrutiny than the pre-quantum schemes they are going to replace. At minimum, the
following criteria must be considered:

* Proofs or guarantees of their security. Being reviewed as part of a NIST
  process, or having some published proofs or demonstrations of the scheme's
  security would be a significant factor.
* The existence of a reference implementation that can be integrated into
  `cardano-base` (a necessary requirement for builtins doing digital
  signatures).
* Size of signature and verification key representations.
* Time required to verify a signature.
* Existing adoption (including by other chains in case of interoperability
  requirements in the future).

## Open Questions

The biggest open question is precisely _which_ scheme should be chosen for the
non-trivial effort involved in introducing it as a builtin. A whole
constellation of different solutions exist, and more are being worked on,
relying on different problems for their hardness, and with a whole range of
tradeoffs and implementations. It is quite likely that no single scheme will be
ideal relative all the criteria given in the Goals section, and some of these
criteria are quite speculative. It is likely that a non-trivial research effort
will be required prior to this choice being made, if only to present sufficient
evidence for the choice.

A related question to the above is whether it might be worthwhile to have
_multiple_ schemes available. Currently, there are builtins covering three
different pre-quantum schemes (although two are variants on the same curve),
which suggests that doing something similar for post-quantum signature
verification may be a good idea. This could help 'cover our bases' regarding
questions of performance and existing adoption, but would magnify all of the
effort involved in getting usable builtins, starting with the research step and
ending with costing and implementation. A related concern is that of educating
dApp and script developers about the benefits, and drawbacks, of each scheme in
such a case, as these are not likely to be clear to someone who isn't a
cryptography expert.

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[quantum-computing]: https://en.wikipedia.org/wiki/Quantum_computing
[shors-algorithm]: https://en.wikipedia.org/wiki/Shor%27s_algorithm
[post-quantum-cryptography]: https://en.wikipedia.org/wiki/Post-quantum_cryptography
[ethereum-top-priority]: https://thequantuminsider.com/2026/01/26/ethereum-foundation-elevates-post-quantum-security-to-top-strategic-priority/
[algorand-steps]: https://thequantuminsider.com/2026/01/26/ethereum-foundation-elevates-post-quantum-security-to-top-strategic-priority/
[cip-121]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0121
[cip-122]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0122
[cip-123]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0123
[grumplestiltskin]: https://github.com/mlabs-haskell/grumplestiltskin/tree/milestone-2
[plutus-sha512]: https://github.com/IntersectMBO/plutus/blob/master/plutus-benchmark/bitwise/src/PlutusBenchmark/SHA512.hs
[plutus-ed25519]: https://github.com/IntersectMBO/plutus/blob/master/plutus-benchmark/bitwise/src/PlutusBenchmark/Ed25519.hs
