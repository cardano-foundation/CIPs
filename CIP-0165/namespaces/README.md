# Namespaces

This is directory of the supported namespaces.

Each namespace defines a non-intersecting slices of the data.

| Shortname                              | Content                    | Key size | Key description                             |
| -------------------------------------- | -------------------------- | -------- | ------------------------------------------- |
| blocks/v0                              | Blocks created             | 36       | keyhash of the stake pool                   |
| entities/accounts/v0                   | Accounts                   | 8        | epoch                                       |
| entities/committee/v0                  | Entities committee         | 8        | epoch                                       |
| entities/dreps/v0                      | DReps                      | 29       | credential                                  |
| entities/stake_pools/v0                | Stake pools                | 28       | stake pool key hash                         |
| entities/stake_pools_vrf_key_hashes/v0 | Stake pools VRF key hashes | 32       | stake pool VRF key hash                     |
| gov/committee/v0                       | Governance action state    | 8        | epoch                                       |
| gov/constitution/v0                    | Constitution               | 8        | epoch                                       |
| gov/pparams/v0                         | Protocol parameters        | 4        | current, previous, or future                |
| gov/proposals/v0                       | Update proposals           | 34       | address of the proposal in transactions     |
| gov/proposals/roots/v0                 | Update proposals roots     | 1        | tag purpose of the proposal                 |
| nonces/v0                              | Nonces                     | 1        | zero key                                    |
| snapshots/mark/v0                      | snapshots                  | 32       | key type, mark stage, value type (see docs) |
| snapshots/set/v0                       | snapshots                  | 32       | key type, set stage, value type (see docs)  |
| snapshots/go/v0                        | snapshots                  | 32       | key type, go stage, value type (see docs)   |
| utxo/v0                                | UTXOs                      | 34       | utxo address in the transaction             |

Key specifications are described in cddl specification comments.
