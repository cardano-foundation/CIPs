---
CIP: 1447
Title: On-chain financial transactions
Category: Metadata
Status: Proposed
Authors:
    - Thomas Kammerlocher <thomas.kammerlocher@cardanofoundation.org>
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Implementors:
    -   Reeve: https://github.com/cardano-foundation/cf-reeve-platform
Discussions:
    - 
Created: 2025-07-17
License: CC-BY-4.0
---

# Abstract

The need for transparency of organisations and legal entities continues to grow as a cornerstone of trust. This demand especially includes the need for transparency of financial transactions of these entities to prove they are fulfilling their purpose.

This Cardano Improvement Proposal (CIP) introduces a standardized method for anchoring both single financial transactions and custom organisational reports into transaction metadata, leveraging the blockchain as an immutable and publicly verifiable layer of trust. 
The proposed standard is designed to be easily intelligible, allowing auditors, stakeholders, and the public to both trace individual transactions and analyze aggregated custom reports, creating a holistic and unalterable financial picture for any entity. 
To ensure its long-term viability and adoption, the CIP also outlines a self-sustaining model to support ongoing development and maintenance of the standard, establishing Cardano as the premier infrastructure for organisational financial accountability.

# Motivation: Why this CIP is necessary?

True transparency is achieved not by merely publishing data, but by ensuring it is structured in a way that is universally understandable and interpretable for everyone.
Without a common standard, on-chain financial data remains cryptic to most, failing to build the trust it promises.

This CIP aims to provide this explanation to enable everyone to understand the financial transactions and reports of organisations and thus bringing real transparency and enhancing trust of organisations willing to share their financial data on-chain.
To achieve this, the format must be as easy as possible to read and understand for humans, while still being machine-readable to allow for automated processing.

**This readability comes with a price:** the format is not as compact as it could be, but this is a trade-off that is worth making to achieve the goal of transparency.

# Specification

This proposal defines how to structure metadata to anchor financial transactions and reports on-chain, ensuring they are both human-readable and machine-interpretable.
These metadata can be attached to any transaction. 
The target of this metadata is to ensure flexibility for organisations. Reports differ between organisations, since they have different purposes, structures, and reporting periods.
The metadata structure is designed to be extensible, allowing for future enhancements without breaking existing implementations.

## General structure

The general structure contains the base information of the organisation, the metadata version, and the type of these financial records. 
The json structure is as follows:
```json
"1447": {
    "org": {
        "id": "string", // SHA3-256 hash of <CountryCode>::<TaxIdNumber>
        "name": "string", // Name of the organisation
        "currency_id": "ISO_4217:XXX", // ISO 4217 currency code of the organisation
        "country_code": "CH" // ISO 3166-1 alpha-2 country code of the organisation
        "tax_id_number": "string" // tax identification number of the organisation
    },
    "metadata": {
        "version": "1.1" // Version of the metadata format
    },
    "type": "string", // Type of the metadata
    "data": // data object is defined through the Type of the metadata 
}
```

The type can have two values:
- `INDIVIDUAL_TRANSACTIONS`: This type is used to anchor individual financial transactions of the organisation.
- `REPORT`: This type is used to anchor a custom report of the organisation

### Individual Transactions
Additionally to the general structure the type `INDIVIDUAL_TRANSACTIONS` stores the individual transactions of the organisation within the data object.

Required fields:

| Field    | Type   | Description                                                                                                    |
|----------|--------|----------------------------------------------------------------------------------------------------------------|
| `number` | string | Unique identifier for the transaction given from the accounting system used for identifying the transaction    |
| `type`   | string | Type of the transaction (e.g., "income", "expense", "transfer")                                                |
| `date`   | string | Date of the transaction in ISO 8601 format (YYYY-MM-DD)                                                        |
| `items`  | array  | Array of items in the transaction, each item can have additional fields like event, project, cost center, etc. |

Additional fields can be added to the data object, such as accounting period, custom id, etc.

Items are the individual financial entries within the transaction. Each item can have the following fields:

| Field          | Type   | Description                                                                                                       |
|----------------|--------|-------------------------------------------------------------------------------------------------------------------|
| `id`           | string | Unique identifier for the item, e.g., a unique identifier from the accounting system                              |
| `amount`       | string | Amount of the transaction item, represented as a string to allow for large numbers and decimal precision          |
| `fx_rate`      | string | Foreign exchange rate if applicable, represented as a string to allow for decimal precision                       |
| `document`     | object | Document details related to the transaction item, can include number, currency, event, project, cost center, etc. |
| `event`        | object | Optional event details related to the transaction item, can include code and name                                 |
| `project`      | object | Optional project details related to the transaction item, can include cust_code and name                          |
| `cost_center`  | object | Optional cost center details related to the transaction item, can include cust_code and name                      |
| `vat`          | object | Optional VAT details related to the transaction item, can include cust_code and rate                              |
| `counterparty` | object | Optional counterparty details related to the transaction item, can include cust_code and type                     |

Example json
```json
{
  <General structure>,
  "type": "INDIVIDUAL_TRANSACTIONS",
  "data": [
    {
      "number": "Transaction123", 
      "type": "JOURNAL",
      "date": "2025-01-01",
      "accounting_period": "2025-12",
      "items": [
        {
          "id": "UniqueIdentifier123",
          "amount": "2874",
          "fx_rate": "0.93",
          "document": {
            "number": "JE-5810",
            "currency": {
              "id": "ISO_4217:EUR",
              "cust_code": "EUR"
            }
          },
          "cost_center": {
            "cust_code": "1000",
            "name": "Internal Operations"
          }
        }
      ]
    }
  ]
}
```

### Report
The type `REPORT` is used to publish reports of organisation. These reports can be highly customized resulting in the need for a flexible and adjustable structure. 

Required fields:

| Field       | Type                        | Description                                                                                                                                                            |
|-------------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `interval`  | string                      | The reporting interval, e.g., "YEARLY", "QUARTERLY", "MONTHLY", etc.                                                                                                   |
| `year`      | string                      | The year of the report, e.g., "2025".                                                                                                                                  |
| `period`    | integer                     | The period of the report according to the interval, e.g., if Monthly 1 for January, 2 for February, etc.                                                               |
| `subtype`   | string                      | Definition of what of the report type - Organisations can have custom reports, e.g., "BALANCE_SHEET", "INCOME_STATEMENT"                                               |
| `data`      | anyOf [string, data object] | The actual report data, which can be highly customized and structured according to the organisation's needs. This object should repesent categories and subcategories. |

#### Example json:

```json
{
  <General structure>,
  "type": "REPORT",
  "interval": "MONTHLY",
  "year": "2025",
  "period": 12,
  "subtype": "BALANCE_SHEET",
  "data": {
    "assets": {
      "current_assets": {
        "cash": "1000"
      },
      "non_current_assets": {
        "property": "5000"
      }
    },
    "liabilities": {
      "current_liabilities": {
        "accounts_payable": "200"
      },
      "non_current_liabilities": {
        "long_term_debt": "1000"
      }
    }
  }
}
```

# Glossary
Since some terms within this CIP require specific definitions to ensure clarity and consistency, the following glossary is provided:
- **Cost Center**: A department or function within an organization that incurs costs but does not directly generate profit (e.g., the IT or Human Resources department). It is used for internal cost tracking.
- **Counterparty**: The other party that participates in a financial transaction. For example, in a sales transaction, the customer is the counterparty to the seller.
- **Foreign Exchange (FX) Rate**: The rate at which one currency can be exchanged for another. It is used when a transaction involves multiple currencies.
- **Value-Added Tax (VAT)**: A consumption tax placed on a product whenever value is added at each stage of the supply chain, from production to the point of sale.
- **Document**: A formal record of a transaction, which can include invoices, receipts, or other financial documents that provide evidence of the transaction.