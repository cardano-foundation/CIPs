---
CIP: 174
Title: Plutus Script Caching  
Category: Node  
Status: Proposed  
Authors:  
  - Philip DiSarro <philip.disarro@gmail.com>  
Implementors: []  
Discussions:  
  - https://github.com/IntersectMBO/cardano-ledger/blob/master/docs/adr/2024-08-14_009-refscripts-fee-change.md
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1031
Created: 2025-05-01  
License: CC-BY-4.0  
---

## Abstract

We propose introducing a memory-bound, Least Recently Used (LRU) in-memory caching layer within Cardano nodes to store deserialized Plutus scripts. This optimization will significantly reduce redundant deserialization operations and improve node performance, especially in high-throughput environments or dApps with widely reused scripts. Scripts not found in cache are lazily reloaded from transaction data or reference inputs via cold reload.

## Motivation: Why is this CIP necessary?

Currently, each Plutus script must be deserialized every time it is encountered during validation, even if it has been used in many recent transactions. This introduces non-trivial CPU overhead, especially for frequently invoked scripts like validators in DeFi protocols, DEXs, or DAOs.

This CIP proposes a RAM-based cache to:

- Reduce CPU overhead per block validation
- Improve performance for scripts reused across transactions
- Avoid repeated deserialization of identical script bytes
- Enable faster block validation, especially under load

**Beneficiaries**:
- Node operators and SPOs
- Off-chain indexers and relays
- Application developers with high-frequency validators

## Specification

### Caching Layer Requirements

- Cache stores deserialized `PlutusScript` objects in memory
- Keyed by script hash (Blake2b-224, consistent with ledger use)
- LRU eviction policy to release least recently used scripts
- Global memory cap (e.g., 256 MB, configurable via node config)

### Behavior

- On script validation, check in-memory cache first
- If cache hit: use deserialized script directly
- If cache miss:
  - Deserialize from transaction or reference input
  - Insert into cache, possibly evicting an older entry

### Cold Reload

- Evicted scripts or rarely used scripts are re-deserialized as needed
- Cache does not affect determinism or validation results
- Deserialization errors are handled identically to current logic

### Configuration Parameters

Add new parameters to the node configuration:

```yaml
PlutusScriptCache:
  maxCacheSizeMB: 256
  evictionPolicy: LRU
```

## Rationale: How does this CIP achieve its goals?

This proposal follows the same spirit as performance optimizations in other smart contract chains (e.g. Solana's JIT caching model). It does not modify on-chain structures or Plutus semantics — only the **execution engine of node software**.

- **Backwards compatible**: does not change transaction format or script representation
- **Deterministic**: cache hit/miss does not change validation result
- **Node-local**: entirely handled in the node runtime

### Alternatives considered

- Persistent on-disk script cache: slower, more complex concurrency
- No caching: leads to redundant deserialization cost

### Interaction with ADR-009 Reference Script Fee Changes

[ADR-009](https://github.com/IntersectMBO/cardano-ledger/blob/master/docs/adr/2024-08-14_009-refscripts-fee-change.md) introduced a tiered fee structure for reference scripts due to the high deserialization overhead of large scripts. This CIP mitigates that overhead at the node level by reusing previously deserialized scripts in memory.

This caching mechanism does **not replace** or invalidate the fee policy defined in ADR-009. The **fee remains based on raw reference script byte size**, regardless of cache hits, as:

- Cache state is local to the validator and non-deterministic from a protocol perspective
- Fees must remain consistent, independent of validator memory state

However, this CIP **reduces the real-world validator cost** of handling such scripts, aligning economic deterrents (via ADR-009) with operational efficiency (via caching).

Future extensions may explore whether cache hits can be made partially fee-aware for further optimization, but that is out of scope for this proposal.

## Path to Active

### Acceptance Criteria

- [ ] Implementation merged into `cardano-node`
- [ ] Benchmarks show measurable reduction in script deserialization cost under load
- [ ] No deviation in transaction validation outcomes due to caching

### Implementation Plan

1. [ ] Modify Plutus script execution in `cardano-node` to check memory cache before deserialization
2. [ ] Integrate cache via bounded LRU store
3. [ ] Add config flags to control cache size and policy
4. [ ] Test under synthetic load with high script reuse

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
