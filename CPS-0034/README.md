---
CPS: 34
Title: Extending Plutus Core conformance testing 
Category: Plutus
Status: Open
Authors:
    - Kenneth MacKenzie <kenneth.mackenzie@iohk.io>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1244
Created: 2026-08-06
License: Apache-2.0
---

## Abstract

For Cardano's node diversity, it is vital that the Plutus Core evaluators in all
node implementations produce identical results. The current
[`plutus-conformance`](https://github.com/IntersectMBO/plutus/tree/master/plutus-conformance)
test suite gives external implementers a fixed collection of about 1000
golden-file test cases, but they don't include any of the property-based tests
the Plutus team uses internally. The suite also only tests against the latest
protocol version and language version. This CPS asks the community to agree on a
way to expose property tests and tests for older protocol versions/language
versions to external implementers with minimal integration effort on their part.
IOG's Plutus team will produce a design document informed by feedback on the CPS
and will then implement the design and make the resulting tool available to the
community.


## Problem

Cardano's security and resilience benefit from having more than one independent
node implementation so that no single codebase or team is a single point of
failure for the network. This is only safe if all implementations agree
precisely on the result (and cost) of evaluating a Plutus Core script: any
divergence is dangerous because a fork could occur if nodes disagree on the
validity of a block.

We currently provide a number of conformance tests in the `plutus-conformance`
directory in the Plutus repository which implementers can use to check that their
evaluator behaves properly. These are simple hand-written unit tests which check
that scripts succeed with expected results in typical cases, and that specific
edge conditions are handled correctly.  The tests are useful but limited in
number and in the range of inputs they exercise.

The Haskell codebase contains many property tests that generate large numbers
(hundreds or thousands) of carefully-distributed random inputs, build Plutus
scripts from them, and check that evaluating those scripts on the reference CEK
machine produces the expected outcome.  These significantly increase confidence
in the correctness of the implementation but are not portable: there is
currently no way for someone implementing Plutus Core independently to run the
tests against their own evaluator instead of ours.

We want external clients to be able to consume these tests using their own tools
with as little integration work as possible on their part. This raises
implementation questions that are the core subject of this CPS: how the
generated test cases and expected outcomes should be packaged and transmitted,
and how failures should be reported back with enough detail (test name, inputs,
expected vs. actual) to be actionable.

Another issue is that the result of evaluating a script can depend on a number
of parameters which change occasionally (including the protocol version, ledger
language version, and cost model: see Section 4 of the [Plutus Core
specification](https://github.com/IntersectMBO/plutus/tree/master/doc/plutus-core-spec)).
We will call a particular set of such things a "version combination".  The
current conformance tests only test the most recent version combination: the
extended conformance tests should provide comprehensive coverage of all
combinations to ensure that the history of the chain can be replayed correctly.

## Use Cases

* **Implementers of alternative Plutus Core evaluators** want to be confident,
    beyond a small fixed set of golden files, that their evaluator agrees with
    the reference evaluator across a wide, randomly-generated range of programs
    and inputs without having to reimplement IOG's QuickCheck/Hedgehog
    generators from scratch or read Haskell source to understand what is being
    tested.

* **A team building or maintaining an alternative Cardano node implementation**
    needs an ongoing, low-friction way to check that its Plutus evaluator stays
    in agreement with the reference implementation as Plutus evolves, not just a
    one-off check at initial release. Since a consensus-relevant disagreement
    between node implementations is a safety issue, this class of user has a
    particularly strong need for broad, repeatable, easily-integrated
    conformance checks.

* **A maintainer of an independent evaluator** wants a clear, actionable failure
    report when their implementation diverges from the reference: which test
    failed, what inputs were used, what result was expected, and what their
    evaluator actually produced.

* **Someone auditing conformance for a specific ledger era** may want to select
    or filter the available tests down to the relevant version combination
    rather than running the entire suite.

## Goals

We intend to implement a Haskell program which generates test cases and provides
them to external clients. There are a number of design goals which should be
fulfilled to maximise the usefulness of the tool:

1. It should use a portable representation of generated conformance test cases
(the program, the inputs, the expected outcome, and optionally the expected
execution budget) that can easily be consumed by clients.  Enough information
should be provided for any failures to be easily diagnosed.

2. The implementation burden placed on client tools should be minimised as far
as possible.

3. It should be possible to run large numbers of generated tests (potentially
many thousands) efficiently, without prohibitive slowdown from process-spawning,
I/O, or serialisation overhead.

4. The tests should be organised systematically and we should provide some way
for users to select particular tests or groups of tests.

5. Test generation and/or selection should be extended to cover different version
combinations to support clients replaying chain history.

Non-goals:

* Replacing the existing golden-file suite in `plutus-conformance`, which
  remains useful for simple, human-readable regression tests.

* Mandating a single client-side testing framework or language; the goal is a
  distribution/interchange mechanism that any client can consume with reasonable
  effort, not a specific client-side implementation.

## Open Questions

There are a number of design decisions that should be made before beginning
implementation.  We are keen to receive feedback on these (especially the first
one) from potential users in the Cardano community.  Our initial aim is to
produce a design document agreed upon by interested parties.

* How should generated test cases and expected results be transmitted to a
  client?  Here are some preliminary suggestions with different tradeoffs between
  implementation effort, speed, and diagnostic quality:

   1. Write large numbers of individual files (programs and expected results) to
   disk for the client to consume at its own pace. This approach would need little
   effort on the part of clients since the test cases could be consumed in the
   same way as the current conformance scripts, but it would potentially be slow
   to generate large numbers of files and awkward for consumers to manage them.

   2. Emit a stream of `flat`-encoded programs (and associated data) on stdout,
   in one of two variants:

      - The client sends its evaluation results back on stdin so that our tooling
        performs the comparison against expected results itself. This allows rich,
        centralised failure reporting (test names, offending inputs), but may be
        slow due to the round trip, and requires the client to speak a two-way
        protocol.

      - The expected result (and possibly the expected budget) is emitted
        alongside each program so the client checks its own output. This requires
        more work by the client and would require an accompanying description
        format providing enough information for the client to produce useful
        diagnostics for failing tests.

   3. Have the client supply a way of invoking their evaluator (e.g. a shell
   command) so our tooling can drive it directly and report failures itself. This
   would likely require spawning a new process per invocation, which might not
   scale well to large numbers of test cases.

   4. Generate self-checking UPLC scripts that run a test over a list of
   inputs and perform the comparison of actual/expected output in UPLC itself,
   avoiding any external protocol. This is appealing for scalability but may be
   difficult or infeasible for tests whose comparison logic is hard to express
   directly in UPLC, and may not generalise to all existing property tests.

   These options are not mutually exclusive: for instance, a stream of
   `flat`-encoded files on `stdout` (option 2) could be captured and written to
   disk to additionally support the simple file-based workflow (option 1).

* If a description format is needed for programs, inputs, and expected outcomes
  to support useful client-side diagnostics, what should it look like?

* How should test generation and/or selection be organised across the version
  combinations? Should distinct test collections be produced per combination,
  should tests be tagged with the combinations they apply to, or should
  generation itself be parameterised by the combination under test?

* What hierarchical or filtering structure, if any, should be offered so that
  clients can list or select subsets of tests (e.g. by category, or by version
  combination) rather than always running the full suite?

* What are the acceptable bounds on execution time and resource usage for a
  client running the full generated suite, and how do the candidate transmission
  mechanisms compare against those bounds in practice?

* Can we provide a simple way for third parties to contribute their own test
  cases to the main Plutus repository?


## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
