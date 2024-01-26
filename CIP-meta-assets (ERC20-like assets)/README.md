---
CIP: _???
Title: meta-assets (ERC20-like assets)
Category: Tokens
Status: Proposed
Authors:
    - Michele Nuzzi <michele.nuzzi.204@gmail.com>
    - Harmonic Laboratories <harmoniclabs@protonmail.com>
    - Matteo Coppola <m.coppola.mazzetti@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-01-14
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta                   | For meta-CIPs which typically serves another category or group of categories.
- Reward-Sharing Schemes | For CIPs discussing the reward & incentive mechanisms of the protocol.
- Wallets                | For standardisation across wallets (hardware, full-node or light).
- Tokens                 | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata               | For proposals around metadata (on-chain or off-chain).
- Tools                  | A broad category for ecosystem tools not falling into any other category.
- Plutus                 | Changes or additions to Plutus
- Ledger                 | For proposals regarding the Cardano ledger
- Catalyst               | For proposals affecting Project Catalyst / the Jörmungandr project

-->

# CIP-XXXX: meta-assets (ERC20-like assets)
<!-- A reminder of the document's number & title, for readability. -->

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
This CIP proposes a standard that if adopted would allow the same level of programmability of other ecosistems at the price of the token true ownership.

This is achieved imitating the way the account model works laveraging the UTxO structure adopted by Cardano.

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

This CIP proposes a solution at the Cardano Problem Statement 3 ([CPS-0003](https://github.com/cardano-foundation/CIPs/pull/382/files?short_path=5a0dba0#diff-5a0dba075d998658d72169818d839f4c63cf105e4d6c3fe81e46b20d5fd3dc8f)).

If adopted it would allow to introduce the programmability over the transfer of tokens (meta-tokens) and their lifecycle.

The solution proposed includes (answering to the open questions of CPS-0003):

1 and 2) very much like account based models, wallets supporting this standard will require to know the address of the smart contract (validator)

3) the soultion can co-exsist with the exsiting native tokens

4) the implementaiton is possible without hardfork since Vasil

5) optimized implementations should not take significant computation, especially on transfers.

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. -->

In the specifiaction we'll use the haskell data type `Data`:
```hs
data Data
    = Constr Integer [Data]
    | Map [( Data, Data )]
    | List [Data]
    | I Integer
    | B ByteString
```

and we'll use the [plu-ts syntax for structs definition](https://pluts.harmoniclabs.tech/docs/onchain/Values/Structs/definition#pstruct) as an abstraction over the `Data` type.

The core idea of the implementation is to emulate the ERC20 standard; where tokens are entries in a map with addresses (or credentials in our case) as key and integers (the balances) as value. ([see the OpenZeppelin implementation for reference](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/9b3710465583284b8c4c5d2245749246bb2e0094/contracts/token/ERC20/ERC20.sol#L16));

Unlike the ERC20 standard; this CIP:

- allows for multiple entries with the same key (same credentials can be used for multiple accounts)
- DOESN'T include an equivalent of the `transferFrom` method; if needed it can be added by a specific implementation but it won't be considered part of the standard.

> **NOTE**
>
> the UTxO model allows for multiple transfers in one transaction
>
> this would allow for a more powerful model than the account based equivalent but implies higher execution costs
>
> whith the goal of keeping the standard interoperable and easy to understand and implement
> in this first implementation we restricts transfers from a single account to a single account
>
> if necessary; this restriction might be dropped in a future version of the CIP 



The implementation requires

- a parametrized minting policy to validate the creation of new accounts (in this CIP also referred as `accountFactory`)
- a spending validator to manage the accounts ((in this CIP also referred as `accountManager`))

### standard data types used

We'll need to use some data types as defined in the script context;

```ts
const PTxId = pstruct({
    PTxId: { txId: bs }
});

const PTxOutRef = pstruct({
    PTxOutRef: {
        id: PTxId.type,
        index: int
    }
});

const PCredential = pstruct({
    PPubKeyCredential: { pkh: bs },
    PScriptCredential: { valHash: bs },
});

const PCurrencySymbol = palias( bs );
```
which are equivalent to the data:
```hs
-- PTxId
Constr 0 [ B txId ]

--- PTxOutRef
Constr 0 [ PTxId, I index ]

-- PPubKeyCredential
Constr 0 [ B pkh ]

-- PScriptCredential
Constr 1 [ B valHash ]

-- PCurrencySymbol
B currencySym
```

## `accountFactory` (minting policy)

The `accountFactory` contract is responsabile of validating the creation of new accounts.

### validation logic

If the creation of the account is considered valid (the minting policy suceeds)
it should result in a single minted asset going to an hard-coded (parametrized) `accountManager` contract.

The standard doesn't include a specification on the policy in case of burning but it is suggested to always allow for the assets burn.

the data needed form the `ScriptContext` includes teh following fields:

- `inputs`
- `output`
- `mint`

used as follows:

- all the transaction inputs MUST NOT include any tokens having the same currency symbol of the `accountFactory` minting policy;
optionally a specific implementation might require a fixed number of inputs (eg. a single input) for performance reasons.

- when minting assets only a single token should be minted (indipendently from the number of inputs)
- the only asset minted MUST have an unique asset name (we suggest using the output of `[(builtin sha2_256) [(builtin serialiseData) fstUtxoRef]]` where `fstUtxoRef` is the utxo reference (or `PTxOutRef`) of the very first input of the transaction)

- the asset minted MUST be included in an output of the transaction being validated going to the hard-coded `accountManager` validator.

- the output going to the `accountManager` validator MUST implement the following checks (in addition to the presence of the minted asset):
    - the address' payment credential MUST have `ScriptCredential` constructor (constructor index `1`) and validator hash MUST equal the hard coded `accountManager` hash
    - the value attached to the UTxO must only have 2 entries (ADA and minted token) to prevent DoS by token spam.
    - the output datum MUST:
        - be constructed using the `InlineDatum` consturctor (consturctor index `2`)
        - have datum value with the [`Account`](#Account) structure (explained below) with the foeeowing fields:
            - amount: `0`
            - currencySym: currency symbol of the `accountFactory` minting policy
            - credentials: the first resolved input address credentials (both public key hash and validator hash supported)
            - state: no restrictions (up to the specific implementaiton).

optionally a specific implementation might require a fixed number of outputs (eg. a single output) for performance reasons.

## `accountManager` (spending validator)

The `accountManager` contract is responsabile of managing exsiting accounts and their balances.

This is done using some standard redeemers and optionally implementation specfic ones.

### `Account`

The `Account` data type is used as the `accountManager` datum; and is defined as follows:

```ts
const Account = pstruct({
    Account: {
        amount: int,
        credentials: PCredential.type,
        currencySym: PCurrencySymbol.type,
        state: data
    }
});
```

### `AccounManagerRedeemer`

The `AccounManagerRedeemer` is used to comunicate the contract the intention with which the utxo is being spent.

It includes 4 standard redeemers; none of which is meant to manipulate the state of the spending account.

for this reason a specific implementation will likely have more than 4 possible redeemers that will not be considered standard
(eg. a wallet implementing an interface SHOULD NOT depend on the exsistence of these additional redeemers).

The minimal `AccounManagerRedeemer` is:

```ts
const AccounManagerRdmr = pstruct({
    Mint: { // or Burn if `amount` is negative
        amount: int
    },
    Transfer: {
        to: PCredential.type,
        amount: int
    },
    Receive: {},
    ForwardCompatibility: {}
});
```

The validation logic is different for each redeemer.

#### Common operations and values

Before proceeding with the redeemers validation logic here are some common operations and values between some of the redeemers.

##### `ownUtxoRef`

the `accountManager` contract is meant to be used only as spending validator.

As succ we can extract the utxo being spent from the `ScriptPurpose` when constructed with the `Spending` contstructor and fail for the rest.

```ts
const ownUtxoRef = plet(
    pmatch( ctx.purpose )
    .onSpending(({ utxoRef }) => utxoRef)
    ._( _ => perror( PTxOutRef.type ) )
);
```

##### `validatingInput`

is the input with `utxoRef` field equivalent to `ownUtxoRef`

##### `ownCreds`

from the `validatingInput`:

```ts
validatingInput.resolved.address.credential
```

##### `ownValue`

from the `validatingInput`:

```ts
validatingInput.resolved.value
```


##### `isOwnOutput`

given an output; we recongize the output as "own" if the attached credantials are equivalent to `ownCreds` 
and the attached value includes an entry for the `currencySym` field in the specified in the datum.

```ts
const isOwnOutput = plet(
    pfn([ PTxOut.type ], bool )
    ( out => 
        out.address.credential.eq( ownCreds )
        // a single account manager contract might handle multiple tokens
        .and(
            out.value.some( ({ fst: policy }) => policy.eq( account.currencySym ) )
        ) 
    )
);
```

##### `isOwnInput` 

an input is "own" if the resolved field is "own";

```ts
const isOwnInput = plet(
    pfn([ PTxInInfo.type ], bool )
    ( input => isOwnOutput.$( input.resolved ) )
);
```

##### `isOwnCurrencySym`

given an asset policy we might want to know if it is the one being validated.

this is done by comparing it with the one specified in the datum field

```ts
const isOwnCurrSym = plet( account.currencySym.eqTerm );
```

##### `outIncludesNFT`

given a transaction output is useful to check if the value includes the NFT generated from the `accountFactory`;

this is done by checking that at least one of the attached value's entry satisfies `isOwnCurrencySym` for the policy.

```ts
 const outIncludesNFT = plet(
    pfn([ PTxOut.type ], bool )
    ( out => out.value.some( entry => isOwnCurrSym.$( entry.fst ) ) )
);
```

##### `ownOuts`

transaction outputs filtered by `isOwnOutput`;

##### `ownInputs`

transaction inputs filtered by `isOwnInput`;

##### updating the `Account` datum

Between all the standard redeemers it must be checked that the datum fields `credentials`, `currencySym` and `state` remain unchanged compared to the current datum.

This might not be true for any implementation specific additional redeemer.

#### `Mint`

the contract being called using the `Mint` redeemer MUST suceed only if the following conditions are met:

> **NOTE** 
>
> we use `mint.amount` to describe the value of the `amount` field included in the `Mint` redeemer
> and `account.amount` to describe the value of the `amount` field included in the input `Account` datum.

- only a single input is comes from the `accountManager` validator;

- the value of the input coming from the `accountManager` MUST include an entry with `PCurrencySymbol`
equivalent to the one specified in the `currencySym` field of the `Account` datum.

- the minted value in the transaction (`ctx.tx.mint`) MUST NOT include any entry with `PCurrencySymbol`
equivalent to the one specified in the `currencySym` field of the `Account` datum (aka. no accounts are created)

- to prevent DoS by token spamming the output going back to the `accountManager` must have at most length 2.

- there MUST be an output going back to the `accountManager` contract with the following properties
    - it MUST have an entry for the `PCurrencySymbol` specified in the `currencySym` field of the `Account` (aka. NFT is preserved)
    - the output datum MUST be constructed using the `InlineDatum` constructor
    - the datum fields `credentials`, `currencySym` and `state` must be unchanged compared to the current datum.
    - the datum field `account.amount` should change based on `mint.amount` as described below.

- if the `mint.amount` is positive the output datum MUST 
    be equal to the sum of `account.datum` and `mint.datum`

- if the `amount` field included in the `Mint` redeemer is negative 
the contract MUST FAIL if the sum of `mint.amount` and `account.amount` is strictly less than `0` (aka. burning more assets than how much the `Account` holds);
otherwhise it should check for the output datum `amount` field to be equal to the result of the sum

#### `Transfer`

The `Transfer` redeemer is used to pay an other account in the same account manager.

When used as redeemer the contract checks for the following conditions to be true;

- `ownInputs` to be of lenght `2`

- the receiver input (the `ownInput` with different `utxoRef` of the `validatingInput`)
being spent with `Receive` redeemer

- the sender input (`validatinInput`) must have the NFT according to `account.currencySym` (the input is valid)

- the output with the sender's credentials must preserve the NFT

- the account fields `credentials`, `currencySym` and `state` are unchanged between sender input datum and sender output datum

- the account fields `credentials`, `currencySym` and `state` are unchanged between receiver input datum and receiver output datum

- `ownOuts` to be of lenght `2`

- every member of `ownOuts` must have at most 2 entries to prevent DoS by token spam.

- the input sender's amount field is greather or equal than the redeemer amount (`transfer.amount`)

- the output sender's amount field is equal to the input one minus `transfer.amount`

- the output receiver's amount field is equal to the input one plus `transfer.amount`

- the sender singned the transaction (included in `ctx.tx.signatories` if a `PPubKeyHash` or included a script input if a `PValidatorHash`)

any additional check can be made based on the `account.state` (implementation specific)

#### `Receive`

- `ownInputs` to be of lenght `2`

- the sender input (the `ownInput` with different `utxoRef` of the `validatingInput`)
being spent with `Transfer` redeemer

- in the sender input `Transefer` redeemer the `to` field is equal to the `account.credentials` (where `account` is the receiver datum)

> **NOTE**
>
> the sender input being an `ownInputs` element and being spent with `Transfer` redeemer 
> implies that the transfer calculation is running in that validation
>
> hence we don't need to perform the same calculation here

#### `ForwardCompatibility`

For the current version this redeemer SHOULD always fail.

The main purpose of the redeemer is to avoid breaking compatibilities for addtional implementation specific redeemers

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

- having at least one instance of the smart contracts described on:
    - mainnet
    - preview testnet
    - preprod testnet
- having at least 2 different wallets integrating meta asset functionalities, mainly:
    - displayning balance of a specified meta asset if the user provides the address of the respecive account manager contract
    - transaction creation with `Transfer` redeemers

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if not applicable. -->

- [x] [PoC implementation](https://github.com/HarmonicLabs/erc20-like)
- [x] [showcase transactions](https://github.com/HarmonicLabs/erc20-like)
- [ ] wallet implementation 

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. -->

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
