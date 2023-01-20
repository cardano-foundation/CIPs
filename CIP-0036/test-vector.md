# Test Vector for CIP-0036

## Keys

**Note:** Not all keys are required for certificate recreation.

Payment **private** signing key Hex:
```
614fdfe13d403bee2014570b190d81851f17d8daca0b6dd1ce33014403191003
```

Payment **public** verification Hex:
```
7a24dd8e692cec94b612c2ec81f508aada96557c2052a447b9d197b006fa7d2a
```

Staking **private** signing key Hex:
```
852fa5d17df3efdfdcd6dac53ec9fe5593f3c0bd7cadb3c2af76c7e15dfa8a5c
```

Staking **public** verification key Hex:
```
e3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e432369
```

CIP-36 Vote **public** verification key Hex:
```
0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0
```

CIP-36 Vote **extended private** signing key Hex:
```
4820f7ce221e177c8eae2b2ee5c1f1581a0d88ca5c14329d8f2389e77a465655c27662621bfb99cb9445bf8114cc2a630afd2dd53bc88c08c5f2aed8e9c7cb89
```

## Addresses
- This example uses Pre-Production testnet (testnet-magic 1).

Payment Address:
```
bech32: "addr_test1qprhw4s70k0vzyhvxp6h97hvrtlkrlcvlmtgmaxdtjz87xrjkctk27ypuv9dzlzxusqse89naweygpjn5dxnygvus05sdq9h07"

hex-encoded: "004777561e7d9ec112ec307572faec1aff61ff0cfed68df4cd5c847f1872b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9"
````

Staking Address:
```
bech32: "stake_test1upetv9m90zq7xzk303rwgqgvnje7hvjyqef6xnfjyxwg86gzpmj80"

hex-encoded: "e072b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9"
```

## Certificate Example

- Assigning all voting power to a single voting key. 

### Human Readable Format

Legacy CIP-15 version:
```javascript
"61284": {
  "1": "0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0",
  "2": "0xe3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e432369",
  "3": "0xe072b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9",
  "4": 1234
}
```

CIP-36 version:
```javascript
"61284": {
  "1": [["0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0", 1]],
  "2": "0xe3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e432369",
  "3": "0x004777561e7d9ec112ec307572faec1aff61ff0cfed68df4cd5c847f1872b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9",
  "4": 1234,
  "5": 0
}
```

### CBOR Encoding

Legacy CIP-15 version:
```
a119ef64a40158200036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0025820e3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e43236903581de072b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9041904d2
```

CIP-36 version:
```
a119ef64a501818258200036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a001025820e3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e432369035839004777561e7d9ec112ec307572faec1aff61ff0cfed68df4cd5c847f1872b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9041904d20500
```

### Blake2b-256 Hash

Legacy CIP-15 version:
```
9946e71b5f6c16150cf431910a0f7dbb8084a992577847802e60d32becb3d6be
```

CIP-36 version:
```
3110fbad72589a80de7fc174310e92dac35bbfece1690c2dce53c2235a9776fa
```

## Metadata Example with Witness

Legacy CIP-15 version:
```javascript
{
  "61284": {
    "1": "0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0",
    "2": "0xe3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e432369",
    "3": "0xe072b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9",
    "4": 1234
  },
  "61285": {
    "1": "0xa9ec8735804c6c4c5c4a02e9589c65508ec7060063b2d7dbeba82d1cbfa1b8be6b457f95d4ead5e8b454b989624fa44e0b89a64d089fdc0a6a1268fef4876d0f" 
  }
}
```

CIP-36 version:
```javascript
{
  "61284": {
    "1": [["0x0036ef3e1f0d3f5989e2d155ea54bdb2a72c4c456ccb959af4c94868f473f5a0", 1]],
    "2": "0xe3cd2404c84de65f96918f18d5b445bcb933a7cda18eeded7945dd191e432369",
    "3": "0x004777561e7d9ec112ec307572faec1aff61ff0cfed68df4cd5c847f1872b617657881e30ad17c46e4010c9cb3ebb2440653a34d32219c83e9",
    "4": 1234,
    "5": 0
  },
  "61285": {
    "1": "0xcbb96ba1596fafc18eec84e306feea3067ba1c6ace95b11af820bcbd53837ef32bdcf28176749061e1f2a1300d4df98c80582722786e40cf330072d0b78a7408"
  }
}
```