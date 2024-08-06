module Prelude.Default where

open import Prelude.Init

-- Types that have a default value.
record Default (A : Type) : Type where
  field def : A
open Default ⦃...⦄ public

private variable A B : Type; n : ℕ

instance
  Default-⊤ : Default ⊤
  Default-⊤ .def = tt

  Default-× : ⦃ Default A ⦄ → ⦃ Default B ⦄ → Default (A × B)
  Default-× .def = def , def

  Default-List : Default (List A)
  Default-List .def = []

  Default-Vec : ⦃ Default A ⦄ → Default (Vec A n)
  Default-Vec .def = V.replicate _ def

Default-Bool-✖ Default-Bool-✓ : Default Bool
Default-Bool-✖ .def = false
Default-Bool-✓ .def = true
