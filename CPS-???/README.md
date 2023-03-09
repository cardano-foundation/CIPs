---
CPS: ?
Title: Burning NFTs / tokens
Status: Open
Category: Tokens
Authors:
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Proposed Solutions: 
    - smart contract / native script that is able to burn token

Created: 2022-12-01
---

## Abstract

The aim of this problem statement is to raise the issue around the ability to burn NFT / tokens and release minUTxO (ADA) backing the NFT / token.

## Problem

It is understood that minUTxO has been introduced as a way to protect ledger from tokens and NFTs spam, however, the only currently supported methods of "burning NFTs" do not address the core of the problem, namely releasing ADA 'locked' behind a token or NFT. Currently recommended methods of 'burning' are either sending to another wallet owned by the person sending or send to another wallet owned by somebody else. Neither of those methods actually releases underlying 'locked' minUTxO ADA.

It is worth mentioning that since the deposit scaling is affine, there is some incentive to keep bundling the tokens into bigger and bigger transaction outputs, potentially making the situation worse. It's unclear what the expectation should be regarding accepting payments in ADA that may be mired in tokens.

## Use cases

- As a Cardano user I have many NFTs that I do not need anymore and I would like to relaim ADA 'locked' by those NFTs. If a Cardano user has many useless NFTs / tokens this could sum up to significant amount of 'locked' minUTxO ADA.
- A typical use case of this would be going to your wallet of choice and bundling one or multiple tokens in one transaction and burning them somehow. Upon such a burn, ADA locked in those UTxOs would be reclaimed.

- Proposal is not a feature request to wallets only, it actually requires ledger changes first, which allow such reclaiming of ADA locked by tokens

## Goals
- Add ability for users to burn tokens and NFTs to be able to reclaim 'locked' minUTxO ADA.

## Open Questions
- How can we actually technically burn tokens?
- What changes would there need to be on ledger level to support such burning and make sense in the current ledger architecture?

## Bad solutions
- a potential solution of sending to zero address is not a good solution because not only it does not give you a full deposit back but also
zero addresses can be used as a reference input which could cause unexpected issues for somebody who thinks a token was burned

##  Possible solution
- smart contract / native script being able to burn token after minting policy is closed
