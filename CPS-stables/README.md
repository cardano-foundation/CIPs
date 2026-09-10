---
CPS: "?"
Title: Shared Standard for Regulated Stablecoins
Category: Tokens
Status: Open
Authors:
    - Alex Moser <alexander.moser@cardanofoundation.org>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/????
    - CIP-0113 | Programmable tokens: https://github.com/cardano-foundation/CIPs/pull/444
    - CPS-???? | Discoverability and machine-readable description of programmable token substandards (draft): https://github.com/Kammerlo/CIPs/blob/docs/cip-113-substandard-cps/CPS-%3F%3F%3F%3F/README.md
Created: 2026-08-20
License: CC-BY-4.0
---

## Abstract

[CIP-0113][CIP-0113] gives Cardano a framework for programmable tokens. It defines the shared parts (a registry, a common address that holds all programmable tokens, and the core validators) and leaves the actual token rules to pluggable *substandards*. Every issuer can bring their own.

That flexibility is expensive for everyone who has to move these tokens. A CIP-0113 transfer has to carry reference inputs and redeemers that are specific to the token's substandard, and often to the specific deployment. So every wallet, exchange, DEX, custodian and payment provider has to integrate every token individually. With a handful of tokens that's annoying. With dozens of stablecoins it doesn't work.

Stablecoins are the main reason regulated issuers are looking at programmable tokens, and what they need is largely the same from one issuer to the next. This CPS argues that they should share one substandard, so that supporting stablecoins becomes a one-time integration. For that to work, the standard has to cover what most issuers need, legally and operationally, while staying small enough that people actually implement it.

## Problem

### Every CIP-0113 token needs its own integration

Programmable tokens sit at a shared `programmable_logic_base` address, and ownership is carried by the stake credential. To spend them, a transaction includes:

- the protocol parameters UTxO and the token's registry node as reference inputs,
- a zero withdrawal from the core `transfer` validator,
- a zero withdrawal from the token's own `transfer_logic_script`, with a redeemer that script understands,
- whatever extra reference inputs that script needs to make its decision.

The first two are the same for every token. The transfer logic script can be looked up in the registry, so that's generic too. What goes into its redeemer, and which reference inputs it expects, are not.

The freeze-and-seize reference substandard needs covering nodes from the token's own denylist to prove the sender isn't on it, and which denylist to use is a per-deployment parameter. An allowlist token needs a membership proof instead. The BaFin securities substandard adds a users list and a global pause. A KYC-based token may need an attestation from an off-chain service. None of this can be derived from the token. You have to read the substandard's code and write a transaction builder for it.

This is a consequence of the eUTxO model. On Ethereum, USDC also has a blacklist, a pause and minter roles, but the contract checks its own storage, so to a wallet it's just an ERC-20 transfer. On Cardano a validator only sees what's in the transaction, so the wallet has to bring the compliance state along. The token's rules end up in every transaction that touches it.

The integration also doesn't stay fixed. Transfer logic is resolved from the registry node at spend time and the issuer can re-point it, so an integration that works today can break after an upgrade.

The result is one integration per token per integrator. Wallets and exchanges won't do that work for a token without volume, and a stablecoin that most wallets and exchanges can't handle won't get volume.

### Why now

CIP-0113 is at Last Check, the core implementation has been audited, and issuers are building on it with mainnet as the target. If there's no shared stablecoin substandard, each issuer will write their own, and a standard will have to be retrofitted across incompatible deployments later, if it happens at all.

This CPS describes CIP-0113 as implemented in the [Cardano Foundation reference implementation][CIP113-IMPL], which differs from the PR #444 text in places.

### Why describing each substandard isn't enough

[CPS-????][CPS-SUBSTD] tackles the general version of this: a machine-readable way to describe any substandard, so generic tooling can build transactions for it. We need that, and the two CPSs complement each other. But a description alone doesn't remove the work. Each substandard still brings its own proofs, its own data sources and its own trust assumptions that an integrator has to support and review, and its own set of issuer powers that a wallet or DEX has to explain to its users. A description format tells you how to talk to a token. A shared standard means that for stablecoins there's only one kind of token to talk to.

### Why one standard is realistic

Regulated stablecoin issuers need the same things. Under MiCAR in the EU, the GENIUS Act in the US and similar regimes elsewhere, issuers have to control supply, freeze and seize funds when lawfully ordered, block sanctioned holders, and honour redemption. The large stablecoins on other chains all ship roughly the same set of controls: mint and burn roles, a blacklist, a pause, and some form of seizure. The differences between issuers are mostly configuration (denylist or allowlist, which roles exist, who holds which keys), not transaction shape.

The existing substandards each cover part of this, but none of them is a stablecoin standard:

| Substandard | Has | Missing |
|---|---|---|
| `freeze-and-seize` (Cardano Foundation) | Denylist, freeze, seize | Supply control, role separation, redemption, issuer info |
| BaFin (FluidTokens) | Detailed role model, users list, pause, mint cap | Built for securities (ISIN, nominal amount); its global pause also blocks redemption |
| KYC (Cardano Foundation) | Allowlist based on off-chain verification | Everything on the issuer side |

The hard part is getting the scope right. A standard that misses a hard legal requirement won't be adopted, because issuers will fork it. A standard that tries to cover every regulatory detail won't be implemented. The goal is the smallest thing most issuers can use as-is.

## Use Cases

- A wallet adds support for the stablecoin standard once, and can then show, send and receive any compliant stablecoin, including telling the user when a balance is frozen.
- An exchange or custodian lists a new stablecoin with configuration instead of new engineering work.
- A DEX or lending protocol checks what an issuer can do to tokens sitting in its pools (freeze, seize) before listing, without reading validator code.
- An issuer launches with a substandard that's already audited and already supported by wallets, and only has to take care of its own keys and configuration.
- An indexer, auditor or regulator reads supply, mints, burns, freezes and seizures the same way for every stablecoin.

## Goals

1. **One transaction shape.** A transfer of any compliant stablecoin uses the same kinds of reference inputs, withdrawals and redeemers, and a wallet can work out everything it needs from the policy ID and chain data.
2. **Cover what most issuers need,** so they don't have to fork it.
3. **Keep it small.** Only things that must be enforced on-chain, or that affect how transactions are built, go in the standard. Everything else stays off-chain.
4. **Reuse what exists.** Build on the CIP-0113 core and on `freeze-and-seize` instead of starting over.
5. **Be describable** by whatever format comes out of [CPS-????][CPS-SUBSTD].

### Requirements

A solution should cover at least the following. Most of these come from MiCAR. That's not meant to make this an EU standard. MiCAR is simply the most detailed stablecoin rulebook being applied today, so it makes a good checklist, and where we know the GENIUS Act asks for the same thing we say so. This list is the part we most want issuers to check, especially outside the EU: what's missing, what isn't needed, and where your rules differ. "Today" shows what already exists in CIP-0113 or its current substandards.

| | Requirement | Why | Today |
|---|---|---|---|
| 1 | Only the issuer can mint and burn, up to a supply cap | Supply has to match reserves | Core supports issuer minting; only BaFin has a cap |
| 2 | The issuer can freeze a holder, and undo it | Sanctions, law enforcement | `freeze-and-seize` |
| 3 | The issuer can seize or burn a frozen balance | Court orders; the GENIUS Act requires the technical ability to seize, freeze, burn or block transfers on a lawful order (Sec. 4(a)(6)) | `freeze-and-seize` |
| 4 | Every freeze and seizure carries a standard reason code, without personal data | Wallets can show why a balance is frozen; audit trail | Nothing |
| 5 | The issuer can pause all transfers | Incidents and exploits | BaFin |
| 6 | A holder who isn't frozen can always redeem, even while transfers are paused | MiCAR Arts. 39 and 49; GENIUS Act Sec. 4(a)(1)(B) (timely redemption) | Nothing; BaFin's pause blocks redemption |
| 7 | Denylist by default, allowlist as an option, with the same transaction shape | Open retail coins vs. permissioned and institutional ones | Separately: `freeze-and-seize` (deny), KYC (allow) |
| 8 | Separate keys for minting, freeze/seize and admin, multisig support, and key rotation without migrating the token | Regulators expect separation of duties, and a lost key shouldn't mean a lost token | BaFin has roles; the core's single `minting_logic_script` limits this |
| 9 | Basic token info on-chain: name, currency, decimals, issuer, and a link and hash to the white paper or terms | Wallets and exchanges need to show it; MiCAR requires a white paper | Nothing for stablecoins; BaFin's is for securities |
| 10 | No personal data on-chain | GDPR and equivalents | Open, see question 3 |
| 11 | Changes to the token's rules are visible to integrators, ideally before they take effect | Integrations shouldn't break silently | Core: registry updates apply immediately |
| 12 | The issuer can burn all outstanding tokens against payout when winding down | MiCAR Art. 47 redemption plan; insolvency rules elsewhere | Nothing specified |

**Non-goals.** Changing the CIP-0113 core, though a solution can point out changes it needs (see Open Questions). Legal advice. Algorithmic stablecoins. Moving off-chain obligations such as reserve management, audits and AML programs on-chain. A general format for describing substandards, which is [CPS-????][CPS-SUBSTD].

## Open Questions

1. **One substandard or a small family?** Denylists and allowlists need different proofs (non-membership vs. membership). Can they share one transaction shape, or do we need two variants? What else can be configuration rather than code?
2. **How is redemption protected?** While transfers are paused, how does the validator let a redemption through without also letting through a transfer that only looks like one? And when does a freeze override a holder's right to redeem?
3. **Denylists and personal data.** A list of stake credentials is arguably personal data, and chain history can't be deleted. Is that acceptable, or does the list have to live off-chain with only a commitment on-chain?
4. **Tokens held by scripts.** A script stake credential can be a DEX pool or a lending protocol. Should the issuer be able to freeze or seize those, and how does a protocol find out before it lists the token?
5. **Upgrades.** The issuer can re-point transfer logic in the registry, and the CIP-0113 core has an upgrade credential that can replace the core validators for all tokens at once. How does the standard handle versioning, and how can an integrator tell that a token is still running standard logic?
6. **Does this need CIP-0113 changes?** For example, `minting_logic_script` controls minting, registration and registry updates with a single credential, which makes requirement 8 hard. Third-party actions like seizure work on one policy per transaction. Should these be fixed in PR #444 before it's merged, or in a follow-up?
7. **Cost at payment volumes.** Every transfer carries denylist proofs and extra withdrawals, and denylist nodes can become contention points. Is that acceptable for a payment token?
8. **How much metadata?** What's the minimum a wallet needs? Do reserve attestations and white paper versions belong on-chain, or behind a link?

## References

- [CIP-0113][CIP-0113]: Programmable tokens
- [CPS-0003][CPS-0003]: Smart Tokens
- [CPS-????][CPS-SUBSTD]: Discoverability and machine-readable description of programmable token substandards (draft)
- CIP-0113 reference implementation: https://github.com/cardano-foundation/cip113-programmable-tokens
- Reference substandards: https://github.com/cardano-foundation/cip113-programmable-tokens-platform
- BaFin securities substandard: https://github.com/FluidTokens/fn-bafin-cardano-sc
- Regulation (EU) 2023/1114 (MiCAR)
- GENIUS Act, Public Law 119-27 (2025): https://www.govinfo.gov/content/pkg/PLAW-119publ27/html/PLAW-119publ27.htm

Regulatory references are here to show which obligations a solution has to support. They are not legal advice.

## Acknowledgements

This builds on the CIP-0113 authors' work, the Cardano Foundation's reference substandards and documentation, and the BaFin substandard by Matteo Coppola and the Finest team.

[CIP-0113]: https://github.com/cardano-foundation/CIPs/pull/444
[CPS-0003]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0003
[CPS-SUBSTD]: https://github.com/Kammerlo/CIPs/blob/docs/cip-113-substandard-cps/CPS-%3F%3F%3F%3F/README.md
[CIP113-IMPL]: https://github.com/cardano-foundation/cip113-programmable-tokens

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
