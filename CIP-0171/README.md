---
CIP: 171
Title: On-chain Smart Contract Bytecode Verification
Category: Metadata
Status: Proposed
Authors:
    - Giovanni Gargiulo <gargiulo.gianni@gmail.com>
Implementors: []
Discussions:
    - Forum Discussion: https://forum.cardano.org/t/cip-idea-smart-contract-source-code-verification-metadata/152403
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1136
    - Amendment PR: <url-pending>
Created: 2026-01-19
License: CC-BY-4.0
---

## Abstract

This CIP defines a decentralized, on-chain metadata standard for linking Cardano script hashes to their published source code. Using transaction metadata label `1984`, anyone can publish records containing the source repository URL, git commit hash, compiler type and version, the build environment used to compile the script (for Aiken), and script parameters. Verifiers can then independently compile the source and confirm that the resulting script hash matches an on-chain script, establishing a verified link between the deployed script and its source code origin.

Unlike centralized verification services that act as trusted intermediaries, this standard enables permissionless verification where anyone can submit and validate records without relying on third parties. The design is intentionally spam-resistant: invalid or fabricated submissions are harmless because non-matching script hashes simply have no corresponding on-chain scripts to link to.

This standard supports multiple Cardano smart contract compilers including Aiken, Plutarch, PlutusTx, Scalus, plu-ts, and OpShin, with a mechanism for adding new compilers as they emerge.

## Motivation: Why is this CIP necessary?

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
| 0 | Aiken | 2 | Aiken |
| 1 | Plutarch | 1 | Haskell |
| 2 | PlutusTx | 1 | Haskell |
| 3 | Scalus | 1 | Scala |
| 4 | plu-ts | 1 | TypeScript |
| 5 | OpShin | 1 | Python |

This design allows each compiler's metadata schema to evolve independently. If a compiler requires changes to its field layout (adding, removing, or reordering fields), a new constructor ID is assigned for the updated schema version. Implementations encountering an unrecognized constructor SHOULD ignore the record rather than fail.

New compilers or schema versions may be added by submitting a pull request to this CIP. Constructor IDs are assigned sequentially and MUST NOT be reused or reassigned.

#### Versioning note: in-place revision of the Aiken schema

Constructor 0 carries schema version 2 while keeping constructor ID 0. This
departs from the two rules stated immediately above:

> If a compiler requires changes to its field layout (adding, removing, or
> reordering fields), a new constructor ID is assigned for the updated schema
> version.

> Constructor IDs are assigned sequentially and MUST NOT be reused or
> reassigned.

Both rules remain in force. This revision is a **one-time exception**, narrowed
to constructor 0 and to this revision only, granted on three grounds:

1. **Status.** This CIP is `Proposed`, not `Active`. Proposed standards are
   explicitly revisable.
2. **Single implementation.** Constructor 0 has one known implementation, and
   it is the reference implementation named in the Implementation Plan.
3. **The prior records were replaced, not stranded.** Every record that existed
   on mainnet under the previous Aiken layout has been re-published by its
   author in the revised layout, with one exception: a duplicate submission for
   a repository and commit already covered by a re-published record, which
   carried no parameters and never completed verification. No consumer is left
   holding a record that this document no longer describes.

Consumers MUST parse constructor 0 as a fixed six-element list per this
document. Records under any constructor that do not decode to that
constructor's field layout — wrong element count, wrong element types, or CBOR
that does not decode at all — MUST be ignored rather than treated as an error;
metadata label 1984 is shared with unrelated payloads and non-conforming data
under the label is expected, not exceptional.

Any future change to any compiler's field layout, constructor 0 included, MUST
use the standard mechanism and be assigned a new constructor ID. This exception
is not a precedent and is not available again.

### Field Layout

Field layout is per-constructor. Aiken (constructor 0, schema version 2) uses a
fixed six-element list; the remaining compilers use the five-field layout below.

#### Constructor 0 (Aiken)

The constructor's fields form a fixed six-element list. All fields are always
present; optionality is expressed through empty values rather than omission.

| Index | Field | Type | Description |
|-------|-------|------|-------------|
| 0 | sourceUrl | Bytes (UTF-8) | Git-compatible repository URL |
| 1 | commitHash | Bytes | Git commit hash (20 bytes for SHA-1, 32 bytes for SHA-256) |
| 2 | sourcePath | Bytes (UTF-8) | Path to the project directory within the repository; empty bytes = repository root |
| 3 | compilerVersion | Bytes (UTF-8) | Exact compiler version string (e.g., "v1.1.3") |
| 4 | env | Bytes (UTF-8) | Build environment identifier; for Aiken, the module name passed to `aiken build --env`. Empty bytes = built without an environment flag |
| 5 | parameters | Map | Script hash to parameter data mappings; may be empty |

#### Constructors 1–5 (Plutarch, PlutusTx, Scalus, plu-ts, OpShin)

The constructor's fields contain the following data in order:

| Index | Field | Type | Required | Description |
|-------|-------|------|----------|-------------|
| 0 | sourceUrl | Bytes (UTF-8) | Yes | Git-compatible repository URL |
| 1 | commitHash | Bytes | Yes | Git commit hash (20 bytes for SHA-1, 32 bytes for SHA-256) |
| 2 | sourcePath | Bytes (UTF-8) | No | Path to source file within repository (empty if root) |
| 3 | compilerVersion | Bytes (UTF-8) | Yes | Exact compiler version string (e.g., "v1.1.3") |
| 4 | parameters | Map | No | Script hash to parameter data mappings |

These layouts are unchanged by this revision.

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

#### Env

The `env` field applies to constructor 0 (Aiken) only. It records the build
environment used to compile the script: the environment module name passed via
`aiken build --env <name>`.

Empty bytes indicate the build was invoked **without** the `--env` flag. This
is not shorthand for `--env default`: a build that explicitly uses the default
environment module MUST record `default`. Verifiers reproduce the build by
invoking the compiler with `--env <env>` when the field is non-empty, and with
no environment flag when it is empty. A verifier that rebuilds an empty-`env`
record with no environment flag and obtains a different script hash has a
**failed verification claim**, not a record with a missing field: it MUST NOT
retry with a guessed environment, and MUST report the record as unverified.

A non-empty value MUST match, in full, `[a-z][a-z0-9_]*` — treat the expression
as anchored at both ends, so the whole value must be consumed by it — and MUST NOT
exceed 64 bytes.

#### Parameters

The `parameters` field maps script hashes to their initialization parameters. This supports parameterized scripts where the same source code produces different script hashes depending on input parameters.

Structure:
```
Map<ScriptHash, List<Bytes>>
```

Where:
- `ScriptHash` is the 28-byte Blake2b-224 hash of the compiled script
- `List<Bytes>` contains the parameters applied to produce that specific script, in application order; each list element is a bytestring wrapping the CBOR encoding of one parameter

### CDDL Schema

```cddl
verification_metadata = { 1984: chunked_plutus_data }

chunked_plutus_data = [ + bounded_bytes ]

bounded_bytes = bytes .size (1..64)

; When chunks are concatenated and decoded as CBOR:
; Constructor ID encodes both compiler and schema version
verification_data = #6.121([aiken_fields])     ; Constructor 0 = Aiken, schema v2
                  / #6.122([compiler_fields])  ; Constructor 1 = Plutarch, schema v1
                  / #6.123([compiler_fields])  ; Constructor 2 = PlutusTx, schema v1
                  / #6.124([compiler_fields])  ; Constructor 3 = Scalus, schema v1
                  / #6.125([compiler_fields])  ; Constructor 4 = plu-ts, schema v1
                  / #6.126([compiler_fields])  ; Constructor 5 = OpShin, schema v1
                  ; Future schema versions will be assigned new constructor IDs

aiken_fields = [ source_url, commit_hash, source_path, compiler_version, env, parameters ]

compiler_fields = [ source_url, commit_hash, source_path / null, compiler_version, ? parameters ]

env = bytes .size (0..64)    ; UTF-8; empty = built without an environment flag;
                             ; non-empty values match [a-z][a-z0-9_]* in full
parameters = { * script_hash => parameter_list }
script_hash = bytes .size 28
parameter_list = [ * bytes ]  ; each element is a bytestring wrapping the CBOR
                              ; encoding of one parameter

source_url = bytes          ; UTF-8 encoded URL
commit_hash = bytes         ; 20 or 32 bytes
source_path = bytes         ; UTF-8 encoded path
compiler_version = bytes    ; UTF-8 encoded version string

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
5. **Compile**: Using the specified compiler and version, compile the source with any provided parameters and with the recorded build environment — for Aiken, `aiken build --env <env>` when the `env` field is non-empty, and with no environment flag when `env` is empty
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

## Rationale: How does this CIP achieve its goals?

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

### Residual Limits on Reproducibility

Recording the build environment closes the largest remaining gap between a
recorded build and a verifier's rebuild, but it does not close all of them. Two
known sources of drift remain for Aiken: dependency versions in `aiken.toml`
may be pinned to mutable git references, so a rebuild can resolve a dependency
to different source than the original build did; and trace flags are governed
by convention and defaults rather than being recorded in the metadata, so a
build that departed from the default convention will not be reproduced. Both
limits are fail-closed. The verification assertion is byte-equality between the
rebuilt script hash and the on-chain script hash, so a mismatch caused by either
source produces a **non-verification** — the record simply does not verify. No
combination of these limits can produce a false verification, because no
sequence of them can make an unequal pair of hashes compare equal.

### Compatibility Impact of the Aiken Schema Revision

The in-place revision of constructor 0 was assessed against the deployed record
corpus rather than argued in the abstract. At the time of this revision,
exactly six CIP-0171 records existed on Cardano mainnet under metadata label
1984, all submitted through the reference implementation:

- `7e6d7d45f072ad01b2ad3ced26c328f7afd0f7fefc6a490a914496f8f0f27bf2`
- `36f3377e558c8b8c7fa02be5bf117f02e318c3ac0008655cc7c7fe16d07f50d4`
- `f7e919f17c4842ce267e4606b7d6b6a5639fdb3d4848426f3240fdfa38f75a26`
- `ac5a74fe08d069b7a8993a4da46f212a5118823ff195a0df282e64fbe415008f`
- `2a88dd41f1fb85235fe97ab00fc0ea4ecfe11ea8ce13ba60cf9d10c0bec00e83`
- `5f6bf196a5d6388c699ac60ae878ff56288066797efdf95883ddcfeab63dd8a4`

All six were re-published by their author in the revised layout. The set of
records this document leaves undescribed is therefore empty, and the
compatibility cost of the revision is zero rather than small.

The same survey found 46 further transactions carrying metadata label 1984 from
unrelated projects, which use the label for their own purposes and do not
follow this standard. Label sharing is observed reality on mainnet, not a
hypothetical. This is why implementations MUST ignore records that do not
decode to a layout described here rather than treat them as errors: a
conforming reader will encounter non-conforming payloads under this label
routinely, and must remain unbothered by them.

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
