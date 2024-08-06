module Prelude.Init where

open import Agda.Primitive public
  using ()
  renaming (Set to Type; Setω to Typeω)
open import Level public
  using (Level; 0ℓ; Setω)
  renaming (suc to lsuc; _⊔_ to _⊔ₗ_)
1ℓ = lsuc 0ℓ; 2ℓ = lsuc 1ℓ; 3ℓ = lsuc 2ℓ; 4ℓ = lsuc 3ℓ
variable ℓ ℓ′ ℓ″ ℓ‴ ℓ₀ ℓ₁ ℓ₂ ℓ₃ ℓ₄ : Level

open import Function public
  using (_∋_; _∘_; _∘′_; _∘₂_; _$_; flip; it; id; _on_; const; case_of_)
open import Data.Empty public
  using (⊥; ⊥-elim)
open import Data.Unit public
  using (⊤; tt)
open import Data.Bool public
  using (Bool; true; false; T; not; _∧_; _∨_; if_then_else_)
open import Data.Product public
  using ( _×_; _,_; proj₁; proj₂; Σ; Σ-syntax; ∃; ∃-syntax; -,_
        ; map₁; map₂; curry; uncurry )
open import Data.Sum public
  using (_⊎_; inj₁; inj₂)
module Bin where
  open import Data.Nat.Binary public
  open import Data.Nat.Binary.Properties public
open Bin public
  using () renaming (ℕᵇ to Bitstring)

module Nat where
  open import Data.Nat public
  open import Data.Nat.Properties public
  open import Data.Nat.DivMod public
  open import Data.Nat.Induction public
open Nat public
  using (ℕ; suc; _≤_; _<_; _<ᵇ_; _≥_; _>_; _+_; _∸_; _*_; _/_)

module Fi where
  open import Data.Fin public
  open import Data.Fin.Properties public
open Fi public
  using (Fin; fromℕ<; pred)
  renaming (zero to fzero; suc to fsuc)

module Fl where
  open import Data.Float public
  open import Data.Float.Properties public
open Fl public
  using (Float)

module Int where
  open import Data.Integer public
  open import Data.Integer.Properties public
open Int public
  using (ℤ)

module M where
  open import Data.Maybe public
  open import Data.Maybe.Properties public
  module Any where
    open import Data.Maybe.Relation.Unary.Any public
  module All where
    open import Data.Maybe.Relation.Unary.All public
    open import Data.Maybe.Relation.Unary.All.Properties public
open import Data.Maybe public
  using ( Maybe; just; nothing; maybe; fromMaybe; is-just; is-nothing
        ; decToMaybe; boolToMaybe )
  renaming (map to mapMaybe)

module V where
  open import Data.Vec public
  open import Data.Vec.Properties public
  module All where
    open import Data.Vec.Relation.Unary.All public
    open import Data.Vec.Relation.Unary.All.Properties public
  module Any where
    open import Data.Vec.Relation.Unary.Any public
    open import Data.Vec.Relation.Unary.Any.Properties public
open V public
  using (Vec; []; _∷_)

module L where
  open import Data.List public
  open import Data.List.Properties public
  module All where
    open import Data.List.Relation.Unary.All public
    open import Data.List.Relation.Unary.All.Properties public
  module Any where
    open import Data.List.Relation.Unary.Any public
    open import Data.List.Relation.Unary.Any.Properties public
  module Mem where
    open import Data.List.Membership.Propositional public
    open import Data.List.Membership.Propositional.Properties public
  module First where
    open import Data.List.Relation.Unary.First public
    open import Data.List.Relation.Unary.First.Properties public
  module NE where
    open import Data.List.NonEmpty public
    open import Data.List.NonEmpty.Properties public
  module SubL where
    open import Data.List.Relation.Binary.Sublist.Propositional public
    open import Data.List.Relation.Binary.Sublist.Propositional.Properties public
  module SubS where
    open import Data.List.Relation.Binary.Subset.Propositional public
    open import Data.List.Relation.Binary.Subset.Propositional.Properties public
  module Unique where
    open import Data.List.Relation.Unary.Unique.Propositional public
    open import Data.List.Relation.Unary.Unique.Propositional.Properties public
open L public
  using (List; []; _∷_; _++_; map; catMaybes; head; filter; length; sum; and; or
        ; any; _[_]∷=_)
open L.NE public
  using (List⁺; _∷_; _∷⁺_)
open L.All public
  using ([]; _∷_)
open L.Any public
  using (here; there; _─_)
open L.First public
  using (First; _∷_)
open L.Mem public
  using (_∈_; _∉_)
open L.SubL public
  using (_⊆_; []; _∷ʳ_; _∷_)
open L.SubS public
  using ()
  renaming (_⊆_ to _⊆ˢ_)
open L.Unique public
  using (Unique)

open import Relation.Nullary public
  using (¬_; Dec; yes; no; Irrelevant)
open import Relation.Nullary.Decidable public
  using ( ⌊_⌋; True; False; toWitness; toWitnessFalse; fromWitness
        ; dec-yes; dec-no; dec-true; dec-false ; ¬?; _⊎-dec_; _×-dec_)
  renaming (map′ to mapDec)
open import Relation.Nullary.Negation public
  using (contradiction; contraposition)
open import Relation.Unary public
  using (Pred)
  renaming (Decidable to Decidable¹; Irrelevant to Irrelevant¹)
open import Relation.Binary public
  using (Rel; REL; DecidableEquality; Transitive)
  renaming (Decidable to Decidable²; Irrelevant to Irrelevant²)
open import Relation.Binary.PropositionalEquality public
  using (_≡_; _≢_; refl; cong; subst; sym; module ≡-Reasoning)

open import Algebra.Core public
  using (Op₁; Op₂)

-- ** extras

-- uniquely exists
∃! : {A : Type ℓ} → Pred A ℓ′ → Type _
∃! = P.∃! _≡_
  where import Data.Product as P

-- iff
_↔_ : Type ℓ → Type ℓ′ → Type (ℓ ⊔ₗ ℓ′)
A ↔ B = (A → B) × (B → A)

-- singleton types
data Is {A : Type ℓ} : A → Type ℓ where
  ⟫_ : (x : A) → Is x
infix -100 ⟫_

-- get the type of a given term
typeOf : ∀ {A : Type ℓ} → (a : A) → Type ℓ
typeOf {A = A} _ = A
