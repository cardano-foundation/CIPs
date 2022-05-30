---
CIP: ??
Title: Treasury donation
Authors: Sebastien Guillemot <seba@dcspark.io>
Comments-URI: TBD
Status: Proposed
Type: Standards
Created: 2022-05-30
License: CC-BY-4.0
---

## Abstract

Cardano's treasury is currently denominated purely in ADA and has no source of revenue other than the existing reward splitting mechanism implemented at the protocol level. This CIP intends to diversity the treasury holdings and increase protocol revenue to the treasury.

## Motivation

Cardano currently spends 12.8M USD every 3 months (~25M ADA at the current price) on Catalyst. Additionally, there is discussion of increase the amount drawn from the treasury through initiatives like the DCF.

However, there are two key points with the current system relevant to this CIP:

1. **Catalyst funds are entirely denominated in ADA**. This is not ideal because Catalyst rewards are currently denominated in USD. It means that the amount of funds available can vary wildly between bear & bull markets and, in the worst case, could lead to Catalyst going bankrupt if the price of ADA falls below its obligations. You can read more about this problem [here](https://uncommoncore.co/a-new-mental-model-for-defi-treasuries/)
2. **Treasury funds for private ventures does not necessarily lead to increased Catalyst revenue.**. To expand on this, a lot of the spending on Catalyst right now is for direct benefit of the protocol (marketing, open source tools, etc). However,  for fund 9, there is 7.8M USD allocated to products & integrations for Catalyst fund 9 which shows there is interest in funding efforts that only may only indirectly lead to protocol revenue (funding private ventures). Despite this, companies are [hesitant to take Catalyst rewards](https://twitter.com/blakelockbrown/status/1530968246332952576) because of this missing link in incentives.

Notably, we can leverage point (2) to tackle point (1) by giving private ventures a way to pay it forward by contributing to treasury funds in a variety of (hopefully uncorrelated) assets.

## Specification

Reminder of the current system: at the time of writing, the Cardano treasury balance is not accumulated through on-chain transactions, but rather kept track of as part of the ledger state (similar to reward balances). To access treasury rewards, a special certificate called the MIR certificate is used to withdraw from the treasury balance. This means that treasury balances, just like reward addresses, only contain ADA (no tokens) and there is no way to send to the treasury address.

This means that to allow companies to donate to the treasury, we need to define an on-chain address for the treasury. This can be done following the same format as the [upgradeable treasury smart contract](https://github.com/dcSpark/plutus-smart-contract-upgrade-dApp) from dcSpark.

### Updating the treasury

Cardano does not have an on-chain governance method for deciding protocol parameters. This missing functionality also makes it hard to decide on how to upgrade the treasury contract. As a temporary workaround similar to the current behavior, we could add MIR certificates to the Plutus context so that the contract can look at the context to decide if the contract can be upgraded.

### Convincing projects to pitch in

Once private ventures receive Catalyst funding, there is nothing to force them to actually donate back to the treasury after they've achieved market success. This should instead be encouraged at the social level and Catalyst proposals for these categories should be encouraged to define in their proposal whether they have any plans to donate funds back to the treasury.

Additionally, the community should encourage projects to pitch in with assets that are as uncorrelated with ADA as possible (different baskets)

### Compatibility with future treasury plans

The upgradeability of the contract should make it easy to keep this system compatible with existing plans for the Cardano treasury. For clarity, I will detail some of the treasury plans and how this proposal is compatible with them:

1. **Allowing Catalyst rounds in non-ADA tokens** (ex: COTI rewards for COTI proposals which has happened in the past). This proposal is compatible with this idea because projects could send their tokens to the treasury address. Additionally, it makes itt easier for this to happen because we could allow projects to put in 10K ADA (arbitrary number) as a fee to mint a project ID to the treasury address which can be redeemable once to add the project to Catalyst using the funds for that token present in the address. The fee of this mint would be used to both fund the main ADA treasury balance and to cover the cost of distributing rewards for the Catalyst challenge of the project.
2. **DCF**. DCF is a more complicated version of Catalyst meant for higher amounts with higher auditability on spending. DCF plans to have its own Plutus scripts, so there may be an overlap in the approach, but these DCF scripts could receive their initial funding from the treasury address so there should not be a compatibility issue.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

[CIP-0008]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0008
