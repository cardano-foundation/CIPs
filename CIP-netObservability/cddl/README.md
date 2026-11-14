# Observability CDDL package
This CDDL draft assumes that it can be integrated into experimental N2N v16 and can use the next available miniprotocol MUX, number 11. 


## Files

| File | Role |
| --- | --- |
| [network.base.cddl](./network.base.cddl) | shared word sizes / base types |
| [node-to-node-version-data-v16.cddl](./node-to-node-version-data-v16.cddl) | V16 VersionData (upstream-aligned; no observability flag yet) |
| [observability.cddl](./observability.cddl) | mini-protocol messages + envelopes |
| [field-registry.md](./field-registry.md) | standard keys 1–6; Amaru experimental catalogue |
| [vectors/README.md](./vectors/README.md) | golden CBOR hex |

## Prototype decisions

| Item | Choice |
| --- | --- |
| Mux id | **11** experimental only (not permanently allocated) |
| N2N floor | **V16** for known experimental peers |
| Capability | Prototype: config + known peers. Final: explicit `observabilitySupport` (likely new N2N version) |
| State machine | One-shot: GetPublications → Publications → Done (**no msgDone**) |
| `publicationVersion` | **1** on every publication; encrypted plaintext = CBOR `openPayload` |
| `snapshot_slot` | Per publication |
| Standard fields | `1`–`6`: name, version major/minor/patch, node_type, git_revision |
| Experimental fields | namespaced tstr; Amaru catalogue typed in CDDL (`amaru.version`, peers, …) |
| Empty `[]` | Protocol enabled; no publication currently in cache |