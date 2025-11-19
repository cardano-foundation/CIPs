# Ouroboros Leios Summary

> [!NOTE]
>
> This summary provides a comprehensive overview of Ouroboros Leios. For the
> complete technical specification, see [CIP-0164](README.md).

## What is Ouroboros Leios?

Ouroboros Leios is a revolutionary consensus protocol designed to dramatically
increase Cardano's transaction throughput while maintaining the security
guarantees of Ouroboros Praos. It's an optimistic protocol that operates
alongside the existing Praos chain, enabling Cardano to support the transaction
volumes needed for long-term economic sustainability.

## The problem it solves

Cardano's current throughput limitations pose a significant challenge as the
ecosystem grows. With increasing transaction volumes and complex decentralized
applications, the network needs a fundamental enhancement to accommodate future
demand without compromising security.

## How It Works: The 5-Step Process

### 1. **EB Proposal**

When a stake pool wins slot leadership, it creates:

- A standard **Ranking Block (RB)** - the normal Praos block
- An optional **Endorser Block (EB)** - containing references to additional
  transactions

### 2. **EB Distribution**

The EB and its referenced transactions are rapidly distributed across the
network using optimized diffusion protocols.

### 3. **Committee Validation**

A randomly selected committee of stake pools validates the EB within a specific
voting period, ensuring network consensus.

### 4. **Certification**

If enough committee members vote (≥75% threshold), the EB becomes certified and
ready for inclusion.

### 5. **Chain Inclusion**

Certified EBs are applied to the ledger just before their certifying RB, but the
EB transactions themselves are not registered on-chain as separate blocks.

## Key Characteristics

### **Massive Throughput Increase**

- Achieving 30-65x improvement over current mainnet (140-300 TxkB/s, equivalent
  to ~100-200 TPS depending on average transaction sizes)
- Each EB can reference significantly more transactions than standard blocks
- Configurable via protocol parameters to optimize for different network
  conditions
- Simulations demonstrate substantial throughput improvements

### **Opportunistic Inclusion**

- Not all EBs get certified due to timing constraints
- This ensures sufficient network diffusion periods for Praos security
  guarantees
- Balances throughput with security requirements

### **Security Preservation**

- Maintains all Praos security guarantees
- Committee-based validation ensures network consensus
- Careful timing constraints prevent security vulnerabilities

## Economic Benefits

### **Balanced Scalability**
- increased transaction capacity with moderate increase in confirmation time (45-60 seconds)
- Supports sustainable rewards as Reserve depletes, requiring ~36 TPS by 2029
- Maintains economic sustainability
- Minimal added complexity through few new protocol elements

### **Future-Proof Design**

- Designed to support Cardano's long-term growth
- Configurable parameters allow adaptation to changing needs
- Preserves existing economic incentives

## Implementation Strategy

### **Backward Compatibility**

- Operates alongside existing Praos chain
- No disruption to current network operations
- Gradual rollout possible

### **Protocol Parameters**

The system includes configurable parameters for:

- **Timing parameters**: Control validation and diffusion periods
- **Size parameters**: Determine EB capacity and committee sizes
- **Security parameters**: Maintain safety guarantees

## Research and Development

This specification presents the first version of the Ouroboros Leios protocol
family. For comprehensive research documentation, development history, and
additional technical resources, visit the Leios Innovation R&D site at
[leios.cardano-scaling.org](https://leios.cardano-scaling.org).

## What's Next?

Ouroboros Leios represents a significant step forward in blockchain scalability.
The protocol is designed to:

- Support Cardano's growing ecosystem
- Enable complex decentralized applications
- Maintain security and decentralization
- Provide economic sustainability for long-term growth

---

Read the complete [CIP-0164 specification](README.md) for in-depth technical
documentation, protocol artifacts, security analysis, and implementation
details.
