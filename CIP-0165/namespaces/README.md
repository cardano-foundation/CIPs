# Namespaces

This is directory of the supported namespaces.

Each namespace defines a non-intersecting slices of the data.

| Shortname            | Content                         | Key size | Key description |
| -------------------- | ------------------------------- | -------- | --------------- |
| blocks/v0            | Blocks created                  | 36       | keyhash of the stake pool |
| gov/committee/v0     | Governance action state         | 8        | epoch |
| gov/constitution/v0  | Constitution                    | 8        | epoch |
| gov/pparams/v0       | Protocol parameters             | 4        | current, previous, or future |
| gov/proposals/v0     | Update proposals                | 34       | address of the proposal in transactions |
| pool_stake/v0        | Stake delegation                | 28       | stake pool keyhash |
| nonce/v0             | Nonces                          | 1        | zero key |
| snapshots/v0         | snapshots                       | 32       | key type, stage, value type (see docs) |
| utxo/v0              | UTXOs                           | 34       | utxo address in the transaction |

Key specifications are described in cddl specification comments.
