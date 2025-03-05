---
CIP: 80
Title: Transaction Serialization Deprecation Cycle
Status: Active
Category: Ledger
Authors:
  - Jared Corduan <jared.corduan@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/372
Created: 2022-11-09
License: CC-BY-4.0
---

## Abstract

This CIP specifies a policy for the backwards compatibility of the serialization scheme of
Cardano transactions.

## Motivation: why is this CIP necessary?

Transactions on Cardano are sent on the wire using CBOR and are specified with CDDL.
The first scheme was introduced with the Byron phase.
This scheme was changed dramatically with the introduction of the Shelley phase.
As of the time of the writing of this CIP, however, every new scheme has been backwards
compatible with the original scheme from the Shelley phase.
The intention is still to maintain backwards compatibility to the extent reasonable,
and to make explicit our policy for breaking backwards compatibility when deemed necessary.

## Specification

Problems with serialization fall into two categories:
* flaws in the implementation
* flaws is the CDDL specification

Note that at the time of the writing of this CIP, there is only one implementation of the Cardano
node, and we do not yet need to consider inconsistencies between different implementations.

The policy for maintaining backwards compatibility with the transaction serialization will be
as follows.

### Serious Flaws

A **serious flaw** in the serialization is an issue which could have a large and negative impact
on the network, and which requires a hard fork to fix.
These will almost always be problems with the serialization and not the specification.
It is up to human discretion to determine what constitutes a serious flaw,
mostly likely by the core developers.

Backwards compatibility can be abandoned in the case of a serious flaw,
and **the fix will occur at the next available hard fork**.

### Non-Serious Flaws

A **non-serious flaw** in the serialization is an issue which is not safety critical,
but is problematic enough to merit breaking backwards compatibility.
This is again a human judgment.

Backwards compatibility can be abandoned in the case of a non-serious flaw,
but there must be a deprecation cycle:
* In the case of a **soft fork** (meaning that the change is backwards incompatible for
  block producers but *not* block validators),
  a new format can be introduced at the next major or minor protocol version,
  at which time the old format can be abandoned.
* In the case of a **hard fork** (meaning that the change is backwards incompatible for
  both block producers and block validators),
  a new format can be introduced at the next major protocol version,
  but the old format must be supported for at least **six months**.
  After six months, the old format can be abandoned at the next possible fork.

#### Examples

A good example of a non-serious flaw is the CDDL specification of the transaction output in the
Alonzo ledger era:

```
alonzo_transaction_output = [ address, amount : value, ? datum_hash : $hash32 ]
```

There is nothing inherently wrong with this scheme, but it caused a problem in the Babbage ledger
era with the addition of inline datums and script references.
In particular, there were two new optional fields, and there was mutual exclusivity.
In order to maintain backwards compatibility, Babbage introduced this scheme:

```
transaction_output = alonzo_transaction_output / babbage_transaction_output

babbage_transaction_output =
  {   0 : address
  ,   1 : value
  , ? 2 : [ 0, $hash32 // 1, data ]
  , ? 3 : script_ref
  }
```

In other words, a new format was created, but the legacy format was still supported.
The new format, `babbage_transaction_output`, was introduced 2022-09-22 with the Vasil hard fork,
The old format, `alonzo_transaction_output`, can be retired after 2023-03-22.

Note that this example required a **hard fork**.

A good example of a non-serious flaw requiring a **soft fork** is the removal
of zero-valued multi-assets in the mint field of the transaction body.

In the Babbage ledger era, a multi-asset value was defined as:

```
value = coin / [coin,multiasset<uint>]
```

Zero values can be confusing inside of things like explorers, so in the Conway era they are removed:

```
natNum = 1 .. 4294967295
value = coin / [coin,multiasset<natNum>]
```

Notice that block validators will not notice this change, though block producers will notice it.

### Summary

* We should strive to maintain backwards compatibility.
* Serious flaws can be fixed immediately (at the next hard fork), and can break backwards
  compatibility.
* Non-Serious flaws can be fixed (at the next hard fork), but the old format
  must be supported for at least six months with support ending at the next hard fork event after
  the six months have passed.

## Rationale: how does this CIP achieve its goals?

It seems clear that security issues merit breaking backwards compatibility and should be fixed
as soon as possible.
The six month compatibility window for non-serious flaws is mostly
arbitrary, but we need to allow enough time for people to migrate.
It would be great to have more explicit definitions for "serious" and "non-serious" flaws,
but this seems very difficult.

## Path to Active

### Acceptance criteria

- [x] The proposal is accepted and recognized by the ledger team.

### Implementation plan

N/A

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
