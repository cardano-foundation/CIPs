# CIP-88 Extension: CIP-0102 | Royalty Datum Metadata

`Version: 1`

## Top-Level Fields

| index | name                | type  | required | notes                                                     |
| ----- | ------------------- | ----- | -------- | --------------------------------------------------------- |
| 0     | Version             | UInt  | No       | Default: 1, which version of this specification is in use |
| 1     | Royalty Token Names | Array | Yes      | Asset names of the royalty token(s) for this collection   |

## Field Notes

#### 0: Version

**_Type: Unsigned Integer | Required: No | Default: 1_**

Which version of this CIP-88 extension specification is in use.

**Example:** `1`

#### 1: Royalty Token Names

**_Type: Array | Required: Yes_**

An array of asset names (as raw bytes) of the CIP-102 royalty NFTs minted under this collection's policy ID. The policy ID is implicit from the CIP-88 registration scope.

Implementors **must** look up each listed asset name under the collection's policy ID to retrieve the associated royalty datum, as specified in [CIP-0102][].

- For **v1** collections with a single royalty policy, this will contain one entry: `001f4d70526f79616c7479` (hex for `(500)Royalty`).
- For **v2** collections using intrapolicy royalties, this lists the asset names of all applicable royalty tokens (e.g., `001f4d70526f79616c747931` for `(500)Royalty1`, `001f4d70526f79616c747932` for `(500)Royalty2`, etc.).

Asset names follow the format defined in the CIP-0102 Pattern section: the [CIP-0067][] label `500` prefix (`001f4d70`) followed by the UTF-8 encoding of `"Royalty"` (`526f79616c7479`), with an optional UTF-8 encoded decimal postfix.

**Example (single policy):**

```
["001f4d70526f79616c7479"]
```

**Example (intrapolicy royalties):**

```
[
  "001f4d70526f79616c747931",
  "001f4d70526f79616c747932"
]
```

## CIP-102 Example

Single royalty policy:

```cbor
{
  102: {
    0: 1,                                    ; version
    1: [                                     ; royalty token names
      h'001f4d70526f79616c7479'              ; (500)Royalty
    ]
  }
}
```

Intrapolicy royalties (multiple royalty policies):

```cbor
{
  102: {
    0: 1,                                    ; version
    1: [                                     ; royalty token names
      h'001f4d70526f79616c747931',           ; (500)Royalty1
      h'001f4d70526f79616c747932'            ; (500)Royalty2
    ]
  }
}
```

[CIP-0102]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0102
[CIP-0067]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067
