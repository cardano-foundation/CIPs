module Prelude.Bitmasks where

open import Prelude.Init
open import Prelude.Lists
open import Prelude.Default

private variable A : Type

Bitmask : List A → Type
Bitmask xs = Vec Bool (length xs)

select : (xs : List A) → Bitmask xs → List A
select []       []       = []
select (x ∷ xs) (b ∷ bs) = (if b then (x ∷_) else id) (select xs bs)

switchOn switchOff : ∀ {xs : List A} → Index xs → Op₁ (Bitmask xs)
switchOn  i bs = bs V.[ i ]≔ true
switchOff i bs = bs V.[ i ]≔ false

-- set default bits to 0
instance Default-Bool = Default-Bool-✖
