---
CIP: 195
Title: Data Encoding of Plutus V4 Ledger Types
Category: Plutus
Status: Proposed
Authors:
    - Ziyang Liu <ziyang.liu@iohk.io>
Implementors:
    - IOG Plutus Team <https://iohk.io>
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1238
    - Plutus repo discussion: https://github.com/IntersectMBO/plutus/issues/7342
Created: 2026-08-03
License: CC-BY-4.0
---

## Abstract

This CIP specifies how the Plutus V4 ledger API types, including script context and the types it mentions, are to be encoded as `Data` objects.
New UPLC primitives and language features, together with lessons learned from Plutus V1-V3, create an opportunity to adopt a simpler and more efficient encoding scheme.

## Motivation: Why is this CIP necessary?

__Choosing between lists and arrays.__
UPLC now includes `Array` as a built-in type, with support for constant-time indexing.
This raises the question of whether the Plutus V4 types should be encoded using `Array`, or should they continue to use `List`.
Array-based encoding may sound like the automatic winner, but that's not the case since list-based encoding has become more efficient thanks to the new `dropList` built-in.

__Addressing known inefficiencies.__
For example, in Plutus V1-V3 every product type is encoded with a redundant `Constr 0` tag, where a plain `List` could have been used.
Small nested types also require more layers of `Constr` than necessary: reaching a bound of an `Interval` requires peeling off two layers of `Constr`, and reaching the credential inside a `Maybe StakingCredential` also requires two, even though one layer would suffice in each case.

__Providing a better specification.__
In Plutus V1-V3 the `Data` encoding of ledger API types was not formally specified.
Instead, the de facto specification was the Template Haskell (TH) code in the `plutus` repository that generated the `ToData` and `UnsafeFromData` instances.
Developers of alternative compilers and tooling must reverse-engineer the encoding from the TH code or the generated Haskell code.

## Specification

### List vs. Array

It may sound counter-intuitive, but we believe `List` is a clearly better choice than `Array` for encoding datatypes.
We therefore propose to use `List`, not `Array`, to encode the Plutus V4 types.
Here are the reasons.

__Keeping the `Data` type simple__.

If the Plutus V4 types are encoded using lists, no change to the `Data` datatype will be required.
If they are encoded using arrays, then we'll need two additional constructors - `Array` and `ConstrArray` - together with four additional built-ins for wrapping and unwrapping.
Adding new constructors to `Data` would be a quite invasive change for the Plutus repository alone.
It would also complicates other languages, compilers andy tooling, and requires substantial ledger integration work.
The overall cost is significant, and it is a change best avoided.

__Lists are usually faster than arrays for working with datatypes__:

- For single-field access, `List` is almost always faster in practice.
  Although `dropList` is linear and `indexArray` is constant-time, `dropList`'s cost model has a low intercept and slope, making list encoding faster than array encoding even when accessing the 20th field of a constructor.

  This has taken into account that `indexArray` directly returns the requested field, while list-encoding requires a call to `headList` after `dropList`.
  Even with this overhead, list-encoding remains faster for the 20th field.

  It is true that if `k` is sufficiently large, accessing the `k`th field of a list can be arbitrarily more expensive than accessing the `k`th field of an array.
  However, this is irrelevant since among the Plutus V4 types, the constructor with the most fields is `TxInfo`, which has 20 fields.

- For multi-field access, array encoding can benefit from the `multiIndexArray` builtin.
  However, our testing indicates that array-encoding is still slower than list-encoding most of the time, and is faster only in corner cases (such as accessing a few widely-separated fields from a constructor with many fields).
  The main reason for this is that `multiIndexArray` returns a list, and this list must itself be traversed.
  It is therefore often better to simply use list-encoding and traverse the original list with `dropList`.

- List encoding is more efficient when constructing `Data` objects.
  Arrays can only be created using `listToArray`, so array-encoded datatypes require an additional conversion whenever a value needs to be encoded as `Data`.

One advantage of array-encoding is that it makes the ordering of fields irrelevant.
We do not believe, however, that this benefit outweighs the cost.

A downside of _not_ adding an `Array` constructor to `Data` is that to use an array, it must be converted from a list using the `listToArray` built-in, incurring a linear cost.
However, a simple calculation suggests that applying `listToArray` to a 1000-element list costs much less than 1% of the per-transaction cost limit.
We therefore do not believe that avoiding this conversion justifies adding an `Array` constructor to Data.

### Encoding product types using `List` instead of `Constr`

Product types in Plutus V1-V3 are encoded as `Constr 0 [x1...xn]`.
The constructor tag carries no information since a product type has only one constructor.
We therefore propose encoding product types as a list: `List [x1...xn]`.
Doing so avoids the overhead of pair-destruction.

### Flattening nested types

__Nested sum types.__
Nested sum types can sometimes be flattened to reduce encoding and decoding overhead.
For example, the V1-V3 `Address` type has a `Maybe StakingCredential` field, which combines two two-constructor sum types, so its `Data` representation requires two layers of `Constr`.
Replacing it with a single three-constructor sum type would remove one layer and improve efficiency.

This should, however, not be done blindly since there are drawbacks:
- it could cause constructor proliferation if we flatten a large nested sum type;
- it could also cause datatype proliferation if we need to keep the original nested type because it is used independently.
  For example, if `StakingCredential` is used independently (not under `Maybe`), then we may need to keep both `StakingCredential`, as well as the flattened `Maybe StakingCredential`.

_We did not identify any nested sum type in the Plutus V4 types that is worth flattening._
`Maybe StakingCredential` was the one clear candidate in the script context of Plutus V1-V3, because `StakingCredential` only ever appears under `Maybe`, and so could be flattened without retaining the original type.
But `StakingCredential` no longer exists in Plutus V4, whose `Address` type now carries a `Maybe AccountId` instead of `Maybe StakingCredential` (see the type definitions below).
That candidate is therefore gone, and every remaining nested sum type in the V4 types runs into one of the two drawbacks above.

__Nested product types.__
Nested product types can likewise be flattened into a single larger product type.
As with sum types, this should be done selectively, especially if we use list-encoding rather than array-encoding, because
- Flattening produces a longer list, making `dropList` more expensive
- Flattening makes constructing the nested type harder.
  For example, suppose type `A` contains a field of type `B`.
  If we flatten `B` into `A`, producing a flattened type `A'`, reconstructing `B` from `A'` becomes much more difficult and costly than extracting `B` directly from `A`.

Considering these trade-offs, we found only one clear case where flattening a nested product type is beneficial: the unnecessarily nested `Interval` type in Plutus V1-V3.

Plutus V4, however, will no longer use `Interval`; it will use the following type instead:

```haskell
data POSIXTimeRange = POSIXTimeRange
  { fromInclusive :: Maybe POSIXTime
    -- ^ Nothing means negative infinity
  , untilExclusive :: Maybe POSIXTime
    -- ^ Nothing means positive infinity
  }
```

We do not believe any other nested product type in the Plutus V4 script context warrants flattening.

### Plutus V4 script context and encoding rules

We specify the Plutus V4 ledger API types as Haskell datatypes plus encoding rules.
The Haskell datatypes are shown below.
The definitions of types reused from V1-V3 are omitted.

```haskell
data ScriptContext = ScriptContext
  { scriptContextTxInfo :: TxInfo
  -- ^ Information about the transaction the currently-executing script is included in
  , scriptContextRedeemer :: V2.Redeemer
  -- ^ Redeemer for the currently-executing script
  , scriptContextScriptInfo :: ScriptInfo
  -- ^ the purpose of the currently-executing script, along with information associated
  -- with the purpose
  , scriptContextScriptHash :: ScriptHash
  -- ^ Hash of the script that is being executed
  }

data TxInfo = TxInfo
  { txInfoId :: V3.TxId
  , txInfoSubTxIx :: Maybe Integer
  , txInfoInputs :: [TxInInfo]
  , txInfoReferenceInputs :: [TxInInfo]
  , txInfoOutputs :: [V2.TxOut]
  , txInfoMint :: Value -- now a built-in type
  , txInfoTxCerts :: [TxCert]
  , txInfoWithdrawals :: Map V2.Credential V2.Lovelace
  , txInfoDirectDeposits :: Map V2.Credential V2.Lovelace
  , txInfoAccountBalanceIntervals :: AccountBalanceIntervals
  , txInfoValidRange :: V2.POSIXTimeRange
  , txInfoGuards :: [V2.Credential]
  , txInfoRequiredTopLevelGuards :: Map V2.Credential (Maybe Datum)
  , txInfoRedeemers :: Map ScriptPurpose V2.Redeemer
  , txInfoData :: Map V2.DatumHash V2.Datum
  , txInfoVotes :: Map Voter (Map GovernanceActionId Vote)
  , txInfoProposalProcedures :: [ProposalProcedure]
  , txInfoCurrentTreasuryAmount :: Haskell.Maybe V2.Lovelace
  , txInfoTreasuryDonation :: V2.Lovelace
  }

data ScriptInfo
  = MintingScript V2.CurrencySymbol
  | SpendingScript V3.TxOutRef (Haskell.Maybe V2.Datum)
  | WithdrawingScript AccountId
  | CertifyingScript
      -- | 0-based index of the given `TxCert` in `txInfoTxCerts`
      Haskell.Integer
      TxCert
  | VotingScript Voter
  | ProposingScript
      -- | 0-based index of the given `ProposalProcedure` in `txInfoProposalProcedures`
      Haskell.Integer
      ProposalProcedure
  | GuardingScript
      Haskell.Integer
      -- | Whenever a `Guard` is executed at the top transaction level it will include extra
      -- information about potential sub-transactions. In other words for sub-transactions this is
      -- guaranteed to be `Nothing`, while for top level transactions this is guaranteed to be
      -- `Just`
      (Maybe TopTxInfo)

data TopTxInfo = TopTxInfo
  { topTxInfoSubTransactions :: [TxInfo]
  -- ^ List of `TxInfo`s for all sub-transactions. Not that `TxInfo` for the top level transaction
  -- itslef is not present in this list.
  , topTxInfoDatums :: Map TxId V2.Datum
  -- ^ Datums supplied in `requiredTopLevelGuards` for that script. Plutus scripts require a datum
  -- to be supplied when listed `requiredTopLevelGuards`. That `Map` will be empty if none of the
  -- transactions within the whole transaction require Plutus scripts to be present in `Guards`
  , topTxInfoStartingAccountBalanceIntervals :: AccountBalanceIntervals
  -- ^ This is a field that allows top level transaction to specify the balance intervals before
  -- the whole transaction is applied
  , topTxInfoSimplified :: TopTxInfoSimplified
  -- ^ Aggregated view on the whole transaction, namely information about sub-transactions and the
  -- top level transaction all concatenated together with loss of some information
  }

data TopTxInfoSimplified = TopTxInfoSimplified
  { ttisIds :: [V3.TxId]
  -- ^ List of all `TxId`s fro the whole transaction, including the top-level transaction, which is
  -- always going to be the last one in the list.
  , ttisInputs :: [TxInInfo]
  -- ^ Concatenated list of all `txInfoInputs`'
  , ttisReferenceInputs :: [TxInInfo]
  -- ^ Concatenated list of all `txInfoReferenceInputs`'
  , ttisOutputs :: [V2.TxOut]
  -- ^ Concatenated list of all `txInfoOutputs`'
  , ttisMints :: V3.MintValue
  -- ^ `MintValue`s from all `txInfoMint` with positive amounts
  , ttisBurns :: V3.MintValue
  -- ^ `MintValue`s from all `txInfoMint` with negative amounts
  , ttisTxCerts :: [TxCert]
  -- ^ Concatenated list of all `ttisTxCerts`'. Note, that unlike individual lists in each
  -- `txInfoTxCerts`, this one can contain duplicates.
  , ttisWithdrawals :: Map V2.Credential V2.Lovelace
  -- ^ Union of all `txInfoWithdrawals` with a sum on the range for duplicate credentials
  , ttisDirectDeposits :: Map V2.Credential V2.Lovelace
  -- ^ Union of all `txInfoWithdrawals` with a sum on the range for duplicate credentials
  , ttisValidRange :: V2.POSIXTimeRange
  -- ^ Intersection of all validity intervals from within the whole transaction
  , ttisGuards :: [V2.Credential]
  -- ^ Concatenated list of all `txInfoGuards`'
  , ttisRequiredTopLevelGuards :: Map V2.Credential ()
  -- ^ Deduplicated set of required top level guards. It is impossible to keep the range of the Map
  -- due to potential presence of duplicates in the domain between different sub-transactions,
  -- therefore the range is eliminated.
  , ttisScriptPurposes :: Map ScriptPurpose ()
  -- ^ Union of all of the `Redeemer`s. Note that it is not possible to preserve actual `Redeemer`s
  -- upon `union` operation due to potential duplicates in the domain. Therefore it is collapsed to
  -- a Set of `ScriptPurpose`s only with duplicates removed.
  , ttisData :: Map V2.DatumHash V2.Datum
  -- ^ Union of all `txInfoData`. Duplicates are simply removed, since domain and range are
  -- a one-to-one mapping.
  , ttisVotes :: Map Voter (Map GovernanceActionId Vote)
  -- ^ Union of all of the votes. Note that a vote in a sub-sequent sub-transaction or a top level
  -- transaction can replace a vote from a prior sub-transaction.
  , ttisProposalProcedures :: [ProposalProcedure]
  -- ^ Concatenated list of all `ProposalPrecedure`s.
  , ttisCurrentTreasuryAmount :: Haskell.Maybe V2.Lovelace
  -- ^ Value of the treasury, which will be present if any of sub-transactions or top level
  -- transaction included such value
  , ttisTreasuryDonations :: V2.Lovelace
  -- ^ Sum of all `txInfoTreasuryDonation`s
  }

data Address = Address
  { addressCredential :: Credential
  -- ^ the payment credential
  , addressStakingCredential :: StakingCredential
  -- ^ the staking credential (flattened)
  }

data TxInInfo = TxInInfo
  { txInInfoOutRef   :: V3.TxOutRef
  , txInInfoResolved :: TxOut
  }

data TxOut = TxOut
  { txOutAddress         :: Address
  , txOutValue           :: Value -- now a built-in type
  , txOutDatum           :: V2.OutputDatum
  , txOutReferenceScript :: Maybe V2.ScriptHash
  }

newtype AccountId = AccountId V2.Credential

-- flattened from the `Interval` in V1-V3
data Interval a = Interval
  { ivFrom        :: Extended a
  , ivFromClosure :: Closure
  , ivTo          :: Extended a
  , ivToClosure   :: Closure
  }

type POSIXTimeRange = Interval POSIXTime
```

The encoding rules are:

1. __Built-in types.__
   `Integer` encodes as `I`; `ByteString` as `B`; `Data` encodes as itself; `[]` encodes as `List`; `Map` encodes as `Map`; `Value` encodes as the new `Value` constructor of `Data` (this differs from V1-V3 where `Value` isn't a built-in type).
2. __Newtypes.__
   Newtypes are transparent: a newtype encodes the same as its underlying type.
3. __Product types__.
   Product types encode as `List [x1, ..., xn]`, where `xi` is the encoding of the `i`-th field.
   This differs from V1-V3, which encodes product types using `Constr 0`.
4. __Sum types.__
   Sum types encode as `Constr t [x1, ..., xn]`, where `t` is the constructor's 0-based index, and `xi` is the encoding of the `i`th constructor field.
   Constructors are indexed in the order in which they appear in the above Haskell datatypes.

## Rationale: How does this CIP achieve its goals?

The previous section already explains why we prefer list-encoding to array-encoding.
We also considered the following alternatives along other dimensions.

__Keeping the datatype definition idiomatic, and introducing special encoding rules for certain types.__
For example, in the datatype defitinion we continue to use `Maybe StakingCredential`, but in the encoding spec, we stipulate that `Maybe StakingCredential` should be encoded as a flat `Constr`.

Under this approach, every compiler targeting UPLC and any tool that needs to construct or inspect `Data` objects would need to implement the same set of type-specific exceptions.

We do not recommend this approach for two reasons:
- It complicates the spec: the spec would degrade from "a small set of general rules for deriving the encoding mechanically from the datatype definitions" to "rules plus a table of exceptions", and every compiler and tool would then need to ensure that the exceptions are implemented correctly.
- It complicates language implementations.
  For example, in Haskell, encodings and decodings are implemented using typeclasses `ToData` and `UnsafeFromData`.
  There is no nice way to encode the standalone `StakingCredential` differently than the `StakingCredential` in `Maybe StakingCredential`.
  The most obvious solution is adding newtype wrappers, but this would be quite annoying and inconvenient.

__Using bare `List`/`Array` to encode sum types__.
We previously proposed that product types should be encoded using `List`, rather than `Constr`.
We could do the same for sum types, where the first element of the `List` would represent the constructor tag.

If we use list-encoding, there would be little reason to do this, since it won't be cheaper than using `Constr`.
If we use array-encoding, then it would be slightly more appealing because it would allow us to avoid adding the `ConstrArray` constructor to `Data`.
However, accessing the constructor tag would then require an `indexArray 0` call which is much more expensive than extracting the tag from `ConstrArray`.
Also, under this approach, a product type and a sum type could have the same `Data` representation; it is unclear whether this could lead to problems.

## Path to Active

### Acceptance Criteria

- [ ] The encoding rules and revised types are implemented in `plutus-ledger-api`.
- [ ] A new `Data` type is created in `plutus-ledger-api` for Plutus V4, which should contain the `Value` constructor.

### Implementation Plan

- [ ] Implementation by the Plutus team
- [ ] Implementation by any authors of other languages targeting UPLC
- [ ] Implementation in related tooling

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
