---
CIP: "?"
Title: DRep Groups
Category: Metadata
Status: Proposed
Authors:
    - Tommy <31965230+katomm@users.noreply.github.com>
Implementors:
    - DRepTalk <https://dreptalk.com>
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-11-09
License: CC-BY-4.0
---

## Abstract

DReps already organize themselves into councils, parties and working groups, yet the chain has no record of who belongs to which group. Affiliations live in the databases of individual websites, or in one-sided statements that the DReps concerned never signed.

This CIP defines an on-chain register of DRep groups in transaction metadata under label 8416. A group is created by one metadata event and controlled by a native script, so a group can be run by several admins from the start. Groups are open (any registered DRep joins) or permissioned (an admission policy approves requests). Every DRep joins with its own signature and can always leave without anyone's consent. Every key a group lists as an admin has signed at least once.

There are no tokens, no deposits and no Plutus scripts. The ledger only checks signatures and fees, and indexers apply the rules in this document. Any two indexers that follow it compute the same groups and memberships from the chain alone. A group's profile is a CIP-100 document referenced by hash.

The protocol records affiliation only. A group holds no voting power, casts no votes on chain and never changes a delegation. Many groups will agree to vote together, as a party or council would. That agreement is social, and each member still casts its own vote with its own DRep.

## Motivation: Why is this CIP necessary?

Since the Conway era, DReps form groups: councils that publish joint rationales, parties with a shared platform, regional or professional collectives. Delegators want to know these affiliations when they choose a DRep, and analysts need them to understand how voting power is organized (see [CPS-0033](../CPS-0033/README.md)).

Today there is no standard for this:

- [CIP-0119](../CIP-0119/README.md) describes individual DReps and leaves teams out of scope. It has no affiliation field.
- Websites keep membership lists in their own databases. Another tool cannot verify them and gets a different list from each source.
- Statements posted from a single platform wallet show that the platform recorded an admission. They do not show that the DRep agreed, and the DRep cannot withdraw them.

A shared register needs three properties that none of these offer:

1. **Mutual consent.** A DRep is shown as a member only when it signed its own join, and in a permissioned group only when the group's admission policy also approved it. A group is shown with an admin only when that admin signed.
2. **Exit at any time.** A DRep can always leave with its own signature, whatever the group's policies are and even when the group has lost its keys.
3. **Verifiable from the chain.** Membership follows from transactions alone. No website, database or cache decides a verdict, so every tool shows the same state.

Stakeholders are DReps who want to make an affiliation public, delegators who want to see it, governance tools and explorers that display DReps, and researchers who study the concentration of voting power.

## Specification

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, RECOMMENDED and MAY are to be interpreted as described in RFC 2119.

### Terms

- **Group**: created by one `create` event, identified by its `group_id`.
- **Control policy**: native script that may change the group's policies and profile, or dissolve the group.
- **Admission policy**: native script that may approve or remove members. Required for permissioned groups, absent for open groups.
- **Membership instance**: created by one `join` event, identified by its `join_id`. It moves through the states defined under [Derived state](#derived-state) and never reopens once closed.
- **Event ref**: `[tx_hash, event_index]`, the hash of a transaction and the zero-based position of an event in that transaction's event list. `group_id` and `join_id` are event refs. A transaction cannot contain its own hash, because the body commits to the metadata hash. An event therefore refers to an earlier event of the same transaction with the local form `[event_index]`, for example a `join` at index 1 that references the `create` at index 0 as `[0]`. Indexers expand a local ref to `[own tx_hash, event_index]`, so identities always have the full form. A local ref to the same or a later index is invalid.

### Metadata envelope

Events are carried under transaction metadata label **8416**. A transaction carries at most one label 8416 payload.

The CDDL below is the format that tools produce. Indexers accept a wider set of bytes, defined by the [decoding layers](#decoding-layers) that follow it, and a mismatch with the CDDL alone MUST NOT make an indexer ignore a payload or an event. In particular the payload map is open to unknown keys, the pairing of `mode` and `admission` is fixed, and `update_map` is closed.

```cddl
payload = {
  0 : 1,                    ; version
  1 : [1*64 event],         ; processed in order, at most 64 events
  ? 2 : [1*8 script_bytes]  ; native scripts, at most 8
}
script_bytes = [+ bytes .size (0..64)]  ; one CBOR-encoded native script, chunked
hash28 = bytes .size 28
tx_hash = bytes .size 32
event_ref = [tx_hash, event_index: uint] / [event_index: uint]  ; second form: same transaction
credential = [0, hash28] / [1, hash28]  ; key hash or script hash, as in the ledger
anchor = [url: [+ text .size (0..64)], data_hash: bytes .size 32]

event =
    [0, 0, control: hash28, [], ? profile: anchor]       ; create, open group
  / [0, 1, control: hash28, admission: hash28, ? profile: anchor] ; create, permissioned group
  / [1, group: event_ref, seq: uint, changes: update_map]  ; update
  / [2, group: event_ref, seq: uint]                       ; dissolve
  / [3, group: event_ref, member: credential]              ; join
  / [4, join: event_ref]                                   ; approve
  / [5, join: event_ref]                                   ; leave
  / [6, join: event_ref]                                   ; remove

update_map = {
  ? 0 : hash28,   ; new control policy
  ? 1 : hash28,   ; new admission policy (permissioned groups only)
  ? 2 : anchor    ; new profile
}

; Conway ledger native script, as used for policies and script DReps
native_script =
    [0, hash28]                       ; sig
  / [1, [* native_script]]            ; all
  / [2, [* native_script]]            ; any
  / [3, n: int64, [* native_script]]  ; n_of_k
  / [4, slot: uint64]                 ; after (invalid_before)
  / [5, slot: uint64]                 ; before (invalid_hereafter)
```

- `mode` is 0 for an open group and 1 for a permissioned group. Mode 1 needs a `hash28` admission policy, mode 0 needs the empty array `[]`. Transaction metadata has no null value, so the empty array is the placeholder. The mode is fixed at `create` and cannot change.
- An `update` with an empty `update_map` is valid. It only increments `seq`, which makes pending control transactions stale on purpose (see [Processing rules](#processing-rules)).
- The anchor URL is split into text chunks of at most 64 bytes, as transaction metadata requires. Indexers decode each chunk as UTF-8 and concatenate the results unchanged, without removing a byte order mark or normalizing the text.
- A script entry is split into byte string chunks of at most 64 bytes. Indexers concatenate the chunks in order, then parse and hash the result.

#### Decoding layers

Two indexers MUST reach the same verdict on any bytes, so decoding is defined in three layers, each with a fixed failure effect.

General rules for all layers: arrays and maps MAY be definite or indefinite length. Two map keys are equal when both are unsigned integers with the same value, whatever their encoding length, and any other two keys are equal when their encoded bytes are equal. The payload as a whole MUST be well-formed CBOR that uses all bytes of the label 8416 value.

1. **Payload.** The label 8416 value is decoded from its own bytes. It MUST be a map without duplicate keys, with key 0 equal to 1 and key 1 an array of 1 to 64 entries. Otherwise the whole payload is ignored, including its scripts. A payload with another version is ignored by indexers of this version. Unknown keys of the payload map are ignored, and their values are skipped without being inspected, however deeply they nest. Transaction metadata cannot carry CBOR tags or floats, so they need no rule.
2. **Script list.** If key 2 is present, it MUST be an array of at most 8 entries. Otherwise only key 2 is ignored. Each entry is judged on its own: an entry is skipped when it is not a non-empty array of definite-length byte strings of at most 64 bytes each, when the concatenated bytes do not parse as a native script, or when the script exceeds 64 nodes or a nesting depth of 8. A skipped entry resolves no script, and the other entries stay usable. Every `sig`, `all`, `any`, `n_of_k`, `after` and `before` counts as a node, and the outermost script has depth 1.
3. **Event.** Each entry of key 1 MUST be an array that starts with a known uint tag and matches that tag's shape exactly: arity, types, byte lengths, and the pairing of mode and admission in `create`. An `update_map` with an unknown or duplicate key makes the event invalid, since a change of authority must not be half understood. Byte and text strings at interpreted positions MUST be definite-length, and text MUST be valid UTF-8. Otherwise that event is invalid. Invalid events keep their index, so refs to later events stay stable.

**Native script parsing** follows the `native_script` rule above, which is the one of the Conway ledger, with exact CBOR major types: tags and integers are CBOR integers, a key hash is a definite-length byte string of 28 bytes, arrays may be definite or indefinite, `n_of_k` takes an int64 threshold, time lock slots are uint64, and the script MUST use all bytes of its entry. The complexity limit of layer 2 applies to scripts published in key 2 only. A script DRep's own script comes from its registration and follows the ledger's rules.

#### Scripts

Whether a script is known MUST follow from the chain alone, otherwise two indexers with different caches disagree. A script hash is **resolved at a chain position** when bytes with `blake2b-224(0x00 || bytes)` equal to the hash were published on chain at or before that position in one of these places:

- key 2 of any label 8416 payload in a valid transaction, including the payload that uses it,
- for a member credential `[1, s]` only: the witness set of a `reg_drep` transaction of that credential.

External stores and caches MAY speed up lookups but MUST NOT decide a verdict. An event whose authorization needs a script that is not resolved at its position is invalid, and learning the bytes later does not make it valid. Tools MUST put a policy script into key 2 the first time its hash appears in a group's events.

### Authorization

Only transactions with `is_valid = true` are considered. A transaction that failed phase 2 validation contributes no events.

The **signer set** of a transaction is the union of the key hashes in `required_signers` (body field 14) and the key hashes of all vkey witnesses in the witness set. The ledger verifies every vkey witness against the body hash, whatever role the key plays in the transaction. Listing a key in `required_signers` additionally makes the ledger demand its witness.

**Native script evaluation** uses the signer set and the transaction's validity interval (`invalid_before`, `invalid_hereafter`):

- `sig h`: `h` is in the signer set.
- `all [s...]`: every child is satisfied (true when empty).
- `any [s...]`: at least one child is satisfied (false when empty).
- `n_of_k n [s...]`: at least `n` children are satisfied (false when `n` exceeds the number of children).
- `after s`: `invalid_before` is set and `invalid_before >= s`.
- `before s`: `invalid_hereafter` is set and `invalid_hereafter <= s`.

The ledger does not evaluate these scripts for a transaction that only carries metadata, so indexers apply these rules themselves.

**Member authorization** for credential `[0, h]`: `h` is in `required_signers`. A key-based member must be listed explicitly, so its wallet signed knowingly. For credential `[1, s]`: the native script `s` is resolved at the event's position and satisfied by the signer set. Plutus script credentials are not supported in this version, and events that need their authorization are invalid.

**Policy authorization** (control and admission): the policy script is resolved at the event's position and satisfied by the signer set. `n_of_k 0` and `all []` are satisfied by any transaction, and tools SHOULD refuse to build such policies.

A signed transaction cannot be replayed once included, because its inputs are spent. A signed transaction that was never submitted stays usable until one of its inputs is spent or its validity interval ends. Tools that collect signatures SHOULD set a short validity interval and SHOULD let the initiator make an abandoned transaction unusable by spending one of its inputs.

### Processing rules

The **chain order** is block height, then the position of the transaction in its block, then, inside a transaction, first its certificates in certificate order and then its label 8416 events in event order.

Two kinds of input are processed in this one order:

- **Ledger inputs**: every DRep registration (`reg_drep`) and retirement (`unreg_drep`) certificate of a credential that a `join` event references.
- **Events**: label 8416 events as decoded above.

An event is valid only against the state produced by everything earlier in chain order. Invalid events change nothing.

| Event | Valid when | Effect |
|---|---|---|
| create | shape valid, every referenced policy resolved, control policy satisfied, every listed key signed | new group, `seq = 0`, active |
| update | group active, `seq` equals the group's current `seq`, current control policy satisfied, new policies resolved, no admission change on an open group, every newly listed key signed | applies the changes, `seq + 1` |
| dissolve | group active, `seq` matches, current control policy satisfied | group dissolved for good, every pending or active instance closes with reason `dissolved` |
| join | group active, member authorized, credential registered as a DRep (a `reg_drep` without a later `unreg_drep`), no pending or active instance of this credential in this group | open group: instance `active`, permissioned group: `pending` |
| approve | instance `pending`, group active, current admission policy satisfied | `active` |
| leave | instance `pending` or `active`, member authorized | closed with reason `left` |
| remove | permissioned group, instance `pending` or `active`, current admission policy satisfied | closed with reason `removed` (also rejects a request) |

| Ledger input | Effect |
|---|---|
| `reg_drep` | the credential counts as registered from this point |
| `unreg_drep` | every pending or active instance of the credential closes with reason `retired`, a later registration reopens nothing |

DRep inactivity, the expiry after `drep_activity` epochs without a vote, is ledger state without a certificate. It neither prevents a join nor closes an instance.

Further rules:

- **Consent of listed keys.** A `create` MUST satisfy the control policy it names, and every key listed in its control and admission policies MUST be in the signer set. An `update` that sets a new control or admission policy MUST, in addition to the current control policy, carry the signature of every key in the new policies that is not already listed in the group's current control or admission policy. Removing a key needs no consent from that key.
- `dissolve` does not change `seq`. A dissolved group is terminal, so its `seq` is never checked again.
- `leave` needs nothing from the group. It stays valid after the group loses its keys, after any policy change, and while the instance is pending. Only dissolution or retirement can close the instance first.
- `seq` makes control transactions stale once any other control event of the group is included. Admission events carry no `seq`, so concurrent approval batches do not conflict. Their staleness is bounded by the validity interval of the transaction.
- A closed instance stays closed. Rejoining creates a new `join_id`, and in a permissioned group it needs a new approval.
- A join that was signed before a retirement and included after a new registration is valid. The key holder consented, and the registration check uses the state at inclusion.
- A transaction MAY carry several events, for example one admission round that approves many requests. Each event is checked on its own.
- Open groups have no `remove`. A group that wants to exclude members must be permissioned.
- A DRep MAY be a member of any number of groups.

### Derived state

Instance states are `pending`, `active` and `closed`, with the close reasons `left`, `removed`, `retired` and `dissolved`. A DRep is a **member** of a group when it has an `active` instance and the group is not dissolved. Indexers SHOULD expose per instance: `join_id`, credential, state, close reason, and the chain positions of the join, the approval and the close.

**Rollbacks.** An indexer MUST undo every event and ledger input of rolled back blocks and recompute the state from the remaining inputs. Waiting for a confirmation depth before showing a state as final is RECOMMENDED (10 blocks), and it does not replace this rule.

### Group identifier

The display form of a `group_id` is the bech32 encoding, with human-readable prefix `group`, of the 34 bytes `tx_hash || uint16be(event_index)`. Example: `group1x9q04su93gdqvuklks4802dhf82j7j08nsh7qsnr0ve0xmg8qk9sqqqdtx542` is the group created by event 0 of preprod transaction `3140fac3858a1a0672dfb42a77a9b749d52f49e79c2fe042637b32f36d07058b`.

### Group profile

The `profile` anchor points to a [CIP-0100](../CIP-0100/README.md) document with `@context`, `hashAlgorithm` and `body`. The anchor hash is blake2b-256 over the raw document bytes, as in CIP-0100. The `body` has these fields:

| Field | Type | |
|---|---|---|
| `name` | string | required, display only, not unique |
| `description` | string | optional |
| `website` | URL | optional, see [Website proof](#website-proof) |
| `image` | URL | optional |
| `charter` | URL | optional, the group's rules |
| `paymentAddresses` | list of `{ address, purpose?, treasuryScript? }` | optional |

The CIP-0100 schema lists `authors` as required. Like CIP-0119 DRep metadata, a group profile leaves `authors` out, and tools ignore it if present. The profile's authority comes from the control policy that signed the `create` or `update` that anchors it, not from witnesses inside the document. The JSON-LD context is [`cip-xxxx.jsonld`](./cip-xxxx.jsonld).

A document that cannot be fetched or does not match its hash MUST be marked as such, and its fields MUST NOT be shown as the group's profile.

**Payment addresses.** A listed address is authenticated by the group's control policy, since only that policy can set the profile. Tools MUST accept only bech32 Shelley payment addresses: base addresses (types 0 to 3, 57 bytes) and enterprise addresses (types 6 and 7, 29 bytes), with prefix `addr` and network id 1 on mainnet, and prefix `addr_test` and network id 0 on preprod and preview, which share these values. Tools MUST reject pointer addresses (types 4 and 5), reward addresses, Byron addresses and addresses of another network. `treasuryScript` is compared case-insensitively. `purpose` is free text such as `donations` or `operations`. `treasuryScript` is the hex hash of a native script. When it is given and resolved, and the address's payment credential is a script credential equal to that hash, tools SHOULD show the address as script-controlled together with the script in readable form ("3 of 5: Alice, Bob, ..."). This proves who can spend from the address. It does not prove that these keys belong to the group's admins, so tools mark which of its keys are also admins and show the others as listed only. Tools that set a `treasuryScript` SHOULD put its bytes into key 2 of the same payload. Otherwise tools show the address as declared. A declared address keeps its own spending rules: changing the group's policies or dissolving the group moves no funds. An enterprise address has no stake part, so tools show no vote delegation for it.

#### Website proof

Names confer nothing. Tools MUST show the `group_id` next to the name wherever two groups could be confused.

A group MAY prove a website whose URL uses the `https` scheme. The proof is the JSON file at `<origin>/.well-known/cardano-drep-groups.json`, where `<origin>` is the origin of the profile's `website` in the sense of RFC 6454 (scheme, host and port, without path or query), for example `https://example.org/.well-known/cardano-drep-groups.json`. Its content is an object `{ "<network>": ["<group_id>", ...] }` with the network names `mainnet`, `preprod` and `preview` and group ids in the bech32 form. Other members of the object are ignored. A proof holds when the response status is 200 and the array of the tool's network contains the `group_id` exactly. Redirects are not followed. Tools MAY show such a group as "website verified" and SHOULD check again at least daily.

### Presentation guidance

This section is not normative. It addresses the concentration concern of CPS-0033.

- Show the individual votes and rationales of members first, group pages second.
- Label aggregates as "voting power of affiliated DReps", never as the voting power of the group.
- Distinguish open groups (self-declared affiliation) from permissioned ones (confirmed by the group).
- Show the control and admission policies with their thresholds, and the membership history.
- Membership changes never change delegations.
- Tools that build admissions should offer to update the control policy to the current member set, since an unchanged policy leaves control with the founders.
- Show when a payment address last changed, since a captured control policy could swap it.
- Show where the stake of a treasury address delegates its votes, especially when that is a member.
- Lists of groups may hide groups below a minimum number of active members and should sort by the voting power of their active members. A group and a profile cost only a transaction fee, and a single DRep can join any number of its own groups. Distinct members and member voting power are the signals that are expensive to fake. A list can count each DRep toward one group only, for example its oldest active membership, so listed groups never outnumber distinct member DReps. Membership itself stays non-exclusive.
- Payment addresses of groups without a verified website and without members besides the founders are best not promoted as donation targets.

### Indexer limits

Anyone can post label 8416 for the price of a transaction fee. The limits of 64 events, 8 scripts, 64 script nodes and a nesting depth of 8 bound the work per transaction. A payload that is ignored as a whole changes no state and needs no storage beyond a marker, and a `join` only warrants a registration lookup for a credential that ever was a DRep.

### Versioning

The payload carries a version in key 0. This document defines version 1. A change to the event grammar or to the processing rules needs a new version. Indexers of version 1 ignore payloads of any other version, and a later version defines how its events interact with groups created under version 1. Profile fields can be added without a new version, since tools ignore fields they do not know.

### Test vectors

[`test-vectors.json`](./test-vectors.json) holds named cases. Each case lists transactions in chain order and the expected state: per group its mode, `seq`, policies, profile anchor (URL and hash) and whether it is dissolved, per instance its group, credential, state and close reason, and the valid or invalid verdict of every event. The cases include the decoding limits at and above their bounds. The reason texts in the vectors are informative only.

## Rationale: How does this CIP achieve its goals?

### Transaction metadata, no tokens or contracts

A group is a list of affiliations with clear authorization rules. Metadata events carry it for the price of a fee, without deposits, and every rule can be checked from the transaction itself.

Other designs were considered:

- **Tokens held by members.** A DRep credential has no address, so a token in a wallet is not bound to the DRep and cannot be withdrawn by the group.
- **A field in the DRep's CIP-0119 document.** It is good for discovery but weak as a register: the group cannot confirm it, every change is a DRep update certificate, and the documents can disappear.
- **Plutus state.** It is only needed when contracts must consume membership, which no use case requires today. A later treasury protocol can bind to a `group_id` with its own state.

### Own label

Label 1694 is reserved for JSON-LD governance documents in CIP-0100. This payload is binary CBOR, which is why CIP-0179 surveys also use a label of their own.

### Native scripts and the consent rule

Groups that matter are run by several people, so control is a native script from the first version, and control and admission are separate policies with their own thresholds. A satisfied threshold alone does not show that the other listed keys agreed: a policy like `any [attacker, alice]` would let anyone present a real person as admin. The consent rule makes every listed key sign once when it is added, so a group can only show admins who agreed.

### Exit without permission

`leave` needs only the member's signature and is valid in every group state. A group can lose its keys or change its policies, and a member can still end its affiliation. Removal by the group exists only in permissioned groups, where the group also decides who joins.

### Verdicts from the chain alone

Scripts count only when their bytes were published on chain at or before the event that uses them. A cache could otherwise make one indexer accept an event that another rejects. The signer set includes all vkey witnesses, since the ledger verifies them all, while key-based members must also appear in `required_signers`, so wallets that implement [CIP-0095](../CIP-0095/README.md) show the DRep key to the user before signing. The three decoding layers and the fixed failure effect of each make two independent decoders agree on malformed bytes.

### Staleness

`seq` turns concurrent control changes into a race with one winner, so a group cannot apply two conflicting policy changes that were signed against the same state. Admission events carry no `seq`, so several approval batches can be collected at the same time.

### Group identifier

The identifier follows the pattern of the CIP-0129 governance action id, a transaction hash followed by an index, with its own prefix. The index is two bytes because one transaction can carry up to 64 events, and a fixed length keeps the identifier simple to parse.

### Label and use before this CIP

Label 8416 is registered in [CIP-0010](../CIP-0010/README.md) in a separate pull request ([#1317](https://github.com/cardano-foundation/CIPs/pull/1317)), so the label is reserved while this CIP is in review. It was unused on mainnet, preprod and preview before the reference implementation started. It carries transactions of the reference implementation in the version 1 format, on preprod since November 2026 and on mainnet from the publication of this CIP. If review changes the format, the version field keeps those events readable, and indexers of the new version can process them or ignore them.

### Backward compatibility

This CIP adds a new label and changes nothing in existing standards. Group profiles are CIP-0100 documents and follow the CIP-0119 precedent for `authors`. Profiles published by the reference implementation before this CIP embed their JSON-LD context inline with the namespace of the reference library. Tools read profile fields by their names in `body`, so these profiles and those with the namespace of this CIP are read the same way.

### Open questions

- Whether the `group` prefix should be registered in CIP-0005 together with this CIP.
- Plutus script DReps as members, which would need an authorization path beyond `required_signers` and native scripts.

## Path to Active

### Acceptance Criteria

- [ ] A second indexer, written independently of the reference library, reaches the same groups, instances and verdicts on the test vectors.
- [ ] At least one tool builds and submits group transactions on mainnet.
- [ ] At least one tool displays groups and memberships following this specification on mainnet.

### Implementation Plan

- [x] Reference library: [drep-groups](https://github.com/katomm/cardano-drep-groups) (TypeScript, Apache-2.0, on npm) with the codec, the processing rules, the test vectors and a conformance suite. It is kept separate from DRepTalk on purpose, as a package without ties to any one product, so other governance tools such as wallets, explorers and governance portals can read and build groups by the same rules.
- [x] Reference implementation: DRepTalk creates and manages groups, collects the signatures of several admins and lists groups. End to end tests on preprod cover founding alone and together, joining, admission with a policy update, leaving and dissolving.
- [x] DRepTalk live on [mainnet](https://dreptalk.com/groups/) and [preprod](https://preprod.dreptalk.com/groups/) together with the publication of this CIP. An example group with a full profile, a charter and five members is [Commons Council](https://preprod.dreptalk.com/groups/group1mz6spxh0f5huee8c4krz62tpzwr2g85k78lxqvp7asypkt7vsjqsqqq3f046h/) on preprod.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
