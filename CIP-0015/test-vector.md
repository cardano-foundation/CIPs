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
'61284': {
  '1': '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
  '2': '0x86870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e',
  '3': '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
  '4': 1234,
  '5': 0
},
```

Metadata (CBOR encoding)
```
a119ef64a50158200036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a002582086870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e03581de0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef041904d20500
```

Blake2b-256 hash of metadata
```
fbab7239fc029ab0ec2f315dba767a6730a60a53c384507bd50c10b7ce26b737
```

### Output

```javascript
{
  '61284': {
    '1': '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
    '2': '0x1c5d88aa573da97e5a4667e0f7c4a9c6a3d848934c3b0a5b9296b401540f2aef',
    '3': '0xe0ae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
    '4': 1234,
    '5': 0
  },
  '61285': {
    '1': '0x783da057e5dadb75c6d6f1ae121df29106a5c4ed8d7c87927c89b5743e05659e2740172aa6c838304c2627a84536844973b34611e374e70e9183b96c85169a04'
  }
}
```
