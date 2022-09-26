---
CIP: 70
Title: Spending policies
Authors: Michael Peyton Jones <michael.peyton-jones@iohk.io>
Status: Rejected 
Type: Standards Track 
Created: 23/09/2022
License: CC-BY-4.0
---

## Abstract

IMPORTANT: this CIP exists to record a design which has been considered in the past and rejected.
No version of this CIP is being proposed for inclusion in Cardano currently.

This CIP proposes to allow native tokens on Cardano to have a _spending_ policy in addition to their _minting_ policy.
The spending policy would be run whenever those tokens were spent, allowing control over how they are spent and moved.

## Motivation

Native tokens on Cardano today are associated with a minting policy that controls how the tokens can be minted or burned.
This allows user control of the _supply_ of tokens.

However, once tokens have been minted, they follow the normal accounting rules of Cardano's ledger. 
This is one of the things that justifies calling them "native", but it makes it difficult to implement some use cases that really _do_ want to change the basic accounting rules that their tokens follow.

Today, it is possible to work around this problem by using Cardano's main feature for controlling the spending of outputs: script-locked outputs.
However, using this systematically typically means that such tokens must always be locked by a script.
This adds significant complexity to the implementation, and negates a good deal of the benefit of the tokens being _native_: tokens locked by a script are not naturally "in" a user's wallet, nor can they be locked with _other_ scripts, which prevents using them in other "smart contracts".

### Examples

#### Blacklisting addresses

A common requirement for tokens that are regulated externally by governmental authorities (e.g. USDC) is to be able to blacklist addresses, preventing them from taking certain actions with their tokens (sometimes spending them, sometimes receiving them).

This has two challenges:
- Blacklisting prevents users from spending/receiving tokens.
- The blacklist is global state, so any spending of the blacklistable tokens must depend on and refer to the global blacklist.

#### "Claw-back"

A slightly less common requirement for regulated tokens is the ability to actually "claw-back" tokens, i.e. seize tokens which are held by certain individuals.

The primary challenge here is that this requires that the issuing authority be able to spend tokens in outputs "belonging" to other users.

#### Custom "transaction fees"

Some token projects would like to extract _transaction fees_ from their users (in the sense of "money paid to the issuer whenever those tokens are transacted", not the native Cardano transaction fees). 

This requires that an additional condition is enforced whenever the tokens are spent, namely that some payment is made to the issuer.

## Specification

The high-level approach is to associate with each currency a _spending_ policy in addition to the minting policy.
The ledger will enforce that the spending policy is run whenever tokens of the currency appear in a transaction.

### Associating tokens with spending policies

NOTE: this section has a couple of obvious deficiencies, but I leave it here as a sketch since this is not the main problem with the proposal.

Currently, we have

```haskell
-- The hash of a minting policy script
type PolicyId = ByteString

type Value = Map PolicyId (Map TokenName Integer)
```

We would change this to
```haskell
type PolicyId =
  -- The hash of a minting policy script
  MintingPolicyOnly ByteString
  -- The hash of a minting policy script and a spending policy script
  | MintingPolicyAndSpendingPolicy ByteString ByteString

type Value = Map PolicyId (Map TokenName Integer)
```

This allows the ledger to identify from the `Value` whether a currency is associated with a spending policy or not. 

### Ledger rules

Whenever a token appears anywhere in a transaction, the ledger will check whether it has a spending policy.
If it does, it will expect the corresponding script to be included in the witnesses, and will require it to be run.
Spending policies receive a redeemer (as do all scripts) and the script context.

## Rationale

All of the examples are based on the desire to regulate the _use_ of tokens in order to follow some rules that deviate from the Cardano's basic rules of accounting.
Spending policies are a simple translation of that: we associate tokens precisely with some user-defined logic that runs when the token is spent.
This is very similar to keeping the tokens always locked with a script, but it is implicit and does not occupy the address field, so that outputs can still clearly "belong" to a user (although as we will see below this is questionable).

However, this proposal has very serious problems.

### Why this CIP (and any like it) should not be accepted

Tokens with spending policies (henceforth "encumbered" tokens) cannot justifiably be described as "native" any more.
Since they effectively change the basic rules of Cardano's ledger, they are very difficult to work with:
- An output locked with a user's public key cannot necessarily be spent by the user, since any encumbered tokens may require arbitrary (opaque) additional conditions in order to be spent.
- Wallets cannot reliably make even basic transactions with encumbered tokens, since they will not know how to satisfy the spending conditions, and may not even be able to.
    - For example, if an encumbered token requires that a global blacklist be referenced in the spending transaction, the wallet would need token-specific logic in order to know how to find and reference the blacklist.[^1]
- Encumbered tokens cannot safely be used in smart contracts, since they may violate the assumptions of the smart contract by requiring additional conditions in order to be spent.
    - For example, consider a typical escrowed swap - what happens if you get to the resolution stage but then one side of the swap gets blacklisted? It gets stuck? One party loses their money? Who knows.[^2]
    
[^1]: This is more of a problem for Cardano than other blockchains because of our "verify don't act" approach. That means that the user constructing transactions is responsible for ensuring that any conditions are satisfied, rather than running that activity on the chain as part of a stateful smart contract.

[^2]: I believe this to be a problem on Ethereum too. If a smart contract expects to operate using some funds held by an ERC-20 contract that supports blacklisting, then unexpected failures may occur if the user gets blacklisted, even if the user had previously demonstrated access to the funds.
    
This is particularly insidious because since encumbered tokens look to a casual observer as though they are native (they are part of `Value`, they can appear in normal locked outputs), this introduces cases that existing code *must* handle, or else risk serious problems.
Realistically, wallets and dapps would have to blacklist any encumbered tokens by default, with exceptions done on a case-by-case basis.

The root cause is that spending policies allow for arbitrary, non-inspectable, user-provided logic to run on every transaction.
In this way they are not _easier_ to work with than the current workaround of keeping tokens always locked in a script, but they provide a false impression of being "native".
Moreover, this then infects truly native tokens with uncertainty: many assumptions about native tokens become invalid unless it is checked that there are no encumbered tokens involved.
The situation is actually better today, because tokens which are constrained in special ways are clearly marked by being kept in outputs locked with scripts.

These problems do not just apply to this specific proposal.
_Any_ proposal that causes certain tokens to be treated in a non-standard way has to answer questions like:
- How will we present the concept of ownership to users if other parties may also have rights to spend "their" outputs?
- How will a wallet know how to spend these tokens, given it may have to satisfy extra conditions?
- How will dapps be able to work with these tokens, given that they may have to satisfy extra conditions (which might change over time)?
- etc.

A possible route forward would be to not support _arbitrary_ user-specified spending policies, but rather have a restricted set of conditions that can be used.
However, it's tricky to see what conditions we could provide that would cover the desired use cases. 
Even something as conceptually simple as a blacklist can be set up in a number of ways, and this approach would require every such variant to be explicitly included in Cardano.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
