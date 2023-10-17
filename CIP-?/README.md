---
CPS: ?
Title: Domain Address Resolving Standard
Status: Proposed
Category: Wallets
Authors:
  - Hinson Wong <hinson@cns.space>
Proposed Solution: []
Discussions: https://github.com/cns-space/CIPs
Created: 2023-10-14
License: CC-BY-4.0
---

## Abstract

As the ecosystem emerges, more and more domain service projects entering Cardano. Currently noticeably there are 3 domain projects:

1. `ADA Handle`
2. `adadomains`
3. `Cardano Name Service`

Both `adadomains` and `Cardano Name Service` has chosen `.ada` as domain suffix. When proceeding with wallet integration on address resolving, one common issue faced is the ambiguity in resolving approach, which could lead to potentially serious loss of fund in sending fund to undesired recipients.

The CPS is written up accordingly to suggest possible solution and open for discussion.

## Problem

As different domain projects emerge, the same prefix or suffix may be employed by different projects, leading to potential naming conflicts. One of the key features of blockchain domain service is to resolve a holder's address. Conflicting names would lead to the wallet's integration ambiguity in resolving. To address this, a community-aligned mechanism should be in place to enable users to select their preferred project when resolving names. This ensures a seamless user experience.

## Use cases

1.  **Naming Conflict Detection:**

    - When a user enters a domain name (e.g., `hinson.ada`) with the same prefix or suffix, the wallet should detect the potential conflict. Possibly by attempt to resolve all potential project's corresponding addresses.
      > Specific example illustration
      >
      > - A user enter `hinson.ada` in any wallet's `recipient field`
      > - Wallet try to resolve all domain projects' corresponding address using suffix `.ada`
      > - Let's say there are 2 domain services (`Domain Service A` and `Domain Service B`) opt in using `.ada` as suffix, wallet would try to resolve address on both services.
    - When a user enters a domain name (e.g., `hinson.ada`) with the same prefix or suffix, the wallet should detect the potential conflict by attempting to resolve all potential project's corresponding addresses.
      > Specific example illustration
      >
      > - `Resolve Case 1`: `Domain Service A` resolves `addr_a` and `Domain Service B` resolves `addr_b`, it is a conflict in resolution.
      > - `Resolve Case 2`: `Domain Service A` resolves `addr_a` and `Domain Service B` resolves nothing, there is no conflict.
      > - `Resolve Case 3`: `Domain Service A` resolves nothing and `Domain Service B` resolves `addr_a`, there is no conflict.
      > - `Resolve Case 4`: `Domain Service A` and `Domain Service B` both resolves `addr_a`, there is no conflict.
      > - `Resolve Case 5`: `Domain Service A` and `Domain Service B` both resolves nothing, there is no conflict. Since no address is resolved, transaction would not proceed.

2.  **User Prompt:**

    - If there is only one corresponding address resolved, the wallet could proceed with the only address for proceeding with the user transaction.
      > Specific example illustration
      >
      > - `Proceed Case 1`: For `Resolve Case 1`, `Resolve Case 3` and `Resolve Case 4`, there is only 1 address resolved. So an only address is identified from resolution and thus the transaction could proceed with `addr_a`.
    - If more than one corresponding address is detected, the wallet should display a prompt to the user, explaining the conflict, and providing options for resolution.
      > Specific example illustration
      >
      > - `Proceed Case 2`: For `Resolve Case 2`, more than 1 address is identified. Wallet should display options of either choosing to resolve using `Domain Service A` or `Domain Service B`
      >   - If user chooses `Domain Service A`, `addr_a` is used for transaction
      >   - If user chooses `Domain Service B`, `addr_b` is used for transaction

3.  **Resolution Options:**

    - The prompt should offer the user the following options:

      - Resolve with Project A
      - Resolve with Project B
      - etc...
      - Cancel
        >     Detail UX implementation to be decided by the wallet as long as users are not confused with their choice, so only showing the project name is the minimal information needed, e.g. one for Cardano Name Service and another for adadomains
        >
        > Specific example illustration
        >
        > - For `Resolve Case 2`, more than 1 address is identified. Wallet should display options of either choosing to resolve using `Domain Service A` or `Domain Service B`. There is also an option to `Cancel`.

4.  **User Selection:**

    - The user selects one of the options presented in the prompt. If they choose to resolve with Project A, the Project A's resolver is used; if they choose the other project, the respective resolver is used.
      > Specific example illustration
      >
      > - If user chooses `Domain Service A`, `addr_a` is used for transaction
      > - If user chooses `Domain Service B`, `addr_b` is used for transaction
      > - If user chooses `Cancel`, transaction is stopped and would not proceed.

5.  **Default Project:**

    - Users may have the option to set a default project for names with a colliding suffix in their wallet settings. This default project will be used for resolution unless changed by the user during the resolution prompt.
      > Specific example illustration
      >
      > - In the wallet's setting, there would be a page showing all conflicting domain suffix or prefix
      > - Assumed apart from `Domain Service A` and `Domain Service B` conflict in choosing `.ada` as suffix, there are also `Domain Service C` and `Domain Service D` conflict choosing `$` as prefix, the list would show
      >   - Setting default `.ada` prefix domain service
      >     - `Domain Service A`
      >     - `Domain Service B`
      >   - Setting default `$` suffix domain service
      >     - `Domain Service C`
      >     - `Domain Service D`
      > - For example, when user selected `Domain Service A` as default for `.ada`, even for `Resolve Case 2` as illustrated above, it would go with `Proceed Case 1` (to directly proceed with transaction) but not `Proceed Case 2` (to show user prompt).
    - Without user specification, there should always be an option prompting to user in case of domain name conflict.

## Goals

This proposal embraces the decentralization property of a blockchain where it welcomes multiple domain name service that exists in the market without user experience competition at the infrastructure level. It ensures a user-friendly experience and allows users to make informed decisions in case of naming conflicts. It accommodates multiple projects with the same suffix in wallets while avoiding disputes and confusion, fostering the integration process of wallet and domain service.

This approach could be applied in resolving other information as well in case of conflict. When there is no other specific CIP covering the particular domain information resolving mechanism, the similar approach with this CIP would by default covering the particular scope.

- Every participating Cardano domain service provider provides an address resolver SDK.
- Every participating Cardano domain service provider provides either a desired prefix or suffix.
- Wallet providers to execute and integrate with resolving address, domain service project to provide assistance.

| Domain Service Project     | Prefix | Suffix | Link to Resolver SDK Repo                     |
| -------------------------- | ------ | ------ | --------------------------------------------- |
| Cardano Name Service (CNS) | N/A    | `.ada` | https://github.com/cns-space/cns-resolver-sdk |
|                            |        |        |                                               |
|                            |        |        |                                               |

## Open Questions

## Copyright

This CIP is licensed under [CC-BY-4.0].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
