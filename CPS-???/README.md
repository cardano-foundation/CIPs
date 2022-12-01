---
CPS: ?
Title: On chain dApp / scripts audits
Status: Open
Category: ?
Authors:
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Proposed Solutions: []
Created: 2022-12-01
---

# DRAFT - certification

## Abstract

Currently there is no way to check if a particular dApp version (release) or a given script has been audited from on-chain metadata.

## Problem

Our understand is that dApp on Cardano is nothing else that a collection of scripts, sometimes it could be even just one script. dApps are naturally evolving therefore they receive new versions and also new script hashes. We often find ourselves in the situation that we have to trust the people issuing scripts. In typical examples one can lookup a certification as PDF from e.g. certiK but there are cases where a team is claiming that a certification of a script is also valid for new version (e.g. when moving from Plutus V1 to Plutus V2). We don't want to trust anybody, we would like to build an indexer from on chain metadata and be able to verify that CertiK has signed off an audit. We don't want to have to trust teams / people building dApps that Plutus V1 certification / audit is also valid for Plutus V2.

If you look at crfa-offchain-metadata registry (https://github.com/Cardano-Fans/crfa-offchain-data-registry) and more specifically dApps currently we maintain manually the fact that there is an audit of a given dApp or not. We would prefer to automate this via on chain indexer and this data should be automatically injested without human level oracle involvement.

##  Possible solution
Propose a CIP where various certification companies will be able to certify a "dapp release" or certain scripts so that we know that they have been properly audited.