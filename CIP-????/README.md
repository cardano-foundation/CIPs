---
CIP: "?"
Title: UTxO Storage Cost Formula
Category: Ledger
Status: Proposed
Authors:
    - Nicolas Henin <nicolas.henin@iohk.io>
    - Will Gould <will.gould@iohk.io>
    - Polina Vinogradova <polina.vinogradova@iohk.io>
Implementors: []
Discussions:
    - "CPS review: https://github.com/cardano-foundation/CIPs/pull/1268"
Solution To:
    - "CPS-0037: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0037"
Created: 2026-11-10
License: CC-BY-4.0
---

## Abstract

On Cardano, every output must contain a certain minimum amount of ADA. This 
minimum is commonly called minutxo, and its calculation is currently based on 
the output.

The current minutxo formula is challenging to calculate and has been explicitly 
referenced as a pain point by community members; specifically, the 
recursive nature of the calculation. 

This CIP seeks to simplify the calculation and remove the need to measure the complete
serialised TxOut. The suggested formula calculates minimum ADA from the address size,
the number of distinct native assets, and the sizes of any datum and reference script.
This makes the calculation easier to reproduce consistently across the tools and
programming languages used to construct transactions.

## Motivation: Why is this CIP necessary?

Cardano's minimum-ADA requirement gives users an economic incentive to use the live UTxO
set efficiently. Creating more outputs, or larger outputs, requires more ADA to remain
committed while those outputs are unspent. This funding requirement is an intended part
of protecting the resource maintained by nodes.

Community feedback collected in CPS-0037 also identifies difficulties caused by the
calculation itself. Developers must handle a requirement that can change as they fund an
output, and reproduce detailed output-sizing rules wherever transactions are
constructed. This CIP aims to reduce that development burden while preserving the
economic deterrent.
[CPS-0037](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0037)

### 1. Funding an output can change the amount it needs

Consider an application preparing an output to send a native token. It needs to
determine how much ADA must accompany that token.

With the current calculation, the following sequence can occur.

1. The application constructs the output with a provisional ADA amount and calculates
   its minimum.
2. It adds enough ADA to meet that minimum.
3. The new ADA amount takes more bytes to encode. The output becomes larger, increasing
   its minimum again.

The application has followed the first calculation, yet the resulting output can still
contain insufficient ADA. Transaction-building software must account for this dependency
and adjust the amount until the final output satisfies the rule.

This complicates the task of deciding how much ADA to allocate to recipients and how
much to return as change. The same dependency must be handled for every output being
constructed, including change outputs.

The proposed calculation makes the minimum independent of the ADA amount being chosen.
Once the output's other contents are determined, software can calculate its requirement
and fund it without that funding increasing the requirement again.

### 2. The calculation must be reproduced throughout the ecosystem

Minimum ADA must be calculated before a transaction reaches a node. Wallets, SDKs,
applications, backend services and scripts all need access to a calculation that agrees
with the ledger.

Today, that means obtaining the exact encoded size of the complete output. The result
depends on details such as the lengths of asset names, the encoding of quantities and
how assets are grouped under policy IDs. Software must either use a suitable serializer
or reproduce its sizing rules accurately.

This requirement carries implementation and maintenance work into every environment
where transactions are built, including TypeScript, Rust and other languages. A sizing
error can leave an output underfunded and cause the transaction to fail validation.

The proposed formula uses fixed allowances, counts distinct native assets and measures
the address, datum and reference script. This gives transaction-building tools a smaller
set of measurements to implement and verify, making the minimum-ADA rule easier to
support consistently across the ecosystem.

## Specification

### 1. Formula

```math
\begin{aligned}
\mathrm{minimumAda}
  ={}& \mathrm{coinsPerUTxOByte} \times \bigl( \\
     & 193 + 74 \times \mathrm{numberOfNativeAssets} \\
     & {}+ \mathrm{serializedAddressBytes} \\
     & {}+ \mathrm{serializedDatumBytes} \\
     & {}+ \mathrm{serializedReferenceScriptBytes}\bigr)
\end{aligned}
```

The address size is required because bootstrap addresses can be significantly 
larger than other address types, up to 4.7KB, most of which can come from 
custom attributes. An attacker can specify up to 254, each of which costs up to 
18 bytes if maximally padded; the ledger does have a 64-byte limit on 
attributes, but it only counts the derivation path and custom attribute values,
so none of these 18 bytes count toward it. So, this would offer exactly the kind 
of attack surface minutxo exists to curb, if we were to omit the address size.

See the following for some examples, with `coinsPerUTxOByte = 4310` as it 
currently is on mainnet. Note that the current formula column shows ranges 
because outputs with the same asset count can differ in size depending on the 
lengths of the asset names, the encoded sizes of the quantities, and the number 
of distinct policy IDs.

| Address | Other output measurements | Pricing units | Required lovelace | Alternative formula ([Rationale §1](#1-primary-alternative-for-community-consideration)) | Current formula |
| --- | --- | ---: | ---: | ---: | ---: |
| Base (57 bytes) | No native assets, datum or script | $`193 + 57`$ | 1,077,500 | 1,077,500 | 969,750 |
| Base (57 bytes) | One native asset, no datum or script | $`193 + 57 + 74`$ | 1,396,440 | 1,396,440 | 1,120,600–1,297,310 |
| Base (57 bytes) | Two native assets, no datum or script | $`193 + 57 + 74 \times 2`$ | 1,715,380 | 1,715,380 | 1,133,530–1,616,250 |
| Base (57 bytes) | Ten native assets, no datum or script | $`193 + 57 + 74 \times 10`$ | 4,266,900 | 4,266,900 | 1,236,970–4,167,770 |
| Base (57 bytes) | One native asset and a 32-byte datum hash | $`193 + 57 + 74 + 32`$ | 1,534,360 | 1,534,360 | 1,267,140–1,443,850 |
| Base (57 bytes) | One native asset, a 100-byte serialised inline datum and a 200-byte serialised reference script | $`193 + 57 + 74 + 100 + 200`$ | 2,689,440 | 2,689,440 | 2,491,180–2,667,890 |
| Enterprise (29 bytes) | No native assets, datum or script | $`193 + 29`$ | 956,820 | 1,077,500 | 849,070 |
| Bootstrap, Icarus style (43 bytes) | No native assets, datum or script | $`193 + 43`$ | 1,017,160 | 1,017,160 | 909,410 |
| Bootstrap, Daedalus style (76 bytes) | No native assets, datum or script | $`193 + 76`$ | 1,159,390 | 1,159,390 | 1,051,640 |
| Bootstrap, padded (4,721 bytes) | No native assets, datum or script | $`193 + 4721`$ | 21,179,340 | 21,179,340 | 21,075,900 |

### 2. Formula inputs

- `coinsPerUTxOByte`: the protocol parameter in effect for the transaction, in
  lovelace per byte.
- `numberOfNativeAssets`: the number of distinct pairs of policy ID and asset 
  name in the output, excluding ADA.
- `serializedAddressBytes`: the size of the address, in bytes: the bytes its
  bech32 or base58 text encodes (57 for a base address).
- `serializedDatumBytes`: the size of the datum, in bytes: 32 when the output 
  carries a datum hash, and the length of the serialised datum itself when the 
  output carries an inline datum; zero if absent.
- `serializedReferenceScriptBytes`: the size of the reference script, in bytes,
  as measured for the reference-script fee; zero if absent.

Each size is measured on the bytes as they appear in the transaction.

### 3. Enforcement and compatibility

The ledger applies the new formula to outputs created after activation.

### 4. Versioning

Any change to the formula's constants or inputs requires a new CIP that
supersedes this one.

## Rationale: How does this CIP achieve its goals?

We achieve the goal of avoiding recursive calculation by omitting ADA quantity 
from the formula.

We achieve this in balance with keeping overestimates close "enough" 
to the current formula, and while keeping underestimates to a minimum.

The constant 193 consists of the existing 160, plus 33, approximating the 
additional components of a near-worst-case output. The constant 74 is made up 
of: 
- 30 for the policy ID (a 28-byte hash and a 2-byte header)
- 1 for the header of that policy's asset map
- 34 for the asset name (32 bytes and a 2-byte header)
- 9 for the quantity (8 bytes and a 1-byte header)

We tested this against the 85.7 million outputs created on mainnet in the
Conway era, from its first block, at slot 133,660,855 with hash
`9aa420cf998dbcceec1abaf83ab26294d278d25527e779050ab334c1fadab16c`
(1 September 2024), to the block at slot 201,657,572 with hash
`30c61172934757a8c210a110b7a4cbf657e53c2f9f60678d6325d80a04c56328`
(28 October 2026). Note that this includes outputs that have already been spent. 
Each output is compared with what the current formula required:

**Funding requirements**

| Formula | Mean requirement | Below the current minimum<br>(outputs / largest shortfall) |
| --- | ---: | ---: |
| Current | 1.43 ADA | – / – |
| No address term | 1.91 ADA | 0 / none |
| Asset and policy counts with address, asset-name, datum and script sizes ([Rationale §2](#2-alternative-formulae-considered)) | 1.53 ADA | 0 / none |
| Token count and datum size only ([Rationale §2](#2-alternative-formulae-considered)) | 1.91 ADA | 5,253 (0.006%) / 69.24 ADA |
| Byte-based formula with a fixed ADA encoding allowance ([Rationale §2](#2-alternative-formulae-considered)) | 1.45 ADA | 0 / none |
| Primary alternative ([Rationale §1](#1-primary-alternative-for-community-consideration)) | 1.91 ADA | 0 / none |
| This CIP ([Specification §1](#1-formula)) | 1.89 ADA | 0 / none |

**Excess over the current requirement (median / 95th percentile)**

| Formula | All outputs | Outputs with 6+ native assets |
| --- | ---: | ---: |
| Current | – / – | 0.00% / 0.00% |
| No address term | 11.1% / 37.3% | 80.70% / 245.93% |
| Asset and policy counts with address, asset-name, datum and script sizes | 4.0% / 6.8% | 17.14% / 42.33% |
| Token count and datum size only | 11.1% / 37.3% | 80.70% / 245.93% |
| Byte-based formula with a fixed ADA encoding allowance | 1.5% / 2.0% | 0.39% / 0.85% |
| Primary alternative | 11.1% / 37.3% | 80.72% / 245.93% |
| This CIP | 11.1% / 30.8% | 80.71% / 245.87% |

<details>
<summary>Formulae compared</summary>

Multiply each expression by $`\mathrm{coinsPerUTxOByte}`$ to obtain the minimum in lovelace.

**Current**

$`160 + \mathrm{serializedOutputBytes}`$

**No address term**

$`\begin{aligned} & 250 \\ & {}+ 74 \times \mathrm{numberOfNativeAssets} \\ & {}+ \mathrm{serializedDatumBytes} \\ & {}+ \mathrm{serializedReferenceScriptBytes} \end{aligned}`$

**Asset and policy counts with address, asset-name, datum and script sizes**

$`\begin{aligned} & 175 \\ & {}+ \mathrm{serializedAddressFieldBytes} \\ & {}+ 12 \times \mathrm{numberOfNativeAssets} \\ & {}+ 30 \times \mathrm{numberOfMintingPolicies} \\ & {}+ \mathrm{totalAssetNameBytes} \\ & {}+ \mathrm{serializedDatumFieldBytes} \\ & {}+ \mathrm{serializedReferenceScriptFieldBytes} \end{aligned}`$

**Token count and datum size only**

$`\begin{aligned} & 250 \\ & {}+ 74 \times \mathrm{numberOfNativeAssets} \\ & {}+ \mathrm{serializedDatumBytes} \end{aligned}`$

**Byte-based formula with a fixed ADA encoding allowance**

$`\begin{aligned} & 160 \\ & {}+ \mathrm{serializedOutputBytes} \\ & {}- \mathrm{serializedAdaAmountBytes} \\ & {}+ 9 \end{aligned}`$

**Primary alternative**

$`\begin{aligned} & \mathrm{baseAllowance} \\ & {}+ 74 \times \mathrm{numberOfNativeAssets} \\ & {}+ \mathrm{serializedDatumBytes} \\ & {}+ \mathrm{serializedReferenceScriptBytes} \end{aligned}`$

**This CIP**

$`\begin{aligned} & 193 \\ & {}+ 74 \times \mathrm{numberOfNativeAssets} \\ & {}+ \mathrm{serializedAddressBytes} \\ & {}+ \mathrm{serializedDatumBytes} \\ & {}+ \mathrm{serializedReferenceScriptBytes} \end{aligned}`$

</details>

These figures are for Conway-era outputs, but it should be noted that 
Babbage-era outputs give higher excess figures: a 95th percentile of 79.3% for
this CIP's formula. Additionally, while there are no under-estimates of 
Conway-era outputs from this CIP's formula, 8,034 Babbage-era outputs are 
under-estimated. Most of this is due to Babbage-era outputs being capable of 
carrying asset entries with zero quantities, which the ledger now rejects.

Method, full results and reproduction: [historical backtest](https://github.com/willjgould/cardano-minutxo-integration/blob/2abe34cabf72799d8c122f23c23f03da31c48415/docs/minutxo-calibration/history-formulas.md).

### 1. Primary alternative for community consideration

An alternative can be adopted if there is a community desire to avoid address
serialisation in most cases. Its base allowance depends on the address type.

```math
\mathrm{baseAllowance} =
\begin{cases}
193 + \mathrm{serializedAddressBytes} & \text{for a bootstrap address} \\
250 & \text{otherwise}
\end{cases}
```

```math
\begin{aligned}
\mathrm{minimumAda}
  ={}& \mathrm{coinsPerUTxOByte} \times \bigl( \\
     & \mathrm{baseAllowance} \\
     & {}+ 74 \times \mathrm{numberOfNativeAssets} \\
     & {}+ \mathrm{serializedDatumBytes} \\
     & {}+ \mathrm{serializedReferenceScriptBytes}\bigr)
\end{aligned}
```

Here, we consider the address only if it's a bootstrap address. Remember: 
bootstrap addresses can be up to 4.7KB, so a formula that doesn't consider 
the address size is vulnerable to a potential attack.

### 2. Alternative formulae considered

| Alternative | Formula | Trade-off |
| --- | --- | --- |
| Asset and policy counts with address, asset-name, datum and script sizes | $`\begin{aligned} & \mathrm{coinsPerUTxOByte} \times \bigl( \\ & 175 \\ & {}+ \mathrm{serializedAddressFieldBytes} \\ & {}+ 12 \times \mathrm{numberOfNativeAssets} \\ & {}+ 30 \times \mathrm{numberOfMintingPolicies} \\ & {}+ \mathrm{totalAssetNameBytes} \\ & {}+ \mathrm{serializedDatumFieldBytes} \\ & {}+ \mathrm{serializedReferenceScriptFieldBytes}\bigr) \end{aligned}`$ | Close to the current formula results, but more complex |
| Token count and datum size only | $`\begin{aligned} & \mathrm{coinsPerUTxOByte} \times \bigl( \\ & 250 \\ & {}+ 74 \times \mathrm{numberOfNativeAssets} \\ & {}+ \mathrm{serializedDatumBytes}\bigr) \end{aligned}`$ | Simple, but underestimates too much |
| Byte-based formula with a fixed ADA encoding allowance | $`\begin{aligned} & \mathrm{coinsPerUTxOByte} \times \bigl( \\ & 160 \\ & {}+ \mathrm{serializedOutputBytes} \\ & {}- \mathrm{serializedAdaAmountBytes} \\ & {}+ 9\bigr) \end{aligned}`$ | Very close to the current formula, but depends on the whole output |

### 3. Alternative implementation

This CIP requires ledger changes, but ledger changes aren't necessary in order 
to solve the recursive nature of the minutxo formula.

Instead, we can simply disseminate the byte-based alternative formula with a 
fixed ADA encoding allowance, which never underestimates, throughout tooling 
only, thus leaving the ledger-enforced formula as it is today. This would give 
users a straightforward way to calculate a sufficient ADA amount, while 
preserving the option to calculate a tighter minimum if they want to commit less 
ADA.

The byte-based formula with a fixed ADA encoding allowance:

$`\begin{aligned} & \mathrm{coinsPerUTxOByte} \times \bigl( \\ & 160 \\ & {}+ \mathrm{serializedOutputBytes} \\ & {}- \mathrm{serializedAdaAmountBytes} \\ & {}+ 9\bigr) \end{aligned}`$

Subtracting the ADA amount's encoded size and replacing it with its maximum of 
9 bytes makes the estimate independent of the amount. Adding ADA doesn't change 
the estimate, and the estimate cannot fall below the ledger's requirement.

As such, we can leave the ledger-enforced formula as it currently stands, and 
provide people with the fixed ADA encoding allowance formula via tooling.

## Path to Active

### Acceptance Criteria

- [ ] The specified minimum-ADA formula is implemented and activated on Cardano 
mainnet.

### Implementation Plan

Implementation requires updating the ledger specification and minimum-ADA 
validation to use the new formula, and updating transaction-building tools to 
calculate the same requirement.

The changes must be implemented, tested and included in a node release. 
Activation requires a hard fork.

## References

- [CPS-0037: application and transaction friction in minUTxO implementation](../CPS-0037/README.md)
- [CIP-0055: Protocol Parameters (Babbage Era)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0055), which defines the current formula

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
