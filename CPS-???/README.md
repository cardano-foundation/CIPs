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

## Use cases

- As a Cardano user I have many NFTs that I do not need anymore and I would like to relaim ADA 'locked' by those NFTs. If a Cardano user has many useless NFTs / tokens this could sum up to significant amount of 'locked' minUTxO ADA.

## Goals
- Add ability for users to burn tokens and NFTs to be able to reclaim 'locked' minUTxO ADA.

## Open Questions
- How can we actually allow this if blockchain is supposed to be immutable? One there was a token and now there is no token anymore (dangling tokens?).


##  Possible solution
- smart contract / native script being able to burn token after minting policy is closed