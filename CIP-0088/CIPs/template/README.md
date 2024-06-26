# CIP-88 Extension: CIP-XXXX | CIP-Descriptor

`Version: 1`

## Top-Level Fields

| index | name              | type   | required | notes                                                     |                                                     
|-------|-------------------|--------|----------|-----------------------------------------------------------|
| 0     | Version           | UInt   | No       | Default: 1, which version of this specification is in use |
| 1     | Details Object #1 | Object | No       | An object describing the CIP-Specific fields              |

**Note: The Details Object can and SHOULD be renamed to match the needs of the CIP in question.
Additional indices and detail structures may be added at the top level of a CIP-Specific Extension.
Please remove this line prior to publication.**

## Details Object #1 Fields

| index | name      | type   | required | notes                             |
|-------|-----------|--------|----------|-----------------------------------|
| 0     | Something | String | Yes      | This is a note about Something... |
| 1     | Foo       | UInt   | No       | The number of bars                |
| 2     | Stuff     | Array  | No       | Can contain things                |

### Field Notes

#### 0: Something

***Type: String | Required: Yes***

Describe what something is and what it does here...

**Example:** `"Things"`

#### 1: Foo

***Type: Unsigned Integer | Required: No | Default: 0***

Describe the Foo field and what it's for here...

**Example:** `7`

#### 2: Stuff

***Type: Array | Required: No | Default: Null***

Use a table and/or prose to describe the contents of the Stuff array here...

**Example:** `[
'Thing #1',
'Thing #2'
]`

## CIP-XXXX Example

```cbor
{
    XXXX: {                  ; CIP-Specific Identifier
        0: 1,                ; version
        1: {                 ; details object #1
            0: 'Blah!'       ; Something
            1: 492           ; Foo
            2: [             ; Stuff
                'Thing #1',  ; Things...
                'Thing #2'   ; More things...
            ]
        }
    }
}  
```


