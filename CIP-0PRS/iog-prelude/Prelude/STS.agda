module Prelude.STS where

open import Prelude.Init
open import Prelude.InferenceRules

-- State transition systems.
--   ∙ inheriting environment of type Γ
--   ∙ between states of type S
--   ∙ signalled by an input of type I
STS : Type → Type → Type → Type₁
STS Γ S I = Γ → S → I → S → Type

private variable Γ S I : Type

-- Functional predicates (a.k.a. uniquely satisfiable).
Functional : {S : Type ℓ} (P : Pred S ℓ′) → Type (ℓ ⊔ₗ ℓ′)
Functional P = ∀ {s s′} → P s → P s′ → s ≡ s′

-- Computational transitions.
record Computational (_⊢_—[_]→_ : STS Γ S I) : Type₁ where
  field
    functional : ∀ {γ s i} → Functional (γ ⊢ s —[ i ]→_)
    decidable  : ∀ {γ} s i → Dec $ ∃ (γ ⊢ s —[ i ]→_)

  -- From decidability, we extract a decision procedure that calculates the next state.
  compute : {γ : Γ} → S → I → Maybe S
  compute {γ} s i
    with decidable {γ} s i
  ... | no _ = nothing
  ... | yes (s′ , _) = just s′

  -- From functionality, we can prove that the decision procedure is sound *and complete*.
  completeness : ∀ {γ} s i s′ →
    γ ⊢ s —[ i ]→ s′
    ─────────────────────────
    compute {γ} s i ≡ just s′
  completeness {γ} s i s′ s→
    with decidable {γ} s i
  ... | no ¬s→ = ⊥-elim $ ¬s→ (-, s→)
  ... | yes (_ , s→′) = cong just (functional s→′ s→)
open Computational ⦃...⦄ public
  renaming (functional to compFun; decidable to compDec)

-- Reflexive transitive closure of a state transition system.
module _ {Γ S I : Type} (_⊢_—[_]→_ : STS Γ S I) where mutual
  private variable
    γ : Γ
    s s′ s″ : S
    i : I
    is : List I

  private
    _⊢_—[_]→∗_ : STS Γ S (List I)
    _⊢_—[_]→∗_ = _∗

  data _∗ : STS Γ S (List I) where
    [] :
        ─────────────────
        γ ⊢ s —[ [] ]→∗ s

    _∷_ :
      ∙ γ ⊢ s  —[ i ]→ s′
      ∙ γ ⊢ s′ —[ is ]→∗ s″
        ───────────────────────
        γ ⊢ s  —[ i ∷ is ]→∗ s″

module _ {_⊢_—[_]→_ : STS Γ S I} (let _⊢_—[_]→∗_ = _⊢_—[_]→_ ∗) where instance
  Computational∗ : ⦃ Computational _⊢_—[_]→_ ⦄ → Computational _⊢_—[_]→∗_
  Computational∗ = record {go} where module go where
    functional : ∀ {γ s i} → Functional (γ ⊢ s —[ i ]→∗_)
    functional []       []         = refl
    functional (p ∷ ps) (p′ ∷ ps′) =
      let ps = subst (λ ◆ → _ ⊢ ◆ —[ _ ]→∗ _) (compFun p p′) ps in
      functional ps ps′

    decidable : ∀ {γ} s i → Dec $ ∃ (γ ⊢ s —[ i ]→∗_)
    decidable _ [] = yes (-, [])
    decidable s (i ∷ is)
      with compDec s i
    ... | no ¬p
      = no λ where (_ , (p ∷ _)) → ¬p (-, p)
    ... | yes (s′ , p)
      = mapDec (map₂ (p ∷_))
              (map₂ λ where
                (p′ ∷ ps) → subst (λ ◆ → _ ⊢ ◆ —[ _ ]→∗ _) (compFun p′ p) ps)
              (decidable s′ is)

-- *Step-indexed* reflexive transitive closure of a state transition system.
module _ {S I : Type} (_⊢_—[_]→_ : STS ℕ S I) where mutual
  private variable
    n n′ : ℕ
    s s′ s″ : S
    sⁱ sⁱ′ : ℕ × S
    i : I
    is : List I

  private
    _⊢_—[_]→∗_ : STS ⊤ (ℕ × S) (List I)
    _⊢_—[_]→∗_ = _∗ⁱ

  data _∗ⁱ : STS ⊤ (ℕ × S) (List I) where
    [] :
        ───────────────────
        _ ⊢ sⁱ —[ [] ]→∗ sⁱ

    _∷_ :
      ∙ n ⊢ s  —[ i ]→ s′
      ∙ _ ⊢ (suc n , s′) —[ is ]→∗ sⁱ
        ─────────────────────────────
        _ ⊢ (n , s)  —[ i ∷ is ]→∗ sⁱ

module _ {_⊢_—[_]→_ : STS ℕ S I} (let _⊢_—[_]→∗_ = _⊢_—[_]→_ ∗ⁱ) where instance
  Computational∗ⁱ : ⦃ Computational _⊢_—[_]→_ ⦄ → Computational _⊢_—[_]→∗_
  Computational∗ⁱ = record {go} where module go where
    functional : ∀ {s i} → Functional (_ ⊢ s —[ i ]→∗_)
    functional []       []         = refl
    functional (p ∷ ps) (p′ ∷ ps′) =
      let ps = subst (λ ◆ → _ ⊢ _ , ◆ —[ _ ]→∗ _) (compFun p p′) ps in
      functional ps ps′

    decidable : ∀ s i → Dec $ ∃ (_ ⊢ s —[ i ]→∗_)
    decidable _       [] = yes (-, [])
    decidable (n , s) (i ∷ is)
      with compDec {γ = n} s i
    ... | no ¬p
      = no λ where (_ , (p ∷ _)) → ¬p (-, p)
    ... | yes (s′ , p)
      = mapDec (map₂ (p ∷_))
               (map₂ λ where
                 (p′ ∷ ps) → subst (λ ◆ → _ ⊢ _ , ◆ —[ _ ]→∗ _) (compFun p′ p) ps)
               (decidable (suc n , s′) is)

-- Class of state transition systems.
record HasTransition (Γ S I : Type) : Type₁ where
  field _⊢_—[_]→_ : STS Γ S I
  _⊢_—[_]→∗_ : STS Γ S (List I)
  _⊢_—[_]→∗_ = _⊢_—[_]→_ ∗
open HasTransition ⦃...⦄ public

_⊢_—[_]→∗ⁱ_ : ⦃ HasTransition ℕ S I ⦄ → STS ⊤ (ℕ × S) (List I)
_⊢_—[_]→∗ⁱ_ = _⊢_—[_]→_ ∗ⁱ
