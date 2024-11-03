---
CIP: 134
Title: Cardano URIs - Address Representation
Category: Wallets
Status: Proposed
Authors:
  - Steven Johnson <steven.johnson@iohk.io>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/888
Created: 2024-08-23
License: CC-BY-4.0
---

## Abstract

This CIP proposes an extension to [CIP-0013] to allow easy and unambiguous encoding of
[CIP-0019]/[CIP-0105] Addresses into URL's.

## Motivation: why is this CIP necessary?

[CIP-0013] defines encoding for payment addresses and stake pool, however [CIP-0019]
and [CIP-0105] define numerous other address types.

These addresses cannot currently be encoded into URIs unambiguously.
This extension proposes a simple and forward compatible method of encoding such addresses into the URI scheme defined by [CIP-0013].

[x509] certificates can contain name or alternative name information related to either the issuer of
the certificate or its subject.
It is desirable to distinguish an Issuer or Subject of a certificate by one or more on-chain keys.
This, for example, can facilitate the ability to link off-chain actions authorized with a x509 certificate,
with an on-chain identity.

Currently, there is no standard way to embed a Cardano address, such as a stake address,
or a dRep address as distinguishing name within a [x509] certificate.

A URI is one of the possible names that can be associated with the Issuer or Subject of a certificate.
This URI can be referenced in the alternative name for both the Issuer and Subject of a certificate
by using the uniformResourceIdentifier in the general name.
[CIP-0013] does not define a method for stake or dRep addresses, etc., to be encoded in the URI scheme it defines.

Allowing these addresses to be easily encoded as URIs allows them to be 100% interoperable
with existing public key infrastructure and certificate creation tools.

## Specification

We extend [CIP-0013] with a single new authority for referencing Cardano addresses in [CIP-0019] format.

### Grammar & interpretation

We extend the grammar from [CIP-0013] with the new authority:

```
authorityref = (... | addr )

addr = "//addr/" cip19-addr
cip19-addr = *cip19-char
cip19-char = ALPHA / DIGIT / "_"
```

Effectively, any address string specified by [CIP-0019], [CIP-0105] or future extension to either
of these specifications can be embedded directly within the URI.

### Examples

#### CIP-19 Addresses

```uri
web+cardano://addr/addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3n0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgse35a3x
web+cardano://addr/addr_test1gz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer5pnz75xxcrdw5vky
web+cardano://addr/stake1uyehkck0lajq8gr28t9uxnuvgcqrc6070x3k9r8048z8y5gh6ffgw
web+cardano://addr/stake_test1uqehkck0lajq8gr28t9uxnuvgcqrc6070x3k9r8048z8y5gssrtvn
```

#### CIP-105 Addresses

```uri
web+cardano://addr/drep_vk17axh4sc9zwkpsft3tlgpjemfwc0u5mnld80r85zw7zdqcst6w54sdv4a4e
web+cardano://addr/drep15k6929drl7xt0spvudgcxndryn4kmlzpk4meed0xhqe25nle07s
web+cardano://addr/drep_script16pjhzfkm7rqntfezfkgu5p50t0mkntmdruwlp089zu8v29l95rg
web+cardano://addr/cc_cold_vk149up407pvp9p36lldlp4qckqqzn6vm7u5yerwy8d8rqalse3t04q7qsvwl
web+cardano://addr/cc_cold1lmaet9hdvu9d9jvh34u0un4ndw3yewaq5ch6fnwsctw02xxwylj
web+cardano://addr/cc_cold_script14ehj5f64f40xju0086fnunctulkh46mq7munm7upe4hpcwpcat
web+cardano://addr/cc_cold_script14ehj5f64f40xju0086fnunctulkh46mq7munm7upe4hpcwpcatv
web+cardano://addr/cc_hot_vk10y48lq72hypxraew74lwjjn9e2dscuwphckglh2nrrpkgweqk5hschnzv5
web+cardano://addr/cc_hot17mffcrm3vnfhvyxt7ea3y65e804jfgrk6pjn78aqd9vg7xpq8dv
web+cardano://addr/cc_hot_script16fayy2wf9myfvxmtl5e2suuqmnhy5zx80vxkezen7xqwskncf40
```

## Rationale: how does this CIP achieve its goals?

By extending [CIP-0013] to allow a [CIP-0019] encoded address to be simply embedded in the URI scheme,
we enable existing certificate creation tools and public key infrastructure to be used to easily
create certificates that reference Cardano addresses.

It is envisioned that this extension could have use cases beyond the one presented here.

## Path to Active

### Acceptance Criteria

* [ ] Community Feedback and Review Integrated.
* [ ] Demonstration of Cardano addresses being embedded in x509 certificates using existing tools.
* [ ] At least one project utilizing this standard.

### Implementation Plan

Project Catalyst intends to use this standard to facilitate linking of on-chain and off-chain identity
with x509 certificates.
This specification does not deal with the processes or proofs required, simply the URI scheme that is
required to embed a Cardano address in a x509 certificate.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-0013]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0013/
[CIP-0019]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0019/
[CIP-0105]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/
[x509]:https://datatracker.ietf.org/doc/html/rfc5280
