---
CIP: ?
Title: Domain Address Resolving Standard
Status: Proposed
Category: Wallets
Authors:
  - Hinson Wong <hinson@cns.space>
Implementors: []
Discussions: https://github.com/cns-space/CIPs
Created: 2023-10-14
License: CC-BY-4.0
---

## Abstract

This proposal suggests a method for Cardano wallets to account for naming conflicts that arise when multiple projects use the same prefix or suffix, such as `$` and `.ada,` for domain names. The proposed solution allows users to choose their desired project when resolving names with colliding prefixes or suffixes.

## Motivation: why is this CIP necessary?

As different domain projects emerge, the same prefix or suffix may be employed by different projects, leading to potential naming conflicts. One of the key features of blockchain domain service is to resolve a holder's address. Conflicting names would lead to the wallet's integration ambiguity in resolving. To address this, a community-aligned mechanism should be in place to enable users to select their preferred project when resolving names. This ensures a seamless user experience.

## Specification

1. **Naming Conflict Detection:**

   - When a user enters a domain name (e.g., `hinson.ada`) with the same prefix or suffix, the wallet should detect the potential conflict. Possibly by attempt to resolve all potential project's corresponding addresses.
   - When a user enters a domain name (e.g., `hinson.ada`) with the same prefix or suffix, the wallet should detect the potential conflict by attempting to resolve all potential project's corresponding addresses.

2. **User Prompt:**

   - If there is only one corresponding address resolved, the wallet could proceed with the only address for proceeding with the user transaction.
   - If more than one corresponding address is detected, the wallet should display a prompt to the user, explaining the conflict, and providing options for resolution.

3. **Resolution Options:**

   - The prompt should offer the user the following options:

     - Resolve with Project A
     - Resolve with Project B
     - etc...
     - Cancel

     > Detail UX implementation to be decided by the wallet as long as users are not confused with their choice, so only showing the project name is the minimal information needed, e.g. one for Cardano Name Service and another for adadomain

4. **User Selection:**

   - The user selects one of the options presented in the prompt. If they choose to resolve with Project A, the Project A's resolver is used; if they choose the other project, the respective resolver is used.

5. **Default Project:**

   - Users may have the option to set a default project for names with a colliding suffix in their wallet settings. This default project will be used for resolution unless changed by the user during the resolution prompt.
   - Without user specification, there should always be an option prompting to user in case of domain name conflict.

## Rationale: how does this CIP achieve its goals?

This proposal embraces the decentralization property of a blockchain where it welcomes multiple domain name service that exists in the market without user experience competition at the infrastructure level. It ensures a user-friendly experience and allows users to make informed decisions in case of naming conflicts. It accommodates multiple projects with the same suffix in wallets while avoiding disputes and confusion, fostering the integration process of wallet and domain service.

This approach could be applied in resolving other information as well in case of conflict. When there is no other specific CIP covering the particular domain information resolving mechanism, the similar approach with this CIP would by default covering the particular scope.

## Path to Active

### Acceptance Criteria

- At least 3 of wallets listed below agree with the approach

  - [ ] Begin <https://begin.is/>
  - [ ] Eternl <https://eternl.io/>
  - [ ] Flint <https://flint-wallet.com/>
  - [ ] GeroWallet <https://www.gerowallet.io/>
  - [ ] Lace <https://www.lace.io/>
  - [ ] Nami <https://namiwallet.io/>
  - [ ] NuFi <https://nu.fi/>
  - [ ] RayWallet <https://raywallet.io/>
  - [ ] Yoroi <https://yoroi-wallet.com/>

  > Initial list of wallet adapted from CIP30, other wallet providers could to request to add to the list.

### Implementation Plan

- Every participating Cardano domain service provider provides an address resolver SDK.
- Every participating Cardano domain service provider provides either a desired prefix or suffix.
- Wallet providers to execute and integrate with resolving address, domain service project to provide assistance.

| Domain Service Project     | Prefix | Suffix | Link to Resolver SDK Repo                     |
| -------------------------- | ------ | ------ | --------------------------------------------- |
| Cardano Name Service (CNS) | N/A    | `.ada` | https://github.com/cns-space/cns-resolver-sdk |
|                            |        |        |                                               |
|                            |        |        |                                               |

## Copyright

This CIP is licensed under [CC-BY-4.0].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
