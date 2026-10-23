# Draft checking profile: UPLC step check v1

Proposed identifier:
`https://cips.cardano.org/cips/cipXXXX/profiles/uplc-step-check/v1`.
This is an editor-discussion draft. The UAL 0.6-draft implementation supports
Data/native schemas, universal or fully applied parameters and evaluation under CEK step bounds.
Scott and ledger-cost checking are explicit
unsupported cases. The illustrative CIP examples need a freshly captured checking
environment before execution; the legacy UAL 0.5 format remains separate.

A checking run MUST perform the following steps before reporting a result:

1. Recognize the assurance-v2 and compiled-interface dialects and this profile.
   An unknown dialect/profile/encoding is **not checked**. Do not infer support
   from successful structural JSON validation.
2. Validate the documents, ids, fragment graph, interface references and complete
   invocation lists. Resolve local artifact URIs relative to their containing
   document. Verify all used artifact digests and the blueprint digest.
3. Recompute every scoped template hash from compiled bytes and the language tag.
   Verify that each target's declared invocation matches its language/purpose.
4. Load the digest-bound environment. It must pin the checker, compiler provenance,
   evaluator, builtin/cryptographic models, libraries, solver and solver options,
   including local patches. An illustrative or incomplete environment does not
   authorize execution. Do not trust an unpinned default namespace or dependency.
5. Accept only `execution.budget.kind: "cek-steps"` and
   `execution.acceptance: "evaluation"` in this profile. The explicit semantics
   variant is passed to the pinned evaluator. No conversion to ledger units is
   defined. A profile supporting ledger-script acceptance requires the separate
   protocol, cost-model and result checks specified in the parent proposal.
6. For universal parameters, import a wrapper whose ordered binders represent all
   unapplied parameters followed by the invocation's runtime arguments. The formal
   property must quantify over the parameters and contain all domain premises.
   The wrapper encodes each parameter according to its referenced schema: Data,
   native UPLC values and versioned Scott terms remain distinct. Runtime inputs
   are raw Data; a narrower well-formedness domain must be an explicit premise.
7. For applied parameters, verify each term artifact digest. Decode a single Flat
   UPLC term with no trailing bytes; terms must be closed values under the chosen
   encoding profile. Establish their encoding/schema premises. Apply every term
   to the template in order. Decode the digest-bound `appliedScript` artifact using
   the blueprint convention, require its AST to equal that exact application,
   and verify `appliedScriptHash` against the artifact bytes. Use that program
   for the property, with only runtime arguments remaining in its wrapper.
   Failure to establish a required binding is not a successful check. This draft
   does not define a partial-application deployment record.
8. Elaborate only the property's declared fragment closure. Reject local axioms
   and admitted dependencies. Check that the proposition refers to every scoped
   compiled program, while recognizing that this cannot establish semantic
   relevance or rule out a vacuous proposition. Documentary assumptions are not
   silently injected as axioms.
9. Distinguish normal return, evaluation error and exhausted steps. A halted
   closure does not show that the listed complete invocation was supplied.
   Evaluation success in this profile is not a claim of ledger acceptance. In
   particular V3 ledger-script acceptance requires native unit. A counterexample
   caused by exhaustion refutes a bounded-termination claim, not a ledger safety
   claim about what the program would do with sufficient resources.
10. Run every executable claim afresh. Emit verified, falsified, inconclusive or
    not checked with the method and assumptions. Historical outcomes never choose
    the expected answer. Record exact input documents, tool revisions, settings,
    and logs in a digest-bound artifact. For selected contexts, include their raw
    byte digest as `checkingContextHash`; do not copy an old context digest onto
    a new result. Emit `smt-check` when trusting SMT translation/solver output
    without a reconstructed proof.

The environment and evidence artifacts must disclose the trust boundary. Source
elaboration can execute code; isolate third-party inputs and bound resources.
The metadata validation tests accompanying this draft do not implement any of
the theorem-checking, term-decoding or parameter-application steps above.

## Migration checklist

- Export `interface` and schema-preserving parameter encodings instead of the
  experimental `arguments` field.
- Export checking contexts instead of validator `budget` fields.
- Update the importer so `integer` and `#integer` remain different wire types,
  and support the canonical CIP-57 spellings `#bytes`, `#pair` and `#list`.
- Implement and test a Scott encoder only for the exact declared profile; reject
  unsupported profiles instead of coercing to Data.
- Bind UAL wrapper generation to a selected checking context and bump the UAL
  checking-profile version. The example's `0.6-draft` is not a released version.
- Extend the checker and evidence producer for context hashes and applied hashes.
- Preserve the old UAL 0.5 fixtures and their recorded verification results.

## Initial implementation environment binding

PlutusCoreBlaster captures `blaster-loaded-environment-v1` through
`#write_checking_environment`. Its manifest binds every imported `.olean`, the
Lean and Z3 executables, Lean version, solver timeout, heartbeat and recursion
settings. A driver loading native Blaster also supplies that library through
`ASSURANCE_NATIVE_LIBRARY`; the manifest hashes it. The driver must load that
same path with `--load-dynlib` for both capture and verification. The checker
recomputes that manifest before executing claims. Ledger-dependent drivers must
include their ledger-model imports when capturing and checking the environment.
The run artifact additionally records source revisions, local changes and generator
inputs. This concrete manifest describes executable checking inputs; it does not
claim to provide a hermetic operating-system image or source-build attestation.
The compiled game and Data/native parameter examples exercise this implementation.


## Function targets

Assurance-v2 also supports a `functions` registry and `scope.functions`.
Function targets select the registry id and require a matching SHA-256
`functionHash`. The checker validates every registry entry's actual single-CBOR
Flat bytes, wire schemas and digest, and rejects unknown targets, duplicate or
incomplete scope coverage and binding collisions. Function result schemas are
required. Guarded recursive Data schemas are supported; Scott and external schema
references remain unsupported. Alias-only cycles are rejected.

Generated `<id>` bindings run the actual function on the CEK machine and return
its state. `<id>_returns` compares that state with an exact halted constant in
the result encoding; it never conflates errors, exhausted fuel and values.
Data inputs and results remain raw Data; native values use the supported builtin
constant types. Schema refinements need explicit property premises. The checker
also requires each proposition to depend on every scoped compiled program;
this syntactic dependency test is not a proof of semantic relevance.

Environment capture and verification must import the same ledger/model modules.
The Auction example uses `CardanoLedgerApi.Examples.Auction`, with typed V3
context constructors adapted from upstream commit
`9938562fd452351655fe2f6b63e583c62422687c`. The verified scenarios are deliberately
bounded transaction shapes, not the entire upstream security audit or ledger
transaction validity. Separately compiled helper claims do not establish
compiler optimization equivalence.

Function checking targets also carry `functionInterface`, an exact copy of the
registry entry's `serialization`, `plutusVersion`, ordered `arguments` and
`result`, plus the assurance `definitions` registry. Omitted definitions mean
an empty registry. The checker requires equality. Together with `functionHash`, this
binds the bytes and their wire interpretation into `checkingContextHash`;
changing only an argument encoding cannot reuse the old context or evidence.

Recursive Data schemas retain their reference graph and use raw `Data` at the
checking boundary. Each cycle must cross a constructor field or container
element. This structural guard does not imply that the schema is inhabited;
properties with domain premises should include explicit satisfiability witnesses.
No fixed-depth schema expansion or implicit malformed-value exclusion is allowed.

Applied Data/native values support the structural schema forms, including guarded
recursive Data. Additional refinements such as numeric bounds currently produce
an explicit unsupported-constraint diagnostic; they are never silently assumed.
The producer API `writeInterfaceBundleWithBindings` records property-specific
bindings built by `compiledParameter` and `appliedParameters`.
