module Prelude.Lists where

open import Prelude.Init
open import Prelude.FromNat

private variable A B : Type

-- * indexing
Index : List A → Type
Index = Fin ∘ length

mapWithIndex : ∀ {B : Type} (xs : List A) → (Index xs → B) → List B
mapWithIndex [] _ = []
mapWithIndex (_ ∷ xs) f = f 0 ∷ mapWithIndex xs (f ∘ fsuc)

filterByIndex : (xs : List A) → (Index xs → Bool) → List A
filterByIndex [] _ = []
filterByIndex (x ∷ xs) f =
  let xs′ = filterByIndex xs (f ∘ fsuc) in
  if f 0 then x ∷ xs′ else xs′

-- * constructing indexed functions
∅ : Index {A = A} [] → B
∅ ()

[_∶_⋯_∶_] : (x : A) → B → ∀ xs → (Index xs → B) → (Index (x ∷ xs) → B)
[ _ ∶ b ⋯ _ ∶ f ] = λ where
  fzero    → b
  (fsuc i) → f i

-- * removing suffix
_─⋯_ : (xs : List A) → Index xs → List A
xs ─⋯ i = L.drop (suc $ Fi.toℕ i) xs

private
  open import Prelude.LiteralSequences
  ns = List ℕ ∋ [ 0 ⨾ 1 ⨾ 2 ⨾ 3 ]
  _ = ns ─⋯ 0 ≡ [ 1 ⨾ 2 ⨾ 3 ]
    ∋ refl
  _ = ns ─⋯ 1 ≡ [ 2 ⨾ 3 ]
    ∋ refl
  _ = ns ─⋯ 2 ≡ [ 3 ]
    ∋ refl
  _ = ns ─⋯ 3 ≡ []
    ∋ refl

private variable xs : List A

─⋯-⊆ : (i : Index xs) → (xs ─⋯ i) ⊆ˢ xs
─⋯-⊆ {xs = _ ∷ _} fzero    = there
─⋯-⊆ {xs = _ ∷ _} (fsuc i) = there ∘ ─⋯-⊆ _

─⋯-∷ : (i : Index xs) → ∃ λ ys → xs ≡ ys ++ L.lookup xs i ∷ (xs ─⋯ i)
─⋯-∷ {xs = _ ∷ _}  fzero    = [] , refl
─⋯-∷ {xs = _ ∷ xs} (fsuc i) = let ys , xs≡ = ─⋯-∷ i in  _ ∷ ys , cong (_ ∷_) xs≡

─⋯-len : (i : Index xs) → length (xs ─⋯ i) < length xs
─⋯-len {xs = _ ∷ _}  fzero    = Nat.≤-refl
─⋯-len {xs = _ ∷ xs} (fsuc i) = Nat.s≤s $ Nat.<⇒≤ $ ─⋯-len {xs = xs} i
