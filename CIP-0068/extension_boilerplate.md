### Extending & Modifying this CIP

> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
> NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
> "OPTIONAL" in this section are to be interpreted as described in
> [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

In order to prevent conflicting updates in the future; the addition of new asset classes following, or as part of, this
standard **MUST** be submitted as a new CIP providing their own justification, implementation, rationale, and community
review prior to official acceptance.

Newly proposed `asset_name_labels` **SHOULD NOT** be added to
[CIP-0067](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067) until the accompanying CIP has matured
through the community review and feedback stage to a point that it is considered in the `Under Review` status and is
assigned a tentative CIP number by the CIP Editors panel.

If a modification or change is deemed necessary to the asset class contained within this document which do not
fundamentally change the nature, use, or reference of the tokens; it **MAY** be submitted as a modification of this
document.

However, any change proposed that presents a non-backwards compatible change **MUST** include an accompanying `version`
field iteration and both specifications for the proposed, current, and historical versions of the format **MUST** be
maintained to assist future implementors who may encounter a version of these tokens from any point in time with the
following format:

```
#### Versions

1. [6d897eb](https://github.com/cardano-foundation/CIPs/tree/6d897eb60805a58a3e54821fe61284d5c5903764/CIP-XXXX)
2. [45fa23b](https://github.com/cardano-foundation/CIPs/tree/45fa23b60806367a3e52231e552c4d7654237678/CIP-XXXX)
3. **Current**
```

Each time a new version is introduced the previous version's link MUST be updated to match the last commit corresponding
to the previous version.

If a change is proposed that would fundamentally alter the nature of one or more of the existing
[CIP-0067](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067) `asset_name_labels` and their
associated tokens; these changes **MUST** be submitted via a new, separate CIP with its own justification, 
implementation, rationale, and community review prior to official acceptance. These separate CIPs **MUST** include a
plan for the obsolescence of any previous versions of the affected tokens. `asset_name_labels` **MUST** only be marked
obsolete once a modifying CIP achieves the `accepted` status.
