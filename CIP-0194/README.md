---
CIP: 194
Title: Builtin pattern matching in UPLC
Category: Plutus
Status: Proposed
Authors:
  - Seungheon Oh <seungheon.oh@iohk.io>
Implementors:
  - Seungheon Oh <seungheon.oh@iohk.io>
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1236
  - Implementation PR: https://github.com/IntersectMBO/plutus/pull/7852
Created: 2026-07-30
License: CC-BY-4.0
---

## Abstract

This proposal adds a `Match` term and a universe-specific builtin-pattern type to Untyped Plutus Core (UPLC). `Match` performs ordered, recursive pattern matching on builtin constants and can capture values from nested `Data`, integers, byte strings, lists, and pairs. Captured values are applied to the handler associated with the first successful pattern.

The proposal addresses the limited expressiveness of builtin `Case`, especially when deconstructing known `Data` structures such as script contexts. It retains `Case` for inexpensive shallow dispatch while providing a more expressive operation for direct and nested matching. Matching work is charged incrementally according to the pattern operations, structural traversal, and failed alternatives performed at runtime.

This proposal covers UPLC syntax and serialization, CEK evaluation, costing, and conformance tests. Typed Plutus Core (TPLC), Plutus IR (PIR), Plinth, PlutusTx libraries, and compiler optimizations that generate or transform `Match` are outside its initial scope.

## Motivation: Why is this CIP necessary?

Builtin casing extended the `Case` term so that it can inspect builtin constants of type integer, list, boolean, and unit. Because a `Case` branch carries no pattern information, its meaning is fixed by its position. For integers, for example, the first branch matches `0`, the second matches `1`, and so on.

This limited form of casing still provides significant performance improvements for integers, lists, and booleans because it avoids the overhead of calling builtin functions. Similar improvements are desirable for `Data`, the builtin type most often used to represent smart-contract inputs.

### Prior approaches to matching `Data`

An initial approach extended builtin casing directly to the five constructors of `Data`, effectively providing a more efficient `chooseData`. This offered limited practical value: contracts rarely use `chooseData` by itself, and known structures such as script contexts can already be deconstructed more efficiently with partial builtins such as `unConstrData`.

A more useful approach is to match `Data.Constr` directly when casing on `Data`. This can improve programs that inspect script contexts, but it introduces an arity problem in TPLC and PIR. `Data.Constr` is an untyped runtime value whose number of fields is not known by the type system. A handler with the wrong number of arguments may therefore partially apply instead of failing:

```haskell
case (Data.Constr 0 [Data.I 1])
  (\x y -> x)

-- Evaluates to: \y -> Data.I 1
```

Atomic multi-lambda and multi-application were proposed to detect such length mismatches:

```haskell
(\[x y] -> x) [Data.I 1, Data.I 2] -- Evaluates
(\[x y] -> x) [Data.I 1]           -- Fails due to arity mismatch
```

That design requires new AST terms and specialized CEK handling while still providing only limited matching on `Data.Constr`. A dedicated `Let` term has similar implementation costs and similarly limited semantics. Both designs also overlap with existing lambda/application behavior.

Since these approaches require new syntax and non-trivial CEK changes, this proposal instead introduces one general pattern-matching term. It supports direct and nested matching across builtin values while keeping the CEK integration close to the existing implementation of builtin `Case`.

### Use cases and stakeholders

The primary use case is efficient deconstruction of known `Data` structures, particularly ledger script contexts. The same operation also supports selective matching and capture in builtin lists, pairs, integers, byte strings, booleans, and unit.

The direct stakeholders are:

- authors and users of UPLC-producing compilers;
- implementors of Plutus Core evaluators, serializers, and analysis tools;
- ledger and node implementors responsible for language-version and cost-model support; and
- smart-contract developers whose scripts repeatedly inspect structured builtin values.

## Specification

### Status of this specification

The pure matching rules in [Matching semantics](#matching-semantics) are normative. They define which alternative is selected, which values are captured, their order, and the resulting handler application.

The cost coefficients described in [Costed operational refinement](#costed-operational-refinement) are pre-activation working values. They must be calibrated against representative benchmarks before they are used by the ledger.

### Scope and type of change

This proposal makes two related changes:

1. It adds a new UPLC language construct, `Match`, together with universe-specific pattern syntax. Under CIP-0035, adding a language construct is a backward-compatible minor Plutus Core language-version change.
2. It adds CEK cost-model parameters for entering a match, processing a pattern step, traversing a structural edge, and proceeding to the next alternative.

This proposal specifies the default-universe patterns. It does not require all Plutus Core universes to use those patterns; pattern matching remains universe-specific.

### Abstract syntax

The UPLC term type gains a `Match` constructor. Its pattern type is supplied by the builtin universe:

```haskell
-- module UntypedPlutusCore.Core.Type
data Term name uni fun ann
  = ...
  | Match
      !ann
      !(Term name uni fun ann)
      !(Vector (BuiltinPattern uni, Term name uni fun ann))
```

A `Match` contains:

- a scrutinee term; and
- an ordered vector of pattern/handler alternatives.

The default universe defines the following field endings and builtin patterns:

```haskell
-- module PlutusCore.Default.Universe
data DefaultPatternFieldEnd
  = DefaultPatternFieldsExact
  | DefaultPatternFieldsPrefixWildcard
  | DefaultPatternFieldsPrefixCapture

data DefaultBuiltinPattern
  = DefaultPatternWildcard
  | DefaultPatternCapture
  | DefaultPatternInteger !Int64
  | DefaultPatternByteString !ByteString
  | DefaultPatternBool !Bool
  | DefaultPatternUnit
  | DefaultPatternList
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternPair
      !DefaultBuiltinPattern
      !DefaultBuiltinPattern
  | DefaultPatternDataConstr
      !Word64
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternDataMap
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternDataList
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternDataI !DefaultBuiltinPattern
  | DefaultPatternDataB !DefaultBuiltinPattern
```

`DefaultPatternWildcard` accepts the value at the current position without capturing it. `DefaultPatternCapture` accepts and records the current value. These correspond roughly to `_` and a variable binding in a Haskell pattern.

The scalar patterns match the corresponding integer, byte string, boolean, or unit value. Pair, list, and `Data` patterns recursively match their contents. `DefaultPatternDataConstr` additionally matches the constructor tag.

For builtin lists, `Data.Constr` fields, `Data.List`, and `Data.Map`, `DefaultPatternFieldEnd` distinguishes:

- an exact match, in which the number of fields or elements must equal the number of child patterns; and
- a prefix match, in which the child patterns match the beginning of the structure and the remaining suffix may be captured.

### Concrete syntax

In the textual form, `match` is followed by its scrutinee and an ordered list of `pattern` alternatives. Each alternative contains a pattern followed by its handler:

```lisp
(program 1.2.0
  (match (con data (Constr 7 [I 1, B #aa, I 9]))
    (pattern
      ; Match Data.Constr 8 [<bind>, Data.List [_, _], ...]
      ; The handler must accept one data capture.
      (data-constr 8
        (prefix
          (bind)
          (data-list (wildcard) (wildcard))
          (wildcard)))
      (error))
    (pattern
      ; Match Data.Constr 7 [Data.I <bind>, ...] and bind the suffix.
      ; The handler must accept an integer and a list of data.
      (data-constr 7
        (prefix
          (data-i (bind))
          (bind)))
      (lam integerCapture (lam rest rest)))
    (pattern
      ; Match [_, <bind>, _, <bind>, ...].
      ; The handler must accept two values of the list element type.
      (list
        (prefix
          (wildcard)
          (bind)
          (wildcard)
          (bind)
          (wildcard)))
      (lam a (lam b a)))
    (pattern
      (wildcard)
      (error))))
```

In Flat, `Match` uses term-constructor tag `10`, followed by its annotation, scrutinee, and a list of alternatives. Each alternative encodes its pattern followed by its handler term.

Default builtin patterns use a four-bit tag:

| Tag | Pattern | Following payload |
|----:|---------|-------------------|
| 0 | wildcard | none |
| 1 | capture | none |
| 2 | integer | `Int64` |
| 3 | byte string | `ByteString` |
| 4 | boolean | `Bool` |
| 5 | unit | none |
| 6 | exact builtin list | child-pattern list |
| 7 | pair | left pattern, right pattern |
| 8 | exact `Data.Constr` | `Word64` tag, child-pattern list |
| 9 | exact `Data.Map` | child-pattern list |
| 10 | exact `Data.List` | child-pattern list |
| 11 | `Data.I` | child pattern |
| 12 | `Data.B` | child pattern |
| 13 | prefix | structural descriptor and one-bit rest tag |

For prefix tag `13`, the structural descriptor is one of tags `6`, `8`, `9`, or `10`, with the same payload as its exact form. A final one-bit tag selects whether the unconsumed suffix is ignored (`0`) or captured (`1`). Other pattern tags, structural descriptors, and rest tags are invalid.

### Matching semantics

This section gives an extensional reduction rule for the UPLC `Match` node. It separates the language semantics—ordered pattern selection and positional capture—from the CEK implementation's explicit work stack and incremental budget accounting.

#### Scope and notation

Write a `Match` term as

$$
\mathsf{match}\;M\;[(p_1,H_1),\ldots,(p_n,H_n)],
$$

where $M$ is the scrutinee, $p_i$ is a universe-specific builtin pattern, and $H_i$ is its handler. The alternatives are ordered.

A builtin constant is written $C=\langle u,v\rangle$, pairing a universe tag $u$ with a value $v:\mathsf{El}(u)$. The UPLC constant term containing $C$ is written $\ulcorner C\urcorner$. A capture sequence is written $\overline C=[C_1,\ldots,C_k]$, and $\epsilon$ is the empty sequence. Sequence concatenation is $\mathbin{+\!+}$.

Define left-associated application of a handler to its captures by

$$
\begin{aligned}
\mathsf{apps}(H,\epsilon) &= H,\\
\mathsf{apps}(H,C_0::\overline C)
  &= \mathsf{apps}(H\;\ulcorner C_0\urcorner,\overline C).
\end{aligned}
$$

Patterns do not introduce UPLC variables. A `bind` records a constant in $\overline C$; selection turns those captures into ordinary applications of the chosen handler.

#### Universe-supplied matching judgment

The core rule depends on a deterministic partial function supplied by the constant universe:

$$
\mu_{\mathcal U}(p,C)=\overline C.
$$

If the pattern does not match, $\mu_{\mathcal U}(p,C)$ is undefined, written $\mu_{\mathcal U}(p,C)\uparrow$.

The alternative-selection function is

$$
\begin{aligned}
\mathsf{select}_{\mathcal U}(C,[]) &= \mathsf{noMatch},\\
\mathsf{select}_{\mathcal U}(C,(p,H)::A) &={}
  \begin{cases}
    (H,\overline C)
      & \text{if }\mu_{\mathcal U}(p,C)=\overline C,\\
    \mathsf{select}_{\mathcal U}(C,A) & \text{if }\mu_{\mathcal U}(p,C)\uparrow.
  \end{cases}
\end{aligned}
$$

This makes first-match-wins explicit. Captures from a failed alternative are discarded before the next alternative is tried.

#### Typing in Typed Plutus Core

The typed language uses a universe-supplied pattern typing judgment

$$
\mathcal U;A\vdash p\Rightarrow\overline A,
$$

Read this as: “In builtin universe $\mathcal U$, pattern $p$ inspects a value of builtin type $A$ and produces captures with types $\overline A$.” This judgment is defined only when $A$ is represented by $\mathcal U$. The universe does not pass a pattern to another pattern. It defines which builtin patterns and constant types are available and how those patterns are typed.

Here, $A$ appears before the turnstile as the type inspected by $p$, while $\Rightarrow$ points to the capture types produced by the pattern. The sequence $\overline A=[A_1,\ldots,A_k]$ contains those capture types in handler-application order.

Let $B$ be the result type of the whole `Match` expression and therefore the result type that every selected handler must eventually produce. Define the handler type for a capture sequence by

$$
\begin{aligned}
\epsilon\Rightarrow B &= B,\\
(A::\overline A)\Rightarrow B &= A\to(\overline A\Rightarrow B).
\end{aligned}
$$

Thus a handler for no captures has type $B$. A handler whose first capture has type $A$ takes an $A$ argument, followed by the arguments required for the remaining capture types, and finally produces $B$.

In the rule below, $\Gamma$ is the term-variable typing context; type well-formedness is implicit.

The typing rule for matching is

$$
\mathrm{TY\_MATCH}\;
\frac{
  \Gamma\vdash M:A
  \qquad
  \forall i.\;\mathcal U;A\vdash p_i\Rightarrow\overline{A_i}
  \qquad
  \forall i.\;\Gamma\vdash H_i:\overline{A_i}\Rightarrow B
}{
  \Gamma\vdash
  \mathsf{match}\;M\;[(p_1,H_1),\ldots,(p_n,H_n)]:B
}.
$$

For an empty alternative list, this rule is admissible only when the expected result type $B$ is known or the syntax carries an explicit result-type annotation.

For `DefaultUni`, the leaf-pattern clauses are

$$
\begin{aligned}
\mathcal U;A\vdash\mathsf{wildcard}
  &\Rightarrow\epsilon,\\
\mathcal U;A\vdash\mathsf{bind}
  &\Rightarrow[A],\\
\mathcal U;\mathsf{integer}\vdash\mathsf{integer}(k)
  &\Rightarrow\epsilon,\\
\mathcal U;\mathsf{bytestring}\vdash\mathsf{bytestring}(b)
  &\Rightarrow\epsilon,\\
\mathcal U;\mathsf{bool}\vdash\mathsf{bool}(q)
  &\Rightarrow\epsilon,\\
\mathcal U;\mathsf{unit}\vdash\mathsf{unit}
  &\Rightarrow\epsilon.
\end{aligned}
$$

Pair captures are concatenated left-to-right:

$$
\frac{
  \mathcal U;A_L\vdash p\Rightarrow\overline{A_p}
  \qquad
  \mathcal U;A_R\vdash q\Rightarrow\overline{A_q}
}{
  \mathcal U;\mathsf{pair}\;A_L\;A_R\vdash
  \mathsf{pair}(p,q)\Rightarrow
  \overline{A_p}\mathbin{+\!+}\overline{A_q}
}.
$$

For a pattern sequence, capture types are concatenated from left to right:

$$
\mathcal U;A\vdash[]\Rightarrow\epsilon.
$$

$$
\frac{
  \mathcal U;A\vdash p\Rightarrow\overline{A_p}
  \qquad
  \mathcal U;A\vdash\bar p\Rightarrow\overline{A_{\bar p}}
}{
  \mathcal U;A\vdash(p::\bar p)\Rightarrow
  \overline{A_p}\mathbin{+\!+}\overline{A_{\bar p}}
}.
$$

The field-ending helper determines whether the remaining suffix contributes a capture type:

$$
\begin{aligned}
\mathsf{endTypes}(\mathsf{exact},A,\overline{A_p})
  &=\overline{A_p},\\
\mathsf{endTypes}(\mathsf{prefixWildcard},A,\overline{A_p})
  &=\overline{A_p},\\
\mathsf{endTypes}(\mathsf{prefixCapture},A,\overline{A_p})
  &=\overline{A_p}\mathbin{+\!+}[\mathsf{list}\;A].
\end{aligned}
$$

Here $e$ ranges over $\mathsf{exact}$, $\mathsf{prefixWildcard}$, and $\mathsf{prefixCapture}$. The complete list rule is

$$
\frac{
  \mathcal U;A\vdash\bar p\Rightarrow\overline{A_p}
}{
  \mathcal U;\mathsf{list}\;A\vdash
  \mathsf{list}_e(\bar p)\Rightarrow
  \mathsf{endTypes}(e,A,\overline{A_p})
}.
$$

Thus exact lists, prefix lists with an ignored suffix, and prefix lists with a captured suffix are all covered. Exact and prefix-wildcard patterns add only their child captures; prefix-capture patterns add one final list capture.

The field-bearing `Data` patterns use the same helper:

$$
\frac{
  \mathcal U;\mathsf{data}\vdash
  \bar p\Rightarrow\overline{A_p}
}{
  \mathcal U;\mathsf{data}\vdash
  \mathsf{dataConstr}_{t,e}(\bar p)\Rightarrow
  \mathsf{endTypes}(e,\mathsf{data},\overline{A_p})
}.
$$

$$
\frac{
  \mathcal U;\mathsf{data}\vdash
  \bar p\Rightarrow\overline{A_p}
}{
  \mathcal U;\mathsf{data}\vdash
  \mathsf{dataList}_e(\bar p)\Rightarrow
  \mathsf{endTypes}(e,\mathsf{data},\overline{A_p})
}.
$$

$$
\frac{
  \mathcal U;\mathsf{pair}\;\mathsf{data}\;\mathsf{data}
  \vdash\bar p\Rightarrow\overline{A_p}
}{
  \mathcal U;\mathsf{data}\vdash
  \mathsf{dataMap}_e(\bar p)\Rightarrow
  \mathsf{endTypes}
  (e,\mathsf{pair}\;\mathsf{data}\;\mathsf{data},\overline{A_p})
}.
$$

The scalar `Data` wrappers expose their enclosed builtin type to the child pattern:

$$
\frac{
  \mathcal U;\mathsf{integer}\vdash p\Rightarrow\overline{A_p}
}{
  \mathcal U;\mathsf{data}\vdash
  \mathsf{dataI}(p)\Rightarrow\overline{A_p}
}.
$$

$$
\frac{
  \mathcal U;\mathsf{bytestring}\vdash p\Rightarrow\overline{A_p}
}{
  \mathcal U;\mathsf{data}\vdash
  \mathsf{dataB}(p)\Rightarrow\overline{A_p}
}.
$$

Consequently, $\mathsf{dataI}(\mathsf{bind})$ captures an integer, while a plain $\mathsf{bind}$ at the same position captures `Data`. Likewise, $\mathsf{dataB}(\mathsf{bind})$ captures a byte string.

#### Term reduction

$$
\mathrm{MATCH\_CONSTANT}\;
\frac{
  \mathsf{select}_{\mathcal U}(C,A)=(H,\overline C)
}{
  \mathsf{match}\;\ulcorner C\urcorner\;A
  \longrightarrow\mathsf{apps}(H,\overline C)
}.
$$

$$
\mathrm{MATCH\_CONG}\;
\frac{
  M\longrightarrow M'
}{
  \mathsf{match}\;M\;A
  \longrightarrow\mathsf{match}\;M'\;A
}.
$$

$$
\mathrm{MATCH\_EXHAUSTED}\;
\frac{
  C\text{ is a builtin constant}
  \qquad
  \mathsf{select}_{\mathcal U}(C,A)=\mathsf{noMatch}
}{
  \mathsf{match}\;\ulcorner C\urcorner\;A
  \longrightarrow\mathsf{failure}_{\mathsf{match}}
}.
$$

$$
\mathrm{MATCH\_NONBUILTIN}\;
\frac{
  V\text{ is a value}
  \qquad
  V\text{ is not a builtin constant}
}{
  \mathsf{match}\;V\;A
  \longrightarrow\mathsf{failure}_{\mathsf{match}}
}.
$$

Here $\mathsf{failure}_{\mathsf{match}}$ is an evaluation failure raised by matching, not a UPLC `Error` term. Unselected handlers are not evaluation contexts. If there are $k$ captures, selection produces exactly $k$ ordinary applications and performs no handler-arity check.

#### The `DefaultUni` instance

Any combination not covered by an equation below is a mismatch.

##### Leaf patterns

For every builtin constant $C$:

$$
\begin{aligned}
\mu(\mathsf{wildcard},C) &= \epsilon,\\
\mu(\mathsf{bind},C) &= [C].
\end{aligned}
$$

Literal patterns match only constants of the corresponding universe type:

$$
\begin{aligned}
\mu(\mathsf{integer}(k),\langle\mathsf{integer},n\rangle)
  &=\epsilon &&\text{if }n=k,\\
\mu(\mathsf{bytestring}(b),\langle\mathsf{bytestring},b'\rangle)
  &=\epsilon &&\text{if }b=b',\\
\mu(\mathsf{bool}(q),\langle\mathsf{bool},q'\rangle)
  &=\epsilon &&\text{if }q=q',\\
\mu(\mathsf{unit},\langle\mathsf{unit},()\rangle)
  &=\epsilon.
\end{aligned}
$$

The `Int64` stored by `DefaultPatternInteger` is embedded into `Integer` before comparison.

##### Pairs

$$
\frac{
  \mu(p,\langle u,x\rangle)=\overline C_1
  \qquad
  \mu(q,\langle v,y\rangle)=\overline C_2
}{
  \mu(\mathsf{pair}(p,q),
  \langle\mathsf{pair}\;u\;v,(x,y)\rangle)
  =\overline C_1\mathbin{+\!+}\overline C_2
}.
$$

##### Homogeneous fields

Define

$$
\mathsf{prefix}_u([p_1,\ldots,p_k],[x_1,\ldots,x_m])
=\overline C_1\mathbin{+\!+}\cdots\mathbin{+\!+}\overline C_k
$$

exactly when $k\le m$ and $\mu(p_i,\langle u,x_i\rangle)=\overline C_i$ for every $1\le i\le k$. Otherwise it is undefined. Then

$$
\begin{aligned}
\mathsf{fields}_u(\mathsf{exact},\bar p,\bar x)
  &=\mathsf{prefix}_u(\bar p,\bar x)
  &&\text{only if }|\bar p|=|\bar x|,\\
\mathsf{fields}_u(\mathsf{prefixWildcard},\bar p,\bar x)
  &=\mathsf{prefix}_u(\bar p,\bar x),\\
\mathsf{fields}_u(\mathsf{prefixCapture},\bar p,\bar x)
  &=\mathsf{prefix}_u(\bar p,\bar x)
  \mathbin{+\!+}
  [\langle\mathsf{list}\;u,\mathsf{drop}_{|\bar p|}(\bar x)\rangle].
\end{aligned}
$$

The two prefix equations are defined only when $|\bar p|\le|\bar x|$. A prefix capture adds one capture even when the suffix is empty, and it does not traverse the suffix.

$$
\mu(\mathsf{list}_{e}(\bar p),
\langle\mathsf{list}\;u,\bar x\rangle)
=\mathsf{fields}_u(e,\bar p,\bar x).
$$

##### `Data`

$$
\begin{aligned}
\mu(\mathsf{dataConstr}_{t,e}(\bar p),
  \langle\mathsf{data},\mathsf{Constr}\;t'\;\bar D\rangle)
  &=\mathsf{fields}_{\mathsf{data}}(e,\bar p,\bar D)
  &&\text{if }t=t',\\
\mu(\mathsf{dataList}_{e}(\bar p),
  \langle\mathsf{data},\mathsf{List}\;\bar D\rangle)
  &=\mathsf{fields}_{\mathsf{data}}(e,\bar p,\bar D),\\
\mu(\mathsf{dataMap}_{e}(\bar p),
  \langle\mathsf{data},\mathsf{Map}\;\overline{(D,D')}\rangle)
  &=\mathsf{fields}_{\mathsf{pair}\;\mathsf{data}\;\mathsf{data}}
  (e,\bar p,\overline{(D,D')}),\\
\mu(\mathsf{dataI}(p),
  \langle\mathsf{data},\mathsf{I}\;n\rangle)
  &=\mu(p,\langle\mathsf{integer},n\rangle),\\
\mu(\mathsf{dataB}(p),
  \langle\mathsf{data},\mathsf{B}\;b\rangle)
  &=\mu(p,\langle\mathsf{bytestring},b\rangle).
\end{aligned}
$$

The `Word64` stored by `DefaultPatternDataConstr` is embedded into `Integer` before comparison with the `Data.Constr` tag.

#### Worked reductions

For

```lisp
(match (con data (Constr 7 [I 1, B #aa, I 9]))
  (pattern
    (data-constr 7 (data-i (bind)) (bind) (wildcard))
    handler)
  (pattern (wildcard) fallback))
```

the matching function returns

$$
[\langle\mathsf{integer},1\rangle,
 \langle\mathsf{data},\mathsf{B}\;\mathtt{\#aa}\rangle].
$$

The term reduces to

```lisp
[[handler (con integer 1)] (con data (B #aa))]
```

For

```lisp
(match (con (list integer) [1, 2, 3, 4])
  (pattern
    (list (prefix (integer 1) (bind) (bind)))
    handler))
```

the captures are the integer `2` and the list `[3, 4]`, so the selected term is

```lisp
[[handler (con integer 2)] (con (list integer) [3, 4])]
```

#### Costed operational refinement

NOTE: These costing step does not seem to well represent the cost of pattern works. I'm still testing different options. This section can be ignored for now.

The source-language reduction remains atomic. The CEK machine refines selection with an explicit work stack and an incrementally costed judgment:

$$
\mathsf{select}_{\mathcal U}(C,A)
\Downarrow^{(n_P,n_S,n_N)}(H,\overline C),
$$

or the corresponding $\mathsf{noMatch}$ result, where:

- $n_P$ counts ordinary pattern-work units (`BPattern`): the initial alternative/root probe, including the empty-alternative check; prefix endpoints; equal-length byte-string precharge units; and two units for every reached capture. Nested child dispatch is covered by the preceding `BStructural` event, while a later alternative's root probe is bundled into `BMatchNext`.
- $n_S$ counts reached structural child or field edges (`BStructural`), including child dispatch and bounded exact-arity probing.
- $n_N$ counts transitions after a known mismatch (`BMatchNext`), including abandoning the failed attempt and probing the next alternative, or discovering exhaustion after the final mismatch.

If the three cost-model entries are $c_P,c_S,c_N$, the match-selection component is

$$
n_Pc_P+n_Sc_S+n_Nc_N.
$$

Entering the AST node separately incurs `cekMatchCost`. Evaluating the scrutinee and selected handler retains the usual CEK costs. Applications introduced by `Match` do not create syntactic `Apply` nodes and do not incur `BApply`; the second `BPattern` unit for each reached capture prepays its implicit handler application. These charges are not refunded if the alternative later fails.

For equal-length byte strings, equality prepays

$$
\max\left(1,\left\lceil\frac{|b|}{8}\right\rceil\right)
$$

`BPattern` units before native equality. Unequal lengths fail from length metadata without that per-word precharge. An ignored or captured prefix suffix is not walked.

The costed judgment must erase to the pure result:

$$
\mathsf{select}_{\mathcal U}(C,A)\Downarrow^w R
\quad\Longrightarrow\quad
\mathsf{select}_{\mathcal U}(C,A)=R.
$$

The event placement is normative. The coefficients $c_P,c_S,c_N$ are pre-activation working values and require calibration before ledger activation.

### Versioning

`Match` is introduced in Plutus Core language version 1.2.0 and is invalid in earlier language versions. Existing language versions and existing `Case` terms retain their current syntax and behavior.

The specification version of this feature is therefore Plutus Core language version 1.2.0. Any incompatible change to the syntax, serialization, or evaluation behavior specified here requires a subsequent language version. Compatible clarifications to this document may follow the normal CIP revision process.

## Rationale: How does this CIP achieve its goals?

### Direct and recursive deconstruction

`Match` attaches explicit patterns to alternatives, allowing a program to select a handler based on the value and shape of a builtin constant. Recursive patterns allow a program to reach a needed field without constructing and evaluating a chain of partial destructors and guards. Captures expose only the values needed by the selected handler.

This is particularly useful for known `Data` structures. A script can match a constructor tag, check nested structure, and capture selected fields in a single evaluator operation.

### Relationship to `Case`

`Match` is functionally more expressive than builtin-value `Case`. For example:

```lisp
(case 4
  (error)
  (con integer 10)
  (error)
  (error)
  (con integer 20))
```

can be written as:

```lisp
(match 4
  (pattern (integer 1) (con integer 10))
  (pattern (integer 4) (con integer 20)))
```

This can reduce script size because `Match` names the integer values of interest instead of requiring all preceding branches to be present.

This proposal does not deprecate builtin-value `Case`. For shallow operations such as unconsing a list or matching a boolean, `Case` should remain faster because it avoids initializing and traversing the general matcher.

### Incremental costing

Pattern size alone does not determine runtime work: an early mismatch may inspect only a prefix, while a successful nested pattern may traverse many fields. Incremental charging follows the work actually performed and ensures that arbitrary patterns remain bounded by the script budget.

An alternative design computed each pattern's size before matching. It reduced evaluator overhead but required either:

- the Flat decoder to inject the encoded pattern size into the AST, making decoding part of the trusted costing path; or
- an uncosted look-ahead traversal before matching.

Neither requirement was justified by the measured performance benefit, so this proposal uses incremental costing.

### Alternatives considered

#### Direct `Data` casing

Assigning the five `Data` constructors to fixed `Case` branches is simple but mainly accelerates `chooseData`. It does not efficiently deconstruct known nested structures, which is the common script-context use case.

#### Multi-lambda and multi-application

Atomic application of multiple arguments can detect constructor-field arity mismatches, but it requires two new language terms and specialized CEK behavior. It also raises a distinction between ordinary nested lambdas and multi-lambdas while providing only limited matching functionality.

#### A dedicated `Let` term

A `Let` term could bind a row of values but still requires CEK support for that row and overlaps with lambda/application as a binding mechanism. Like multi-lambda, it does not provide general nested matching.

The proposed `Match` term concentrates these use cases into one ordered pattern-matching operation and integrates with the CEK in a manner similar to `Case`.

### Backward compatibility

The change is backward-compatible at the Plutus Core language level because `Match` is guarded by a new minor language version. Scripts using earlier versions continue to parse and evaluate with unchanged semantics.

Nodes and tools that do not support the new language version cannot accept scripts using `Match`; activation therefore requires a hard fork that introduces the language version and its cost-model parameters. No existing script is rewritten, and `Case` remains available.

### Performance

The following local benchmarks compare `Match` with existing deconstruction using partial builtins, optionally guarded by `chooseData`, or builtin `Case`. They measure CEK wall-clock time rather than calibrated on-chain execution units.

#### Capturing one deeply positioned value

| Input and target                  | Traditional baseline      | Traditional CEK | `Match` CEK | Traditional / `Match` |
|-----------------------------------|---------------------------|----------------:|------------:|----------------------:|
| `Data.Constr`, field 1,024        | direct `UnConstrData`     |       33.628 us |    5.119 us |                 6.50x |
|                                   | guarded with `ChooseData` |       33.479 us |    5.230 us |                 6.38x |
| `Data.List`, field 1,024          | direct `UnListData`       |       33.775 us |    5.283 us |                 6.42x |
|                                   | guarded with `ChooseData` |       33.525 us |    5.150 us |                 6.56x |
| Builtin list, element 1,024       | builtin `Case`            |       33.675 us |    5.131 us |                 6.51x |
| 64 nested `Data.Constr` layers    | direct destructors        |       21.719 us |    2.240 us |                 9.70x |
|                                   | guarded with `ChooseData` |       31.068 us |    2.297 us |                13.74x |
| 64 nested `Data.List` layers      | direct destructors        |       13.108 us |    1.969 us |                 6.67x |
|                                   | guarded with `ChooseData` |       21.523 us |    2.001 us |                10.67x |
| 64 alternating Constr/List layers | direct destructors        |       17.998 us |    2.127 us |                 8.46x |
|                                   | guarded with `ChooseData` |       26.110 us |    2.158 us |                12.10x |

Each benchmark captures the innermost value. For a wide list, this is the last element; for nested structures, this is the innermost value. In these cases, `Match` is at least six times faster in the measured CEK runtime.

#### Capturing multiple values

| Input and target                                | Traditional baseline      | Traditional CEK | `Match` CEK | Traditional / `Match` |
|-------------------------------------------------|---------------------------|----------------:|------------:|----------------------:|
| `Data.Constr`, all 1,024 fields captured        | direct `UnConstrData`     |       35.523 us |   20.502 us |                 1.75x |
|                                                 | guarded with `ChooseData` |       35.257 us |   20.674 us |                 1.67x |
| `Data.List`, all 1,024 fields captured          | direct `UnListData`       |       34.978 us |   20.359 us |                 1.72x |
|                                                 | guarded with `ChooseData` |       35.297 us |   20.712 us |                 1.72x |
| Builtin list, all 1,024 elements captured       | builtin `Case`            |       34.369 us |   20.443 us |                 1.68x |
| 64 nested `Data.Constr` layers, 192 captures    | direct destructors        |       21.252 us |    4.929 us |                 4.29x |
|                                                 | guarded with `ChooseData` |       31.078 us |    5.091 us |                 6.10x |
| 64 nested `Data.List` layers, 192 captures      | direct destructors        |       12.887 us |    4.943 us |                 2.59x |
|                                                 | guarded with `ChooseData` |       21.461 us |    4.935 us |                 4.30x |
| 64 alternating Constr/List layers, 192 captures | direct destructors        |       17.663 us |    5.075 us |                 3.48x |
|                                                 | guarded with `ChooseData` |       26.182 us |    5.041 us |                 5.21x |

Capturing values is more expensive because each captured value must be stored and later applied to the handler. The performance gap therefore narrows when every field is captured, but all measured cases remain faster with `Match`.

The cost parameters used for these measurements are not fully calibrated. Preliminary CPU and memory budgets improved by between 10% and 90%, depending on the amount of capture work. Typical script-context use is expected to capture only a few fields; with the initial conservative parameters, the observed budget improvement in those cases was approximately 40% to 60%.

## Path to Active

### Acceptance Criteria

- [ ] The `plutus` repository contains an updated Plutus Core specification defining:
  - [ ] the `Match` term and default-universe pattern syntax;
  - [ ] textual and Flat serialization;
  - [ ] ordered matching, capture application, mismatch, and failure semantics; and
  - [ ] Plutus Core language version 1.2.0 as the version that introduces the feature.
- [ ] The `plutus` repository contains:
  - [ ] a production implementation of syntax, serialization, and CEK evaluation;
  - [ ] conformance tests covering scalar, structural, nested, prefix, exact, capture, fallback, and failure behavior;
  - [ ] calibrated costs for `BMatch`, `BPattern`, `BStructural`, and `BMatchNext`; and
  - [ ] benchmarks showing the effect on representative and adversarial inputs.
- [ ] External implementations or independent test implementations are available.
- [ ] The ledger supports the new Plutus Core language version and all required cost-model parameters.
- [ ] The feature is released in a Cardano node version.
- [ ] The released implementation is present in block-producing nodes representing at least 80% of active stake.

### Implementation Plan

The reference implementation adds `Match` to UPLC and its Flat encoding, implements universe-specific matching in the CEK machine, and provides costing, benchmarks, and conformance tests in the `plutus` repository.

The main matching rules are implemented in `plutus-core/plutus-core/src/PlutusCore/Default/Universe.hs`. CEK evaluation and incremental costing are implemented in `plutus-core/untyped-plutus-core/src/UntypedPlutusCore/Evaluation/Machine/Cek/Internal.hs`.

The change requires Plutus Core language version 1.2.0 and new cost-model parameters. Under CIP-0035, these are introduced through a hard fork. Ledger integration must gate the new language version and supply the calibrated parameters. Activation should occur only after specification review, cost calibration, conformance testing, independent implementation or test implementation, and release in the node.

## References

- [CIP-0001: CIP Process](https://cips.cardano.org/cip/CIP-0001)
- [CIP-0035: Plutus Core Evolution](https://cips.cardano.org/cip/CIP-0035)
- [CIP-0085: Sums-of-products in Plutus Core](https://cips.cardano.org/cip/CIP-0085)
- [IntersectMBO/plutus issue #5777](https://github.com/IntersectMBO/plutus/issues/5777)
- [IntersectMBO/plutus issue #6225](https://github.com/IntersectMBO/plutus/issues/6225)
- [IntersectMBO/plutus issue #6602](https://github.com/IntersectMBO/plutus/issues/6602)
- [IntersectMBO/plutus pull request #7209](https://github.com/IntersectMBO/plutus/pull/7209)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
