---
CIP: 152
Title: Modules in UPLC
Status: Proposed
Category: Plutus
Authors:
  - John Hughes <john.hughes@quviq.com>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/946
Created: 2024-11-12
License: CC-BY-4.0
---
## Abstract

Cardano scripts are limited in complexity by the fact that each script
must be supplied in one transaction, whether the script is supplied in
the same transaction in which it is used, or pre-loaded onto the chain
for use as a reference script. This limits script code size, which in
turn limits the use of libraries in scripts, and ultimately limits the
sophistication of Cardano apps, compared to competing blockchains. The
script size limit is an aspect of Cardano that script developers
commonly complain about.

This CIP addresses this problem directly, by allowing reference inputs
to supply 'modules', which can be used from other scripts (including
other modules), thus allowing the code of a script to be spread across
many reference inputs. The 'main specification' requires *no* changes to
UPLC, PTLC, PIR or Plinth; only a 'dependency resolution' step before
scripts are run. Many variations are described for better performance,
including some requiring changes to the CEK machine itself.

Higher performance variations will be more expensive to implement; the
final choice of variations should take implementation cost into
account, and (in some cases) may require extensive benchmarking.

## Motivation: Why is this CIP necessary?

Cardano scripts are currently subject to a fairly tight size limit,
deriving from the overall limit on transaction size; even when a
script is supplied in a reference UTxO, that UTxO must itself be
created by a single transaction, which is subject to the overall
transaction size limit. Competing blockchains suffer from no such
limit: on the Ethereum chain, for example, contracts can call one
another, and so the code executed in one transaction may come from
many different contracts, created independently on the
blockchain--each subject to a contract size limit, but together
potentially many times that size. This enables more sophisticated
contracts to be implemented; conversely, on Cardano, it is rather
impractical to implement higher-level abstractions as libraries,
because doing so will likely exceed the script size limit. This is not
just a theoretical problem: complaints about the script size limit are
commonly made by Cardano contract developers.

Thus the primary goal of this CIP is to lift the limit on the total
amount of code run during a script execution, by allowing part of the
code to be provided in external modules. By storing these modules on
the blockchain and providing them as reference UTxOs, it will be
possible to keep transactions small even though they may invoke a large
volume of code.

Once scripts can be split into separate modules, then the question
immediately arises of whether or not the script and the modules it
imports need to be in the same language. Today there are many
languages that compile to UPLC, and run on the Cardano
blockchain. Ideally it should be possible to define a useful library
in any of these languages, and then use it from all of them. A
secondary goal is thus to define a module system which permits this,
by supporting cross-language calls.

Note that many languages targetting UPLC already support modules. In
particular, Plinth already enjoys a module system, namely the Haskell
module system. This already enables code to be distributed across
several modules, or put into libraries and shared. Indeed this is
already heavily used: the DJED code base distributes Plinth code
across 24 files, of which only 4 contain top-level contracts, and the
others provide supporting code of one sort or another. Thus the
software engineering benefits of a module system are already
available. The *disadvantage* of this approach is that all the code is
combined into one script, which can easily exceed the size limit as a
result. Indeed, the DJED code base also contains an implementation of
insertion sort in Plinth, with a comment that a quadratic algorithm is
used because its code is smaller than, for example, QuickSort. There
is no clearer way to indicate why the overall limit on code size must be
lifted.

### The Situation on Ethereum

Ethereum contracts are not directly comparable to Cardano scripts;
they correspond to both the *on-chain* and the *off-chain* parts of
Cardano contracts, so one should expect Ethereum contracts to require
more code for the same task, since in Cardano only the verifiers need
to run on the chain itself. Nevertheless, it is interesting to ask
whether, and how, the need for modules has been met in the Ethereum
context.

Solidity does provide a notion of 'library', which collects a number
of reusable functions together. Libraries can be 'internal' or
'external'--the former are just compiled into the code of client
contracts (and so count towards its size limit), while the latter are
stored separately on the blockchain.

There is a problem of trust in using code supplied by someone else:
the documentation for the `ethpm` package manager for Ethereum warns
sternly

**you should NEVER import a package from a registry with an unknown or
  untrusted owner**

It seems there *is* only one trusted registry, and it is the one
supplied as an example by the developers of `ethpm`. In other words,
while there is a package manager for Ethereum, it does not appear to
be in use.

This is not to say that code is never shared. On the contrary, there
is an open source repo on `github` called `OpenZeppelin` which appears
to be heavily used. It provides 264 Solidity files, in which 43
libraries are declared (almost all internal). It seems, thus, that
libraries are not the main way of reusing code in Solidity; rather it
is by calling, or inheriting from, another contract, that code reuse
primarily occurs.

A small study of 20 'verified' contracts running on the Ethereum chain
(verified in the sense that their source code was provided) showed that

* 55% of contracts consisted of more than one module
* 40% of contracts contained more than one 'application' module
* 55% of contracts imported `OpenZeppelin` modules
* 10-15% of contracts imported modules from other sources
* 5% of contracts were simply copies of `OpenZeppelin` contracts

Some of the 'other' modules were provided to support specific
protocols; for example Layr Labs provide modules to support their
Eigenlayer protocol for re-staking.

A sample of 20 is too small to draw very strong statistical conclusions,
but we can say that the 95% confidence interval for contracts to
consist of multiple modules is 34-74%.
Thus code sharing is clearly going on, and a significant number of
transactions exploit multiple modules. We may conclude that there is a
significant demand for modules in the context of smart contracts, even
if the total contract code still remains relatively small.


## Specification

### Adding modules to UPLC

This CIP provides the simplest possible way to split scripts across
multiple UTxOs; essentially, it allows any closed subterm to be
replaced by its hash, whereupon the term can be supplied either as a
witness in the invoking transaction, or via a [reference script](https://cips.cardano.org/cip/CIP-0033) in that
transaction. To avoid any change to the syntax of UPLC, hashes are
allowed only at the top-level (so to replace a deeply nested subterm
by its hash, we need to first lambda-abstract it). This also places
all references to external terms in one place, where they can easily
be found and resolved. Thus we need only change the definition of a
`Script`; instead of simply some code, it becomes the application of
code to zero or more arguments, given by hashes.

Currently, the definition of “script” used by the ledger is (approximately):
```
newtype Script = Script ShortByteString
```
We change this to:
```
newtype CompleteScript = CompleteScript ShortByteString

newtype Arg = ScriptArg ScriptHash

data Script =
  ScriptWithArgs { head :: CompleteScript, args :: [Arg] }

-- hash of a Script, not a CompleteScript
type ScriptHash = ByteString
```

Scripts in transactions, and on the chain, are represented in this
way, with dependencies that must be supplied in a transaction using
the script. During phase 2 verification we need to resolve the
arguments of each script before running it:
```
resolveScriptDependencies
  :: Map ScriptHash Script
  -> Script
  -> Maybe CompleteScript
resolveScriptDependencies preimages = go
  where
    go (ScriptWithArgs head args) = do
      argScripts <- traverse lookupArg args
      pure $ applyScript head argScripts
      where
        lookupArg :: Arg -> Maybe CompleteScript
        lookupArg (ScriptArg hash) = do
          script <- lookup hash preimages
          go script
```
The `preimages` map is the usual witness map constructed by the ledger,
so in order for a script hash argument to be resolved, the transaction
must provide the pre-image in the usual way. Note that arguments are
mapped to a `Script`, not a `CompleteScript`, so the result of looking
up a hash may contain further dependencies, which need to be resolved
recursively. A transaction must provide witnesses for *all* the
recursive dependencies of the scripts it invokes.

The only scripts that can be run are complete scripts, so the type of
`runScript` changes to take a `CompleteScript` instead of a `Script`.

#### Variation: Lazy Loading

With the design above, if any script hash is missing from the `preimages`,
then the entire resolution fails. As an alternative, we might replace
missing subterms by a dummy value, such as `builtin unit`, thus:
```
resolveScriptDependencies
  :: Map ScriptHash Script
  -> Script
  -> CompleteScript
resolveScriptDependencies preimages = go
  where
    go (ScriptWithArgs head args) =
      applyScript head (map lookupArg args)
      where
        lookupArg :: Arg -> CompleteScript
        lookupArg (ScriptArg hash) = do
          case lookup hash preimages of
	    Nothing     -> builtin unit
	    Just script -> go script
```
This would allow transactions to provide witnesses only for script
arguments which are actually *used* in the calls that the transaction
makes. This may sometimes lead to a significant reduction in the
amount of code that must be loaded; for example, imagine a spending
verifier which offers a choice of two encryption methods, provided as
separate script arguments. In any call of the verifier, only one
encryption method will be required, allowing the other (and all its
dependencies) to be omitted from the spending transaction.

#### Variation: Value Scripts

The goal of this variation is to eliminate the cost of evaluating
scripts, by converting them directly to values (in linear time). Since
UPLC runs on the CEK machine, this means converting them directly into
the `CekValue` type, *without* any CEK machine execution. To make this
possible, the syntax of scripts is restricted so that those parts that
would be evaluated during an application to the script arguments are
already (UPLC) values. That is, script code is syntactically
restricted to explicit λ-expressions with one λ per `ScriptArg`,
followed by a syntactic value. (Values are constants, variables,
built-ins, λ-abstractions, delayed terms, and SoP constructors whose
fields are also values).

This means that every script must take the form
`λA1.λA2....λAn.<value>`, where `n` is the number of `ScriptArg`s
supplied. Now, since variables in `CompiledCode` are de Bruijn indices
then the `n` λs can be omitted from the representation--we know how
many there must be from the number of `ScriptArg`s, and the names
themselves can be reconstructed.

There must be a dynamic check that the code of each script really is
of this form, but this check can be built into deserialization, and
thus need cost very little.

`Script`s in this restricted form can be mapped directly into CEK
values, without any CEK-machine evaluation steps. In pseudocode:
```
scriptCekValue
  :: Map ScriptHash CekValue
  -> Script
  -> CekValue
scriptCekValue scriptValues (ScriptWithArgs head args) =
  cekValue (Env.fromList [case lookup h scriptValues of
	   		    Just v -> v
			    Nothing -> vbuiltin unit
	   		 | ScriptArg h <- args])
	   (deserialize (getPlc head))

```
That is, a script is turned into a value by creating a CEK machine
environment from the values of the `ScriptArg`s, and converting the
body of the script (a syntactic value) in a CekValue in that
environment.

This pseudocode follows the 'lazy loading' variation; an easy
variation treats not finding a script hash as an error.

Syntactic values are turned into `CekValue`s by the following
function, which is derived by simplifying `computeCek` in
UntypedPlutusCore.Evaluation.Machine.Cek.Internal, and restricting it
to syntactic values.
```
cekValue
  :: Env
  -> NTerm
  -> CEKValue
cekValue env t = case t of
  Var _ varname      -> lookupVarName varName env
  Constant _ val     -> VCon val
  LamAbs _ name body -> VLamAbs name body env
  Delay _ body       -> VDelay body env
  Builtin _ bn       ->
    let meaning = lookupBuiltin bn ?cekRuntime in
    VBuiltin bn (Builtin () bn) meaning
  Constr _ i es      ->
    VConstr i (foldr ConsStack EmptyStack (map (cekValue env) es)
  _                  -> error
```
Converting a syntactic value to a CekValue does require traversing it,
but the traversal stops at λs and delays, so will normally traverse
only the top levels of a term.

Finally, if `preimages` is the `Map ScriptHash Script` constructed from
a transaction, then we may define
```
scriptValues = Map.map (scriptCekValue scriptValues) preimages
```
to compute the CekValue of each script.

Scripts are then applied to their arguments by building an initial CEK
machine configuration applying the script value to its argument value.



Note that this recursive definition of `scriptValues` could potentially allow an
attacker to cause a black-hole exception in the transaction validator,
by submitting a transaction containing scripts with a dependency
cycle. However, since scripts are referred to by hashes, then
constructing such a transaction would require an attack on the hash
function itself... for example a script hash `h` and values for `head`
and `args` such that
```
h = hash (Script head (h:args))
```
We assume that finding such an `h` is impossible in practice; should
this not be the case, or if we should wish to defend against an
attacker with the resources to find such an attack on the hash
function, then we must build a script dependency graph for each
transaction and check that it is acyclic before evaluating the scripts
in this way.

##### Cost

Converting `Script`s to `CekValue`s does require a traversal of all
`Script`s, and the top level of each `Script` value. This is linear
time in the total size of the scripts, though, and should be
considerably faster than doing the same evaluation using CEK machine
transitions. The conversion can be done *once* for a whole
transaction, sharing the cost between several scripts if they share
modules (such as frequently used libraries). So costs should be
charged *for the whole transaction*, not per script. The most accurate
cost would be proportional to the total size of values at the
top-level of scripts. A simpler approach would be to charge a cost
proportional to the aggregated size of all scripts, including
reference scripts--although this risks penalizing complex scripts with
a simple API.

##### Implementation concerns
The CEK implementation does not, today, expose an API for starting
evaluation from a given configuration, or constructing `CekValue`s
directly, so this variation does involve significant changes to the
CEK machine itself.

##### Subvariation: Module-level recursion

Many modules define recursive functions at the top-level. In this
variation, the innermost body of a script is further restricted to the
form `λSelf.<value>`, and `resolveScriptDependencies` applies an
implicit `fix` to the script body, after supplying the script
arguments.  Like the other λs binding script arguments, the `λSelf.`
need not appear in the actual representation; we know it has to be
there so we can just store the body of the `λ`. When a script is
evaluated, the value of the script is just added to the environment in
the same way as the script arguments. The script can then refer to
its own value using `Self`.

#### Variation: Explicit lambdas

This variation is a less-restrictive version of 'value scripts'. As in
the former case, we restrict scripts syntactically to explicit
λ-expressions binding the script arguments, but we do not restrict the
script body proper to be a syntactic value. As in the former case, the
λs need not be present in the `Script` representation, because their
number is known from the number of script arguments, and the bound
variables are deBruijn indices.

In this variation, script bodies cannot be converted to `CekValue`s
using `cekValue`; we actually have to run the CEK machine to evaluate
them. This requires extending the API of the CEK machine, to support
evaluating a UPLC term *in a given environment*, and returning a
`CekValue`, rather than a discharged `NTerm`, because discharging a
`CekValue` loses sharing. Losing sharing is unacceptable because it
introduces a potentially exponential space cost for acyclic
structures, and leads to non-termination in the case of cyclic
structures (created by 'Module-level recursion').

The implementation of the CEK machine currently always discharges
values before returning them; the core loop of the machine will need
to be modified to change this.

Since script bodies must be evaluated by running the CEK machine, then
it is possible to exceed the execution unit budget at any point during
the script evaluation. The budget must be checked during these
evaluations, and the budget for evaluating each script will depend on
the actual costs of evaluating all the previous ones.

To avoid circular dependencies, the scripts must be topologically
sorted before evaluation, so that no earlier script depends on a later
one. Topological sorting is linear time in the total number of scripts
and script arguments.

It is still possible to write a recursive definition of the
`scriptValues`, so that each script can depend on the *same* map, but
care is needed to avoid circular dependencies for the reasons
explained above.

#### A Note on Tuples

The following variations make heavy use of tuples which in practice
could grow quite large--tuples of modules, and modules as tuples of
exports. These variations only make sense if projection of a component
from a tuple is *efficient*, and in particular, constant time,
independent of the tuple size. At present, tuples are represented
using the SoP extension (CIP-85) as `constr 0 x1...xn`, but the only
way to select the `i`th component is using
```
  case t of (constr 0 x1...xi...xn) -> xi
```
which takes time linear in the size of the tuple to execute, because
all `n` components need to be extracted from the tuple and passed to
the case branch (represented by a function).

We assume below that there is an expression `proj i t` in UPLC, where
`i` is a constant, which efficiently extracts the `i`th component from
tuple `t`. There are several ways this could be implemented:

* `proj i t` could be added as a new construct to UPLC, together with
  extensions to the CEK machine to evaluate it.
* `proj` could be added as a new built-in to UPLC--probably a smaller
  change to the implementation, but less efficient (because `i` would
  be an argument needing evaluation, rather than a constant integer in
  the AST), and problematic to add to TPLC (because typing it requires
  dependent types).
* represent 'tuples' in this context as functions from indices to
  components, so `(x,y,z)` would be represented as
  ```
  λi. case i of 0 -> x
      	     	1 -> y
		2 -> z
  ```
  This requires support in UPLC for pattern-matching on integers in
  constant time, which is not implemented right now, but is on the
  horizon. It would also need dependent types to be typed, and so
  cannot be added to Plinth, PIR or PTLC.

In the sections below we just use tuples and the notation `proj i t`,
on the assumption that an implementation is chosen and deployed.

#### Variation: Tuples of modules

In the main specification in this CIP, script code is a curried
function of the script arguments; that is, imported modules are
supplied to scripts as individual arguments. In this variation, the
script code is instead an *uncurried* function of the script
arguments, which are tupled together to be passed to the script code.

This variation only makes sense if the 'value scripts' variation is
also adopted, and places an additional syntactic restriction on script
code: it must be of the form `λMods.e`, and all occurrences of `Mods`
in `e` must be of the form `proj i Mods` for some `i`. That is, it is
impossible to refer to the whole tuple of modules; scripts can refer
to only one module at a time.

To avoid additional overheads for scripts without arguments, we
redefine the `Script` type as follows:
```
data Script =
    CompleteScript CompleteScript
  | ScriptWithArgs { head :: CompleteScript, args :: [Arg] }
```
Here the `CompleteScript` alternative is used for scripts without
script arguments; such scripts are not applied to a tuple of modules
before use, and so need not be of the form `λMods.e`. (This is only
needed because a 'function of zero arguments' has no overhead, while a
function of a zero-tuple does).

##### Subvariation: Global module environment

In the 'tuples of modules' variation, each script is paremeterised on
a tuple of modules, and fetches the modules when needed by projecting
out a component of the tuple. In the 'global module environment'
subvariation, *all* the modules are placed in *one* tuple, from which
scripts fetch the modules they need.

The global module environment is constructed for the transaction as a
whole, containing all the scripts provided by the transaction. It
follows that the *same* module may end up in *different* components in
different transactions. Scripts refer to other modules via references
of the form `proj i Mods`, where `Mods` is the variable bound to the
tuple of modules. Before scripts are run, these references must be
replaced by `proj j Mods`, where `j` is the index of the corresponding
module in the global module environment. Thus it is necessary to
traverse the code of all the scripts, relocating module references to
refer to the global module environment instead. One this is done, then all
the script values can refer to the *same* tuple of modules.

###### Subsubvariation: Module environment built into the CEK machine

In this subsubvariation, the (single) tuple of modules is passed (as a
new implicit parameter) directly to the CEK machine, instead of being
passed as a parameter in UPLC. Consequently it cannot be accessed as a
UPLC variable; new UPLC constructs are needed instead. Since
references to the global tuple of modules always refer to a
*particular* module, then it suffices to add a construct of the form
```
data Term name uni fun ann = ..  | ModuleRef Int
```
such that `ModuleRef i` evaluates to the `i`th component of the global
module tuple.

Once again, the scripts provided in a transaction must refer to script
arguments using an index into *the script's own* script arguments;
before execution these indices must be replaced by the corresponding
indices in the global module environment, necessitating a traversal of
the script code to prepare it for execution.

##### Subvariation: Unboxed modules

In this subvariation, we distinguish between validation scripts and
scripts representing modules; the latter are subject to an additional
syntactic restriction that the script body must be a tuple. We change
the `Script` type accordingly
```
data Script = ValidatorScript         CompiledCode [ScriptArg]
            | ModuleScript            CompiledCode [ScriptArg]
```
so that the deserializer can easily check the new syntactic
restriction. `Script`s used as `ScriptArg`s may only be of the
`ModuleScript` form (this requires a dynamic check). The idea is that
a module provides a number of exports, which are the components of the
tuple. (Again, special cases for an empty list of script arguments
can be included in this type if desired).

In addition, expressions `M` referring to modules (of the form `proj j
Mods`) may only appear in contexts of the form `proj i M`, projecting
out one of the module exports. We call these terms 'export
references'.

With this restriction, a tuple of modules is now a tuple of tuples,
and the effect of the subvariation is to flatten that into a tuple of
exports instead. Every module export is assigned an index in the
resulting tuple, and the scripts must be preprocessed before execution
to replace the indexes in every export reference by the corresponding
index in the tuple--so `proj i (proj j Mods)` becomes `proj k Mods`
for `k` the index of the `i`th export of the `j`th module.

In the case of modules which are omitted from the transaction (see
'lazy loading'), the export references `proj i (proj j Mods)` should
be replaced by `builtin unit`. This is either the correct value, or
will cause a run-time type error (and thus verification failure) if
the value is used.

In the case of a global module environment, then since the placement
of modules in a global tuple depends on *all* the modules used in a
transaction, and since some of the scripts used by a transaction are
taken from pre-existing reference UTxOs, then this preprocessing
cannot be done in advance; it must be done during script verification
of the transaction.  This subvariation can be combined with 'module
environment built into the CEK machine', in which case the export
references are replaced by suitable `ModuleRef k` expressions as
before.  It does not change the `CompiledCode` stored in scripts; it
only affects the way that code is prepared for execution.

If the module environment is *local* for each script, then the
preprocessing can be done at *compile-time*--and scripts on the chain
can be stored as functions of one big tuple, containing all the
exports from modules imported into the script. There is a subtlety in
the case of lazy loading: `resolveScriptDependencies` becomes
responsible for creating a tuple with one entry per export, *even for
modules which are not provided in the transaction*. For this to be
possible, `resolveScriptDependencies` needs to know *how many* exports
the imported module has, even without access to its body. To make this
possible we can extend the `ScriptArg` type:
```
data ScriptArg = ScriptArg ScriptHash Int
```
In the case of a module which *is* supplied, there should be a dynamic
check that the number of components agrees with the `ScriptArg`; in
the case of a module which is not supplied in the transaction,
`resolveScriptDependencies` should just add this number of `builtin
unit`s to the tuple passed to the script. Note that an attacker could
force the transaction verifier to allocate a very large amount of
memory by supplying a very large integer here, in a transaction that
does not include the module itself--and so might be cheap. To prevent
this, transaction fees must take the *values* of these integers into
account; it may also be sensible to place an absolute upper limit on
the number of exports from a module.

##### Script traversal costs

The last two subvariations above both require a traversal of all the
script code in a transaction (including the code fetched from
reference scripts) to adjust module or export references. If they are
adopted, transaction fees should be increased by an amount linear in
the total script size to pay for this traversal.

### Modules in TPLC

No change is needed in TPLC.

### Modules in PIR

No change is needed in PIR.

### Modules in Plinth

The Plinth modules introduced in this CIP bear no relation to Haskell
modules; their purpose is simply to support the module mechanism added
to UPLC. They are first-class values in Haskell.

Just as we introduced a distinction in UPLC between `CompleteScript`
and `Script`, so we introduce a distinction in Plinth between
`CompiledCode a` (returned by the Plinth compiler when compiling a
term of type `a`), and `Module a` representing a top-level `Script`
with a value of type `a`.
```
newtype Module a = Module {unModule :: Mod}

newtype ModArg = ModArg ScriptHash

data Mod = forall b. Mod{ modCode :: Maybe (CompiledCode b),
     	   	     	  modArgs :: Maybe ([ModArg]),
			  modHash :: ScriptHash }
```

Here the `modArgs` correspond to the `ScriptArg`s in the UPLC case,
and the `modHash` is the hash of the underlying `Script`.  The type
parameter of `Module a` is a phantom parameter, just like the type
parameter of `CompiledCode a`, which tells us the type of value which
the application of the `modCode` to the `modArgs` represents.

We can convert any `ScriptHash` into a module:
```
fromScriptHash :: ScriptHash -> Module a
fromScriptHash hash = Module Nothing Nothing hash
```
and we can convert any `CompiledCode` into a module:
```
makeModule :: CompiledCode a -> Module a
makeModule code = Module (Just (Mod code)) (Just []) ...compute the script hash...
```

We also need a way to supply an imported module to a `Module`:
```
applyModule :: Module (a->b) -> Module a -> Module b
applyModule (Module (Mod (Just code) (Just args) _)) m =
  Module (Mod (Just code) (Just (args++[modHash m])) ...compute the script hash...)
```
As in UPLC, the intention is that scripts that import modules be
written as lambda-expressions, and the imported module is then
supplied using `applyModule`. No change is needed in the Plinth
compiler to support this mechanism.

Note that only a `Module` containing code and an argument list can
have the argument list extended by `applyModule`; this is because the
`ScriptHash` of the result depends on the code and the entire list of
arguments, so it cannot be computed for a module that lacks either of
these.

It is `Module` values that would then be serialised to produce scripts
for inclusion in transactions.

In the 'unboxed modules' variation we need to distinguish two kinds of
scripts, scripts which define modules, and scripts which define
validators. In Plinth, this distinction can be made in the types, by
turning the `Module` type into a GADT with an extra parameter, of type
```
data ScriptType = ModuleScript | ValidatorScript
```
`applyModule` would be given a more restrictive type:
```
applyModule :: Module s (a->b) -> Module ModuleScript a -> Module s b
```
thus ensuring that only scripts representing modules are passed as
script arguments.

### Plutus Ledger Language Versions

Plutus ledger language version is what "Plutus V1", "Plutus V2", "Plutus V3" refer to.
These are not distinct programming languages; the primary difference lies in the arguments the script receives from the ledger, and the value it returns[^1].
Plutus V1, V2 and V3 can therefore be understood as type signatures, in the sense that they each represent a subset of UPLC programs with specific types. Any UPLC program that matches the expected argument and return types can be considered and used as a Plutus V1, V2 or V3 script.
A new ledger era is the primary reason for introducing a new ledger language version, though technically there can be cases where a new ledger language version is necessary without a new ledger era.

Currently each script on-chain is tagged with a specific ledger language version - V1, V2, V3 or native script - and this version tag is a component of the script hash.
A logical approach, therefore, is to continue doing so for module scripts, and require that a validator script and all modules it references must use the same ledger language version; failure to do so leads to a phase-1 error.

A different approach is to distinguish between validator scripts and module scripts by applying version tags only to validator scripts.
Module scripts are untagged and can be linked to any validator script.
This makes module scripts more reusable, which is advantageous because in most cases, a UPLC program has the same semantics regardless of the ledger language version.

This is, however, not always the case because a few builtin functions have multiple semantic variants, and the variant used may differ depending on the ledger language version.
Nonetheless, if a module script depends on a particular ledger language version to work correctly, this requirement can be communicated through alternative means, e.g., as a piece of metadata in a module script registry.

Another drawback of untagged modules is that untagged modules will be a new concept that doesn't currently exist, and as a result, modules will not be usable in Plutus V1 through V3, and can only be used from Plutus V4 onwards.

### Plutus Core Versions

Plutus Core version is the usual sense of version pertaining to programming languages - in this instance the Plutus Core language.
So far there have been two Plutus Core versions: 1.0.0 and 1.1.0. 1.1.0 adds sums-of-products to the language by introducing two new AST node types: Case and Constr.
See [CIP-85](https://cips.cardano.org/cip/CIP-0085) for more details.
Each UPLC program is tagged with a Plutus Core version (where as for ledger language versions, only _scripts_ that exist on-chain, i.e., stored in UTXOs, are tagged with ledger language versions).

UPLC programs with different Plutus Core versions are incompatible and cannot be combined, and therefore, a validator script and all modules it references must share the same Plutus Core version; otherwise it is a phase-1 error.

### Implementation and Integration Considerations

Here we use the term "script" to refer to either a validator script (which needs to be run to validate a transaction) and a module script (which serves as a dependency for other scripts).
Both validators and modules can reference other modules.

The feature proposed in this CIP can only be released in a new ledger era.
As such, it is anticipated that it will be released alongside the next ledger era - the Dijkstra era.

Whether this feature can be used in existing Plutus ledger language versions (V1 through V3) depends on which of the options described in subsection _Plutus Ledger Language Versions_ (i.e., tagged or untagged modules) is chosen.
If tagged modules are adopted, the feature will be available across all Plutus language versions (V1 through V4) starting at the hard fork that introduces the Dijkstra era.
If untagged modules are adopted, it will only be usable in Plutus V4, as explained in the subsection.

The bulk of the implementation effort lies on the Plutus side, including updates to `plutus-ledger-api`, updates to the CEK machine, costing and benchmarking, among others.
The specifics will depend on which of the various alternatives outlined in this CIP is selected.
The Plutus team aims to complete the implementation of the selected approach according to its specification, in time for the Dijkstra era.

On the ledger and cardano-api side, the effort required to support this feature is not as substantial as it may appear to be.
This is because the ledger already supports reference inputs and reference scripts since the Babbage era, and this existing mechanism can largely be reused to accommodate module scripts.
The processes of storing a module script in a UTXO and using it in a transaction are similar to storing and using a reference script.

The main difference between reference scripts and module scripts is that a module script is, like an object file, not directly runnable but must be linked with a validator to form a runnable script.
To support this, the ledger and cardano-api will need to implement some changes.
The specifics will slightly vary depending on which of the alternative approaches is chosen, but it will generally involve the following.

Currently, deserialising a script returns a `ScriptForEvaluation`, which contains a deserialised script, along with the original serialised script. The ledger has a `PlutusRunnable` newtype that wraps `ScriptForEvaluation`.
With the introduction of modules, deserialising a script no longer produces a runnable script unless it is a self-contained validator that doesn't use modules.
Otherwise, the module hashes it references must be resolved and the modules linked before the validator can be executed.

To do so, the `plutus-ledger-api` package can implement one of two options, depending on which is more suitable for the ledger:
- Script deserialisation will be modified to return a new data type, `ScriptForLinking`.
  It is similar to `ScriptForEvaluation` except that the deserialized script is not necessarily a self-contained script and may be accompanied by a list of module hashes it needs.

  Then, a function `linkValidator :: Map ScriptHash ScriptForLinking -> ScriptHash -> LinkedScript` is provided that performs linking for a particular validator identified by `ScriptHash`, where `LinkedScript ~ UPLC.Program DeBruijn DefaultUni DefaultFun ()` is a fully linked script.
- Alternatively, the following function can be provided: `linkScripts :: Map ScriptHash SerialisedScript -> Map ScriptHash LinkedScript`, which performs deserialisation and linking for all (validator and module) scripts in one go.

In either case, the ledger should ensure that each script (including validator script and module script) is deserialised and processed no more than once.

Moreover, for the transaction builder to decide which modules a validator refers to are used at runtime, `plutus-ledger-api` will also expose the following function:

```haskell
getUsedModules ::
  MajorProtocolVersion ->
  EvaluationContext ->
  -- | All scripts provided in a transaction
  Map ScriptHash SerialisedScript ->
  -- | Hash of the validator
  ScriptHash ->
  -- | Script arguments
  [Data] ->
  -- | Hashes of used module scripts
  Set ScriptHash
```

The value type of the `Map` could instead be `ScriptForLinking` (i.e., deserialised script) rather than `SerialisedScript`.

This function is to be called by the code building transactions (e.g., `Cardano.Api.Fees.makeTransactionBodyAutoBalance`) to determine which modules are necessary to include in a transaction.

## Rationale: How does this CIP achieve its goals?

This CIP provides a minimal mechanism to split scripts across several
transactions. 'Imported' modules are provided in the calling
transaction and passed as arguments to the top-level script, and their
identity is checked using their hash. In the main specification, the
representation of modules is left entirely up to compiler-writers to
choose--a module may be any value at all (although some of the
variations do restrict the form). For example, one compiler might
choose to represent modules as a tuple of functions, while another
might map function names to tags, as Solidity does, and represent a
module as a function from tags to functions. Each language will need
to define its own conventions for module representations, and
implement them on top of this low-level mechanism. For example, a
typed language might represent a module as a tuple of exported values,
and store the names and types of the values in an (off-chain)
interface file. Clients could use the interface file to refer to
exported values by name, and to perform type-checking across module
boundaries.

### Recursive modules

This design does not support mutually recursive modules. Module
recursion is sometimes used in languages such as Haskell, but it is a
rarely-used feature that will not be much missed.

### Cross-language calls

There is no a priori reason why script arguments need be written in
the same high-level language as the script itself; thus this CIP
supports cross-language calls. However, since different languages may
adopt different conventions for how modules are represented, then some
'glue code' is likely to be needed for modules in different languages
to work together. In the longer term, it might be worthwhile defining
an IDL (Interface Definition Language) for UPLC, to generate this glue
code, and enable scripts to call code in other languages more
seamlessly. This is beyond the scope of this CIP; however this basic
mechanism will not constrain the design of such an IDL in the future.

In Plinth, because the `Module` type is a phantom type, it is easy to
take code from elsewhere and turn it into a `Module t` for arbitrary
choice of `t`; this can be used to import modules compiled from other
languages into Plinth (provided a sensible Plinth type can be given to
them).


### Static vs Dynamic Linking

With the introduction of modules, scripts are no longer
self-contained--they may depend on imported modules. This applies both
to scripts for direct use, such as spending verifiers, and to scripts
representing modules stored on the chain.  A module may depend on
imported modules, and so on transitively. An important question is
when the identity of those modules is decided. In particular, if a
module is replaced by a new version, perhaps fixing a bug, can
*existing* code on the chain use the new version instead of the old?

The design in this CIP supports both alternatives. Suppose a module
`A` imports modules `B` and `C`. Then module `A` will be represented
as the lambda-expression `λB.λC.A`. This can be compiled into a
`CompleteScript` and placed on the chain, with an empty list of
`ScriptArg`s, as a reference script in a UTxO, allowing it to be used
with any implementations of `B` and `C`--the calling script must pass
implementations of `B` and `C` to the lambda expression, and can
choose them freely. We call this 'dynamic linking', because the
implementation of dependencies may vary from use to use. On the other
hand, if we want to *fix* the versions of `B` and `C` then we can
create a `Script` that applies the same `CompleteScript` to two
`ScriptArg`s, containing the hashes of the intended versions of `B`
and `C`, which will then be supplied by
`resolveScriptDependencies`. We call this 'static linking', because
the version choice for the dependency is fixed by the script. It is up
to script developers (or compiler writers) to decide between static
and dynamic linking in this sense.

On the other hand, when a script is used directly as a validator then
there is no opportunity to supply additional arguments; all modules
used must be supplied as `ScriptArg`s, which means they are
fixed. This makes sense: it would be perverse if a transaction trying
to spend a UTxO protected by a spending validator were allowed to
replace some of the validation code--that would open a real can of
worms, permitting many attacks whenever a script was split over
several modules. With the design in the CIP, it is the script in the
UTxO being spent that determines the module versions to be used, not
the spending transaction. That transaction does need to *supply* all
the modules actually used--including all of their dependencies--but it
cannot choose to supply alternative implementations of them.

### In-service upgrade

Long-lived contracts may need upgrades and bug fixes during their
lifetimes. This is especially true of contracts made up of many
modules--every time a dependency is upgraded or receives a bug fix,
the question of whether or not to upgrade the client contract
arises. However, the problem of upgrading contracts *securely* is a
tricky one, and exists whether or not modules are used. Therefore this
CIP does not address this problem specifically: developers should use
the same mechanisms to handle upgrades of scripts with dependencies,
as they use to upgrade scripts without dependencies. The only thing we
note here is that the need for upgrades is more likely to arise when a
script depends on many others, so it is more important to be prepared
for it. Note that, because a script contains the hashes of its
dependencies, no 'silent' upgrade can occur: the hash of a script
depends on *all* of its code, including the code of its dependencies,
so any change in a dependency will lead to a change in the script
hash.

### Lazy loading

The 'lazy loading' variation in the specification section above
permits fewer modules to be supplied in a transaction.  Dependency
trees have a tendency to grow very large; when one function in a
module uses another module, it becomes a dependency of the entire
module and not just of that function. It is easy to imagine situations
in which a script depends on many modules, but a particular call
requires only a few of them. For example, if a script offers a choice
of protocols for redemption, only one of which is used in a particular
call, then many modules may not actually be needed. The variation
allows a transaction to omit the unused modules in such cases. This
reduces the size of the transaction, which need provide fewer
witnesses, but more importantly it reduces the amount of code which
must be loaded from reference UTxOs.

If a script execution *does* try to use a module which was not
provided, it will encounter a run-time type error and fail (unless the
module value was `builtin unit`, in which case the script will behave
as though the module had been provided).

To take advantage of this variation, it is necessary, when a
transaction is constructed, to *observe* which script arguments are
actually used by the script invocations needed to validate the
transaction. The transaction balancer runs the scripts anyway, and so
can in principle observe the uses of script arguments, and include
witnesses in the transaction for just those arguments that are used.

#### Balancer modifications

To take advantage of 'lazy loading', it's necessary to identify
reference scripts that are *dynamically* unused, when the scripts in a
transaction run. The best place to do that is in a transaction
balancer, which needs to run the scripts anyway, both to check that
script validation succeeds, and to determine the number of execution
units needed to run the scripts. We adopt the view that

**A transaction balancer may drop reference inputs from a
   transaction, if the resulting transaction still validates**

We call reference scripts which are not actually invoked during script
verification 'redundant'; these are the reference scripts that can be
removed by the balancer.

##### First approach: search

The simplest way for a balancer to identify redundant reference inputs
is to try rerunning the scripts with an input removed. If script
validation still succeeds, then that input may safely be removed. The
advantages of this approach are its simplicity, and lack of a need for
changes anywhere else in the code. The disadvantage is that
transaction balancing may become much more expensive--quadratic in the
number of scripts, in the worst case.

The reason for this is that removing one script may make others
redundant too; for example if script A depends on script B, then
script B may become redundant only after script A has been
removed--simply evaluating script A may use the value of B, and
scripts are evaluated when they are passed to other scripts, whether
they are redundant or not. So if the balancer tries to remove B first,
then script verification will fail--and so the balancer must try again
to remove B after A has been shown to be redundant. Unless we exploit
information on script dependencies, after one successful script
removal then all the others must be revisited. Hence a quadratic
complexity.

In the case of 'value scripts' this argument does not apply:
evaluating a script will never fail just because a different script is not
present. In this case it would be sufficient to traverse all the
scripts once, resulting in a linear number of transaction
verifications.

##### Second approach: garbage collection

First the balancer analyses all the scripts and reference scripts in a
transaction, and builds a script dependency dag (where a script
depends on its `ScriptArg`s). Call the scripts which are invoked
directly in the transaction (as validators of one sort or another) the
*root* scripts.

Topologically sort the scripts according to the dependency relation;
scripts may depend on scripts later in the order, but not
earlier. Now, traverse the topologically sorted scripts in order. This
guarantees that removing a *later* script in the order does not cause
an *earlier* one to become redundant.

For each script, construct a modified dependency graph by removing the
script concerned, and then 'garbage collecting'... removing all the
scripts that are no longer reachable from a root. Construct a transaction
including only the reference scripts remaining in the graph, and run
script validation. If validation fails, restore the dependency graph
before the modification. If validation succeeds, the script considered
and all the 'garbage' scripts are redundant; continue using the now
smaller dependency graph.

When all scripts have been considered in this way, then the remaining
dependency graph contains all the scripts which are dynamically needed
in this transaction. These are the ones that should be included in the
transaction, either directly or as reference scripts.

The advantage of this approach is that only the code in the balancer
needs to be changed. The disadvantage is that transaction balancing
becomes more expensive: script verification may need to be rerun up to
once per script or reference script. In comparison to the first
approach above, this one is more complex to implement, but replaces a
quadratic algorithm by a linear one.

##### Third approach: modified CEK machine

The most direct way to determine that a script is not redundant is to
observe it being executed during script verification. Unfortunately,
the CEK machine, in its present form, does not make that
possible. Thus an alternative is to *modify the CEK machine* so that a
balancer can observe scripts being executed, and declare all the other
scripts redundant. In comparison to the first two approaches, this is
likely to be much more efficient, because it only requires running
script verification once.

The modifications needed to the CEK machine are as follows:

`CekValue`s are extended with *tagged values*, whose use can be
observed in the result of a run of the machine.
```
data CekValue uni fun ann =
  ...
  | VTag ScriptHash (CekValue uni fun ann)
```
In the 'value script' variation, no expression resulting in a `VTag`
value is needed, because `VTag`s will be inserted only by
`resolveScriptDependencies`. In other variations, a `Tag` constructor
must also be added to the `NTerm` type, to be added by
`resolveScriptDependencies`. In either case the version of
`runScriptDependencies` *used in the balancer* tags each value or
subterm derived from a `ScriptHash` `h` as `VTag h ...` (or `Tag h
...` in variations other than 'value scripts').

The CEK machine is parameterized over an emitter function, used for
logging. We can make use of this to emit `ScriptHash`es as they are
used. This allows the balancer to observe which `ScriptHash`es *were*
used.

Simply evaluating a tagged value, or building it into a
data-structure, does not *use* it in the sense we mean here: replacing
such a value with `builtin unit` will not cause a validation
failure. Only when such a value is actually *used* should we strip the
tag, emit the `ScriptHash` in the `CekM` monad, and continue with the
untagged value. This should be done in `returnCek`, on encountering a
`FrameCases` context for a tagged value, and in `applyEvaluate` when
the function to be applied turns out to be tagged, or when the
argument to a `builtin` turns out to be tagged.

Adding and removing tags must be assigned a zero cost *in the
balancer*, since the intention is that they should not appear in
transactions when they are verified on the chain. Thus a zero cost is
required for the balancer to return accurate costs for script
verification on the chain. On the other hand, if these operations *do*
reach the chain, then they should have a *high* cost, to deter attacks
in which a large number of tagging operations are used to keep a
transaction verifier busy. This can be achieved by adding a `BTag`
step kind to the CEK machine, a `cekTagCost` to the
`CekMachineCostsBase` type, and modifying the balancer to set this
cost to zero during script verification.

The advantage of this approach is that it only requires running each
script once in the balancer, thus reducing the cost of balancing a
transaction, perhaps considerably. The disadvantage is that it
requires extensive modifications to the CEK machine itself, a very
critical part of the Plutus infrastructure.

##### Fourth approach: lazy scripts

Another way to observe script uses *without* modifying the CEK machine
is to wrap them in `Delay` and force them at the point of use. The
balancer can then insert trace output of the script hash just inside
the `Delay`, and so observe which scripts are actually forced during
script execution.

The difficulties with this approach arise from the fact that delayed
closures must be *explicitly* forced in UPLC; this does not 'just
happen' when a delayed value is used. This means that corresponding
`Force` operations must also be added to scripts, and the question is:
who does this, and if it is to be done automatically, then how?

One possibility is that it is the developer's responsibility to force
script arguments at the point of use--that is, that the `Force`
operations needed would be written by the human programmer. It follows
that they would *always* be part of the script, even when running on
the chain, and so even on the chain script arguments would need to be
delayed (even if no trace output would be needed). This would increase
code size a little, and impose a force-delay overhead on every
cross-module reference, which is probably not acceptable.

The alternative is to have the balancer insert corresponding `Force`
operations, as well as the `Delay`s. A simple way to do so would be
to add a `Force` around every use of a variable corresponding to a
script argument--under the 'value scripts' syntactic restriction these
variables are easy to identify. These modifications would not be made
during normal script verification, which might therefore cost less--or
more--than the modified balancer run. The balancer would thus need to
perform script verification twice: once with `Delay` and
`Force`inserted to determine redundant scripts, and then a second time
(with redundant scripts removed) to determine the actual cost on the
chain.

The bigger problem with this approach, though, is that it will
*overestimate* the set of used scripts, leading to more scripts being
used in a transaction, and thus potentially exponentially more
expensive transactions. The reason for the overestimation is that
*all* occurrences of variables bound to script arguments are wrapped
in `Force`, even those that would not lead to untagging the
corresponding tagged value in the third approach above. For example,
suppose a variable bound to a script argument is passed as a parameter
to another function. With the simple `Force`-placement strategy
described above, the script argument would be forced *at that call*,
making the corresponding script appear to be used, even though the
function it is passed to might not actually use it in all cases. Hence
the set of scripts used would be overestimated.

One might use a more sophisticated strategy to insert `Force`
operations. For example, in the case described above one might pass
the script argument *unforced* to the function, and modify the
function to force it when it is used. This would require the balancer
to perform a flow analysis, to identify the functions that might be
passed a delayed script argument. Moreover, such functions might be
called *sometimes* with a delayed script argument, and sometimes
not. The code could be replicated to create two versions of such
functions. But with *n* script arguments, this might require up to
*2^n* versions of each function, leading to an exponential increase in
code size. An attacker could exploit this to craft a transaction that
would cause the balancer to run out of memory. This is really not
attractive.

Finally, one might finesse these problems by modifying the CEK machine
to force delayed closures automatically where the value is required,
thus enabling explicit `Force` operations to be omitted. This would
effectively turn UPLC into a call-by-name programming language. That would

enable this problem to be solved more easily, but  at the cost of
reversing a rather fundamental design decision in UPLC--and probably
making the CEK machine a little bit slower, for all programs.

Thus it appears that there is no good way of using UPLC's existing
lazy evaluation to observe use of script arguments.

### Value Scripts

This section discusses the 'value scripts' variation.

The main specification in this CIP represents a `Script` that imports
modules as compiled code applied to a list of `ScriptHash`es. To
prepare such a script for running, `resolveScriptDependencies`
replaces each hash by the term it refers to, and builds nested
applications of the compiled code to the arguments. These applications
must be evaluated by the CEK machine *before* the script proper begins
to run. Moreover, each imported module is itself translated into such
a nested application, which must be evaluated before the module is
passed to the client script. In a large module hierarchy this might
cause a considerable overhead before the script proper began to
run. Worst of all, if a module is used *several times* in a module
dependency tree, then it must be evaluated *each time* it is
used. Resolving module dependencies traverses the entire dependency
*tree*, which may be exponentially larger than the dependency *dag*.

The value script variation addresses this problem head on. Scripts are
converted directly into CEK-machine values that can be invoked at low
cost. Each script is converted into a value only once, no matter how
many times it is referred to, saving time and memory when modules
appear several times in a module hierarchy.

On the other hand it does restrict the syntactic form of
scripts. Scripts are restricted to be syntactic lambda expressions,
binding their script arguments at the top-level. This is not so
onerous. But inside those λs, there must also be a syntactic
value. For example, consider a module represented by a tuple, whose
components represent the exports of the module. Then all of those exports
need to be syntactic values--an exported value could not be computed
at run-time, for example using an API exported by another
module. While many module exports are functions, and so naturally
written as λ-expressions (which are values), this restriction will be
onerous at times.

This method does require opening up the API of the CEK machine, so
that CEK values can be constructed in other modules, and introducing a
way to run the machine starting from a given configuration. So it
requires more invasive changes to the code than the main
specification.

#### `ScriptHash` allowed in terms?

An alternative design would allow UPLC terms to contain `ScriptHash`es
directly, rather than as λ-abstracted variables, to be looked up in a
global environment at run-time. This would address this same problem:
the cost of performing many applications before script evaluation
proper begins. It would also require changes to the CEK machine, and
is not really likely to perform better than the 'value scripts'
variation (in practice, the main difference is the use of a global
environment to look up script hashes, as opposed to many per-module
ones). However, this approach is less flexible because it does not
support dynamic linking (see Static vs Dynamic Linking above). Once a
`ScriptHash` is embedded in a term, then a different version of the
script cannot readily be used instead. Moreover, script hashes are
quite large (32 bytes), and including more than a few in a script
would quickly run into size limits.

#### Module-level recursion

This section discusses the `module-level recursion` subvariation of
the `value scripts` variation.

UPLC provides a fixpoint combinator, and this is how recursion is
compiled. For the sake of argument, consider the well-known fixpoint
combinator `Y` (in reality, `Y` is not suitable for use in a strict
programming language, so the UPLC version is slightly different). We
can imagine that a recursive function `f` is compiled as `Y h`, for
some suitable `h`.

The difficulty that arises is that `Y h` *is not a value*, and thus
cannot appear at the top-level of a module, under the 'value script'
restriction. It can be *normalised* into a value, of course, using
```
Y h ---> h (Y h)
```
and then reducing the application of `h`; this would need to be done
by a compiler generating UPLC with the `value script`
restriction. But reducing `h (Y h)` may well duplicate `Y h`. When
this happens at CEK runtime it is not a problem, because all the
occurrences of `Y h` are represented by the same pointer. But when the
reductions are applied by a compiler, and the resulting term is
serialized to UPLC code for inclusion in a script, then each
occurrence of `Y h` will be serialized separately, losing sharing and
causing code duplication in the resulting script. The result could be
*larger* code, the opposite of what we are trying to achieve. Thus
this method of compiling recursion fits badly with the 'value scripts'
variation.

Hence module-level recursion, which allows recursive occurrences of
script values to be referred to via the `Self` variable instead of
using a fixpoint combinator implemented in UPLC. To take advantage of
this feature, the compiler will need to float occurrences of `fix`
upwards, to the top-level of a module. This can be done using suitable
analogues of the rules
```
(..,fix (λx.e),...) ---> fix (λx.(..,e[proj i x/x],..))
```
where `i` is the index in the tuple at which `fix (λx.e)` appears,
`proj i x` selects the `i`th component from `x`, and `x` does not
occur free elsewhere in the tuple; a corresponding rule for
constructor applications; and
```
fix (λx. fix (λy.e)) ---> fix (λx. e[x/y])
```
Both these rules require adjusting deBruijn numbers in the UPLC
implementation.

The intention here is to implement module-level recursion using a
cyclic data-structure--the value restriction guarantees that the
module value `Self` is not needed to compute the top-level value of
the module, and thus there is no risk of falling into an infinite loop
at this point. (Of course, a recursive function can loop *when it is
called*, but constructing the function itself cannot loop because it
must be a syntactic λ-expression). This is a *more efficient* way to
implement recursion than the fixpoint combinators currently used in
UPLC, and so will probably become the preferred way to implement
recursion.

Note that if we adopt value scripts, but *not* module-level recursion,
then modules will be unable to export recursive functions without
'hiding' them in a value, such as a `Delay`.

#### Variation: Explicit lambdas

This variation lifts some of the restrictions of the 'value scripts'
approach, at the cost of running the CEK machine to evaluate each
module, and taking care to compute and check costs correctly for the
new CEK machine runs. This requires topological sorting of the scripts
in a transaction before evaluation, to guarantee that we do not
encounter a situation where script A depends on script B, but the
budget for computing script B depends on the cost of script A--such a
situation would lead to a blackhole error during script verification.

Because script bodies may now be arbitrary terms, 'module-level
recursion' is no longer essential--it is possible to use fixpoint
combinators in script bodies as at present. It would still improve
efficiency, of course.

Note that if modules *do* meet the syntactic restrictions of 'value
scripts', then this variation will be less efficient than 'value
scripts'--sometimes considerably so. This is because even evaluating,
say, a large tuple whose components are λ-expressions, leads the CEK
machine to descend into, evaluate, and return out of, each component,
thus performing several CEK transitions per element. The `cekValue`
function must also visit each component, of course, doing the same
work, but because this is done directly in Haskell then it will be
considerably more efficient.

This variation is compatible with the various tuple-based variations,
but when the script body is constrained to return a tuple then this
must be checked dynamically when CEK-evaluation is complete; the check
cannot be built into deserialization any more because it is no longer
syntactic.

#### Variation: Tuples of modules

This variation changes the way modules are referenced in scripts: in
the main specification, each imported module is bound to a name in the
environment, and referenced using the associated variable; in this
variation *all* imported modules are bound to a single name, and
modules are referenced by projecting the corresponding component from
the tuple bound to this name.

Thus: in the main specification, a module reference costs one name
lookup; in this variation, a module reference costs a name lookup plus
projection of a component from a tuple. However, because projecting a
component from a tuple is constant time, while the cost of a
name lookup is logarithmic in the number of names in the environment,
then this variation may reduce the cost of module references--since
scripts which import many modules will run with significantly fewer
names in the environment.

Note that the uncurried script form can be generated from the curried
one, by
* introducing a `λMods.` outermost,
* removing the `λ`s binding names to script arguments,
* substituting `proj i Mods` for the `i`th script argument name in the
script body

Thus there is no need for any change to earlier parts of the compiler,
or to the languages Plutus, PIR, or TPLC. Tuples of modules can be
introduced as a last step in the generation of UPLC.

##### Subvariation: Global module environment

The advantage of using a global module environment instead of one
tuple of modules per script is that only one, big, tuple of modules
per transaction need be constructed, instead of one per script. The
cost is an additional traversal of the script code, needed to adjust
module indices to refer to the correct index in the global tuple of
modules. By itself, this is unlikely to improve performance.

However, using a global module environment is a prerequisite to
building the module environment into the CEK machine. Doing the latter
transforms a module reference from a projection from the
tuple-of-modules variable, to a custom construction `ModuleRef i` that
directly accesses the module in the `i`th component of the global
module environment. This reduces the cost from a variable lookup plus
a projection, to just a projection; this can be expected to speed up every
reference to an external module.

##### Subvariation: Unboxed modules

This subvariation makes every reference to a module export cheaper, by
replacing two projections from a tuple by one. It does require
preprocessing script code before it is run, updating export references
to refer to the correct element of the large tuple combining several
modules. This requires a traversal of all the script code in a
transaction, which must be performed every time script verification is
run, including on the chain. Because of this, it makes most sense to
use this subvariation in combination with 'global module environment',
which also requires such a traversal. In both cases, the purpose is to
adjust references to refer to the correct index in the new, merged
data structure; a single traversal suffices to achieve both ends.

The syntactic restriction, requiring a module body to be a tuple of
exports, is not onerous. While some compilers might wish to represent
a module as built-in data, or as a function from a tag (as Solidity
does), this can be achieved by placing the intended module value as
the first component of a one-tuple. The implementation described here
optimises away the selection of an element from such a tuple, so the
restriction introduces no extra overhead in this case.

### Transaction fees

Imported modules are provided using reference scripts, an existing
mechanism (see CIP-33), or in the transaction itself. Provided the
cost of loading reference scripts is correctly accounted for, this CIP
introduces no new problems.

Note that there is now (since August 2024) a hard limit on the total
size of reference scripts used in a transaction, and the transaction
fee is exponential in the total script size (see
[here](https://github.com/IntersectMBO/cardano-ledger/blob/master/docs/adr/2024-08-14_009-refscripts-fee-change.md)).The
exponential fees provide a strong motivation to prefer the 'lazy
loading' variation in this CIP: even a small reduction in the number
of reference scripts that need to be provided may lead to a large
reduction in transaction fees.

The motivation for these fees is to deter DDoS attacks based on
supplying very large Plutus scripts that are costly to deserialize,
but run fast and so incur low execution unit fees. While these fees
are likely to be reasonable for moderate use of the module system, in
the longer term they could become prohibitive for more complex
applications. It may be necessary to revisit this design decision in
the future. To be successful, the DDoS defence just needs fees to
become *sufficiently* expensive per byte as the total size of
reference scripts grows; they do not need to grow without bound. So
there is scope for rethinking here.

Some of the variations in this CIP require a traversal of all the
script code in a transaction to adjust module references before
execution. This should be reflected by a component in the transaction
fee linear in the total size of scripts.

### Verification

Since scripts invoked by a transaction specify all their dependencies
as hashes, then the running code is completely known, and testing or
formal verification is no harder than usual. Standalone verification
of modules using 'dynamic linking' poses a problem, however, in that
the code of the dependencies is unknown. This makes testing
difficult--one would have to test with mock implementations of the
dependencies--and formal verification would require formulating
assumptions about the dependencies that the module can rely on, and
later checking that the actual implementations used fulfill those
assumptions.

### Impact on optimisation and script performance

Splitting a script into separately compiled parts risks losing
optimisation opportunities that whole-program compilation gives. Note
that script arguments are known in advance, and so potentially some
cross-module optimisation may be possible, but imported modules are
shared subterms between many scripts, and they cannot be modified when
the client script is compiled. Moreover, unrestrained inlining across
module boundaries could result in larger script sizes, and defeat the
purpose of breaking the code into modules in the first place.

On the other hand, since the size limit on scripts will be less of a
problem, then compilers may be able to optimize *more*
aggressively. For example, today the Plinth inliner is very careful
not to increase script size, but once modules are available it may be
able to inline more often, which can enable further optimizations.

Moreover, today we see examples of deliberate choice of worse
algorithms, because their code is smaller, and easier to fit within
the script size limit. Removing the need to make such choices can
potentially improve performance considerably.

### Example: Defining and using a Set module

As an example of how the module system might be used in a high-level
language, consider the following code, which defines and uses a module
implementing set insertion and membership testing, using an ordered
binary tree.
```
data Tree a = Leaf | Branch (Tree a) a (Tree a)

empTree = Leaf

insTree a Leaf = Branch Leaf a Leaf
insTree a (Branch l b r)
  | a < b = Branch (insTree a l) b r
  | a > b = Branch l b (insTree a r)
  | a== b = Branch l b r

memTree a Leaf = False
memTree a (Branch l b r)
  | a < b = memTree a l
  | a > b = memTree a r
  | a== b = True

data Set = Set {emptySet :: forall a. Tree a,
     	        insertSet :: forall a. Ord a => a -> Tree a -> Tree a,
		memberSet :: forall a. Ord a => a -> Tree a -> Bool}

setMod = Set empTree insTree memTree

setModule :: Module Set
setModule = makeModule ($$(PlutusTx.compile [| setMod |]))

client set redeemer _ = memberSet set redeemer s
  where s = insertSet set 1 (insertSet set 2 (emptySet set))

clientModule = makeModule ($$(PlutusTx.compile [| client |]))
 `applyModule` setModule
```
Here the module signature is represented by a Haskell record type;
Haskell records are compiled into tuples in UPLC, and the record
fields are all values (once fixpoints are floated upwards to the
module level), so the `setModule` in this example fits the 'unboxed
modules' syntactic restrictions. The client script takes the record as
an argument, and uses the module exports via record field selectors,
which compile to projections from the tuple. Thus the client also
meets the syntactic restrictions for 'unboxed modules'. To make use
of these modules, the off-chain code must construct a UTxO
containing `setModule` as a reference script, and include it as a
reference UTxO in transactions that use the client.

### Related work

#### Merkelized Validators

Philip DiSarro describes ["Merkelized
validators"](https://github.com/Anastasia-Labs/design-patterns/blob/main/merkelized-validators/merkelized-validators.md),
which offer a way of offloading individual function calls to stake
validators: the client script just checks that the appropriate stake
validator is invoked with a particular function-argument and result
pair, checks that the argument equals the argument it wants to call
the function with, and then uses the result as the result of the
function. The stake validator inspects the argument-result pair,
computes the function for the given argument, and checks that the
result equals the result in the pair. This design pattern enables the
logic of a script to be split between the client script and the stake
validator, thus circumventing the limits on script size. But the main
point is that the function call, whose result may be needed by several
validators, can be computed just *once* per transaction. More details
can be found
[here](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md).

Factoring out a shared part of the validation in this way is a
generally useful technique which is largely independent of the
existence of modules--this CIP does not remove the need for sharing
work between validators, and indeed this trick will work equally well
once modules are added. But as a way of *implementing* modules, it is
rather intricate and unsatisfactory.

#### The WebAssembly Component Model

The [Web Assembly Component
Model](https://component-model.bytecodealliance.org/) defines a
high-level IDL to enable components written in different programming
languages (such as C/C++, C#, Go, Python and Rust), to work together
in one WebAssembly system. WASM already has a module system, and a
WASM component may consist of a number of modules (written in the same
language). The focus here is on interaction between *different*
programming languages in a well-typed way. Defining such an IDL for
Cardano might be useful in the future, but it is too early to do so
now.

### Preferred Options

Allowing script code to be spread across many transactions lifts a
commonly complained-about restriction faced by Cardano script
developers. It permits more complex applications, and a much heavier
use of libraries to raise the level of abstraction for script
developers. Modules are already available on the Ethereum blockchain,
and quite heavily used. Adopting this CIP, in one of its variations,
will make Cardano considerably more competitive against other smart
contract platforms.

The *main alternative* in this CIP is the simplest design, is easiest
to implement, but suffers from several inefficiencies.

The *lazy loading* variation allows redundant scripts to be omitted
from transactions, potentially making transactions exponentially
cheaper. To take full advantage of it requires a balancer that can
drop redundant scripts from transactions. Three alternative methods
are described: *search*, the simplest, which must run script
verification a quadratic number of times in the number of scripts in
the worst case; *garbage collection*, a self-contained change to the
balancer which analyses script dependencies and thus needs to run script
verification only a linear number of times; a *modified CEK machine*
which adds tagged values to the machine, which the balancer can use to
identify redundant scripts in *one* run of script verification,
possibly requiring one more run to make accurate exunit cost estimates.

The *value scripts* variation restricts scripts to be explicit
λ-expressions binding the script arguments, with an innermost script
body which is a syntactic value. Such scripts can be converted to CEK
values in a single traversal; each script can be converted to a value
*once per transaction*, rather than at every use. *Module-level
recursion* enables recursive definitions to recurse via the module
itself, rather than locally, and makes the syntactic-value restriction
easier to satisfy. This variation is expected to reduce the start-up
costs of running each script considerably; on the down-side the
syntactic restriction would be a little annoying, and it requires CEK
operations which are not currently part of the API, so it requires
modifications to a critical component of the Plutus implementation.

The *explicit λs* variation is a half-way house between the main
variation and the 'value scripts' variation. It places less onerous
syntactic restrictions on script bodies, and as such can be used with
the existing implementation of recursion (although efficiency would
still benefit from module-level recursion). Cost accounting during
script evaluation is a little intricate. It requires modifications to
the loop at the core of the CEK machine.

The *tuples of modules* variation replaces parameters referring to
individual modules with a single parameter bound to a tuple of
modules, effectively uncurrying scripts wrt their module
parameters. At the cost of a traversal of all the script code in a
transaction to 'relocate' module references, it is possible to replace
many tuples-of-modules, one per script, by a global tuple of modules
for the entire transaction; a further improvement would then be to
unbox modules, replacing the global tuple of modules with a global
tuple of module exports. These variations reduce the cost of referring
to a module export, at the cost of an additional traversal of the
script code before execution. Extensive benchmarking would be needed
to decide whether or not they improve performance overall.

Performance can probably be improved further by building the module
environment in to the CEK machine.

The simplest alternative to implement would be the main alternative
without variations. A more efficient implementation would combine
value scripts with lazy loading, using tagged values in the CEK
machine to analyse dynamic script dependencies in the balancer, and so
drop redundant scripts from each transaction. Further improvements to
performance may be achievable using a global module environment, and
unboxed modules; because there are performance costs as well as
benefits to these approaches, extensive benchmarking would be required
to make an informed choice.

These latter variations all require modifications to the CEK machine
and to the balancer, as well as resolving dependencies in scripts;
that is, they are considerably more expensive to implement.

There are many variations proposed in this CIP; I do have an opinion
as to which choices might be best. These are opinions, so might be
proven wrong later by benchmarks.

Firstly, I believe lazy loading will be very valuable, especially for
small, cheap transactions.

I don't think lazy loading will make *any* transaction worse, it's
simply a win. In general, though, many choices have effects that will
differ for different transactions, speeding some up while slowing
others down.  Many variations do some work before running scripts, in
order to speed them up when they are actually run. These variations
will tend to make small, cheap transactions *more* expensive, because
there will be too little execution time to recoup the initial
investment, while they make long-running transactions cheaper. It's
necessary to make a choice here, and decide what kind of transactions
to prioritize. Personally, I favour keeping small, cheap transactions
cheap, even at the cost of making longer running transactions a bit
slower. So I favour choosing a variation that does work in advance
only if the break-even point is reached very quickly. This is a
personal opinion, and could be questioned: the important thing is
think about this issue and make the choices deliberately.

With this in mind, I am against variations that require a traversal of
all the script code *during phase 2 verification*. This would be, in
particular, the 'global module environment' and the 'module
environment built into the CEK machine' variations. Note that
syntactic restrictions which can be implemented during deserialization
do not require an extra traversal of the code in this sense. Also, the
'unboxed modules' variation--*in its local form*--requires a traversal
of the script code *which treats each script independently*, and so
can be done at compile-time. This is not either a run-time cost that
concerns me.

I like the 'value scripts' variation. I believe it may reduce costs
significantly for small, cheap transactions. It does require 'module
level recursion' as well, if recursion is to be compiled simply and
efficiently. It does constrain compilers a little bit; any compiler
that takes advantage of modules must generate code meeting the
restriction. But since modules are a new feature, no existing code
will be broken by this. It's also straightforward to meet the
restriction trivially, for example by wrapping the entire module body
in `Delay`. So I do not expect any major problems here.

The 'tuples of modules' variation, given efficient projections, should
simply be a performance improvement, so I am in favour of it. It does
require `resolveScriptDependencies` to *construct* the tuple before
script execution, but this replaces adding the modules one-by-one to
the environment, and should be cheaper. Moreover, accessing modules
should in most cases be slightly cheaper. Checking the restriction
that the variable bound to the tuple only appears as an argument to a
projection might be costly, requiring an additional traversal of the
code, but on the other hand that restriction exists to make adjustment
of the index possible, and this is only required by the 'global module
environment' variation. So, provided this is not adopted, one might
relax that restriction and *allow* scripts to refer to the tuple of
modules as a whole. That is an odd thing to do, but not actively
harmful.

The 'unboxed modules' variation is quite attractive, in its local
variant (where each script is passed a tuple of the exports from
modules that *that script* imports). In this variant a traversal of
the code to adjust references to module exports *is* needed, but can
be done at compile-time, so does not impose a cost during phase 2
verification. However, (in combination with 'lazy loading') this does
require `ScriptArg`s to be larger, making all scripts slightly larger
on the chain. Also, there is a start-up cost for the unboxing itself:
`resolveScriptDependencies` must copy *all* the exports from each
imported module into the same tuple (whether or not they will be
used). Modules may have quite a lot of exports--`Data.Map` for example
has 97--and many may not be used in any particular script. The benefit
of unboxing modules is slightly faster access to module exports when
the script runs, but for small, cheap runs we may never recover the
cost of building the unboxed tuple in the first place. On balance, I
would probably prefer *not* to do this, but this is not a strong
preference.

Finally, all the variations using tuples rely on efficient, constant
time projections of tuple components. These are not presently
available in UPLC--but they would benefit *all* UPLC users, not least
by providing an efficient implementation for Haskell record field
selectors in Haskell. Adding efficient projections for SoP data deserves
a CIP of its own; it is a prerequisite for many variations here, but
logically is not a part of implementing modules. A separate CIP should
be written for this in the near future--it should be straightforward
and uncontroversial compared to adding modules.


## Path to Active

### Acceptance criteria

- [ ] determine which approach outlined in this CIP will be selected
- [ ] `plutus` changes
- [ ] `cardano-ledger` changes
- [ ] `cardano-api` changes
- [ ] benchmarking and testing
- [ ] integrate the feature into `cardano-node`
- [ ] end-to-end testing
- [ ] release at the hard fork introducing the Dijkstra era

### Implementation Plan

This CIP will be implemented by the Plutus Core team with assistance from the Ledger team and the Cardano API team.
Should we decide to implement tagged modules - the safer and more recommended option - then modules will be usable in existing Plutus ledger language versions (V1, V2 and V3).
If we instead opt for untagged modules, modules will only be usable from Plutus V4 onwards.

Enabling modules on-chain requires a new ledger era.
Therefore modules will be enabled in the Dijkstra era at the earliest.

Developers of compilers for other languages targeting Untyped Plutus Core will need to update their languages and compilers accordingly if they wish to support modules.

Alternative Cardano node implementors must update their Plutus evaluator (unless a variant is chosen that doesn't require modifying the Plutus evaluator, which is unlikely), ledger, and transaction balancer to support this feature and align with the Haskell node.

## Acknowledgements

This CIP draws heavily on a design by Michael Peyton Jones, and has
benefitted greatly from discussion with Ziyang Liu, Roman Kireev, and
Phil Wadler.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

---

[^1]: At present, a newer ledger language version may have access to more builtin functions and more Plutus Core versions than an older ledger language version, but this difference is going away.
