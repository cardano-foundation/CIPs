---
Title: Certification Standard Level 0
Authors:
    - Romain Soulat <romain.soulat@iohk.io>
Implementors: []
Created: 2023-11-10
License: CC-BY-4.0
---

## Overview

Certification Standard Level 0 is the first level of the certification standard. This level is used to define security audits that do not comply to any of the other levels of the certification standard. The other certification levels should be seen as the true "certification" levels. This level is useful for existing DApps, or their auditors, to publish those audits on-chain.

## Terminology

**shall** is to be interpreted as a requirement.

**should**  is to be interpreted as a recommendation.

## Documentation

The developer should follow CIP-0052 guidelines and provide the auditors with the relevant information to perform the audit. 

## Audit process

The auditor should follow CIP-0052 guidelines for the audit process.

## Certificate

The certificate shall be compliant with CIP-0096 on-chain and off-chain metadata schemas.

The fields shall be filled with the appropriate values as described in CIP-0096.

This section describes how the Auditor shall fill the certification metadata to reflect a Level 0 certification.

### On-chain metadata

The certificate on-chain metadata shall be issued with `type` set to `AUDIT`.

The certificate on-chain metadata shall be issued with `certificationLevel` set to `0`.

### Off-chain metadata

The certificate off-chain metadata shall be issued with `certificationLevel` set to `0`.
