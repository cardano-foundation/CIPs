---
CPS: ?
Title: Reading transaction metadata in Plutus contracts
Status: Open
Category: Plutus
Authors:
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Proposed Solutions: 
    - reading metadata via reference inputs

Created: 2023-03-09
---

## Abstract

In Plutus we can only read datums but we cannot read metadata.

## Problem
There are cases where reading metadata from Plutus is beneficial without having to go via Datums first.

## Use cases

- Imagine you run a metadata based oracle service such as nut.link (https://nut.link), regularly published oracle feeds cannot be used by Plutus based smart contracts. One solution (workaround?) is something like Charlie C3 Oracles, where feed service is datum based but being able to read metadata based oracles should be allowed as well.

- dApps around Catalyst will be limited since wallets registered with metadata and this cannot be read by smart contracts

## Goals
- Expose transaction metadata in read only matter to Plutus smart contracts.

##  Possible solution
- Make it possible to read metadata via CIP-31 compatible reference inputs.
