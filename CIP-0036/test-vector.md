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

Legacy version (full delegation to one key only):
```javascript
'61284': {
  '1': '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
  '2': '0x86870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e',
  '3': '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
  '4': 1234,
},
```

New version:
```javascript
'61284': {
  '1': [['0xa6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d1663', 1], ['0x00588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee', 3]],
  '2': '0x86870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e',
  '3': '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
  '4': 1234,
  '5': 0
},
```


Metadata (CBOR encoding)

Legacy:
```
a119ef64a4015820a6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d166302582086870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e03581de0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef041904d2
```

New:
```
a119ef64a50182825820a6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d16630182582000588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee0302582086870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e03581de0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef041904d20500
```

Blake2b-256 hash of metadata

Legacy:
```
872bcb4a9e2b110a06fd5de04be5924b6c659c28a1665ecc75def13ebca6dfd8
```

New:
```
5bc0681f173efd76e1989037a3694b8a7abea22053f5940cbb5cfcdf721007d7
```

### Output

Legacy:
```javascript
{
  '61284': {
    '1': '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
    '2': '0x1c5d88aa573da97e5a4667e0f7c4a9c6a3d848934c3b0a5b9296b401540f2aef',
    '3': '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
    '4': 1234,
  },
  '61285': {
    '1': '0xcf8e34db193edc930faf64626a0a759dd9ce654874d4b6f255dc2aa8f52313b6dbb9aa1b162b43ed8946668edca920dd34f5a51a14130814fdc86adb6218b501'
  }
}
```

New:
```javascript
{
  '61284': {
    '1': [['0xa6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d1663', 1], ['0x00588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee', 3]],
    '2': '0x1c5d88aa573da97e5a4667e0f7c4a9c6a3d848934c3b0a5b9296b401540f2aef',
    '3': '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
    '4': 1234,
    '5': 0
  },
  '61285': {
    '1': '0x3aaa2e6b43c0a96e880a7d70df84dffb2a1a17b19d7a99a6ed27b91d499b32027c43acfbf6dff097af7634b2ee38c8039af259b0b6a64316f02b4ffee28a0608'
  }
}
```
