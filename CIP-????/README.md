---
CIP: ????
Title: Account Address Enhancement
Category: Ledger
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
    - George Flerovsky <george.flerovsky@gmail.com>
Implementors: N/A
Discussions: []
Created: 2025-07-16
License: CC-BY-4.0
---

## Abstract

Currently, Cardano's account addresses (a.k.a. reward addresses) can only be used for receiving ADA
from the Cardano protocol (e.g., staking rewards). Users are not allowed to deposit ADA into these
addresses. By removing this restriction, and enabling very specific plutus script support, Cardano
can unlock new use cases **without sacrificing local determinism**.

## Motivation: why is this CIP necessary?

Consider the following use cases:

### Wallet Revenue

Imagine a Cardano wallet that wants to charge a fee in a transaction it generates for a user. Right
now, the `minUTxOValue` network parameter disallows UTxOs with less than ~1 ADA. So if the wallet
just had the user send the money to them directly, **the smallest fee they could charge is 1 ADA**.
When the average transaction fee is only about [0.39
ADA](https://cardanoscan.io/analytics/dailyTxCountAndFees), it is hard to justify paying an extra 1
ADA on top.

*What if the wallet wanted to charge only 0.1 ADA? How could it get this 0.1 ADA from the user?*

The current method is to have the user deposit 1 ADA into a UTxO for the wallet provider. Then,
whenever the user needs to pay 0.1 ADA, this *deposit UTxO* would be spent to accumulate the 0.1 ADA.
This UTxO is effectively a "fee bucket" for that user.

While this method works, it has a few downsides:

1. It creates a bad UX since features are now gated behind different deposits that need proper
   management (with smart contracts for trustlessness).
2. What if the user wants to close out their deposit UTxO? If the deposit UTxO has less than 2 ADA
   (e.g., 1.5 ADA), the amount above 1 ADA (e.g., 0.5 ADA) needs to be sent to the wallet provider
which isn't possible due to the `minUTxOValue`! This complicates the reclamation process for user
deposits.
3. The wallet provider needs to manage one deposit UTxO per user which doesn't scale: withdrawing
   the accumulated fees requires spending one UTxO per user! (Having fewer UTxOs than users will
cause UTxO contention.)

**All of these problems go away if the wallet provider can just have the user deposit 0.1 ADA into
the designated account address!** By being able to charge much smaller fees, Cardano wallets will
have a significantly easier time finding product-market fit.

### Cheaper Batchers/Aggregators

Most batcher/aggregator networks charge at least 1 ADA. For some, the reason is the `minUTxOValue`
requirement. If it was actually possible to charge smaller fee amounts, Cardano's DeFi would be much
cheaper!

### Decentralized Fixed-Supply Token Minting

Imagine you only wanted to have 1 million units of a token minted. How can you keep a global count
while supporting decentralized minting? Currently, you can't. But what if users needed to deposit 1
ADA into an account address for every token minted. The account address' balance would be the global
count!

> [!IMPORTANT]
> In order to prevent actually needing global state, this CIP proposes account balance *intervals*.
> For example, the transaction to mint another token is only valid if the current account's balance
> is *less than 1 million*. Checking intervals can be done cheaply in Phase 1 validation just like
> with time (a.k.a. slot intervals). Plutus scripts will be able to see the interval constraints as
> part of their contexts.

By using account balance intervals, users can mint this token and their transactions can be
processed *in any order* - incrementing the account's balance doesn't invalidate other transactions
until the interval's upper bound is met.

### L2 reserves

Most L2s (e.g. Midgard) need to manage huge reserves of the L1 ADA from the users in the L2.
Initially, users typically create "deposit" event UTxOs; but eventually, the L2 will process these
deposits and move the ADA into a "reserve UTxO". Since the reserve itself is a UTxO, there may be
contention issues around how it is managed.

*With this CIP, L2s can process the deposit events UTxOs by depositing the ADA into an account
address.*

## Specification

### No datum support

In order to avoid global state issues, datums will not be supported. Consider the decentralized
minting example: what if each user needed to update the datum after each account deposit? The datum
itself would be a source of contention. As far as the authors are aware, there are no compelling use
cases for adding datums to account addresses.

> [!TIP]
> If a staking script *needs* data for its execution, it can use a datum attached to an existing
> UTxO.

### Enable ADA Deposits -- NO NATIVE ASSETS

The ledger rules currently disallow depositing into account addresses. This restriction will be
lifted to support ADA deposits. The transaction balancing rules will need to be updated to consider
these deposits.

**Depositing into an account address does not require a witness from the receiving account.** In
other words, the receiving staking script does *not* need to be executed. This behavior mirrors how
UTxOs can be created at script addresses without having to execute the spending script.

> [!IMPORTANT]
> Adding support for depositing native assets into account addresses is **out of scope** for this
> CIP. There are open questions for *how* to safely add support for native assets discussed in the
> [Rationale section](#future-cip---native-asset-deposit-support) of this CIP.

In order to deposit ADA into an account address, the receiving account address *must* be registered.

> [!NOTE]
> Withdrawing from the account address still requires delegation to a DRep.

When a deposit is made, plutus scripts can see the deposit amount in their contexts similarly to how
they can see the withdrawal amount. Since it is not recommended to enable negative numbers in the
[withdrawal
field](https://github.com/IntersectMBO/cardano-ledger/blob/cd7a8fd7ca833d120b87563a7e99e9b8c1db2dc1/eras/conway/impl/cddl-files/conway.cddl#L136)
of the transaction body, a new optional field needs to be added to the transaction body:

```cbor
transaction_body = 
  {   0  : set<transaction_input>         
  ,   1  : [* transaction_output]      
  ...
  , ? 23 : account_deposits ; new field
  }

account_deposits = {+ reward_account => coin} ; same definition as current withdrawals
```

And here is the associated change to the `TxInfo` seen by plutus scripts:

```haskell
data TxInfo = TxInfo
  { txInfoInputs                :: [TxInInfo]
  , txInfoReferenceInputs       :: [TxInInfo]
  , txInfoOutputs               :: [TxOut]
  , txInfoFee                   :: Value
  , txInfoMint                  :: Value
  , txInfoTxCerts               :: [TxCert]
  , txInfoWdrl                  :: Map Credential Haskell.Integer
  ...
  , txInfoDeposits              :: Map Credential Haskell.Integer -- ^ New field.
  }
```


> [!NOTE]
> See the [Rationale section](#future-cip---native-asset-deposit-support) for why `account_deposits`
> uses `coin` instead of preparing the stage for future native asset support.

### Account Balance Intervals

In order to give plutus scripts some idea of what is happening with the account address without
introducing a dependency on global state which can cause contention, transactions can specify
account balance intervals similarly to how time intervals are set. In order for the transaction to
be valid, the account's actual balance *must* fall within the validity interval. The lower bound is
inclusive while the upper bound is exclusive (i.e., `[1,5)`). The account balance intervals will be
passed to plutus scripts as part of their script contexts.

**Using the account balance interval does not require the associated credential to witness the
transaction.**

> [!IMPORTANT]
> Checking the validity of the withdrawn balance in a transaction is currently validated during
> Phase 1 validation and so is the time interval. Therefore, checking the account balance intervals
> should be cheap enough to be part of Phase 1 validation as well.

The transaction body will need to be changed to support these intervals. But considering transaction
builders may wish to specify intervals for multiple accounts in a single transaction, these
intervals need a different representation than what is used for time intervals:

```cbor
; Proposed alternative.
account_balance_checks = 
  { + reward_account => [ inclusive_lower_bound: coin, exclusive_upper_bound: coin ] }

transaction_body = 
  {   0  : set<transaction_input>         
  ,   1  : [* transaction_output]      
  ...
  , ? 24 : account_balance_checks ; new field
  }
```

And here is the change for `TxInfo`:

```haskell
data TxInfo = TxInfo
  { txInfoInputs                :: [TxInInfo]
  , txInfoReferenceInputs       :: [TxInInfo]
  , txInfoOutputs               :: [TxOut]
  , txInfoFee                   :: Value
  , txInfoMint                  :: Value
  , txInfoTxCerts               :: [TxCert]
  , txInfoWdrl                  :: Map Credential Haskell.Integer
  , txInfoValidRange            :: POSIXTimeRange
  ... 
  , txInfoDeposits              :: Map Credential Haskell.Integer
  , txInfoBalanceInterval       :: Map Credential BalanceInterval -- ^ New field. 
  }
```

> [!Tip]
> It is possible to specify the *exact* current balance of the account using the the intervals.

**Be careful around epoch boundaries since reward payouts will change the actual balance!**

### Enable Partial Withdrawals

There is currently a restriction that withdrawing from a stake address is "all-or-nothing". This
restriction will be lifted. Withdrawing any amount within the interval `0 <= x <= current_balance`
will be valid. Withdrawing an amount outside of this interval will fail Phase 1 Validation.

### Transactions Still Require UTxO inputs!

UTxO inputs effectively act as a transaction nonce that prevents certain possible attacks on
Cardano. Essentially, they guarantee every transaction is unique. Account addresses by themselves
are unable to offer the same guarantee which means this CIP does not remove the transaction's
requirement for at least one UTxO input.

## Rationale: how does this CIP achieve its goals?

This CIP makes Cardano's account addresses more expressive without introducing global state issues.
And critically, it offers safe ways around the `minUTxOValue` requirement which enables businesses
to charge fees <1 ADA. This dramatically increases the number of viable business models that can
operate on Cardano.

These specific changes to how account addresses work enable very simple parallel processing of
account actions without sacrificing Cardano's local determinism.

### Future CIP - Native Asset Deposit Support

Native asset support dramatically complicates the design since it would allow depositing worthless
native assets. This creates a type of "dusting attack" on account addresses. At this time, it is
unclear how to best solve this problem.

Due to this uncertainty, it was decided that it was best not to try future-proofing this CIP by
*guessing* what the future Native Asset CIP would require. If the guess turned out to be wrong,
Cardano would need to revert the failed future-proofing changes introduced by this CIP.

## Path to Active

### Acceptance Criteria
- [ ] These rules included within an official Plutus version, and released via a major hard fork.
      
### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve utility of
account addresses.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
