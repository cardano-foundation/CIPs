---
CIP: ???
Title: eBTC – A Trustless BTC Bridge on Cardano
Category: Standards / Token
Authors:
  - An <anrodz42@gmail.com>
Implementors:
  - TBD
Status: Draft
Created: 2024-12-21
License: CC-BY-4.0
Discussions:
  - https://forum.cardano.org/t/ebtc-a-trustless-btc-bridge-on-cardano/141117
---

## Abstract

This proposal defines eBTC: a trustless, one-way bridge allowing Bitcoin (BTC) value to enter Cardano as a native token. Users burn BTC on Bitcoin and present cryptographic proofs (for example, using NIPoPoW [1]) to a Cardano smart contract, which mints a corresponding amount of eBTC. Unlike centralized solutions, there are no custodians or oracles. This opens BTC liquidity to Cardano’s DeFi, NFTs, and other on-chain functionalities.

## Motivation: Why is this CIP necessary?

1. Expand BTC use cases.
   BTC has limited scripting, restricting DeFi and smart contract capabilities. eBTC brings BTC-derived value onto Cardano for greater utility and financial integration.

2. Trustless design.
   Existing wrapped BTC tokens rely on third-party custodians. eBTC eliminates this centralized point of failure by leveraging verifiable on-chain proofs.

3. One-way migration.
   By burning BTC, the bridging mechanism is simpler and avoids two-way complexities. This finality preserves trustlessness and ensures a clear supply correlation.

4. Potential decimal expansion.
   BTC transactions often involve fractional satoshis, so eBTC may need sufficient decimal places (such as 8 or more) to handle microtransactions and avoid rounding issues.

## Specification

### Key Components

1. Burn operation.
   - The user sends BTC to a publicly verifiable, unspendable “burn address” on the Bitcoin network.
   - This permanently removes those BTC from circulation.

2. Proof construction.
   - The user compiles minimal Bitcoin block headers and NIPoPoW [1] data.
   - These proofs demonstrate that the burn transaction was included in the valid main chain.

3. Proof submission.
   - A Plutus contract on Cardano checks the provided block headers.
   - If the proof is valid, it mints new eBTC (at a 1:1 ratio with burned BTC).

### State Management (Cumulative Burn Model)

To prevent complex tracking of every single burn transaction:

- Each user provides proofs showing the total BTC they have cumulatively burned at a certain Bitcoin block height.
- The contract compares this new cumulative figure against the last recorded total for that address.
- If the new proof shows a higher burn total, the contract mints the difference in eBTC.
- This avoids storing data for every transaction ID or satoshi burned, reducing on-chain state overhead.

### User Ownership

- Users provide their unique Bitcoin burn address and cryptographic proof of control.
- The contract links that address to the user so that only that address’s rightful owner can mint eBTC from its burns.
- No centralized registry is required; all information is verified on-chain via proofs.

## Rationale: How does this CIP achieve its goals?

- Decentralization.
  eBTC removes reliance on custodians by verifying burns with Bitcoin’s proof-of-work.
- Security.
  Uses minimal proof-of-work headers and NIPoPoW data, reducing attack surfaces.
- Simplicity.
  One-way bridging (BTC → Cardano) avoids intricate two-way redeem logic.

## Path to Active

### Acceptance Criteria

- Broad community agreement that trustless, one-way bridging is beneficial.
- Working proof-of-concept demonstrating on-chain validation of minimal Bitcoin headers with no reliance on external oracles.

### Implementation Plan

1. Prototype.
   - Implement a Plutus script to parse minimal Bitcoin headers, verify chain difficulty, and confirm transaction inclusion.
2. Community testing.
   - Deploy a testnet version of the script, invite public trials to validate performance, security, and feasibility.
3. Mainnet rollout.
   - Once proven stable, define a timeline for mainnet release and specify final parameters (e.g., required confirmations, decimal precision).

## Security Considerations

- Forks and reorganizations.
  The script should require a certain number of confirmations to ensure the burn transaction remains in Bitcoin’s main chain.
- Header validation.
  The Plutus contract must correctly parse and verify each block header’s proof-of-work.
- Spam or denial of service.
  Transaction fees for on-chain proofs discourage frivolous submissions. Off-chain proof generation is intentionally non-trivial.

## References

[1] Non-Interactive Proofs of Proof-of-Work (NIPoPoWs). Kiayias et al. (IOHK Research). https://eprint.iacr.org/2017/963.pdf

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
