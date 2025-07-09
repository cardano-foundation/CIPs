## Test vector 1

Twelve word mnemonic, with account index of zero.

**Mnemonic:** `test walk nut penalty hip pave soap entry language right filter choice`

**Account index:** `0x80000000`

#### Scripts

Scripts were constructed according to the following native script templates:

**Script 1:** `all [$vKeyhash, active_from 5001]`

**Script 2:** `any [$vKeyhash, all [active_from 5001, active_until 6001]]`

Where `$vKeyhash` is the Verification key hash aka `{drep_vkh1... | cc_cold_vkh1... | cc_hot_vkh1...}`.

### DRep Keys

#### DRep signing key

Hex: `a8e57a8e0a68b7ab50c6cd13e8e0811718f506d34fca674e12740fdf73e1a45e612fa30b7e4bbe9883958dcf365de1e6c1607c33172c5d3d7754f3294e450925`

Bech32: `drep_sk14rjh4rs2dzm6k5xxe5f73cypzuv02pknfl9xwnsjws8a7ulp530xztarpdlyh05csw2cmnekths7dstq0se3wtza84m4fueffezsjfglsqmad`

#### DRep verification key

Hex: `f74d7ac30513ac1825715fd0196769761fca6e7f69de33d04ef09a0c417a752b`

Bech32: `drep_vk17axh4sc9zwkpsft3tlgpjemfwc0u5mnld80r85zw7zdqcst6w54sdv4a4e`

#### DRep extended signing key

Hex: `a8e57a8e0a68b7ab50c6cd13e8e0811718f506d34fca674e12740fdf73e1a45e612fa30b7e4bbe9883958dcf365de1e6c1607c33172c5d3d7754f3294e4509251d8411029969123371cde99fb075730f1da4fd41ee7acefba7e211f0e20c91ca`

Bech32: `drep_xsk14rjh4rs2dzm6k5xxe5f73cypzuv02pknfl9xwnsjws8a7ulp530xztarpdlyh05csw2cmnekths7dstq0se3wtza84m4fueffezsjfgassgs9xtfzgehrn0fn7c82uc0rkj06s0w0t80hflzz8cwyry3eg9066uj`

#### DRep extended verification key

Hex: `f74d7ac30513ac1825715fd0196769761fca6e7f69de33d04ef09a0c417a752b1d8411029969123371cde99fb075730f1da4fd41ee7acefba7e211f0e20c91ca`

Bech32: `drep_xvk17axh4sc9zwkpsft3tlgpjemfwc0u5mnld80r85zw7zdqcst6w543mpq3q2vkjy3nw8x7n8asw4es78dyl4q7u7kwlwn7yy0sugxfrjs6z25qe`

#### [DEPRECATED] Verification key hash (DRep ID)

Hex: `a5b45515a3ff8cb7c02ce351834da324eb6dfc41b5779cb5e6b832aa`

Bech32: `drep15k6929drl7xt0spvudgcxndryn4kmlzpk4meed0xhqe25nle07s`

#### Verification key hash (DRep VKH)

Hex: `a5b45515a3ff8cb7c02ce351834da324eb6dfc41b5779cb5e6b832aa`

Bech32: `drep_vkh15k6929drl7xt0spvudgcxndryn4kmlzpk4meed0xhqe254czjh2`

#### [CIP-0129 compliant] Verification key hash appended with  '22' hex-encoded byte (DRep key hash credential)

Hex: `22a5b45515a3ff8cb7c02ce351834da324eb6dfc41b5779cb5e6b832aa`

Bech32: `drep1y2jmg4g450lced7q9n34rq6d5vjwkm0ugx6h0894u6ur92s9txn3a`

#### Script 1 hash (DRep Script Hash)

Hex: `d0657126dbf0c135a7224d91ca068f5bf769af6d1f1df0bce5170ec5`

Bech32: `drep_script16pjhzfkm7rqntfezfkgu5p50t0mkntmdruwlp089zu8v29l95rg`

#### [CIP-0129] Script 1 hash appended with '23' hex-encoded byte (DRep script hash credential)

Hex: `23d0657126dbf0c135a7224d91ca068f5bf769af6d1f1df0bce5170ec5`

Bech32: `drep1y0gx2ufxm0cvzdd8yfxerjsx3adlw6d0d503mu9uu5tsa3gtkvwpe`

#### Script 2 hash (DRep Script Hash)

Hex: `ae5acf0511255d647c84b3184a2d522bf5f6c5b76b989f49bd383bdd`

Bech32: `drep_script14edv7pg3y4wkglyykvvy5t2j906ld3dhdwvf7jda8qaa63d5kf4`

#### [CIP-0129] Script 2 hash appended with '23' hex-encoded byte (DRep script hash credential)

Hex: `23ae5acf0511255d647c84b3184a2d522bf5f6c5b76b989f49bd383bdd`

Bech32: `drep1ywh94nc9zyj46erusje3sj3d2g4ltak9ka4e386fh5urhhga37qxs`


### Constitutional Committee Cold

#### Constitutional Committee Signing Key

Hex: `684f5b480507755f387e7e544cb44b3e55eb3b88b9f6976bd41e5f746ce1a45e28b4aa8bf129088417c0fade65a98a056cbcda96c0a8874cfcbef0bf53932a12`

Bech32: `cc_cold_sk1dp84kjq9qa647wr70e2yedzt8e27kwugh8mfw675re0hgm8p530z3d9230cjjzyyzlq04hn94x9q2m9um2tvp2y8fn7tau9l2wfj5yslmdl88`

#### Constitutional Committee Cold Verification Key

Hex: `a9781abfc1604a18ebff6fc35062c000a7a66fdca1323710ed38c1dfc3315bea`

Bech32: `cc_cold_vk149up407pvp9p36lldlp4qckqqzn6vm7u5yerwy8d8rqalse3t04q7qsvwl`

#### Constitutional Committee Extended Cold Signing Key

Hex: `684f5b480507755f387e7e544cb44b3e55eb3b88b9f6976bd41e5f746ce1a45e28b4aa8bf129088417c0fade65a98a056cbcda96c0a8874cfcbef0bf53932a12c601968e75ff3052ffa675aedaaea49ff36cb23036df105e28e1d32b4527e6cf`

Bech32: `cc_cold_xsk1dp84kjq9qa647wr70e2yedzt8e27kwugh8mfw675re0hgm8p530z3d9230cjjzyyzlq04hn94x9q2m9um2tvp2y8fn7tau9l2wfj5ykxqxtgua0lxpf0lfn44md2afyl7dktyvpkmug9u28p6v452flxeuca0v7w`

#### Constitutional Committee Cold Extended Verification Key

Hex: `a9781abfc1604a18ebff6fc35062c000a7a66fdca1323710ed38c1dfc3315beac601968e75ff3052ffa675aedaaea49ff36cb23036df105e28e1d32b4527e6cf`

Bech32: `cc_cold_xvk149up407pvp9p36lldlp4qckqqzn6vm7u5yerwy8d8rqalse3t04vvqvk3e6l7vzjl7n8ttk646jflumvkgcrdhcstc5wr5etg5n7dnc8nqv5d`

#### [DEPRECATED] Constitutional Committee Cold Verification Key Hash

Hex: `fefb9596ed670ad2c9978d78fe4eb36ba24cbba0a62fa4cdd0c2dcf5`

Bech32: `cc_cold1lmaet9hdvu9d9jvh34u0un4ndw3yewaq5ch6fnwsctw02xxwylj`

#### Constitutional Committee Cold Verification key hash (Constitutional Committee Cold VKH)

Hex: `fefb9596ed670ad2c9978d78fe4eb36ba24cbba0a62fa4cdd0c2dcf5`

Bech32: `cc_cold_vkh1lmaet9hdvu9d9jvh34u0un4ndw3yewaq5ch6fnwsctw0243cw47`

#### [CIP-0129 compliant] Constitutional Committee Cold Verification key hash appended with  '12' hex-encoded byte (Constitutional Committee Cold key hash credential)

Hex: `12fefb9596ed670ad2c9978d78fe4eb36ba24cbba0a62fa4cdd0c2dcf5`

Bech32: `cc_cold1ztl0h9vka4ns45kfj7xh3ljwkd46yn9m5znzlfxd6rpdeagw6p59q`

#### Constitutional Committee Cold Script 1 Hash

Hex: `ae6f2a27554d5e6971ef3e933e4f0be7ed7aeb60f6f93dfb81cd6e1c`

Bech32: `cc_cold_script14ehj5f64f40xju0086fnunctulkh46mq7munm7upe4hpcwpcatv`

#### [CIP-0129] Constitutional Committee Cold Script 1 hash appended with '13' hex-encoded byte (Constitutional Committee Cold script hash credential)

Hex: `13ae6f2a27554d5e6971ef3e933e4f0be7ed7aeb60f6f93dfb81cd6e1c`

Bech32: `cc_cold1zwhx723824x4u6t3aulfx0j0p0n767htvrm0j00ms8xku8q30p2xd`

#### Constitutional Committee Cold Script 2 Hash

Hex: `119c20cecfedfdba057292f76bb110afa3ab472f9c35a85daf492316`

Bech32: `cc_cold_script1zxwzpnk0ah7m5ptjjtmkhvgs4736k3e0ns66shd0fy33vdauq3j`

#### [CIP-0129] Constitutional Committee Cold Script 2 hash appended with '13' hex-encoded byte (Constitutional Committee Cold script hash credential)

Hex: `13119c20cecfedfdba057292f76bb110afa3ab472f9c35a85daf492316`

Bech32: `cc_cold1zvgecgxwelklmws9w2f0w6a3zzh6826897wrt2za4ayjx9swtgkr6`


### Constitutional Committee Hot

#### Constitutional Committee Hot Signing Key

Hex: `d85717921e6289606e15c1e2ee65b3bd6ec247e357889ba16178eedb74e1a45ef955aa17bd002971b05e750048b766eb6df4d855c54dd2ec7ad8850e2fe35ebe`

Bech32: `cc_hot_sk1mpt30ys7v2ykqms4c83wuednh4hvy3lr27yfhgtp0rhdka8p5300j4d2z77sq2t3kp082qzgkanwkm05mp2u2nwja3ad3pgw9l34a0sdh7u7e`

#### Constitutional Committee Hot Verification Key

Hex: `792a7f83cab90261f72ef57ee94a65ca9b0c71c1be2c8fdd5318c3643b20b52f`

Bech32: `cc_hot_vk10y48lq72hypxraew74lwjjn9e2dscuwphckglh2nrrpkgweqk5hschnzv5`

#### Constitutional Committee Hot Extended Signing Key

Hex: `d85717921e6289606e15c1e2ee65b3bd6ec247e357889ba16178eedb74e1a45ef955aa17bd002971b05e750048b766eb6df4d855c54dd2ec7ad8850e2fe35ebe5487e846e9a708b27681d6835fa2dac968108b3c845e379597491e6b476aa0b2`

Bech32: `cc_hot_xsk1mpt30ys7v2ykqms4c83wuednh4hvy3lr27yfhgtp0rhdka8p5300j4d2z77sq2t3kp082qzgkanwkm05mp2u2nwja3ad3pgw9l34a0j5sl5yd6d8pze8dqwksd069kkfdqggk0yytcmet96fre45w64qkgyxl0dt`

#### Constitutional Committee Hot Extended Verification Key

Hex: `792a7f83cab90261f72ef57ee94a65ca9b0c71c1be2c8fdd5318c3643b20b52f5487e846e9a708b27681d6835fa2dac968108b3c845e379597491e6b476aa0b2`

Bech32: `cc_hot_xvk10y48lq72hypxraew74lwjjn9e2dscuwphckglh2nrrpkgweqk5h4fplggm56wz9jw6qadq6l5tdvj6qs3v7ggh3hjkt5j8ntga42pvs5rvh0a`

#### [DEPRECATED] Constitutional Committee Hot Verification Key Hash

Hex: `f6d29c0f7164d37610cbf67b126a993beb24a076d0653f1fa069588f`

Bech32: `cc_hot17mffcrm3vnfhvyxt7ea3y65e804jfgrk6pjn78aqd9vg7xpq8dv`

#### Constitutional Committee Hot Verification key hash (Constitutional Committee Hot VKH)

Hex: `f6d29c0f7164d37610cbf67b126a993beb24a076d0653f1fa069588f`

Bech32: `cc_hot_vkh17mffcrm3vnfhvyxt7ea3y65e804jfgrk6pjn78aqd9vg7vk5akz`

#### [CIP-0129 compliant] Constitutional Committee Hot Verification key hash appended with  '02' hex-encoded byte (Constitutional Committee Hot key hash credential)

Hex: `02f6d29c0f7164d37610cbf67b126a993beb24a076d0653f1fa069588f`

Bech32: `cc_hot1qtmd98q0w9jdxasse0m8kyn2nya7kf9qwmgx20cl5p543rcdtr4dz`

#### Constitutional Committee Hot Script 1 Hash

Hex: `d27a4229c92ec8961b6bfd32a87380dcee4a08c77b0d6c8b33f180e8`

Bech32: `cc_hot_script16fayy2wf9myfvxmtl5e2suuqmnhy5zx80vxkezen7xqwskncf40`

#### [CIP-0129] Constitutional Committee Hot Script 1 hash appended with '03' hex-encoded byte (Constitutional Committee Hot script hash credential)

Hex: `03d27a4229c92ec8961b6bfd32a87380dcee4a08c77b0d6c8b33f180e8`

Bech32: `cc_hot1q0f85s3feyhv39smd07n92rnsrwwujsgcaas6mytx0ccp6q7ak53g`

#### Constitutional Committee Hot Script 2 Hash

Hex: `62e0798c7036ff35862cf42f4e7ada06f7fb5b6465390082a691be14`

Bech32: `cc_hot_script1vts8nrrsxmlntp3v7sh5u7k6qmmlkkmyv5uspq4xjxlpg6u229p`

#### [CIP-0129] Constitutional Committee Hot Script 2 hash appended with '03' hex-encoded byte (Constitutional Committee Hot script hash credential)

Hex: `0362e0798c7036ff35862cf42f4e7ada06f7fb5b6465390082a691be14`

Bech32: `cc_hot1qd3wq7vvwqm07dvx9n6z7nn6mgr0076mv3jnjqyz56gmu9qaj7nrc`
