---
CIP: 158
Title: Cardano URIs - Browse Application
Category: Wallets
Status: Proposed
Authors:
Authors:
    - Adam Dean <adam@crypto2099.io>
    - Alex Dochioiu (VESPR Wallet) <alex@vespr.xyz> 
Implementors:
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1058
Created: 2025-07-17
License: CC-BY-4.0
---

## Abstract

This CIP proposes a new URI scheme authority, `browse`, under `web+cardano` to
enable Cardano wallets to launch external or embedded applications and dApps
with the full path and context, using a standardized, interoperable URI format.

## Motivation: why is this CIP necessary?

Today, exploring dApps on Cardano — especially on mobile devices — is
cumbersome. Most Cardano wallets with embedded browsers require users to
manually launch the wallet, open its browser, and type or paste full URLs to
reach specific applications. This creates significant friction, particularly in
real-world scenarios like:

* Trade shows or events promoting dApps
* Point-of-sale terminals or vending machines using Cardano
* Marketing campaigns linking directly to dApp actions

The goal of this CIP is to introduce a **deep-linking compatible method** that
lets dApps and external actors provide QR codes or clickable links that:

* Open the user’s preferred wallet automatically (via `web+cardano` handler)
* Direct the wallet to launch its embedded browser or app view
* Navigate directly to the intended dApp page or state without manual user input

This reduces friction, improves dApp discoverability, and creates a smoother
experience for both developers and end-users, particularly in mobile and
cross-device contexts.

### Security Benefits & Considerations

The existing process for transferring sessions and information between devices
or from physical to digital is fraught with opportunity for accidents, errors,
and malicious interception.

Existing standards for `web+cardano://` URIs describe some rudimentary
interactions that may be automated by following the specification such as
sending payment or claiming airdrops. However, no current standards exist to
easily point a mobile user to a complex application that requires smart contract
interaction (for example).

By defining this standard to instantly transport the user from a browser or
QR-based "deeplink" to a precise session or page within an application, we
enable developers to build richer, safer and more interactive experiences such
as:

* Showing a full "checkout" process and later "receipt" to the user on their
  mobile device rather than simply a payment request out of context
* Navigating users directly to complex application paths that would otherwise be
  prone to user data-entry errors and typos

## Specification

### URI Format

```
web+cardano://browse/<version>?uri=<percent_encoded_uri>
```

* **authority (REQUIRED):** `browse`
* **version (REQUIRED):** `v1`
* **percent_encoded_uri (REQUIRED):** percent-encoded URI (only `http` and `https` scheme is supported. If no scheme is defined, `https` scheme is assumed)

### Versioning

This document describes `Version 1` of this specification. Once this CIP is
merged and canonized as `Accepted` this `Version 1` should no longer be modified
to avoid potentially introducing breaking changes with legacy integrations.

Instead, those seeking to amend, extend, or modify the `browse` authority should
introduce a new CIP that iterates this standard and increments the Version
Number by a single whole integer value (i.e., the next CIP will be `Version 2`).

Extensions to this standard should follow whatever accepted criteria exist at
the time of their authoring in terms of acceptance and adoption.

### Example URIs

Web app (SundaeSwap ADA <=> USDM Trading Page):

```
web+cardano://browse/v1?uri=https%3A%2F%2Fapp.sundae.fi%2Fexchange%3Fgiven%3Dada.lovelace%26taken%3Dc48cbb3d5e57ed56e276bc45f99ab39abe94e6cd7ac39fb402da47ad.0014df105553444d%26routeIdent%3D64f35d26b237ad58e099041bc14c687ea7fdc58969d7d5b66e2540ef
```

Local development app (HTTP localhost with port):

```
web+cardano://browse/v1?uri=http%3A%2F%2Flocalhost%3A3000%2FdevPage
```

### Wallet Behavior

* Parse and validate version, scheme, and domain.
* Forward the entire app-specific path and query string to the app.
* Suggested allowlist/blocklist and security policies:
    * Each wallet may optionally implement its own allowed list of trusted domains where navigation would not require explicit permissions
    * Each wallet may optionally implement a blacklist of known untrusted domains where the user would be shown a clear warning that the website is known to be malicious. With very explicit user permission user should still be allowed to navigate.
    * For domains outside of allowlist / blacklist, wallet may want to show a warning and request explicit permission before navigating. This is to prevent unwanted IP / device info / other data exfiltration which can be obtained simply by loading a webpage

### Security Considerations

* Wallets SHOULD prompt users before launching non-allowlisted or unsafe
  schemes.
* Wallets cannot automatically determine whether query parameters contain
  sensitive or user-specific data; app developers are responsible for ensuring
  that no long-lived secrets or sensitive information are embedded in shared
  links.
* Wallets SHOULD provide a clear UI to inform users of the destination and allow
  cancellation before proceeding.
* dApp developers SHOULD design links and query parameters with privacy and
  security in mind, using short-lived or ephemeral tokens where needed and avoid
  embedding sensitive user data.

## Rationale: how does this CIP achieve its goals?

A dedicated `browse` authority isolates app navigation and launch intents from
payment or metadata intents, improving clarity and interoperability.

## Path to Active

### Acceptance Criteria

- [ ] At least one major Cardano wallet implements support for the browse
  authority in web+cardano URIs, including launching its embedded browser with
  the specified path.
  that work reliably across supported wallets.
- [ ] Demonstrated user success in navigating from mobile device (e.g., native
  camera or link) into a wallet and then directly into the dApp or application
  flow.
- [ ] Positive feedback or validation from the community or wallet/dApp
  developers confirming interoperability.

### Implementation Plan

- [X] Publish and socialize the CIP draft for feedback from wallet and dApp
  developers.
- [X] Develop a reference implementation or demo prototype showing browse URI
  handling in at least one wallet.
    - Reference Implementation: https://github.com/crypto2099/cardano-uri-parser
    - NPM Package: https://www.npmjs.com/package/cardano-uri-parser
- [ ] Collaborate with at least one dApp team to generate example deep links and
  test them live (e.g., at events or with public beta testers).
- [ ] Write integration guides or example code for wallet and dApp developers.
- [ ] Monitor ecosystem adoption and collect feedback for potential refinements
  or amendments to the standard.

## Copyright

This CIP is licensed
under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).