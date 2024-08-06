module Prelude.Irrelevance where

open import Prelude.Init
open import Prelude.Decidable
open import Prelude.Anyable

≡-irrelevant : ∀ {A : Type} {x y : A} → Irrelevant (x ≡ y)
≡-irrelevant refl refl = refl

T-irrelevant : ∀ {b} → Irrelevant (T b)
T-irrelevant {false} ()
T-irrelevant {true}  _ _ = refl

private variable A : Type ℓ

private data ∅ : Type where
record ·⊥ : Type where
  field .absurd : ∅

·⊥-elim : ·⊥ → A
·⊥-elim ()

·⊥⇒⊥ = (·⊥ → ⊥) ∋ ·⊥-elim
⊥⇒·⊥ = (⊥ → ·⊥) ∋ ⊥-elim
·⊥⇔⊥ = (·⊥ ↔ ⊥) ∋ ·⊥⇒⊥ , ⊥⇒·⊥

infix 3 ·¬_
·¬_ : Type ℓ → Type ℓ
·¬_ A = A → ·⊥

·¬-irrelevant : Irrelevant (·¬ A)
·¬-irrelevant _ _ = refl

·¬⇒¬ : ·¬ A → ¬ A
·¬⇒¬ ¬p = ·⊥-elim ∘ ¬p

¬⇒·¬ : ¬ A → ·¬ A
¬⇒·¬ ¬p = ⊥-elim ∘ ¬p

instance
  Dec-·⊥ : ·⊥ ⁇
  Dec-·⊥ .dec = no λ ()

private variable P : Pred A ℓ′

AnyFirst : ∀ {A : Type ℓ} → Pred A ℓ′ → Pred (List A) _
AnyFirst P = First (·¬_ ∘ P) P

module _ {a p} {A : Set a} where
  ·∁ : Pred A ℓ′ → Pred A ℓ′
  (·∁ P) x = ·¬ P x

  import Relation.Nullary.Decidable as Dec
  module _ {P : Pred A p} where
    AnyFirst-irrelevant : Irrelevant¹ P → Irrelevant¹ (AnyFirst P)
    AnyFirst-irrelevant = L.First.irrelevant (·⊥-elim ∘₂ _$_) ·¬-irrelevant

    first? : Decidable¹ P → Decidable¹ (First P (·∁ P))
    first? P? xs = mapDec (L.First.map id ¬⇒·¬) (L.First.map id ·¬⇒¬)
                          (L.First.first? P? xs)

    cofirst? : Decidable¹ P → Decidable¹ (First (·∁ P) P)
    cofirst? P? xs = mapDec (L.First.map ¬⇒·¬ id)  (L.First.map ·¬⇒¬ id)
                            (L.First.cofirst? P? xs)

instance
  Dec-AnyFirst : ⦃ P ⁇¹ ⦄ → AnyFirst P ⁇¹
  Dec-AnyFirst .dec = cofirst? dec¹ _

module _ {A : Type ℓ} {P : A → Type} where

  private variable xs : List A

  AnyFirst⇒Any : AnyFirst P xs → Any P xs
  AnyFirst⇒Any First.[ px ] = here px
  AnyFirst⇒Any (_ ∷ p)      = there (AnyFirst⇒Any p)

  firstIndex : AnyFirst P xs → Fin (length xs)
  firstIndex = L.Any.index ∘ AnyFirst⇒Any
