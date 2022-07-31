---
CIP: XXXX
Title: Script language annotated addresses
Authors: Sebastien Guillemot <seba@dcspark.io>
Comments-URI: TBD
Status: Draft
Type: Standards
Created: 2022-07-29
License: CC-BY-4.0
---

# Abstract

Currently, scripts inside addresses are represented simply by their script hash with no indicated of which language was used to generate the script. This is problematic as it means users cannot know whether or not they are sending to a native script (very common use-case that is perfectly fine) or if they are sending to a Plutus script (in which case they may be accidentally locking their funds forever)

This proposal aims to solve tackle this issue by introducing a new address format that asserts the type of script held in its hash

# Motivation

Currently native scripts in Cardano are commonly used for multisig. Other proposals exist such as the [Arbitrary Script as Native Script spending conditions CIP](https://github.com/cardano-foundation/CIPs/pull/309) that enable native scripts to cover a larger set of use-cases as well. However, these multisig and proxy script users have trouble getting users to actually send ADA to them from their wallet. The reason why is that all wallets currently show a warning to the user if they are sending to a script address as there is no easy way for the wallet software to know whether or not a script is a native script or a native script

Additionally, this is not a problem that can easily be solved with better indexing tools for Cardano. This is because in the proxy native script contract use-case, it's possible that the proxy contract is unique for each individual user (some parameterized Plutus contract is calculated and then added as the requirement of the native script). Therefore, this feature benefits from being supported at the address level.

Lastly, the fact that addresses contain just their script hash without information about which language they use also leads to complexity in ledger rules and code of SDKs for Cardano as they cannot process any script language specific behavior until after the scripts are later provided as part of the witness. Knowing the language ahead of time allows the ledger to protect users from mistakes such as creating a Plutus V1 utxo entry with inline datum (which effectively makes it unspendable)

# Specification

All addresses in Cardano currently start with a header that indicates which address type they are. Notably, these can be seen in [CIP19](../CIP-0019/README.md).

Note there are two ways we can support our modification to the address type:

1) Reserve a new address type as part of the header nibble. This is not great because it means we have to reserve many new address types (a new alternative for every case where the old address format contains a script hash)
2) Add a new column to existing address types that contain scripts. This doesn't work for pointer addresses because they are variable-width so it isn't possible to differentiate between the original address format and this annotated format (note that pointer addresses are almost never used on chain, so this is an acceptable limitation). This does, however, limit the kinds of modifications we could make to these address types in the future as we would need to make sure the length continues to uniquely identify the content.

In this CIP, we propose using option (2) and extend the CIP19 table as follows:

Header type (`t t t t . . . .`) | script namespace* | Payment Part     | script namespace* | Delegation Part
---                             | ---               | ---              | ---               |---
(0) `0000....`                  | ø                 | `PaymentKeyHash` | ø                 | `StakeKeyHash`
(1) `0001....`                  | 0-255             | `ScriptHash`     | ø                 | `StakeKeyHash`
(2) `0010....`                  | ø                 | `PaymentKeyHash` | 0-255             | `ScriptHash`
(3) `0011....`                  | 0-255             | `ScriptHash`     | 0-255             | `ScriptHash`
(6) `0110....`                  | ø                 | `PaymentKeyHash` | ø                 | ø
(7) `0111....`                  | 0-255             | `ScriptHash`     | ø                 | ø

**script namespace* is defined to be the key used to identify the script kind in the `script` of the [binary spec](https://github.com/input-output-hk/cardano-ledger/blob/master/eras/babbage/test-suite/cddl-files/babbage.cddl#L421). Note that this is the same namespace used to generate a script hash from script bytes.

# Asserted language and script language mismatch

Note that nothing stops somebody from creating a mal-constructed address where the language asserted inside the address does not match the actual language used for the script hash.

This is an unlikely error since addresses are provided to the users by dApps. Additionally, even if due to an error the wrong address is used, funds are not permanently lost because the spending condition is still controlled by the script hash -- meaning they can still be spent and additionally can be considered 

# On-chain vs off-chain encoding

There are two different ways this CIP can be implemented:

1. Purely as a wallet standard and, at the ledger rules level, the address format stays the same as before
2. Adding support for this new encoding in the ledger rules

The advantage of (1) is that it means this feature can be implemented without a hard fork. However, the disadvantage is that tools that parse chain history (wallets tx history on wallet restore, explorers, etc.) would not be able to show this new encoding for addresses potentially leading to user confusion (same address appearing in different formats at different places)

Therefore, although projects can implement this CIP before it is implemented on-chain, we still recommend adding support for this address encoding at the protocol level.

# Language vs script namespace

Care has to be taken when using the word `language` in Cardano. This is because strictly speaking, `language` is defined in the binary spec as any script type that has a cost model associated with it (i.e. PlutusV1 & PlutusV2. Does not include native scripts)

Since we explicitly want our CIP to be usable for native scripts, we instead use *script namespace* as defined above.