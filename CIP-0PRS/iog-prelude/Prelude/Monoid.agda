module Prelude.Monoid where

open import Prelude.Init

record Monoid (A : Type) : Type where
  field ε : A
open Monoid ⦃...⦄ public

private variable A : Type

instance
  Monoid-List : Monoid (List A)
  Monoid-List .ε = []

  Monoid-Bin : Monoid Bitstring
  Monoid-Bin .ε = Bin.zero
