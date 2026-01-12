---
CPS: 8
Title: Domain Name Resolution
Status: Open
Category: Tools
Authors:
  - Hinson Wong <hinson@cns.space>
Proposed Solutions: []
Discussions: 
  - Cardano Name Service CIPs fork: https://github.com/cns-space/CIPs
  - Original pull request: https://github.com/cardano-foundation/CIPs/pull/605
Created: 2023-10-14
License: CC-BY-4.0
---

## Abstract

As different domain projects emerge, the same prefix or suffix may be employed by different projects, leading to potential naming conflicts. One of the key features of blockchain domain service is to resolve domain information. Conflicting names would lead to the integration ambiguity in resolving. To address this, a community-aligned mechanism should be in place to enable users to select their preferred project when resolving names. This ensures a seamless user experience.

The CPS is written up accordingly to open for discussion on potential approaches to the above issue.

## Problem

As the ecosystem emerges, more and more domain service projects entering Cardano. Currently noticeably there are 3 domain projects:

1. `ADA Handle`
2. `adadomains`
3. `Cardano Name Service (CNS)`

Both `adadomains` and `CNS` has chosen `.ada` as domain suffix. When proceeding with resolving integration, one common issue faced is the ambiguity in resolving approach, which could lead to user confusion at the minimal impact. On some specific information resolving, it might even cause serious loss of fund when sending tokens with monetary value to unexpected recipients.

## Use cases

Let's illustrate the potential issues with a hypothetical example in wallet address resolving area.

1. Assuming `Yoroi` wallet is going to integrate with `CNS` and `NuFi` wallet is going to integrate `adadomains`. (And both `CNS` and `adadomains` opt for `.ada` as the suffix)
2. Both protocol has their separate domain NFT called `hinson.ada` and there are separate holder of `hinson.ada` for 2 domain projects.
3. When the `hinson.ada` `CNS` holder requesting fund from others, there would be potential loss of fund when the user sending fund to `hinson.ada` through `NuFi` since the fund would be sent to `adadomains` domain holder instead.

This is not a desirable outcome as funds are mistakenly sending to the incorrect recipient without users noticing it.

## Goals

The goal of this `CPS` is to invite community discussion on how to best approach this potential problem when the ecosystem evolves and having more and more domain projects entering the space.

### Pro-decentralization Solution

The solution should embrace the decentralization property of a blockchain where it welcomes multiple domain name services exist in the market without user experience competition at the infrastructure level. The solution should not be made customized for any specific domain service providers, ideally shifting domain service projects' focus to enhancing features rather than competing with each other by oligarchic alliance.

### Clear User Experience Flow

It ensures a user-friendly experience and allows users to make informed decisions in case of naming conflicts. It accommodates multiple projects with the same suffix while avoiding disputes and confusion, fostering the integration process of wallet and domain service.

## Open Questions

### On Domain Service Providers

1. Should there be any standard in domain service provider side to store user information?
2. Should there be standardization in domain metadata to assist with consistent integration?
3. Apart from address resolving, should there be any standardized way to resolve domain information?
4. Is there any threshold or minimum requirement on domain projects in order to be considered as applicable to apply the potential solution?
5. Following `question 4 on integration partners`, would it be the domain service providers' responsibility to ensure the integration is in compliance with the potential solution?

### On Integration Partners (e.g. Wallets)

1. Should the potential solution just provide a high level guideline on integration user experience flow? Or a detailed guideline would be preferred?
2. How to inform the community on whether which projects participated in the solution `CIP` so to alleviate users' concern when proceeding with integration partners? For example user could be confirmed that their fund would not be sent to unexpected recipients when using certain wallets participating in the `CIP`.
3. Should there be any kind of community verification to include integration partners on to the participation list?
4. If the potential solution `CIP` only serves as a soft guideline, how could we make it useful to community when projects integrating with domain services do bother to spend time and effort into this alignment?

## Copyright

This CPS is licensed under [CC-BY-4.0].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
