# Two coordinated proposals for CIP-editor discussion

Both changes are drafted on `cip/extended-blueprints-verification` in the CIPs
fork. No new CIP number or published schema identifier is assumed.

| Concern | Owning proposal |
| --- | --- |
| Stable validator identity and complete invocation interface | [CIP-57 extension draft](../CIP-0057/extensions/compiled-interface) |
| Data/native distinction and an explicitly defined Scott representation | CIP-57 extension draft |
| Claims, assumptions, formal fragments and evidence | [Assurance proposal](./README.md) |
| Selected semantics, resource bounds, acceptance interpretation and pinned checking environment | Assurance checking context |
| Concrete parameter applications, resulting script hash and use of a universal parameter theorem | Assurance checking context, using the blueprint's encoding definitions |

## Proposed placement

Keep the active CIP-57 schema unchanged and review the interface extension under
its own draft dialect. Editors can choose whether to incorporate it into a future
CIP-57 revision or assign a companion CIP number. The main CIP-57 README links to
the draft so both changes are reviewable together.

The assurance envelope remains detached and useful with legacy blueprints. The
new executable profile needs the richer interface. It uses `assurance-v2.json`
because a checking context affects a statement's meaning and must not be silently
ignored by a legacy executable consumer. The earlier, unpublished schema and
verified UAL 0.5 example are retained as prototype compatibility fixtures.

## Decisions to review

1. **Dialect ownership and naming.** Amend CIP-57 or assign a companion CIP? Which
   versioned schema/vocabulary identifiers should be published?
2. **Representation syntax.** This draft puts `#scott` in the parameter schema
   and references parameters from invocations. It avoids an encoding flag that
   contradicts an existing `integer` or `#integer` wire schema.
3. **Scott conventions.** The proposed `scott-cbv-v1` delays all branch handlers.
   Agree exact behavior and vectors with compiler maintainers; existing encoders
   with different conventions must use different profiles.
4. **Ledger conventions.** Review purpose coverage, V1/V2/V3 context mapping,
   parameter order and return-value rules with ledger maintainers.
5. **Scope of the first implementation.** Data/native support and universal
   parameters can ship before Scott or concrete deployment checking. Consumers
   must explicitly refuse unsupported features, not silently narrow claims.
6. **Checking contexts.** Confirm separation of step bounds from ledger budgets,
   protocol/cost-model pinning, raw-byte context hashes and applied-script binding.

## What is demonstrated here

The new game example preserves the previously compiled game bytes and recomputes
its blueprint-document binding after migrating the metadata. It carries no
verification evidence: its environment is illustrative. The UAL 0.6-draft
implementation requires a freshly captured environment and currently supports the
Data/native, universal-parameter, CEK-step subset of this draft. The old game example and the previously completed
verification remain separate.

Schemas, examples and selected semantic constraints can be checked locally with:

```sh
python3 -m unittest discover -s CIP-XXXX/tests -p 'test_interface_drafts.py' -v
```

The tests use Python's `jsonschema` package and resolve schemas locally without
network access. They validate metadata, not a proof or the compiler's encoding.


Library functions are assurance targets, not blueprint validators. Their code,
ordered input schemas and result schema live in assurance-v2 `functions`.
CIP-57 remains the ledger-facing interface; the only shared piece is the wire
schema vocabulary. No new CIP-57 functions collection is proposed.
