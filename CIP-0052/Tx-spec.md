# Cardano Tx blueprint specification

## Purpose
Establish a standard submitter requirement for a Plutus on-chain audit. This standard is designed to be orthogonal to the domain of the DApp, easy to write, intuitive and helpful for the auditor and finally, concrete.

## Content
The common aspect to all Plutus DApps is their transaction blueprint specification. That is, what are the allowable transactions for the particular set of validator scripts and monetary policies in question and what are the specific datum/redeemer pairs that must be consumed and the expectations on the produced datums.

This document should include the system flow or transaction dependency. For example, if the system is a DEX, we would expect the flow to outline that one must initiate a pool *before* applying an order to it.

## Format
Designed to be as intuitive as possible. No additional explanation needed after looking at an example:
```YAML
transactions:
  openPool:
    inputs:
      pkUtxo:
        value: v
        satisfies: v must have 2 coins with at least M amount. # spoken-language annotation

    mints:
      factoryToken:
        amount: 1

    outputs:
      scriptUtxo:
        script: poolValidator
        datum: Pool v
        value: v <> factoryToken(1)

  buy:
    inputs:
      scriptUtxo:
        script: poolValidator
        datum: Pool v1
        redeemer: Buy

      pkUtxo:
        address: a
        value: v2

    outputs:
      scriptUtxo:
        script: poolValidator
        datum: Pool buyEquationPool(v1, v2)
        value: buyEquationPool(v1, v2) # buyEquation is a pure-math formula listed somewhere…

      pkUtxo:
        address: a
        value: buyEquationBuyer(v1, v2)
```

## Format Considerations
We should rely on a simple textual format for two reasons: 
  *  easy to automatically generate and consume with tooling; and 
  *  easy to incorporate as comments to code and or Markdown files, which is how most clients provide their design documents.

## Specifying Tx-flow
In addition to specifying each transaction separately, these will be presented to the chain according to an underlying logic, or flow, which could be seen as a state transition system. Ideally these flows will be specified, but it is understood that specifying those systems formally is a lot of work and detail. We propose a very high-level description of these systems, which omits a lot of detail but conveys the essential information needed by the auditor.

We advocate for a simple, flat, set of states: all the states' labels appearing. We can easily generate a dot-file from this and it is low-effort for the developer of the contract to produce. Developers and auditors can add more information as they want on the label itself, which should be ids of elements in the transactions listed above.
```YAML
flow:
  startGovernance:
	from: initial
	to: hasNPools(0)

  openPool:
	from: hasNPools(n)
	to: hasNPools(n+1)

  buy:
	id: hasNPools(n)

  sell:
	id: hasNPools(n)

  closePool:
	from: hasNPools(n+1)
	to: hasNPools(n)
```

It is worth noting that `hasNPools(n+1)` should perhaps be read as just a string, not parsing the application of `n+1` to a family of states `hasNPools`. Even if the output graph contains three states labeled `hasNPools(0)`, `hasNPools(n)` and `hasNPools(n+1)` the auditor can still have a clear understanding of the flow of the DApp in question.

