---
CIP: ????
Title: No Datum Is Unit
Author: Maksymilian 'zygomeb' Brodowicz <zygomeb@gmail.com>
Status: Draft
Type: Standards Track
Created: 2022-08-23
License: CC-BY-4.0
---

## Simple Summary / Abstract

The CIP changes interpretation of how the absence of a datum hash or inline datum is interpreted. The entire scope of what is does is make it so that such a UTXO is equivalent to a one that has `()` as the datum for the purpose of script evaluation.

## Motivation / History

Currently if a transaction is sent to a script without a datum it means that even if the script is `alwaysTrue` then that utxo is unable to be consumed. This enables the use case of spending scrips without datums and lets us design scripts that are more fault-tolerant.

## Specification

When trying to consume a utxo without a datum hash or an inline datum, the node would substitute a unit datum as an argument instead.

## Rationale

The scripts always failing on a missing datum seems like an oversight, especially for spending scripts that make no use of datums which are forced to include the unit datum anyway and increase the likelihood of an erroneous transaction be made. 

## Backwards compatibility

This change can be made to the node without creating a new language version as every utxo locked in this way was forever lost anyway.

## Copyright

This CIP is licensed under Apache-2.0