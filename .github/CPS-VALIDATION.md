# CPS Validation Rules

This document describes all validation rules applied to Cardano Problem Statement (CPS) documents.

These validations are to be ran automatically via Github workflow using [`/scripts/validate-cps.py`](./scripts/validate-cps.py).

These attempt to codify the guidance described within [CIP-9999 | Cardano Problem Statements](../CIP-9999/README.md).

## File-Level Validations

| Validation | Description |
| ---------- | ----------- |
| File path | Must be in a `CPS-*` directory |
| Line endings | Must use UNIX line endings (LF), not Windows (CRLF) or old Mac (CR) |
| Frontmatter | Must have valid YAML frontmatter between `---` delimiters |
| No H1 headings | H1 (`#`) headings are not allowed in the document body |

## Header Field Validations

All 9 fields are **required**,
must appear in order,
and no extra fields are allowed.

| Field | Order | Validation Rules |
| ----- | ----- | ---------------- |
| **CPS** | 1 | Positive integer (`1`, `42`) or `?`/`??`/etc. for unassigned |
| **Title** | 2 | 1-100 characters, no backticks (`` ` ``) |
| **Category** | 3 | One of: `Meta`, `Wallets`, `Tokens`, `Metadata`, `Tools`, `Plutus`, `Ledger`, `Consensus`, `Network`, `?` |
| **Status** | 4 | `Open`, `Solved`, or `Inactive` (optionally with reason, e.g., `Inactive (Superseded)`) |
| **Authors** | 5 | Non-empty list, each entry: `Name <email>` |
| **Proposed Solutions** | 6 | List (can be empty), each entry: `Label: URL` |
| **Discussions** | 7 | Non-empty list, each entry: `Label: URL` |
| **Created** | 8 | Date in `YYYY-MM-DD` format |
| **License** | 9 | `CC-BY-4.0` or `Apache-2.0` |

## CIP Label Validation

For the **Proposed Solutions** and **Discussions** fields,
when an entry label matches the `CIP-NNNN` pattern,
extra validation applies:

| Rule | Description |
| ---- | ----------- |
| GitHub URL required | Must be `https://github.com/cardano-foundation/CIPs/...` |
| Valid URL types | `/pull/NNN` (PR) or `/tree/{branch}/CIP-NNNN` or `/blob/{branch}/CIP-NNNN` (merged) |
| `?` suffix for PRs | `CIP-0030?` required when linking to a pull request (candidate) |
| No `?` for merged | `CIP-0030` (without `?`) required when linking to a merged CIP |

Non-CIP labels (e.g., `Forum Post`, `Pull Request`) are allowed with any valid URL.

## Required Sections (H2 Headers)

The following sections must exist in this order with **exact capitalization**.

**No other H2 sections are allowed** except the optional sections listed below.

| Order | Section |
| ----- | ------- |
| 1 | `Abstract` |
| 2 | `Problem` |
| 3 | `Use Cases` |
| 4 | `Goals` |
| 5 | `Open Questions` |
| 6 | `Copyright` |

## Optional Sections

The following sections are allowed with exact capitalization.
They can appear after `Open Questions`:

- `References`
- `Appendices`
- `Acknowledgments` / `Acknowledgements`
