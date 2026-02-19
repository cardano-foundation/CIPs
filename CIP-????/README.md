---
CIP: "?"
Title: Native Token Fee Payment API
Category: Tools
Status: Proposed
Authors:
    - Chase Maity <chase@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1052
Created: 2025-07-08
License: CC-BY-4.0
---

## Abstract

This document describes a user facing HTTP service that allows dApps to use native non-ada tokens from a wallet to pay for transaction fees and deposits. This can either be achieved by the official babel fees functionality once available, or UTxO based solutions (such as [feesaswap.io](http://feesaswap.io), [aquarium by fluid](https://docs.fluidtokens.com/protocols/aquarium/) etc). This specification defines the manner in which such a service should be accessed by a dApp, as well as defining the API and its expected behavior that such a service should provide.

## Motivation: why is this CIP necessary?

There is growing interest in using custom tokens to pay for transaction fees and UTxO deposits within the Cardano community. On the flipside, there are an increasing number of services trying to fulfill this niche in lieu of the official babel fees, e.g [feesaswap.io](http://feesaswap.io), [aquarium by fluid](https://docs.fluidtokens.com/protocols/aquarium/). Given this trend may spark the interest of dApp and wallet developers and drive them to integrate with these services, it would be beneficial to have a standardized API that users and integrators could use to inter-operate between different services, and eventually babel fees. This could kick-start the user/integrator-side of the niche, utilizing existing UTxO based services, while waiting for babel fees to reach the finish line.

## Specification

### Data Types

#### Address

A string representing an address on the blockchain. Must be in hex encoded [CBOR](https://datatracker.ietf.org/doc/html/rfc7049) format as defined in the [Shelley Multi-Asset binary spec](https://github.com/IntersectMBO/cardano-ledger/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl).

Example:
```
00e1cbb80db89e292269aeb93ec15eb963dda5176b66949fe1c2a6a38d1b930e9f7add78a174a21000e989ff551366dcd127028cb2aa39f616
```

#### TransactionInput

A string representing a transaction input. Must be in hex encoded [CBOR](https://datatracker.ietf.org/doc/html/rfc7049) format as defined in the [Shelley Multi-Asset binary spec](https://github.com/IntersectMBO/cardano-ledger/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl).

Example:
```
8282582004ffecdf5f3ced5c5c788833415bcbef26e3e21290fcebcf8216327e21569e420082583900e1cbb80db89e292269aeb93ec15eb963dda5176b66949fe1c2a6a38d1b930e9f7add78a174a21000e989ff551366dcd127028cb2aa39f6161a004c4b40
```

#### PolicyId

A string representing the minting policy of a custom token. Must be the hex encoded hash of a minting policy.

Example:
```
ff80aaaf03a273b8f5c558168dc0e2377eea810badbae6eceefc14ef
```

#### TokenName

A string representing the token name of a custom token. Must be the hex encoded version of the UTF-8 encoded name.

Example:
```
474f4c44
```
(Represents 'GOLD')

#### Asset

PolicyId and TokenName joined by a period (‘.’).

```ts
type Asset = `${PolicyId}.${TokenName}`;
```

Example:
```
ff80aaaf03a273b8f5c558168dc0e2377eea810badbae6eceefc14ef.474f4c44
```

#### Transaction

A string representing a full transaction. Must be in hex encoded [CBOR](https://datatracker.ietf.org/doc/html/rfc7049) format as defined in the [Shelley Multi-Asset binary spec](https://github.com/IntersectMBO/cardano-ledger/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl).

Example:
```
84a70082825820975e4c7f8d7937f8102e500714feb3f014c8766fcf287a11c10c686154fcb27501825820c887cba672004607a0f60ab28091d5c24860dbefb92b1a8776272d752846574f000d818258207a67cd033169e330c9ae9b8d0ef8b71de9eb74bbc8f3f6be90446dab7d1e8bfd00018282583900fd040c7a10744b79e5c80ec912a05dbdb3009e372b7f4b0f026d16b0c663651ffc046068455d2994564ba9d4b3e9b458ad8ab5232aebbf401a1abac7d882583900fd040c7a10744b79e5c80ec912a05dbdb3009e372b7f4b0f026d16b0c663651ffc046068455d2994564ba9d4b3e9b458ad8ab5232aebbf40821a0017ad4aa2581ca6bb5fd825455e7c69bdaa9d3a6dda9bcbe9b570bc79bd55fa50889ba1466e69636b656c1911d7581cb17cb47f51d6744ad05fb937a762848ad61674f8aebbaec67be0bb6fa14853696c6c69636f6e190258021a00072f3c0e8009a1581cb17cb47f51d6744ad05fb937a762848ad61674f8aebbaec67be0bb6fa14853696c6c69636f6e1902580b5820291b4e4c5f189cb896674e02e354028915b11889687c53d9cf4c1c710ff5e4aea203815908d45908d101000033332332232332232323232323232323232323232323232323232222223232323235500222222222225335333553024120013232123300122333500522002002001002350012200112330012253350021001102d02c25335325335333573466e3cd400488008d404c880080b40b04ccd5cd19b873500122001350132200102d02c102c3500122002102b102c00a132635335738921115554784f206e6f7420636f6e73756d65640002302115335333573466e3c048d5402c880080ac0a854cd4ccd5cd19b8701335500b2200102b02a10231326353357389210c77726f6e6720616d6f756e740002302113263533573892010b77726f6e6720746f6b656e00023021135500122222222225335330245027007162213500222253350041335502d00200122161353333573466e1cd55cea8012400046644246600200600464646464646464646464646666ae68cdc39aab9d500a480008cccccccccc888888888848cccccccccc00402c02802402001c01801401000c008cd40548c8c8cccd5cd19b8735573aa0049000119910919800801801180f1aba15002301a357426ae8940088c98d4cd5ce01381401301289aab9e5001137540026ae854028cd4054058d5d0a804999aa80c3ae501735742a010666aa030eb9405cd5d0a80399a80a80f1aba15006335015335502101f75a6ae854014c8c8c8cccd5cd19b8735573aa00490001199109198008018011919191999ab9a3370e6aae754009200023322123300100300233502475a6ae854008c094d5d09aba2500223263533573805605805405226aae7940044dd50009aba150023232323333573466e1cd55cea8012400046644246600200600466a048eb4d5d0a80118129aba135744a004464c6a66ae700ac0b00a80a44d55cf280089baa001357426ae8940088c98d4cd5ce01381401301289aab9e5001137540026ae854010cd4055d71aba15003335015335502175c40026ae854008c06cd5d09aba2500223263533573804604804404226ae8940044d5d1280089aba25001135744a00226ae8940044d5d1280089aba25001135744a00226aae7940044dd50009aba150023232323333573466e1d400520062321222230040053016357426aae79400c8cccd5cd19b875002480108c848888c008014c060d5d09aab9e500423333573466e1d400d20022321222230010053014357426aae7940148cccd5cd19b875004480008c848888c00c014dd71aba135573ca00c464c6a66ae7007807c07407006c0680644d55cea80089baa001357426ae8940088c98d4cd5ce00b80c00b00a9100109aab9e5001137540022464460046eb0004c8004d5406488cccd55cf8009280c119a80b98021aba100230033574400402446464646666ae68cdc39aab9d5003480008ccc88848ccc00401000c008c8c8c8cccd5cd19b8735573aa004900011991091980080180118099aba1500233500c012357426ae8940088c98d4cd5ce00b00b80a80a09aab9e5001137540026ae85400cccd5401dd728031aba1500233500875c6ae84d5d1280111931a99ab9c012013011010135744a00226aae7940044dd5000899aa800bae75a224464460046eac004c8004d5405c88c8cccd55cf8011280b919a80b19aa80c18031aab9d5002300535573ca00460086ae8800c0444d5d080089119191999ab9a3370ea0029000119091180100198029aba135573ca00646666ae68cdc3a801240044244002464c6a66ae7004004403c0380344d55cea80089baa001232323333573466e1cd55cea80124000466442466002006004600a6ae854008dd69aba135744a004464c6a66ae7003403803002c4d55cf280089baa0012323333573466e1cd55cea800a400046eb8d5d09aab9e500223263533573801601801401226ea8004488c8c8cccd5cd19b87500148010848880048cccd5cd19b875002480088c84888c00c010c018d5d09aab9e500423333573466e1d400d20002122200223263533573801c01e01a01801601426aae7540044dd50009191999ab9a3370ea0029001100911999ab9a3370ea0049000100911931a99ab9c00a00b009008007135573a6ea80048c8c8c8c8c8cccd5cd19b8750014803084888888800c8cccd5cd19b875002480288488888880108cccd5cd19b875003480208cc8848888888cc004024020dd71aba15005375a6ae84d5d1280291999ab9a3370ea00890031199109111111198010048041bae35742a00e6eb8d5d09aba2500723333573466e1d40152004233221222222233006009008300c35742a0126eb8d5d09aba2500923333573466e1d40192002232122222223007008300d357426aae79402c8cccd5cd19b875007480008c848888888c014020c038d5d09aab9e500c23263533573802402602202001e01c01a01801601426aae7540104d55cf280189aab9e5002135573ca00226ea80048c8c8c8c8cccd5cd19b875001480088ccc888488ccc00401401000cdd69aba15004375a6ae85400cdd69aba135744a00646666ae68cdc3a80124000464244600400660106ae84d55cf280311931a99ab9c00b00c00a009008135573aa00626ae8940044d55cf280089baa001232323333573466e1d400520022321223001003375c6ae84d55cf280191999ab9a3370ea004900011909118010019bae357426aae7940108c98d4cd5ce00400480380300289aab9d5001137540022244464646666ae68cdc39aab9d5002480008cd5403cc018d5d0a80118029aba135744a004464c6a66ae7002002401c0184d55cf280089baa00149924103505431001200132001355008221122253350011350032200122133350052200230040023335530071200100500400132001355007222533500110022213500222330073330080020060010033200135500622225335001100222135002225335333573466e1c005200000d00c13330080070060031333008007335009123330010080030020060031122002122122330010040031122123300100300212200212200111232300100122330033002002001482c0252210853696c6c69636f6e003351223300248920975e4c7f8d7937f8102e500714feb3f014c8766fcf287a11c10c686154fcb27500480088848cc00400c00880050581840100d87980821a001f372a1a358a2b14f5f6
```

### Error Types

On a HTTP response with status code 400, the possible error types are shown below:

```
interface UserError {
    InvalidRequest: -1;
    NoCollateral: -2;
    InsufficientCollateral: -3;
    InsufficientFunds: -4;
    InsufficientSwap: -5;
    ExUnitsExhausted: -6;
    SizeExhausted: -7;
    MalformedTransaction: -8;
    UnsupportedAssets: -9;
    UnsupportedStrategy: -10;
}

interface ErrorResponse {
    code: UserError;
    info: string;
}
```

- `InvalidRequest` - Request inputs are malformed. Parsing did not succeed.
- `NoCollateral` - The wallet has no collateral set.
- `InsufficientCollateral` - The wallet has a collateral set but it does not contain enough value.
- `InsufficientFunds` - The wallet does not contain enough funds to build the transaction.
- `InsufficientSwap` - The wallet does not contain enough of the tokens to be used for swapping.

   This happens when the wallet needs at least N ada to pay for fees and deposits, but there are not enough swap tokens to get N ada.
- `ExUnitsExhausted` - Transaction script execution exhausted the execution units limit.
- `SizeExhausted` - Transaction size crossed the size limit.
- `MalformedTransaction` - Semantically invalid transaction CBOR supplied.
- `UnsupportedAssets` - None of the asset(s) to use for swap, as identified in the request, are supported.
- `UnsupportedStrategy` - The specified strategy (not `"default"`) was not recognized.

### API

There must be one endpoint that accepts a POST request.

```
POST /feeswap
```

With a JSON payload of the following schema:

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "strategy": {
            "type": "string"
        },
        "addresses": {
            "items": {
                "$ref": "#/definitions/types/Address"
            },
            "type": "array"
        },
        "change": {
            "$ref": "#/definitions/types/Address"
        },
        "collateral": {
            "$ref": "#/definitions/types/TransactionInput"
        },
        "swapAssets": {
            "items": {
                "$ref": "#/definitions/types/Asset"
            },
            "type": "array"
        },
        "tx": {
            "$ref": "#/definitions/types/Transaction"
        }
    },
    "required": [ "addresses", "change", "checkCollateral", "collateral", "swapAssets", "tx" ]
}
```
#### Description of the input properties

- `strategy` - A string which denotes what strategy the service should use to choose swap assets to pay for fees. There is only one strategy that all services must support: `"default"`. The exact behavior of this strategy is implementation defined. However, the strategy must guarantee that ALL transaction fees and UTxO deposits are paid for by the exclusive use of the identified swap assets. If there are not enough swap assets to _fully_ cover this, the service should return an `InsufficientSwap` error.

  The `strategy` property is optional. If unspecified, the `"default"` strategy will be used.

  The value of the `strategy` property may be `"default"` or some service-defined string.

  If the user specifieds a value for `strategy` that is unrecognized by the service, an `UnsupportedStrategy` error should be returned.
- `addresses` - Array of addresses owned by the user wallet. This can be obtained via the `getUsedAddresses` method call from any [CIP-30](https://cips.cardano.org/cip/CIP-0030) conforming wallet.
- `change` - The change address belonging to the wallet. This can be obtained via the `getChangeAddress` method call from any [CIP-30](https://cips.cardano.org/cip/CIP-0030) conforming wallet.
- `collateral` - A UTxO in the wallet that should be used as collateral for the transaction. This can be obtained via the `getCollateral` method call from any [CIP-30](https://cips.cardano.org/cip/CIP-0030) conforming wallet.
- `swapAssets` - Assets in user wallet that should be used instead of Ada to pay for transaction fees and UTxO deposits.
- `tx` - Partially balanced transaction that should be augmented with fee swapping functionalities provided by the service.

A successful response (HTTP status code 200) will return a JSON object with the following schema:

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "unsignedTx": {
            "$ref": "#/definitions/types/Transaction"
        }
    }
}
```

The returned transaction will be a modified version of the input transaction. It will be augmented with the fee swapping functionalities provided by the service. Transaction fees and UTxO deposits should be covered using one or more of the non-ada assets specified by the caller (`swapAssets`).

If the service is unable to pay for the fees and deposits using _any_ of the assets identified as swap assets, the service should return an `UnsupportedAssets` error.

A minimal example for the input payload is provided below:

```json
{
  "addresses": [
    "00e1cbb80db89e292269aeb93ec15eb963dda5176b66949fe1c2a6a38d1b930e9f7add78a174a21000e989ff551366dcd127028cb2aa39f616"
  ],
  "change": "00e1cbb80db89e292269aeb93ec15eb963dda5176b66949fe1c2a6a38d1b930e9f7add78a174a21000e989ff551366dcd127028cb2aa39f616",
  "collateral": "8282582004ffecdf5f3ced5c5c788833415bcbef26e3e21290fcebcf8216327e21569e420082583900e1cbb80db89e292269aeb93ec15eb963dda5176b66949fe1c2a6a38d1b930e9f7add78a174a21000e989ff551366dcd127028cb2aa39f6161a004c4b40",
  "position": "4293386fef391299c9886dc0ef3e8676cbdbc2c9f2773507f1f838e00043a189#1",
  "swapAssets": [
    "ff80aaaf03a273b8f5c558168dc0e2377eea810badbae6eceefc14ef.474f4c44"
  ],
  "tx": "84a70082825820975e4c7f8d7937f8102e500714feb3f014c8766fcf287a11c10c686154fcb27501825820c887cba672004607a0f60ab28091d5c24860dbefb92b1a8776272d752846574f000d818258207a67cd033169e330c9ae9b8d0ef8b71de9eb74bbc8f3f6be90446dab7d1e8bfd00018282583900fd040c7a10744b79e5c80ec912a05dbdb3009e372b7f4b0f026d16b0c663651ffc046068455d2994564ba9d4b3e9b458ad8ab5232aebbf401a1abac7d882583900fd040c7a10744b79e5c80ec912a05dbdb3009e372b7f4b0f026d16b0c663651ffc046068455d2994564ba9d4b3e9b458ad8ab5232aebbf40821a0017ad4aa2581ca6bb5fd825455e7c69bdaa9d3a6dda9bcbe9b570bc79bd55fa50889ba1466e69636b656c1911d7581cb17cb47f51d6744ad05fb937a762848ad61674f8aebbaec67be0bb6fa14853696c6c69636f6e190258021a00072f3c0e8009a1581cb17cb47f51d6744ad05fb937a762848ad61674f8aebbaec67be0bb6fa14853696c6c69636f6e1902580b5820291b4e4c5f189cb896674e02e354028915b11889687c53d9cf4c1c710ff5e4aea203815908d45908d101000033332332232332232323232323232323232323232323232323232222223232323235500222222222225335333553024120013232123300122333500522002002001002350012200112330012253350021001102d02c25335325335333573466e3cd400488008d404c880080b40b04ccd5cd19b873500122001350132200102d02c102c3500122002102b102c00a132635335738921115554784f206e6f7420636f6e73756d65640002302115335333573466e3c048d5402c880080ac0a854cd4ccd5cd19b8701335500b2200102b02a10231326353357389210c77726f6e6720616d6f756e740002302113263533573892010b77726f6e6720746f6b656e00023021135500122222222225335330245027007162213500222253350041335502d00200122161353333573466e1cd55cea8012400046644246600200600464646464646464646464646666ae68cdc39aab9d500a480008cccccccccc888888888848cccccccccc00402c02802402001c01801401000c008cd40548c8c8cccd5cd19b8735573aa0049000119910919800801801180f1aba15002301a357426ae8940088c98d4cd5ce01381401301289aab9e5001137540026ae854028cd4054058d5d0a804999aa80c3ae501735742a010666aa030eb9405cd5d0a80399a80a80f1aba15006335015335502101f75a6ae854014c8c8c8cccd5cd19b8735573aa00490001199109198008018011919191999ab9a3370e6aae754009200023322123300100300233502475a6ae854008c094d5d09aba2500223263533573805605805405226aae7940044dd50009aba150023232323333573466e1cd55cea8012400046644246600200600466a048eb4d5d0a80118129aba135744a004464c6a66ae700ac0b00a80a44d55cf280089baa001357426ae8940088c98d4cd5ce01381401301289aab9e5001137540026ae854010cd4055d71aba15003335015335502175c40026ae854008c06cd5d09aba2500223263533573804604804404226ae8940044d5d1280089aba25001135744a00226ae8940044d5d1280089aba25001135744a00226aae7940044dd50009aba150023232323333573466e1d400520062321222230040053016357426aae79400c8cccd5cd19b875002480108c848888c008014c060d5d09aab9e500423333573466e1d400d20022321222230010053014357426aae7940148cccd5cd19b875004480008c848888c00c014dd71aba135573ca00c464c6a66ae7007807c07407006c0680644d55cea80089baa001357426ae8940088c98d4cd5ce00b80c00b00a9100109aab9e5001137540022464460046eb0004c8004d5406488cccd55cf8009280c119a80b98021aba100230033574400402446464646666ae68cdc39aab9d5003480008ccc88848ccc00401000c008c8c8c8cccd5cd19b8735573aa004900011991091980080180118099aba1500233500c012357426ae8940088c98d4cd5ce00b00b80a80a09aab9e5001137540026ae85400cccd5401dd728031aba1500233500875c6ae84d5d1280111931a99ab9c012013011010135744a00226aae7940044dd5000899aa800bae75a224464460046eac004c8004d5405c88c8cccd55cf8011280b919a80b19aa80c18031aab9d5002300535573ca00460086ae8800c0444d5d080089119191999ab9a3370ea0029000119091180100198029aba135573ca00646666ae68cdc3a801240044244002464c6a66ae7004004403c0380344d55cea80089baa001232323333573466e1cd55cea80124000466442466002006004600a6ae854008dd69aba135744a004464c6a66ae7003403803002c4d55cf280089baa0012323333573466e1cd55cea800a400046eb8d5d09aab9e500223263533573801601801401226ea8004488c8c8cccd5cd19b87500148010848880048cccd5cd19b875002480088c84888c00c010c018d5d09aab9e500423333573466e1d400d20002122200223263533573801c01e01a01801601426aae7540044dd50009191999ab9a3370ea0029001100911999ab9a3370ea0049000100911931a99ab9c00a00b009008007135573a6ea80048c8c8c8c8c8cccd5cd19b8750014803084888888800c8cccd5cd19b875002480288488888880108cccd5cd19b875003480208cc8848888888cc004024020dd71aba15005375a6ae84d5d1280291999ab9a3370ea00890031199109111111198010048041bae35742a00e6eb8d5d09aba2500723333573466e1d40152004233221222222233006009008300c35742a0126eb8d5d09aba2500923333573466e1d40192002232122222223007008300d357426aae79402c8cccd5cd19b875007480008c848888888c014020c038d5d09aab9e500c23263533573802402602202001e01c01a01801601426aae7540104d55cf280189aab9e5002135573ca00226ea80048c8c8c8c8cccd5cd19b875001480088ccc888488ccc00401401000cdd69aba15004375a6ae85400cdd69aba135744a00646666ae68cdc3a80124000464244600400660106ae84d55cf280311931a99ab9c00b00c00a009008135573aa00626ae8940044d55cf280089baa001232323333573466e1d400520022321223001003375c6ae84d55cf280191999ab9a3370ea004900011909118010019bae357426aae7940108c98d4cd5ce00400480380300289aab9d5001137540022244464646666ae68cdc39aab9d5002480008cd5403cc018d5d0a80118029aba135744a004464c6a66ae7002002401c0184d55cf280089baa00149924103505431001200132001355008221122253350011350032200122133350052200230040023335530071200100500400132001355007222533500110022213500222330073330080020060010033200135500622225335001100222135002225335333573466e1c005200000d00c13330080070060031333008007335009123330010080030020060031122002122122330010040031122123300100300212200212200111232300100122330033002002001482c0252210853696c6c69636f6e003351223300248920975e4c7f8d7937f8102e500714feb3f014c8766fcf287a11c10c686154fcb27500480088848cc00400c00880050581840100d87980821a001f372a1a358a2b14f5f6"
}
```

## Rationale: how does this CIP achieve its goals?

### Standard, Easy To Use Interface

The primary goal of this CIP is to standardize an easy-to-use interface for paying transaction fees and UTxO deposits using non-Ada tokens. In an ecosystem where there may be multiple providers for such a functionality, it's important for users and dApp integrators to be able to leverage one or more of these services with minimal friction.

The CIP achieves this by documenting a simple HTTP interface with expected behavior as well as input, output, and error types. Service providers should be able to conform to these requirements and users should be able to reliably utilize their service using said interface.

### Extensible By Service Providers

The CIP also aims to make it possible for service providers to differentiate themselves by providing different supported tokens for balancing the fee swap transactions. For example, service provider A might support the non-Ada tokens T1, T2 and T3 to use for paying fees. On the other hand, service provider B might support T1, T2, T3, T4, and T5. The interface allows for service providers to choose what tokens they support, and reliably signal to the user in the case where they do not support any of the assets identified.

More interestingly, the API also has a notion of "balancing strategies". Strategies define how the identified swap assets may be used to pay for fees. For example, a strategy "least-sum-of-squares", may involve finding the best exchange rate possible for evenly using multiple identified swap assets to pay for fees.

There is only one strategy that is required for a conforming API: `"default"`.

Different services may support different strategies, which they should name and advertise. If a service supports other strategies, users can specify the strategy name when using the API connected to said service. If a strategy name is specified that the service does not support, the service may return an error as specified above.

The `"default"` strategy of each service may also be different. This could serve as an incentive for services to have "better defaults" than competitors.

## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented by one or more services.
- [ ] The interface is used by one or more dApps or wallets.
- [ ] There exists one or more client libraries that wrap the HTTP API and expose easy to use functions.

### Implementation Plan

- [ ] Provide a reference implementation for a fee swapping service.
- [ ] Provide an example of a popular dApp transaction being augmented with fee swapping utilizing said service.
- [ ] Provide a reference implementation for a client library.

### Copyright
This CIP is licensed under  [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
