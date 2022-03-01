---
CIP: ?  
Title: Deterministic transaction input ordering
Authors: Gergely Szabo <gergely@mlabs.city>  
Discussions-To:   
Comments-Summary:   
Comments-URI:   
Status: Draft  
Type: Standards Track  
Created: 2022-02-25  
License: Apache-2.0  
---

# Deterministic transaction input ordering

## Abstract

This CIP proposes a way to improve efficiency of handling transaction inputs in Plutus scripts by changing the way they are representend in the ledger.

## Motivation

The current implementation of the transaction body stores transaction inputs as a set. When interacting with transaction inputs inside a validator script, this representation changes to a linked list, but the ordering of the transaction inputs is different than that of the originally submitted transaction's. In the case when we want to find a certain transaction input on chain, we need to do a costly filtering on the input list with the worst case of O(n).
However if the transaction inputs would be stored as an array, preserving the original ordering, we could better optimise our scripts by determining the order of inputs off-chain and simplifying the search to a pattern match.
For example, for a script needing transaction inputs for two purposes: one for updating the datum of the script, and one or more for supplying the funds. We could order these inputs such that the one including the datum comes first, and then we can use a pattern match `txWithDatum : txWithFunds = txInfoInputs`.

## Specification

In the CDDL definiotion of the transaction body, transaction inputs will need to be changed from Set to Array:

```
transaction_body =
 { 0 : [* transaction_input]     ; inputs
 , 1 : [* transaction_output]
 , 2 : coin                      ; fee
 , ? 3 : uint                    ; time to live
 , ? 4 : [* certificate]
 , ? 5 : withdrawals
 , ? 6 : update
 , ? 7 : auxiliary_data_hash
 , ? 8 : uint                    ; validity interval start
 , ? 9 : mint
 , ? 11 : script_data_hash       ; New
 , ? 13 : set<transaction_input> ; Collateral ; new
 , ? 14 : required_signers       ; New
 , ? 15 : network_id             ; New
 }
```

Note that the Set is defined in the cardano-ledger specification as an Array of zero or more elements `set = [* a]`, so this would only cause a semantic change, without the actual change of the underlying data structure.

## Rationale

In theory we could pre-calculate the index of the searched transaction input off-chain, by relying on the ordering of transaction inputs (lexicographic ordering on `(TransactionID, TransactionIndex)`). But then, to pass this information to the script, we would need to use a redeemer, which could defeat the purpose of this optimisation with it's own fees. Also, we could only reliably do this after transaction balancing, but changing the transaction after balancing could affect fees, rendering the transaction unbalanced again. This method also introduces unnecessary complexity.

## Backward Compatibility

As noted in the specification above, the underlying CBOR data structure only changes semantically, so we do not need any backwards compatibility measures.

## Test Cases

We need regression tests to assert that no utxo appears twice in the transaction input list.

## Implementations

The ledger implementation currently represents transaction inputs as a Map with the key of `(TransactionID, TransactionIndex)`.

## Copyright

This CIP is licensed under Apache-2.0
