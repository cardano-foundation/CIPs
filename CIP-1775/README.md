---
CIP: 1775
Title: Delegated Spending Authorizations
Authors: Ivan Mikushin <sorrel_cantos.0@icloud.com>
Comments-URI:
Status: Proposed
Type: Standards Track
Created: 2022-11-17
License: CC-BY-4.0
---

# Delegated Spending Authorizations

"Give me custody, or give me death!" - [@ArmySpies](https://twitter.com/ArmySpies/status/1592586212816355328)

## Abstract

We propose to allow users to delegate authorized spending of outputs in their wallets to smart contracts or other users, without sending said outputs out of their wallets.

## Motivation

In order to use any dApp on Cardano (e.g. a decentralized exchange or an NFT marketplace), a user has to **deposit tokens** to a script address, thereby **giving up custody** of the tokens.

This can be problematic for a number of reasons.

- The user loses control of the assets they send out to a smart-contract, unless the smart contract is specifically designed to allow for such control (e.g. giving a "Cancel trade" or "De-list NFT" button in the UI).
- Assets sent out from a user's wallet:
  - are no longer  **delegated** to the stake pool of the user's choice.
  - cannot participate in **governance voting** on behalf of the user.
- Any output, accidentally sent to a script address without a datum is effectively lost now (because of how transaction validation scripts are invoked).
- Requiring users to deposit assets into a dapp may subject the dapp's owners to regulatory scrutiny.

We believe, this is not strictly necessary and would like a way to allow users to delegate spending authorization for some outputs **within** their wallets to other users (smart contracts, multisigs, wallet addresses).

### Use Cases

Instead of sending tokens to the dapp smart-contract, the user creates an output in their own wallet that delegates spending authorization to a smart-contract (or other entity).

Some **existing** use cases, where this can be beneficial:

1. Swapping tokens on a decentralized exchange.
2. Providing liquidity on a decentralized exchange.
3. Listing an NFT on a marketplace.

Some **New** use cases, enabled by this proposal:

1. On-chain noncustodial asset management. A user can delegate managing (some of) their assets to a manager, another individual user or organization.
2. Concurrent use of dapps. For example, a user can provide liquidity and, at the same time, have a trade open at a (different) DEX, with the same output. When the trade is executed, it looks just as though the user has withdrawn the output from the liquidity pool.
3. Seamless interaction with L2 (sidechains or Hydra). The user doesn't need to send assets to the L2 entrypoint script/multisig, nor do they need to explicitly take them out.
4. Combinations of all of the above, both existing and new 🙃.

### Other Benefits

- Users' assets continue to participate in delegated proof of stake and on-chain governance.
- Assets cannot be locked forever in noncustodial (delegated) smart-contracts, by definition.

## Specification

### Delegated Spending Authorizations

A solution is to introduce _delegated spending authorizations_: instead of **sending** a output to an address, a user could **delegate** a spending authorization of the output to the address.

### CDDL

To enable this, a **new** field is added to the transaction output (the current spec can be found here: https://github.com/input-output-hk/cardano-ledger/blob/master/eras/babbage/test-suite/cddl-files/babbage.cddl):

```cddl
post_alonzo_transaction_output =
  { 0 : address
  ; ...
  , ? 4 : { * address => ( datum_option / nil ) }   ; New; delegated spending authorizations
  }
```

The new field is a map from `address` to `datum_option` or `nil`. In this map, `address` can be any address: Plutus v1 and v2 scripts, wallets, etc. The value (`datum_option`) only makes sense for Plutus script addresses, so it is optional (can be `nil`).

### Spending of Outputs

When the output's `address` (field 0) is a **wallet** address, a transaction can spend the output if it satisfies spending conditions:
- for the output's address (i.e. signed by the wallet's private key), or 
- for any address in the output's _delegated spending authorizations_.

If the output's `address` is of **any other kind** (e.g. native or Plutus script), the _delegated spending authorizations_ field contents **do not affect** spending behavior. Existing scripts' assumptions must be **unaffected** by the proposed ledger change: spending of outputs at a script address are controlled by the script only.

With the above rules, we believe, the change does not require Plutus language version bump.

## Implications

While providing the benefits listed in the **Motivation** section, there is a certain cost: users need to be made aware of _delegated spending authorizations_ on the outputs in their wallets. 

Assets that arrive into a user's wallet with delegated spending authorizations attached, kind of come with a form of remote control (which can be exploited). Obviously, the user can remove it, but **only** if they know of its existence.

Therefore, when this change is implemented, wallet UX **needs** to reflect it.

## Related Work

The idea for this CIP came about when thinking of ways to simplify user experience and reduce L1 transaction load when interacting with sidechains. 

To work with a sidechain, assets need to be deposited into its "gate script" -- a script, that will hold the assets for the duration of their usage in the sidechain. When the sidechain transactions are settled, the assets can be withdrawn by their new owner. Of course, when/if the new owner needs to use them on the sidechain, they need to send to the gate script again.

These "deposit / withdraw" steps may seem unavoidable, but in fact, to some extent, they defeat the purpose of a sidechain (provide superior user experience, higher speed, lower cost, rely on L1 for security). For example, if a sidechain powers a decentralized CashApp equivalent, these extra "deposit / withdraw" steps would mean added load on the L1 and additional complexity for the user and the developer.

_Delegated spending authorizations_ solve these problems:

- Assets stay in users' wallets.
- Spending authorization is delegated to the sidechain.
- Recipients see assets arrive directly into their wallets.
- The received assets are immediately ready to be used on either Cardano L1 or the sidechain.
