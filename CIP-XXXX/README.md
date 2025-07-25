---
CIP: 157
Title: Cardano URIs - Enhanced Payments
Category: Wallets
Status: Proposed
Authors:
    - Adam Dean <adam@crypto2099.io>
Implementors:
    - Begin Wallet <@francisluz>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/843
    - https://github.com/cardano-foundation/CIPs/issues/836
Created: 2024-06-15
License: Apache-2.0
---

## Abstract

This CIP will propose a new [CIP-13] Extension; introducing a new, dedicated
`payment` authority and provide support for _Native Assets_ and transactional
_Metadata_ as well as providing for extensibility and versioning. All features
lacking in the original [CIP-13] payment URIs.

## Motivation: why is this CIP necessary?

[CIP-13] was originally introduced in early 2021, prior to the Mary hard fork
event that brought _Native Assets_ to Cardano. Since that time the Cardano
Native Asset ecosystem has flourished and become a large, multi-million dollar
economy. However, [CIP-13] Payment URIs have not been updated to support Native
Assets and have struggled to find adoption amongst mobile wallet creators.

## Specification

This extension to the [CIP-13] URN scheme defines the `payment` authority for
Cardano URIs to more explicitly extend the functionality originally defined in
[CIP-13] in the era of native assets, metadata, and smart contracts as everyday
parts of the Cardano ledger.

### ABNF Grammar

* Due to attempting to optimize for QR code usage for payment URIs, this scheme
  intentionally aims to keep query parameters as truncated as possible as every
  byte of data is sacred.

```
uri             = scheme "://" authority "/" address [ "?" query ]
scheme          = "web+cardano"
authority       = "pay"
address         = (base58 | bech32)

query           = query-param *( "&" query-param )
query-param     = lovelace-param / payment-id-param / note-param / tokens-param

lovelace-param  = "l=" 1*DIGIT
payment-id-param= "i=" 1*( ALPHA / DIGIT / "-" / "_" )
note-param      = "n=" pct-encoded-note
pct-encoded-note = *( unreserved / pct-escape )
pct-escape      = "%" HEXDIG HEXDIG
unreserved      = ALPHA / DIGIT / "-" / "." / "_" / "~"

tokens-param    = "t=" token *( "," token )
token           = bech32-asset "|" 1*DIGIT
bech32-asset    = "asset1" 39bechchar
39bechchar      = 39*bech32char
bech32char      = %x30-39 / %x61-7A

ALPHA           = %x41-5A / %x61-7A
DIGIT           = %x30-39
```

#### URI

This defines the overall structure of a Cardano payment URI. It starts with the
URI scheme (`web+cardano://`), followed by an authority component (`pay`), a
single forward slash, a Cardano address, and an optional query string that
contains one or more payment parameters.

#### Scheme

The URI must begin with the literal string `web+cardano`, indicating that this
is a Cardano-specific URI.

#### Authority

The authority component of the URI must be the string `pay`, which identifies
the URI as a payment request.

#### Address

This is the recipient’s Cardano address. It may be encoded in either:

Bech32 (e.g., `addr1...`), used for Shelley-era and later addresses, or

Base58 (e.g., `Ae2...`), used for legacy Byron-era addresses.

#### Query

The optional query string contains one or more key-value pairs separated by &.
Each parameter defines a specific payment option, such as amount, note, or
additional tokens.

##### Query Parameters

Defines the allowed query parameters. Each one must match one of the following:

* `l=` for specifying lovelace amount
* `i=` for an optional payment identifier
* `n=` for a short note (percent-encoded)
* `t=` for additional assets (tokens)

##### Lovelace Parameter

Specify the amount to send in lovelace (1 ADA = 1,000,000 lovelace). This is a
positive integer with no decimal points. For example: `l=1500000`.

##### Payment Identifier Parameter

An optional identifier for the payment. It can include letters, digits, dashes,
and underscores. Useful for linking to an invoice ID or internal reference.

##### Note Parameter

An optional user-readable note describing the payment. The note must be
percent-encoded and should not exceed 64 characters after decoding. For example:
`n=Thanks%20for%20lunch`.

##### Tokens Parameter

Specify one or more native Cardano tokens to be included in the transaction.
Each token is expressed as a CIP-0014 Bech32-encoded asset ID, followed by `|`
and the quantity. Commas separate multiple tokens and their quantities. Tokens
must be bech32-encoded per [CIP-14].

Example:
`t=asset1xyz...|100,asset1abc...|5`

### Examples

#### Minimal URI

``` 
web+cardano://pay/addr1q9fxv0...
```

This is the most basic form. It simply specifies a recipient Cardano address
with no additional metadata. A wallet should open with this address pre-filled
but leave the amount and other fields blank for the user to complete manually.

#### Send a specific amount of Lovelace (ADA)

``` 
web+cardano://pay/addr1q9fxv0...?l=1000000
```

This request is for 1 ADA (1,000,000 lovelace). When opened, the wallet should
pre-fill the recipient and the amount to send.

> **NOTE:** If not specified, it's assumed that the wallet will include the
> minimum amount of Lovelace (minUTxO) to complete the transaction.

#### Add a human-readable payment note

``` 
web+cardano://pay/addr1q9fxv0...?l=1500000&n=Thanks%20for%20the%20coffee
```

This request includes both an amount (1.5 ADA) and a note: "Thanks for the
coffee". The note is percent-encoded to ensure URI safety. Wallets should decode
and show this message to the sender.

#### Include a Payment ID (for POS & E-Comm Systems Integration)

``` 
web+cardano://pay/addr1q9fxv0...?i=invoice-934
```

Includes an optional payment identifier (e.g., for tracking or invoice
purposes). Wallets may display this reference but aren't required to store or
act on it.

#### Include Native Assets

``` 
web+cardano://pay/addr1q9fxv0...?t=asset1w3nsh8n34lk5vh4qk43z5pv77rxz9xjkw6t3rr|5
```

This transaction includes 5 units of a native asset identified by its Bech32
CIP-14 asset ID (`asset1...`). Wallets should include this token in the
transaction output.

#### Multiple Tokens and Lovelace

``` 
web+cardano://pay/addr1q9fxv0...?l=2500000&t=asset1xyz...|10,asset1abc...|1
```

This URI requests 2.5 ADA plus:

* 10 units of `asset1xyz...`
* 1 unit of `asset1abc...`

This could be used for redeeming multiple rewards or purchasing a bundle of
items.

#### Full URI with all optional parameters

``` 
web+cardano://pay/addr1q9fxv0...?l=5000000&i=order1234&n=Swag%20Booth%20Redemption&t=asset1sh9k...|3
```

This URI requests:

* 5 ADA
* A payment ID of `order1234`
* A note: "Swag Booth Redemption"
* 3 units of the native asset `asset1sh9k...`

#### Legacy Byron Address support

``` 
web+cardano://pay/Ae2tdPwUPEZKTmZVtb8N9...
```

Supports backward compatibility for Byron-era Base58 addresses. All query
parameters work the same.

Perfect for event check-in, point redemption, or ticket claiming.

## Rationale: how does this CIP achieve its goals?

This CIP achieves its goals by defining a new, explicit `Payment URI` standard
that is aligned with modern Cardano transaction standards such as:

* Providing an address to pay to
* Providing a Lovelace amount to send
* Providing one (or more) Native Assets to send
* Providing a transaction metadata message to send

## Path to Active

### Acceptance Criteria

* [ ] Community Feedback and Review Integrated
* [ ] At least one wallet supports this payment standard
* [ ] At least one project utilizing this payment standard

### Implementation Plan

Leveraging existing connections within the ecosystem; we will find willing
partners to integrate this new standard and deploy a proof of concept
integration.

## Copyright

This CIP is licensed
under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[CIP-13]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0013/

[CIP-14]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0014/

[CPS-16]:https://github.com/cardano-foundation/CIPs/blob/master/CPS-0016/
