module Prelude.Anyable where

open import Prelude.Init
open import Prelude.LiteralSequences

record Anyable (F : Type ℓ → Type ℓ) : Type (lsuc ℓ) where
  field Any : ∀ {A} → (A → Type) → F A → Type ℓ

  ∃∈-syntax  = Any
  ∃∈-syntax′ = Any
  ∄∈-syntax  = λ {A} P → ¬_ ∘ Any {A} P
  ∄∈-syntax′ = ∄∈-syntax
  infix 2 ∃∈-syntax ∃∈-syntax′ ∄∈-syntax ∄∈-syntax′
  syntax ∃∈-syntax  P         xs = ∃[∈    xs ] P
  syntax ∃∈-syntax′ (λ x → P) xs = ∃[ x ∈ xs ] P
  syntax ∄∈-syntax  P         xs = ∄[∈    xs ] P
  syntax ∄∈-syntax′ (λ x → P) xs = ∄[ x ∈ xs ] P

open Anyable ⦃...⦄ public

instance
  Anyable-List : Anyable {ℓ} List
  Anyable-List .Any = L.Any.Any

  Anyable-Vec : ∀ {n} → Anyable {ℓ} (flip Vec n)
  Anyable-Vec .Any P = V.Any.Any P

  Anyable-Maybe : Anyable {ℓ} Maybe
  Anyable-Maybe .Any = M.Any.Any

private
  open import Prelude.Decidable

  _ : ∃[ x ∈ List ℕ ∋ [ 1 ⨾  2 ⨾ 3 ] ] (x > 0)
  _ = auto

  _ : ∃[ x ∈ just 42 ] (x > 0)
  _ = auto

  _ : ∄[ x ∈ nothing ] (x > 0)
  _ = auto
