---
CIP: ????
Title: NFT Metadata Update Oracles
Status: Proposed
Category: Metadata
Authors:
    - Nicolas Ayotte <nick@equine.gg>
    - George Flerovsky <george@mlabs.city>
    - Samuel Williams <samuel@mlabs.city>
Implementors:
    - Equine <[https://www.equine.gg/](https://www.equine.gg/)>
    - MLabs <[https://mlabs.city/](https://mlabs.city/)>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/430
Created: 2022-11-01
License: CC-BY-4.0
---
# CIP-????: NFT Metadata Update Oracles

## Abstract

This proposal extends the CIP-25 standard for defining and updating token metadata via transaction metadata, by providing a new mechanism to update token metadata without having to mint or burn tokens, while maintaining full backward compatibility with CIP-25. The new mechanism is capable of expressing metadata updates more efficiently than CIP-25 updates.

## Motivation

On Cardano’s eUTxO ledger, native tokens exist without any inherently attached metadata. The ledger does not provide a direct method for preserving any information associated with an asset class of native tokens, as transactions move the tokens from one UTxO to another.

The Media NFT Metadata Standard ([CIP-25](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025)) proposed an indirect way to attach metadata to an asset class — using the metadata field (CBOR tag 721) of its minting transactions. When there are multiple minting transactions for the same asset class, the latest minting transaction’s metadata overrides all previous metadata defined for that asset class.

CIP-25 is widely supported across the Cardano community by blockchain indexers, wallet providers, marketplace applications, and other stakeholders. It has served the community quite well so far, in particular for non-fungible tokens (NFTs) with static metadata (i.e. intended to be mostly immutable after minting).

However, the CIP-25 metadata update mechanism is suboptimal because it requires tokens of the asset class to be minted or burned whenever its metadata is updated. This is incongruous with the often purely-informational purpose of metadata update transactions. While it may sometimes be convenient to combine token minting and metadata updates within the same transaction (e.g. to save on transaction fees), there is a broad range of applications where metadata updates need to be more frequent and independent from minting events.

In practice, there are three main drawbacks to the CIP-25 update mechanism:

1. The metadata authority for an asset class must retain the ability to mint/burn more tokens of the asset class if it wants to retain the ability to post metadata updates/corrections. This compromises the token issuers’ guarantees to token holders that the token supply (or NFT collections) will not be diluted in the future. Token holders are being asked to trust that the metadata authority will not abuse its power to mint new tokens of the same asset class.
2. Executing a minting policy script to mint or burn tokens every time that an asset class’ metadata is updated incurs script execution fees, particularly if the script is Plutus-based, far exceeding the fees corresponding to the actual informational content of the metadata update. This cost can become severe for large collections of thousands of NFTs, and it may be prohibitive for implementing any dynamic fields for such large NFT collections.
3. An asset class’ metadata can only be updated as a whole. This is inefficient (both in terms of transaction fees and ledger bloat) when only a small subset of the metadata fields needs to be updated for a large collection of NFTs, and it can lead to errors if the unmodified fields are improperly copied over to the update.

We encountered these drawbacks during the development of an NFT gaming application, where thousands of NFTs correspond to game assets with properties (e.g. horse age, physical and mental abilities) that evolve both over time and as the NFTs participate in various game-related events on-chain. These properties do not need to interact with smart contract logic directly, which makes transaction metadata a more appropriate place to define them, rather than UTxO datums with complicated state-evolution logic.

Our NFT gaming application is leveraging the Cardano immutable ledger, rather than an off-chain database, as the single source of truth to track the evolution of the game assets’ most important properties. This reassures users that the history of metadata states for a game NFT cannot be retroactively erased or altered by the game admins — although the game admins have the authority to modify metadata going forward, they are retroactively accountable for all past updates.

We expect that this proposal will be useful to many other applications that need to track dynamic on-chain metadata for large NFT collections, particularly in the growing NFT gaming sector. It may also be useful for artists to update on-chain metadata about their art NFTs (e.g. royalty payment receiving address) without having to burn or mint anything.

## Specification

Our proposal extends CIP-25 with a new update mechanism:

-   A metadata oracle can be assigned for a given policy ID.
-   For a policy with a metadata oracle assigned, the metadata oracle can post CIP-???? updates to add, remove, or modify any fields of the token’s CIP-25 metadata, without needing to mint or burn any tokens in the metadata update transactions.
-   The current metadata for a token can be deterministically reconstructed by starting from the latest CIP-25 update to the token, and applying the subsequent CIP-???? metadata updates in ascending blockchain transaction order.

Both CIP-25 and CIP-???? updates affect the token metadata:

-   A CIP-25 update removes all fields in the current metadata state and replaces them with a new complete definition of the metadata state.
-   A CIP-???? update selectively adds, removes, or modifies fields relative to the current metadata state. It does not apply to any asset class that has not had tokens previously minted or any asset class that has not had CIP-25 metadata previously defined, before the CIP-???? update.

However, we recommend that CIP-???? adopters use the new metadata update mechanism exclusively to manage all updates to their token metadata after the initial CIP-25 metadata is set.

Our proposal only affects the `????` top-level CBOR tag of the metadata field in Cardano transactions. (Note: we’re using `????` as a stand-in for the CIP number that will eventually be assigned to this proposal.)

### Assigning a metadata oracle for a token policy ID

A token metadata oracle is defined via two addresses:

-   An oracle update address that is authorized to post metadata updates. For example, this address could be controlled by a bot that automatically posts token metadata updates as needed to the blockchain.
-   An oracle main address that is used to update the oracle update address. This address should be controlled via private keys held in cold storage or hardware wallets.

A metadata oracle can be explicitly assigned to a policy ID by setting the following metadata in a transaction that mints or burns tokens for that policy:

```json
{
    "????": {
        "assign_metadata_oracle": {
            "<policyId>": {
                "main_address": "<Shelley_address>",
                "update_address": "<Shelley_address>"
            }
        }
    }
}
```

While a metadata oracle is not explicitly assigned to a native-script-based policy ID, the policy ID is implicitly assigned a metadata oracle with both addresses set to an address derived from the native script. Specifically, they are both set to an Enterprise address constructed by setting the payment key to the verification key from the native script and keeping the staking key empty.

### Updating an oracle assignment

The metadata oracle assignment for a policy ID can be updated via a transaction signed by the oracle main address key. The transaction must only send ADA from the oracle main address to itself and must not mint any tokens, but it may contain any number of inputs and outputs. Otherwise, the transaction is ignored for the purposes of metadata oracle assignment.

The schema for updating an oracle assignment is the same as for the initial assignment in the minting transaction:

```json
{
    "????": {
        "assign_metadata_oracle": {
            "<policyId>": {
                "main_address": "<Shelley_address>",
                "update_address": "<Shelley_address>"
            }
        }
    }
}
```

The `main_address` or the `update_address` fields for a `<policyID>` can be omitted, in which case the addresses for the omitted fields remain the same for that policy ID.

If a metadata oracle was implicitly assigned to a policy ID before the assignment update, then the implicit assignment is replaced by the new explicit assignment.

### Simple metadata updates

A simple metadata update transaction must only send ADA from the oracle update address to itself and must not mint any tokens, but it may contain any number of inputs and outputs. Otherwise, the transaction is ignored for the purposes of token metadata.

The schema for simple metadata updates in CIP-???? is similar to the CIP-25 schema, but it is nested under `"????".simple_metadata_update` in the transaction metadata object.

```json
{
    "????": {
        "simple_metadata_update": {
            "<policyId>": {
                "<tokenName>": {
                    "<metadataField>": "<metadataValue>"
                }
            }
        }
    }
}
```

To remove a metadata field, set its value explicitly to `null` in the metadata update.

### Regex metadata updates

The schema for regex metadata updates is as follows:

```json
{
    "????": {
        "regex_metadata_update": {
            "<policyId>": {
                "<tokenNameRegex>": {
                    "<metadataField>": "<metadataValue>"
                }
            }
        }
    }
}
```

A regex metadata update transaction must only send ADA from the oracle update address to itself and must not mint any tokens, but it may contain any number of inputs and outputs. Otherwise, it is ignored for the purposes of token metadata.

The only difference from the simple metadata update is that here the token names are defined in terms of PCRE regular expressions (regex). The regex metadata update applies to any previously minted token whose policy ID matches `<policyID>` and whose token name matches the `<tokenNameRegex>` regular expression.

For example, the following metadata update would apply to every Equine pioneer horse between `EquinePioneerHorse05000` and `EquinePioneerHorse05999`:

```json
{
    "????": {
        "regex_metadata_update": {
            "30ed3d95db1d6bb2c12fc5228a2986eab4553f192a12a4607780e15b": {
                "^EquinePioneerHorse05\\d{3}$": {
                    "age": 2
                }
            }
        }
    }
}
```

The regular expression pattern in `<tokenNameRegex>` is defined according to the grammar in:

-   European Computer Manufacturers Association, "ECMAScript Language Specification 5.1 Edition", ECMA Standard ECMA-262, June 2011. Section 15.10. [https://www.ecma-international.org/wp-content/uploads/ECMA-262_5.1_edition_june_2011.pdf](https://www.ecma-international.org/wp-content/uploads/ECMA-262_5.1_edition_june_2011.pdf)

### Tabular metadata updates

Tabular metadata updates use a condensed rectangular format to specify new values for a fixed set of fields for a large number of assets. Specifically, we use the comma-separated values (CSV) format:

```json
{
  "????": {
	  "tabular_metadata_update": {
	    "<policyId>": "<CsvValue>"
  }
}
```

A tabular metadata update transaction must only send ADA from the oracle update address to itself and must not mint any tokens, but it may contain any number of inputs and outputs. Otherwise, it is ignored for the purposes of token metadata.

The `<CsvValue>` must be encoded as a single bytestring containing a whole CSV table, which must follow the following rules:

-   The first row (i.e. the header row) contains column names.
-   The first column name is `tokenName`.
-   Each of the other column names specifies a field name at the top level of the metadata of an asset class, or a path of dot-separated field names to reach a field nested more deeply within the metadata.
-   The values in the first column are token names.
-   Each row of the table specifies the values to be applied to the metadata fields corresponding to the column names for the token name specified in the first cell of that row.

For example, in a given tabular metadata update, we could set the `<CsvValue>` for a given policy ID to the bytestring representation of the following CSV table:

```
tokenName,age,stats.acceleration,stats.agility,stats.endurance,stats.speed,stats.stamina
EquinePioneerHorse00000,3,34,16,18,51,33
EquinePioneerHorse00012,2,24,48,12,32,18
EquinePioneerHorse00315,3,33,34,41,14,31
EquinePioneerHorse01040,4,19,22,21,21,50
EquinePioneerHorse09175,1,24,11,36,22,14
```

A tabular metadata update with the above `<CsvValue>` applied to a given `<policyID>` is equivalent to the following simple metadata update:

```json
{
    "????": {
        "simple_metadata_update": {
            "<policyId>": {
                "EquinePioneerHorse00000": {
                    "age": 3,
                    "stats": {
                        "acceleration": 34,
                        "agility": 16,
                        "endurance": 18,
                        "speed": 51,
                        "stamina": 33
                    }
                },
                "EquinePioneerHorse00012": {
                    "age": 2,
                    "stats": {
                        "acceleration": 24,
                        "agility": 48,
                        "endurance": 12,
                        "speed": 32,
                        "stamina": 18
                    }
                },
                "EquinePioneerHorse00315": {
                    "age": 3,
                    "stats": {
                        "acceleration": 33,
                        "agility": 34,
                        "endurance": 41,
                        "speed": 14,
                        "stamina": 31
                    }
                },
                "EquinePioneerHorse01040": {
                    "age": 4,
                    "stats": {
                        "acceleration": 19,
                        "agility": 22,
                        "endurance": 21,
                        "speed": 21,
                        "stamina": 50
                    }
                },
                "EquinePioneerHorse09175": {
                    "age": 1,
                    "stats": {
                        "acceleration": 24,
                        "agility": 11,
                        "endurance": 36,
                        "speed": 22,
                        "stamina": 14
                    }
                }
            }
        }
    }
}
```

The CSV format is defined by the following standard:

-   Internet Engineering Task Force, “Common Format and MIME Type for Comma-Separated Values (CSV) Files", Request for Comments 4180, October 2005. [https://www.ietf.org/rfc/rfc4180.txt](https://www.ietf.org/rfc/rfc4180.txt)

### Order of application for updates

Up to network consensus, the Cardano blockchain imposes a total ordering on transactions added to the chain — each transaction can be indexed by the slot number of the block that added it to the chain, and the transaction’s index within that block. Network nodes may disagree about which blocks have been added most recently to the blockchain; however, the disagreement about whether a particular transaction was added at a particular position in the total order decreases exponentially as more and more blocks are added to the chain.

To reconstruct the metadata state for a given asset class, scan through the sequence of transactions in a Cardano node’s blockchain, applying the CIP-25 and CIP-???? updates in the order that they are encountered in this sequence. If the Cardano node rolls back some blocks from the chain tip, then roll back the updates from those blocks as well.

We recommend that token metadata oracle operators wait for their metadata update transactions to be confirmed at a sufficient block depth before submitting any subsequent metadata updates for the same asset classes. Doing so should minimize any confusion about the order of simultaneous pending metadata updates while the Cardano network settles toward consensus.

A transaction that contains a CIP-25 update may also contain an explicit oracle assignment, but these can be applied in parallel because they do not clash with each other. On the other hand, a CIP-25 update transaction cannot contain CIP-???? token metadata updates, because CIP-25 updates can only occur in minting transactions while CIP-???? token metadata transactions can only occur in non-minting transactions.

A transaction can contain CIP-???? token metadata updates of different types, plus oracle assignment updates. In this case, apply the updates in the following sequence:

1. Apply the CIP-???? regex update.
2. Apply the CIP-???? tabular update.
3. Apply the CIP-???? simple update.
4. Apply the CIP-???? oracle assignment update.

We recommend that token metadata oracle operators not mix multiple update types in the same transaction, unless they have a clear understanding of the outcome of applying the updates in the above sequence.

### Token metadata indexer

The CIP-???? token metadata indexer begins with a configuration of the policy IDs for which it will be tracking metadata. Optionally, it can be configured to track metadata for all tokens on Cardano.

The indexer monitors the blockchain for minting transactions. If such a minting transaction mints tokens of a tracked policy ID and contains an explicit oracle assignment and/or CIP-25 metadata for that policy ID, then the indexer caches that assignment and metadata in its database. If the transaction does not contain an explicit oracle assignment for the policy ID, and there is no prior oracle assignment, then the indexer caches the implicit oracle assignment for the policy ID in its database.

The indexer continues to monitor minting transactions for the policy IDs that it’s tracking, applying oracle assignment updates and CIP-25 metadata updates accordingly in its database. A CIP-25 metadata update is applied as a wholesale replacement of the metadata cached in the indexer database for the respective asset classes.

For each oracle main address currently assigned to a policy ID, the indexer monitors the blockchain for non-minting transactions that only send ADA from the oracle main address to itself and contain oracle assignment updates in their metadata. The indexer updates its database to reflect these explicit oracle assignments and removes any implicit assignments that were replaced by explicit assignments.

For each oracle update address currently assigned to a policy ID, the indexer monitors the blockchain for non-minting transactions that only send ADA from the oracle update address to itself and contain CIP-???? token metadata updates. The indexer applies these metadata updates in the order defined in [Order of application for updates](https://www.notion.so/Order-of-application-for-updates-07b8a74001c9484698f400f9c5e1c7c8). CIP-???? metadata updates are applied to the asset classes and metadata fields that they target, while keeping all other fields the same.

For tabular metadata updates, the bytestring CSV value may get broken up into an array of bytestring chunks in the CBOR representation. When this happens, the indexer recombines the chunks into the whole CSV table before applying the tabular metadata update.

To be able to handle blockchain rollbacks, the indexer keeps track of past metadata states for its policy IDs, going back 2160 blocks (~12 hours) from the current blockchain tip. Cardano’s `securityParam` Shelley Genesis parameter prevents nodes from rolling back more than 2160 blocks. If the Cardano node informs the indexer of a rollback, the indexer restores the past metadata state that existed immediately before all the metadata updates in the rolled-back blocks were applied.

For compatibility with existing applications that are already relying on CIP-25 metadata indexers, the CIP-???? indexer provides a similar API so that those applications can get and display the current CIP-???? token metadata in the same way that they have been for CIP-25 metadata. The indexer indicates that it is following the CIP-???? standard.

## Rationale

We pursued the following design goals in our solution:

1. Maintain backward compatibility with CIP-25 — tokens that only use CIP-25 updates should have token metadata displayed identically by CIP-25 indexers and CIP-???? indexers.
2. Ensure that the current token metadata can be reconstructed by only looking at the blockchain, without accessing any external resources.
3. Allow token metadata to be updated by designated authorities without minting or burning tokens.
4. Allow existing token issuers to opt into and out of the CIP-???? update mechanism without having to remint all of their existing tokens.
5. Allow designated authorities to securely rotate any keys that they use in their automated and networked processes (e.g. oracle update address used by a bot to update token metadata).
6. Allow token metadata to be updated more efficiently than by a wholesale replacement of the entire metadata object for an asset class.
7. Minimize the time and resource usage required for an indexer to apply CIP-25 and CIP-???? updates for an asset class and then serve the resulting token metadata to applications.
8. Gracefully handle blockchain rollbacks that modify the sequence of CIP-25 and CIP-???? metadata updates for an asset class.

### Backward compatibility

We maintain full backward compatibility with CIP-25:

-   CIP-25 updates are respected and applied in the same way as before by the CIP-???? indexer.
-   CIP-???? updates are namespaced under a different top-level CBOR tag than CIP-25, in order to prevent any clashes between field names, policy IDs, and token names.
-   The CIP-???? indexer provides the accumulated CIP-25 and CIP-???? metadata via the same API as the CIP-25 indexer.

### Using an assigned oracle for token metadata updates

We recognize CIP-???? updates only if they are issued by an oracle currently assigned for the corresponding policy IDs. This assignment is either directly authorized by the token issuer (explicitly or implicitly) or else indirectly authorized by the token issuer via the delegated authority that the token issuer placed in the originally assigned oracle to transfer the assignment to other oracles. Therefore, all authority to post valid CIP-???? updates about a token originates from the token issuer.

An alternative design could have oracles that declare themselves as sources of metadata for tokens, without authorization from anyone, and then users could voluntarily subscribe to the metadata oracles that they wish to follow. However, such an approach would make it very difficult for the Cardano ecosystem to converge on a single objective metadata state for a token, as each user would have his own subjective view of token metadata based on his oracles subscriptions. This alternative approach could be interesting to allow secondary/auxiliary metadata to be defined for tokens, but it is unsuitable for the primary metadata that CIP-25 and CIP-???? seek to manage.

### Identifying oracles by addresses

We use two addresses to identify an oracle when assigning it to a policy ID. It would be simpler to use a single oracle address, but we chose to separate the main address (authorized to reassign the oracle) from the update address (authorized to post updates) for an oracle. We did this to mitigate the risk of using the update address in an automated process on a network machine, and to allow the update address to be safely rotated via a transaction that can only be signed on a cold storage or hardware wallet device using the main address.

Instead of using addresses to identify oracles, we could have identified oracles by minting policies (not the minting policies to which oracles are assigned). In this alternative design, a minting policy `X` could have an assigned oracle identified by minting policy `A`. Under such an assignment, a CIP-???? update for a token under `X` would be valid if the update transaction consumed a utxo that contained a token of minting policy `A`. In other words, the holder of an `A` token would be allowed to post metadata updates about any `X` tokens.

This minting-policy-based alternative for identifying oracles may be more advantageous for more flexibly managing oracle authorization (including rate-limiting, time-boxing, etc.) and proving data provenance to on-chain scripts. These advantages are relevant for oracles that provide information in utxo datums meant for use in smart contracts, but they are not as relevant for this CIP, where we seek to provide a method to provide updateable token metadata via transaction metadata (as a direct extension of CIP-25). Furthermore, it is easier to track transactions originating from a given address in an indexer than to keep track of all the people who control various authorization tokens, at a given time.

### Restricting CIP-???? update transactions

We prohibit CIP-???? oracle assignment updates and metadata updates from occurring in transactions that mint tokens, in order to avoid awkward clashes with CIP-25 metadata transactions. Also, it does not make sense conceptually for CIP-25 metadata transactions to coincide with CIP-???? updates. CIP-25 should be used to define the initial metadata for an asset class, and then CIP-???? updates should be used for any subsequent changes to that metadata.

We require CIP-???? updates to occur in transactions that only send ADA from an oracle address (main or update, as appropriate), to prevent unforeseen interactions with other mechanisms that may have negative consequences. CIP-???? update transactions should have the singular purpose of interacting with the CIP-???? update mechanism.

### Implicit oracle assignment

The implicit method of assigning a metadata oracle is needed to allow existing token issuers to opt into the CIP-???? update mechanism. Their minting policies may no longer allow any more token minting or burning, which would prevent the token issuers from being able to explicitly assign an oracle via a CIP-25 update for those policies. The implicit assignment method bootstraps the CIP-???? update mechanism for these policies.

The implicit address is of the Enterprise address type, to avoid having to deal with staking keys. If needed, the metadata oracle operator can send ADA to the Enterprise address, and then spend it if the operator still controls the payment key of that Enterprise address.

### Opting out of CIP-????

Opting out of the CIP-???? update mechanism can be done by explicitly assigning an oracle with addresses from which ADA cannot be spent (e.g. Plutus AlwaysFails). If the minting policy does not allow any more minting or burning, then this is an irreversible opt-out.

### Regex metadata updates

When managing large collections of thousands of NFTs, one often needs to set a given field to the same value for many NFTs. Doing this individually for each NFT via CIP-25 updates or CIP-???? simple updates is inefficient, so we have proposed the regex metadata update as a succinct way to specify a mapping from multiple token names to a single metadata update.

### Tabular metadata updates

Another common use case for dynamic token metadata involves having a set of volatile fields that should receive relatively frequent updates, but where those updates should be different for each NFT. Labeling each field value update with its field name for each NFT is very verbose, especially if the field is deeply nested within the metadata schema for the NFT. For this use case, we have proposed the tabular metadata update format as a way to avoid this repetition — field names/paths are defined once in the column names of a rectangular table and applied consistently for each row of updated metadata field values.

Rectangular tables are a standard format used in the data analytics field for these situations, and the CSV format is the most widely used and interoperable rectangular data format.

## Path to Active

### Acceptance Criteria

This proposal may be considered active if:

1. The solution meets the design goals listed in the [Rationale](https://www.notion.so/Rationale-4c5ae115646841539e734672fd67ba22) section to a satisfactory degree.
2. The indexer and simple tools to construct CIP-???? update transactions (as described in the [Specification](https://www.notion.so/Specification-2cdbc357edda4b08b581b25d63968e3c) section) are fully implemented and provided in an open-source (Apache 2.0 licensed) repository with sufficient documentation.
3. The CIP-???? metadata format, indexer, and/or indexer API are used by several stakeholders in the Cardano ecosystem, including dApps, blockchain explorers, analytics platforms, etc.

### Implementation Plan

Equine and MLabs are collaborating on developing the indexer described in this CIP and the Equine NFT gaming application will be using CIP-???? updates to manage metadata updates for its large collection of thousands of NFTs under multiple minting policies.

We will include detailed documentation, example configurations, and tutorials on how to adapt the tools to new projects.

We are actively engaged in discussions with other stakeholders in the Cardano ecosystem that are interested in adopting this CIP to their projects, platforms, and tools.

## Copyright

This CIP is licensed under the Creative Commons Attribution 4.0 International Public License ([CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)).

---
