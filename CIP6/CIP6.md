---
CIP: 6
Title: Extended Metadata
Authors: Mike Fullman <mike@fullman.net>, Markus <>
Comments-URI: 
Status: Draft
Type: Standards
Created: 2020-07-20
License: Apache-2.0
---

## Abstract

This CIP defines the concept of extended metadata for pools that is referenced from the pool registration data stored on chain.

## Motivation

As the ecosystem around cardano stake pools proliferate so will the desire to slice, organize and search pool information dynamically.  Currently the metadata refernced on chain provides 512 bytes that can be allocated across the four information categories:

| key           | Value                                |  Rules  | 
| ---           | ---                                  |  ---  |
|  `ticker` | Pool ticker.  uppercase | 5 Characters Maximum, Uppercase letters and numbers |
|  `description` | Pool Description.  Text that describes the pool | 50 Characters Maximum |
|  `homepage` | A website URL for the pool  | 64 Characters Maximum, must be a valid URL |
|  `name` | A name for the pool | 50 Characters Maximum |

Many additional attributes can be envisioned for future wallets, pool explorers, and information aggregators.  The proposal below outlines an initial strategy for capturing this extended metadata.
 
## Specification

#### On Chain referenced metadata file
We define one more line for the on chain referenced metadata file that references another json file on a url with the extended metadata.  The proposed metadata is as follows:

| key           | Value                                | Rules  | 
| ---           | ---                                  | ---  |
|  `ticker`       | Pool ticker.  uppercase              | 5 Characters Maximum, Uppercase letters and numbers  |
|  `description` | Pool Description.  Text that describes the pool | 50 Characters Maximum |
|  `homepage` | A website URL for the pool| 64 Characters Maximum, must be a valid URL |
|  `name` | A name for the pool | 50 Characters Maximum |
|  `extended` | A url for extended metadata| Optional, 64 Characters Maximum, must be a valid URL |

#### Extended Metadata
The file located at the URL for extended data is a json compliant text file with the following fields:

| key           | Value                                | Rules | 
| ---           | ---                                  | --- |
|  `itn.owner` | ITN pool public key | TBD |
|  `itn.witness` | Signature of mainnet pool id signed by teh ITN pool secret key | TBD |

#### Extended Metadata Schema

TBD

## Backwards compatibility

No fields are removed or changed in the current on chain metadata.  The new field `extended` is optional and not necessary to parse for any entities that do not need additional information about a pool

## Reference implementation

N/A

## Copyright

This CIP is licensed under Apache-2.0.
