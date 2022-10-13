---
CIP: 71
Title: Non-Fungible Token (NFT) Proxy Voting Standard
Authors: Thaddeus Diamond <support@wildtangz.com>
Comments-URI:
Status: Proposed
Type: Informational
Created: 2022-10-11
Post-History:
License: CC-BY-4.0
---

## Abstract

This proposal defines a standard mechanism for performing verifiable on-chain voting in NFT projects that do not want a governance token using inline datums, plutus minting policies, and smart contracts.

## Motivation

This proposal is intended to provide a standard mechanism for non-fungible token (NFT) projects to perform on-chain verifiable votes using only their NFT assets. There are several proposed solutions for governance that involve using either a service provider (e.g., Summon) with native assets or the issuance of proprietary native assets.  However, there are several issues with these approaches:
- Airdrops of governance tokens require minUTxO ADA attached, costing the NFT project ADA out of pocket
- Fungible tokens do not have a 1:1 mechanism for tracking votes against specific assets with voting power
- Sale of the underlying NFT is not tied to sale of the governance token, creating separate asset classes and leaving voting power potentially with those who are no longer holders of the NFT

This standard provides a simple solution for this by using the underlying NFT to mint a one-time "ballot" token that can be used only for a specific voting topic. Projects that adopt this standard will be able to integrate with web viewers that track projects' governance votes and will also receive the benefits of verifiable on-chain voting without requiring issuance of a new native token.

It is not intended for complex voting applications or for governance against fungible tokens that cannot be labeled individually.

## Specification

### A Simple Analogy

The basic analogy here is that of a traditional state or federal vote.  Imagine a citizen who has a state ID (e.g., Driver's License) and wants to vote.  That citizen would:
1. Go to a precinct and show their ID to the appropriate authority
2. Receive a ballot with choices for the current vote
3. Mark their selections on the ballot
4. Sign their ballot with their name
5. Submit their ballot into a single "ballot box"
6. Authorized vote counting authorities process the vote after polls close
7. Await the election results through a trusted news outlet

This specification follows the same process, but using tokens:
1. A holder of a project validates their NFT by sending it to self
2. The user signs a Plutus minting policy to create a proxy NFT that represents the current ballot
3. The holder marks their vote selections off-chain
4. The holder signs a new transaction that sends the proxy "ballot" NFT to a smart contract ("the ballot box") with a datum representing the vote
5. Authorized vote counting wallets process the UTxOs' datum in the "ballot box" smart contract after the polls close
6. Project creators report the results in a human-readable off-chain format to their holders.

Because of the efficient UTxO model Cardano employs, steps #1, #2, and #4 can occur in a single transaction.

### The Vote Casting Process

#### "Ballot" -> Plutus Minting Policy

[ ] TODO: Describe the mechanism for creating the ballot and verifying ownership

#### "Vote" -> Inline Datum

[ ] TODO: Describe and diagram the format for vote casting

#### "Ballot Box" -> Smart Contract

[ ] TODO: Describe the logic required in the "ballot box" smart contract and potential for extension

### The Vote Counting Process

#### "Ballot Counter" -> Authorized Wallet

[ ] TODO: Describe the mechanism for creating the ballot and verifying ownership

### Reclaiming ADA Locked by the Ballot NFTs

[ ] TODO: Describe how/why ballot minting policy allows any user to burn the asset

## Potential Disadvantages

[ ] TODO: Token proliferation
[ ] TODO: Lack of easy way to determine vote after it is cast but before counted
[ ] TODO: Non-secret nature of the ballot if that is desired

## Backward Compatibility

Due to the nature of Plutus minting policies and smart contracts, which derive policy identifiers and payment addresses from the actual source code, once a vote has been started it cannot change versions or code implementations. However, because the mechanism we propose here is just a reference architecture, between votes projects are free to change either the "ballot" Plutus minting policy or the "ballot box" smart contract as they see fit.  There are no prior CIPs with which to conform with for backward interoperability.

## Path to Active

- Considerations for ranked-choice voting if projects wish to have it
- Minimal reference implementation making use of [Lucid](https://github.com/spacebudz/lucid) (off-chain), [Plutus Core](https://github.com/input-output-hk/plutus) [using Helios](https://github.com/Hyperion-BT/Helios) (on-chain): [Implementation](./example/)
- Open-source implementations from other NFT projects that make use of this CIP

## References

- [CIP-0025](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025): NFT Metadata Standard
- [CIP-0030](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030): Cardano dApp-Wallet Web Bridge
- [CIP-0068](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068): Datum Metadata Standard

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
