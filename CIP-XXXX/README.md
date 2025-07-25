---
CIP: 158
Title: Cardano URIs - Browse Application
Category: Wallets
Status: Proposed
Authors:
    - Adam Dean <adam@crypto2099.io>
Implementors:
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1058
Created: 2025-07-17
License: CC-BY-4.0
---

## Abstract

This CIP proposes a new URI scheme authority, `browse`, under `web+cardano` to
enable Cardano wallets to launch external or embedded applications and dApps
with full path and context, using a standardized, interoperable URI format.

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

## Specification

### URI Format

```
web+cardano://browse/<scheme>/<namespaced_domain>/<app-specific-path>?<parameters>
```

* **Authority (REQUIRED):** `browse`
* **Scheme (REQUIRED):** `https`, `http`, `ipfs`, etc.
* **Namespaced domain (REQUIRED):** reverse domain name (e.g., `fi.sundae.app`)
* **App-specific path (OPTIONAL):** full path within the app
* **Query parameters (OPTIONAL):** optional, passed as-is to the app

### Example URIs

* Web app (SundaeSwap ADA <=> USDM Trading Page):

  ```
  web+cardano://browse/https/fi.sundae.app/exchange?given=ada.lovelace&taken=c48cbb3d5e57ed56e276bc45f99ab39abe94e6cd7ac39fb402da47ad.0014df105553444d&routeIdent=64f35d26b237ad58e099041bc14c687ea7fdc58969d7d5b66e2540ef
  ```

* IPFS app (simulated CID):

  ```
  web+cardano://browse/ipfs/QmXkYpAbC1234567890abcdef1234567890abcdef/actionPage
  ```

* Local development app (HTTP localhost with port):

  ```
  web+cardano://browse/http/localhost:3000/devPage
  ```

### ABNF Grammar

``` 
cardano-browse-uri = "web+cardano:" browse-path

browse-path = "//browse" "/" scheme "/" namespaced-domain [ "/" app-path ] [ query ]
scheme = ALPHA *( ALPHA / DIGIT / "." / "+" / "-" )
namespaced-domain = *( ALPHA / DIGIT / "." / "-" )
app-path = *( unreserved / pct-encoded / sub-delims / "/" )
query = "?" *( unreserved / pct-encoded / sub-delims / "=" / "&" )
```

### Wallet Behavior

* Parse and validate scheme and domain.
* Forward the entire app-specific path and query string to the app.
* Apply allowlist/blocklist and security policies:

    * Warn on `http` and `localhost`.
    * Allow `https` by default.
    * Resolve `ipfs` via trusted gateway or native resolver.

### Security Considerations

* Wallets SHOULD prompt users before launching non-allowlisted or unsafe
  schemes.
* Wallets cannot automatically determine whether query parameters contain
  sensitive or user-specific data; app developers are responsible for ensuring
  that no long-lived secrets or sensitive information are embedded in shared
  links.
* Wallets SHOULD provide clear UI to inform users of the destination and allow
  cancellation before proceeding.
* dApp developers SHOULD design links and query parameters with privacy and
  security in mind, using short-lived or ephemeral tokens where needed and
  avoiding embedding sensitive user data.

## Rationale: how does this CIP achieve its goals?

A dedicated `browse` authority isolates app navigation and launch intents from
payment or metadata intents, improving clarity and interoperability.

### Why use reverse domain names for `namespaced_domain`

* **Global uniqueness:** avoids collisions.
* **Decentralized management:** no central registry needed.
* **Developer familiarity:** matches Android, Apple, Java ecosystems.
* **Verifiability:** can tie domains to apps via `.well-known` or DNS records.
* **Cross-platform compatibility:** works on web, mobile, desktop.

### Why include scheme in the path

* Removes ambiguity — scheme is required, not optional.
* Supports alternative protocols (IPFS, local dev) explicitly.
* Simplifies wallet parsing — no need to extract from query params.

## Path to Active

### Acceptance Criteria

- [ ] At least one major Cardano wallet implements support for the browse
  authority in web+cardano URIs, including launching its embedded browser with
  the specified path.
- [ ] At least one dApp publishes deep links or QR codes using the browse scheme
  that work reliably across supported wallets.
- [ ] Demonstrated user success in navigating from mobile device (e.g., native
  camera or link) into a wallet and then directly into the dApp or application
  flow.
- [ ] Positive feedback or validation from the community or wallet/dApp
  developers confirming interoperability.

### Implementation Plan

- [ ] Publish and socialize the CIP draft for feedback from wallet and dApp
  developers.
- [ ] Develop a reference implementation or demo prototype showing browse URI
  handling in at least one wallet.
- [ ] Collaborate with at least one dApp team to generate example deep links and
  test them live (e.g., at events or with public beta testers).
- [ ] Write integration guides or example code for wallet and dApp developers.
- [ ] Monitor ecosystem adoption and collect feedback for potential refinements
  or amendments to the standard.

## Copyright

This CIP is licensed
under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).