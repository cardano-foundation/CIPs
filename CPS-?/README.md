---
CPS: ?
Title: Cardano Multi Asset Treasury (CMAT)
Category: Ledger
Status: Open
Authors: 
  - Hinson Wong - SIDAN Lab <hinson.wong@deltadefi.io> 
  - Felix Weber - Mesh <felix@meshjs.dev> 
  - Nicolas Cerny - Cardano Foundation <nicolas.cerny@cardanofoundation.org>
Proposed Solutions: []
Discussions:
  - https://forum.cardano.org/t/cardano-multi-asset-treasury-cmat/149984
  - https://github.com/cardano-foundation/CIPs/pull/1061
  - https://github.com/cardano-foundation/CIPs/pull/1103
Created: 2025-10-26
License: CC-BY-4.0
---

## Abstract

Cardano’s on-chain treasury currently holds funds in ada (lovelace) only. However, there is growing interest in allowing the treasury to support multiple assets. This CPS serves as an initial documents to outline the motivation of Cardano multi asset treasury.

## Problem

The Cardano treasury's exclusive holding of ada (lovelace) creates financial instability for both the treasury and funding proposers. Proposers must denominate their requests in ada, yet their real-world costs are in fiat. This forces them to gamble on a fixed exchange rate in their budgets. Consequently, proposers bear all the financial risk: a drop in ada's price can render their project underfunded and unviable, while a sharp price increase results in an inefficient over-allocation of community funds. This volatility makes sustainable, long-term budgeting impossible for proposers and complicates the treasury's own capital management, creating a high-risk environment that can deter high-quality, long-term ecosystem development.

## Use cases

Enabling the Cardano treasury to hold Cardano Native Tokens (CNTs) (including stablecoins) unlocks a range of possibilities beyond just ada funding:

- **Stable-Value Funding**: Treasury Withdrawals can be denominated in stablecoins, providing reliable budgets not subject to ada’s volatility. For instance, critical infrastructure projects could receive annual payments in a USD-pegged stablecoin, ensuring stable maintenance funding for key Cardano projects. This is more predictable than equivalent ada payouts whose fiat value can fluctuate dramatically.

- **New Funding Models**: Community funding can go beyond one-way payouts. Ideas like token-based loans, collateralized loans or investments from the treasury become more feasible when the treasury can hold CNTs. For instance, the treasury could offer a loan in stablecoin to a project, which repays later in that same stablecoin – avoiding any need to convert currencies. The treasury could even participate in token raises by receiving a project’s tokens in exchange for funding, aligning incentives between the ecosystem and for-profit endeavors.

- **Diverse Treasury Holdings**: The community gains the ability to strategically manage treasury holdings by holding a mix of assets, not just ada. For example, by leveraging the on-chain governance model, the community could decide to keep a portion of the treasury in stablecoins as a hedge against market downturns, or hold partner chain tokens that have strategic value. (One community suggestion is that only a certain percentage of the ada treasury should be converted into other assets like stablecoins – not all of it – to balance growth vs. stability, for example the NCL budgets which can be determined in stablecoins.) Holding RWAs (Real World Assets) furthermore could path the way of Cardano manifesting physical holdings (real-estate), moving towards a full fletched network-nation not only in the digital/virtual but also in the physical space.

- **Token Donations and Deposits**: Anyone could donate or return funds in any CNT. Community members or partner organizations might send their native tokens (including stablecoins) to the treasury as contributions. This expands the treasury’s resource pool beyond ada – e.g. a DeFi project that raised funds in a stablecoin could return unused funds directly in that stablecoin to the treasury, rather than converting back to ada.

- **Cross-Chain Collaboration**: A multi-asset treasury can strengthen partnerships with Cardano’s partner chains. These networks could contribute their native tokens to Cardano’s treasury as part of collaboration agreements. This creates financial bridges; for instance, if an IOU token from a sidechain or a governance token from a partner blockchain, which are represented as CNTs on Cardano, is contributed to Cardano’s treasury, it effectively links the ecosystems.

Notably, multi-asset treasuries are not without precedent. Other blockchain ecosystems with on-chain governance have already implemented similar features. Polkadot, for example, has a treasury that holds DOT (its native coin) plus assets like USDC, USDT, and even tokens from its parachains. Cardano, coming later to on-chain governance, can leverage these lessons as a second mover – implementing a multi-asset treasury in a careful, informed way.

## Goals

The good solution to this CPS consists of 3 components:

1. Well articulated proposals considering below:

   - Amend the Cardano Constitution:

     - To address potential other CNTs in the constitutions
     - Any guardrails in practice for inclusion of CNTs
     - Do we define net change limits in CNTs also

   - A new CIP for multi asset treasury covering below areas:

     - Exact specification to describe the ledger change
     - Analysis to take network security into account
     - Do we need new protocol parameters for CMAT
     - What we use for threshold for listing & delisting if it introduces new governance actions
     - Other ledger rule's technical consideration such as min ADA

   - Update on existing CIPs such as [CIP-1694](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694).

2. Submit an Info Action of the CIP to gauge community sentiment if this is a requested change.

3. Implementation of the CIP (likely including passing governance action to initial hardfork in updating ledger)

### Out of Scope

- The whitelisted assets to be included in the Cardano Multi Asset Treasury
- The conversion and management of the multi-assets in the treasury

## Open Questions

### Spam Prevention - Only Allow Whitelisted Tokens

Spam prevention as if only whitelisted tokens can send into the treasury. Do we want to build in this feature into CMAT?

- For: Discussion in [(CIP159)](https://github.com/cardano-foundation/CIPs/pull/1061) thread acknowledges the need for spam prevention
- Against: Polkadot community mentioned whitelist is not needed as people just do not care

Spam prevention options:

- Introduce new governance action type with the function to add-new-asset to the treasuy, the gov action would be governed as other gov actions (CIP1694). Also comes with the usual 100k GA deposit.
- Another alternative is simply coordinate offchain tool set to ignore non-whitelisted CNTs from indexer, but not enforcing onchain.

### Should Onchain Treasury Participate in DeFi?

In Polkadot ecosystem, a large part of treasury activities are denominated in stables rather than its native token DOT. In order to meet such demand, Polkadot treausry indeed directly interacting with DeFi project to conduct dollar cost averaging selling DOT into stables. Do we want Cardano treasury to be able to participate in DeFi like Polkadot? Or do we prefer to stay clean and only use CMAT as custody of multi-assets only while conducting most active management offchain?

### Technology Path in Implementation

There are several potential ways to implement CMATs:

1. Cardano Wallet as Treasury

   > Implementing CMAT through ledger updates which transform the current Cardano Treasury files into an actuall address which can receive, hold and distribute multi assets

2. Multi Asset Stake Address as Treasury ([CIP159](https://github.com/cardano-foundation/CIPs/pull/1061))

   > A CIP that adds support for depositing assets into account addresses (a.k.a. reward/staking addresses) which helps alleviate some of the pain-points from the minUTxOValue requirement. The CIP also provides a mechanism for plutus smart contracts to get a sense of the account's current balance using account balance intervals similarly to how time is specified

3. Cardano Smart Contract as Treasury

   > A less technical challenging solution, deploying smart contracts which can receive, hold and distribute multi-assets under specific CIP1649 compatible rules

4. Reference Polkadot Implementation and deploy the open source tech stack
   > Polkadot runs its Multi Asset Treasury address not on its relay chain, but on its partnerchain framework using [substrate](https://docs.rs/pallet-treasury/latest/pallet_treasury/), substrate also implemented at Cardano for its L1 architecture would allow a similar approach

What technology path is more ideal in pursuing CMAT?

#### Additional Note on Technology Pathway from Cardano Summit Day 0 Discussion'

- There is historical reason / previous discussion in ledger team, and make it a deliberate decision to NOT implementing Cardano treasury as an address. Therefore, pathway number 1 is not suggested from there.
- [CIP159](https://github.com/cardano-foundation/CIPs/pull/1061) is the crucial infrastructure to enable multi-assets treasury withdrawal from user's point of view
- Prefer to implement the treasury in a simpler way of holding `Value` rather than `Coin`, with extra guardrails on whitelisting and de-whitelisting. From there, also not directly implementing CIP159 account as treasury due to first point above.`

### Other Technical Consideration

- How to make sure we do not expose additional vulnerability to Cardano ledger? Any accomodation with min ADA protocol parameter?
- How to ensure only minimal burden is created to Cardano toolchains, such as indexers, wallets, open source SDKs etc.

### Governance Implication

- Turning budget into stable denominated by default?
- Update on CIP-1694 to allow budget request in terms of Cardano Native Tokens but not limited to ADA
- How to determine which assets the treasury should hold?
- How are assets acquired or disposed?
- Guardrail on asset management. How to ensure proper financial stewardship?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
