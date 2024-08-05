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
Created: 2024-07-31
License: Apache-2.0
---

> [!IMPORTANT]
>
> Decisions needed:
> - [ ] Do we want the CIP to be type-checked by the Agda compiler?
>     - [ ] *Option 1:* Write the CIP as a single, self-contained `.lagda.md` file.
>         - *Pro:* completely self-contained
>         - *Con:* need to flatten our `src/` files into a single file
>     - [ ] *Option 2:* Put all of the Agda code in a `src/` folder within the CIP's folder.
>         - *Pro:* the existing `src/` can be copied over into the CIP, after a little clean-up
>         - *Con:* the Agda specification won't appear in the top-level CIP file, but will be reachable by links
>     - [ ] *Option 3:* Copy-and-paste the Agda code from our `src/` into the CIP
>         - *Pro:* smaller CIP file
>         - *Con:* not type-checked
> - [ ] Should we only include the ALBA certificates in the specification? It's confusing to propose two types of certificate. Maybe the Mithril-certificate section could be moved to an appendix?
> - [ ] The benchmarks don't properly belong in the "Specification" section, so they're being moved to "Resources".
> - [ ] How much of the evidence and analyses should be embedded in this document versus referencing the technical reports?
> - [ ] Editing
>     - [ ] Edit in a folder of `peras-design`
>     - [ ] Edit in a fork of the CIP repo
> - [ ] Include the research team as CIP authors?
> - [ ] In order to speed things up, should we also draft the meta-CIP that creates the "Consensus" category?

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

* Look at [Leios spec](https://github.com/cardano-foundation/CIPs/blob/ouroboros-leios/CIP-0079/README.md) for inspiration
* [CIP-001](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0001) guidelines

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
We propose Peras, an enhancement to the Ouroboros Praos protocol that introduces a voting layer for optimistic fast settlement. 

Peras, or more precisely Ouroboros Peras, is an extension of Ouroboros Praos that addresses one of the known issues of blockchains based on Nakamoto-style consensus, namely settlement time. Peras achieves that goal while being self-healing, preserving the security of Praos, and being light on resources.


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

The following informal, non-normative, pseudo-imperative summary of the Peras protocol is provided as an index into the formal Agda specification. Peras relies on a few key concepts:

- The progression of the blockchain's *slots* is partitioned in *rounds* of equal length.
- In each round a *committee of voters* is selected via a sortition algorithm.
- Members of the committee may *vote* for a block in the history of their preferred chain.
- A *quorum* of votes during the same round for the same block is memorialized as a *certificate*.
- A quorum of votes for a block gives that block's weight a *boost*.
- The *weight* of a chain is its length plus the total of the boosts its blocks have received.
- The lack of a quorum in a round typically triggers a *cool-down period* where no voting occurs.
- Relevant vote certificates are typically *recorded* in a block near the start and finish of a cool-down period.
- Certificates *expire* after a specified number of slots if they haven't been included in a block.

> [!IMPORTANT]
>
> If we retain this subsection, provide links from it to the corresponding parts of the Agda specification later in this document.
>
> The text needs review by the research team because it risks self-plagarizing.

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

### Normative protocol specification in Agda

The following relational specification for Peras uses [Agda 2.6.4.1](https://github.com/agda/agda/tree/v2.6.4.1) and the [Agda Standard Library 2.0](https://github.com/agda/agda-stdlib/tree/v2.0). The repository [github:input-output-hk/peras-design](https://github.com/input-output-hk/peras-design/tree/main) provides a Nix-based environment for compiling and executing Peras's specification.

> [!IMPORTANT]
>
> Brian would like to signifcantly expand the explanatory text in this section and import the definitions for `Block` etc. However, we first need to figure out how to sync the `peras-design` repo with this document.
>
> ----- START OF PASTED TEXT -----

```agda
module Peras.SmallStep where
```

The small-step semantics of the **Ouroboros Peras** protocol define the
evolution of the global state of the system modelling *honest* and *adversarial*
parties. The number of parties is fixed during the execution of the protocol and
the list of parties has to be provided as a module parameter. In addition the
model is parameterized by the lotteries (for slot leadership and voting
committee membership) as well as the type of the block tree. Furthermore
adversarial parties share generic, adversarial state.

References:

* Formalizing Nakamoto-Style Proof of Stake, Søren Eller Thomsen and Bas Spitters

#### Parameters

The parameters for the *Peras* protocol and hash functions are defined as
instance arguments of the module.

```agda
module _ ⦃ _ : Hashable Block ⦄
         ⦃ _ : Hashable (List Tx) ⦄
         ⦃ _ : Params ⦄
         ⦃ _ : Network ⦄
         ⦃ _ : Postulates ⦄

         where
```
  The block tree, resp. the validity of the chain is defined with respect of the
  parameters.
```agda
  open Hashable ⦃...⦄
  open Params ⦃...⦄
  open Network ⦃...⦄
  open Postulates ⦃...⦄
```

#### Messages

Messages for sending and receiving chains and votes. Note, in the *Peras* protocol
certificates are not diffused explicitly.
```agda
  data Message : Type where
    ChainMsg : Chain → Message
    VoteMsg : Vote → Message
```

#### Block-tree

A block-tree is defined by properties - an implementation of the block-tree
has to fulfil all the properties mentioned below:

```agda
  record IsTreeType {T : Type}
                    (tree₀ : T)
                    (newChain : T → Chain → T)
                    (allChains : T → List Chain)
                    (preferredChain : T → Chain)
                    (addVote : T → Vote → T)
                    (votes : T → List Vote)
                    (certs : T → List Certificate)
                    (cert₀ : Certificate)
         : Type₁ where

    field
```
Properties that must hold with respect to chains, certificates and votes.
```agda
      instantiated :
        preferredChain tree₀ ≡ []

      instantiated-certs :
        certs tree₀ ≡ cert₀ ∷ []

      instantiated-votes :
        votes tree₀ ≡ []

      extendable-chain : ∀ (t : T) (c : Chain)
        → certs (newChain t c) ≡ certsFromChain c ++ certs t

      valid : ∀ (t : T)
        → ValidChain (preferredChain t)

      optimal : ∀ (c : Chain) (t : T)
        → let
            b = preferredChain t
            cts = certs t
          in
          ValidChain c
        → c ∈ allChains t
        → ∥ c ∥ cts ≤ ∥ b ∥ cts

      self-contained : ∀ (t : T)
        → preferredChain t ∈ allChains t

      valid-votes : ∀ (t : T)
        → All ValidVote (votes t)

      unique-votes : ∀ (t : T) (v : Vote)
        → let vs = votes t
          in
          v ∈ vs
        → vs ≡ votes (addVote t v)

      no-equivocations : ∀ (t : T) (v : Vote)
        → let vs = votes t
          in
          Any (v ∻_) vs
        → vs ≡ votes (addVote t v)

      quorum-cert : ∀ (t : T) (b : Block) (r : ℕ)
        → length (filter (λ {v →
                    (getRoundNumber (votingRound v) ≟ r)
              ×-dec (blockHash v ≟-BlockHash hash b)}
            ) (votes t)) ≥ τ
        → Any (λ {c →
            (getRoundNumber (round c) ≡ r)
          × (blockRef c ≡ hash b) }) (certs t)
```
In addition to chains the block-tree manages votes and certificates as well.
The block-tree type is defined as follows:
```agda
  record TreeType (T : Type) : Type₁ where

    field
      tree₀ : T
      newChain : T → Chain → T
      allChains : T → List Chain
      preferredChain : T → Chain

      addVote : T → Vote → T

      votes : T → List Vote
      certs : T → List Certificate

    cert₀ : Certificate
    cert₀ = MkCertificate (MkRoundNumber 0) (MkHash emptyBS)

    field
      is-TreeType : IsTreeType
                      tree₀ newChain allChains preferredChain
                      addVote votes certs cert₀

    latestCertOnChain : T → Certificate
    latestCertOnChain =
      latestCert cert₀ ∘ catMaybes ∘ map certificate ∘ preferredChain

    latestCertSeen : T → Certificate
    latestCertSeen = latestCert cert₀ ∘ certs

    hasCert : RoundNumber → T → Type
    hasCert (MkRoundNumber r) = Any ((r ≡_) ∘ roundNumber) ∘ certs

    hasCert? : (r : RoundNumber) (t : T) → Dec (hasCert r t)
    hasCert? (MkRoundNumber r) = any? ((r ≟_) ∘ roundNumber) ∘ certs

    hasVote : RoundNumber → T → Type
    hasVote (MkRoundNumber r) = Any ((r ≡_) ∘ votingRound') ∘ votes

    hasVote? : (r : RoundNumber) (t : T) → Dec (hasVote r t)
    hasVote? (MkRoundNumber r) = any? ((r ≟_) ∘ votingRound') ∘ votes

    preferredChain′ : SlotNumber → T → Chain
    preferredChain′ (MkSlotNumber sl) =
      let cond = (_≤? sl) ∘ slotNumber'
      in filter cond ∘ preferredChain

    allBlocks : T → List Block
    allBlocks = concat ∘ allChains
```

#### Additional parameters

In order to define the semantics the following parameters are required
additionally:

  * The type of the block-tree
  * adversarialState₀ is the initial adversarial state
  * Tx selection function per party and slot number
  * The list of parties

```agda
  module Semantics
           {T : Type} {blockTree : TreeType T}
           {S : Type} {adversarialState₀ : S}
           {txSelection : SlotNumber → PartyId → List Tx}
           {parties : Parties} -- TODO: use parties from blockTrees
                               -- i.e. allow dynamic participation

           where

    open TreeType blockTree

    instance
      Default-T : Default T
      Default-T .def = tree₀
```

#### Block-tree update

Updating the block-tree upon receiving a message for vote and block messages.

```agda
    data _[_]→_ : T → Message → T → Type where

      VoteReceived : ∀ {v t} →
          ────────────────────────────
          t [ VoteMsg v ]→ addVote t v

      ChainReceived : ∀ {c t} →
          ──────────────────────────────
          t [ ChainMsg c ]→ newChain t c
```

#### Vote in round

When does a party vote in a round? The protocol expects regular voting, i.e. if
in the previous round a quorum has been achieved or that voting resumes after a
cool-down phase.

#### BlockSelection
```agda
    BlockSelection : SlotNumber → T → Maybe Block
    BlockSelection (MkSlotNumber s) =
      head ∘ filter (λ {b → (slotNumber' b) ≤? (s ∸ L)}) ∘ preferredChain
```
```agda
    ChainExtends : Maybe Block → Certificate → Chain → Type
    ChainExtends nothing _ _ = ⊥
    ChainExtends (just b) c =
      Any (λ block → (hash block ≡ blockRef c))
        ∘ L.dropWhile (λ block' → ¬? (hash block' ≟-BlockHash hash b))
```

#### Voting rules

VR-1A: A party has seen a certificate cert-r−1 for round r−1
```agda
    VotingRule-1A : RoundNumber → T → Type
    VotingRule-1A (MkRoundNumber r) t = r ≡ roundNumber (latestCertSeen t) + 1
```
VR-1B: The  extends the block certified by cert-r−1,
```agda
    VotingRule-1B : SlotNumber → T → Type
    VotingRule-1B s t =
      Any (ChainExtends (BlockSelection s t) (latestCertSeen t)) (allChains t)
```
VR-1: Both VR-1A and VR-1B hold
```agda
    VotingRule-1 : SlotNumber → T → Type
    VotingRule-1 s t =
        VotingRule-1A (v-round s) t
      × VotingRule-1B s t
```
VR-2A: The last certificate a party has seen is from a round at least R rounds back
```agda
    VotingRule-2A : RoundNumber → T → Type
    VotingRule-2A (MkRoundNumber r) t = r ≥ roundNumber (latestCertSeen t) + R
```
VR-2B: The last certificate included in a party's current chain is from a round exactly
c⋆K rounds ago for some c : ℕ, c ≥ 0
```agda
    VotingRule-2B : RoundNumber → T → Type
    VotingRule-2B (MkRoundNumber r) t =
        r > roundNumber (latestCertOnChain t)
      × r mod K ≡ (roundNumber (latestCertOnChain t)) mod K
```
VR-2: Both VR-2A and VR-2B hold
```agda
    VotingRule-2 : RoundNumber → T → Type
    VotingRule-2 r t =
        VotingRule-2A r t
      × VotingRule-2B r t
```
If either VR-1A and VR-1B or VR-2A and VR-2B hold, voting is expected
```agda
    VotingRule : SlotNumber → T → Type
    VotingRule s t =
        VotingRule-1 s t
      ⊎ VotingRule-2 (v-round s) t
```

#### State

The small-step semantics rely on a global state, which consists of the following fields:

* Current slot of the system
* Map with local state per party
* All the messages that have been sent but not yet been delivered
* All the messages that have been sent
* Adversarial state

```agda
    record State : Type where
      constructor ⟦_,_,_,_,_⟧
      field
        clock : SlotNumber
        blockTrees : AssocList PartyId T
        messages : List Envelope
        history : List Message
        adversarialState : S

      blockTrees' : List T
      blockTrees' = map proj₂ blockTrees

      v-rnd : RoundNumber
      v-rnd = v-round clock

      v-rnd' : ℕ
      v-rnd' = getRoundNumber v-rnd
```

#### Progress

Rather than keeping track of progress, we introduce a predicate stating that all
messages that are not delayed have been delivered. This is a precondition that
must hold before transitioning to the next slot.
```agda
    Fetched : State → Type
    Fetched = All (λ { z → delay z ≢ 𝟘 }) ∘ messages
      where open State
```
Predicate for a global state stating that the current slot is the last slot of
a voting round.
```agda
    LastSlotInRound : State → Type
    LastSlotInRound M =
      suc (rnd (getSlotNumber clock)) ≡ rnd (suc (getSlotNumber clock))
      where open State M
```
```agda
    LastSlotInRound? : (s : State) → Dec (LastSlotInRound s)
    LastSlotInRound? M =
      suc (rnd (getSlotNumber clock)) ≟ rnd (suc (getSlotNumber clock))
      where open State M
```
Predicate for a global state stating that the next slot will be in a new voting
round.
```agda
    NextSlotInSameRound : State → Type
    NextSlotInSameRound M =
      rnd (getSlotNumber clock) ≡ rnd (suc (getSlotNumber clock))
      where open State M
```
```agda
    NextSlotInSameRound? : (s : State) → Dec (NextSlotInSameRound s)
    NextSlotInSameRound? M =
      rnd (getSlotNumber clock) ≟ rnd (suc (getSlotNumber clock))
      where open State M
```
Predicate for a global state asserting that parties of the voting committee for
a the current voting round have voted. This is needed as a condition when
transitioning from one voting round to another.

**TODO**: Properly define the condition for required votes
```agda
    RequiredVotes : State → Type
    RequiredVotes M =
         Any (VotingRule clock ∘ proj₂) blockTrees
       → Any (hasVote (v-round clock) ∘ proj₂) blockTrees
      where open State M
```
Ticking the global clock increments the slot number and decrements the delay of
all the messages in the message buffer.
```agda
    tick : State → State
    tick M =
      record M
        { clock = next clock
        ; messages =
            map (λ where e → record e { delay = pred (delay e) })
              messages
        }
      where open State M
```
Updating the global state inserting the updated block-tree for a given party,
adding messages to the message buffer for the other parties and appending the
history
```agda
    _,_,_,_⇑_ : Message → Delay → PartyId → T → State → State
    m , d , p , l ⇑ M =
      record M
        { blockTrees = set p l blockTrees
        ; messages =
            map (uncurry ⦅_,_, m , d ⦆)
              (filter (¬? ∘ (p ≟_) ∘ proj₁) parties)
            ++ messages
        ; history = m ∷ history
        }
      where open State M

    add_to_diffuse_ : (Message × Delay × PartyId) → T → State → State
    add (m@(ChainMsg x) , d , p) to t diffuse M = m , d , p , newChain t x ⇑ M
    add (m@(VoteMsg x) , d , p) to t diffuse M = m , d , p , addVote t x ⇑ M
```

#### Fetching

A party receives messages from the global state by fetching messages assigned to
the party, updating the local block tree and putting the local state back into
the global state.

```agda
    data _⊢_[_]⇀_ : {p : PartyId} → Honesty p → State → Message → State → Type
      where
```
An honest party consumes a message from the global message buffer and updates
the local state
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
An adversarial party might delay a message
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

Helper function for creating a vote
```agda
    createVote : SlotNumber → PartyId → MembershipProof → Signature → Hash Block → Vote
    createVote s p prf sig hb =
      record
        { votingRound = v-round s
        ; creatorId = p
        ; proofM = prf
        ; blockHash = hb
        ; signature = sig
        }
```
A party can vote for a block, if
  * the current slot is the first slot in a voting round
  * the party is a member of the voting committee
  * the chain is not in a cool-down phase

Voting updates the party's local state and for all other parties a message
is added to be consumed immediately.
```agda
    infix 2 _⊢_⇉_

    data _⊢_⇉_ : {p : PartyId} → Honesty p → State → State → Type where

      honest : ∀ {p} {t} {M} {π} {σ} {b}
        → let
            open State
            s = clock M
            r = v-round s
            v = createVote s p π σ (hash b)
          in
        ∙ BlockSelection s t ≡ just b
        ∙ blockTrees M ⁉ p ≡ just t
        ∙ IsVoteSignature v σ
        ∙ StartOfRound s r
        ∙ IsCommitteeMember p r π
        ∙ VotingRule s t
          ───────────────────────────────────
          Honest {p} ⊢
            M ⇉ add (VoteMsg v , 𝟘 , p) to t
                diffuse M
```
Rather than creating a delayed vote, an adversary can honestly create it and
delay the message.


#### Block creation

Certificates are conditionally added to a block. The following function determines
if there needs to be a certificate provided for a given voting round and a local
block-tree. The conditions are as follows

a) There is no certificate from 2 rounds ago in certs
b) The last seen certificate is not expired
c) The last seen certificate is from a later round than
   the last certificate on chain

```agda
    needCert : RoundNumber → T → Maybe Certificate
    needCert (MkRoundNumber r) t =
      let
        cert⋆ = latestCertOnChain t
        cert′ = latestCertSeen t
      in
        if not (any (λ {c → ⌊ roundNumber c + 2 ≟ r ⌋}) (certs t)) -- (a)
           ∧ (r ≤ᵇ A + roundNumber cert′)                          -- (b)
           ∧ (roundNumber cert⋆ <ᵇ roundNumber cert′)              -- (c)
        then just cert′
        else nothing
```
Helper function for creating a block
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
            in blockHash
                 record
                   { blockHash = hash txs
                   ; payload = txs
                   }
        ; signature = σ
        }
```
A party can create a new block by adding it to the local block tree and
diffuse the block creation messages to the other parties. Block creation is
possible, if as in *Praos*

  * the block signature is correct
  * the party is the slot leader

Block creation updates the party's local state and for all other parties a
message is added to the message buffer
```agda
    infix 2 _⊢_↷_

    data _⊢_↷_ : {p : PartyId} → Honesty p → State → State → Type where

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

#### Small-step semantics

The small-step semantics describe the evolution of the global state.
```agda
    variable
      M N O : State
      p : PartyId
      h : Honesty p
```
The relation allows

* Fetching messages at the beginning of each slot
* Block creation
* Voting
* Transitioning to next slot in the same voting round
* Transitioning to next slot in a new voting round

Note, when transitioning to the next slot we need to distinguish whether the
next slot is in the same or a new voting round. This is necessary in order to
detect adversarial behaviour with respect to voting (adversarialy not voting
in a voting round)
```agda
    data _↝_ : State → State → Type where

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

#### Reflexive, transitive closure
List-like structure for defining execution paths.
```agda
    infix  2 _↝⋆_
    infixr 2 _↣_
    infix  3 ∎

    data _↝⋆_ : State → State → Type where
      ∎ : M ↝⋆ M
      _↣_ : M ↝ N → N ↝⋆ O → M ↝⋆ O
```

#### Transitions of voting rounds
Transitioning of voting rounds can be described with respect of the small-step
semantics.
```agda
    data _↦_ : State → State → Type where

      NextRound : let open State in
          suc (v-rnd' M) ≡ v-rnd' N
        → M ↝⋆ N
        → M ↦ N
```

#### Reflexive, transitive closure
List-like structure for executions for voting round transitions
```agda
    infix  2 _↦⋆_
    infixr 2 _⨾_
    infix  3 ρ

    data _↦⋆_ : State → State → Type where
      ρ : M ↦⋆ M
      _⨾_ : M ↦ N → N ↦⋆ O → M ↦⋆ O
```

> [!IMPORTANT]
>
> ----- END OF PASTED TEXT -----

### Specification of votes

#### Overview

Voting in Peras is mimicked after the _sortition_ algorithm used in Praos, e.g it is based on the use of a _Verifiable Random Function_ (VRF) by each stake-pool operator guaranteeing the following properties:

* The probability for each voter to cast their vote in a given round is correlated to their share of total stake,
* It should be computationally impossible to predict a given SPO's schedule without access to their secret key VRF key,
* Verification of a voter's right to vote in a round should be efficiently computable,
* A vote should be unique and non-malleable. (This is a requirement for the use of efficient certificates aggregation, see [below](#alba-certificates).)

Additionally we would like the following property to be provided by our voting scheme:

* Voting should require minimal additional configuration (i.e., key management) for SPOs,
* Voting and certificates construction should be fast in order to ensure we do not interfere with other operations happening in the node.

We have experimented with two different algorithms for voting, which we detail below.

#### Structure of votes

We have used an identical structure for single `Vote`s, for both algorithms. We define this structure as a CDDL grammar, inspired by the [block header](https://github.com/input-output-hk/cardano-ledger/blob/e2aaf98b5ff2f0983059dc6ea9b1378c2112101a/eras/conway/impl/cddl-files/conway.cddl#L27) definition from cardano-ledger:

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

This definition relies on the following primitive types (drawn from Ledger definitions in [crypto.cddl](https://github.com/input-output-hk/cardano-ledger/blob/e2aaf98b5ff2f0983059dc6ea9b1378c2112101a/eras/conway/impl/cddl-files/crypto.cddl#L1))

```cddl
round_no = uint .size 8
voting_weight = uint .size 8
vrf_cert = [bytes, bytes .size 80]
hash32 = bytes .size 32
kes_vkey = bytes .size 32
kes_signature = bytes .size 448
kes_period = uint .size 8
```

As already mentioned, `Vote` mimicks the block header's structure which allows Cardano nodes to reuse their existing VRF and KES keys. Some additional notes:

* Total vote size is **710 bytes** with the above definition,
* Unless explicitly mentioned, `hash` function exclusively uses 32-bytes Blake2b-256 hashes,
* The `voter_id` is it's pool identifier, ie. the hash of the node's cold key.

#### Casting a vote

A vote is _cast_ by a node using the following process which paraphrases the [actual code](https://github.com/input-output-hk/peras-design/blob/4ab6fad30b1f8c9d83e5dfb2bd6f0fe235e1395c/peras-vote/src/Peras/Voting/Vote.hs#L293)

1. Define _nonce_ as the hash of the _epoch nonce_ concatenated to the `peras` string and the round number voted for encoded as 64-bits big endian value,
2. Generate a _VRF Certificate_ using the node's VRF key from this `nonce`,
3. Use the node's KES key with current KES period to sign the VRF certificate concatenated to the _block hash_ the node is voting for,
4. Compute _voting weight_ from the VRF certificate using _sortition_ algorithm (see details below).

#### Verifying a vote

[Vote verification](https://github.com/input-output-hk/peras-design/blob/34196ee6e06ee6060c189116b04a2666450c5b75/peras-vote/src/Peras/Voting/Vote.hs#L392) requires access to the current epoch's _stake distribution_ and _stake pool registration_ information.

1. Lookup the `voter_id` in the stake distribution and registration map to retrieve their current stake and VRF verification key,
2. Compute the _nonce_ (see above),
3. Verify VRF certificate matches nonce and verification key,
4. Verify KES signature,
5. Verify provided KES verification key based on stake pool's registered cold verification key and KES period,
6. Verify provided _voting weight_ according to voting algorithm.

#### Approaches to voter election

> [!IMPORTANT]
>
> These subsections are about implementation more than about specification. Should we rewrite this purely as a specification? We could link to the two implementations.

##### Leader-election like voting

The first algorithm is basically identical to the one used for [Mithril](https://mithril.network) signatures, and is also the one envisioned for [Leios](https://leios.cardano-scaling.org) (see Appendix D of the recent Leios paper). It is based on the following principles:

* The goal of the algorithm is to produce a number of votes targeting a certain threshold such that each voter receives a number of vote proportionate to $\sigma$, their fraction of total stake, according to the basic probability function $\phi(\sigma) = 1 - (1 - f)^\sigma$,
* There are various parameters to the algorithm:
    * $f$ is the fraction of slots that are "active" for voting
    * $m$ is the number of _lotteries_ each voter should try to get a vote for,
    * $k$ is the target total number of votes for each round (e.g., quorum) $k$ should be chosen such that $k = m \cdot \phi(0.5)$ to reach a majority quorum,
* When its turn to vote comes, each node run iterates over an index $i \in [1 \dots m]$, computes a hash from the _nonce_ and the index $i$, and compares this hash with $f(\sigma)$: if it is lower than or equal, then the node has one vote.
    * Note the computation $f(\sigma)$ is exactly identical to the one used for [leader election](https://github.com/intersectmbo/cardano-ledger/blob/f0d71456e5df5a05a29dc7c0ac9dd3d61819edc8/libs/cardano-protocol-tpraos/src/Cardano/Protocol/TPraos/BHeader.hs#L434).

We [prototyped](https://github.com/input-output-hk/peras-design/blob/73eabecd272c703f1e1ed0be7eeb437d937e1179/peras-vote/src/Peras/Voting/Vote.hs#L311) this approach in Haskell.

##### Sortition-like voting

The second algorithm is based on the _sortition_ process initially invented by [Algorand](https://web.archive.org/web/20170728124435id_/https://people.csail.mit.edu/nickolai/papers/gilad-algorand-eprint.pdf) and [implemented](https://github.com/algorand/sortition/blob/main/sortition.cpp) in their node. It is based on the same idea, namely that a node should have a number of votes proportional to their fraction of total stake, given a target "committee size" expressed as a fraction of total stake $p$. And it uses the fact the number of votes a single node should get based on these parameters follows a binomial distribution.

The process for voting is thus:

* Compute the individual probability of each "coin" to win a single vote $p$ as the ratio of expected committee size over total stake.
* Compute the binomial distribution $B(n,p)$ where $n$ is the node's stake.
* Compute a random number between 0 and 1 using _nonce_ as the denominator over maximum possible value (e.g., all bits set to 1) for the nonce as denominator.
* Use [bisection method](https://en.wikipedia.org/wiki/Bisection_method) to find the value corresponding to this probability in the CDF for the aforementioned distribution.

This yields a vote with some _weight_ attached to it "randomly" computed so that the overall sum of weights should be around expected committee size.

This method has also been [prototyped in Haskell](https://github.com/input-output-hk/peras-design/blob/73eabecd272c703f1e1ed0be7eeb437d937e1179/peras-vote/src/Peras/Voting/Vote.hs#L174).

### Specification of certificates

> [!CAUTION]
> We need to commit solely to ALBA or to Mirthril, and edit this section accordingly.

#### Mithril certificates

Mithril certificates' construction is described in details in the [Mithril](https://iohk.io/en/research/library/papers/mithril-stake-based-threshold-multisignatures/) paper and is implemented in the [mithril network](https://github.com/input-output-hk/mithril). It's also described in the [Leios paper](https://iohk.io/en/research/library/papers/high-throughput-blockchain-consensus-under-realistic-network-assumptions/), in the appendix, as a potential voting scheme for Leios, and implicitly Peras.

Mithril certificates have the following features:

* They depend on BLS-curve signatures aggregation to produce a so-called _State based Threshold Multi-Signature_ that's easy to verify,
* Each node relies on a _random lottery_ as described in the [previous section](#leader-election-like-voting) to produce a vote weighted by their share of total stake,
* The use of BLS signatures implies nodes will need to generate and exchange specialized keys for the purpose of voting, something we know from [Mithril](https://mithril.network/doc/mithril/mithril-protocol/certificates) is somewhat tricky as it requires some form of consensus to guarantee all nodes have the exact same view of the key set.

#### ALBA

[Approximate Lower Bound Arguments](https://iohk.io/en/research/library/papers/approximate-lower-bound-arguments/) or _ALBAs_ in short, are a novel cryptographic algorithm based on a _telescope_ construction providing a fast way to build compact certificates out of a large number of _unique_ items. A lot more details are provided in the paper, on the [website](https://alba.cardano-scaling.org) and the [GitHub repository](https://github.com/cardano-scaling/alba) where implementation is being developed, we only provide here some key information relevant to the use of ALBAs in Peras.

##### Proving & verification time

ALBA's expected proving time is benchmarked in the following picture which shows mean execution time for generating a proof depending on: The _total_ number of votes, the actual number of votes ($s_p$), the honest ratio ($n_p$). Note that as proving time increases exponentially when $s_p \rightarrow total \cdot n_p$, we only show here the situation when $s_p = total$ and $s_p = total - total \cdot n_p / 2$ to ensure graph stays legible.
![ALBA Proving Time](/img/alba-proving.png)

The following diagram is an excerpt from the ALBA benchmarks highlighting verification. Note these numbers do not take into account the time for verifying individual votes. As one can observe directly from these graphs, verification time is independent from the number of items and only depends on the $n_p/n_f$ ratio.
![ALBA Verification Time](/img/alba-verifying.png)

In practice, as the number of votes is expected to be in the 1000-2000 range, and there is ample time in a round to guarantee those votes are properly delivered to all potential voting nodes (see below), we can safely assume proving time of about 5 ms, and verification time under a millisecond.

##### Certificate size

For a given set of parameters, namely fixed values for $\lambda_{sec}$, $\lambda_{rel}$, and $n_p/n_f$, the proof size is perfectly linear and only depends on the size of each vote.

Varying the security parameter and the honest votes ratio for a fixed set of 1000 votes of size 200 yields the following diagram, showing the critical factor in proof size increase is the $n_p/n_f$ ratio: As this ratio decreases, the number of votes to include in proof grows superlinearly.

![Proof size vs. λ and honest votes ratio](/img/alba-proof-size-lambda.svg)

#### Benchmarks

> [!WARNING]
> The benchmarking data should be moved to the Resources section.

In the following tables we compare some relevant metrics between the two different kind of certificates we studied, Mithril certificates (using BLS signatures) and ALBA certificates (using KES signatures): Size of certificate in bytes, proving time (e.g., the time to construct a single vote), aggregation time (the time to build a certificate), and verification time.

For Mithril certificates, assuming parameters similar to mainnet's ($k=2422, m=20973, f=0.2$):

| Feature                         | Metric |
| ------------------------------- | ------ |
| Certificate size                | 56 kB  |
| Proving time (per vote)         | ~70 ms |
| Aggregation time                | 1.2 s  |
| Verification time (certificate) | 17 ms  |

For ALBA certificates, assuming 1000 votes, a honest to faulty ratio of 80/20, and security parameter $λ=128$. Note the proving time _does not_ take into account individual vote verification time, whereas certificate's verification time _includes_ votes verification time.

| Feature                         | Metric  |
| ------------------------------- | ------- |
| Certificate size                | 47 kB   |
| Proving time (per vote)         | ~133 us |
| Aggregation time                | ~5 ms   |
| Verification time (certificate) | 15 ms   |
|                                 |         |

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

## Attacks and Mitigations


## Resource Requirements

In this section, we evaluate the impact on the day-to-day operations of the Cardano network and cardano nodes of the deployment of Peras protocol, based on the data gathered over the course of project.

In this section, we evaluate the impact on the day-to-day operations of the Cardano network and cardano nodes of the deployment of Peras protocol, based on the data gathered over the course of project.

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



## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
