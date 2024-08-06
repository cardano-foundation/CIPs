module Prelude.DecEq where

open import Prelude.Init

record DecEq (A : Type) : Type where
  field _≟_ : DecidableEquality A

  _==_ : A → A → Bool
  _==_ = ⌊_⌋ ∘₂ _≟_

  ≟-refl : ∀ (x : A) → (x ≟ x) ≡ yes refl
  ≟-refl x with refl , p ← dec-yes (x ≟ x) refl = p
open DecEq ⦃...⦄ public

private variable
  n : ℕ
  A : Type

instance
  DecEq-⊤ : DecEq ⊤
  DecEq-⊤ ._≟_ _ _ = yes refl

  DecEq-ℕ : DecEq ℕ
  DecEq-ℕ = record {Nat}

  DecEq-Fin : DecEq (Fin n)
  DecEq-Fin = record {Fi}

  DecEq-List : ⦃ DecEq A ⦄ → DecEq (List A)
  DecEq-List ._≟_ = L.≡-dec _≟_

  DecEq-Bin : DecEq Bitstring
  DecEq-Bin = record {Bin}
