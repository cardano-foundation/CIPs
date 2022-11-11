# Test vector for CIP-0036

## Keys

Payment **public** verfication key:
```javascript
{
    "type": "PaymentVerificationKeyShelley_ed25519",
    "description": "Payment Verification Key",
    "cborHex": "58203bc3383b1b88a628e6fa55dbca446972d5b0cd71bcd8c133b2fa9cd3afbd1d48"
}
```
Payment **public** address:
```javascript
bench32: "addr_test1qp7n0mudgm6gkyaf6q883nqw7ls73a89mt8exk4gkk44gaeez0pen8lxnyz4nejgal24e7zegkk53p3h6twnafy5ra2qpy52u6"

HEX: "007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54"
```

Payment **private** signing key:
```javascript
{
    "type": "PaymentSigningKeyShelley_ed25519",
    "description": "Payment Signing Key",
    "cborHex": "5820b5c85fa8fb2d8cd4e4f624c206946652b6764e1af83034a79b32320ce3940dd9"
}
```

Staking **public** verfication key:
```javascript
{
    "type": "StakeVerificationKeyShelley_ed25519",
    "description": "Stake Verification Key",
    "cborHex": "5820b5462be6a8a8ec0c4d6ee6edb83794a03df1bca43edc72b380df2ad3a982a555"
}
```

Staking **public** "rewards" address:
```javascript
bench32: "stake_test1uqu38suenlnfjp2eueywl42ulpv5tt2gscma9hf75j2p74qhtfeq7"

HEX: "3913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54"
```

Staking **private** signing key:
```javascript
{
    "type": "StakeSigningKeyShelley_ed25519",
    "description": "Stake Signing Key",
    "cborHex": "58202f669f45365099666940922d47b29563d2c9f885c88a077bfea17631a7579d65"
}
```

Catalyst **private** key:
```javascript
4820f7ce221e177c8eae2b2ee5c1f1581a0d88ca5c14329d8f2389e77a465655c27662621bfb99cb9445bf8114cc2a630afd2dd53bc88c08c5f2aed8e9c7cb89
```

## Delegation Certificate Example

### Data to sign (human readable format)

Legacy CIP-15 version (full delegation to one key only):
```javascript
61284: {
  1: '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
  2: '0x93bf1450ec2a3b18eebc7acfd311e695e12232efdf9ce4ac21e8b536dfacc70f',
  3: '0x3913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54',
  4: 1234,
},
```

CIP-36 version:
```javascript
61284: {
  1: [['0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0', 1]],
  2: '0x93bf1450ec2a3b18eebc7acfd311e695e12232efdf9ce4ac21e8b536dfacc70f',
  3: '0x007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54',
  4: 1234,
  5: 0
},
```


### Output

Legacy:
```javascript
{
  61284: {
    1: '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
    2: '0x93bf1450ec2a3b18eebc7acfd311e695e12232efdf9ce4ac21e8b536dfacc70f',
    3: '0x3913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54',
    4: 1234,
},
  61285: {
    1: ''
  }
}
```

New:
```javascript
{
  61284: {
    1: [['0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0', 1]],
    2: '0x93bf1450ec2a3b18eebc7acfd311e695e12232efdf9ce4ac21e8b536dfacc70f',
    3: '0x007d37ef8d46f48b13a9d00e78cc0ef7e1e8f4e5dacf935aa8b5ab54773913c3999fe6990559e648efd55cf85945ad488637d2dd3ea4941f54',
    4: 1234,
    5: 0
},
  61285: {
    1: ''
  }
}
```