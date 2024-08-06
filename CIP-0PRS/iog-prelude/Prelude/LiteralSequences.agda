module Prelude.LiteralSequences where

open import Prelude.Init

pattern [_] x = x ∷ []
pattern [_⨾_] x y = x ∷ [ y ]
pattern [_⨾_⨾_] x y z = x ∷ [ y ⨾ z ]
pattern [_⨾_⨾_⨾_] x y z w = x ∷ [ y ⨾ z ⨾ w ]
pattern [_⨾_⨾_⨾_⨾_] x y z w q = x ∷ [ y ⨾ z ⨾ w ⨾ q ]
pattern [_⨾_⨾_⨾_⨾_⨾_] x y z w q r = x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ]
pattern [_⨾_⨾_⨾_⨾_⨾_⨾_] x y z w q r s = x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ⨾ s ]
pattern [_⨾_⨾_⨾_⨾_⨾_⨾_⨾_] x y z w q r s t = x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ⨾ s ⨾ t ]
pattern [_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_] x y z w q r s t v = x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ⨾ s ⨾ t ⨾ v ]
pattern [_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_] x y z w q r s t v p =
  x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ⨾ s ⨾ t ⨾ v ⨾ p ]
pattern [_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_] x y z w q r s t v p o =
  x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ⨾ s ⨾ t ⨾ v ⨾ p ⨾ o ]
pattern [_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_⨾_] x y z w q r s t v p o u =
  x ∷ [ y ⨾ z ⨾ w ⨾ q ⨾ r ⨾ s ⨾ t ⨾ v ⨾ p ⨾ o ⨾ u ]
