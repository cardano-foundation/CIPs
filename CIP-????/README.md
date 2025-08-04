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

## Table of Contents

- [Abstract](#abstract)
- [Motivation](#motivation-why-is-this-cip-necessary)
  - [Wallet Revenue](#wallet-revenue)
  - [Cheaper Batchers/Aggregators](#cheaper-batchersaggregators)
  - [Multi-Asset Cardano Treasury](#multi-asset-cardano-treasury)
  - [Decentralized Fixed-Supply Token Minting](#decentralized-fixed-supply-token-minting)
  - [L2 Reserves](#l2-reserves)
- [Specification](#specification)
  - [Definitions](#definitions)
  - [Enable Direct Deposits](#enable-direct-deposits)
  - [Partial Withdrawals and Native Asset Withdrawals](#partial-withdrawals-and-native-asset-withdrawals)
  - [Account Balance Intervals](#account-balance-intervals)
  - [New Ledger State](#new-ledger-state)
  - [New Plutus Script Context](#new-plutus-script-context)
- [Rationale](#rationale-how-does-this-cip-achieve-its-goals)
- [Path To Active](#path-to-active)

## Abstract

Currently, Cardano's account addresses (a.k.a. reward addresses) can only be used for receiving ADA
from the Cardano protocol (e.g., staking rewards). Users are not allowed to deposit assets into
these addresses. By removing this restriction, and enabling very specific plutus script support,
Cardano can unlock new use cases **without sacrificing local determinism**. And by still requiring
UTxO inputs in transactions, these accounts avoid many of the pitfalls from Ethereum-style accounts.

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

### Multi-Asset Cardano Treasury

Cardano's Treasury account is currently only allowed to hold ADA. However, it would be more fiscally
responsible for the Treasury to hold a basket of assets. The basket would diversify the risk of price fluctuations and ensure that important protocol developments can continue despite price shocks in any particular asset class.

### Decentralized Fixed-Supply Token Minting

Imagine you only wanted to have 1 million units of a token minted. How can you keep a global count
while supporting decentralized minting? Currently, you can't. But what if users needed to deposit 1
"count" token into an account address for every unit of the target token minted? The account
address' balance of the "count" token would be the global count! Since addition is commutative, the
transactions that mint the tokens can be processed in any order and fully parallel.

> [!IMPORTANT]
> In order to prevent actually needing global state, this CIP proposes account balance *intervals*.
> For example, the transaction to mint another token is only valid if the current account's balance
> is *less than 1 million*. Checking intervals can be done cheaply in Phase 1 validation just like
> with time (a.k.a. slot intervals). Plutus scripts will be able to see the interval constraints as
> part of their contexts.

By using account balance intervals, incrementing the account's balance doesn't invalidate other
transactions until the interval's upper bound is met.

### L2 reserves

Most L2s (e.g. Midgard) need to manage huge reserves of the L1 ADA from the users in the L2.
Initially, users typically create "deposit" event UTxOs; but eventually, the L2 will process these
deposits and move the ADA into a "reserve UTxO". Since the reserve itself is a UTxO, there may be
contention issues around how it is managed.

*With this CIP, L2s can process the deposit event UTxOs by depositing the ADA into an account
address.*

## Specification

### Definitions

For clarity:
  - *Protocol Deposit* will refer to the deposits required by the protocol for registration.
  - *Direct Deposit* will refer to assets being sent to an account address.

### Enable Direct Deposits

The ledger rules currently disallow directly depositing assets into account addresses. This
restriction will be lifted to support direct deposits. The transaction balancing rules will need to
be updated to consider these direct deposits.

**Direct depositing into an account address does not require a witness from the receiving account.**
In other words, the receiving staking script does *not* need to be executed. This behavior mirrors
how UTxOs can be created at script addresses without having to execute the spending script.

> [!IMPORTANT]
> In order to support direct deposits, the account address must be registered.

By default, only direct deposits of ADA are supported. Pre-existing registered account addresses
will be automatically upgraded to support direct deposits of ADA through a hardfork-combinator
event. 

Users will be able to submit a new certificate event (`reg_account_value_cert`), which will initialize the balances of certain native assets (listed in the certificate) at an account address, starting all of the balances at zero. After these balances are initialized, users will be able to direct-deposit those native assets into that account.

The set of initialized balances at an account also acts as a **whitelist** on the native assets allowed at the account. Direct deposits of other native assets into the account will be rejected by the ledger rules, except for ADA, which can always be deposited into any Cardano account.

> [!IMPORTANT]
> We implement this by using the new `AccountValue` type, which is similar to `Value` but prevents adding or
> removing assets in the `AccountValue`. You can only increase or decrease the asset quantities. If a
> transaction tries directly depositing a native asset that is not found in the `AccountValue`, it
> will fail phase 1 validation.

The only way to alter which native assets are found in the `AccountValue` is through another
dedicated certificate event. The new certificates are outlined below:

```cbor
; Certificate to initialize the `AccountValue` and requires an extra protocol deposit.
; The protocol deposit will be proportional to the `multiasset` in the certificate.
reg_account_value_cert = (19, stake_credential, multiasset)

; Certificate to disable native asset direct deposits and reclaim the associated
; protocol deposit.
unreg_account_value_cert = (20, stake_credential)

certificate = 
  [  stake_registration
  // stake_deregistration
  // stake_delegation
  ...
  // reg_account_value_cert
  // unreg_account_value_cert
  ]
```

Crucially, since the `AccountValue` will take up space in memory, it must be accompanied with an
extra protocol deposit that is proportional to the size of the `AccountValue`. This extra protocol
deposit must be paid in the transaction using the `reg_account_value_cert`.

> [!NOTE]
> With UTxOs, the minUTxO protocol deposit is paid by the creator of the UTxO. With account
> addresses, the `AccountValue` protocol deposit will be paid upfront by the address owner. This is
> what enables the micropayments discussed in the [Motivation section](#motivation-why-is-this-cip-necessary).

There are a few important behaviors to be aware of with these new certificates:

- The `unreg_account_value_cert` forces the user to withdraw all native assets currently in the
account address.
- Updating the registered `AccountValue` can be done by submitting the `unreg_account_value_cert`
and the `reg_account_value_cert` in the same transaction. To carry over the balances from the old
`AccountValue` to the new `AccountValue`, the transaction must specify direct deposits for those
assets in the same transaction. The assets must effectively be re-deposited.
- If you are only using the `unreg_account_value_cert`, you will be able to recover the part of the
  protocol deposit that was for the `AccountValue`. **The account address itself remains
registered for delegation.**
- Transactions involving these certificates must be witnessed by the associated staking credentials.
  These certificates must be approved by the community to be used on the Cardano Treasury account
address.

For this to work, the transaction representation needs a new direct deposit field:

```cbor
direct_deposits = {+ reward_account => value}

transaction_body = 
  {   0  : set<transaction_input>         
  ,   1  : [* transaction_output]      
  ,   2  : coin                            
  , ? 3  : slot_no                         
  , ? 4  : certificates                    
  , ? 5  : withdrawals                     
  ...
  , ? 23 : direct_deposits ; new field
  }
```

> [!TIP]
> *Why not just make withdrawals support negative numbers?*
>
> 1. It would cut in half the maximum supported number.
> 2. Withdrawals require witnesses while direct deposits do not. This means we need to be able to
>    distinguish between direct deposits and withdrawals with for the `ScriptPurpose`.
>
> Adding a separate field is the better approach.

Plutus scripts will be able to see the direct deposits occuring in the transaction as part of their
`ScriptContext`. See the [New Plutus Script Context section](#new-plutus-script-context).

> [!IMPORTANT]
> The direct deposits are only the diff! If the account currently has 100 ADA and the transaction is
> direct depositing another 0.1 ADA, the transaction only needs to specify 0.1 ADA.

### Partial Withdrawals and Native Asset Withdrawals

In order for direct deposits to actually be useful, partial withdrawals are a fundamental
requirement. To see why, imagine a wallet charges a 0.1 ADA fee per transaction and these
transactions are submitted every 30 seconds. Currently, the ledger rules require the wallet to
withdraw the full balance in the account address. Let's say when the wallet submits the withdrawal
transaction, the balance is 100 ADA. While this transaction is sitting in the mempool, another user
directly deposits another 0.1 ADA into the wallet's account address. Now the wallets transaction in
the mempool is *not* withdrawing the full amount and will fail phase 1 validation! Without partial
withdrawals, whether the wallet will actually be able to access the assets in the account will
depend on luck! So the ledger rules *must* be changed to allow withdrawing any amount between 0 and
the current balance. 

> [!IMPORTANT]
> For all withdrawals, partial or full, the pre-existing `Withdraw` purpose will be used. We do not
> need a dedicated purpose for partial withdrawals.

To enable support for withdrawing native assets from account addresses, the representation of
withdrawals inside transactions needs to be updated:

```cbor
; Old representation.
withdrawals = {+ reward_account => coin}

; New representation.
withdrawals = {+ reward_account => value} ; replaced `coin` with `value`
```

Likewise, since the Cardano Treasury is also able to hold whitelisted native assets, the
`treasury_withdrawals_action` must be updated:

```cbor
; Old representation.
treasury_withdrawals_action = (2, {* reward_account => coin}, policy_hash/ nil)

; New representation.
treasury_withdrawals_action = (2, {* reward_account => value}, policy_hash/ nil) ; replaced `coin` with `value`
```

### Account Balance Intervals

Transactions can specify account balance intervals similarly to how time intervals are set. In order
for the transaction to be phase 1 valid, the actual balance for the associated asset in the account
*must* fall within the specified interval. The transaction representation is shown below:

```cbor
account_balance_intervals = 
  {+ reward_account => 
      {+ policy_id => 
          {+ asset_name => [ inclusive_lower_bound: uint, exclusive_upper_bound: uint ] }}}

transaction_body = 
  {   0  : set<transaction_input>         
  ,   1  : [* transaction_output]      
  ...
  , ? 24 : account_balance_intervals ; new field
  }
```

As the representation shows, the transaction submitter can specify intervals for different assets
inside a given account address. In addition to this, there are two important behaviors that need to
be mentioned:

1. Using the account balance interval does *not* require a witness from the associated credential.
2. To declare that a certain asset in the `AccountValue` has a `0` balance, the asset's balance interval must be set to `[0,0)`.

Plutus scripts will be able to see the set account balance intervals as part of their
`ScriptContext`. See the [New Plutus Script Context section](#new-plutus-script-context).

### New Ledger State

Currently, account address state is [stored in the ledger](https://github.com/IntersectMBO/cardano-ledger/blob/3fa847bd67a6d1c3c2d5960578c993487e9883b0/eras/conway/impl/src/Cardano/Ledger/Conway/State/Account.hs#L45) as:

```haskell
data AccountState era
  = AccountState
  { balance :: !(CompactForm Coin)
  -- ^ Current balance of the account
  , deposit :: !(CompactForm Coin)
  -- ^ Deposit amount that was left when staking credential was registered
  , stakePoolDelegation :: !(StrictMaybe (KeyHash 'StakePool))
  -- ^ Potential delegation to a stake pool
  , dRepDelegation :: !(StrictMaybe DRep)
  -- ^ Potential delegation to a DRep
  }
```

This CIP proposes changing this ledger state to:

```haskell
data AccountState era
  = AccountState
  { balance :: !(CompactForm Coin)
  -- ^ Current ADA balance of the account.
  , deposit :: !(CompactForm Coin)
  -- ^ Total protocol deposit amount that was left when staking credential
  -- was registered and when multi-asset whitelist was created.
  , multiAssetBalance :: MultiAsset (Map PolicyID (Map AssetName Integer))
  -- ^ Current balance of the native assets in the account address.
  , stakePoolDelegation :: !(StrictMaybe (KeyHash 'StakePool))
  , dRepDelegation :: !(StrictMaybe DRep)
  }
```

There are a few important points to notice:

1. The ADA balance is kept separate from the multi-asset balance.
2. The `deposit` field holds *both* the stake credential registration deposit *and* the whitelist
   registration deposit.
3. The `multiAssetBalance` map *is the whitelist*. It can only increase/decrease the `Integer`; it
   cannot add/remove new `PolicyID`s or `AssetName`s to the map. If the asset has no balance, the
`Integer` should be set to `0`.

> [!IMPORTANT]
> The required protocol deposit for the whitelist registration will be proportional to the size of
> the `multiAssetBalance` map. The calculation can be similar to the `minUTxOValue` calculation, but
> it should get separate protocol parameters so that the `multiAssetBalance` costing can be changed
> independently to the `minUTxOValue` costing.

### New Plutus Script Context

This CIP does not introduce any new `ScriptPurpose`s, but the `TxInfo` field needs to contain the
new sub-fields:

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
  , txInfoDirectDeposits        :: Map Credential Haskell.Integer -- ^ New field.
  , txInfoBalanceIntervals      :: Map Credential (Map PolicyID (Map AssetName BalanceInterval)) -- ^ New field. 
  }
```

## Rationale: how does this CIP achieve its goals?

This CIP is able to upgrade Cardano's account addresses to full accounts *without* sacrificing local
determinism and *without* introducing the issues seen with Ethereum-style accounts. The reasons for
this are based on what this CIP *does not* enable, more than on what it does enable. The most
important things are:

- This CIP *does not* enable submitting transactions without UTxO inputs.
- This CIP *does not* enable attaching datums to account addresses.
- This CIP *does not* enable phase-2 scripts to view the **exact** account balance.
- This CIP *does not* enable directly depositing arbitrary native assets into account addresses.
Only whitelisted native assets are allowed (i.e. native assets with balances initialized at the account).

### Still Require UTxO Inputs

On Ethereum, every address has an integer nonce that must be incremented after each account event.
This integer is required to prevent replay attacks (e.g., it ensures transactions are processed in
the right order), but it has the downside of causing contention - if two Ethereum transactions try
to withdraw using the same nonce integer, only one will succeed. The problem is that the nonce is
intrinsic to the account.

Since each Cardano transaction must include a UTxO, the UTxO's output reference acts as a nonce.
Changing the order of the Cardano transactions does not matter as long as the UTxOs actually exist.
This means withdrawing from Cardano account addresses *does not* experience contention. Both Alice
and Bob can each submit a transaction withdrawing from an account address, and these transactions
can be processed in any order.

### No Datum Support

Consider the decentralized minting example: what if each user needed to update the datum after each
account deposit? The datum itself would be a source of contention in the same way the integer nonce
is for Ethereum.

If an account *needs* data for its validation, it can use a datum attached to an existing UTxO.
UTxOs are the perfect medium for controlling access to data and they enable breaking the data into
chunks. If an account only needs a piece of the available data, it can reference a UTxO with *just*
that data. Storing the data with the account would require processing *all* of the stored data, even
the parts that aren't necessary for a given execution. In short, using the datums attached to UTxOs
is much more efficient.

### No Exact Balance View

Enabling plutus scripts to view the account's exact balance would require sacrificing Cardano's
local determinism. If Alice submits a transaction at time `t0` where the account's balance is 100
ADA and then the transaction gets processed at time `t1` when the account balance is 1000 ADA, the
smart contracts in the transaction use different numbers in there executions. This can result in
completely different execution budget usages which results in completely different fees. Same
transaction; different fees.

By using the account balance intervals instead, Alice's transaction would get the same inputs at
`t0` and `t1`. As long as the intervals are still satisfied, it does not matter that the account
balance has actually changed. Both executions result in the same execution budget usages and
therefore, the same fees. Cardano's local determinism is preserved.

### Whitelisted Native Assets Only

The reason Cardano has a `minUTxOValue` requirement is to prevent native asset dusting attacks - a
malicious person can create worthless tokens and create UTxOs with *only* these assets. When block
producers try to validate transactions, they need to load the UTxOs into memory. If the size of
these UTxOs are not somehow tied to real world resource constraints, the malicious actors can cause
block producer memory usages to explode with these worthless native assets taking up space. This is
effectively a ddos attack. By requiring every UTxO to contain ADA, a malicious actor is only able to
cause this attack if they actually have the required amount of ADA to back the memory usage required
to process the native asset values.

If account addresses could accept arbitrary native assets like UTxOs, they would be susceptible to
the same dusting attacks. A first thought might be to have a `minUTxOValue`-like protocol deposit
for account addresses - the person depositing the native asset into the account would need to cover
this protocol deposit. But this would actually prevent the account addresses from being used for
some of the use cases discussed in the [Motivation section](#motivation-why-is-this-cip-necessary).
Consider if a wallet was charging 0.1 ADA per transaction and decides to accept a stablecoin as
payment instead. The protocol deposit could be more than 1 ADA which is 10x the amount the wallet
wanted to charge! Users will not pay the fees in stablecoins if using ADA instead is 10x cheaper!

So the goal is to prevent dusting attacks while still allowing micropayments using non-ADA assets.
That is why the whitelist is used. The account address owner covers the protocol deposit for the native
assets they are interested in and now users can just deposit those native assets without having to
also cover a protocol deposit. The account address owner would not be able to cover the protocol
deposit if they did not know which native assets would be deposited ahead of time, so this approach
only works with a whitelist.

## Path to Active

These changes require a new plutus and ledger version.

### Acceptance Criteria
- [ ] These rules included within an official Plutus and Ledger version, and released via a major hard fork.
      
### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve utility of
account addresses.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
