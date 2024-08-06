-- Finite maps as association lists
module Prelude.AssocList where

open import Prelude.Init
open import Prelude.DecEq
open import Prelude.Decidable
open import Prelude.Irrelevance
open import Prelude.Default

AssocList : Type → Type → Type
AssocList K V = List (K × V)

mapValues : ∀ {K V V′} → (V → V′) → AssocList K V → AssocList K V′
mapValues f = map (map₂ f)

module _ {K V : Type} where
  _∈ᵐ_ _∉ᵐ_ : K → AssocList K V → Type
  k ∈ᵐ m = AnyFirst ((k ≡_) ∘ proj₁) m
  k ∉ᵐ m = ·¬ (k ∈ᵐ m)

  ∈ᵐ-irrelevant : ∀ {k m} → Irrelevant (k ∈ᵐ m)
  ∈ᵐ-irrelevant = AnyFirst-irrelevant λ where refl refl → refl

  _∪_ : Op₂ (AssocList K V)
  _∪_ = _++_

  module _ ⦃ _ : DecEq K ⦄ where

    _∈ᵐ?_ = ¿ _∈ᵐ_ ¿²
    _∉ᵐ?_ = ¿ _∉ᵐ_ ¿²

    _‼_ : ∀ {k : K} (m : AssocList K V) → k ∈ᵐ m → V
    m ‼ p = L.First.satisfied p .proj₁ .proj₂

    _⁉_ : AssocList K V → K → Maybe V
    m ⁉ k with k ∈ᵐ? m
    ... | yes p = just (m ‼ p)
    ... | no  _ = nothing

    module _ {k : K} {m : AssocList K V} where
      _∷~_ : k ∈ᵐ m → (V → V) → AssocList K V
      p ∷~ f = m [ L.First.index p ]∷= (k , f (m ‼ p))

      _∷=_ : k ∈ᵐ m → V → AssocList K V
      p ∷= v = p ∷~ const v

    module _ ⦃ _ : Default V ⦄ where
      modify : K → (V → V) → Op₁ (AssocList K V)
      modify k f m = case k ∈ᵐ? m of λ where
        (no _)  → (k , f def) ∷ m
        (yes p) → p ∷= f (m ‼ p)

      set : K → V → Op₁ (AssocList K V)
      set k v = modify k (const v)

      _‼d_ : AssocList K V → K → V
      m ‼d k with m ⁉ k
      ... | nothing = def
      ... | just v  = v
