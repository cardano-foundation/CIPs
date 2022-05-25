# Cardano Improvement Proposals (CIPs)

Cardano Improvement Proposals (CIPs) describe standards, processes; or provide general guidelines or information to the Cardano Community. It is a formal, technical communication process that exists off-chain. CIPs do **not** represent a commitment of any form towards existing projects. Rather, they are a collection of sensible and sound solutions to common problems within the Cardano ecosystem. CIPs evolves around different statuses, driven by one or more authors:

| Status   | Description                                                                                                                    |
| ---      | ---                                                                                                                            |
| Draft    | The idea has been formally accepted in the repository and is being worked on by its authors.                                   |
| Proposed | A working implementation exists, as well as a clear plan highlighting what is required for this CIP to transition to "Active". |
| Active   | The proposal is deemed to have met all the appropriate criteria to be considered Active.                                       |
| On Hold  | The CIP author is not currently working on this effort.                                                                        |
| Obsolete | The CIP was either retired or made obsolete by a newer CIP.                                                                    |
| Rejected | There is some issue with the CIP that makes it not acceptable at this point.                                                   |

It is therefore quite common for proposals and implementations to be worked on concomitantly. Even more so that a working implementation (when relevant) is a mandatory condition for reaching an `Active` status. 

The entire process is described in greater detail in [CIP1 - "CIP Process"](./CIP-0001).

### Reviewed Proposals (as of 2022-04-07)

| # | Title | Status | 
| --- | --- | --- |
| 1 | [CIP process](./CIP-0001/) | Active |
| 2 | [Coin Selection Algorithms for Cardano](./CIP-0002/) | Active |
| 3 | [Wallet key generation](./CIP-0003/) | Active |
| 4 | [Wallet Checksums](./CIP-0004/) | Draft |
| 5 | [Common Bech32 Prefixes](./CIP-0005/) | Draft |
| 6 | [Stake Pool Extended Metadata](./CIP-0006/) | Draft |
| 7 | [Curve Pledge Benefit](./CIP-0007/) | Proposed |
| 8 | [Message Signing](./CIP-0008/) | Draft |
| 9 | [Protocol Parameters](./CIP-0009/) | Active |
| 10 | [Transaction Metadata Label Registry](./CIP-0010/) | Active |
| 11 | [Staking key chain for HD wallets](./CIP-0011/) | Active |
| 12 | [On-chain stake pool operator to delegates communication](./CIP-0012/) | Draft |
| 13 | [Cardano URI Scheme](./CIP-0013/) | Draft |
| 14 | [User-Facing Asset Fingerprint](./CIP-0014/) | Active |
| 15 | [Catalyst Registration Transaction Metadata Format](./CIP-0015/) | Active |
| 16 | [Cryptographic Key Serialisation Formats](./CIP-0016/) | Active |
| 17 | [Cardano Delegation Portfolio](./CIP-0017/) | Active |
| 18 | [Multi-Stake-Keys Wallets](./CIP-0018/) | Draft |
| 19 | [Cardano Addresses](./CIP-0019/) | Active |
| 20 | [Transaction message/comment metadata](./CIP-0020/) | Active |
| 21 | [Transaction requirements for interoperability with hardware wallets](./CIP-0021/) | Draft |
| 22 | [Pool operator verification](./CIP-0022/) | Active |
| 23 | [Fair Min Fees](./CIP-0023/) | Draft |
| 24 | [Non-Centralizing Rankings](./CIP-0024/) | Draft |
| 25 | [NFT Metadata Standard](./CIP-0025/) | Active |
| 26 | [Cardano Off-Chain Metadata](./CIP-0026/) | Draft |
| 27 | [CNFT Community Royalties Standard](./CIP-0027/) | Draft |
| 28 | [Protocol Parameters (Alonzo)](./CIP-0028/) | Active |
| 29 | [Phase-1 Monetary Scripts Serialization Formats](./CIP-0029/) | Active |
| 30 | [Cardano dApp-Wallet Web Bridge](./CIP-0030/) | Draft |
| 31 | [Reference Inputs](./CIP-0031/) | Draft |
| 32 | [Inline Datums](./CIP-0032/) | Draft |
| 33 | [Reference Scripts](./CIP-0033/) | Draft |
| 34 | [Chain ID Registry](./CIP-0034/) | Draft |
| 35 | [Plutus Core Evolution](./CIP-0035) | Active |
| 36 | [Catalyst/Voltaire Registration Transaction Metadata Format](./CIP-0036) | Proposed | 
| 1852 | [HD (Hierarchy for Deterministic) Wallets for Cardano](./CIP-1852/) | Active |
| 1853 | [HD (Hierarchy for Deterministic) Stake Pool Cold Keys for Cardano](./CIP-1853/) | Active |
| 1854 | [Multi-signatures HD Wallets](./CIP-1854/) | Draft |
| 1855 | [Forging policy keys for HD Wallets](./CIP-1855/) | Active |

> 💡 For more details about Statuses, refer to [CIP1](./CIP-0001).

### Proposals Under Review (as of 2022-03-17)

Below are listed tentative CIPs still under discussion with the community. Discussions and progress will be reviewed by CIP editors in [bi-weekly meetings](https://www.crowdcast.io/cips-biweekly). Note that they are listed below for easing navigation and also, tentatively allocating numbers to avoid clashes later on.

| # | Title | 
| --- | --- | 
| 37? | [Dynamic Saturation Based on Pledge](https://github.com/cardano-foundation/CIPs/pull/163) |
| 38? | [On-Chain Token Metadata Standard](https://github.com/cardano-foundation/CIPs/pull/137) | 
| 39? | [Smart Contract Software Licenses](https://github.com/cardano-foundation/CIPs/pull/185) |
| 40? | [Collateral Output](https://github.com/cardano-foundation/CIPs/pull/216) | 
| 41? | [Collateral Rewards](https://github.com/cardano-foundation/CIPs/pull/217) | 
| 42? | [New Plutus Builtin: serialiseBuiltinData](https://github.com/cardano-foundation/CIPs/pull/218) |
| 43? | ~~[New Plutus Builtin: dataHash](https://github.com/cardano-foundation/CIPs/pull/222)~~ |
| 44? | [Additional Factors For NFT Market Verification](https://github.com/cardano-foundation/CIPs/pull/226) | 
| 45? | [Decentralization: Using Pledge as a Bidding Param](https://github.com/cardano-foundation/CIPs/pull/229) |
| 46? | [Prepay Min Fixed Fee](https://github.com/cardano-foundation/CIPs/pull/190) | 
| 47? | [Deep-Link to Desktop Wallet App](https://github.com/cardano-foundation/CIPs/pull/234) | 
| 48? | [Extended NFT metadata](https://github.com/cardano-foundation/CIPs/pull/249) |
| 49? | [ECDSA and Schnorr signatures in Plutus Core](https://github.com/cardano-foundation/CIPs/pull/250) | 
| 50? | [Liesenfelt Shelleys Voltaire Decentralization Update](https://github.com/cardano-foundation/CIPs/pull/242) |
| 51? | [Preserve Submitter's Ordering of Transaction Inputs](https://github.com/cardano-foundation/CIPs/pull/231) | 
| 52? | [Cardano Audit Best Practice Guidelines](https://github.com/cardano-foundation/CIPs/pull/252) | 
| 53? | [Light Wallet Backend Connection](https://github.com/cardano-foundation/CIPs/pull/254) | 
| 381? | [Plutus Support For Pairings Over Curve Bls12-381](https://github.com/cardano-foundation/CIPs/pull/220) |
| 989? | [ISPO KYC_CDD](https://github.com/cardano-foundation/CIPs/pull/241) |

### CIP creation process as a Sequence Diagram

  “_Alice has a Cardano idea she'd like to build more formally…_”

![Diagram: Mary interacting with community and editors for a Cardano Proposal](https://raw.githubusercontent.com/cardano-foundation/CIPs/master/BiweeklyMeetings/sequence_diagram.png "sequence_diagram.png")

Extend or discuss ‘ideas’ in the [Developer Forums](https://forum.cardano.org/c/developers/cips/122), Cardano’s Official [Developer Telegram Group](https://t.me/CardanoDevelopersOfficial) or in `#developers` in Cardano Ambassadors Slack.
CIP Editors meetings are [public](https://www.crowdcast.io/cips-biweekly), [recorded](https://www.crowdcast.io/cips-biweekly) and [summarized](https://github.com/cardano-foundation/CIPs/tree/master/BiweeklyMeetings): do join and participate for discussions/PRs of significances to you.

> 🛈 To facilitate browsing and information sharing for non-Github users, an auto-generated site is also provided at [cips.cardano.org](https://cips.cardano.org/).

### Current Editors

- Matthias Benkort (@KtorZ)
- _(Duncan Coutts (@dcoutts))_
- Sebastien Guillemot (@SebastienGllmt)
- Frederic Johnson (@crptmppt)
- Robert Phair (@rphair)
