---
CPS: ?
Title: On chain dApp / scripts audits
Status: Open
Category: Metadata
Authors:
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Proposed Solutions: ?
Created: 2022-12-01
---

## Abstract

Currently there is no way to check if a particular dApp version (release) or a given script has been audited by a certain auditing company / party from on-chain metadata. As a developer using on-chain metadata I would like to verify that a given script hash has been audited by a certain auditing company. 

## Problem

A typical understanding of dApps on Cardano is that a dApp is nothing else that a collection of scripts (identifiable by a script hash), sometimes it could be even just one script. dApps are naturally evolving therefore they receive new versions and also new script hashes. We often find ourselves in the situation that we have to trust the people issuing scripts. A typical process is that by manually, without any automated process, one can open audit / certification as PDF from an auditing company (e.g. certiK) and check if audit applies to given script hashesh. This process is manual but it works, however, in some cases a company / people issing a script may claim that a former certification of a script is also valid for new version (e.g. when moving from Plutus V1 to Plutus V2). One should not trust issuers, one should be able to verify in an automated manner that a given script (hash) is audited by certain certification / audit which lives on chain and is signed by a certain auditing company.

If you look at crfa-offchain-metadata registry [https://github.com/Cardano-Fans/crfa-offchain-data-registry]    (https://github.com/Cardano-Fans/crfa-offchain-data-registry) and more specifically dApps currently we maintain manually the fact that there is an audit of a given dApp or not. We would prefer to automate this via on chain indexer and this data should be automatically injested without any human involvement.

## Use cases
- DappsOnCardano.com would like to show a certification icon and link to audit report and be certain that this audit is pertinent for a given dApp - in our case all scripts that belong to a certain dApp have been audited.
- lace wallet would like to know if a given dApp is fully audited and certified.
- A certification / auditing company would like to issue an audit report assuring that certain scripts have been audited with a link to an off chain (e.g. IPFS) audit report.

## Goals
- issuing an audit report for a given dApp
- identify issuing company and that their signing keys indeed belong to them in an automated fashion
- protection against fake signing audit report, somebody signed audit report but it wasn't a certification company
- verify that a given script hash belongs to a certain audit report
- certification / audit could be AUTOMATED or MANUAL, MANUAL would be done by humans and certification company / auditing firm but AUTOMATED one could be done by e.g. Marlowe software suite or any other tool which could do an automated formal verification
- It should be possible to issue multiple MANUAL / AUTOMATED certifications for a given "dApp release" or set of scripts since it is not uncommon that a given dApp has multiple certifications.

## Open Questions

- how would I know that a given audit is not signed by a fake certification company (we don't have on Cardano key distribution system like keybase)?
- Since a dApp is a collection of scripts how do I know that audit report signs all scripts which compose of a dApp?
- Since dApps have releases, v1, v2, how do I know that a previous audit is still valid for a new script, it seems like audit reports should be released for each new script hash?

## Possible solution
Propose a CIP where various certification companies / auditing firms will be able to certify a "dapp release" or certain scripts so that anybody interested in this infrmation will be able to subscribe to those on chain event and verify that have been properly audited.
