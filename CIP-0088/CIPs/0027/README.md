# CIP-88 Extension: CIP-0027 | Cardano Token Royalty Information

`Version: 1`

## Top Level Fields

| index | name            | type   | required | notes                                                          |
|-------|-----------------|--------|----------|----------------------------------------------------------------|
| 0     | Version         | UInt   | No       | Default: 1, which version of this specification is in use      |
| 1     | Royalty Details | Object | Yes      | An object detailing the project royalties as defined in CIP-27 |

## Royalty Details Fields

| index | name              | type              | required |
|-------|-------------------|-------------------|----------|
| 0     | Rate              | String            | Yes      |
| 1     | Recipient Address | Array             | Yes      |

### Field Notes

#### 0: Rate

***Type: String | Required: Yes***

This should be a floating point number between 0.000000 - 1.000000 representing the rate of royalties requested

**Example:** `"0.05"`

#### 1: Recipient Address

***Type: Array | Required: Yes***

This should be an array containing a single Cardano Shelley-era address in BECH32 format to receive royalties

**Example:** `[
"addr_test1qqp7uedmne8vjzue66hknx87jspg56qhkm4gp6ahyw7kaahevmtcux",
"lpy25nqhaljc70094vfu8q4knqyv6668cvwhsq64gt89"
]`

## CIP-27 Example

```cbor 
{
  27: {
    0: 1,
    1: {
      0: "0.05",
      1: [
        "addr_test1qqp7uedmne8vjzue66hknx87jspg56qhkm4gp6ahyw7kaahevmtcux",
        "lpy25nqhaljc70094vfu8q4knqyv6668cvwhsq64gt89"
      ]
    }
  }
}
```