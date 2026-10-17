# Observability field registry (prototype)

Logical field identifiers from the draft observability-CIP map to wire keys in
`openPayload` / sealed-box plaintext.

## Standardized integer keys (publicationVersion = 1)

Only fields with agreed semantics get numeric IDs. Strongly typed in
[`observability.cddl`](./observability.cddl).

| fieldKey | logical id | CBOR value | notes |
| -------: | ---------- | ---------- | ----- |
| 1 | `node_name` | tstr | e.g. `amaru`, `cardano-node` |
| 2 | `node_version_major` | `word16` | |
| 3 | `node_version_minor` | `word16` | |
| 4 | `node_version_patch` | `word16` | |
| 5 | `node_type` | tstr | process class, e.g. `full`, `relay`, `block_producer` |
| 6 | `git_revision` | tstr | short VCS revision when available |

Unknown future integer keys: consumers MUST ignore them (forward compatibility).
Producers MUST NOT emit undefined standard keys until an observability-CIP amendment assigns them.

### Intentionally omitted (available elsewhere)

Do **not** standardize these as observability fields; consumers already get them
from handshake / dedicated mini-protocols:

- `node_n2n_supported_versions` (handshake VersionData)
- `node_peer_sharing_enabled` (handshake VersionData)
- `chain_network` (handshake / topology)
- `chain_tip_slot` (ChainSync)

## Not yet standardized (do not assign numeric IDs)

Keep these experimental / namespaced until semantics are agreed:

- `system_cores`, `system_memory`
- `chain_pool_bech32`, `chain_block_height`
- `chain_state_hash` (especially provisional)

Example experimental wire keys (tstr):

```text
"dingo.peers_remote"
"amaru.some_metric"
"cardano_node.mempool_tx_count"
```

Graduation path: proven useful across implementations → observability-CIP amendment → new integer key.


Wire types are declared in [`observability.cddl`](./observability.cddl) `openPayload`.

| config / wire id | kind | CBOR value | notes |
| ---------------- | ---- | ---------- | ----- |
| `node_name` | standard key 1 | tstr | always `"amaru"` |
| `node_version_major` | standard key 2 | `word16` | package major |
| `node_version_minor` | standard key 3 | `word16` | package minor |
| `node_version_patch` | standard key 4 | `word16` | package patch |
| `node_type` | standard key 5 | tstr | always `"full"` for now |
| `git_revision` | standard key 6 | tstr | short SHA (`amaru --version`) |
| `amaru.version` | experimental tstr | tstr | full semver string |
| `amaru.cpu_cores` | experimental tstr | uint | available parallelism |
| `amaru.process_rss_bytes` | experimental tstr | uint | omitted if unavailable |
| `amaru.peers_inbound` | experimental tstr | uint | accepted inbound |
| `amaru.peers_outbound` | experimental tstr | uint | established outbound |
| `amaru.peers_outbound_connecting` | experimental tstr | uint | outbound dials in flight |
| `amaru.peers_using` | experimental tstr | uint | Diffusion local use |
| `amaru.peers_target_upstream` | experimental tstr | uint | config target |
| `amaru.peers_target_downstream` | experimental tstr | uint | config inbound cap |

