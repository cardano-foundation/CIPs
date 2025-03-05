# CIP-88 Extension: CIP-48 | Metadata References Standard

`Version: 1`

CIP-48 has been proposed to extend on-chain metadata formats to support "references" which could be:

1. Shared/Repeated pieces of content
2. Pointers or References to other on-chain information

CIP-88 could help support the definition and standardization of the reference definitions at a top-level, allowing
references declared within individual token metadata to be easily identified and replaced.

## Top Level Fields

| index | name              | type   | required | notes                                                      |
|-------|-------------------|--------|----------|------------------------------------------------------------|
| 0     | Version           | UInt   | No       | Default "1", which version of this specification is in use |
| 1     | Reference Details | Object | Yes      | An object detailing CIP-48 references in use               |

## Reference Details Fields

| index | name       | type              | required | notes                  |
|-------|------------|-------------------|----------|------------------------|
| 1     | References | Array\<Reference> | No       | An array of References |


## Reference Fields

| index | name    | type   | required | notes                                                                                                                 |
|-------|---------|--------|----------|-----------------------------------------------------------------------------------------------------------------------|
| 0     | Name    | String | Yes      | A case sensitive path identifier for this reference                                                                   |
| 1     | Type    | Enum   | Yes      | An enum of accepted types of references which may include direct payloads or pointers to other sources of information |
| 2     | Payload | Object | Yes      | A "Reference Payload" object containing the information to be substituted in place of the reference                   |

**TODO: Expand Support for CIP-48**

## CIP-48 Example

```cbor
{
    48: {
        0: 1,
        1: {
            0: '',
            1: '',
            2: {}
        }
    }
}
```