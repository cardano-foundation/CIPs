---
CIP: 34
Title: Smart Contract Software Licensing
Authors: Pi Lanningham <pi@sundaeswap.finance>
Comments-URI:
Status: Draft
Type: Informational
Created: 2022-01-03
Post-History: 
License: CC-BY-4.0
---

## Abstract

This proposal defines a metadata standard for specifying the license for a smart contract.

## Motivation

Smart contracts, specified in source code or compiled to raw bytecode as presented on the blockchain, are creative and often highly valuable works and are often subject to legal licensing concerns.  It is important that companies building on Cardano have the ability to link their smart contracts unambiguously to the license.

This standard allows such a dApp builder to specify in the metadata of a transaction a reference to the license for each script.

Ensuring that there is a consistent way to do this will have a number of benefits:
 - Explorer projects, such as CardanoScan, can be updated to show the script license before showing the bytecode
 - Projects have legal recourse against outright, low-effort forks of their projects (such as the Sushiswap / Uniswap fiasco)
 - In theory, parts of the ecosystem could (at their discretion) choose to honor these licenses, and refuse to interoperate with projects that violate the license; A DEX, for example, could justify excluding a token on the basis of violation of an appropriate software license.

Ultimately, the above encourages and fosters a more Open and collaborative Cardano.  With some confidence that their license-restricted code won't be copied outright, projects can feel more comfortable open-sourcing more of their intellectual property for the sake of knowledge sharing and innovation, with the risk of a whole-sale copy mitigated.

## Specification

This is the proposed `transaction_metadatum_label` value

| transaction_metadatum_label | description            |
| --------------------------- | ---------------------- |
| 1998                        | Smart Contract License |

This value is chosen as it is unused, and because it is the year that the [Open Source Initiative was founded](https://opensource.org/history).

### Structure

The structure allows for multiple smart contracts, also with different licenses, in a single transaction.  It also allows specifying licenses for only a subset of the contracts.

```
{
  "1998": {
    "<contract_address>": {
      "uri": "https://...",
      "osi": "MIT"
      "sha256": "..."
      <other_properties>
    }
    "version": "1.0"
  }
}
```

One of either **`uri`** or **`osi`** MUST be provided.

**`uri`** is an RFC-3986 / RFC-2397 Universal Resource Identifier pointing to the contents of the license.  This MAY be, for example, hosted on a companies website, or stored in IPFS.

**`osi`** MUST be an OSI approved license name or SPDX identifier.  The current list can be found [here.](https://opensource.org/licenses/alphabetical)

The **`sha256`** property is optional, and if provided MUST be the sha256 hash of the contents of the license.  This allows you to provide evidence that the license hasn't been changed.

This structure defines a forward compatible basis. New properties and standards can be defined in the future if needed.

## Backward Compatibility

To keep this metadata compatible with changes in the future, we use the **`version`** property. Version `1.0` is used in the current metadata structure of this CIP.

## References

- CIP about reserved labels: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010
- URI: https://tools.ietf.org/html/rfc3986, https://tools.ietf.org/html/rfc2397
- Open Source Initiative https://opensource.org/
- OSI Licenses https://opensource.org/licenses/alphabetical
- Heavy inspiration from CIP-0025: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
