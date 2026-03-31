---
CPS: 5
Title: Plutus Script Usability
Category: Plutus
Status: Open
Authors:
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Proposed Solutions:
  - CIP-0038?: https://github.com/cardano-foundation/CIPs/pull/309
  - CIP-0057: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0057
  - CIP-0069: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0069
  - CIP-0087?: https://github.com/cardano-foundation/CIPs/pull/440
Discussions:
  - Original pull request: https://github.com/cardano-foundation/CIPs/pull/497
  - Developer Experience Working Group: https://github.com/input-output-hk/Developer-Experience-working-group
Created: 2023-04-04
License: CC-BY-4.0
---

## Abstract

The EUTXO model in Cardano makes it possible to implement a wide variety of rich and complex applications on top of Cardano.
However, it does not necessarily make it easy, and there are a number of usability issues that make it difficult for both users and automated systems to work with Plutus scripts in particular.

## Problem

There are a constellation of related issues around using Plutus scripts in practice and sending money to them.
In this CPS we restrict ourselves to usability issue with the _base_ experience of using Plutus scripts, i.e. not issues with implementing complex applications on top of Cardano, but issues with the basic actions of creating and spending outputs locked with Plutus scripts.

### 1. Plutus scripts need datums

Sending money to Plutus script addresses is harder than to other addresses because of the need for a datum in addition to the address and the value.
Moreover, the datum is mandatory, and if it is not included, the output will be unspendable.

On the flip side, many Plutus scripts don’t actually need datums.
Since they are forced to have one, they have to use a trivial fake datum, which just makes things harder for them.

### 2. It is not possible to know from the address whether a datum is required

Plutus scripts require datums otherwise they are unspendable.
Native scripts do not require datums.
But both Plutus script addresses and native script addresses are represented by “script addresses”.
So it’s possible to tell that an address is not a public key address, but not which kind of script address it is.

That means it’s not possible to know whether or not you need to provide a datum when creating  an output.
Since the cost of not including the datum when you need to is high (the output becomes unspendable), this can lead to overly cautious UX from wallets.
Currently some wallets warn when sending money to a native script address without a datum, because they can’t know that it’s not a Plutus script address!

### 3. Users are not familiar with the EUTXO concepts

Users are typically aware of the concept of addresses, but are much less likely to be aware of the concept of datums.
Thus, anything that requires them to think or operate with them is likely to be confusing, counterintuitive, and error-prone (at least at first).

### 4. Difficulty of communicating datums

Application developers often need to tell users to send money to a Plutus script address in order to participate in the application in some way (e.g. paying some money into the contract).
In order to do this, the user will need to provide a datum.
But it is difficult to communicate this to the user, because the most common format for making payments is to just provide an address and the amount to transfer.
This doesn’t accommodate adding a datum.

Plus, since users are not generally familiar with EUTXO concepts, attempts to communicate what they have to do via less direct means are difficult.

There are some tools that can help smooth this over, like the Dapp Connector, but they are not used universally.

### 5. Lack of affordances for EUTXO concepts

Many systems for working with Cardano don’t account for the need for datums or don’t make it easy to provide them.
A key example is wallets, but more generally many systems that can take an address to send funds to needs to explicitly accommodate datums, otherwise it will not be possible to use Plutus script addresses with it (see the Catalyst use case for an example).
This is often not obvious to the designers of the system!

### 6. Interaction models for Plutus scripts are obscure

Interacting with Plutus scripts is hard for everyone: users, wallets, and applications.
In base Cardano:

- You can’t find out how to form the datum and redeemer objects correctly
- You can’t find out what kind of actions you can take with a script
- You can’t find out how to take particular actions that you want to take

All of this makes it hard for both humans and computer systems to know whether they are interacting with the script correctly, which increases the risk of error significantly.
It also makes generic discoverability impossible, which forces application developers to provide lots of custom logic for every application in order to present users and systems with a comprehensible interface.

## Use Cases

### Simple escrow

Alice wants to escrow money using an escrow script S.
S requires a datum that indicates where to send the money back if the escrow fails to complete by the timeout.
It is difficult for the Alice to know a) that the datum is required, b) what the format is, c) how to actually enter it and make the payment.

### Catalyst payouts

Catalyst proposals include where to send the funds if the proposal is successful… in the form of an address.
This doesn’t support datums, so Plutus script addresses cannot be used to receive Catalyst funds.
Thus one cannot, for example, have the funds go directly into a DAO or similar system.

### DAO contribution

Bob wants to pay some money into a DAO or similar system which is supposed to reward them for their contributions with some special tokens.
In order for this to be enforced on-chain, we need a Plutus script output with a datum that records who the contributor was, so that their reward can be routed to them.

This means that Bob needs to construct a Plutus script output with a datum at some point, and that Bob cares about the content of the datum and cannot fully trust another party to construct it for them (otherwise they might just route the reward to themselves).
So Bob needs to somehow ensure that the correct output is created, and to verify the content of the datum.

### Ada Handles

The Ada Handle system works as follows:

1. Try to resolve handle H
2. Look for a specific NFT T that is related to H
3. H resolves to the address of the output at which T is held

This resolves the handle to an address, but as we have seen this is not enough to know how to make a payment to that address if it is a Plutus script address (which you can’t know).
A naive system which assumes it can send money to the address directly may create unspendable outputs if the handle token is held at a Plutus script address.

### Native script payments

Charlie wants to make a payment to a native script address.
This doesn’t require a datum, so they can do it simply based on the address, but their wallet gives them a scary warning because it doesn’t know that the address isn’t a Plutus script address that requires a datum.

### Smart contract wallet

Eve has no idea about key security, but cares about custodianship and hence prefers to use a wallet which allows her to recover funds using a social recovery key sharing scheme.
This system uses a Plutus script to be the “owner” of the funds.
When Eve wants to receive funds, her friends should not need to know what kind of wallet she is using - she should be able to provide them with a simple way to pay that is not meaningfully harder or different to paying into a normal wallet.

## Goals

### Avoid the need for users to know about datums in simple cases

Ideally users should be able to mostly not know about datums unless they actually want to determine the content of the datum themselves.

### Avoid forcing datums on scripts that don’t need them

If a script doesn’t want or need the facility to have datum then it shouldn’t be forced to have one, even if that makes things more consistent for the ledger.

### Uniform handling of payments to non-script addresses and script addresses

There should be a straightforward path for a system that deals with payments to support both non-script and script addresses correctly without additional effort.

### Single string for payments to script addresses

There should be a way to provide a user or system with a single string that contains all the information needed to make payment, whether it is to a Plutus script address or otherwise.

### Reduce the risk of accidentally making unspendable outputs

Try to make it less likely that users will accidentally create unspendable outputs, at least in some parts of the problem space (e.g. scripts that don’t “actually” need a datum).

## Open Questions

### Do we need to modify Cardano itself?

Many of the listed problems are about users interacting with Cardano.
That suggests that it may be possible to mitigate the problems in the systems that users use for interacting with Cardano (wallets, applications, etc.).

More generally, it’s unclear to what degree we should be aiming for excellent UX in Layer 1 itself.
But if we can make simple changes in Layer 1 that make it much easier for supporting systems to provide good UX, that might well be worth it.

### How many solutions do we need?

This CPS lists a lot of problems.
It’s not clear whether we will be able to come up with “big” solutions that solve many of the problems together, or whether we will need many “small” solutions that solve specific problems.

### How does this relate to generic metadata problems?

There has long been a problem of how to establish metadata about on-chain entities in Cardano (no CPS so far, but see CIP-25, CIP-26, CIP-68, etc. for various attempted solutions).
Many of the above problems could be mitigated with a good metadata solution, and it’s unclear to what degree this just “is” the metadata problem again.

For example, simply knowing the script itself (i.e. the pre-image of the hash used in the script address) helps with problem 1, because then you can know that it’s a Plutus script.
But it still doesn’t tell you what the form of the datum should be (problem 6), but this could be conveyed with additional metadata.

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
