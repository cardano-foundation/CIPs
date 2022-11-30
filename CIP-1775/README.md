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

We propose to allow users to delegate authorized spending of outputs in their wallets to smart contracts or other users,
without sending said outputs out of their wallets.

## Motivation

In order to use any dApp on Cardano (e.g. a decentralized exchange or an NFT marketplace), a user has to **deposit
tokens** to a script address, thereby **giving up custody** of the tokens.

This can be problematic for a number of reasons.

- The user loses control of the assets they send out to a smart-contract, unless the smart contract is specifically
  designed to allow for such control (e.g. providing a "Cancel trade" or "De-list NFT" button in the UI).
- Assets sent out from a user's wallet:
    - are no longer **delegated** to the stake pool of the user's choice, unless sent to a specially constructed
      _hybrid_ address with the user's StakeKeyHash as the delegation part,
    - cannot participate in **governance voting** on behalf of the user, unless hybrid addresses are used and the voting
      system counts assets at these hybrid addresses based on the stake key hash.
- Any output, accidentally sent to a script address without a datum is effectively lost now (because of how transaction
  validation scripts are invoked).
- Requiring users to deposit assets into a dapp may subject the dapp to regulatory scrutiny.

We believe, this is not strictly necessary and would like a way to allow users to delegate spending authorization for
some outputs **within** their wallets to other users (smart contracts, multisigs, wallet addresses).

### Use Cases

Instead of sending tokens to the dapp smart-contract, the user creates an output in their own wallet that delegates
spending authorization to a smart-contract (or other entity).

Some **existing** use cases, where this can be beneficial:

1. Swapping tokens on a decentralized exchange.
2. Providing liquidity on a decentralized exchange.
3. Listing an NFT on a marketplace.

Some **new** use cases, enabled by this proposal:

1. On-chain noncustodial asset management. A user can delegate managing (some of) their assets to a manager, another
   individual user or organization.
2. Concurrent use of dapps. For example, a user can provide liquidity and, at the same time, have a trade open at a (
   different) DEX, with the same output. When the trade is executed, it looks just as though the user has withdrawn the
   output from the liquidity pool.
3. Seamless interaction with L2 (sidechains or Hydra). The user doesn't need to send assets to the L2 entrypoint
   script/multisig, nor do they need to explicitly take them out.
4. Combinations of all of the above, both existing and new 🙃.

Note, that we are **not** proposing to eliminate DApps with full control of outputs. Traditional custodial ("deposit and
pray") smart contracts are preserved in full force.

### Other Benefits

- Users' assets continue to participate in delegated proof of stake and on-chain governance without special effort from
  DApps or users.
- Assets cannot be locked forever in noncustodial (delegated) smart-contracts, by definition.

## Specification

### Delegated Spending Authorizations

A solution is to introduce _delegated spending authorizations_: instead of **sending** an output to an address, a user
could **delegate** a spending authorization of the output to the address.

### CDDL

To enable this, a **new** field is added to the transaction output (the current spec can be found
here: https://github.com/input-output-hk/cardano-ledger/blob/master/eras/babbage/test-suite/cddl-files/babbage.cddl):

```cddl
post_alonzo_transaction_output =
  { 0 : address
  ; ...
  , ? 4 : { * address => ( datum_option / nil ) }   ; New; authorized spenders
  }
```

The new field is a map from `address` to `datum_option` or `nil`. In this map, `address` is a Shelley address (
see [CIP-19](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0019)). The value (`datum_option`) only makes
sense for Plutus script addresses, so it is optional (can be `nil`).

### Spending of Outputs

Delegated spending authorizations **only** work for:

- wallets (Shelley addresses Type 0, 2, 4 or 6, according
  to [CIP-19](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0019)),
- Plutus v3 (or higher) scripts (Shelley addresses Type 1, 3, 5 or 7, according
  to [CIP-19](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0019)).

These addresses can:

- own outputs with delegated spending authorizations,
- be a delegated authorized spender of an output.

A transaction can spend the output if it satisfies spending conditions:

- for the output's owner address (i.g. signed by the wallet's private key), or
- for any address in the output's _delegated spending authorizations_.

Delegated spending authorizations are **ignored** for addresses of other kinds (both as output owners and delegated
authorized spenders).

### Script Context

Plutus v3 (or higher) scripts can participate in delegated spending authorizations, both as owners of the output and as
authorized spenders. The Plutus version bump is required because:

- assumption of exclusive control of outputs should be preserved for prior script versions - to not break things,
- authorized spenders need to be added to the script context - to make the script aware of its "competition".

## Implications

While providing the benefits listed in the **Motivation** section, there is a certain **cost**: users need to be made
aware of _delegated spending authorizations_ on the outputs in their wallets.

Assets arriving into a user's wallet with delegated spending authorizations attached, come with a form of remote
control (which can be exploited). Obviously, the user can remove it, but **only** if they know it exists.

Therefore, when this change is implemented, wallet UX **needs** to reflect it. Users should be warned when:

- they are _about to sign_ a transaction resulting in UTXOs with delegated spending authorizations in their wallets,
- have UTXOs with delegated spending authorizations attached (perhaps, having received them from a dapp or a sidechain).

## Related Work

The idea for this CIP came about when thinking of ways to simplify user experience and reduce L1 transaction load when
interacting with sidechains.

To work with a sidechain, assets need to be deposited into its "gate script" -- a script, that will hold the assets for
the duration of their usage in the sidechain. When the sidechain transactions are settled, the assets can be withdrawn
by their new owner. Of course, when/if the new owner needs to use them on the sidechain, they need to send to the gate
script again.

These "deposit / withdraw" steps may seem unavoidable, but in fact, to some extent, they defeat the purpose of a
sidechain (provide superior user experience, higher speed, lower cost, rely on L1 for security). For example, if a
sidechain powers a decentralized CashApp equivalent, these extra "deposit / withdraw" steps would mean added load on the
L1 and additional complexity for the user and the developer.

_Delegated spending authorizations_ solve these problems:

- Assets stay in users' wallets.
- Spending authorization is delegated to the sidechain.
- Recipients see assets arrive directly into their wallets.
- The received assets are immediately ready to be used on either Cardano L1 or the sidechain.
