# Test vector for CIP15

### Inputs

Payment **public** key hex
```
3273a5316e4de228863bd7cf8dac90d57149e1a595f3dd131073b84e35546676
```

Staking **private** key hex
```
f5beaeff7932a4164d270afde7716067582412e8977e67986cd9b456fc082e3a
```

Catalyst **private** key hex
```
4820f7ce221e177c8eae2b2ee5c1f1581a0d88ca5c14329d8f2389e77a465655c27662621bfb99cb9445bf8114cc2a630afd2dd53bc88c08c5f2aed8e9c7cb89
```

### Intermediate steps

Reward address generated from staking key
```
bech32
stake_test1uzhr5zn6akj2affzua8ylcm8t872spuf5cf6tzjrvnmwemcehgcjm

hex-encoded
e0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef
```

Data to sign (human readable format)
```javascript
61284: {
  1: '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
  2: '0x86870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e',
  3: '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
  4: 1234,
},
```

Metadata (CBOR encoding)
```
a119ef64a40158200036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a002582086870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e03581de0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef041904d2
```

Blake2b-256 hash of metadata
```
a3d63f26cd94002443bc24f24b0a150f2c7996cd3a3fd247248de396faea6a5f
```

### Output

```javascript
{
  61284: {
    1: '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
    2: '0x1c5d88aa573da97e5a4667e0f7c4a9c6a3d848934c3b0a5b9296b401540f2aef',
    3: '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
    4: 1234
  },
  61285: {
    1: '0x6c2312cd49067ecf0920df7e067199c55b3faef4ec0bce1bd2cfb99793972478c45876af2bc271ac759c5ce40ace5a398b9fdb0e359f3c333fe856648804780e'
  }
}
```
