# CIP Validation Rules

This document describes all validation rules applied to Cardano Improvement Proposal (CIP) documents.

These validations are run automatically via Github workflow using [`/scripts/validate-cip.py`](./scripts/validate-cip.py).

These attempt to codify the guidance described within [CIP-0001 | CIP Process](../CIP-0001/README.md).

## File-Level Validations

| Validation | Description |
| ---------- | ----------- |
| File path | Must be in a `CIP-*` directory |
| Directory name | If the `CIP` field has an assigned number (not `"?"`), the directory must be named `CIP-NNNN` where `NNNN` is the CIP number zero-padded to 4 digits (e.g., `CIP: 12` → `CIP-0012/`). Even when the number is unassigned, any directory matching `CIP-<digits>` must be zero-padded to 4 digits (e.g. `CIP-032/` fails; `CIP-0032/` passes). |
| Line endings | Must use UNIX line endings (LF), not Windows (CRLF) or old Mac (CR) |
| Frontmatter | Must have valid YAML frontmatter between `---` delimiters |
| Header line whitespace | Frontmatter lines must not have trailing whitespace |
| No unquoted `?` values | Header fields must not have a bare `?` value (e.g. `CIP: ?`); it is invalid YAML and breaks GitHub's frontmatter rendering. Use a quoted `CIP: "?"` until a number is assigned. |
| No H1 headings | H1 (`#`) headings are not allowed in the document body |
| Body cross-references | `CIP-NNNN` / `CPS-NNNN` references in the body must point to an existing folder. References with a `?` suffix (`CIP-NNNN?`) are treated as intentional references to not-yet-merged proposals and are skipped; the `?` notation is optional, not mandated. References inside fenced or inline code blocks are ignored. |

## Header Field Validations

All 9 required fields must appear in order. The `Solution To` field is optional. No other fields are allowed.

| Field | Order | Required? | Validation Rules |
| ----- | ----- | --------- | ---------------- |
| **CIP** | 1 | Yes | Positive integer (`1`, `42`) or quoted `"?"`/`"??"`/etc. for unassigned (an unquoted `?` fails — see file-level rules). No leading zeros. |
| **Title** | 2 | Yes | 1-100 characters |
| **Category** | 3 | Yes | One of: `Meta`, `Wallets`, `Tokens`, `Metadata`, `Tools`, `Plutus`, `Ledger`, `Consensus`, `Network`, `?` |
| **Status** | 4 | Yes | `Proposed`, `Active`, or `Inactive` with a required parenthetical reason (e.g., `Inactive (Superseded by CIP-NNNN)`) |
| **Authors** | 5 | Yes | Non-empty list, each entry: `Name <email>` |
| **Implementors** | 6 | Yes | List of `Name <email-or-URI>` strings (the bracketed contact may be an email address or a project URI, same shape as `Authors`), `[]` if no implementor yet, or `N/A` when not applicable |
| **Discussions** | 7 | Yes | Non-empty list, each entry: `Label: URL`. Must include at least one pull request link of the form `https://github.com/cardano-foundation/CIPs/pull/<N>`. |
| **Solution To** | (between Discussions and Created, if present) | No | Non-empty list. Each entry is `CPS-NNNN[?] [\| optional title]: URL`. The number must be zero-padded to at least 4 digits and refer to a positive number. URL must be a GitHub CIPs repository link: bare `CPS-NNNN` requires a `/tree/<branch>/CPS-NNNN` or `/blob/<branch>/CPS-NNNN` URL whose referent matches the label; `CPS-NNNN?` requires a `/pull/<N>` URL. A bare `CPS-NNNN` must point to an existing folder; a `CPS-NNNN?` must point to one that does not yet exist. |
| **Created** | 8 | Yes | Date in `YYYY-MM-DD` format |
| **License** | 9 | Yes | `CC-BY-4.0` or `Apache-2.0` |

## CIP / CPS Label Validation

For the **Discussions** field,
when an entry label matches the `CIP-NNNN` or `CPS-NNNN` pattern,
extra validation applies:

| Rule | Description |
| ---- | ----------- |
| GitHub URL required | Must be `https://github.com/cardano-foundation/CIPs/...` |
| Valid URL types | `/pull/NNN` (PR) or `/tree/{branch}/{CIP\|CPS}-NNNN` or `/blob/{branch}/{CIP\|CPS}-NNNN` (merged) |
| `?` suffix for PRs | `CIP-0030?` / `CPS-0010?` required when linking to a pull request (candidate) |
| No `?` for merged | `CIP-0030` (without `?`) required when linking to a merged document |

Non-CIP/CPS labels (e.g., `Forum Post`, `Pull Request`) are allowed with any valid URL.

The **Solution To** field applies a stricter variant of these rules: every label must be a `CPS-NNNN[?]` reference (optionally followed by ` | descriptive title`), the URL is required to be a GitHub CIPs repository link, and a bare `CPS-NNNN` must additionally match the URL referent (e.g. `CPS-0001` must link to `.../CPS-0001`). See the **Solution To** row above for the full rule.

## Required Sections (H2 Headers)

The following sections must exist in this order with **exact capitalization**.

**No other H2 sections are allowed** except the optional sections listed below.

| Order | Section |
| ----- | ------- |
| 1 | `Abstract` |
| 2 | `Motivation: Why is this CIP necessary?` |
| 3 | `Specification` |
| 4 | `Rationale: How does this CIP achieve its goals?` |
| 5 | `Path to Active` |
| 6 | `Copyright` |

### Required Path to Active Subsections (H3)

Under `Path to Active`, the following H3 subsections are required:

- `Acceptance Criteria`
- `Implementation Plan`

### Copyright Section Content

The body of the `Copyright` section must contain the abbreviation declared in the `License` header field (e.g., a `License: CC-BY-4.0` header requires the literal text `CC-BY-4.0` to appear under `## Copyright`).

## Optional Sections

The following H2 sections are allowed with exact capitalization.
They **must** appear after `Path to Active` and before `Copyright`:

- `Versioning`
- `References`
- `Appendix` / `Appendices`
- `Acknowledgments` / `Acknowledgements`

Optional sections appearing before any required section (other than `Copyright`) will cause validation to fail.

Note: `Open Questions` is a CPS-only section and is **not** allowed in CIPs. Unresolved design questions belong in the `Rationale: How does this CIP achieve its goals?` section, e.g. as an `### Open Questions` subsection.

## Link Checking (manual)

Dead-link checking is **not** part of the GitHub workflow (external link checking from CI runners is unreliable due to bot protection and rate limiting). A standalone checker is provided for authors and editors to run out-of-band:

```
python3 .github/scripts/check-links.py                  # all CIP-*/README.md and CPS-*/README.md
python3 .github/scripts/check-links.py CIP-0030         # one proposal directory
python3 .github/scripts/check-links.py --internal-only  # skip external URLs (fast)
```

It verifies that relative links point to existing files, that `#anchor` fragments match a heading in the target markdown file, and that external `http(s)` URLs respond without an error. Bot-protected (`403`) and rate-limited (`429`) responses are reported as warnings rather than failures.
