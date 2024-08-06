module Prelude.FromNat where

open import Prelude.Init
open import Prelude.LiteralSequences
open import Prelude.Decidable

-- ** dependent version
record Fromℕ (A : Type) (Can : ℕ → Type) : Type where
  field fromℕ : (n : ℕ) → ⦃ Can n ⦄ → A
open Fromℕ ⦃...⦄ public
{-# BUILTIN FROMNAT fromℕ #-}

-- ** non-dependent version
Fromℕ′ : Type → Type
Fromℕ′ A = Fromℕ A (const ⊤)

fromℕ′ : ∀ {A} → ⦃ Fromℕ′ A ⦄ → ℕ → A
fromℕ′ n = fromℕ n

record MkFromℕ′ (A : Type) : Type where
  constructor fromℕ∶_
  field fromℕ : ℕ → A

mkFromℕ′ : ∀ {A} → MkFromℕ′ A → Fromℕ′ A
mkFromℕ′ r .fromℕ n = r .MkFromℕ′.fromℕ n

instance
  Fromℕ-Nat   = Fromℕ′ ℕ          ∋ mkFromℕ′ (fromℕ∶ id)
  Fromℕ-Bool  = Fromℕ′ Bool       ∋ mkFromℕ′ (fromℕ∶ λ where 0 → false; _ → true)
  Fromℕ-Bin   = Fromℕ′ Bitstring  ∋ mkFromℕ′ (record {Bin})
  Fromℕ-Float = Fromℕ′ Float      ∋ mkFromℕ′ (record {Fl})

  Fromℕ-Fin : ∀ {n} → Fromℕ (Fin n) (λ m → True (¿ suc m ≤ n ¿))
  Fromℕ-Fin {n} .fromℕ m ⦃ m≤n ⦄ = (Fi.# m) {n} {m≤n}

_ = ℕ         ∋ 0
_ = Bool      ∋ 0
_ = Bitstring ∋ 0
_ = Float     ∋ 0
_ = Fin 1     ∋ 0
_ = Fin 200   ∋ 1
