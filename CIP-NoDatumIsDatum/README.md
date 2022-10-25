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

Currently if a transaction is sent to a script without a datum it means that even if the script is `alwaysTrue` then that utxo is unable to be consumed. This enables the use case of spending scrips without datums