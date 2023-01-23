# Test Vector for CIP-0062

## Delegation

### Keys

Payment **public** verification key Hex:
```
3bc3383b1b88a628e6fa55dbca446972d5b0cd71bcd8c133b2fa9cd3afbd1d48
``` 

Payment **private** signing key Hex:
```
b5c85fa8fb2d8cd4e4f624c206946652b6764e1af83034a79b32320ce3940dd9
```

Staking **public** verification key Hex:
```
b5462be6a8a8ec0c4d6ee6edb83794a03df1bca43edc72b380df2ad3a982a555
```

Staking **private** signing key:
```
2f669f45365099666940922d47b29563d2c9f885c88a077bfea17631a7579d65
```

### Addresses

* Addresses for Pre-Production testnet (testnet-magic 1).

#### Payment Address
```
bech32: "addr_test1qp7n0mudgm6gkyaf6q883nqw7ls73a89mt8exk4gkk44gaeez0pen8lxnyz4nejgal24e7zegkk53p3h6twnafy5ra2qpy52u6"

hex-encoded: "007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54"
```

### Delegation Certificate Example

* In this example voting power is delegated to two voting keys with varying weights; assigning key 1 25% voting power and key 2 75% voting power.
* For Project Catalyst, so using voting purpose 0. 
* Transaction submitted to Pre-Production testnet.

#### Delegation Certificate

```
{
  "1":[["0x1788b78997774daae45ae42ce01cf59aec6ae2acee7f7cf5f76abfdd505ebed3",1],["0xb48b946052e07a95d5a85443c821bd68a4eed40931b66bd30f9456af8c092dfa",3]],
  "2":"0xb5462be6a8a8ec0c4d6ee6edb83794a03df1bca43edc72b380df2ad3a982a555",
  "3":"0x007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54",
  "4":5479467,
  "5":0
}
```

#### Delegation Certificate with Signature

```
{
  "61284":{
    "1":[["0x1788b78997774daae45ae42ce01cf59aec6ae2acee7f7cf5f76abfdd505ebed3",1],["0xb48b946052e07a95d5a85443c821bd68a4eed40931b66bd30f9456af8c092dfa",3]],
    "2":"0xb5462be6a8a8ec0c4d6ee6edb83794a03df1bca43edc72b380df2ad3a982a555",
    "3":"0x007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54",
    "4":5479467,
    "5":0
  },
  "61285": {
    "1":"0xafb9e76a6ba5e391fc11bb233d77b54bb6a1222d9a52cf420143445d3397861917d5dc6f106d5969a45fe2067109fc12697596cf5c1c2d006993ea5cbcc35307"
  }
}
```

#### Transaction with Delegation Certificate as Metadata Hex

```
84a40081825820117ca91fc909a8d8741fe93b732f4d1433eb6c645e564249217f2c357be8abbe000181a2005839007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54011a05f312d7021a0002ce290758202ff4fc9e1fe0e8d5a0154b6d9c5ca5e281416f5c54fd8b32b0653b2c9fac93a0a100818258203bc3383b1b88a628e6fa55dbca446972d5b0cd71bcd8c133b2fa9cd3afbd1d4858401092539f644df9b8cce12c8c7bff1d2a570b83d3e75e1659ccd349bb6599afe415a1726621626d6b6afd1fd68591c73474a69baa897070c1483c91631222840bf5d90103a100a219ef64a501828258201788b78997774daae45ae42ce01cf59aec6ae2acee7f7cf5f76abfdd505ebed301825820b48b946052e07a95d5a85443c821bd68a4eed40931b66bd30f9456af8c092dfa03025820b5462be6a8a8ec0c4d6ee6edb83794a03df1bca43edc72b380df2ad3a982a555035839007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54041a00539c2b050019ef65a1015840afb9e76a6ba5e391fc11bb233d77b54bb6a1222d9a52cf420143445d3397861917d5dc6f106d5969a45fe2067109fc12697596cf5c1c2d006993ea5cbcc35307
```

#### On-Chain View

```
Transaction Hash: "1439e90955c2b5d87bc07149840981b5257e4a7f60a584e57f954f7229f67397"

Block: "308719"

Epoch / Slot: "34 / 397143"

Absolute Slot: "13443543"
```

## Voting 

* Each project utilizing this standard should provide their own set of test vectors for voting

### Catalyst Version 0 

TODO