---
CIP: ?
Title: Better script purposes
Category: Plutus
Status: Proposed
Authors:
    - Michele Nuzzi <michele@harmoniclabs.tech>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1072
Created: 2025-08-06
License: CC-BY-4.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
This CIP proposes better script purposes to optimize for common operations for each purpose

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

Common operations such as deriving the hash of the script being executed, or finding the relevant data for validation could be optimized if the trusted data provided to the script was more complete.

The same result could be achieved by including this data in the redeemer, however these alternative solutions ofter imply greater complexity in the offchain code, and do not come without overhead on-chian, since the redeemer cannot be trusted.

This CIP would solve those problems, with great improvements on the development experience as well as the resulting onchain scripts complexity and efficiency.


## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

this CIP proposes to modify the definition of `ScriptInfo` and `ScriptPurpose` in [`plutus-ledger-api`](https://github.com/IntersectMBO/plutus/blob/618480658ec1750179c2832c6b619bc2d872b225/plutus-ledger-api/src/PlutusLedgerApi/V3/Contexts.hs#L428-L461) as follows

```hs
data ScriptInfo
  = MintingScript
      -- hash of the script being executed (same as polciy)
      V2.CurrencySymbol
      -- | 0-based index of the given `CurrencySymbol` in `txInfoMint`
      Haskell.Integer
  | SpendingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the input being spent in `txInfoInputs`
      Haskell.Integer
      -- removed optional datum, since its presence (or not) is determined by the resolved input
      -- (Haskell.Maybe V2.Datum)
      -- resolved input being spent
      V3.TxOut
      V3.TxOutRef
  | RewardingScript
      -- V2.Credential -- removed, since implictily it must be a script credential
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the withdrawal being verified in `txInfoWdrl`
      Haskell.Integer
  | CertifyingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the given `TxCert` in `txInfoTxCerts`
      Haskell.Integer
      TxCert
  | VotingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the given vote in `txInfoVotes`
      Haskell.Integer
      Voter
  | ProposingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the given `ProposalProcedure` in `txInfoProposalProcedures`
      Haskell.Integer
      ProposalProcedure
  deriving stock (Generic, Haskell.Show, Haskell.Eq)
  deriving anyclass (HasBlueprintDefinition)
  deriving (Pretty) via (PrettyShow ScriptInfo)
```

```hs
data ScriptPurpose
  = MintingScript
      -- hash of the script being executed (same as polciy)
      V2.CurrencySymbol
      -- | 0-based index of the given `CurrencySymbol` in `txInfoMint`
      Haskell.Integer
  | SpendingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the input being spent in `txInfoInputs`
      Haskell.Integer
      V3.TxOutRef
  | RewardingScript
      -- V2.Credential -- removed, since implictily it must be a script credential
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the withdrawal being verified in `txInfoWdrl`
      Haskell.Integer
  | CertifyingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the given `TxCert` in `txInfoTxCerts`
      Haskell.Integer
      TxCert
  | VotingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the given vote in `txInfoVotes`
      Haskell.Integer
      Voter
  | ProposingScript
      -- hash of the script being executed
      V2.ScriptHash
      -- | 0-based index of the given `ProposalProcedure` in `txInfoProposalProcedures`
      Haskell.Integer
      ProposalProcedure
  deriving stock (Generic, Haskell.Show, Haskell.Eq)
  deriving anyclass (HasBlueprintDefinition)
  deriving (Pretty) via (PrettyShow ScriptInfo)
```

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

This modification would be reflected in the underlying data representation as always having the script hash of the given script as the first field of the purpose, and the index relevant to the purpose as second element.

This allows to optimize for the very common operation of deriving the hash of the script itself onchain, greatly reducing onchain complexity and cost of execution.

The change also propses to add the resovled input in the case of the very common spending purpose, where the majority of the relevant informations is present.

## Path to Active

Changes are reflected on the plutus-ledger-api

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

The change is included in an hardfork

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->
N/A

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. Uncomment the license you wish to use (delete the other one) and ensure it matches the License field in the header.

If AI/LLMs were used in the creation of the copyright text, the author may choose to include a disclaimer to describe their application within the proposal.
-->

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
