---
CPS: ????
Title: PostQuantum resistance and migration
Category: Ledger
Authors:
  - Michał J. Gajda (mjgajda@migamake.com)
Discussions-To:
  - https://github.com/cardano-foundation/CIPs/pull/441
Comments-Summary: 
Comments-URI: https://github.com/cardano-foundation/CIPs/issues/441
Status: Open
Proposed Solutions: CIP-???? Post-quantum signatures in Plutus and native wallets
Discussions:
  - https://github.com/cardano-foundation/CIPs/issues/413
  - https://github.com/cardano-foundation/CIPs/issues/441
Created: 2023-03-03
License: Apache-2.0
Proposed Solutions: Opt-in PostQuantum signatures in Plutus and native wallets
---

# Abstract

Rapid and ramping up progress of quantum computing threatens safety of traditional
cryptographic protocols like Ed25519 and SHA256 used in Cardano blockchain.
While migration of a blockchain itself within a single year is imaginable,
migration of user wallets and smart contracts will certainly take much longer.
We should prepare by allowing gradual, opt-in migration of wallets and smart contracts
well in advance.

# Problem

NIST estimates that pre-quantum cryptographic algorithms may be no longer safe
by 2035. However, the smart contracts have long development and lifetime,
so migration to post-quantum cryptography algorithms should start several
years before they would become insecure.
This summer NIST has selected three PQC signature algorithms
for standardization. This includes publishing their reference implementations,
and finishing initial comment period.

NIST plans to finalize standardization in 2023/2024 time frame, with US executive branch recommending
all projects to plan for post-quantum resistance by mid-2023.

[IBM has a goal of 4000-qbit processor by 2025](https://research.ibm.com/blog/ibm-quantum-roadmap-2025), while a group of researchers
claimed that [372 physical qbits may be sufficient](https://arxiv.org/pdf/2212.12372.pdf) with few thousand layers to break RSA2048.
If confirmed, then an existing [400-qbit](https://newsroom.ibm.com/2022-11-09-IBM-Unveils-400-Qubit-Plus-Quantum-Processor-and-Next-Generation-IBM-Quantum-System-Two) quantum processor could break the RSA2048 using [IBM public quantum computing service](https://quantum-computing.ibm.com/) **this year**.

# Use cases

Adding multiple PQC signature algorithms will allow the following:

* opt-in migration of wallets and smart contracts to safer cryptographic protocol
* pay-as-you-go for longer signatures required for post-quantum resistance
* opt-in resistance to _cryptocalypse_ - surprise breakage of a single major encryption algorithm -
  by using multiple signature algorithms for redundancy.
* compliance with US government regulations past July 2023, when all agencies
  are expected to plan post-quantum migration.
* allow fast migration of entire blockchain to post-quantum resistance when it becomes necessary.
* [Long-term document storage](https://adastamp.co) is a killer application for the blockchain.
  While any single signature may be obsoleted, this application adds new signatures for each document
  that keep integrity of the document and prolong its validity.
  This requires a single dApp that will be able to support multiple signature algorithms,
  ideally extensible to future signature algorithms.

Supporting PQC signatures will bring the following benefits:

* smart contracts may use future standard algorithms today;
* early support for PQC will simplify future PQC migration, if needed;
* future PQC migration would be smooth and require less changes;
* support for PQC may increase industry acceptance for long running projects;
* users that want their wallets to survive over ten years may
  use smart contracts verifying multiple algorithms today;
* Cardano will become first blockchain to verify PQC standard signatures,
  thus getting first-mover advantage.

# Open questions

* While three PQC algorithms were selected for standardization,
  they all have rather large storage requirements.
  It is unknown whether and when will there be a standardized or even just trustworthy
  post-quantum resistance signature algorithm that would require less than 600 bytes
  of storage per signature.

* It may be contentious whether resistance to black swan event
  like _cryptocalypse_ justifies including three different PQC algorithms at the moment.
  Maybe including just Falcon (600 bytes per signature), and leaving the list extensible
  is a better option.

* While cryptographers expect [SHA-384](https://cryptobook.nakov.com/quantum-safe-cryptography#quantum-safe-and-quantum-broken-crypto-algorithms) will ultimately needed for post-quantum resistance,
  it is hard to estimate when it would happen. At the moment single SHA-256
  hash algorithm is deemed sufficient [for a very long time](https://cryptobook.nakov.com/quantum-safe-cryptography#quantum-safe-and-quantum-broken-crypto-algorithms).
  It is open question, whether seamless of both signatures will suffice
  for _full quantum resistance_ in the long term.

* Cardano Ledger specialists would have to confirm that upgrade of signature
  and hash protocol suffices for full quantum resistance.

* Status of the proposed zero-knowledge protocol extensions to Cardano
  and their resistance to post-quantum attacks
  is unknown. In absence of the mathematical proof it remains doubtful.

* It is unknown when exactly post-quantum computing will break pre-existing
  cryptography, altough [researchers made bold claim](https://arxiv.org/pdf/2212.12372.pdf)
  about 372 qubits being sufficient to break RSA2048. This hybrid algorithm
  could efficiently use an existing quantum computer, but would
  [take a long time](https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/AkfdRQS4yoY/m/3plDftUEAgAJ).

# Goals

* Prepare Cardano for migration to post-quantum encryption algorithms.
* Make any cryptographic migrations easy in the future.
* Allow creating post-quantum resistant smart contracts today.

# Copyright

This CPS is licensed under Apache-2.0.
