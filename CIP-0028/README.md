---
CIP: 28
Title: Protocol Parameters (Alonzo Era)
Status: Active
Category: Ledger
Authors:
  - Kevin Hammond <kevin.hammond@iohk.io>
Implementors:
  - IOG
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/140
Created: 2021-10-14
License: Apache-2.0
---

## Abstract

This CIP extends CIP-0009 to include the new protocol parameters that have been introduced for Alonzo, specifically those relating to the costing of Plutus scripts.  It describes the initial settings for those parameters.

## Motivation: Why is this CIP necessary?

We need to document the chain of changes to the protocol parameters.  This document describes precisely the changes that have been made from CIP-0009, allowing the differences to be determined.  It thus supplements rather than replaces CIP-0009.

## Specification

### New Updatable Protocol Parameters

The new **updatable** protocol parameter values for Alonzo are given below (in JSON format).  Any of these parameters may be changed by submitting
a parameter update proposal to the chain, and without triggering a "hard fork".  Note that these parameters are given using the names used
in the genesis file.  Be aware that some parameters are shown differently using ``cardano-cli query protocol-parameters`` -- this has been raised
as an issue with the development team.

```
{
    "lovelacePerUTxOWord": 34482,
    "executionPrices": {
        "prSteps":
	{
	    "numerator" :   721,
	    "denominator" : 10000000
		},
        "prMem":
	{
	    "numerator" :   577,
	    "denominator" : 10000
	}
    },
    "maxTxExUnits": {
        "exUnitsMem":   10000000,
        "exUnitsSteps": 10000000000
    },
    "maxBlockExUnits": {
        "exUnitsMem":   50000000,
        "exUnitsSteps": 40000000000
    },
    "maxValueSize": 5000,
    "collateralPercentage": 150,
    "maxCollateralInputs": 3,
    "costModels": {
        "PlutusV1": {
            "sha2_256-memory-arguments": 4,
            "equalsString-cpu-arguments-constant": 1000,
            "cekDelayCost-exBudgetMemory": 100,
            "lessThanEqualsByteString-cpu-arguments-intercept": 103599,
            "divideInteger-memory-arguments-minimum": 1,
            "appendByteString-cpu-arguments-slope": 621,
            "blake2b-cpu-arguments-slope": 29175,
            "iData-cpu-arguments": 150000,
            "encodeUtf8-cpu-arguments-slope": 1000,
            "unBData-cpu-arguments": 150000,
            "multiplyInteger-cpu-arguments-intercept": 61516,
            "cekConstCost-exBudgetMemory": 100,
            "nullList-cpu-arguments": 150000,
            "equalsString-cpu-arguments-intercept": 150000,
            "trace-cpu-arguments": 150000,
            "mkNilData-memory-arguments": 32,
            "lengthOfByteString-cpu-arguments": 150000,
            "cekBuiltinCost-exBudgetCPU": 29773,
            "bData-cpu-arguments": 150000,
            "subtractInteger-cpu-arguments-slope": 0,
            "unIData-cpu-arguments": 150000,
            "consByteString-memory-arguments-intercept": 0,
            "divideInteger-memory-arguments-slope": 1,
            "divideInteger-cpu-arguments-model-arguments-slope": 118,
            "listData-cpu-arguments": 150000,
            "headList-cpu-arguments": 150000,
            "chooseData-memory-arguments": 32,
            "equalsInteger-cpu-arguments-intercept": 136542,
            "sha3_256-cpu-arguments-slope": 82363,
            "sliceByteString-cpu-arguments-slope": 5000,
            "unMapData-cpu-arguments": 150000,
            "lessThanInteger-cpu-arguments-intercept": 179690,
            "mkCons-cpu-arguments": 150000,
            "appendString-memory-arguments-intercept": 0,
            "modInteger-cpu-arguments-model-arguments-slope": 118,
            "ifThenElse-cpu-arguments": 1,
            "mkNilPairData-cpu-arguments": 150000,
            "lessThanEqualsInteger-cpu-arguments-intercept": 145276,
            "addInteger-memory-arguments-slope": 1,
            "chooseList-memory-arguments": 32,
            "constrData-memory-arguments": 32,
            "decodeUtf8-cpu-arguments-intercept": 150000,
            "equalsData-memory-arguments": 1,
            "subtractInteger-memory-arguments-slope": 1,
            "appendByteString-memory-arguments-intercept": 0,
            "lengthOfByteString-memory-arguments": 4,
            "headList-memory-arguments": 32,
            "listData-memory-arguments": 32,
            "consByteString-cpu-arguments-intercept": 150000,
            "unIData-memory-arguments": 32,
            "remainderInteger-memory-arguments-minimum": 1,
            "bData-memory-arguments": 32,
            "lessThanByteString-cpu-arguments-slope": 248,
            "encodeUtf8-memory-arguments-intercept": 0,
            "cekStartupCost-exBudgetCPU": 100,
            "multiplyInteger-memory-arguments-intercept": 0,
            "unListData-memory-arguments": 32,
            "remainderInteger-cpu-arguments-model-arguments-slope": 118,
            "cekVarCost-exBudgetCPU": 29773,
            "remainderInteger-memory-arguments-slope": 1,
            "cekForceCost-exBudgetCPU": 29773,
            "sha2_256-cpu-arguments-slope": 29175,
            "equalsInteger-memory-arguments": 1,
            "indexByteString-memory-arguments": 1,
            "addInteger-memory-arguments-intercept": 1,
            "chooseUnit-cpu-arguments": 150000,
            "sndPair-cpu-arguments": 150000,
            "cekLamCost-exBudgetCPU": 29773,
            "fstPair-cpu-arguments": 150000,
            "quotientInteger-memory-arguments-minimum": 1,
            "decodeUtf8-cpu-arguments-slope": 1000,
            "lessThanInteger-memory-arguments": 1,
            "lessThanEqualsInteger-cpu-arguments-slope": 1366,
            "fstPair-memory-arguments": 32,
            "modInteger-memory-arguments-intercept": 0,
            "unConstrData-cpu-arguments": 150000,
            "lessThanEqualsInteger-memory-arguments": 1,
            "chooseUnit-memory-arguments": 32,
            "sndPair-memory-arguments": 32,
            "addInteger-cpu-arguments-intercept": 197209,
            "decodeUtf8-memory-arguments-slope": 8,
            "equalsData-cpu-arguments-intercept": 150000,
            "mapData-cpu-arguments": 150000,
            "mkPairData-cpu-arguments": 150000,
            "quotientInteger-cpu-arguments-constant": 148000,
            "consByteString-memory-arguments-slope": 1,
            "cekVarCost-exBudgetMemory": 100,
            "indexByteString-cpu-arguments": 150000,
            "unListData-cpu-arguments": 150000,
            "equalsInteger-cpu-arguments-slope": 1326,
            "cekStartupCost-exBudgetMemory": 100,
            "subtractInteger-cpu-arguments-intercept": 197209,
            "divideInteger-cpu-arguments-model-arguments-intercept": 425507,
            "divideInteger-memory-arguments-intercept": 0,
            "cekForceCost-exBudgetMemory": 100,
            "blake2b-cpu-arguments-intercept": 2477736,
            "remainderInteger-cpu-arguments-constant": 148000,
            "tailList-cpu-arguments": 150000,
            "encodeUtf8-cpu-arguments-intercept": 150000,
            "equalsString-cpu-arguments-slope": 1000,
            "lessThanByteString-memory-arguments": 1,
            "multiplyInteger-cpu-arguments-slope": 11218,
            "appendByteString-cpu-arguments-intercept": 396231,
            "lessThanEqualsByteString-cpu-arguments-slope": 248,
            "modInteger-memory-arguments-slope": 1,
            "addInteger-cpu-arguments-slope": 0,
            "equalsData-cpu-arguments-slope": 10000,
            "decodeUtf8-memory-arguments-intercept": 0,
            "chooseList-cpu-arguments": 150000,
            "constrData-cpu-arguments": 150000,
            "equalsByteString-memory-arguments": 1,
            "cekApplyCost-exBudgetCPU": 29773,
            "quotientInteger-memory-arguments-slope": 1,
            "verifySignature-cpu-arguments-intercept": 3345831,
            "unMapData-memory-arguments": 32,
            "mkCons-memory-arguments": 32,
            "sliceByteString-memory-arguments-slope": 1,
            "sha3_256-memory-arguments": 4,
            "ifThenElse-memory-arguments": 1,
            "mkNilPairData-memory-arguments": 32,
            "equalsByteString-cpu-arguments-slope": 247,
            "appendString-cpu-arguments-intercept": 150000,
            "quotientInteger-cpu-arguments-model-arguments-slope": 118,
            "cekApplyCost-exBudgetMemory": 100,
            "equalsString-memory-arguments": 1,
            "multiplyInteger-memory-arguments-slope": 1,
            "cekBuiltinCost-exBudgetMemory": 100,
            "remainderInteger-memory-arguments-intercept": 0,
            "sha2_256-cpu-arguments-intercept": 2477736,
            "remainderInteger-cpu-arguments-model-arguments-intercept": 425507,
            "lessThanEqualsByteString-memory-arguments": 1,
            "tailList-memory-arguments": 32,
            "mkNilData-cpu-arguments": 150000,
            "chooseData-cpu-arguments": 150000,
            "unBData-memory-arguments": 32,
            "blake2b-memory-arguments": 4,
            "iData-memory-arguments": 32,
            "nullList-memory-arguments": 32,
            "cekDelayCost-exBudgetCPU": 29773,
            "subtractInteger-memory-arguments-intercept": 1,
            "lessThanByteString-cpu-arguments-intercept": 103599,
            "consByteString-cpu-arguments-slope": 1000,
            "appendByteString-memory-arguments-slope": 1,
            "trace-memory-arguments": 32,
            "divideInteger-cpu-arguments-constant": 148000,
            "cekConstCost-exBudgetCPU": 29773,
            "encodeUtf8-memory-arguments-slope": 8,
            "quotientInteger-cpu-arguments-model-arguments-intercept": 425507,
            "mapData-memory-arguments": 32,
            "appendString-cpu-arguments-slope": 1000,
            "modInteger-cpu-arguments-constant": 148000,
            "verifySignature-cpu-arguments-slope": 1,
            "unConstrData-memory-arguments": 32,
            "quotientInteger-memory-arguments-intercept": 0,
            "equalsByteString-cpu-arguments-constant": 150000,
            "sliceByteString-memory-arguments-intercept": 0,
            "mkPairData-memory-arguments": 32,
            "equalsByteString-cpu-arguments-intercept": 112536,
            "appendString-memory-arguments-slope": 1,
            "lessThanInteger-cpu-arguments-slope": 497,
            "modInteger-cpu-arguments-model-arguments-intercept": 425507,
            "modInteger-memory-arguments-minimum": 1,
            "sha3_256-cpu-arguments-intercept": 0,
            "verifySignature-memory-arguments": 1,
            "cekLamCost-exBudgetMemory": 100,
            "sliceByteString-cpu-arguments-intercept": 150000
        }
    }
}
```

The meaning of the fields is:

| Field                 	| Initial Value                                                          	| Description                                                                                                                                                                                                                      	|
|-----------------------	|------------------------------------------------------------------------	|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| lovelacePerUTxOWord       	| 34482 	| Deposit charged per word of UTxO storage.  |
| executionPrices | `{ "prSteps": { "numerator" : 721, "denominator" : 10000000}, "prMem": { "numerator" :   577, "denominator" : 10000 } }` | Fee per Plutus execution step and per memory unit |
| maxTxExUnits | `{ "exUnitsMem":   10000000,        "exUnitsSteps": 10000000000 }` | Maximum number of memory units and steps in a single transaction. |
| maxBlockExUnits | `{ "exUnitsMem":   50000000, "exUnitsSteps": 40000000000 }` | Maximum number of memory units and steps in a single block. |
| maxValueSize | 5000 | The limit on the serialized size of the Value in each output. |
| collateralPercentage | 150 | Percentage of fee that is used as collateral for a failed transaction. |
| maxCollateralInputs | 3 | Maximum number of collateral inputs in a transaction. |
| costModels | `{  "PlutusV1": { ... } }` | Detailed cost models for each Plutus version. |

Each version of the Plutus interpreter may use different cost model parameters and settings.  Although the parameters are updatable,
they are likely to be changed only when introducing new Plutus interpreter versions at a "hard fork".
For simplicity, the details of the parameter settings is omitted here.

### Obsoleted Updatable Protocol Parameters

``minUTxOValue`` is no longer used.  It is replaced by ``lovelacePerUTxOWord``.

### Non-Updatable Parameters

There are no changes to the non-updatable protocol parameters.

## Rationale: How does this CIP achieve its goals?

The majority of the parameters are needed to enable the use of Plutus scripts on-chain.  They relate to the fees calculations for
transactions that include Plutus scripts.

``executionPrices`` are specified in fractions of lovelace per Plutus CPU execution step or memory unit.
These have been set to be consistent with the cost for a full transaction.

``lovelacePerUTxOWord`` replaces ``minUTxOValue``.
Rather than determining a fixed minimum deposit, the new value scales each word that is used.
The value is set to give a very similar result for an ada-only UTxO entry (previously, 1,000,000 lovelace; now 999,978 lovelace, since each ada-only
UTxO entry is 29 words).

``collateralPercentage``has been chosen to be higher than the transaction fee.  Collateral should only be used to pay fees if a user has deliberately
submitted a transaction that is known to fail.  Setting the percentage high acts to discourage the submission of rogue transactions, which
maliciously consume chain resources.

``maxCollateralInputs`` has been set to allow the option of multiple inputs to be used to pay collateral, if needed (e.g. so that
multiple instance of a transaction can be submitted without sharing a single collateral, that might restrict concurrency or cause
script failure if the collateral was not available).

``maxValueSize`` has been set based on benchmarking.

``costModels`` has been set for ``PlutusV1`` based on benchmarking inputs.  Each Plutus Core primitive has associated costs.

## Path to Active

### Acceptance Criteria

- [x] The Alonzo ledger era is activated.
- [x] Documented parameters have been in operational use by Cardano Node and Ledger as of the Alonzo ledger era.

### Implementation Plan

- [x] Alonzo ledger era parameters are deemed correct by working groups at IOG.

## Copyright

This CIP is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
