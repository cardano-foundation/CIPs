module Prelude.Allable where

open import Prelude.Init
open import Prelude.LiteralSequences
open import Prelude.DecEq

record Allable (F : Type ℓ → Type ℓ) : Type (lsuc ℓ) where
  field All : ∀ {A} → (A → Type) → F A → Type ℓ

  ∀∈-syntax   = All
  ∀∈-syntax′  = All
  ¬∀∈-syntax  = λ {A} P → ¬_ ∘ All {A} P
  ¬∀∈-syntax′ = ¬∀∈-syntax
  infix 2 ∀∈-syntax ∀∈-syntax′ ¬∀∈-syntax ¬∀∈-syntax′
  syntax ∀∈-syntax   P         xs = ∀[∈     xs ] P
  syntax ∀∈-syntax′  (λ x → P) xs = ∀[  x ∈ xs ] P
  syntax ¬∀∈-syntax  P         xs = ¬∀[∈    xs ] P
  syntax ¬∀∈-syntax′ (λ x → P) xs = ¬∀[ x ∈ xs ] P

open Allable ⦃...⦄ public

instance
  Allable-List : Allable {ℓ} List
  Allable-List .All = L.All.All

  Allable-Vec : ∀ {n} → Allable {ℓ} (flip Vec n)
  Allable-Vec .All P = V.All.All P

  Allable-Maybe : Allable {ℓ} Maybe
  Allable-Maybe .All = M.All.All

private
  open import Prelude.Decidable

  _ : ∀[ x ∈ List ℕ ∋ [ 1 ⨾ 2 ⨾ 3 ] ] (x > 0)
  _ = auto

  _ : ∀[ x ∈ just 42 ] (x > 0)
  _ = auto

  _ : ∀[ x ∈ nothing ] (x > 0)
  _ = auto

  _ : ¬∀[ x ∈ just 0 ] (x > 0)
  _ = auto
