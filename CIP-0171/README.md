---
CIP: 171
Title: On-chain Smart Contract Bytecode Verification
Category: Metadata
Status: Proposed
Authors:
    - Giovanni Gargiulo <gargiulo.gianni@gmail.com>
Implementors: []
Discussions:
    - https://forum.cardano.org/t/cip-idea-smart-contract-source-code-verification-metadata/152403
    - https://github.com/cardano-foundation/CIPs/pull/1136
Created: 2026-01-19
License: CC-BY-4.0
---

## Abstract

This CIP defines a decentralized, on-chain metadata standard for linking Cardano script hashes to their published source code. Using transaction metadata label `1984`, anyone can publish records containing the source repository URL, git commit hash, compiler type and version, and script parameters. Verifiers can then independently compile the source and confirm that the resulting script hash matches an on-chain script, establishing a verified link between the deployed script and its source code origin.

Unlike centralized verification services that act as trusted intermediaries, this standard enables permissionless verification where anyone can submit and validate records without relying on third parties. The design is intentionally spam-resistant: invalid or fabricated submissions are harmless because non-matching script hashes simply have no corresponding on-chain scripts to link to.

This standard supports multiple Cardano smart contract compilers including Aiken, Plutarch, PlutusTx, Scalus, plu-ts, and OpShin, with a mechanism for adding new compilers as they emerge.

## Motivation: why is this CIP necessary?

### The Problem

Users regularly interact with Cardano smart contracts without any practical way to verify that an on-chain script was produced from source code they have reviewed or that has been audited. This creates a trust gap: users must either blindly trust contract deployers or rely on third-party verification services.

On other blockchain platforms like Ethereum, verification typically depends on centralized services such as Etherscan. While functional, this approach introduces a single point of trust and potential failure. Cardano currently lacks any standardized mechanism for linking scripts to their source code, centralized or otherwise.

### Why Decentralization Matters

Centralized verification services present several concerns:

- **Single point of failure**: Service downtime means no verification
- **Trust assumption**: Users must trust the service operator
- **Gatekeeping potential**: Services can choose what to verify or display
- **Permanence risk**: Services may discontinue or change policies

A decentralized standard stores verification data on-chain, making it permanently available, independently verifiable, and free from any single party's control.

### Permissionless Design

This standard allows anyone to submit verification metadata, not just the original contract deployer. This permissionless approach provides several benefits:

- **Third-party verification**: Auditors, security researchers, or community members can submit verification records for scripts they have analyzed
- **No gatekeeper**: Deployers who neglect or refuse to verify their scripts can still have their code verified by others
- **Spam resistance**: Invalid submissions are self-invalidating. If someone submits fabricated metadata, the resulting script hash will not match any on-chain script. These orphaned records are harmless noise that verifiers simply ignore.

### Use Cases

- **Wallets**: Display verification status before users sign transactions interacting with a script
- **Block explorers**: Show verified source code alongside script details
- **dApp developers**: Provide cryptographic proof linking their on-chain scripts to published source
- **Auditors**: Confirm that an on-chain script was produced from audited source code
- **Security researchers**: Independently verify the source origin of any on-chain script

## Specification

### Metadata Label

This standard uses transaction metadata label **1984**, registered in CIP-0010.

The label was chosen for its cultural reference to themes of trust and transparency, and for being easily memorable.

### Data Structure Overview

Verification metadata is encoded as CBOR PlutusData and stored under metadata label 1984. Due to Cardano's 64-byte limit on individual metadata bytestrings, the PlutusData is serialized to CBOR, split into chunks of at most 64 bytes, and stored as an array.

The top-level structure is:

```
{ 1984: [ <chunk1>, <chunk2>, ..., <chunkN> ] }
```

When reassembled, the chunks form a PlutusData structure using a constructor to identify the compiler type.

### Compiler and Schema Versioning

Compilers and their metadata schema versions are identified by PlutusData constructor IDs. Each constructor uniquely identifies both the compiler and the schema version used to encode the verification metadata.

| Constructor ID | Compiler | Schema Version | Language |
|----------------|----------|----------------|----------|
| 0 | Aiken | 1 | Aiken |
| 1 | Plutarch | 1 | Haskell |
| 2 | PlutusTx | 1 | Haskell |
| 3 | Scalus | 1 | Scala |
| 4 | plu-ts | 1 | TypeScript |
| 5 | OpShin | 1 | Python |

This design allows each compiler's metadata schema to evolve independently. If a compiler requires changes to its field layout (adding, removing, or reordering fields), a new constructor ID is assigned for the updated schema version. Implementations encountering an unrecognized constructor SHOULD ignore the record rather than fail.

New compilers or schema versions may be added by submitting a pull request to this CIP. Constructor IDs are assigned sequentially and MUST NOT be reused or reassigned.

### Field Layout

The constructor's fields contain the following data in order:

| Index | Field | Type | Required | Description |
|-------|-------|------|----------|-------------|
| 0 | sourceUrl | Bytes (UTF-8) | Yes | Git-compatible repository URL |
| 1 | commitHash | Bytes | Yes | Git commit hash (20 bytes for SHA-1, 32 bytes for SHA-256) |
| 2 | sourcePath | Bytes (UTF-8) | No | Path to source file within repository (empty if root) |
| 3 | compilerVersion | Bytes (UTF-8) | Yes | Exact compiler version string (e.g., "v1.1.3") |
| 4 | parameters | Map | No | Script hash to parameter data mappings |

#### Source URL

The `sourceUrl` field accepts any URL compatible with `git clone`. This includes but is not limited to:

- GitHub: `https://github.com/org/repo`
- GitLab: `https://gitlab.com/org/repo`
- Codeberg: `https://codeberg.org/org/repo`
- Self-hosted: `https://git.example.com/repo`
- SSH URLs: `git@github.com:org/repo.git`

Implementations MUST NOT assume any particular git hosting provider.

#### Commit Hash

The `commitHash` field contains the raw bytes of the git commit hash. Standard git repositories use SHA-1 (20 bytes), while repositories with SHA-256 enabled use 32 bytes.

#### Compiler Version

The `compilerVersion` field MUST contain the exact version string required to reproduce the compilation. Partial versions (e.g., "v1.x" or "latest") are invalid.

#### Parameters

The `parameters` field maps script hashes to their initialization parameters. This supports parameterized scripts where the same source code produces different script hashes depending on input parameters.

Structure:
```
Map<ScriptHash, List<PlutusData>>
```

Where:
- `ScriptHash` is the 28-byte Blake2b-224 hash of the compiled script
- `List<PlutusData>` contains the parameters applied to produce that specific script

### CDDL Schema

```cddl
verification_metadata = { 1984: chunked_plutus_data }

chunked_plutus_data = [ + bounded_bytes ]

bounded_bytes = bytes .size (1..64)

; When chunks are concatenated and decoded as CBOR:
; Constructor ID encodes both compiler and schema version
verification_data = #6.121([compiler_fields])  ; Constructor 0 = Aiken, schema v1
                  / #6.122([compiler_fields])  ; Constructor 1 = Plutarch, schema v1
                  / #6.123([compiler_fields])  ; Constructor 2 = PlutusTx, schema v1
                  / #6.124([compiler_fields])  ; Constructor 3 = Scalus, schema v1
                  / #6.125([compiler_fields])  ; Constructor 4 = plu-ts, schema v1
                  / #6.126([compiler_fields])  ; Constructor 5 = OpShin, schema v1
                  ; Future schema versions will be assigned new constructor IDs

compiler_fields = [
    source_url,
    commit_hash,
    source_path / null,
    compiler_version,
    ? parameters
]

source_url = bytes          ; UTF-8 encoded URL
commit_hash = bytes         ; 20 or 32 bytes
source_path = bytes         ; UTF-8 encoded path
compiler_version = bytes    ; UTF-8 encoded version string

parameters = { * script_hash => parameter_list }
script_hash = bytes .size 28
parameter_list = [ * plutus_data ]

plutus_data = #6.121([* plutus_data])   ; Constr 0
            / #6.122([* plutus_data])   ; Constr 1
            / { * plutus_data => plutus_data }
            / [ * plutus_data ]
            / int
            / bytes
```

### Verification Process

To verify a script using this metadata:

1. **Retrieve metadata**: Query the blockchain for transactions containing metadata label 1984
2. **Reassemble chunks**: Concatenate the bytestring array and decode as CBOR PlutusData
3. **Extract fields**: Parse the constructor ID (compiler type) and fields
4. **Clone source**: Clone the repository at the specified commit hash
5. **Compile**: Using the specified compiler and version, compile the source with any provided parameters
6. **Compute script hash**: Calculate the Blake2b-224 hash of the resulting UPLC bytecode
7. **Match**: If the computed script hash matches an on-chain script hash, the link is verified

A script's source is considered **verified** if and only if the script hash derived from compiling the referenced source exactly matches the on-chain script hash.

### Compiler Reproducibility Requirements

Achieving reproducible builds requires precise control over the compilation environment. Different compiler flags, optimization levels, or even minor version differences can produce different bytecode from identical source code.

Compiler developers integrating with this standard SHOULD document:

1. **Deterministic compilation flags**: Any flags or parameters required to produce deterministic output
2. **Environment constraints**: Required runtime versions, dependencies, or system configurations
3. **Known non-determinism sources**: Any compiler behaviors that may produce varying output and how to mitigate them

Verification tool implementers SHOULD maintain documentation linking to compiler-specific reproducibility guidance.

Verification metadata submitters MUST use the exact compiler version string that produces the matching bytecode. Using approximate versions will result in verification failures.

## Rationale: how does this CIP achieve its goals?

### Why Transaction Metadata?

Transaction metadata provides an ideal storage mechanism for verification records:

- **Lightweight**: No UTxO creation or consumption required
- **Permanent**: Data persists on-chain indefinitely
- **Queryable**: Indexers can efficiently filter by metadata label
- **Established pattern**: Follows precedent set by CIP-0010, CIP-0025, CIP-0088, and others

Alternative approaches were considered and rejected:

- **Datum storage**: Requires UTxO management and incurs higher costs
- **Off-chain databases**: Introduces trust assumptions and availability concerns
- **Centralized registries**: Contradicts decentralization goals

### Why Permissionless Submission?

Requiring deployer signatures for verification would limit the standard's utility:

- Deployers may neglect verification
- Deployers may become unreachable
- Third-party auditors could not independently verify scripts

The permissionless model allows anyone with access to the source code to submit verification records. This maximizes coverage while maintaining integrity through hash matching.

Invalid submissions pose no threat to the system. A malicious actor submitting fabricated metadata gains nothing: the script hash computed from their fake source will not match any on-chain script. Verifiers simply ignore non-matching records.

### Why Constructor-Based Compiler and Schema Encoding?

Using PlutusData constructors to identify both compiler and schema version provides several advantages:

- **Compact**: Single integer vs. multiple fields for compiler name and schema version
- **Self-describing**: The constructor alone tells parsers exactly how to decode the fields
- **Unambiguous**: No string matching or normalization required
- **Extensible**: New constructors can be added without breaking existing parsers
- **Independent evolution**: Each compiler's schema can evolve independently by adding new constructor IDs
- **Type-safe**: Unrecognized constructor IDs are cleanly ignored

String-based compiler names would require case normalization, typo handling, and version disambiguation that constructors avoid entirely. A separate schema version field would add bytes to every record and require parsers to read the version before knowing how to decode the remaining fields.

### Git URL Flexibility

Early feedback requested that the standard not assume GitHub as the hosting provider. The `sourceUrl` field accepts any git-compatible URL, supporting:

- Major hosting platforms (GitHub, GitLab, Bitbucket, Codeberg)
- Self-hosted git servers
- SSH and HTTPS protocols

This ensures the standard remains useful regardless of where developers choose to host their code.

### Backward Compatibility

This CIP introduces a new metadata label and does not modify any existing standards. Scripts deployed before this standard's adoption can still have their source linked by submitting metadata referencing their original source repositories and commits.

The standard is purely additive and has no impact on existing scripts, wallets, or infrastructure that do not implement it.

### Related Work

#### CIP-0072: Cardano dApp Registration & Discovery

[CIP-0072](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0072) defines a standard for dApp developers to register application-level metadata (name, logo, company, categories) and list the script hashes their dApp uses.

This CIP complements CIP-0072 by operating at a different level:

| | CIP-0072 | CIP-0171 |
|--|----------|----------|
| **Scope** | dApp (application) | Script (code) |
| **Purpose** | Discovery & metadata | Source verification |
| **Trust model** | Requires trusting the claimant | Trustless - cryptographic verification |

CIP-0072 lists script hashes but does not verify their origin. This CIP provides the missing link: a cryptographic proof that a script hash was produced from specific source code. The two standards can work together - a dApp registers via CIP-0072, and its scripts are independently verified via CIP-0171, giving users confidence in both the application metadata and the code provenance.

## Path to Active

### Acceptance Criteria

- [ ] Metadata format specification complete and reviewed by the community
- [ ] CDDL schema validated against reference implementation
- [ ] At least one verification tool implementing the standard deployed and operational
- [ ] At least three Cardano protocols have registered verification metadata on mainnet
- [ ] Integration documentation published enabling third-party implementations

### Implementation Plan

- A reference implementation is available at [uplc-link](https://github.com/easy1staking-com/uplc-link)
- Coordination with block explorer teams for potential integration
- Outreach to smart contract developers and protocols for adoption
- Collaboration with compiler maintainers to document reproducibility requirements

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
