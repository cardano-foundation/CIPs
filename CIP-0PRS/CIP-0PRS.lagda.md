---
Title: Ouroboros Peras - Faster Settlement
CIP: ?
Category: Consensus
Status: Proposed
Authors:
  - Arnaud Bailly <arnaud.bailly@iohk.io>
  - Brian W. Bush <brian.bush@iohk.io>
  - Yves Hauser <yves.hauser@iohk.io>
  - Hans Lahe <hans.lahe@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/872
Created: 2024-08-06
License: Apache-2.0
---


> [!NOTE]
> A "Consensus" category must be created by a new CIP before this CIP can be submitted within that category.
>
> Existing categories:
> 
> - Meta     | For meta-CIPs which typically serves another category or group of categories.
> - Wallets  | For standardisation across wallets (hardware, full-node or light).
> - Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
> - Metadata | For proposals around metadata (on-chain or off-chain).
> - Tools    | A broad category for ecosystem tools not falling into any other category.
> - Plutus   | Changes or additions to Plutus
> - Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
> - Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

## Abstract

We propose Ouroboros Peras, an enhancement to the Ouroboros Praos protocol that introduces a voting layer for fast settlement. It is adaptively secure, supports dynamic participation, and integrates self healing. Voting provides a “boost” to blocks that receive a quorum of votes, and this dramatically reduces the roll-back probability of the boosted block and its predecessors. Fast settlement occurs in the presence of adversaries with up to one-quarter of the stake, but Praos-like safety is maintained when adversaries control more than that amount of stake. In fact, the protocol enters a “cool-down period” of Praos-like behavior when adversaries prevent voting quorums; that cool-down period is exited only when the chain has healed, achieves chain quality, and reaches a common prefix. For realistic settings of the Peras protocol parameters, blocks can be identified post-facto as being settled vs rolled-back (with overwhelming probability) after as little as two minutes. This enables use cases like partner-chains and bridges where high certainty for the status of a transaction is required in a brief time. The protocol requires the implementation of a vote-diffusion layer, certificates that aggregate votes, and one minor addition to the contents of a block.

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

* Define clearly what settlement is (and how it differs from finality)
  * Checkout https://docs.google.com/spreadsheets/d/1s_LfDQ4Qg3BArMgr6GskGGzG_Ibg-VbPdMmlRWvZ75o/edit#gid=431199162
  * See Peter Gazi comment -> settlement as a probability or measure of risk to be taken into account by users making transactions
  * Hans's take: Settlement occurs before finality. Settled transactions can be reversible, finalized Txs are irreversible. The difference is in the degree of certainty. A settled Tx is considered valid and is likely to be included in the final, immutable history of blockchain. Depending on the specific use case, different levels of certainity might be required - i.e. a multi-day finality could be a feature of a system. It seems that in traditional finance the long settlement time is often used as an escrow - e.g. for the the buyer to verify the purchase, or for regulatory compliance to be reached. 
 
* Explain settlement on Cardano with Ouroboros Praos
  * Include data -> settlement probabilities (is this sensitive?)
* Explain the required changes to Praos *maybe in terms of current limitations of Praos*
    * Low cost solution
    * "Overlay" protocol, adding incremental behaviour, no fundamental change to Praos
* Distinguish from orthogonal protocol upgrades such as Genesis, Leios, etc.
* Worst-case vs. optimistic case
    * Praos is geared towards worst case but Peras takes advantage of the opportunities afforded by the optimistic or average case (eg. when things are fine, go faster)

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

### Non-normative overview of the Peras protocol

The following informal, non-normative, pseudo-imperative summary of the Peras protocol is provided as an index into the formal, normative Agda specification. Peras relies on a few key concepts:

- The progression of the blockchain's *slots* is partitioned in *rounds* of equal length.
- In each round a *committee of voters* is selected via a sortition algorithm.
- Members of the committee may *vote* for a block in the history of their preferred chain.
- A *quorum* of votes during the same round for the same block is memorialized as a *certificate*.
- A quorum of votes for a block gives that block's weight a *boost*.
- The *weight* of a chain is its length plus the total of the boosts its blocks have received.
- The lack of a quorum in a round typically triggers a *cool-down period* where no voting occurs.
- Relevant vote certificates are typically *recorded* in a block near the start and finish of a cool-down period.
- Certificates *expire* after a specified number of slots if they haven't been included in a block.

> [!TIP]
> - In the above, hyperlink the key terms to the sections defining them in the formal specification.
> - Add a diagram illustrating the operation of Peras.

The protocol keeps track of the following variables, initialized to the values below:

- $C_\text{pref} \gets C_\text{genesis}$: preferred chain;
- $\mathcal{C} \gets \{C_\text{genesis}\}$: set of chains;
- $\mathcal{V} \gets \emptyset$: set of votes;
- $\mathsf{Certs} \gets \{\mathsf{cert}_\text{genesis}\}$: set of certificates;
- $\mathsf{cert}^\prime \gets \mathsf{cert}_\text{genesis}$: the latest certificate seen;
- $\mathsf{cert}^* \gets \mathsf{cert}_\text{genesis}$: the latest certificate on chain.

A *fetching* operation occurs at the beginning of each slot:

- Fetch new chains $\mathcal{C}_\text{new}$ and votes $\mathcal{V}_\text{new}$.
- Add any new chains in $\mathcal{C}_\text{new}$ to $\mathcal{C}$, add any new certificates contained in chains in $\mathcal{C}_\text{new}$ to $\mathsf{Certs}$.
    -  Discard any equivocated blocks or certificates: i.e., do not add them to $\mathcal{C}$ or $\mathsf{Certs}$.
- Add $\mathcal{V}_\text{new}$ to $\mathcal{V}$ and turn any new quorum in $\mathcal{V}$ into a certificate $\mathsf{cert}$ and add $\mathsf{cert}$ to $\mathsf{Certs}$.
    -  Discard any equivocated votes: i.e., do not add the to $\mathcal{V}$.
- Set $C_\text{pref}$ to the heaviest (w.r.t. $\mathsf{Wt}_\mathsf{P}(\cdot)$) valid chain in $\mathcal{C}$.
    -  *If several chains have the same weight, select the one whose tip has the smallest block hash as the preferred one.*
    - Each party $\mathsf{P}$ assigns a certain weight to every chain $C$, based on $C$'s length and all certificates that vote for blocks in $C$ that $\mathsf{P}$ has seen so far (and thus stored in a local list $\mathsf{Certs}$).
    - Let $\mathsf{certCount}_\mathsf{P}(C)$ denote the number of such certificates, i.e., $\mathsf{certCount}_\mathsf{P}(C) := \left| \left\{ \mathsf{cert} \in \mathsf{Certs} : \mathsf{cert} \text{ votes for a block on } C \right\} \right|$.
    - Then, the weight of the chain $C$ in $\mathsf{P}$'s view is $\mathsf{Wt}_\mathsf{P}(C) := \mathsf{len}(C) + B \cdot \mathsf{certCount}_\mathsf{P}(C)$ for a protocol parameter $B$.
- Set $\mathsf{cert}^\prime$ to the certificate with the highest round number in $\mathsf{Certs}$.
- Set $\mathsf{cert}^*$ to the certificate with the highest round number on (i.e., included in) $C_\text{pref}$.

*Block creation* occurs whenever party $\mathsf{P}$ is slot leader in a slot $s$, belonging to some round $r$:

- Create a new block $\mathsf{block} = (s, \mathsf{P}, h, \mathsf{cert}, ...)$, where
    - $h$ is the hash of the last block in $C_\text{pref}$,
    - $\mathsf{cert}$ is set to $\mathsf{cert}^\prime$ if
        - there is no round-$(r-2)$ certificate in $\mathsf{Certs}$, and
        - $r - \mathsf{round}(\mathsf{cert}^\prime) \leq A$, and
        - $\mathsf{round}(\mathsf{cert}^\prime) > \mathsf{round}(\mathsf{cert}^*)$,
        - and to $\bot$ otherwise,
- Extend $C_\text{pref}$ by $\mathsf{block}$, add the new $C_\text{pref}$ to $\mathcal{C}$ and diffuse it.

During *voting*, each party $\mathsf{P}$ does the following at the beginning of each voting round $r$:

- Let $\mathsf{block}$ be the youngest block at least $L$ slots old on $C_\text{pref}$.
- If party $\mathsf{P}$ is (voting) committee member in a round $r$,
    - either
        - : $\mathsf{round}(\mathsf{cert}^\prime) = r-1$ and $\mathsf{cert}^\prime$ was received before the end of round $r-1$, and
        - : $\mathsf{block}$ extends (i.e., has the ancestor or is identical to) the block certified by $\mathsf{cert}^\prime$,
    - or
        - : $r \geq \mathsf{round}(\mathsf{cert}^\prime) + R$, and
        - : $r = \mathsf{round}(\mathsf{cert}^*) + c \cdot K$ for some $c > 0$,
    - then create a vote $v = (r, \mathsf{P}, h,...)$,
    - Add $v$ to $\mathcal{V}$ and diffuse it.

### Normative Peras specification in Agda

The following formal, relational specification for Peras type checks using [Agda 2.6.4.1](https://github.com/agda/agda/tree/v2.6.4.1). The repository [github:input-output-hk/peras-design](https://github.com/input-output-hk/peras-design/tree/main) provides a Nix-based environment for compiling and executing Peras's specification.

> [!TIP]
> - This is based on [github:input-output-hk/peras-design/1afae5e35a6f6e484d87df7926f3cf8d02d10501](https://github.com/input-output-hk/peras-design/commit/1afae5e35a6f6e484d87df7926f3cf8d02d10501).
> - Periodically diff the main branch of that repository against this commit, in order to identify any changes that need to be migrated to this document.

```agda
module CIP-0PRS where
```

> [!CAUTION]
> Rename the module when this file name changes.

Most of the imports come from the [Agda Standard Library 2.0](https://github.com/agda/agda-stdlib/tree/v2.0).

```agda
open import Data.Bool using (Bool; if_then_else_; not; _∧_)
open import Data.Empty using (⊥)
open import Data.Fin using (Fin; pred)
                     renaming (zero to fzero; suc to fsuc)
open import Data.List using (List; any; catMaybes; concat; dropWhile; filter; head; map; sum; []; _∷_; _++_)
                      renaming (length to ∣_∣)
open import Data.List.Membership.Propositional using (_∈_)
open import Data.List.Relation.Unary.All using (All)
open import Data.List.Relation.Unary.Any using (Any; any?; _─_)
                                         renaming (_∷=_ to _∷ˡ=_)
open import Data.Maybe using (Maybe; just; nothing)
open import Data.Nat using (NonZero; Ordering; suc; ℕ; _≤_; _≥_; _>_; _≤?_; _<ᵇ_; _≤ᵇ_; _+_; _∸_; _*_; _/_; _%_)
open import Data.Nat.Properties using (_≟_)
open import Data.Product using (proj₁; proj₂; uncurry; ∃-syntax; _×_; _,_)
open import Data.Sum using (_⊎_)
open import Function.Base using (_∘_)
open import Relation.Binary using (DecidableEquality)
open import Relation.Binary.PropositionalEquality using (_≡_; _≢_; cong)
open import Relation.Nullary using (Dec; no; yes; ¬_; ⌊_⌋)
open import Relation.Nullary.Decidable using (_×-dec_; ¬?)
```

Several additional imports come from the [IOG Agda Prelude](iog-prelude/).

```agda
open import Prelude.AssocList using (AssocList; set; _⁉_)
open import Prelude.DecEq using (DecEq; _==_)
open import Prelude.Default using (Default)
open import Prelude.InferenceRules
```

#### Protocol parameters

The seven *protocol parameters* are natural numbers.

```agda
record Params : Set where
  field
```

The $U$ parameter is the duration of each voting round, measured in slots.

```agda
        U : ℕ
```

The $L$ parameter is the minimum age of a candidate block for being voted upon, measured in slots.

```agda
        L : ℕ
```

The $A$ parameter is the maximum age for a certificate to be included in a block, measured in slots.

```agda
        A : ℕ
```

The $R$ parameter is the number of rounds for which to ignore certificates after entering a cool-down period.

```agda
        R : ℕ
```

The $K$ parameter is the minimum number of rounds to wait before voting again after a cool-down period starts.

```agda
        K : ℕ
```

The $B$ parameter is the extra chain weight that a certificate (a quorum of votes) imparts to a block.

```agda
        B : ℕ
```

The $\tau$ parameter is the number of votes (the quorum) required to create a certificate.

```agda
        τ : ℕ
```

Note that neither the round length nor the cool-down duration may be zero.

```agda
        ⦃ U-nonZero ⦄ : NonZero U
        ⦃ K-nonZero ⦄ : NonZero K
```

#### Network representation

At the protocol level, the only *network parameter* of interest is the diffusion time $\Delta$,  which is the upper limit on the number of slots needed to honestly diffuse a message to all nodes.

```agda
record Network : Set₁ where
  field
    Δ : ℕ
```

#### Slots and rounds

As in Praos, time is measured in *slots*.

```agda
record SlotNumber : Set where
  constructor MkSlotNumber
  field getSlotNumber : ℕ

  next : SlotNumber
  next = record {getSlotNumber = suc getSlotNumber}

open SlotNumber using (getSlotNumber)
```

Each Peras voting *round* consists of $U$ consecutive slots.

```agda
record RoundNumber : Set where
  constructor MkRoundNumber
  field getRoundNumber : ℕ

open RoundNumber using (getRoundNumber)

module _ ⦃ _ : Params ⦄ where
  open Params ⦃...⦄

  StartOfRound : SlotNumber → RoundNumber → Set
  StartOfRound (MkSlotNumber sl) (MkRoundNumber r) = sl ≡ r * U

  rnd : ℕ → ⦃ _ : NonZero U ⦄ → ℕ
  rnd s = s / U

  v-round : SlotNumber → RoundNumber
  v-round (MkSlotNumber s) = MkRoundNumber (rnd s)
```

#### Hashing

The protocol requires a type for the result of hashing data, an empty value for that type, and an equality test for that type.

> [!WARNING]
> I tried to eliminate `ByteString` altogether by postulating `Hash`,
> but it results in an error that requires `Block` to be inductive or
> coinductive.

```agda
postulate
  ByteString : Set
  emptyBS : ByteString
  _≟-BS_ : DecidableEquality ByteString
```

Hashes are represented by a byte string, and most of the protocol's primary data types can be hashed.

```agda
record Hash (a : Set) : Set where
  constructor MkHash
  field hashBytes : ByteString

record Hashable (a : Set) : Set where
  field hash : a → Hash a

open Hashable ⦃...⦄
```

#### Parties

A *party* operates a node and controls its cryptographic keys. Parties are, of course, distinguishable for one another.

```agda
postulate
  PartyId : Set
  _≟-party_ : DecidableEquality PartyId

instance
  iDecEqPartyId : DecEq PartyId
  iDecEqPartyId .DecEq._≟_ = _≟-party_
```

Honest parties follow the protocol's rules, but corrupt parties might choose not to. 

```agda
data Honesty : PartyId → Set where
  Honest : ∀ {p : PartyId} → Honesty p
  Corrupt : ∀ {p : PartyId} → Honesty p
```

The honesty of parties participating in the protocol is represented in this specification.

```agda
PartyTup = ∃[ p ] (Honesty p)

Parties = List PartyTup
```

#### Signatures

The protocol uses standard KES *signatures* (Ed25519) for signing blocks or votes.

```agda
postulate
  Signature : Set
```

#### Slot leadership and committee membership

A *leadership proof* attests a party's slot leadership exactly as it does in Praos. The function `IsSlotLeader` verifies a party's leadership for a particular slot and the function `IsBlockSignature` verifies the validity of a block's signature.

```agda
record Block : Set  -- Blocks will be defined later in this specification.

postulate
  LeadershipProof : Set
  IsSlotLeader : PartyId → SlotNumber → LeadershipProof → Set
  IsBlockSignature : Block → Signature → Set
```

The voting scheme used by Peras is specified in the proposed CIP [*Votes & Certificates on Cardano*](https://github.com/cardano-foundation/CIPs/pull/870). It involves a *proof of membership* in a round's voting committee. The function `IsCommitteeMember` verifies a party's membership in a round's voting committee and the weight of their vote and the function `IsVoteSignature` verifies that validity of a vote's signature.

```agda
record Vote : Set  -- Votes will be defined later in this specification.

record VotingWeight : Set where
  field votes : ℕ

postulate
  MembershipProof : Set
  IsCommitteeMember : PartyId → RoundNumber → VotingWeight → MembershipProof → Set
  IsVoteSignature : Vote → Signature → Set
```

#### Votes

*Votes* have a creator, a weight, a proof of the creator's membership in the round's voting committee, and a reference to the block being voted for.

```agda
record Vote where
  constructor MkVote
  field votingRound : RoundNumber
        creatorId   : PartyId
        weight      : VotingWeight
        proofM      : MembershipProof
        blockHash   : Hash Block
        signature   : Signature

  votingWeight : ℕ
  votingWeight = VotingWeight.votes weight
  
  votingRound' : ℕ
  votingRound' = getRoundNumber votingRound
```

Votes are valid if the party and weight are correct for the round and the vote is properly signed.

```agda
ValidVote : Vote → Set
ValidVote v =
  IsCommitteeMember
    (Vote.creatorId v)
    (Vote.votingRound v)
    (Vote.weight v)
    (Vote.proofM v)
  × IsVoteSignature v (Vote.signature v)
```

*Equivocated votes* are ones that duplicate votes by the same party in the same round. The protocol will reject such equivocated votes.

```agda
data _∻_ : Vote → Vote → Set where
  Equivocation : ∀ {v₁ v₂}
    → Vote.creatorId v₁ ≡ Vote.creatorId v₂
    → Vote.votingRound v₁ ≡ Vote.votingRound v₂
    → v₁ ≢ v₂
    → v₁ ∻ v₂
```

#### Certificates

A *certificate* attends that a quorum of votes where cast during a round for the same block.

```agda
record Certificate : Set where
  constructor MkCertificate
  field round : RoundNumber
        blockRef : Hash Block
        
  roundNumber : ℕ
  roundNumber = getRoundNumber round
```

The protocol places special emphasis on the most recent certificate among a set of certificates.

```agda
latestCert : Certificate → List Certificate → Certificate
latestCert c = maximumBy c Certificate.roundNumber
  where maximumBy : {a : Set} → a → (a → ℕ) → List a → a
        maximumBy candidate _ [] = candidate
        maximumBy {a} candidate f (x ∷ xs) =
          if f candidate ≤ᵇ f x
            then maximumBy x f xs
            else maximumBy candidate f xs
```

#### Block bodies

*Block bodies* are identical to those in Praos. They consist of a payload of transactions and are identified by their unique hash. The detailed contents are irrelevant for Peras, so we represent them in a slightly simplified manner.

```agda
postulate
  Tx : Set
  hashTxs : List Tx → Hash (List Tx)

Payload = List Tx

instance
  iHashablePayload : Hashable Payload
  iHashablePayload .hash = hashTxs

record BlockBody : Set where
  constructor MkBlockBody
  field blockHash : Hash Payload
        payload : Payload
```

#### Blocks

*Blocks* are identical to those in Praos, except for rare inclusion of a certificate, which may happen near the beginning or ending of a cool-down period. The other detailed contents are irrelevant for Peras, so we represent them in a slightly simplified manner.

```agda
record Block where
  constructor MkBlock
  field slotNumber : SlotNumber
        creatorId : PartyId
        parentBlock : Hash Block
        certificate : Maybe Certificate  -- NB: New in Peras and not present in Praos.
        leadershipProof : LeadershipProof
        signature : Signature
        bodyHash : Hash Payload
        
  slotNumber' : ℕ
  slotNumber' = getSlotNumber slotNumber

postulate
  hashBlock : Block → Hash Block
  
instance
  iHashableBlock : Hashable Block
  iHashableBlock .hash = hashBlock
  
_≟-BlockHash_ : DecidableEquality (Hash Block)
(MkHash b₁) ≟-BlockHash (MkHash b₂) with b₁ ≟-BS b₂
... | yes p = yes (cong MkHash p)
... | no ¬p =  no (¬p ∘ cong Hash.hashBytes)
```

#### Chains

The linking of blocks into a *chain* is identical to Praos.

```agda
Chain = List Block

genesis : Chain
genesis = []
```

The protocol scrutinizes any certificates recorded on the chain.
```agda
certsFromChain : Chain → List Certificate
certsFromChain = catMaybes ∘ map Block.certificate
```

It also needs to test whether a certificate (quorum of votes) refers to a block found on a particular chain.

```agda
_PointsInto_ : Certificate → Chain → Set
_PointsInto_ c = Any ((Certificate.blockRef c ≡_) ∘ hash)

_PointsInto?_ : ∀ (c : Certificate) → (ch : Chain) → Dec (c PointsInto ch)
_PointsInto?_ c = any? ((Certificate.blockRef c ≟-BlockHash_) ∘ hash)
```

Peras differs from Praos in that the weight of a chain is its length plus the boost parameter $B$ times the number of vote quorums (certificates) its blocks have received.

```agda
module _ ⦃ _ : Params ⦄ where
  open Params ⦃...⦄

  ∥_∥_ : Chain → List Certificate → ℕ
  ∥ ch ∥ cts = ∣ ch ∣ + ∣ filter (_PointsInto? ch) cts ∣ * B
```

A chain is valid if its blocks are signed and their creators were slot leaders. The chain's genesis is always valid.

```agda
data ValidChain : Chain → Set where
  Genesis : ValidChain genesis
  Cons : ∀ {c₁ c₂ : Chain} {b₁ b₂ : Block}
    → IsBlockSignature b₁ (Block.signature b₁)
    → IsSlotLeader (Block.creatorId b₁) (Block.slotNumber b₁) (Block.leadershipProof b₁)
    → Block.parentBlock b₁ ≡ hash b₂
    → c₂ ≡ b₂ ∷ c₁
    → ValidChain c₂
    → ValidChain (b₁ ∷ c₂)
```

The protocol can identify a chain by the hash of its most recent block (its tip).

```agda
tipHash : ∀ {c : Chain} → ValidChain c → Hash Block
tipHash Genesis = record { hashBytes = emptyBS }
tipHash (Cons {b₁ = b} _ _ _ _ _) = hash b
```

A block is said to extend a certificate on a chain if the certified block is an ancestor of or identical to the block and on the chain.

```agda
ChainExtends : Maybe Block → Certificate → Chain → Set
ChainExtends nothing _ _ = ⊥
ChainExtends (just b) c =
  Any (λ block → (hash block ≡ Certificate.blockRef c))
    ∘ dropWhile (λ block' → ¬? (hash block' ≟-BlockHash hash b))
```

#### Messages and their envelopes

In addition to the chain *messages* already diffused among nodes in Praos, the Peras protocol also diffuses votes between nodes. (Note that Peras implementations might choose also to diffuse certificates in lieu of sets of votes that meet the quorum condition.)

```agda
data Message : Set where
  ChainMsg : Chain → Message
  VoteMsg : Vote → Message
```

Diffusion of votes or blocks over the network may involve delays of a slot or more.

```agda
module _ ⦃ _ : Params ⦄ ⦃ _ : Network ⦄ where
  open Params ⦃...⦄
  open Network ⦃...⦄
  
  Delay = Fin (suc (suc Δ))
  pattern 𝟘 = fzero
  pattern 𝟙 = fsuc fzero
```

Messages are put into an *envelope* and assigned to a party. Such messages can be delayed.

```agda
  record Envelope : Set where
    constructor ⦅_,_,_,_⦆
    field
      partyId : PartyId
      honesty : Honesty partyId
      message : Message
      delay : Delay
```

#### Block trees

*Block trees* are defined by functions and properties: any implementation of the block tree has to possess the required functions.

```agda
module _ ⦃ _ : Params ⦄ where
  open Params ⦃...⦄
  
  record IsTreeType {T : Set}
                    (tree₀ : T)
                    (newChain : T → Chain → T)
                    (allChains : T → List Chain)
                    (preferredChain : T → Chain)
                    (addVote : T → Vote → T)
                    (votes : T → List Vote)
                    (certs : T → List Certificate)
                    (cert₀ : Certificate)
         : Set₁ where

    field
```

It must also conform to properties that must hold with respect to chains, certificates and votes.

In particular, the genesis tree must prefer the genesis chain, have an empty set of certificates, and have an empty set of votes.

```agda
      instantiated :
        preferredChain tree₀ ≡ genesis

      instantiated-certs :
        certs tree₀ ≡ cert₀ ∷ []

      instantiated-votes :
        votes tree₀ ≡ []
```

The certificates in a chain newly incorporated into the block tree must equate to the certificates on the chain itself and the block tree's record of certificates.

```agda
      extendable-chain : ∀ (t : T) (c : Chain)
        → certs (newChain t c) ≡ certsFromChain c ++ certs t
```

A valid block tree must have a valid preferred chain.

```agda
      valid : ∀ (t : T)
        → ValidChain (preferredChain t)
```

The preferred chain must be at least as weighty as any other chain present in the block tree.

```agda
      optimal : ∀ (c : Chain) (t : T)
        → let b = preferredChain t
              cts = certs t
          in ValidChain c
        → c ∈ allChains t
        → ∥ c ∥ cts ≤ ∥ b ∥ cts
```

The preferred chain must be present in the list of all chains seen.

```agda
      self-contained : ∀ (t : T)
        → preferredChain t ∈ allChains t
```

Only valid votes are recorded in the block tree.

```agda
      valid-votes : ∀ (t : T)
        → All ValidVote (votes t)
```

Duplicate or equivocated votes must not be present in the block tree.

```agda
      unique-votes : ∀ (t : T) (v : Vote)
        → let vs = votes t
          in v ∈ vs
        → vs ≡ votes (addVote t v)

      no-equivocations : ∀ (t : T) (v : Vote)
        → let vs = votes t
          in Any (v ∻_) vs
        → vs ≡ votes (addVote t v)
```

Every certificate must represent a quorum of recorded votes.

> [!CAUTION]
> Check that weighted voting is correctly represented here.

```agda
      quorum-cert : ∀ (t : T) (b : Block) (r : ℕ)
        →  (sum ∘ map Vote.votingWeight) (filter (λ {v →
                     (getRoundNumber (Vote.votingRound v) ≟ r)
               ×-dec (Vote.blockHash v ≟-BlockHash hash b)}
             ) (votes t)) ≥ τ
        → Any (λ {c →
            (getRoundNumber (Certificate.round c) ≡ r)
          × (Certificate.blockRef c ≡ hash b) }) (certs t)
```

The concrete block tree type (`TreeType`) manages chains, certificates, and votes.

```agda
  record TreeType (T : Set) : Set₁ where

    field
      tree₀ : T
      newChain : T → Chain → T
      allChains : T → List Chain
      preferredChain : T → Chain
      addVote : T → Vote → T
      votes : T → List Vote
      certs : T → List Certificate
```

It memorializes the genesis certificate.

```agda
    cert₀ : Certificate
    cert₀ = MkCertificate (MkRoundNumber 0) (MkHash emptyBS)
```

It conforms to the `IsTreeType` requirements.

```agda
    field
      is-TreeType : IsTreeType
                      tree₀ newChain allChains preferredChain
                      addVote votes certs cert₀
```

Several convenience functions are provided for extracting information about certificates and votes.

```agda
    latestCertOnChain : T → Certificate
    latestCertOnChain = latestCert cert₀ ∘ catMaybes ∘ map Block.certificate ∘ preferredChain

    latestCertSeen : T → Certificate
    latestCertSeen = latestCert cert₀ ∘ certs

    hasVote : RoundNumber → T → Set
    hasVote (MkRoundNumber r) = Any ((r ≡_) ∘ Vote.votingRound') ∘ votes
```

#### Parameterization of the semantics

In order to define the semantics the following parameters are required.

- The type of the block-tree
- The adversarial state
- A function that mimics the node's memory pool by selecting the transactions available to a particular party in a particular slot
- A list of the parties participating in the protocol

```agda
module Semantics
           ⦃ _ : Params ⦄
           ⦃ _ : Network ⦄
           {T : Set} {blockTree : TreeType T}
           {S : Set} {adversarialState₀ : S}
           {txSelection : SlotNumber → PartyId → List Tx}
           {parties : Parties}
           where
    open Params ⦃...⦄
    open TreeType blockTree
```

The protocol starts from the genesis block tree.

```agda
    instance
      Default-T : Default T
      Default-T .Default.def = tree₀
```

#### Block-tree update

Updating the block tree involves recording the votes and chains received via messages.

```agda
    data _[_]→_ : T → Message → T → Set where

      VoteReceived : ∀ {v t} →
       ────────────────────────────
       t [ VoteMsg v ]→ addVote t v

      ChainReceived : ∀ {c t} →
       ──────────────────────────────
       t [ ChainMsg c ]→ newChain t c
```

#### Block selection

The block selected for voting is the most recent one on the preferred chain that is at least $L$ slots old.

```agda
    BlockSelection : SlotNumber → T → Maybe Block
    BlockSelection (MkSlotNumber s) =
      head ∘ filter (λ {b → (Block.slotNumber' b) ≤? (s ∸ L)}) ∘ preferredChain
```

#### Rules for voting in a round

Voting is allowed in a round if voting has proceeded regularly in preceding rounds or if a sufficient number of slots have lapsed since the protocol entered a cool-down period. Specifically, either of two pairs of conditions must be met.

- `VR-1A`: The vote has seen the certificate for the previous round.

```agda
    VotingRule-1A : RoundNumber → T → Set
    VotingRule-1A (MkRoundNumber r) t = r ≡ Certificate.roundNumber (latestCertSeen t) + 1
```

- `VR-1B`: The block being voted upon extends the most recently certified block

```agda
    VotingRule-1B : SlotNumber → T → Set
    VotingRule-1B s t =
      Any (ChainExtends (BlockSelection s t) (latestCertSeen t)) (allChains t)
```

- `VR-1`: Both `VR-1A` and `VR-1B` hold, which is the situation typically occurring when the voting has regularly occurred in preceding rounds.

```agda
    VotingRule-1 : SlotNumber → T → Set
    VotingRule-1 s t =
        VotingRule-1A (v-round s) t
      × VotingRule-1B s t
```

- `VR-2A`: The last certificate a party has seen is from a round at least $R$ rounds previously. This enforces the chain-healing period that must occur before leaving a cool-down period.

```agda
    VotingRule-2A : RoundNumber → T → Set
    VotingRule-2A (MkRoundNumber r) t =
      r ≥ Certificate.roundNumber (latestCertSeen t) + R
```

- `VR-2B`: The last certificate included in a party's current chain is from a round exactly $c \cdot K$ rounds ago for some $c \in ℕ$ with $c ≥ 0$. This enforces chain quality and a common prefix before leaving a cool-down period.

```agda
    VotingRule-2B : RoundNumber → T → Set
    VotingRule-2B (MkRoundNumber r) t =
        r > Certificate.roundNumber (latestCertOnChain t)
      × r mod K ≡ (Certificate.roundNumber (latestCertOnChain t)) mod K
      where
        _mod_ : ℕ → (n : ℕ) → ⦃ NonZero n ⦄ → ℕ
        _mod_ a b ⦃ prf ⦄ = _%_ a b ⦃ prf ⦄
```

- `VR-2`: Both `VR-2A` and `VR-2B` hold, which is the situation typically occurring when the chain is about to exit a cool-down period.

```agda
    VotingRule-2 : RoundNumber → T → Set
    VotingRule-2 r t =
        VotingRule-2A r t
      × VotingRule-2B r t
```

If either `VR-1A` and `VR-1B` hold, or `VR-2A` and `VR-2B` hold, then voting is allowed.

```agda
    VotingRule : SlotNumber → T → Set
    VotingRule s t =
        VotingRule-1 s t
      ⊎ VotingRule-2 (v-round s) t
```

#### State

The small-step semantics rely on a global state, which consists of several pieces of information.

- Current slot of the system
- Map with local state per party
- All the messages that have been sent but not yet been delivered
- All the messages that have been sent
- Adversarial state

```agda
    record State : Set where
      constructor ⟦_,_,_,_,_⟧
      field
        clock : SlotNumber
        blockTrees : AssocList PartyId T
        messages : List Envelope
        history : List Message
        adversarialState : S
```

#### Progress

Rather than keeping track of progress, we introduce a predicate stating that all messages that are not delayed have been delivered. This is a precondition that must hold before transitioning to the next slot.

```agda
    Fetched : State → Set
    Fetched = All (λ { z → Envelope.delay z ≢ 𝟘 }) ∘ messages
      where open State
```

A predicate for the global state assesses that the current slot is the last slot of a voting round.

```agda
    LastSlotInRound : State → Set
    LastSlotInRound M =
      suc (rnd (getSlotNumber clock)) ≡ rnd (suc (getSlotNumber clock))
      where open State M
```

Similarly, a predicate for the global state assesses that the next slot will be in a new voting round.

```agda
    NextSlotInSameRound : State → Set
    NextSlotInSameRound M =
      rnd (getSlotNumber clock) ≡ rnd (suc (getSlotNumber clock))
      where open State M
```

Furthermore, there is a predicate for the global state asserting that parties of the voting committee for a the current voting round have voted. This is needed as a prerequisite for transitioning from one voting round to another.

```agda
    RequiredVotes : State → Set
    RequiredVotes M =
         Any (VotingRule clock ∘ proj₂) blockTrees
       → Any (hasVote (v-round clock) ∘ proj₂) blockTrees
      where open State M
```

#### Advancing the clock

Ticking the global clock increments the slot number and decrements the delay of all the messages in the message buffer.

```agda
    tick : State → State
    tick M =
      record M
        { clock = SlotNumber.next clock
        ; messages =
            map (λ where e → record e { delay = pred (Envelope.delay e) })
              messages
        }
      where open State M
```

#### Updating the global state

New messages are buffered, recorded in the global history, and will update a party's portion of the global state.
```agda
    _,_,_,_⇑_ : Message → Delay → PartyId → T → State → State
    m , d , p , l ⇑ M =
      record M
        { blockTrees = set p l blockTrees
        ; messages =
            map (uncurry ⦅_,_, m , d ⦆)
              (filter (¬? ∘ (p ≟-party_) ∘ proj₁) parties)
            ++ messages
        ; history = m ∷ history
        }
      where open State M
```

This occurs when a message diffuses to new parties.

```agda
    add_to_diffuse_ : (Message × Delay × PartyId) → T → State → State
    add (m@(ChainMsg x) , d , p) to t diffuse M = m , d , p , newChain t x ⇑ M
    add (m@(VoteMsg x) , d , p) to t diffuse M = m , d , p , addVote t x ⇑ M
```

#### Fetching

A party receives messages from the global state by fetching messages assigned to the party, updating the local block tree, and putting the local state back into the global state.

```agda
    data _⊢_[_]⇀_ : {p : PartyId} → Honesty p → State → Message → State → Set
      where
```

An honest party consumes a message from the global message buffer and updates their local state.

```agda
      honest : ∀ {p} {t t′} {m} {N} → let open State N in
          blockTrees ⁉ p ≡ just t
        → (m∈ms : ⦅ p , Honest , m , 𝟘 ⦆ ∈ messages)
        → t [ m ]→ t′
          ---------------------------------------------
        → Honest {p} ⊢
          N [ m ]⇀ record N
            { blockTrees = set p t′ blockTrees
            ; messages = messages ─ m∈ms
            }
```

An adversarial party might delay a message.

```agda
      corrupt : ∀ {p} {as} {m} {N} → let open State N in
           (m∈ms : ⦅ p , Corrupt , m , 𝟘 ⦆ ∈ messages)
           ----------------------------------------------
        →  Corrupt {p} ⊢
           N [ m ]⇀ record N
             { messages = m∈ms ∷ˡ= ⦅ p , Corrupt , m , 𝟙 ⦆
             ; adversarialState = as
             }
```

#### Voting

Votes are created with the required information about committee membership and the block being voted for.

```agda
    createVote : SlotNumber → PartyId → VotingWeight → MembershipProof → Signature → Hash Block → Vote
    createVote s p w prf sig hb =
      record
        { votingRound = v-round s
        ; creatorId = p
        ; weight = w
        ; proofM = prf
        ; blockHash = hb
        ; signature = sig
        }
```

A party can vote for a block, if

- the current slot is the first slot in a voting round
- the party is a member of the voting committee
- the chain is not in a cool-down phase

Voting updates the party's local state and for all other parties a message is ready to be consumed immediately.

> [!CAUTION]
> Check that weighted voting is correctly represented here.

```agda
    infix 2 _⊢_⇉_
    data _⊢_⇉_ : {p : PartyId} → Honesty p → State → State → Set where
    
      honest : ∀ {p} {t} {M} {w} {π} {σ} {b}
        → let
            open State
            s = clock M
            r = v-round s
            v = createVote s p w π σ (hash b)
          in
        ∙ BlockSelection s t ≡ just b
        ∙ blockTrees M ⁉ p ≡ just t
        ∙ IsVoteSignature v σ
        ∙ StartOfRound s r
        ∙ IsCommitteeMember p r w π
        ∙ VotingRule s t
          ───────────────────────────────────
          Honest {p} ⊢
            M ⇉ add (VoteMsg v , 𝟘 , p) to t
                diffuse M
```

Rather than creating a delayed vote, an adversary can honestly create it and delay the message.

> [!WARNING]
> Is there missing code for `corrupt` that should be included right here?

#### Block creation

Certificates are conditionally added to a block, typically near the beginning of ending of a cool-down period. Such recording occurs if . . .

1. There is no certificate seen (recorded) from two rounds ago
2. The last seen certificate is not expired
3. The last seen certificate is from a later round than the last certificate on chain

```agda
    needCert : RoundNumber → T → Maybe Certificate
    needCert (MkRoundNumber r) t =
      let
        cert⋆ = latestCertOnChain t
        cert′ = latestCertSeen t
      in
        if not (any (λ {c → ⌊ Certificate.roundNumber c + 2 ≟ r ⌋}) (certs t))  -- (1)
           ∧ (r ≤ᵇ A + Certificate.roundNumber cert′)                           -- (2)
           ∧ (Certificate.roundNumber cert⋆ <ᵇ Certificate.roundNumber cert′)   -- (3)
        then just cert′
        else nothing
```

Blocks are created with the require information.

```agda
    createBlock : SlotNumber → PartyId → LeadershipProof → Signature → T → Block
    createBlock s p π σ t =
      record
        { slotNumber = s
        ; creatorId = p
        ; parentBlock =
            let open IsTreeType
            in tipHash (is-TreeType .valid t)
        ; certificate =
            let r = v-round s
            in needCert r t
        ; leadershipProof = π
        ; bodyHash =
            let txs = txSelection s p
            in BlockBody.blockHash
                 record
                   { blockHash = hash txs
                   ; payload = txs
                   }
        ; signature = σ
        }
```

A party can create a new block by adding it to the local block tree and diffuse the block creation messages to the other parties. Block creation is possible, if as in Praos.

- the block signature is correct
- the party is the slot leader

Block creation updates the party's local state, but for all other parties a message is added to the message buffer

```agda
    infix 2 _⊢_↷_
    data _⊢_↷_ : {p : PartyId} → Honesty p → State → State → Set where

      honest : ∀ {p} {t} {M} {π} {σ}
        → let
            open State
            s = clock M
            b = createBlock s p π σ t
            pref = preferredChain t
          in
        ∙ blockTrees M ⁉ p ≡ just t
        ∙ ValidChain (b ∷ pref)
          ───────────────────────────
          Honest {p} ⊢
            M ↷ add (
                  ChainMsg (b ∷ pref)
                , 𝟘
                , p) to t
                diffuse M
```

> [!WARNING]
> Is there missing code for `corrupt` that should be included right here?

#### Small-step semantics

The small-step semantics describe the evolution of the global state.

```agda
    variable
      M N O : State
      p : PartyId
      h : Honesty p
```

The relation allows

- Fetching messages at the beginning of each slot
- Block creation
- Voting
- Transitioning to next slot in the same voting round
- Transitioning to next slot in a new voting round

Note that when transitioning to the next slot we need to distinguish whether the next slot is in the same or a new voting round. This is necessary in order to detect adversarial behavior with respect to voting (adversarialy not voting
in a voting round).

```agda
    data _↝_ : State → State → Set where

      Fetch : ∀ {m} →
        ∙ h ⊢ M [ m ]⇀ N
          ──────────────
          M ↝ N

      CreateVote :
        ∙ Fetched M
        ∙ h ⊢ M ⇉ N
          ─────────
          M ↝ N

      CreateBlock :
        ∙ Fetched M
        ∙ h ⊢ M ↷ N
          ─────────
          M ↝ N

      NextSlot :
        ∙ Fetched M
        ∙ NextSlotInSameRound M
          ─────────────────────
          M ↝ tick M

      NextSlotNewRound :
        ∙ Fetched M
        ∙ LastSlotInRound M
        ∙ RequiredVotes M
          ─────────────────
          M ↝ tick M
```

This completes for formal specification of Peras. The repository [github:input-output-hk/peras-design](https://github.com/input-output-hk/peras-design/tree/main) leverages this specification by providing the following Agda code.

- Proofs of properties of the Peras protocol.
- An executable specification (since the above specification is *relational* and not *executable*)
- Proofs of the soundness of the executable specification with respect to this relational one
- Scaffolding for generating dynamic, property-based conformance tests using the Haskell [`quickcheck-dynamic`](https://hackage.haskell.org/package/quickcheck-dynamic) package.

### Specification of votes and certificates

The stake-proportional voting in Peras is mimicked after the _sortition_ algorithm used in Praos: specifically it is based on the use of a *verifiable random function* (VRF) by each stake-pool operator guaranteeing the following properties:

- The probability for each voter to cast their vote in a given round is correlated to their share of total stake.
- It should be computationally impossible to predict a given SPO's schedule without access to their secret key VRF key.
- Verification of a voter's right to vote in a round should be efficiently computable.
- A vote should be unique and non-malleable, which is a requirement for the use of efficient certificates aggregation.

Additionally one would like the following property to be provided by our voting scheme:

- Voting should require minimal additional configuration (i.e., key management) for SPOs,
- Voting and certificates construction should be fast in order to ensure we do not interfere with other operations happening in the node.

The precise scheme and format for votes and certificates is immaterial to the protocol itself, but for reasons of efficiency (i.e., minimal resource usage) the selection of ALBA certificates, as described in proposed CIP [*Votes & Certificates on Cardano*](https://github.com/cardano-foundation/CIPs/pull/870), is recommended for Peras.

### CDDL schema for ledger

Peras requires a single addition, `peras_cert`, the block data on the ledger. 

```diff
 block =
   [ header
   , transaction_bodies         : [* transaction_body]
   , transaction_witness_sets   : [* transaction_witness_set]
   , auxiliary_data_set         : {* transaction_index => auxiliary_data }
   , invalid_transactions       : [* transaction_index ]
+  , ? peras_cert               : alba_certificate
   ]
```

Votes are serialized in the following CDDL.

```cddl
vote =
  [ voter_id         : hash32
  , voting_round     : round_no
  , block_hash       : hash32
  , voting_proof     : vrf_cert
  , voting_weight    : voting_weight
  , kes_period       : kes_period
  , kes_vkey         : kes_vkey
  , kes_signature    : kes_signature
  ]
```

This definition relies on the following primitive types (drawn from Ledger definitions in [crypto.cddl](https://github.com/input-output-hk/cardano-ledger/blob/e2aaf98b5ff2f0983059dc6ea9b1378c2112101a/eras/conway/impl/cddl-files/crypto.cddl#L1)).

```cddl
round_no = uint .size 8
voting_weight = uint .size 8
vrf_cert = [bytes, bytes .size 80]
hash32 = bytes .size 32
kes_vkey = bytes .size 32
kes_signature = bytes .size 448
kes_period = uint .size 8
```

As already mentioned, the vote serialization mimics the block header's structure, which allows Cardano nodes to reuse their existing VRF and KES keys. Also note the following.

- The total size of each vote is 710 bytes, according to the above definition.
- Unless explicitly mentioned, the `hash` function exclusively uses 32-bytes Blake2b-256 hashes.
- The `voter_id` is it's pool identifier (i.e., the hash of the node's cold key).

The CDDL for the certificates that aggregate votes is specified in the proposed CIP [*Votes & Certificates on Cardano*](https://github.com/cardano-foundation/CIPs/pull/870).

For ALBA certificates, assuming 1000 votes, a honest to faulty ratio of 80/20, and security parameter $λ=128$, one has the following typical measurements.

| Metric                          |  Value |
| ------------------------------- | -----: |
| Certificate size                |  47 kB |
| Proving time (per vote)         | 133 μs |
| Vote verification (per vote)    | 161 μs |
| Aggregation time                |   5 ms |
| Verification time (certificate) |  15 ms |

> [!WARNING]
> The text from here onwards is still under major revision.

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

* relate the spec with the motivation? -> ticking the boxes
* Provide numbers from simulations/models

We have refined our analysis and understanding of Peras protocol, taking into account its latest evolution:

* A promising solution for votes and certificates construction has been identified based on existing VRF/KES keys and ALBAs certificates.
    * This solution relies on existing nodes' infrastructure and cryptographic primitives and therefore should be straightforward to implement and deploy.
* Peras's votes and certificates handling will have a negligible impact on existing node CPU, network bandwidth, and memory requirements.
    * They will have a moderate impact on storage requirements leading to a potential increase of disk storage of 15 to 20%..
    * Peras might have a moderate economical impact for SPOs running their nodes with cloud providers due to increasing network _egress traffic_.
* Peras's impact on settlement probabilities depends strongly upon the specific choices for protocol parameters and upon which stakeholder use case(s) those have been tuned for.
    * Settlement can be as fast as two minutes, with an infinitesimal probability of rollback after that, but there is an appreciable probability of rollback prior to that time if a strong adversary attacks.
    * Stakeholders will have to reach consensus about the relative importance of settlement time versus pre-settlement resistance to attacks.
* We think development of a *pre-alpha* prototype integrated with the cardano-node should be able to proceed.

Peras provides demonstrably fast settlement without weakening security or burdening nodes. The settlement time varies as a function of the protocol-parameter settings and the prevalence of adversarial stake. For a use case that emphasizes rapid determination of whether a block is effectively finally incorporated into the preferred chain, it is possible to achieve settlement times as short as two minutes, but at the expense of having to resubmit rolled-back transactions in cases where there is a strong adversarial stake.

The impact of Peras upon nodes falls into four categories: network, CPU, memory, and storage. We have provided [evidence](#votes--certificates) that the CPU time required to construct and verify votes and certificates is much smaller than the duration of a voting round. Similarly, the [memory](#memory) needed to cache votes and certificates and the [disk space](#persistent-storage) needed to persist certificates is trivial compared to the memory needed for the UTXO set and the disk needed for the blocks.

On the networking side, our [ΔQ studies](#vote-diffusion) demonstrate that diffusion of Peras votes and certificates consumes minimal bandwidth and would not interfere with other node operations such as memory-pool and block diffusion. However, [diffusion of votes and certificates](#network-traffic) across a network will still have a noticeable impact on the _volume_ of data transfer, in the order of 20%, which might translate to increased operating costs for nodes deployed in cloud providers.

In terms of development impacts and resources, Peras requires only a minimal modification to the ledger CDDL and block header. Around cool-down periods, a certificate hash will need to be included in the block header and the certificate itself in the block. Implementing Peras does not require any new cryptographic keys, as the existing VRF/KES will be leveraged. It will require an implementation of the ALBA algorithm for creating certificates. It does require a new mini-protocol for diffusion of votes and certificates. The node's logic for computing the chain weight needs to be modified to account for the boosts provided by certificates. Nodes will have to persist all certificates and will have to cache unexpired votes. They will need a thread (or equivalent) for verifying votes and certificates. Peras only interacts with Genesis and Leios in the chain-selection function and it is compatible with the historical evolution of the blockchain. A node-level specification and conformance test will also need to be written.

In no way does Peras weaken any of the security guarantees provided by Praos or Genesis. Under strongly adversarial conditions, where an adversary can trigger a Peras voting cool-down period, the protocol in essence reverts to the Praos (or Genesis) protocol, but for a duration somewhat longer than the Praos security parameter. Otherwise, settlement occurs after each Peras round. This document has approximately mapped the trade-off between having a short duration for each round (and hence faster settlement) versus having a high resistance to an adversary forcing the protocol into a cool-down period. It also estimates the tradeoff between giving chains a larger boost for each certificate (and hence stronger anchoring of that chain) versus keeping the cool-down period shorter.

## Use Cases

Main benefit is that Peras drastically decreases the need to wait for confirmation for transactions, from minutes/hours to seconds/minutes

* I would highlight Peras making Cardano more attractive option for interoperability solutions like LayerZero, Axelar, WormHole, etc. Maybe we can even go as far to state that Peras is a pre-requisite for this? 
* Sidechains
* Exchanges?
* DApps/service providers, basically anyone accepting or using ADAs, and anyone building some service on top of cardano with some kind of sensitivity to time

## Attack and Mitigation


## Resource Requirements

In this section, we evaluate the impact on the day-to-day operations of the Cardano network and cardano nodes of the deployment of Peras protocol, based on the data gathered over the course of project.

In this section, we evaluate the impact on the day-to-day operations of the Cardano network and cardano nodes of the deployment of Peras protocol, based on the data gathered over the course of project.


### Network diffusion of votes

Building on [previous work](./tech-report-1#network-performance-analysis), we built a ΔQ model to evaluate the expected delay to reach _quorum_.
The model works as follows:

* We start from a base uniform distribution of single MTU latency between 2 nodes, assuming a vote fits in a single TCP frame. The base latencies are identical as the one used in previous report.
* We then use the expected distribution of paths length for a random graph with 15 average connections, to model the latency distribution across the network, again reusing previously known values.
* We then apply the `NToFinish 75` combinator to this distribution to compute the expected distribution to reach 75% of the votes (quorum).
* An important assumption is that each vote diffusion across the network is expected to be independent from all other votes.
* Verification time for a single vote is drawn from the above benchmarks, but we also want to take into account the verification time of a single vote, which we do in two different ways:
    * One distribution assumes a node does all verifications sequentially, one vote at a time
    * Another assumes all verifications can be done in parallel
    * Of course, the actual verification time should be expected to be in between those 2 extremes

Using the "old" version of ΔQ library based on numerical (e.g., Monte-Carlo) sampling, yields the following graph:
![Vote diffusion](/img/vote-diffusion.svg)

This graph tends to demonstrate vote diffusion should be non-problematic, with a quorum expected to be reached in under 1 second most of the time to compare with a round length of about 2 minutes.

At the time of this writing, a newer version of the ΔQ library based on _piecewise polynomials_ is [available](https://github.com/DeltaQ-SD/dqsd-piecewise-poly). Our [attempts](https://github.com/input-output-hk/peras-design/blob/01206e5d4d3d5132c59bff18564ad63adc924488/Logbook.md#L302) to use it to model votes diffusion were blocked by the high computational cost of this approach and the time it takes to compute a model, specifically about 10 minutes in our case. The code for this experiment is available as a [draft PR #166](https://github.com/input-output-hk/peras-design/pull/166).

In the old version of ΔQ based on numerical sampling, which have [vendored in our codebase](https://github.com/input-output-hk/peras-design/blob/a755cd033e4898c23ee4bacc9b677145497ac454/peras-delta-q/README.md#L1), we introduced a `NToFinish` combinator to model the fact we only take into account some fraction of the underlying model. In our case, we model the case where we only care about the first 75% of votes that reach a node.

Given convolutions are the most computationally intensive part of a ΔQ model, it seems to us a modeling approach based on discrete sampling and vector/matrices operations would be quite efficient. We did some experiment in that direction, assessing various approaches in Haskell: A naive direct computation using [Vector](https://hackage.haskell.org/package/vector)s, FFT-based convolution using vectors, and [hmatrix](https://hackage.haskell.org/package/hmatrix)' convolution function.

![Computing Convolutions](/img/convolutions.png)

This quick-and-dirty spike lead us to believe we could provide a fast and accurate ΔQ modelling library using native vector operations provided by all modern architectures, and even scale to very large model using GPU libraries.

### Network

#### Network traffic

For a fully synced nodes, the impact of Peras on network traffic is modest:

* For votes, assuming $U \approx 100$, a committee size of 2000 SPOs, a single vote size of 700 bytes, means we will be adding an average of 14 kB/s to the expected traffic to each node,
* For certificates, assuming an average of 50 kB size (half way between Mithril and ALBA sizes) means an negligible increase of 0.5 kB/s on average. Note that a node will download either votes or certificate for a given round, but never both so these numbers are not cumulative.

A non fully synced nodes will have to catch-up with the _tip_ of the chain and therefore download all relevant blocks _and_ certificates. At 50% load (current [monthly load](https://cexplorer.io/usage) is 34% as of this writing), the chain produces a 45 kB block every 20 s on average. Here are back-of-the-napkin estimates of the amount of data a node would have to download (and store) for synchronizing, depending on how long it has been offline:

| Time offline | Blocks (GB) | Certificates (GB) |
|--------------|-------------|-------------------|
| 1 month      | 5.56        | 1.23              |
| 3 months     | 16.68       | 3.69              |
| 6 months     | 33.36       | 7.38              |

#### Network costs

![Typical node inbound & outbound traffic](https://peras-staging.cardano-scaling.org/assets/images/node-average-traffic-49a7cbcee8e4f05a7a42b61e445e5db9.jpg#scale50)

We did some research on network pricing for a few major Cloud and well-known VPS providers, based on the [share](https://pooltool.io/networkhealth) of stakes each provider is reported to support, and some typical traffic pattern as exemplified by the following picture (courtesy of Markus Gufler).

The next table compares the cost (in US$/month) for different outgoing data transfer volumes expressed as bytes/seconds, on similar VMs tailored to cardano-node's [hardware requirements](https://developers.cardano.org/docs/operate-a-stake-pool/hardware-requirements/) (32GB RAM, 4+ Cores, 500GB+ SSD disk). The base cost of the VM is added to the network cost to yield total costs depending on transfer rate.

| Provider     | VM     | 50 kB/s | 125 kB/s | 250 kB/s |
| ------------ | ------ | ------- | -------- | -------- |
| DigitalOcean | $188   | $188    | $188     | $188     |
| Google Cloud | $200   | $213.6  | $234     | $268     |
| AWS          | $150 ? | $161.1  | $177.9   | $205.8   |
| Azure        | $175   | $186    | $202     | $230     |
| OVH          | $70    | $70     | $70      | $70      |
| Hetzner      | $32    | $32     | $32      | $32      |


> [!NOTE]
> 
> * The AWS cost is quite hard to estimate up-front, obviously on purpose. The $150 base price is a rough average of various instances options in the target range.
> * Google, AWS and Azure prices are based on 100% uptime and at least 1-year reservation for discounts.
> * Cloud providers only charge _outgoing_ network traffic. The actual cost per GB depends on the destination, this table assumes all outbound traffic will be targeted outside of the provider which obviously won't be true, so it should be treated as an upper bound.

For an AWS hosted SPO, which represent about 20% of the SPOs, a 14 kB/s increase in traffic would lead to a cost increase of **\$3.8/mo** (34 GB times $0.11/GB). This represents an average across the whole network: depending on the source of the vote and its diffusion pattern, some nodes might need to send a vote to more than one downstream peer which will increase their traffic, while other nodes might end up not needing to send a single vote to their own peers. Any single node in the network is expected to download each vote _at most_ once.

### Persistent storage

Under similar assumptions, we can estimate the storage requirements entailed by Peras: Ignoring the impact of cooldown periods, which last for a period at least as long as $k$ blocks, the requirement to store certificates for every round increases node's storage by about **20%**.

Votes are expected to be kept in memory so their impact on storage will be null.

### CPU

In the [Votes & Certificates](#votes-certificates) section we've provided some models and benchmarks for votes generation, votes verification, certificates proving and certificates verification, and votes diffusion. Those benchmarks are based on efficient sortition-based voting and ALBAs certificate, and demonstrate the impact of Peras on computational resources for a node will be minimal. Moreover, the most recent version of the algorithm detailed in this report is designed in such a way the voting process runs in parallel with block production and diffusion and therefore is not on this critical path.

Voting:

* Single Voting (Binomial): 139.5 μs
* Single Verification (binomial): 160.9 μs
* Single Voting (Taylor): 47.02 ms

The implementation takes some liberty with the necessary rigor suitable for cryptographic code, but the timings provided should be consistent with real-world production grade code. In particular, when using _nonce_ as a random value, we only use the low order 64 bits of the nonce, not the full 256 bits.

### Memory

A node is expected to need to keep in memory:

* Votes for the latest voting round: For a committee size of 1000 and individual vote size of 700 bytes, that's 700 kB.
* Cached certificates for voting rounds up to settlement depth, for fast delivery to downstream nodes: With a boost of 10/certificate, settlement depth would be in the order of 216 blocks, or 4320 seconds, which represent about 10 rounds of 400 slots. Each certificate weighing 50 kB, that's another 500 kB of data a node would need to cache in memory.

Peras should not have any significant impact on the memory requirements of a node.


## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

* Conformance test suite passes on cardano-node

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->

* Updated CIP Specification with full detail - assuming we will publish the CIP with some details to be figured out. 
* Need to figure out IOI/Intersect dance?
* Sketch a generic plan
* Some incremental deployment possible?
    * Vote casting and diffusion
    * Certificate baking and diffusion
    * Chain selection based on weight as heuristic
    * Full chain selection 

### Integration into Cardano Node

In the [previous](tech-report-1.md) report, we already studied how Peras could be concretely implemented in a Cardano node. Most of the comments there are still valid, and we only provide here corrections and additions when needed. We have addressed resources-related issue in a previous section.

The following picture summarizes a possible architecture for Peras highlighting its interactions with other components of the system.

![Peras High-level Architecture](/img/peras-architecture.jpg)

The main impacts identified so far are:

* There is no impact in the existing block diffusion process, and no changes to block headers structure.
* Block body structure needs to be changed to accomodate for a certificate when entering _cooldown_ period.
* Consensus _best chain_ selection algorithm needs to be aware of the existence of a _quorum_ to compute the _weight_ of a possible chain, which is manifested by a _certificate_ from the Peras component.
    * Consensus will need to maintain or query a list of valid certificates (e.g., similar to _volatile_ blocks) as they are received or produced.
    * Chain selection and headers diffusion is not dependent on individual votes.
* Peras component can be treated as another _chain follower_ to which new blocks and rollbacks are reported.
    * Peras component will also need to be able to retrieve current _stake distribution_.
    * It needs to have access to VRF and KES keys for voting, should we decide to forfeit BLS signature scheme.
* Dedicated long term storage will be needed for certificates.
* Networking layer will need to accomodate (at least) two new mini-protocols for votes and certificates diffusion.
    * This seems to align nicely with current joint effort on [Mithril integration](https://hackmd.io/yn9643iKTVezLbiVb-BzJA?view).
* Our remarks regarding the possible development of a standalone prototype interacting with a modifified adhoc node still stands and could be a good next step.
 
<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Defining Protocol Parameters values

In order to provide useful recommendations for the protocol parameters, we first need to understand what is their admissible range of values, e.g. the constraints stemming from practical and theoretical needs, and to analyse their impact on the settlement probabilities.

### Constraints on Peras Parameters

The following constraints on Peras parameters arise for both theoretical and practical considerations.

| Parameter               | Symbol          | Units   | Description                                                                               | Constraints                                              | Rationale                                                                                    |
| ----------------------- | --------------- | ------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Round length            | $U$             | slots   | The duration of each voting round.                                                        | $U \geq \Delta$                                          | All of a round's votes must be received before the end of the round.                         |
| Block selection offset  | $L$             | slots   | The minimum age of a candidate block for being voted upon.                                | $\Delta < L \leq U$                                    | Rule VR-1B will fail if the candidate block is older than the most recently certified block. |
| Certificate expiration  | $A$             | slots   | The maximum age for a certificate to be included in a block.                              | $A = T_\text{heal}+T_\text{CQ}$                          | After a quorum failure, the chain must heal and achieve quality.                             |
| Chain ignorance period  | $R$             | rounds  | The number of rounds for which to ignore certificates after entering a cool-down period.  | $R = \left\lceil A / U \right\rceil$                     | Ensure chain-ignorance period lasts long enough to include a certificate on the chain.       |
| Cool-down period        | $K$             | rounds  | The minimum number of rounds to wait before voting again after a cool-down period starts. | $K = \left\lceil \frac{A + T_\text{CP}}{U} \right\rceil$ | After a quorum failure, the chain must heal, achieve quality, and attain a common prefix.    |
| Certification boost     | $B$             | blocks  | The extra chain weight that a certificate gives to a block.                               | $B > 0$                                                | Peras requires that some blocks be boosted.                                                  |
| Quorum size             | $\tau$          | parties | The number of votes required to create a certificate.                                     | $\tau > 3 n / 4$                                       | Guard against a minority (< 50%) of adversarial voters.                                       |
| Committee size          | $n$             | parties | The number of members on the voting committee.                                            | $n > 0$                                                | Peras requires a voting committee.                                                           |
| Network diffusion time  | $\Delta$        | slots   | Upper limit on the time needed to diffuse a message to all nodes.                         | $\Delta > 0$                                           | Messages have a finite delay.                                                                |
| Active slot coefficient | $f$             | 1/slots | The probability that a party will be the slot leader for a particular slot.               | $0 < f \leq 1$                                         | Blocks must be produced.                                                                     |
| Healing time            | $T_\text{heal}$ | slots   | Healing period to mitigate a strong (25-50%) adversary.                                   | $T_\text{heal} = \mathcal{O}\left( B / f \right)$        | Sufficient blocks must be produced to overcome an adversarially boosted block.               |
| Chain-quality time      | $T_\text{CQ}$   | slots   | Ensure the presence of at least one honest block on the chain.                            | $T_\text{CQ} = \mathcal{O} (k/f)$                        | A least one honest block must be produced.                                                   |
| Common-prefix time      | $T_\text{CP}$   | slots   | Achieve settlement.                                                                       | $T_\text{CP} = \mathcal{O} (k/f)$                        | The Ouroboros Praos security parameter defines the time for having a common prefix.          |
| Security parameter      | $k$             | blocks  | The Ouroboros Praos security parameter.                                                   | n/a                                                      | Value for the Cardano mainnet.                                                               |

### Settlement probabilities

In the estimates below, we define the *non-settlement probability* as the probability that a transaction (or block) is rolled back. Note that this does not preclude the possibility that the transaction could be included in a later block because it remained in the memory pool of a node that produced a subsequent block. Because there are approximately 1.5 million blocks produced per year, even small probabilities of non-settlement can amount to an appreciable number of discarded blocks.

### Case 1: Blocks without boosted descendants

Blocks that are not cemented by a boost to one of their descendant (successor) blocks are most at risk for being rolled back because they are not secured by the extra weight provided by a boost.

The *Variant 2* scenario in the *Adversarial chain receives boost* section above dominates the situation where a transaction is recorded in a block but an adversarial fork later is boosted by a certificate to become the preferred chain. This scenario plays out as follows:

1. Both the honest chain and an initially private adversarial chain have a common prefix that follows the last boosted block.
2. The adversary privately grows their chain and does not include transactions in the memory pool.
3. When the time comes where the last block is first eligible for later being voted upon, the adversarial chain is published and all parties see that it is longer than the honest chain.
4. Hence the newly published adversarial chain becomes the preferred chain, and all parties build upon that.
5. Later, when voting occurs, the chain that had been adversarial will received the boost.
6. Because the adversarial prefix has been boosted, there is a negligible probability that the discarded portion of the honest chain will ever become part of the preferred chain.
7. Therefore the preferred chain does not include any transactions that were in blocks of the honest chain after the common prefix and before the adversarially boosted block.

Note that this is different from the situation where a transaction is included on honest forks because such a transaction typically reaches the memory pool of the block producers on each fork and is included on each. The adversary refrains from including the transaction on their private chain.

The active-slot coefficient (assumed to be 5%), the length of the rounds, and the adversary's fraction of stake determine the probability of non-settlement in such a scenario. The table below estimates this probability. For example, in the presence of a 5% adversary and a round length of 360 slots, one could expect about two blocks to be reverted per year in such an attack.

| Round Length | 5% Adversary | 10% Adversary | 15% Adversary | 20% Adversary | 45% Adversary |
| -----------: | -----------: | ------------: | ------------: | ------------: | ------------: |
|           60 |     1.35e-02 |      3.64e-02 |      6.99e-02 |      1.15e-01 |      4.81e-01 |
|           90 |     5.45e-03 |      1.82e-02 |      4.14e-02 |      7.77e-02 |      4.64e-01 |
|          120 |     2.16e-03 |      9.16e-03 |      2.47e-02 |      5.31e-02 |      4.48e-01 |
|          150 |     8.55e-04 |      4.63e-03 |      1.49e-02 |      3.66e-02 |      4.34e-01 |
|          180 |     3.40e-04 |      2.36e-03 |      9.08e-03 |      2.55e-02 |      4.22e-01 |
|          240 |     5.46e-05 |      6.27e-04 |      3.42e-03 |      1.25e-02 |      4.00e-01 |
|          300 |     8.91e-06 |      1.69e-04 |      1.31e-03 |      6.27e-03 |      3.81e-01 |
|          360 |     1.47e-06 |      4.63e-05 |      5.11e-04 |      3.18e-03 |      3.65e-01 |
|          420 |     2.46e-07 |      1.28e-05 |      2.00e-04 |      1.63e-03 |      3.51e-01 |
|          480 |     4.12e-08 |      3.56e-06 |      7.92e-05 |      8.37e-04 |      3.37e-01 |
|          540 |     6.97e-09 |      9.96e-07 |      3.15e-05 |      4.33e-04 |      3.25e-01 |
|          600 |     1.18e-09 |      2.80e-07 |      1.26e-05 |      2.25e-04 |      3.14e-01 |

Using the approach of Gaži, Ren, and Russell (2023) and setting $\Delta = 5 \text{\,slots}$ to compute the upper bound on the probability of failure to settle results in similar, but not identical probabilities.

| Blocks | ≈ Slots | 5% Adversary | 10% Adversary | 15% Adversary | 20% Adversary |
| -----: | ------: | -----------: | ------------: | ------------: | ------------: |
|      3 |      60 |     6.13e-02 |      1.41e-01 |      2.53e-01 |      3.89e-01 |
|      4 |      80 |     2.73e-02 |      8.15e-02 |      1.73e-01 |      3.01e-01 |
|      5 |     100 |     1.22e-02 |      4.73e-02 |      1.19e-01 |      2.34e-01 |
|      6 |     120 |     5.46e-03 |      2.75e-02 |      8.26e-02 |      1.83e-01 |
|      9 |     180 |     4.95e-04 |      5.55e-03 |      2.80e-02 |      8.89e-02 |
|     12 |     240 |     4.51e-05 |      1.13e-03 |      9.65e-03 |      4.40e-02 |
|     15 |     300 |     4.11e-06 |      2.32e-04 |      3.35e-03 |      2.20e-02 |
|     18 |     360 |     3.75e-07 |      4.77e-05 |      1.17e-03 |      1.11e-02 |
|     21 |     420 |     3.42e-08 |      9.83e-06 |      4.11e-04 |      5.60e-03 |
|     24 |     480 |     3.13e-09 |      2.03e-06 |      1.44e-04 |      2.83e-03 |
|     27 |     540 |     2.85e-10 |      4.17e-07 |      5.06e-05 |      1.44e-03 |
|     30 |     600 |     2.60e-11 |      8.60e-08 |      1.78e-05 |      7.30e-04 |

### Case 2: Blocks with boosted descendants

Once one of a block's descendants (successors) has been boosted by a certificate, it is much more difficult for an adversary to cause it to be rolled back because they adversary must overcome both count of blocks on the preferred, honest chain and the boost that chain has already received.

The *Healing from adversarial boost* section above provides the machinery for estimating the probability of an adversary building a private fork that has more weight than a preferred, honest chain that has been boosted. The scenario plays out as follows:

1. Both the honest chain and an initially private adversarial chain have a common prefix that precedes the last boosted block.
2. The adversary privately grows their chain.
3. When the adversary's chain is becomes long enough to overcome both the honest blocks and the boost, the adversarial chain is published and all parties see that it is longer than the honest chain.
4. Hence the newly published adversarial chain becomes the preferred chain, and all parties build upon that.
5. Therefore the preferred chain does not include any transactions that were in blocks of the honest chain after the common prefix.

Typically, the adversary would only have a round's length of slots to build sufficient blocks to overcome the boosted, honest, preferred fork. After that, the preferred fork would typically receive another boost, making it even more difficult for the adversary to overcome it. The table below shows the probability that of non-settlement for a block after the common prefix but not after the subsequent boosted block on the honest chain, given a 5% active slot coefficient and a 5 blocks/certificate boost.

| Round Length | 5% Adversary | 10% Adversary | 15% Adversary | 20% Adversary | 45% Adversary |
| -----------: | -----------: | ------------: | ------------: | ------------: | ------------: |
|           60 |     3.09e-08 |      1.08e-06 |      8.94e-06 |      4.07e-05 |      3.10e-03 |
|           90 |     5.91e-08 |      2.27e-06 |      2.03e-05 |      9.91e-05 |      9.36e-03 |
|          120 |     6.32e-08 |      2.73e-06 |      2.70e-05 |      1.44e-04 |      1.74e-02 |
|          150 |     5.01e-08 |      2.49e-06 |      2.77e-05 |      1.62e-04 |      2.57e-02 |
|          180 |     3.31e-08 |      1.94e-06 |      2.45e-05 |      1.59e-04 |      3.37e-02 |
|          240 |     1.07e-08 |      8.98e-07 |      1.51e-05 |      1.23e-04 |      4.74e-02 |
|          300 |     2.73e-09 |      3.44e-07 |      7.88e-06 |      8.19e-05 |      5.80e-02 |
|          360 |     6.15e-10 |      1.20e-07 |      3.78e-06 |      5.04e-05 |      6.62e-02 |
|          420 |     1.29e-10 |      3.94e-08 |      1.73e-06 |      2.96e-05 |      7.23e-02 |
|          480 |     2.57e-11 |      1.25e-08 |      7.65e-07 |      1.70e-05 |      7.70e-02 |
|          540 |     4.98e-12 |      3.88e-09 |      3.33e-07 |      9.56e-06 |      8.05e-02 |
|          600 |     9.43e-13 |      1.19e-09 |      1.43e-07 |      5.32e-06 |      8.31e-02 |

A boost of 10 blocks/certificate makes the successful adversarial behavior even less likely.

| Round Length | 5% Adversary | 10% Adversary | 15% Adversary | 20% Adversary | 45% Adversary |
| -----------: | -----------: | ------------: | ------------: | ------------: | ------------: |
|           60 |      < 1e-16 |      4.92e-14 |      2.98e-12 |      5.56e-11 |      2.23e-07 |
|           90 |     7.77e-16 |      8.89e-13 |      5.65e-11 |      1.10e-09 |      4.98e-06 |
|          120 |     3.55e-15 |      4.47e-12 |      3.01e-10 |      6.15e-09 |      3.27e-05 |
|          150 |     8.88e-15 |      1.16e-11 |      8.39e-10 |      1.82e-08 |      1.16e-04 |
|          180 |     1.38e-14 |      2.01e-11 |      1.59e-09 |      3.70e-08 |      2.90e-04 |
|          240 |     1.60e-14 |      2.97e-11 |      2.87e-09 |      7.93e-08 |      9.83e-04 |
|          300 |     1.05e-14 |      2.53e-11 |      3.08e-09 |      1.03e-07 |      2.13e-03 |
|          360 |     4.77e-15 |      1.57e-11 |      2.48e-09 |      1.02e-07 |      3.62e-03 |
|          420 |     1.55e-15 |      7.98e-12 |      1.67e-09 |      8.59e-08 |      5.31e-03 |
|          480 |     4.44e-16 |      3.56e-12 |      9.96e-10 |      6.46e-08 |      7.08e-03 |
|          540 |     4.44e-16 |      1.45e-12 |      5.49e-10 |      4.52e-08 |      8.85e-03 |
|          600 |     2.22e-16 |      5.54e-13 |      2.86e-10 |      3.00e-08 |      1.06e-02 |

A boost of 15 blocks/certificate makes the successful adversarial behavior even less likely.

| Round Length | 5% Adversary | 10% Adversary | 15% Adversary | 20% Adversary | 45% Adversary |
| -----------: | -----------: | ------------: | ------------: | ------------: | ------------: |
|           60 |      < 1e-16 |       < 1e-16 |       < 1e-16 |       < 1e-16 |      9.81e-13 |
|           90 |      < 1e-16 |       < 1e-16 |      2.22e-16 |      8.88e-16 |      2.24e-10 |
|          120 |      < 1e-16 |       < 1e-16 |      2.22e-16 |      2.39e-14 |      6.59e-09 |
|          150 |     1.11e-16 |      1.11e-16 |      2.78e-15 |      2.19e-13 |      6.90e-08 |
|          180 |      < 1e-16 |      2.22e-16 |      1.18e-14 |      1.07e-12 |      3.91e-07 |
|          240 |      < 1e-16 |      3.33e-16 |      7.89e-14 |      8.19e-12 |      4.29e-06 |
|          300 |     3.33e-16 |      4.44e-16 |      2.16e-13 |      2.61e-11 |      2.07e-05 |
|          360 |     1.11e-16 |      5.55e-16 |      3.49e-13 |      5.01e-11 |      6.26e-05 |
|          420 |      < 1e-16 |      6.66e-16 |      4.01e-13 |      6.97e-11 |      1.42e-04 |
|          480 |      < 1e-16 |      2.22e-16 |      3.68e-13 |      7.81e-11 |      2.65e-04 |
|          540 |     3.33e-16 |      2.22e-16 |      2.88e-13 |      7.53e-11 |      4.35e-04 |
|          600 |     2.22e-16 |      3.33e-16 |      2.00e-13 |      6.51e-11 |      6.47e-04 |


### Recommendations for Peras parameters

Based on the analysis of adversarial scenarios, a reasonable set of default protocol parameters for further study and simulation is show in the table below. The optimal values for a real-life blockchain would depend strongly upon external requirements such as balancing settlement time against resisting adversarial behavior at high values of adversarial stake. This set of parameters is focused on the use case of knowing soon whether a block is settled or rolled back; other sets of parameters would be optimal for use cases that reduce the probability of roll-back at the expense of waiting longer for settlement.

| Parameter              | Symbol           | Units   | Value | Rationale                                                            |
| ---------------------- | ---------------- | ------- | ----: | -------------------------------------------------------------------- |
| Round length           | $U$              | slots   |    90 | Settlement/non-settlement in under two minutes.                      |
| Block-selection offset | $L$              | slots   |    30 | Several multiples of $\Delta$ to ensure block diffusion.             |
| Certification boost    | $B$              | blocks  |    15 | Negligible probability to roll back boosted block.                   |
| Security parameter     | $k_\text{peras}$ | blocks  |  3150 | Determined by the Praos security parameter and the boost.            |
| Certificate expiration | $A$              | slots   | 27000 | Determined by the Praos security parameter and boost.                |
| Chain-ignorance period | $R$              | rounds  |   300 | Determined by the Praos security parameter, round length, and boost. |
| Cool-down period       | $K$              | rounds  |   780 | Determined by the Praos security parameter, round length and boost.  |
| Committee size         | $n$              | parties |   900 | 1 ppm probability of no honest quorum at 10% adversarial stake.      |
| Quorum size            | $\tau$           | parties |   675 | Three-quarters of committee size.                                    |

A *block-selection offset* of $L = 30 \text{\,slots}$ allows plenty of time for blocks to diffuse to voters before a vote occurs. Combining this with a *round length* of $U = 90 \text{\, slots}$ ensures that there is certainty in $U + L = 120 \text{\,slots}$ as to whether a block has been cemented onto the preferred chain by the presence of a certificate for a subsequent block. That certainty of not rolling back certified blocks is provided by a *certification boost* of $B = 15 \text{\,blocks}$ because of the infinitesimal probability of forging that many blocks on a non-preferred fork within the time $U$. Thus, anyone seeing a transaction appearing in a block need wait no more than two minutes to be certain whether the transaction is on the preferred chain (effectively permanently, less than a one in a trillion probability even at 45% adversarial stake) versus having been discarded because of a roll back. Unless the transaction has a stringent time-to-live (TTL) constraint, it can be resubmitted in the first $U - L = 60 \text{\,slots}$ of the current round, or in a subsequent round.

> [!WARNING]
> The security-related computations in the next paragraph are not rigorous with respect to the healing, chain-quality, and common-prefix times, so they need correction after the research team reviews them and proposes a better approach.

The Praos security parameter $k_\text{praos} = 2160 \text{\,blocks} \approx 43200 \text{\,slots} = 12 \text{\,hours}$ implies a ~17% probability of a longer private adversarial chain at 49% adversarial stake. At that same probability, having to overcome a $B = 15 \text{\,blocks}$ adversarial boost would require $k_\text{peras} \approx 70200 \text{\,slots} = 3510 \text{\,blocks} = 19.5 \text{\,hours}$. This determines the *certificate-expiration time* as $A = k_\text{peras} - k_\text{praos} = 27000 \text{\,slots}$, the *chain-ignorance period* as $R = \left\lceil A / U \right\rceil = 300 \text{\,rounds}$, and the *cool-down period* as $K = \left\lceil k_\text{peras} / U \right\rceil = 780 \text{\,rounds}$.

The *committee size* of $n = 900 \text{\,parties}$ corresponds to a one in a million chance of not reaching a quorum if 10% of the parties do not vote for the majority block (either because they are adversarial, offline, didn't receive the block, or chose to vote for a block on a non-preferred fork). This "no quorum" probability is equivalent to one missed quorum in every 1.2 years. The *quorum size* of $\tau = \left\lceil 3 n / 4 \right\rceil = 675 \text{\,parties}$ is computed from this.


## Versioning

This document describes the *pre-alpha* version of the Peras protocol. We anticipate a subsequent, separate CIP for an *alpha* or *beta* version of the protocol. That version will add strong guarantees for block selection prior to the voting process and will constitute a layer built upon this pre-alpha version.

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
