# CIP-88 Extension: CIP-0086 | Token Metadata Update Oracles

`Version: 1`

## Top Level Fields

| index | name           | type                | required |
|-------|----------------|---------------------|----------|
| 0     | version        | Unsigned Integer    | No       |
| 1     | main address   | [Address](#address) | Yes      |
| 2     | update address | [Address](#address) | Yes      |

### Field Notes

#### 0: Version

***Type: Unsigned Integer | Required: No | Default: 1***

The version of this standard being used

#### 1: Main Address

***Type: [Address](#address) | Required: Yes***

An address capable of providing a new address to be used for updates
per [CIP-0086](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0086).

#### 2: Update Address

***Type: [Address](#address) | Required: Yes***

The address to monitor for metadata updates
per [CIP-0086](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0086).

## Address

**Type: Array\<String>**

An address should be represented in the metadata (JSON) as an array of strings using the hex-encoded address value.

In CBOR, the Address should be represented as a byte-encoded string.

### Examples

#### Enterprise Address

**JSON**
```json
{
  "1": ["613d4d8113505bc64686c7baf802b4ce14c9e203f8a3cd4377babfb3a3"]
}
```

**CBOR**
```cbor
{
    1: h'613d4d8113505bc64686c7baf802b4ce14c9e203f8a3cd4377babfb3a3'
}
```

#### Staking Address

**JSON**
```json
{
  "1": ["01640020a2dafc5f336104f78afe924637c06f269b207ed44782a105f0", "8910cb650afd1bd6cf3fc1480887bfe5d211a0770d0d3fd70fc8e6b9"]
}
```

**CBOR**
```cbor 
{
    1: h'01640020a2dafc5f336104f78afe924637c06f269b207ed44782a105f08910cb650afd1bd6cf3fc1480887bfe5d211a0770d0d3fd70fc8e6b9'
}
```

## CIP-86 Example

```cbor
{
    86: {
        0: 1,                                                                                                                       ; Version
        1: h'613d4d8113505bc64686c7baf802b4ce14c9e203f8a3cd4377babfb3a3',                                                           ; Main Address
        2: h'01640020a2dafc5f336104f78afe924637c06f269b207ed44782a105f08910cb650afd1bd6cf3fc1480887bfe5d211a0770d0d3fd70fc8e6b9'    ; Update Address
    }
}
```