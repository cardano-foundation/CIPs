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

Base address generated from payment key and staking key
```
bech32
addr_test1qz0srp4ptag9j2e3rdtesrsxe708j80uhxv2r7utl4jaqm4w8g984mdy46jj9e6wfl3kwk0u4qrcnfsn5k9yxe8kanhswx8e6k

hex-encoded
009f0186a15f50592b311b57980e06cf9e791dfcb998a1fb8bfd65d06eae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef
```

Data to sign (human readable format)
```javascript
'61284': {
  '1': '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
  '2': '0x86870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e',
  '3': '0x009f0186a15f50592b311b57980e06cf9e791dfcb998a1fb8bfd65d06eae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef',
  '4': 1234,
},
```

Metadata (CBOR encoding)
```
a119ef64a40158200036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a002582086870efc99c453a873a16492ce87738ec79a0ebd064379a62e2c9cf4e119219e035839009f0186a15f50592b311b57980e06cf9e791dfcb998a1fb8bfd65d06eae3a0a7aeda4aea522e74e4fe36759fca80789a613a58a4364f6ecef041904d2
```

Blake2b-256 hash of metadata
```
ad9536996c7910882e77d4e54465883b39ef4aa86837c8ff4f18d34ae6876d1a
```

### Output

```javascript
{
  '61284': {
    '1': '0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0',
    '2': '0x1c5d88aa573da97e5a4667e0f7c4a9c6a3d848934c3b0a5b9296b401540f2aef',
    '3': '0x019f0186a15f50592b311b57980e06cf9e791dfcb998a1fb8bfd65d06ea3ba547223c9b7f4d6c545c70c0f2c1dbdf925ae98db761287aa5a85',
    '4': '1234
  },
  '61285': {
    '1': '0x1d1e5d6d35d6088aac2cc60cc58fb603860982fb1dd144bebad222448042845a3e33a1e43daef605ee42ddd68940780bd69960833c3831c013707f8d6ed8c10f'
  }
}
```