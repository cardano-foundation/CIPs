---
CIP: 194
Title: Plutus Core builtin `matchDataConstr`
Category: Plutus
Status: Proposed
Authors:
  - Seungheon Oh <seungheon.oh@iohk.io>
Implementors:
  - Seungheon Oh <seungheon.oh@iohk.io>
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1236
  - Recursive pattern-matching prototype PR: https://github.com/IntersectMBO/plutus/pull/7852
  - matchDataConstr implementation branch: https://github.com/SeungheonOh/plutus/tree/type-pattern-matchdata
Created: 2026-07-30
License: CC-BY-4.0
---

## Abstract

This proposal adds the builtin function `matchDataConstr` to Plutus Core. The builtin combines
`Data.Constr` tag selection, exact-arity checking, and selective field capture in one costed
operation:

```text
matchDataConstr
  : forall S.
    BuiltinRep matchDataConstr S
    -> data
    -> S
```

The first argument is an explicit, checked description of the accepted constructor tags, the
required field count for each tag, and the fields to retain. A successful call returns an existing
sum-of-products value. Its constructor is the compact position of the matched table entry, and its
arguments are exactly the selected `Data` fields in source order. Ordinary `Case` performs the
subsequent branch dispatch.

The runtime description is a `ByteString`. It is passed explicitly and remains after
type erasure. PLC adds a builtin-specific `BuiltinRep` type and checked `builtinrep` term so that
the typechecker can validate the bytes and index them by the result SOP type. Erasure retains the
same bytes as a UPLC constant.

## Motivation: Why is this CIP necessary?

Plutus contracts receive ledger inputs as `Data`. Known structures such as script contexts are
commonly encoded as nested `Data.Constr` values. Deconstructing one such value traditionally
requires calling `unConstrData`, inspecting the returned pair, comparing its constructor tag, and
traversing the field list to retain the fields needed by the continuation. The program must also
fail when the constructor or expected shape is wrong.

That sequence repeats evaluator, builtin-application, pair, list, and tag-comparison overhead at
each structural node. It also tends to serialize traversal code proportional to the number and
location of the selected fields.

Builtin `Case` does not solve this problem. `Case` can dispatch efficiently on an existing
`Constr` value, but a `Data.Constr` is an opaque builtin constant. Its runtime tag and field list
must first be decoded. Extending `Case` directly to all `Data` values would also leave a typed
arity problem: PLC cannot derive a branch result shape from the type `Data` alone.

`matchDataConstr` moves this operation behind one builtin boundary. It selects among explicitly
listed `Data.Constr` tags, checks the exact immediate field count, and scans one selector bit per
field. It retains the selected fields in a `VConstr`, which an existing `Case` term can dispatch.

The table determines the result SOP, so typed PLC must check the two together. `BuiltinRep`
performs that check while leaving the table as a runtime term.

## Specification

### Status of this specification

The builtin type, checked-representation rules, canonical table format, result construction,
capture order, exact-arity behavior, failure behavior, and erasure rules below are normative.

The numerical cost coefficients and benchmark results are pre-activation evidence. Final
coefficients must be generated from the final implementation using the standard builtin-costing
procedure and approved through the normal ledger cost-model process.

### Scope and type of change

This proposal appends `matchDataConstr` to `DefaultFun` and adds the PLC-only nominal type
`BuiltinRep matchDataConstr S` together with a checked `builtinrep` term containing a literal
builtin constant. It specifies the canonical `ByteString` representation, the UPLC runtime
behavior and costing shape, and activation through the existing protocol-version and cost-model
mechanisms.

The checking interface is general, but this CIP registers only the
`BuiltinRep matchDataConstr` family.

It does not add a PLC or UPLC `Match` term, a pattern AST, pattern-bound lexical variables,
recursive patterns, a recoverable default branch, or a new UPLC value form. It also does not
directly match `Data.List`, `Data.Map`, `Data.I`, or `Data.B`.

A compiler expresses nested matching using successive `matchDataConstr` calls and existing `Case`
terms. Existing builtins can inspect a selected field after `matchDataConstr` returns it.

### PLC interface

PLC assigns `matchDataConstr` the ordinary first-class polymorphic type:

$$
\mathsf{matchDataConstr}
  :
  \forall S:*.
  \mathsf{BuiltinRep}(\mathsf{matchDataConstr},S)
  \to \mathsf{data}
  \to S.
$$

A bare `matchDataConstr` is a valid builtin term. Its type does not depend on recognizing a
privileged application shape.

PLC gains a nominal, builtin-specific representation type:

```haskell
TyBuiltinRep
  ann
  BuiltinRepName
  (Type tyname uni ann)
```

`BuiltinRepName` is a nominal identifier for a representation family. For every family $\rho$
registered by the builtin interface, the general kinding rule is:

$$
\text{KIND-BUILTINREP}
\frac{
  \Gamma\vdash I::*
}{
  \Gamma\vdash
    \mathsf{BuiltinRep}(\rho,I)
    ::*
}.
$$

The nominal family defines the meaning of $I$. `matchDataConstr` uses its result SOP as the index;
another family may index a larger static contract.

A `BuiltinRepName` has no term-level constructor by itself. Terms of that type are introduced by
the representation checker registered for the name. This CIP registers `matchDataConstr`.

`BuiltinRep matchDataConstr S` is not a member of `DefaultUni`. It cannot classify an ordinary PLC or
UPLC constant, and it has no UPLC type counterpart. Keeping it outside `DefaultUni` prevents
ordinary builtin-type operations from manufacturing or eliminating a checked witness.

### Checked representation interface

PLC gains one general term that associates a builtin with one literal universe constant:

```haskell
BuiltinRep
  ann
  fun
  (Some (ValueOf uni))
```

Its general textual form is:

```lisp
(builtinrep <builtin-function> <constant-type> <constant-value>)
```

For example:

```lisp
(builtinrep matchDataConstr bytestring #...)
```

The payload is a literal universe constant, not a PLC term; evaluation and substitution do not
enter it. The builtin identity is part of the term, so two builtins cannot share a checked witness
merely because they use the same universe constant type.

#### Builtin registration

The builtin-meaning interface gains optional checked-representation metadata. Schematically:

```haskell
newtype BuiltinRepresentation uni = BuiltinRepresentation
  { brInferType
      :: Some (ValueOf uni)
      -> Either Text (Type TyName uni ())
  }

class ToBuiltinMeaning uni fun where
  type CostingPart uni fun
  data BuiltinSemanticsVariant fun

  toBuiltinMeaning
    :: BuiltinSemanticsVariant fun
    -> fun
    -> BuiltinMeaning val (CostingPart uni fun)

  toBuiltinRepresentation
    :: BuiltinSemanticsVariant fun
    -> fun
    -> Maybe (BuiltinRepresentation uni)

  toBuiltinRepresentation _ _ = Nothing
```

`toBuiltinMeaning` remains the source of the builtin's runtime denotation, type scheme, and
costing function. `toBuiltinRepresentation` is a separate optional hook used only while checking
PLC `BuiltinRep` terms. A builtin that uses ordinary arguments keeps the default `Nothing`.

The typechecking configuration constructs two tables indexed by the builtin enumeration:

```haskell
data BuiltinTypes uni fun = BuiltinTypes
  { unBuiltinTypes
      :: Array fun (BuiltinTypeInfo uni)
  , builtinRepresentations
      :: Array fun (Maybe (BuiltinRepresentation uni))
  }
```

The checker builds both tables for the same `BuiltinSemanticsVariant fun`; a representation checker
therefore cannot be selected independently of the runtime semantics that consume its output.

Core PLC looks up the builtin's callback and passes it the literal constant. The callback either
reports an error or returns a type to normalize. Constant decoding, result-index calculation, and
runtime interpretation remain outside the core typechecker.

#### Typing

Let $\mathcal R_\nu(f)$ be the representation metadata registered for builtin $f$ under semantics
variant $\nu$. The callback either rejects a literal constant $c$ or returns its complete PLC type.
The general rule is:

$$
\text{TY-BUILTINREP}
\frac{
  \mathcal R_\nu(f)=r
  \qquad
  r(c)=\mathsf{Right}(T)
  \qquad
  \vdash T::*
  \qquad
  T\text{ is closed}
}{
  \Gamma\vdash
  \mathsf{builtinrep}(f,c):T
}.
$$

If $\mathcal R_\nu(f)=\mathsf{Nothing}$, the term is invalid even when $c$ is otherwise a valid
universe constant. If the builtin tag is unknown, ordinary unknown-builtin rejection occurs before
representation checking.

This indexed typing discipline follows Crary, Weirich, and Morrisett's $\lambda_R$. Runtime type
information in $\lambda_R$ is carried by terms rather than types. A term $v$ representing $\tau$
has type $R(\tau)$, and $R(\tau)$ is a singleton. The type establishes which representation was
passed, but erasure removes the type and retains $v$. Without a representation term, code cannot
inspect the hidden type.

For `matchDataConstr`, the checker assigns $b$ the type `BuiltinRep matchDataConstr S` only when
decoding $b$ produces $S$. The builtin consumes that witness and returns $S$. Erasure removes the
index and retains $b$ as the first UPLC argument.

Unlike $R(\tau)$, `BuiltinRep matchDataConstr S` is not a singleton. Different tables can produce
the same SOP type. The table represents a matching operation rather than the structure of $S$, and
the nominal representation family has no generic typecase operation.

A registered callback must satisfy these obligations:

- **Determinism:** the same semantics variant, builtin, and literal constant returns the same type
  or the same rejection.
- **Total validation:** malformed constants produce `Left` rather than a host exception.
- **Closed type:** the inferred type contains no free type variables and has kind $*$.
- **Nominal ownership:** after any leading type quantifiers, the inferred type uses the
  representation family assigned to that builtin, normally `BuiltinRep name I`. Another builtin
  cannot return or consume that family unless a later proposal explicitly specifies shared
  ownership.
- **Canonicality:** if the represented format has multiple byte-level spellings, the callback
  accepts only the normative canonical form.
- **Runtime adequacy:** the runtime denotation consuming the erased constant either fails or
  produces a value consistent with the static relation established by the callback.
- **Cost coverage:** the builtin's UPLC costing function covers accepted and rejected raw
  constants, because UPLC does not run this PLC callback.

These conditions belong to the registration, not to builtin-specific branches in the core
typechecker. A later builtin can register a different literal format and index without adding
another PLC term constructor.

#### Erasure

Every successfully checked representation term erases identically:

$$
|\mathsf{builtinrep}(f,c)| = \mathsf{constant}(c).
$$

`brInferType` runs during PLC checking, not erasure. The eraser emits the retained constant without
inspecting its nominal family or its eventual consumer.

#### `matchDataConstr` registration

`matchDataConstr` instantiates the general interface as follows:

```haskell
toBuiltinRepresentation _ MatchDataConstr =
  Just (BuiltinRepresentation inferMatchDataConstrRepType)

inferMatchDataConstrRepType constant = do
  bytes    <- requireByteString constant
  patterns <- decodeMatchDataConstrTable bytes
  pure
    (TyBuiltinRep
      (BuiltinRepName "matchDataConstr")
      (captureSOP patterns))
```

The callback accepts only a `ByteString`, validates the canonical table in the following section,
and returns the complete `BuiltinRep matchDataConstr S` type. The runtime builtin independently
receives the erased `ByteString` through its ordinary first argument.

Write:

- $\mathsf{Decode}(b)=P$ when bytes $b$ decode to the canonical pattern table $P$;
- $\mathsf{Valid}(P)$ when all table invariants below hold; and
- $\mathsf{Capt}(P)$ for the SOP result type determined by $P$.

The introduction rule for `matchDataConstr` is:

$$
\text{TY-MATCHDATACONSTR-REP}
\frac{
  b:\mathsf{bytestring}
  \qquad
  \mathsf{Decode}(b)=P
  \qquad
  \mathsf{Valid}(P)
  \qquad
  S=\mathsf{Capt}(P)
}{
  \Gamma\vdash
  \mathsf{builtinrep}(\mathsf{matchDataConstr},b)
  :
  \mathsf{BuiltinRep}(\mathsf{matchDataConstr},S)
}.
$$

A builtin with no registered representation metadata cannot form a well-typed `builtinrep` term.
A representation registered for one builtin cannot inhabit another builtin's nominal family.

### Abstract pattern table

A decoded table is a finite sequence:

$$
P =
[(t_0,a_0,m_0),\ldots,(t_{n-1},a_{n-1},m_{n-1})],
$$

where:

- $n>0$;
- each $t_i$ is a `Word64` constructor tag;
- tags are strictly increasing;
- $a_i$ is the exact number of immediate fields required for tag $t_i$; and
- $m_i$ contains exactly $a_i$ selector bits.

Selector bit $j$ is:

- $0$ to skip immediate field $j$; or
- $1$ to retain immediate field $j$.

Let $c_i$ be the number of set bits in $m_i$. Then:

$$
\mathsf{Capt}(P) =
\mathsf{sop}\left(
  [\underbrace{\mathsf{data},\ldots,\mathsf{data}}_{c_0}],
  \ldots,
  [\underbrace{\mathsf{data},\ldots,\mathsf{data}}_{c_{n-1}}]
\right).
$$

Table order determines SOP branch order. Original constructor tags do not become SOP tags, so
unused tags need neither table rows nor `Case` handlers.

### Canonical ByteString encoding

The runtime representation has the following concatenated format:

```text
entry-count,
(
  constructor-tag,
  field-count,
  packed-selector-bits
)*
```

`entry-count`, every `constructor-tag`, and every `field-count` use canonical unsigned
LEB128:

- seven payload bits per byte;
- bit 7 indicates another byte;
- least-significant group first; and
- the shortest possible encoding is required.

Additional validity rules are:

1. the representation is non-empty;
2. `entry-count` is nonzero and equals the number of encoded rows;
3. constructor tags fit in `Word64` and are strictly increasing;
4. a row with field count $a$ contains exactly $\lceil a/8\rceil$ selector bytes;
5. field $j$ is bit $j\bmod 8$ of byte $\lfloor j/8\rfloor$;
6. unused high bits in the final selector byte are zero; and
7. no trailing bytes are permitted.

There is no in-band format-version byte. A semantically incompatible representation format
requires a new builtin or language version, rather than making every call inspect a version field.

For example:

$$
P =
[
  (7,3,[0,1,0]),
  (42,2,[1,1])
]
$$

is encoded as:

```text
#020703022a0203
```

and has type:

```text
BuiltinRep matchDataConstr (sop [data] [data data])
```

Here `02` gives the entry count. The first row, `07 03 02`, has tag 7, arity 3, and captures only
field 1. The second, `2a 02 03`, has tag 42, arity 2, and captures both fields.

The checker and runtime evaluator must use the same decoder or two implementations proven to
accept exactly the same canonical language.

### Application and result

Schematically, typed PLC applies the builtin as:

```lisp
[
  [
    {(builtin matchDataConstr) (sop [data] [data data])}
    (builtinrep matchDataConstr bytestring #020703022a0203)
  ]
  value
]
```

If `value` is:

```text
Constr 7 [x0, x1, x2]
```

the result is:

```text
Constr 0 [x1]
```

If `value` is:

```text
Constr 42 [y0, y1]
```

the result is:

```text
Constr 1 [y0, y1]
```

The caller uses ordinary `Case` over the resulting SOP value. Captured fields remain `Data`;
the builtin does not recursively inspect their payloads.

### Runtime semantics

Let $P$ be the successfully decoded table. Evaluation of
$\mathsf{matchDataConstr}(b,d)$ proceeds as follows:

1. Decode $b$ and reject a noncanonical or malformed table.
2. Require $d$ to be `Data.Constr t fields`.
3. Locate $t$ among the sorted table tags.
4. Require the number of immediate fields to equal the selected row's field count.
5. Scan the immediate fields from left to right.
6. Retain a field exactly when its selector bit is set.
7. Return `VConstr i captures`, where $i$ is the zero-based table position.

The builtin fails when:

- its first argument is not a `ByteString`;
- the representation is malformed or noncanonical;
- the second argument is not `Data.Constr`;
- no row has the runtime constructor tag; or
- the selected row's exact field count differs from the runtime field count.

Mismatch is an ordinary builtin failure, not a recoverable branch. A caller that needs other
root-`Data` behavior must discriminate before the call; several accepted `Data.Constr` tags belong
in one table.

The builtin binary-searches the sorted tags. It returns the compact table position, not the
original `Data.Constr` tag.

### Static soundness obligation

Define:

$$
\mathsf{Valid}_{\mathsf{matchDataConstr}}(b,S)
\quad\Longleftrightarrow\quad
\exists P.
  \mathsf{Decode}(b)=P
  \land \mathsf{Valid}(P)
  \land S=\mathsf{Capt}(P).
$$

The checked representation rule establishes this relation. Let $\mathsf{Val}(T)$ denote the
runtime values interpreting type $T$. Runtime adequacy requires:

$$
\frac{
  \mathsf{Valid}_{\mathsf{matchDataConstr}}(b,S)
  \qquad
  d\in\mathsf{Val}(\mathsf{data})
}{
  \mathsf{matchDataConstrRuntime}(b,d)
  \in\mathsf{Val}(S)
  \quad\text{or evaluation fails}
}.
$$

On success, the returned constructor position, capture count, capture order, and field types must
agree with $S$. The checked witness and runtime use the same canonical table, and row $i$
determines branch $i$ in both $\mathsf{Capt}(P)$ and the runtime result. Every selected input field
has builtin type `Data`; scanning the selector bits from left to right fixes the number and order of
those fields.

This guarantee applies to checked PLC. Raw UPLC may supply arbitrary bytes, so the runtime decoder
must reject malformed inputs safely and the cost model must cover both successful and rejected
calls.

### Erasure

The representation type has no UPLC counterpart:

$$
|\mathsf{BuiltinRep}(\rho,S)|
  = \mathsf{erased}.
$$

Together with the generic term rule above, the instance needs only the standard erasure of its
type application:

$$
|\mathsf{matchDataConstr}[S]|
  = \mathsf{force}(\mathsf{matchDataConstr}).
$$

Therefore:

```text
PLC:
  matchDataConstr
    @S
    (builtinrep matchDataConstr bytestring b)
    d

UPLC:
  force matchDataConstr b |d|
```

Erasure is syntax-directed: it retains $b$ without decoding it or consulting builtin semantics.

The UPLC builtin has one force and two term arguments. No `BuiltinRep` type or
representation-specific universe type survives into UPLC.

### Costing

`matchDataConstr` uses the standard two-argument builtin-costing pipeline. Let $x$ be the ordinary
execution-memory measure of the first `ByteString` argument in eight-byte words and $y$ the
ordinary measure of the `Data` argument.

The intended model shapes are:

$$
\begin{aligned}
\mathsf{cpu}(x,y) &= a+b x,\\
\mathsf{memory}(x,y) &= c+d x.
\end{aligned}
$$

There is no term in $y$. Table decoding and tag lookup are bounded by the encoded bytes. Every
declared field contributes one selector bit, so one eight-byte word describes at most 64 field
visits and at most 64 retained references. Nested payloads are not traversed.

The constructor tag and exact field count are also encoded in the first argument, so $x$ covers
their decoding. The selector-bit format ensures that a small encoding cannot direct an unbounded
field traversal.

Final coefficients are not normative in this draft. They must be fitted with the repository's
canonical builtin benchmark against a same-build two-argument no-op baseline. The calibration data
must vary table and tag size, arity, capture density, successful and missing tags, malformed
representations, and selector-saturated traversal. Varying nested payload size independently must
confirm the absence of a $y$ term. The standard R pipeline must then produce the affected protocol
cost models and pass the repository's safety and Haskell-versus-R consistency checks.

### Serialization

`matchDataConstr` is appended to the existing builtin-function enumeration. Existing builtin tags do
not change.

PLC assigns type-constructor tag 8 to `TyBuiltinRep` and term-constructor tag 12 to the checked
`BuiltinRep` term.

The current typed PLC/PIR prototype widens type tags from three bits to four bits because the
previous type-tag space was full. This changes typed PLC/PIR serialization and therefore requires
an explicit typed-language/serialization version decision before release.

It does not change the serialization of existing submitted UPLC terms: `TyBuiltinRep` is erased,
and a checked representation becomes an ordinary `ByteString` constant. Existing UPLC scripts do
not contain the new builtin tag and retain their previous meaning.

## Rationale: How does this CIP achieve its goals?

### Builtin rather than `Match`

As a builtin, `matchDataConstr` uses the existing application and CEK builtin paths, returns a
`VConstr` for `Case`, and erases its checked table to an ordinary `ByteString`. It requires no new
UPLC term, binder, evaluator frame, or value form.

A native `Match` term avoids some builtin application and dispatch overhead, and the prototype is
cheaper on many of the tested shapes. Supporting it would also require new core and Flat syntax,
scoping rules, evaluator frames, optimizer cases, conformance rules, and machine costs.

The costing models also differ. Native matching charges as it processes alternatives, pattern
nodes, edges, and captures. `matchDataConstr` is charged once per call through the standard
two-argument builtin interface, and only the size of its `ByteString` argument varies in the model.
This avoids match-specific costing inside the traversal. The coefficients in the tables below came
from earlier sparse-table and gap-program prototypes. They are not final costs for the selector-bit
encoding.

### Checked representation and SOP result

The result type depends on the runtime table, so accepting unchecked bytes in PLC would let a
caller claim an arbitrary result SOP. Keeping the representation only in a type would avoid that
problem, but would make erasure inspect a builtin-specific type and synthesize runtime bytes. An
ordinary universe type is also unsuitable: its usual constructors or eliminators could forge a
value whose claimed result index disagrees with its runtime meaning.

`BuiltinRep matchDataConstr S` and `builtinrep matchDataConstr b` instead establish the
relationship once in the typechecker, while the same bytes pass to UPLC unchanged.

The result uses existing `VConstr` and `Case` machinery. Each table row becomes one SOP branch,
whose type records the number and order of captured fields. Branch tags are compact table
positions, so a source tag such as 42 does not require 42 empty branches.

### Reuse and phase separation

`BuiltinRepresentation` is not specific to `matchDataConstr`. Another builtin can register a
literal format and a callback that returns its indexed PLC type. For example, later proposals
could use the same mechanism for builtin lists and `Data.List`. Their checked literals could
describe exact or prefix length and selected positions, and their runtime builtins could return
`VConstr` for dispatch by `Case`.

A `Data.List` matcher has the fixed element type `Data` and can use the result SOP as its index. A
polymorphic builtin-list matcher must also relate its element type to the captured fields in the
result; otherwise a witness for `list B` could be applied to `list A`. The exact type and encoding
belong in the proposal for that builtin.

Most of the language change remains in PLC. PLC validates the literal, computes its static index,
and ties that index to a nominal builtin family. UPLC receives the erased literal and the value to
inspect. The runtime builtin still rejects malformed raw UPLC input, but UPLC needs no pattern AST,
binders, scoping rules, or new value form. Evaluation and charging use the existing builtin path.

The eraser remains syntax-directed. The runtime representation is already a term before erasure;
it is not reconstructed from an erased type. The generic erasure rule copies the literal unchanged
and does not call the registration callback. Adding `matchList`, `matchDataList`, or another
checked builtin therefore adds no builtin-specific erasure rule and does not make PLC types
computationally relevant.

### Table format

The builtin is limited to `Data.Constr`, the form used to encode known records and sum
alternatives. Matching sites normally accept a small set of possibly non-dense tags, so the table
stores only those tags in strictly increasing order. This keeps the result SOP compact, enables
binary search, and rules out duplicate entries. Each row gives the exact immediate arity; accepting
only a prefix could let malformed or version-mismatched data pass as the expected source type.

One selector bit per field keeps dense and sparse captures compact and also bounds runtime work:
each encoded bit authorizes at most one immediate field visit and one capture.

Earlier prototypes used one-byte masks or byte-coded skip distances. Gap coding reduced some
scripts, but a single byte could direct traversal of up to 255 fields, forcing a very conservative
CPU slope when costing only by ordinary `ByteString` size. The bitset makes the relationship
between encoded size and runtime work direct.

The table represents the successful result SOP. A default of an unrelated shape would either
complicate that index or require handler terms in the representation, so mismatch remains a
builtin failure. Other `Data` forms already have suitable operations: `Data.I` and `Data.B` can be
decoded after capture, while `Data.List` and `Data.Map` have no constructor-tag table.

### Performance evidence

The prototype benchmark suite contains 22 explicitly defined `Data.Constr` workloads covering
depth 1 to 100, width 1 to 1,000, one to 32 captures, spines, root forks, full trees, and
alternatives sharing a prefix.

Every implementation receives the same closed `Data` argument, captures the same integer fields,
performs the same final arithmetic, and is checked against the same exact result before
measurement. The comparison covers native shallow `Match` lowered one structural layer at a time,
native deep `Match` represented by one recursive pattern, traditional `unConstrData`
deconstruction, and sparse-tag `matchDataConstr` followed by ordinary `Case`.

`matchDataConstr` was not uniformly cheaper than traditional matching in CPU. It lost on the
minimal D=1/W=1/C=1 constructor and the D=64 and D=100 width-2 spines. The minimal case does too
little work to amortize builtin setup. The two spines call `matchDataConstr` at every node while
saving little field traversal. Its memory budget remained lower than traditional matching in all
three cases.

#### Complete CEK wall-time comparison

The table reports Criterion means in microseconds. Each benchmark process selected one case;
argument and matcher generation, full forcing, application construction, and exact-result checking
happened before timing. The measured action was `whnf runCEK appliedTerm`. Runs used GHC 9.6.7,
Criterion 1.6.5.0, Cabal `-O1`, one GHC capability, and an AMD Ryzen 9 7950X pinned to one CPU.

The three baseline prototypes and sparse-tag `matchDataConstr` were measured at their recorded
historical revisions; `matchDataConstr` was run in a separate session. Wall time is host-specific
and is not used for ledger costing. The execution-budget tables provide that comparison.

| # | Case | Shallow `Match` (µs) | Deep `Match` (µs) | Traditional (µs) | `matchDataConstr` (µs) |
|---:|---|---:|---:|---:|---:|
| 1 | `constr_flat_d1_w1_c1` | 0.357901 | 0.377854 | 0.667046 | 0.541754 |
| 2 | `constr_flat_d1_w16_c4` | 1.031776 | 1.067766 | 1.606495 | 1.204469 |
| 3 | `constr_flat_d1_w1000_c1` | 3.893735 | 7.142544 | 1.917121 | 1.637811 |
| 4 | `constr_flat_d1_w1000_c16` | 6.698639 | 9.939033 | 5.745813 | 4.448110 |
| 5 | `constr_spine_front_d4_w16_c8` | 2.034489 | 2.224007 | 3.835260 | 2.528054 |
| 6 | `constr_spine_middle_d4_w16_c8` | 2.045473 | 2.235749 | 4.025645 | 2.535028 |
| 7 | `constr_spine_last_d4_w16_c8` | 2.059960 | 2.137027 | 3.817799 | 2.506234 |
| 8 | `constr_spine_irregular_d4_w16_c8` | 2.073076 | 2.210344 | 3.935280 | 2.546669 |
| 9 | `constr_spine_irregular_d8_w8_c8` | 2.404038 | 2.371215 | 5.718656 | 3.156149 |
| 10 | `constr_spine_front_d64_w2_c8` | 5.498050 | 4.415301 | 17.525628 | 12.089634 |
| 11 | `constr_spine_zigzag_d100_w2_c10` | 8.022903 | 5.985006 | 28.262511 | 18.299033 |
| 12 | `constr_binary_d3_w16_c8` | 2.445819 | 2.607416 | 4.674805 | 3.050840 |
| 13 | `constr_ternary_d3_w8_c10` | 3.139957 | 3.067398 | 7.350378 | 4.377922 |
| 14 | `constr_quaternary_d3_w8_c17` | 5.151877 | 4.783671 | 11.630594 | 7.197313 |
| 15 | `constr_rootfork2_d6_w12_c8` | 2.563802 | 2.638462 | 5.520768 | 3.353414 |
| 16 | `constr_rootfork3_d5_w10_c9` | 2.814644 | 2.762332 | 6.258073 | 3.682175 |
| 17 | `constr_rootfork4_d4_w8_c8` | 2.278199 | 2.308060 | 4.947085 | 3.201121 |
| 18 | `constr_spine_stress_d10_w100_c20` | 8.296058 | 10.892651 | 11.166538 | 7.349628 |
| 19 | `constr_binary_stress_d8_w8_c32` | 28.182496 | 27.443982 | 116.878475 | 51.198701 |
| 20 | `constr_alt_spine_d16_w8_c8` | 3.067825 | 4.632294 | 8.327314 | 4.526635 |
| 21 | `constr_alt_rootfork3_d5_w10_c9` | 2.844845 | 4.093085 | 6.540113 | 3.856224 |
| 22 | `constr_alt_binary_d8_w8_c32` | 28.255839 | 50.902547 | 114.013661 | 51.392019 |

#### Complete execution CPU comparison

| # | Case | Shallow `Match` | Deep `Match` | Traditional | `matchDataConstr` |
|---:|---|---:|---:|---:|---:|
| 1 | `constr_flat_d1_w1_c1` | 251,720 | 339,976 | 481,765 | 646,072 |
| 2 | `constr_flat_d1_w16_c4` | 1,388,354 | 1,387,462 | 2,005,238 | 1,473,928 |
| 3 | `constr_flat_d1_w1000_c1` | 17,544,410 | 13,383,928 | 2,982,974 | 1,691,272 |
| 4 | `constr_flat_d1_w1000_c16` | 21,929,330 | 17,589,406 | 9,640,109 | 5,554,312 |
| 5 | `constr_spine_front_d4_w16_c8` | 3,618,046 | 3,746,106 | 6,082,994 | 4,127,420 |
| 6 | `constr_spine_middle_d4_w16_c8` | 3,618,046 | 3,746,106 | 6,598,823 | 4,127,420 |
| 7 | `constr_spine_last_d4_w16_c8` | 3,618,046 | 3,575,250 | 5,854,164 | 4,127,420 |
| 8 | `constr_spine_irregular_d4_w16_c8` | 3,618,046 | 3,746,106 | 6,151,999 | 4,127,420 |
| 9 | `constr_spine_irregular_d8_w8_c8` | 3,924,046 | 4,410,546 | 10,189,609 | 6,240,172 |
| 10 | `constr_spine_front_d64_w2_c8` | 9,315,886 | 14,943,370 | 29,303,115 | 35,885,260 |
| 11 | `constr_spine_zigzag_d100_w2_c10` | 13,900,862 | 20,320,430 | 47,413,347 | 55,484,412 |
| 12 | `constr_binary_d3_w16_c8` | 4,678,426 | 4,683,342 | 7,979,231 | 5,761,904 |
| 13 | `constr_ternary_d3_w8_c10` | 5,583,602 | 6,115,850 | 13,173,734 | 9,432,216 |
| 14 | `constr_quaternary_d3_w8_c17` | 9,349,738 | 10,379,768 | 20,190,093 | 14,966,744 |
| 15 | `constr_rootfork2_d6_w12_c8` | 4,762,186 | 5,105,942 | 9,408,724 | 6,814,120 |
| 16 | `constr_rootfork3_d5_w10_c9` | 4,992,534 | 5,466,452 | 11,034,419 | 7,588,740 |
| 17 | `constr_rootfork4_d4_w8_c8` | 3,924,046 | 4,296,642 | 8,336,134 | 6,240,172 |
| 18 | `constr_spine_stress_d10_w100_c20` | 23,787,142 | 20,349,186 | 18,625,485 | 11,327,012 |
| 19 | `constr_binary_stress_d8_w8_c32` | 64,039,978 | 76,680,422 | 193,778,602 | 131,892,496 |
| 20 | `constr_alt_spine_d16_w8_c8` | 5,695,816 | 11,368,843 | 15,748,590 | 10,866,611 |
| 21 | `constr_alt_rootfork3_d5_w10_c9` | 5,044,464 | 9,205,495 | 11,152,344 | 7,787,915 |
| 22 | `constr_alt_binary_d8_w8_c32` | 64,091,908 | 147,351,747 | 193,009,841 | 132,091,671 |

#### Complete execution memory comparison

| # | Case | Shallow `Match` | Deep `Match` | Traditional | `matchDataConstr` |
|---:|---|---:|---:|---:|---:|
| 1 | `constr_flat_d1_w1_c1` | 1,700 | 1,236 | 2,565 | 1,606 |
| 2 | `constr_flat_d1_w16_c4` | 6,806 | 4,440 | 7,579 | 4,183 |
| 3 | `constr_flat_d1_w1000_c1` | 101,600 | 61,182 | 4,333 | 2,611 |
| 4 | `constr_flat_d1_w1000_c16` | 119,630 | 72,696 | 25,239 | 14,215 |
| 5 | `constr_spine_front_d4_w16_c8` | 17,914 | 10,455 | 22,710 | 9,866 |
| 6 | `constr_spine_middle_d4_w16_c8` | 17,914 | 10,455 | 23,810 | 9,866 |
| 7 | `constr_spine_last_d4_w16_c8` | 17,914 | 10,437 | 21,450 | 9,866 |
| 8 | `constr_spine_irregular_d4_w16_c8` | 17,914 | 10,455 | 22,882 | 9,866 |
| 9 | `constr_spine_irregular_d8_w8_c8` | 19,914 | 10,525 | 36,054 | 13,358 |
| 10 | `constr_spine_front_d64_w2_c8` | 54,314 | 15,387 | 148,914 | 62,310 |
| 11 | `constr_spine_zigzag_d100_w2_c10` | 81,918 | 21,651 | 223,478 | 95,318 |
| 12 | `constr_binary_d3_w16_c8` | 24,214 | 13,368 | 29,649 | 12,533 |
| 13 | `constr_ternary_d3_w8_c10` | 28,818 | 14,526 | 48,791 | 19,271 |
| 14 | `constr_quaternary_d3_w8_c17` | 47,632 | 23,894 | 77,245 | 31,077 |
| 15 | `constr_rootfork2_d6_w12_c8` | 24,814 | 13,178 | 35,791 | 14,275 |
| 16 | `constr_rootfork3_d5_w10_c9` | 25,716 | 13,485 | 40,974 | 15,894 |
| 17 | `constr_rootfork4_d4_w8_c8` | 19,914 | 10,513 | 32,006 | 13,358 |
| 18 | `constr_spine_stress_d10_w100_c20` | 128,938 | 75,939 | 59,076 | 25,088 |
| 19 | `constr_binary_stress_d8_w8_c32` | 369,862 | 151,706 | 736,289 | 236,581 |
| 20 | `constr_alt_spine_d16_w8_c8` | 30,614 | 24,401 | 58,082 | 21,938 |
| 21 | `constr_alt_rootfork3_d5_w10_c9` | 26,016 | 21,883 | 41,814 | 17,296 |
| 22 | `constr_alt_binary_d8_w8_c32` | 370,162 | 286,767 | 735,045 | 237,983 |

#### Complete script-size comparison

| # | Case | Shallow `Match` | Deep `Match` | Traditional | `matchDataConstr` |
|---:|---|---:|---:|---:|---:|
| 1 | `constr_flat_d1_w1_c1` | 15 | 12 | 29 | 24 |
| 2 | `constr_flat_d1_w16_c4` | 43 | 37 | 76 | 50 |
| 3 | `constr_flat_d1_w1000_c1` | 266 | 638 | 45 | 28 |
| 4 | `constr_flat_d1_w1000_c16` | 383 | 712 | 256 | 138 |
| 5 | `constr_spine_front_d4_w16_c8` | 99 | 90 | 221 | 128 |
| 6 | `constr_spine_middle_d4_w16_c8` | 99 | 90 | 232 | 128 |
| 7 | `constr_spine_last_d4_w16_c8` | 99 | 90 | 212 | 128 |
| 8 | `constr_spine_irregular_d4_w16_c8` | 99 | 90 | 224 | 128 |
| 9 | `constr_spine_irregular_d8_w8_c8` | 116 | 94 | 348 | 189 |
| 10 | `constr_spine_front_d64_w2_c8` | 378 | 197 | 1,663 | 1,094 |
| 11 | `constr_spine_zigzag_d100_w2_c10` | 569 | 294 | 2,600 | 1,724 |
| 12 | `constr_binary_d3_w16_c8` | 124 | 123 | 305 | 176 |
| 13 | `constr_ternary_d3_w8_c10` | 164 | 135 | 488 | 288 |
| 14 | `constr_quaternary_d3_w8_c17` | 270 | 218 | 808 | 467 |
| 15 | `constr_rootfork2_d6_w12_c8` | 132 | 123 | 362 | 206 |
| 16 | `constr_rootfork3_d5_w10_c9` | 142 | 124 | 409 | 229 |
| 17 | `constr_rootfork4_d4_w8_c8` | 116 | 94 | 320 | 191 |
| 18 | `constr_spine_stress_d10_w100_c20` | 453 | 741 | 605 | 314 |
| 19 | `constr_binary_stress_d8_w8_c32` | 2,025 | 1,853 | 8,879 | 4,484 |
| 20 | `constr_alt_spine_d16_w8_c8` | 197 | 280 | 584 | 333 |
| 21 | `constr_alt_rootfork3_d5_w10_c9` | 175 | 240 | 419 | 245 |
| 22 | `constr_alt_binary_d8_w8_c32` | 2,167 | 3,697 | 8,861 | 4,500 |

The native prototypes are faster on many narrow or highly branching cases. Traditional
deconstruction is the direct baseline for `matchDataConstr`; the native results quantify the
performance tradeoff of using a builtin instead of adding a `Match` term.

All 22 `matchDataConstr` cases returned the expected value and passed the benchmark runner's
script-size, CPU, and memory limits. The recorded data is retained in the
[sparse-tag validation CSV](https://github.com/SeungheonOh/plutus/blob/5f08b9cd1/plutus-benchmark/matching-cpu-runtime/results/2026-08-17-matchdata-sparse-tags-validation.csv),
the [baseline validation CSV](https://github.com/SeungheonOh/plutus/blob/5f08b9cd1/plutus-benchmark/matching-cpu-runtime/results/2026-08-06-preflight-validation.csv),
the [baseline wall-time CSV](https://github.com/SeungheonOh/plutus/blob/5f08b9cd1/plutus-benchmark/matching-cpu-runtime/results/2026-08-06-criterion-wall-time.csv),
and the [sparse-tag wall-time CSV](https://github.com/SeungheonOh/plutus/blob/5f08b9cd1/plutus-benchmark/matching-cpu-runtime/results/2026-08-17-matchdata-sparse-tags-criterion-wall-time.csv).
Those historical revisions and artifact filenames retain the builtin's former `matchData`
spelling; this CIP renames the proposed builtin to `matchDataConstr`.

### Alternatives considered

#### Native shallow `Match`

The shallow design added one `Match` term whose alternatives inspected one structural layer. Its
most developed form recognized `Data.Constr tag fields`, `Data.List fields`, and
`Data.Map entries` at the root.

Each immediate position was either `skip` or `bind x`, followed by either exact-arity or
minimum-arity-with-ignored-rest behavior. Patterns could not contain child patterns. A compiler
lowered a nested source pattern to successive `Match` terms, with the outer node binding a child
`Data` value and its selected body performing the next shallow match.

Two branch interfaces were explored:

1. **Handler application.** The matcher collected captures and applied them to a handler lambda.
   This reused lambda/application semantics but made branch arity indirect and paid closure,
   `Apply`, and `LamAbs` costs.
2. **Direct lexical binding.** Binder names lived at selected field positions and the CEK entered
   the selected body under an environment extended by the captured values. An isolated
   1,024-capture experiment measured 19.897 microseconds for direct entry versus 23.247
   microseconds for handler application.

Because shallow lowering expresses each level as a separate term, alternatives can share the
successful prefix already traversed by their enclosing terms. It performs well on flat and wide
values and on alternatives that diverge near a leaf. It used less CPU than `matchDataConstr` in 19
of the 22 budget cases.

Implementing shallow `Match` touches PLC and UPLC syntax, Flat tags, branch-local scope, de Bruijn
conversion, renaming, substitution, discharge, hashing, typing, optimizer traversals, and all CEK
variants. Defaults, arity mismatch, captures, and unselected branch bodies also need machine costs
and conformance rules.

Each shallow match site carries AST field descriptors and branch bodies, which is expensive for
wide sparse records. `matchDataConstr` is smaller on both width-1,000 cases and the width-100 stress
case; shallow `Match` is smaller on most narrow cases.

This CIP does not add shallow `Match`. Its lower CPU budget on many cases comes with a new core
term and the associated binding, evaluation, costing, serialization, and conformance rules.

#### Native deep/recursive `Match`

The deep design added a `Match` term with ordered alternatives whose patterns recursively mirrored
builtin values. Its pattern language covered wildcards, captures, integer and byte-string
literals, booleans, unit, builtin lists and pairs, structural `Data.Constr`, `Data.List`, and
`Data.Map` patterns, and `Data.I` and `Data.B` wrappers.

Exact and prefix structural endings controlled whether an unconsumed suffix caused mismatch,
was ignored, or was captured. A successful recursive walk accumulated captures in left-to-right
depth-first order and applied them to the first successful handler. A single pattern could
therefore describe an entire nested script-context shape without entering another AST match node
at each depth.

The evaluator required an explicit work stack containing pending child patterns, values, captured
values, remaining alternatives, and suffix policy. Costing was incremental rather than a single
up-front charge, with distinct events for entering a match, processing a pattern node, traversing
a structural edge, and abandoning a failed alternative.

Deep matching performs well on successful narrow paths. Its CPU budget is 14,943,370 on the
D=64/W=2 spine, compared with 35,885,260 for `matchDataConstr`; on the full binary D=8 tree the
figures are 76,680,422 and 131,892,496.

A failed deep alternative restarts from the root. Shallow lowering and `matchDataConstr` instead
share the successful prefix through their enclosing program structure, so `matchDataConstr` uses
less CPU in all three alternative cases in the table above.

Deep matching also needs recursive typing judgments, nested mismatch propagation, capture-order
proofs, recursive Flat validation, and costing for literals and failed alternatives. Its pattern
can grow with every nested field even when most fields are wildcards. `matchDataConstr` does not
need this machinery because it only deconstructs one `Data.Constr` layer per call.

#### Extending `Case` over `Data`

Direct root discrimination would provide a more efficient `chooseData`, but it would not express
exact constructor arity or selective field capture. Adding field masks and result-shape metadata to
`Case` would effectively create a second pattern language while changing an established term.

#### Traditional deconstruction

`unConstrData`, integer comparison, list traversal, and `unIData` remain sufficient for
expressiveness and form the compatibility baseline measured above.

#### Atomic multi-lambda or multi-application

Atomic application could detect handler arity mismatches, but requires new terms and CEK behavior
while still passing every selected value through an application interface. It does not perform tag
selection or field traversal.

#### Type-directed erasure

An earlier design encoded a pattern in a PLC type argument and taught erasure to reify that type
into a UPLC constant. That makes erasure builtin-aware and makes an erased type computationally
relevant. Explicit checked representations retain the same information as an ordinary term and
keep erasure structural.

#### Array of `(integer, bytestring)` pairs

The sparse-pair prototype encoded tags explicitly, but generic array and pair overhead inflated
scripts. A canonical `ByteString` keeps the runtime directives in one costed argument and has one
canonical encoding.

## Path to Active

### Acceptance Criteria

- [ ] The PLC specification and implementation define checked builtin representations as a
      general, semantics-variant-indexed interface, with `matchDataConstr` registered through that
      interface rather than special-cased in the core typechecker.
- [ ] The specified table format, typing rule, runtime behavior, failures, and structural erasure
      are covered by conformance tests, including malformed encodings and agreement between the
      inferred SOP type and returned `VConstr`.
- [ ] The final CPU and memory models are produced by the standard builtin-costing pipeline, cover
      successful and rejected inputs, pass the repository's safety and model-consistency checks,
      and are propagated to every affected protocol cost model.
- [ ] Reproducible benchmarks run every compared implementation on one production evaluator,
      check exact results, and report CEK wall time, execution CPU, execution memory, and script
      size, including cases where `matchDataConstr` is more expensive.
- [ ] The typed PLC/PIR serialization change has an approved versioning plan, and an independent
      implementation or independently reproduced test vectors confirm interoperability.
- [ ] A protocol release enables the builtin with its approved cost parameters, and supporting
      block-producing nodes represent at least 80% of active stake.

### Implementation Plan

The reference implementation adds the general checked-representation type, term, registration
hook, and typechecking path throughout PLC and PIR. Parser, Flat, traversal, and erasure support
must treat the new type and term generically.

The `matchDataConstr` implementation provides the canonical table codec, runtime behavior, and
compiler lowering to `matchDataConstr` followed by `Case`. Conformance tests cover the registration
interface, table format, result construction, failure behavior, serialization, and erasure.

Before activation, the final implementation must be benchmarked and recosted. The comparison must
use one evaluator revision and report wall time, execution budgets, and script size. Ledger and
node releases then add the builtin with the approved cost parameters.

## References

- [CIP-0001: CIP Process](https://cips.cardano.org/cip/CIP-0001)
- [CIP-0035: Plutus Core Evolution](https://cips.cardano.org/cip/CIP-0035)
- [CIP-0085: Sums-of-products in Plutus Core](https://cips.cardano.org/cip/CIP-0085)
- [CIP-0194 discussion](https://github.com/cardano-foundation/CIPs/pull/1236)
- [Crary, Weirich, and Morrisett: *Intensional Polymorphism in Type-Erasure Semantics*](https://doi.org/10.1017/S0956796801004282)
- [Recursive `Match` implementation experiment](https://github.com/IntersectMBO/plutus/pull/7852)
- [matchDataConstr implementation branch](https://github.com/SeungheonOh/plutus/tree/type-pattern-matchdata)
- [IntersectMBO/plutus issue #5777](https://github.com/IntersectMBO/plutus/issues/5777)
- [IntersectMBO/plutus issue #6225](https://github.com/IntersectMBO/plutus/issues/6225)
- [IntersectMBO/plutus issue #6602](https://github.com/IntersectMBO/plutus/issues/6602)
- [IntersectMBO/plutus pull request #7209](https://github.com/IntersectMBO/plutus/pull/7209)

### Prototypes

| Implementation or artifact | Revision |
|---|---|
| Native shallow `Match` implementation | [`d118a596`](https://github.com/SeungheonOh/plutus/commit/d118a596556784d599bf6e9a80c9fcffa01d2cf0) |
| Native recursive `Match` implementation | [`20d7f06e`](https://github.com/SeungheonOh/plutus/commit/20d7f06ed4dc5f29439b5b0d4b1ab8a62627f3b3) |
| Traditional deconstruction baseline | [`b9d726d7`](https://github.com/SeungheonOh/plutus/commit/b9d726d7cc957fa154c6ba9f01959952887f1246) |
| Gap-only `matchDataConstr` encoding | [`25baa821`](https://github.com/SeungheonOh/plutus/commit/25baa82102b5e684e5a5478a345519c3252a674a) |
| Fitted sparse `matchDataConstr` costing | [`140c5e6e`](https://github.com/SeungheonOh/plutus/commit/140c5e6ef) |
| Sparse-tag `matchDataConstr` validation | [`5f08b9cd`](https://github.com/SeungheonOh/plutus/commit/5f08b9cd1) |
| Explicit checked representations | [`e6aba017`](https://github.com/SeungheonOh/plutus/commit/e6aba0171) |

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
