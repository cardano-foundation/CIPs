---
CIP: 159
Title: Account Address Enhancement
Category: Ledger
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
    - George Flerovsky <george.flerovsky@gmail.com>
Implementors: N/A
Discussions: 
    - https://github.com/cardano-foundation/CIPs/pull/1061
    - https://github.com/IntersectMBO/cardano-ledger/issues/5474
Created: 2025-07-16
License: CC-BY-4.0
---

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
now, the `minUTxOValue` network parameter (now called `utxoCostPerByte`) disallows UTxOs with less
than ~1 ADA. So if the wallet just had the user send the money to them directly, **the smallest fee
they could charge is ~1 ADA**. When the average transaction fee is only about [0.39
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

> [!IMPORTANT]
> In order for direct deposits to actually be useful, *partial withdrawals are a fundamental
> requirement*. To see why, imagine a wallet charges a 0.1 ADA fee per transaction and these
> transactions are submitted every 30 seconds. Currently, the ledger rules require the wallet to
> withdraw the full balance in the account address. Let's say when the wallet submits the withdrawal
> transaction, the balance is 100 ADA. While this transaction is sitting in the mempool, another
> user directly deposits another 0.1 ADA into the wallet's account address. Now the wallets
> transaction in the mempool is *not* withdrawing the full amount and will fail phase 1 validation!
> Without partial withdrawals, whether the wallet will actually be able to access the assets in the
> account will depend on luck!

### Cheaper Batchers/Aggregators

Most batcher/aggregator networks charge at least 1 ADA. For some, the reason is the `minUTxOValue`
requirement. If it was actually possible to charge smaller fee amounts, Cardano's DeFi would be much
cheaper!

### Multi-Asset Cardano Treasury

Cardano's Treasury account is currently only allowed to hold ADA. However, it would be more fiscally
responsible for the Treasury to hold a basket of assets. The basket would diversify the risk of
price fluctuations and ensure that important protocol developments can continue despite price shocks
in any particular asset class.

> [!NOTE]
> This CIP only lays *some* of the groundwork for a Cardano Multi-Asset Treasury.

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
  - *Protocol Deposit* will refer to the deposits required by the protocol for registration (either
  delegation registration or whitelist registration).
  - *Direct Deposit* will refer to assets being sent to an account address.

### Enable Direct Deposits

The ledger rules currently disallow directly depositing assets into account addresses. This
restriction will be lifted to support direct deposits. The transaction balancing rules will need to
be updated to consider these direct deposits.

**Direct depositing into an account address does not require a witness from the receiving account.**
In other words, the receiving staking script does *not* need to be executed. This behavior mirrors
how UTxOs can be created at script addresses without having to execute the spending script.
[CIP-160](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0160) could enable requiring a
witness for direct deposits as an opt-in feature.

> [!IMPORTANT]
> In order to support direct deposits, the account address must be registered.

By default, only direct deposits of ADA are supported. Pre-existing registered account addresses
will be automatically upgraded to support direct deposits of ADA through a hardfork-combinator
event. 

Users will be able to submit a new certificate event (`stake_credential_adjust_whitelist`), which will
initialize the balances of certain native assets (listed in the certificate) at an account address,
starting all of the balances at zero. After these balances are initialized, users will be able to
direct-deposit those native assets into that account.

The set of initialized balances at an account also acts as a **whitelist** on the native assets
allowed at the account. Direct deposits of other native assets into the account will be rejected by
the ledger rules, except for ADA, which can always be deposited into any Cardano account.

> [!IMPORTANT]
> We implement this by using the new `AccountValue` type, which is similar to `Value` but prevents adding or
> removing assets in the `AccountValue`. You can only increase or decrease the asset quantities. If a
> transaction tries directly depositing a native asset that is not found in the `AccountValue`, it
> will fail phase 1 validation.

The only way to alter which native assets are found in the `AccountValue` is through another
dedicated certificate event. The new certificate is outlined below:

```cddl
add_to_whitelist = multiasset
remove_from_whitelist = multiasset

; stake_credential - account that will have the whitelist adjusted
; delta_coin - change in deposit from what the current deposit is in the system
;              it can be negative (in case whitelist shrinks in size) or
;              positive (in case when the size is increased)
; add_to_whitelist - multiassets to be added to the whitelist
; remove_from_whitelist - multiassets to be removed from the whitelist
stake_credential_adjust_whitelist = 
  (19, stake_credential, delta_coin, add_to_whitelist, remove_from_whitelist)

certificate = 
  [  stake_registration
  // stake_deregistration
  // stake_delegation
  ...
  // stake_credential_adjust_whitelist
  ]
```

The `stake_credential_adjust_whitelist` certificate is an *idempotent* insert/remove operation on
the `AccountValue` whitelist. Note a few important points:

1. Removing an asset from the whitelist requires withdrawing all of that asset from the account in
   the same transaction.
2. When an asset is added to the whitelist, it is not possible to direct deposit that asset in the
   same transaction ([CIP-118](https://github.com/cardano-foundation/CIPs/pull/862) can be used to
   get around this restriction: one sub-tx updates the whitelist while a subsequent sub-tx makes the
   direct deposit.)
3. You cannot add and remove the same asset in one transaction (i.e., the `add_to_whitelist` and
   `remove_from_whitelist` fields cannot intersect).

The benefits of this idempotent diffing approach are four-fold:

1. **Proof of Inclusion/Exclusion:** The `stake_credential_adjust_whitelist` can be used to assert
   that an asset is or is not present in the whitelist.
2. **Large Whitelists:** A large whitelist can be built up over several transactions which enables
   whitelists that are larger than the transaction's size limit.
3. **Efficiency:** Updating only part of a whitelist is significantly cheaper than having to
   re-certify the entire whitelist every time.
4. **Improved Decentralized Governance:** It enables breaking up the approval process of a
   whitelist into digestible pieces. If a community could only vote on the *full* whitelist, it
   could be rejected just because one asset in the whitelist is contentious. This approach enables
   voting on each asset independently.

Crucially, since the `AccountValue` will take up space in memory, it must be accompanied with an
extra protocol deposit that is proportional to the size of the `AccountValue`. This extra protocol
deposit must be paid in the transaction using the `stake_credential_adjust_whitelist`. A new
parameter `accountWhitelistCostPerByte` will be needed.

> [!NOTE]
> With UTxOs, the minUTxO protocol deposit is paid by the creator of the UTxO. With account
> addresses, the `AccountValue` protocol deposit will be paid upfront by the address owner. This is
> what enables the micropayments discussed in the [Motivation section](#motivation-why-is-this-cip-necessary).

For this to work, the transaction representation needs a new direct deposit field:

```cddl
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
>    distinguish between direct deposits and withdrawals for the `ScriptPurpose`.
>
> Adding a separate field is the better approach.

Plutus scripts will be able to see the direct deposits occuring in the transaction as part of their
`ScriptContext`. See the [New Plutus Script Context section](#new-plutus-script-context).

> [!IMPORTANT]
> The direct deposits are only the diff! If the account currently has 100 ADA and the transaction is
> direct depositing another 0.1 ADA, the transaction only needs to specify 0.1 ADA.

### Partial Withdrawals and Native Asset Withdrawals

The ledger rules *must* be changed to allow withdrawing any amount between 0 and the current
balance. 

> [!IMPORTANT]
> For all withdrawals, partial or full, the pre-existing `Withdraw` purpose will be used. We do not
> need a dedicated purpose for partial withdrawals.

To enable support for withdrawing native assets from account addresses, the representation of
withdrawals inside transactions needs to be updated:

```cddl
; Old representation.
withdrawals = {+ reward_account => coin}

; New representation.
withdrawals = {+ reward_account => value} ; replaced `coin` with `value`
```

> [!IMPORTANT]
> Partial withdrawals will only be possible in transactions *without* plutus v1-v3 scripts. However,
> [CIP-118](https://github.com/cardano-foundation/CIPs/pull/862) can help here by isolating the
> partial withdrawal in a sub-tx.

> [!IMPORTANT]
> When CIP-118 is implemented, sub-txs can deposit/withdraw from the same account. If this is
> naively supported, it can *look* like native assets are minted out of thin air. For example, if
> the first sub-tx withdraws 1 million ADA and the second sub-tx deposits 1 million ADA, the overall
> transaction is properly balanced and no ADA is actually minted (the value cancels out), but plutus
> scripts inside the sub-txs can possibly be tricked. To prevent these *Phantom Asset* attacks,
> transactions can only withdraw funds that exist in the account *before* the overall transaction
> is run. This means later sub-txs cannot withdraw assets that were deposited by prior sub-txs in
> the same overall transaction. This restriction will be enforced as part of Phase 1 Validation.

### Account Balance Intervals

Transactions can specify account balance intervals similarly to how time intervals are set. In order
for the transaction to be phase 1 valid, the actual balance for the associated asset in the account
*must* fall within the specified interval. The transaction representation is shown below:

```cddl
; We don't want to allow arbitrary precision intervals because it would make
; costing difficult so we constrain them to be 8-byte integers. 
balance_bound = uint .size 8

account_balance_intervals = 
  {+ reward_account => 
      {+ policy_id => 
          {+ asset_name => 
               [ inclusive_lower_bound: balance_bound, exclusive_upper_bound: balance_bound / null ]  /
               [ inclusive_lower_bound: balance_bound / null, exclusive_upper_bound: balance_bound ]
          }
      }
  }

transaction_body = 
  {   0  : set<transaction_input>         
  ,   1  : [* transaction_output]      
  ...
  , ? 24 : account_balance_intervals ; new field
  }
```

As the representation shows, the transaction submitter can specify intervals for different assets
inside a given account address. In addition to this, there are a few important behaviors that need to
be mentioned:

1. Using the account balance interval does *not* require a witness from the associated credential.
2. To declare that a certain asset in the `AccountValue` has a specific balance of `n`, the asset's
   balance interval must be set to `[n, n+1)`.
3. If the account balance interval is used for an asset not supported in the current whitelist, the
   transaction will fail *Phase 1 Validation*.

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
  { balance :: !(CompactForm (AccountValue era))
  -- ^ Current multi-asset balance of the account.
  , deposit :: !(CompactForm Coin)
  -- ^ Total deposit amount from the staking credential registration *and* the account whitelist.
  , stakePoolDelegation :: !(StrictMaybe (KeyHash 'StakePool))
  , dRepDelegation :: !(StrictMaybe DRep)
  }
```

There are a few important points to notice:

1. The `deposit` field holds *both* the stake credential registration deposit *and* the whitelist
   registration deposit.
2. The `balance` map *is the whitelist*. Therefore, direct deposits/withdrawals can only
   increase/decrease the `Integer`; only the `stake_credential_adjust_whitelist` can add/remove
`PolicyID`s or `AssetName`s from the map. If an asset in the whitelist has no balance, the
`Integer` should be set to `0`.

> [!IMPORTANT]
> The required protocol deposit for the whitelist registration will be proportional to the in-memory
> representation of the multi-assets in the whitelist. The calculation can be similar to the
> `minUTxOValue` calculation, but it should get separate protocol parameters so that the
> whitelist costing can be changed independently to the `minUTxOValue` costing.

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
  , txInfoWdrl                  :: Map Credential AccountValue -- ^ Upgraded field.
  , txInfoValidRange            :: POSIXTimeRange
  ... 
  , txInfoDirectDeposits        :: Map Credential AccountValue -- ^ New field.
  , txInfoBalanceIntervals      :: Map Credential (Map PolicyID (Map AssetName BalanceInterval)) -- ^ New field. 
  }
```

> [!IMPORTANT]
> In order for contemporary DeFi to be able to charge lower fees with this CIP, **direct deposits
> must be supported in transactions using smart contracts from prior plutus versions.** To enable
> this backporting without introducing security vulnerabilities in older smart contracts, older
> plutus scripts will be supported in the top-level of a nested transaction
> ([CIP-118](https://github.com/cardano-foundation/CIPs/pull/862)). Then these new transaction
> fields can be isolated inside a sub-transaction.

### Phased Delivery

In order to expedite delivery of this CIP, development will be broken over two phases/eras. 

#### Phase 1: ADA Support

This phase only adds support for ADA because it will be very quick to implement. ADA support is
enough to enable wallets, DEX aggregators, and DePIN infrastructure to offer lower fees since they
are all forced to charge *~1 ADA* due to the `minUTxOValue` requirement.

**Ledger Rule Changes**
1. Deposit ADA into account addresses.
2. Partial withdrawals from account addresses in sub-transactions, or in a top-level transaction
   but only when plutus v1-v3 scripts are not used in it.
3. Account balance intervals validated as part of *Phase 1 Validation*.

**CDDL Changes**
```cddl
; The withdrawals field is left unchanged.

; Same definition as current withdrawals.
direct_deposits = {+ reward_account => coin}

account_balance_intervals = 
  { + reward_account => 
        [ inclusive_lower_bound: coin, exclusive_upper_bound: coin / null ]  /
        [ inclusive_lower_bound: coin / null, exclusive_upper_bound: coin ] 
  }

transaction_body = 
  {   0  : set<transaction_input>         
  ,   1  : [* transaction_output]      
  ...
  , ? 23 : direct_deposits ; new field
  , ? 24 : account_balance_intervals ; new field
  }
```

**Plutus Script Context**

The plutus script context will be pre-emptively upgraded to support the fields needed in the second
delivery phase. This way the features can be turned on with a hardfork and plutus scripts written
for the first delivery phase can immediately take advantage of the new features without having to be
recompiled.

```haskell
data TxInfo = TxInfo
  { txInfoInputs                :: [TxInInfo]
  , txInfoReferenceInputs       :: [TxInInfo]
  , txInfoOutputs               :: [TxOut]
  , txInfoFee                   :: Value
  , txInfoMint                  :: Value
  , txInfoTxCerts               :: [TxCert]
  , txInfoWdrl                  :: Map Credential AccountValue -- ^ Upgraded field.
  , txInfoValidRange            :: POSIXTimeRange
  ... 
  , txInfoDirectDeposits        :: Map Credential AccountValue -- ^ New field.
  , txInfoBalanceIntervals      :: Map Credential (Map PolicyID (Map AssetName BalanceInterval)) -- ^ New field. 
  }
```

> [!IMPORTANT]
> In order for the community to get the benefits from this CIP, plutus v1-v3 scripts must be
> allowed in transactions that contain the new `direct_deposits` field. To accomplish this,
> plutus v1-v3 scripts will be allowed to run inside the top-level of a nested transaction
> ([CIP-118](https://github.com/cardano-foundation/CIPs/pull/862)). Then the `direct_deposits`
> field can be safely isolated inside a sub transaction.

#### Phase 2: Multi-Asset Support

This phase will add support for native asset deposits and whitelist certificates which will pave the
way for a Cardano Multi-Asset Treasury, simplify L2 reserve management, and enable more
decentralized voting mechanisms.

**Ledger Rule Changes**
1. Deposit native assets into account addresses.
2. Withdraw native assets from account addresses.
3. Whitelist certificates (and extra protocol deposits) for account addresses.

**New Protocol Parameter**
- `accountWhitelistCostPerByte` which is similar to the current `utxoCostPerByte`.

**CDDL Changes**
```cddl
add_to_whitelist = multiasset
remove_from_whitelist = multiasset

; stake_credential - account that will have the whitelist adjusted
; delta_coin - change in deposit from what the current deposit is in the system
;              it can be negative (in case whitelist shrinks in size) or
;              positive (in case when the size is increased)
; add_to_whitelist - multiassets to be added to the whitelist
; remove_from_whitelist - multiassets to be removed from the whitelist
stake_credential_adjust_whitelist = 
  (19, stake_credential, delta_coin, add_to_whitelist, remove_from_whitelist)

; New representation: replaced `coin` with `value`.
withdrawals = {+ reward_account => value}

; New representation: replaced `coin` with `value`.
direct_deposits = {+ reward_account => value}

; New representation: replaced `coin` with `balance_bound` and enables individual
; intervals for each asset.
balance_bound = uint .size 8
account_balance_intervals = 
  {+ reward_account => 
      {+ policy_id => 
          {+ asset_name => 
               [ inclusive_lower_bound: balance_bound, exclusive_upper_bound: balance_bound / null ]  /
               [ inclusive_lower_bound: balance_bound / null, exclusive_upper_bound: balance_bound ]
          }
      }
  }
```

**New `AccountState`**
```haskell
data AccountState era
  = AccountState
  { balance :: !(CompactForm (AccountValue era))
  -- ^ Current multi-asset balance of the account.
  , deposit :: !(CompactForm Coin)
  -- ^ Total deposit amount from the staking credential registration *and* the account whitelist.
  , stakePoolDelegation :: !(StrictMaybe (KeyHash 'StakePool))
  , dRepDelegation :: !(StrictMaybe DRep)
  }
```

## Rationale: how does this CIP achieve its goals?

This CIP is able to upgrade Cardano's account addresses to full accounts *without* sacrificing local
determinism and *without* introducing the issues seen with Ethereum-style accounts. The reasons for
this are based on what this CIP *does not* enable, more than on what it does enable. The most
important things are:

- This CIP *does not* enable submitting transactions without UTxO inputs.
- This CIP *does not* enable attaching datums to account addresses.
- This CIP *does not* enable phase-2 scripts to view the **exact** account balance, except when the
balance interval is set to the exact value (making this feature *opt-in*).
- This CIP *does not* enable directly depositing arbitrary native assets into account addresses.
Only whitelisted native assets are allowed (i.e. native assets with balances initialized at the
account).

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

Enforcing plutus scripts to view the account's exact balance would require sacrificing Cardano's
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
malicious person can create worthless tokens and create UTxOs with *only* these assets or create
UTxOs with no assets at all. When block producers try to validate transactions, they need to load
the UTxOs into memory. If the size of these UTxOs are not somehow tied to real world resource
constraints, the malicious actors can cause block producer memory usages to explode with these
worthless/valueless UTxOs taking up space. This is effectively a DDoS attack. By requiring every
UTxO to contain a minimum of ADA, a malicious actor is only able to cause this attack if they
actually have the required amount of ADA to back the memory usage required to process the native
asset values.

If account addresses could accept arbitrary native assets like UTxOs, they would be susceptible to
the same dusting attacks. A first thought might be to have a `minUTxOValue`-like protocol deposit
for account addresses - the person depositing the native asset into the account would need to cover
this protocol deposit. But this would actually prevent the account addresses from being used for
some of the use cases discussed in the [Motivation section](#motivation-why-is-this-cip-necessary).
Consider if a wallet was charging 0.1 ADA per transaction and decides to accept a stablecoin as
payment instead. The protocol deposit could be more than 1 ADA which is 10x the amount the wallet
wanted to charge! Users will not pay the fees in stablecoins if using ADA instead is 10x cheaper!

So the goal is to prevent dusting attacks while still allowing micropayments using non-ADA assets.
That is why the whitelist is used. The account address owner covers the protocol deposit for the
native assets they are interested in and now users can direct deposit those native assets into the
account without having to also cover a protocol deposit. The account address owner would not be able
to cover the protocol deposit if they did not know which native assets would be deposited ahead of
time, so this approach only works with a whitelist.

## Path to Active

### Acceptance Criteria
- [ ] These rules included within an official Plutus and Ledger version, and released via a major hard fork.
- [ ] These changes have acknowledgement from infrastructure parties (e.g., wallets, indexers,
off-chain library maintainers, smart contract language maintainers, L2 builders, etc.).
      
### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve utility of
account addresses.
- [ ] Each phase is implemented either together or in separate Cardano eras:
    - [ ] Delivery Phase 1: ADA Support
    - [ ] Delivery Phase 2: Multi-Asset Support

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
