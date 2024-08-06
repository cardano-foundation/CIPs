open import Prelude.Init

module Prelude.Closures {A : Type ℓ} (_—→_ : Rel A ℓ) where

private variable x y z : A

-- left-biased
infix  3 _∎
infixr 2 _—→⟨_⟩_ _—↠⟨_⟩_
infix  1 begin_; pattern begin_ x = x
infix -1 _—↠_

data _—↠_ : Rel A ℓ where
  _∎ : ∀ x → x —↠ x
  _—→⟨_⟩_ : ∀ x → x —→ y → y —↠ z → x —↠ z

—↠-trans : Transitive _—↠_
—↠-trans (x ∎) xz = xz
—↠-trans (_ —→⟨ r ⟩ xy) yz = _ —→⟨ r ⟩ —↠-trans xy yz

_—↠⟨_⟩_ : ∀ x → x —↠ y → y —↠ z → x —↠ z
_—↠⟨_⟩_ _ = —↠-trans
