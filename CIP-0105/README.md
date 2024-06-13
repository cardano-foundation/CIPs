---
CIP: 105
Title: Conway era Key Chains for HD Wallets
Status: Proposed
Category: Wallets
Authors:
  - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/597
Created: 2023-09-22
License: CC-BY-4.0
---

## Abstract

The Conway Ledger era introduces many new features to Cardano, notably features to support community governance via CIP-1694.
This includes the introduction of the new first class credentials; `drep_credential`, `committee_cold_credential` and `committee_hot_credential`.

We propose a HD wallet key derivation paths for registered DReps and constitutional committee members to deterministically derive keys from which credentials can be generated.
Such keys are to be known as DRep keys, constitutional committee cold keys and constitutional committee hot keys.
Here we define some accompanying tooling standards.

> **Note** this proposal assumes knowledge of the Conway ledger design (see
> [draft ledger specification](https://github.com/IntersectMBO/cardano-ledger/blob/d2d37f706b93ae9c63bff0ff3825d349d0bd15df/eras/conway/impl/cddl-files/conway.cddl))
> and
> [CIP-1694](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md).

## Motivation: why is this CIP necessary?

In the Conway ledger era, DRep credentials allow registered DReps to be identified on-chain, in DRep registrations, retirements, votes, and in vote delegations from ada holders.
Whilst constitutional committee members can be recognized by their cold credentials within update committee governance actions, authorize hot credential certificate and resign cold key certificates.
Constitutional committee hot credential can be observed within the authorize hot key certificate and votes.

CIP-1694 terms these DRep credentials as DRep IDs, which are either generated from blake2b-224 hash digests of Ed25519 public keys owned by the DRep, or are script hash-based.
Similarly, both the hot and cold credentials for constitutional committee members can be generated from public key digests or script hashes.

This CIP defines a standard way for wallets to derive DRep and constitutional committee keys.

Since it is best practice to use a single cryptographic key for a single purpose, we opt to keep DRep and committee keys separate from other keys in Cardano.

By adding three paths to the [CIP-1852 | HD (Hierarchy for Deterministic) Wallets for Cardano](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852/README.md), we create an ecosystem standard for wallets to be able to derive DRep and constitutional committee keys.
This enables DRep and constitutional committee credential restorability from a wallet seed phrase.

Stakeholders for this proposal are wallets that follow the CIP-1852 standard and tool makers wishing to support DReps and or constitutional committee members.
This standard allows DReps and constitutional committee members to use alternative wallets whilst being able to be correctly identified.
By defining tooling standards, we enable greater interoperability between governance-focussed tools.

## Specification

### Derivation

#### DRep Keys

Here we describe DRep key derivation as it pertains to Cardano wallets that follow the CIP-1852 standard.

To differentiate DRep keys from other Cardano keys, we define a new `role` index of `3`:

`m / 1852' / 1815' / account' / 3 / address_index`

We strongly recommend that a maximum of one set of DRep keys should be associated with one wallet account, which can be achieved by setting `address_index=0`.

#### DRep ID

Tools and wallets can generate a DRep ID (`drep_credential`) from the Ed25519 public DRep key (without chaincode) by creating a blake2b-224 hash digest of the key.
As this is key-based credential it should be marked as entry `0` in a credential array.

#### Constitutional Committee Cold Keys

Here we describe constitutional committee cold key derivation as it pertains to Cardano wallets that follow the CIP-1852 standard.

To differentiate constitutional committee cold keys from other Cardano keys, we define a new `role` index of `4`:

`m / 1852' / 1815' / account' / 4 / address_index`

We strongly recommend that a maximum of one set of constitutional committee cold keys should be associated with one wallet account, which can be achieved by setting `address_index=0`.

#### Constitutional Committee Cold Credential

Tools and wallets can generate a constitutional committee cold credential (`committee_cold_credential`) from the Ed25519 public constitutional committee cold key (without chaincode) by creating a blake2b-224 hash digest of the key.
As this is key-based credential it should be marked as entry `0` in a credential array.

#### Constitutional Committee Hot Keys

Here we describe constitutional committee hot key derivation as it pertains to Cardano wallets that follow the CIP-1852 standard.

To differentiate constitutional committee hot keys from other Cardano keys, we define a new `role` index of `5`:

`m / 1852' / 1815' / account' / 5 / address_index`

We strongly recommend that a maximum of one set of constitutional committee hot keys should be associated with one wallet account, which can be achieved by setting `address_index=0`.

#### Constitutional Committee Hot Credential

Tools and wallets can generate a constitutional committee hot credential (`committee_hot_credential`) from the Ed25519 public constitutional committee hot key (without chaincode) by creating a blake2b-224 hash digest of the key.
As this is key-based credential it should be marked as entry `0` in a credential array.

### Bech32 Encoding

These are also described in [CIP-0005 | Common Bech32 Prefixes](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0005/README.md), but we include them here for completeness.

> **Note** we also include the prefixes for script-based credentials in the following subsections, for completeness.

#### DRep Keys

DRep keys and DRep IDs should be encoded in Bech32 with the following prefixes:

| Prefix        | Meaning                                                 | Contents                                                          |
| ------------- | --------------------------------------------------------| ----------------------------------------------------------------- |
| `drep_sk`     | CIP-1852’s DRep signing key                             | Ed25519 private key                                               |
| `drep_vk`     | CIP-1852’s DRep verification key                        | Ed25519 public key                                                |
| `drep_xsk`    | CIP-1852’s DRep extended signing key                    | Ed25519-bip32 extended private key                                |
| `drep_xvk`    | CIP-1852’s DRep extended verification key               | Ed25519 public key with chain code                                |
| `drep`        | Delegate representative verification key hash (DRep ID) | blake2b\_224 digest of a delegate representative verification key |
| `drep_script` | Delegate representative script hash (DRep ID)        | blake2b\_224 digest of a serialized delegate representative script |

#### Constitutional Committee Cold Keys

Constitutional cold keys and credential should be encoded in Bech32 with the following prefixes:

| Prefix           | Meaning                                                               | Contents                                                               |
| ---------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------  |
| `cc_cold_sk`     | CIP-1852’s constitutional committee cold signing key                  | Ed25519 private key                                                    |
| `cc_cold_vk`     | CIP-1852’s constitutional committee verification signing key          | Ed25519 private key                                                    |
| `cc_cold_xsk`    | CIP-1852’s constitutional committee cold extended signing key         | Ed25519-bip32 extended private key                                     |
| `cc_cold_xvk`    | CIP-1852’s constitutional committee extended verification signing key | Ed25519 public key with chain code                                     |
| `cc_cold`        | Constitutional committee cold verification key hash (cold credential) | blake2b\_224 digest of a consitutional committee cold verification key |
| `cc_cold_script` | Constitutional committee cold script hash (cold credential)           | blake2b\_224 digest of a serialized constitutional committee cold script |

#### Constitutional Committee Hot Keys

Constitutional hot keys and credential should be encoded in Bech32 with the following prefixes:

| Prefix          | Meaning                                                               | Contents                                                              |
| --------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `cc_hot_sk`     | CIP-1852’s constitutional committee hot signing key                   | Ed25519 private key                                                   |
| `cc_hot_vk`     | CIP-1852’s constitutional committee verification signing key          | Ed25519 private key                                                   |
| `cc_hot_xsk`    | CIP-1852’s constitutional committee hot extended signing key          | Ed25519-bip32 extended private key                                    |
| `cc_hot_xvk`    | CIP-1852’s constitutional committee extended verification signing key | Ed25519 public key with chain code                                    |
| `cc_hot`        | Constitutional committee hot verification key hash (hot credential)   | blake2b\_224 digest of a consitutional committee hot verification key |
| `cc_hot_script` | Constitutional committee hot script hash (hot credential)             | blake2b\_224 digest of a serialized constitutional committee hot script |

### Tooling Definitions

### DRep Keys

Supporting tooling should clearly label these key pairs as "DRep Keys".

Examples of acceptable `keyType`s for supporting tools:

| `keyType`                                   | Description                                       |
| ------------------------------------------- | ------------------------------------------------- |
| `DRepSigningKey_ed25519`                    | Delegate Representative Signing Key               |
| `DRepExtendedSigningKey_ed25519_bip32`      | Delegate Representative Extended Signing Key      |
| `DRepVerificationKey_ed25519`               | Delegate Representative Verification Key          |
| `DRepExtendedVerificationKey_ed25519_bip32` | Delegate Representative Extended Verification Key |

For hardware implementations:

| `keyType`                     | Description                                       |
| ----------------------------- | ------------------------------------------------- |
| `DRepHWSigningFile_ed25519`   | Hardware Delegate Representative Signing File     |
| `DRepVerificationKey_ed25519` | Hardware Delegate Representative Verification Key |

#### Constitutional Committee Cold Keys

Supporting tooling should clearly label these key pairs as "Constitutional Committee Cold Keys".

Examples of acceptable `keyType`s for supporting tools:

| `keyType`                                                          | Description                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------- |
| `ConstitutionalCommitteeColdSigningKey_ed25519`                    | Constitutional Committee Cold Signing Key               |
| `ConstitutionalCommitteeColdExtendedSigningKey_ed25519_bip32`      | Constitutional Committee Cold Extended Signing Key      |
| `ConstitutionalCommitteeColdVerificationKey_ed25519`               | Constitutional Committee Cold Verification Key          |
| `ConstitutionalCommitteeColdExtendedVerificationKey_ed25519_bip32` | Constitutional Committee Cold Extended Verification Key |

For hardware implementations:

| `keyType`                                            | Description                                             |
| ---------------------------------------------------- | ------------------------------------------------------- |
| `ConstitutionalCommitteeColdHWSigningFile_ed25519`   | Hardware Constitutional Committee Cold Signing File     |
| `ConstitutionalCommitteeColdVerificationKey_ed25519` | Hardware Constitutional Committee Cold Verification Key |

#### Constitutional Committee Hot Keys

Supporting tooling should clearly label these key pairs as "Constitutional Committee Hot Keys".

| `keyType`                                                         | Description                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------ |
| `ConstitutionalCommitteeHotSigningKey_ed25519`                    | Constitutional Committee Hot Signing Key               |
| `ConstitutionalCommitteeHotExtendedSigningKey_ed25519_bip32`      | Constitutional Committee Hot Extended Signing Key      |
| `ConstitutionalCommitteeHotVerificationKey_ed25519`               | Constitutional Committee Hot Verification Key          |
| `ConstitutionalCommitteeHotExtendedVerificationKey_ed25519_bip32` | Constitutional Committee Hot Extended Verification Key |

For hardware implementations:

| `keyType`                                           | Description                                            |
| --------------------------------------------------- | ------------------------------------------------------ |
| `ConstitutionalCommitteeHotHWSigningFile_ed25519`   | Hardware Constitutional Committee Hot Signing File     |
| `ConstitutionalCommitteeHotVerificationKey_ed25519` | Hardware Constitutional Committee Hot Verification Key |

### Versioning

This CIP is not to be versioned using a traditional scheme, rather if any large technical changes are required then a new proposal must replace this one.
Small changes can be made if they are completely backwards compatible with implementations, but this should be avoided.

## Rationale: how does this CIP achieve its goals?

### Derivation

By standardizing derivation, naming, and tooling conventions we primarily aim to enable wallet interoperability.
By having a standard to generate DRep and constitutional committee credentials from mnemonics, we allow wallets to always be able to discover a user’s governance activities.

#### Why add a new roles to the 1852 path?

This approach mirrors how stake keys were rolled out, see [CIP-0011 | Staking key chain for HD wallets](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0011/README.md).
We deem this necessary since these credentials sit alongside each other in the Conway ledger design.

The alternative would be to define a completely different derivation paths, using a different index in the purpose field, similar to the specification outlined within [CIP-0036](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0036/README.md#derivation-path), but this could introduce complications with HW wallet implementations.

#### Why not multi-DRep/CC wallet accounts?

We believe the overhead that would be introduced by multi-DRep accounts or multi-constitutional-committee is an unjustified expense.
Future iterations of this specification may expand on this, but at present this is seen as unnecessary.
This avoids the need for DRep, cc hot or cc cold key discovery.

We model this on how stake keys are generally handled by wallets.
If required, another CIP could, of course, introduce a multi-DRep/CC method.

### Encoding

#### Why not allow network tags?

For simplicity, we have omitted network tags within the encoding.
This is because we have modeled DRep IDs and CC credentials on stake pool operator IDs, which similarly do not include a network tag.

The advantage of including a network tag would be to reduce the likelihood of mislabelling a DRep’s network of operation (eg Preview v Cardano mainnet).

### Test vectors

Scripts were constructed according to the following script templates:

`script_1: all [keyhash, active_from 5001]`
`script_2: any [keyhash, all [active_from 5001, active_until 6001]]`

where

`keyhash: {drep | cc_cold | cc_hot}`

#### Test vector 1
`mnemonic: test walk nut penalty hip pave soap entry language right filter choice`
`accountIx: 0x80000000`
```
drep_xsk: drep_xsk14rjh4rs2dzm6k5xxe5f73cypzuv02pknfl9xwnsjws8a7ulp530xztarpdlyh05csw2cmnekths7dstq0se3wtza84m4fueffezsjfgassgs9xtfzgehrn0fn7c82uc0rkj06s0w0t80hflzz8cwyry3eg9066uj
drep_sk:
drep_xvk: drep_xvk17axh4sc9zwkpsft3tlgpjemfwc0u5mnld80r85zw7zdqcst6w543mpq3q2vkjy3nw8x7n8asw4es78dyl4q7u7kwlwn7yy0sugxfrjs6z25qe
drep_vk: drep_vk17axh4sc9zwkpsft3tlgpjemfwc0u5mnld80r85zw7zdqcst6w54sdv4a4e
drep: drep15k6929drl7xt0spvudgcxndryn4kmlzpk4meed0xhqe25nle07s
drep_script_1: drep_script16pjhzfkm7rqntfezfkgu5p50t0mkntmdruwlp089zu8v29l95rg
drep_script_2: drep_script14edv7pg3y4wkglyykvvy5t2j906ld3dhdwvf7jda8qaa63d5kf4

cc_cold_xsk: cc_cold_xsk1dp84kjq9qa647wr70e2yedzt8e27kwugh8mfw675re0hgm8p530z3d9230cjjzyyzlq04hn94x9q2m9um2tvp2y8fn7tau9l2wfj5ykxqxtgua0lxpf0lfn44md2afyl7dktyvpkmug9u28p6v452flxeuca0v7w
cc_cold_sk:
cc_cold_xvk: cc_cold_xvk149up407pvp9p36lldlp4qckqqzn6vm7u5yerwy8d8rqalse3t04vvqvk3e6l7vzjl7n8ttk646jflumvkgcrdhcstc5wr5etg5n7dnc8nqv5d
cc_cold_vk: cc_cold_vk149up407pvp9p36lldlp4qckqqzn6vm7u5yerwy8d8rqalse3t04q7qsvwl
cc_cold: cc_cold1lmaet9hdvu9d9jvh34u0un4ndw3yewaq5ch6fnwsctw02xxwylj
cc_cold_script_1: cc_cold_script14ehj5f64f40xju0086fnunctulkh46mq7munm7upe4hpcwpcatv
cc_cold_script_2: cc_cold_script1zxwzpnk0ah7m5ptjjtmkhvgs4736k3e0ns66shd0fy33vdauq3j

cc_hot_xsk: cc_hot_xsk1mpt30ys7v2ykqms4c83wuednh4hvy3lr27yfhgtp0rhdka8p5300j4d2z77sq2t3kp082qzgkanwkm05mp2u2nwja3ad3pgw9l34a0j5sl5yd6d8pze8dqwksd069kkfdqggk0yytcmet96fre45w64qkgyxl0dt
cc_hot_sk:
cc_hot_xvk: cc_hot_xvk10y48lq72hypxraew74lwjjn9e2dscuwphckglh2nrrpkgweqk5h4fplggm56wz9jw6qadq6l5tdvj6qs3v7ggh3hjkt5j8ntga42pvs5rvh0a
cc_hot_vk: cc_hot_vk10y48lq72hypxraew74lwjjn9e2dscuwphckglh2nrrpkgweqk5hschnzv5
cc_hot: cc_hot17mffcrm3vnfhvyxt7ea3y65e804jfgrk6pjn78aqd9vg7xpq8dv
cc_hot_script_1: cc_hot_script16fayy2wf9myfvxmtl5e2suuqmnhy5zx80vxkezen7xqwskncf40
cc_hot_script_2: cc_hot_script1vts8nrrsxmlntp3v7sh5u7k6qmmlkkmyv5uspq4xjxlpg6u229p
```

#### Test vector 2
`mnemonic: test walk nut penalty hip pave soap entry language right filter choice`
`accountIx: 0x80000100`
```
drep_xsk: drep_xsk1zracgd4mqt32f5cj0ps0wudf78u6lumz7gprgm3j8zec5ahp530weq4z9ayj6jzj33lpj86jkk2gnt0ns0d5sywteexxehvva7gugz99ydmpemzpsfnj49vjvw88q9a2s2hxc9ggxal5q6xsqz5vaat2xqsha72w
drep_sk:
drep_xvk: drep_xvk1wq6ylcpjnwavhveey855tkhdrqdav6yfxvltw0emky9d3erxn9m22gmkrnkyrqn8922eycuwwqt64q4wds2ssdmlgp5dqq9gem6k5vq23ph3c
drep_vk: drep_vk1wq6ylcpjnwavhveey855tkhdrqdav6yfxvltw0emky9d3erxn9mqdrlerg
drep: drep1rmf3ftma8lu0e5eqculttpfy6a6v5wrn8msqa09gr0tr5rgcuy9
drep_script_1: drep_script18cgl8kdnjculhww4n3h0a3ahc85ahjcsg53u0f93jnz9c0339av
drep_script_2: drep_script1hwj9yuvzxc623w5lmwvp44md7qkdywz2fcd583qmyu62jvjnz69

cc_cold_xsk: cc_cold_xsk1dppxrjspxrjj5e5xrmh6yaw6w30arsl5lqcsp09ynyzwwulp530q4tlvug79xx6ja3u32fu9jyy84p6erjmza6twrackm9kfsdpc3ap7uxpempqjftx74qwxnmn7d6pg8pl9zpnc0rese26pfmzl9cmtgg8xsxvu
cc_cold_sk:
cc_cold_xvk: cc_cold_xvk1e2mquwugpwnykfftjs4mv3w4uk80f4hjgd2zls5vusz3zuqhr7gnacvrnkzpyjkda2qud8h8um5zswr72yr8s78npj45znk97t3kkssryhkyv
cc_cold_vk: cc_cold_vk1e2mquwugpwnykfftjs4mv3w4uk80f4hjgd2zls5vusz3zuqhr7gs3qg4hr
cc_cold: cc_cold1aymnf7h8rr53h069ephcekq707tg0ek0lexfzrw35npkq02wke0
cc_cold_script_1: cc_cold_script1prtcxdlu75dz48lf8hh86gt8ng7z39yvmyqcg92sgze7g6m8dtq
cc_cold_script_2: cc_cold_script1969h0m92nuqrj7x74pj3tnhxh97lfhl4y2vwvqvc6kecwdshr6f

cc_hot_xsk: cc_hot_xsk15pt89wppyhr9eqgm5nnu7tna3dfmqxa2u45e4g7krzp9u78p530pez36k8k9n0gw08hn6drxlwxxsgc4jsejv6hvcnkd7gd3zxhstpe3vzde6e98zql6n2cmekklm63dydnt80szdr0h768dexeklrfspc5lznuz
cc_hot_sk:
cc_hot_xvk: cc_hot_xvk10qawpxlz7eytt9yr4xlwtjkw345v0ehzsxdlkks6qralyp975phrzcymn4j2wypl4x43hnddlh4z6gmxkwlqy6xl0a5wmjdnd7xnqrsvak8ry
cc_hot_vk: cc_hot_vk10qawpxlz7eytt9yr4xlwtjkw345v0ehzsxdlkks6qralyp975phqx538xn
cc_hot: cc_hot1682whkcedz0ftcyhjxdasufyg85fks0vxm0y006qx38c2jz0ae0
cc_hot_script_1: cc_hot_script1hheftszv4jw83f5megrvhrevl7lwwmtnjav7srkqngr92gna52t
cc_hot_script_2: cc_hot_script1dg9jdwlsxzakctywv2cw7a7ggj2dwu0gz5tueu2rf40zvkj8dwc
```

#### Test vector 3
`mnemonic: excess behave track soul table wear ocean cash stay nature item turtle palm soccer lunch horror start stumble month panic right must lock dress`
`accountIx: 0x80000000`
```
drep_xsk: drep_xsk17pwn6d7pu0d6sfzysyk5taux99f5tdqsct7zzthgljyd5zs33azej0tm5ny7ksunthqu84tqg832md6vs3hm392agwx3auhvyjtzxr2l6c0dj47k6zedl4kgugneu04j64fc5uueayydmufdrdaled9k4qllaka6
drep_sk:
drep_xvk: drep_xvk15j30gk0uex88lc9vh6sfda93lv6zede65mzp7ck56m9pgeqhnht9l4s7m9tad59jmltv3c38nclt942n3feen6ggmhcj6xmmlj6td2qu4ce82
drep_vk: drep_vk15j30gk0uex88lc9vh6sfda93lv6zede65mzp7ck56m9pgeqhnhtqvs6j8t
drep: drep1x0jc06clgnj37sc8amkhahnpjqytcnguxtqcpxwkxeejj4y6sqm
drep_script_1: drep_script17fql6ztxyk63taryk2e4mh47jw3wdchv9e7u4jxg4edrx89ym9g
drep_script_2: drep_script10qp23w0gppuvc7chc3g7saudlmhj9jmm9ssrrzzm3qwksv3gsq7

cc_cold_xsk: cc_cold_xsk1hqtevrzlhtcglwvt5pmgct8ssqx37vjjf3wuydpd6flyqrg33azacap5w5mclacmuycx3xgrtstxgrpzcncf6l840t0klmywc69ryd9zf95taaaseka98yakuj2048slnuekw22qm58majt8alhs438eecehquu0
cc_cold_sk:
cc_cold_xvk: cc_cold_xvk13wc4cvvr266t4rxm9wyel4deeqxyylvjzjdk5w74lva2xm0dhxt6yjtghmmmpnd62wfmdey5l20pl8envu55phg0hmyk0ml0ptz0nns9cqjlk
cc_cold_vk: cc_cold_vk13wc4cvvr266t4rxm9wyel4deeqxyylvjzjdk5w74lva2xm0dhxtsfpa2qu
cc_cold: cc_cold17z4s83htmrgmg5268hx68j4vqumk38wrc5x9cr0mc7glyntw6cl
cc_cold_script_1: cc_cold_script15z7ynn7fuqu55hh850962vrrg7tcdncl8spnjtrxjjm06y3avt9
cc_cold_script_2: cc_cold_script1ahw3qh3ledhxp0frga9aawfkxpu0qstte9nmem0phqqegeeg6zv

cc_hot_xsk: cc_hot_xsk1wzamzchtj7m79mjfpg3c02m534ugej5ac0p3s2sresr7vys33azktmjva6flctprqu6m4k4w459x9qkfsz2ahgy5ganjn23djhhkg5e5eyhu7fjxl6tpxtmzh7e2ftuj4qgmawsmcl7sqesn8e0pmh97zs3c3fqj
cc_hot_sk:
cc_hot_xvk: cc_hot_xvk1tazd6lvnf2c9j8m58h6xy56uuyhkee526jgxj2ylaextl0xamd4nfjf0eunydl5kzvhk90aj5jhe92q3h6aph3laqpnpx0j7rhwtu9qe7dhsc
cc_hot_vk: cc_hot_vk1tazd6lvnf2c9j8m58h6xy56uuyhkee526jgxj2ylaextl0xamd4swmuygc
cc_hot: cc_hot1c2n5ax72vfqdj3ljn04hmmvkqjt5q9k694yw8f7rv3xvgxas90x
cc_hot_script_1: cc_hot_script1tmwlec0twwvl29h6pgvew5mf4recsxtktev9g07xm37fv46mta9
cc_hot_script_2: cc_hot_script1c77thg5lrahy0he4q6glsk8vgsp45gt75k3pq09d02u8g4s30yx
```

#### Test vector 4
`mnemonic: excess behave track soul table wear ocean cash stay nature item turtle palm soccer lunch horror start stumble month panic right must lock dress`
`accountIx: 0x80000100`
```
drep_xsk: drep_xsk14z6a7nd2q5r03s4gxsrujc59sg757vqqcwxeuc5s874c2rq33az37lwkxpxvh5s4a94sncxp6y7m73pxsuknt7gvethhue5jk5vc5n2hrg95mynhw7mtrshxr5mpku4v8x6lpm05nznrqej70u0fllgfkusexdkv
drep_sk:
drep_xvk: drep_xvk14dwjrplj73qeggdsg4lh4j9tp495asyq9t6augwaue8kqvjg5wq4wxstfkf8waakk8pwv8fkrde2cwd47rklfx9xxpn9ulc7nl7sndcvdjh2m
drep_vk: drep_vk14dwjrplj73qeggdsg4lh4j9tp495asyq9t6augwaue8kqvjg5wqskrq5yn
drep: drep1cx359uxlhq4e8j3wddqxht9sfqp004t2n8v0jk5q4zmv27sh0h5
drep_script_1: drep_script1ckr4x9293myuyz5379wndh4ag00c787htnzwzxxmpfnfzjzk4cq
drep_script_2: drep_script1wgly5zd539aam7yxr7trxy48dhupswmwusutm4q40dwkcquwecx

cc_cold_xsk: cc_cold_xsk1hqe5kcsq59mx4t9nxrctmth0ppz9gda0gnppyll3h9rxcyq33az4uy3u6qhzuhjsstzca9awgsx27j07hxhrkrk6487nvywp0ag669m4v6lj3knq7e6pxaujy98akn5exhgk44ftruepkte0hdm74dd8zceqnk2h
cc_cold_sk:
cc_cold_xvk: cc_cold_xvk1lmqejccjpxsd9cl4uavxj0jryjlfk5r8wemr0d8saal49lttp2482e4l9rdxpan5zdmeyg20md8fjdw3dt2jk8ejrvhjlwmha266w9syf55nr
cc_cold_vk: cc_cold_vk1lmqejccjpxsd9cl4uavxj0jryjlfk5r8wemr0d8saal49lttp24q6lw08l
cc_cold: cc_cold1fjej4ec9lvam509vjapr26yqeyf2x6j20n98f4y4d3l5zygwxt4
cc_cold_script_1: cc_cold_script1qlk7rgkd5n6ga8enwk08vwtmlklhzfnmjtjlzlwed62tuycmmh5
cc_cold_script_2: cc_cold_script1a4qmd5d3dqppxtq5wcuuaa3xfe868vyn46afvktz5ucxzxvflg4

cc_hot_xsk: cc_hot_xsk14rzh5lvtdhvum6vjfvkwp73mz9gl426cj04xfavnjgmdxrq33azugz0k9sekf2eg70lr34rg5aclr54v30za77xn945kncdm0le6lutxlr5ar355u5awqt2hkmdurv4qv64cmpg39zq2ahjxqken8vk62qunx4hl
cc_hot_sk:
cc_hot_xvk: cc_hot_xvk1g2925ntunmthw66sr8t7v3qe7fls4575wput3936cguzk7m6w4fkd78f68rffef6uqk40dkmcxe2qe4t3kz3z2yq4m0yvpdnxwed55q798msd
cc_hot_vk: cc_hot_vk1g2925ntunmthw66sr8t7v3qe7fls4575wput3936cguzk7m6w4fs0zjxf8
cc_hot: cc_hot14845f592rnj4txmuygns4s3aresm7ts3fhvwtfzw6wjjj3l0520
cc_hot_script_1: cc_hot_script1n42mr24e22eyspa7m0y6lq5rk8tesq35xt6gfgkezcxluqysk4n
cc_hot_script_2: cc_hot_script1gfqmx4g0czk2nz2m2rfawg4me283jl7wz4wfssup03av2yzf2kd
```


## Path to Active

### Acceptance Criteria

- [x] The DRep derivation path is used by three wallet/tooling implementations.
  - [Nufi](https://assets.nu.fi/extension/sanchonet/nufi-cwe-sanchonet-latest.zip)
  - [Lace](https://chromewebstore.google.com/detail/lace-sanchonet/djcdfchkaijggdjokfomholkalbffgil?hl=en)
  - [Yoroi](https://chrome.google.com/webstore/detail/yoroi-nightly/poonlenmfdfbjfeeballhiibknlknepo/related)
  - [demos wallet](https://github.com/Ryun1/cip95-demos-wallet)
- [ ] The consitutional committee derivation paths are used by two implementations.

### Implementation Plan

- [ ] Author to provide an example implementation inside a HD wallet.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
