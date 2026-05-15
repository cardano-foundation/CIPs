CPS: ???? Title: Cardano Handle Namespace Governance Framework Status: Open Category: Tokens Authors:

    Slavcho King Andreevski support@getmyid.today Created: 2026-05-15 License: CC-BY-4.0

Abstract

This CPS (Cardano Problem Statement) documents the absence of an open, governed framework for human-readable handle namespaces on Cardano. It identifies the problems created by the current unregulated situation and proposes the requirements that a solution must satisfy — including the establishment of the .did (Decentralized Identifier) namespace under the GetMyID reference implementation as a starting point for community governance.
Problem

    No open standard exists for Cardano handle namespaces

Cardano currently has multiple handle/naming services (ADA Handle, CNS, GetMyID) operating independently with no shared governance framework, no open standards, and no defined hierarchy. Each platform independently decides which suffixes to use, which Policy IDs to mint under, and how resolution works — with no coordination mechanism between them.

    Well-funded incumbents can claim any namespace at any time

Nothing in the current Cardano ecosystem prevents an existing naming platform from minting handles with any suffix at any time. A new entrant who goes through the proper CIP process in good faith can have their proposed namespace claimed by an incumbent after submission — leaving their users with broken handles. This is not hypothetical: ADA Handle already mints handles ending in .id, directly conflicting with the initial GetMyID CIP proposal (PR #1187).

    No protection for users of non-incumbent platforms

If multiple platforms mint handles with the same suffix under different Policy IDs, wallet resolution becomes ambiguous. Wallets default to whichever Policy ID they integrated first — typically the incumbent. Users who purchased handles from a newer platform may find their handles do not resolve in popular wallets, through no fault of their own.

    ADA Handle operates as a de facto monopoly with no open standard

ADA Handle received significant Catalyst funding and achieved widespread wallet integration without contributing any open specification, CIP, or governance framework to the Cardano ecosystem. Other entities were "licensed" by ADA Handle without any public technical process or community input. This creates a closed, proprietary system that contradicts Cardano's core values of decentralization and openness.

    The CIP process provides no enforcement mechanism

As acknowledged by the CIP editors, participation in the CIP process is entirely voluntary. A CIP or CPS alone cannot prevent any entity from violating the intent of a standard. Without an on-chain governance mechanism or community coordination framework, any standard can be ignored by well-resourced incumbents.
Use Cases

UC-1: Developer testing environment A developer building a dApp that uses human-readable addresses needs to test handle resolution on testnet before deploying to mainnet. Currently no open testnet handle infrastructure exists — developers must either build their own or go straight to mainnet. GetMyID is the only platform currently running simultaneous testnet and mainnet handle resolution.

UC-2: Professional identity handles A professional wants a handle in firstname.lastname.did format as their permanent Cardano identity. Current solutions charge variable pricing based on character count, making common names expensive. An open framework would allow competing providers to offer flat pricing and different value propositions.

UC-3: Wallet resolution of handles from multiple providers A user holds john.smith.did from GetMyID. Another user holds john.smith.did from a future provider using a different Policy ID. Wallets need a deterministic rule to resolve the correct address — currently no such rule exists.

UC-4: New entrant protection An independent developer (without Catalyst funding or institutional backing) builds a handle platform, proposes a CIP, and invests in building a user base — only to have an incumbent claim the same namespace. A governance framework would prevent this scenario.
Goals

A solution to this problem MUST:

    Define an open registry of approved handle namespace providers on Cardano, governed by a transparent and accessible process.

    Establish clear resolution priority rules so wallets can deterministically resolve handles when multiple providers use the same suffix.

    Define the .did namespace as Cardano's implementation of the W3C Decentralized Identifier standard (https://www.w3.org/TR/did-core/), with GetMyID's Policy ID registered as the primary reference implementation (fde643f9cb864ca69f40eec06a7f97f720a14ff3561963b25da8cade) — as the first entity to propose and implement this standard on Cardano.

    Prevent namespace squatting by requiring that any entity wishing to issue handles in a registered namespace must participate in the governance framework rather than unilaterally claiming suffixes.

    Allow open participation — any technically qualified entity should be able to register as a handle provider under a governed namespace, not just a single licensed incumbent.

    Be enforceable on-chain — the registry of approved providers and their Policy IDs should be maintained on-chain so wallets can query it trustlessly without depending on any centralized API.

    Protect existing users — any governance transition must include protections for users who have already purchased handles, ensuring their handles continue to resolve correctly.

A solution SHOULD:

    Align with the W3C DID specification to position Cardano handles as part of a globally recognized identity standard.
    Support both testnet and mainnet environments simultaneously.
    Define a dispute resolution process for namespace conflicts.
    Involve the Cardano Foundation given their trademark interests in the "Cardano" and "Ada" brand names.

Open Questions

    Should the on-chain registry be managed by a smart contract, a governance action, or a committee?

    How should resolution priority be determined when multiple providers exist under the same namespace — registration order, stake weight, community vote?

    Should the Cardano Foundation serve as the ultimate arbiter of namespace disputes given their trademark position?

    Can ADA Handle's existing handles be migrated into an open framework retroactively, or must new namespaces be created from scratch?

References

    CIP PR #1187 — GetMyID Handle Standard
    W3C Decentralized Identifier Specification
    GetMyID Platform
    GetMyID Resolver API
    ADA Handle
    Cardano Name Service (CNS)

Copyright

This CPS is licensed under CC-BY-4.0.
