---
CIP: 186
Title: Cardano Wallet Deep-Link Signing
Category: Wallets
Status: Proposed
Authors:
    - Nathaniel "decimalist" Minton (Flux Point Studios) <nathanielminton@fluxpointstudios.com>
Implementors: []
Discussions:
    - Forum thread: https://forum.cardano.org/t/cip-proposal-mobile-deep-link-signing-for-native-dapps-cip-30-extension/154561
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1189
Solution To:
    - CPS-0010 | Wallet Connectors: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0010
Created: 2026-05-13
License: CC-BY-4.0
---

## Abstract

This proposal defines a deep-link wire protocol that lets a native mobile application (the *dApp*) ask an
installed Cardano wallet (the *wallet*) to perform CIP-30 operations &mdash; chiefly `signTx` and `signData` &mdash;
over the operating system's URL-handling mechanism, with no relay server, embedded WebView, QR code, or
WebSocket. The protocol layers a small set of request-response endpoints onto a single namespaced URI
prefix (`https://<wallet-domain>/cip30dl/v1/...`, with `cip30dl:` as a platform fallback), pairs the dApp
and wallet with an ephemeral X25519 key exchange, binds every signing request to a BLAKE2b-256 commit
over the canonical transaction body so the dApp can verify *which* transaction was signed, and returns
the witness set via a universal-link callback. The spec is profiled for iOS (Universal Links preferred,
custom scheme fallback) and Android (App Links plus Intent disambiguation). It is a strict subset of
CIP-30's method surface so wallets can reuse their existing signing UI.

## Motivation: Why is this CIP necessary?

[CPS-0010](https://cips.cardano.org/cps/CPS-0010) ("Wallet Connectors", Open) documents that
[CIP-30](https://cips.cardano.org/cip/CIP-30) is a JavaScript-injection contract over a shared browser
`window` object. CPS-0010 specifically calls out the resulting limitation (CPS-0010:124-130):
"The CIP-30 connection standard is based upon injecting code into shared web windows. ... mobile
wallets are thus required to reimplement web browsers in their applications, which is wasted effort.
... non-web-based wallets (and their users) are unable to utilize the benefits of Cardano's web3."
CPS-0010 also notes the API is "Language Dependent" because "CIP-30's connection standard and API is
defined using Typescript" (CPS-0010:118-122) &mdash; friction for any non-JS stack. Our deep-link
transport is language-agnostic (URLs over OS handlers) and resolves both: a Swift, Kotlin, Flutter,
or React-Native dApp can speak CIP-30-DeepLink without a single line of JavaScript or an embedded
browser. That model presupposes either (a) a browser extension or (b) a wallet-controlled
in-app WebView. Both options are hostile to the *mobile-native dApp* shape:

- Mobile-native dApps (React Native, Capacitor, Flutter, Swift, Kotlin) do not run inside a wallet's
  WebView. They run inside their own app sandbox.
- Embedding a wallet's WebView inside the dApp inverts the security model: the dApp can now intercept
  seeds and keystrokes.
- [CIP-45](https://cips.cardano.org/cip/CIP-45) (WebRTC + WebTorrent tracker, Active) replaces a
  central relay with a decentralised peer-discovery layer (CIP-45:42-67), but the data channel is
  still a long-lived WebRTC session that requires both peers to be online concurrently.
  WalletConnect requires a relay outright; relays add latency, a third-party dependency, an attack
  surface, and &mdash; empirically &mdash; failure modes (WalletConnect monorepo issue #1165
  documents recurring iOS deep-link UX regressions even *with* a relay). CIP-30-DeepLink is one-shot
  per signature with no concurrent online requirement; CIP-45 and CIP-30-DeepLink are therefore
  complementary, not competitive (CIP-45 for cross-device persistent channel; CIP-30-DeepLink for
  same-device one-shot).
- The status quo for a mobile-native Cardano dApp that wants a "Sign with Lace" button is: there is no
  documented path. Builders either ship an embedded WebView, fork CIP-30, or hand-roll a deep link
  with no security guarantees.

Other ecosystems have shipped solutions to this exact problem and are battle-tested on iOS and Android:

| Spec / Wallet              | Scheme                              | Encryption           | Callback                                |
|----------------------------|-------------------------------------|----------------------|-----------------------------------------|
| Cardano CIP-45             | `web+cardano://connect/v1?identifier=` | none in identifier; WebRTC channel may use DTLS | WebRTC RPC over peer-discovered channel |
| EIP-681 (Ethereum payment) | `ethereum:<addr>?value=...`         | none (URI only)      | none (one-way URI)                      |
| EIP-831 (URI envelope)     | `ethereum:[prefix-]<payload>`       | none                 | none                                    |
| BIP-21 (Bitcoin)           | `bitcoin:<addr>?amount=...`         | none                 | none                                    |
| Solana MWA 2.0             | `solana-wallet:/v1/associate/...`   | P-256 ECDH + WS TLS  | WebSocket (local) / reflector (remote)  |
| Phantom Deeplinks          | `https://phantom.app/ul/v1/...`     | NaCl box (X25519)    | Universal-link redirect, encrypted body |
| Petra (Aptos)              | `petra://api/v1/...`                | NaCl box (X25519)    | Custom-scheme redirect, encrypted body  |
| LNURL / BIP-21+lightning   | `lightning:<bech32 payload>`        | none (bech32 only)   | callback URL embedded in payload        |

Reference URLs:

- [Phantom Deeplinks documentation](https://docs.phantom.com/phantom-deeplinks)
- [Petra (Aptos) Mobile Deep Links](https://petra.app/docs/mobile-deeplinks)
- [Aptos Wallet Adapter (Aptos Wallet Standard)](https://github.com/aptos-labs/aptos-wallet-adapter)
- [Solana Mobile Wallet Adapter (MWA) 2.0 specification](https://solana-mobile.github.io/mobile-wallet-adapter/spec/spec.html)

The Solana MWA team's published guidance treats iOS deep-linking as *flawed for high-throughput dApps*
and recommends Safari Web Extensions instead. That guidance is correct for high-frequency game-style
dApps but wrong for the dominant Cardano use case (insurance, lending, governance, DEX) which signs a
transaction at most every few minutes. For those use cases, the Phantom/Petra deep-link pattern is
both shipped and successful: Phantom on iOS handles millions of signing flows per month using exactly
the pattern this CIP proposes to standardise.

This proposal does not replace CIP-30. It is a transport profile for CIP-30's *methods* over a
deep-link URI rather than over `window.cardano`. A wallet that implements both CIP-30 and
CIP-30-DeepLink can serve browser-extension dApps, WebView dApps, *and* mobile-native dApps with one
signing engine.

## Specification

### Conformance language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
[RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) when, and only when, they appear in all
capitals.

### Terminology

- *dApp* &mdash; the initiating application, running natively on iOS or Android.
- *Wallet* &mdash; the responding application, holding the user's signing keys.
- *Session* &mdash; an authorised pairing between dApp and wallet, established by `connect` and torn down
  by `disconnect`.
- *Commit* &mdash; `BLAKE2b-256(canonical-cbor(tx_body))`, the canonical 32-byte identifier of the
  transaction the user is signing. This is identical to `tx_id` on Cardano and SHOULD be re-derivable
  by the dApp from the locally held CBOR. BLAKE2b is defined by
  [RFC 7693](https://datatracker.ietf.org/doc/html/rfc7693). The `canonical-cbor` encoding follows
  [RFC 8949 §4.2 "Core Deterministic Encoding"](https://datatracker.ietf.org/doc/html/rfc8949#section-4.2)
  (definite-length items, sorted maps, canonical numeric forms). Cardano nodes use this same encoding
  to compute `tx_id`; any deviation will produce a `commit` that does not match the chain's
  transaction identifier and the tx will be rejected at submit time.
- `tx_body` &mdash; the inner CBOR map of a Conway-era Cardano transaction, extracted per the rule in
  *Specification &sect; Conway transaction body extraction* below.

### URI format

Every CIP-30-DeepLink interaction is a single HTTPS URL (Universal Link / App Link) or &mdash; only as a
platform-specific fallback &mdash; a custom-scheme URL. Conforming wallets MUST register both of the
following:

```text
HTTPS form (preferred):        https://<wallet-domain>/cip30dl/v1/<method>?<params>
Custom-scheme form (fallback): cip30dl-<wallet-id>:/v1/<method>?<params>
```

`<wallet-domain>` is a hostname owned by the wallet vendor. The wallet-domain is the runtime-
authoritative anchor for a wallet's CIP-30-DeepLink identity: the vendor MUST serve, under
well-known paths on that domain, both its platform association documents &mdash;
`apple-app-site-association` (iOS) and `/.well-known/assetlinks.json` (Android), claiming the path
prefix `/cip30dl/` &mdash; and its vendor-attestation document
`/.well-known/cip30dl-attestation.json` (*Security model &sect; Vendor attestation manifest*). dApps
MUST resolve a wallet's protocol commitments from these origin-anchored documents at runtime rather
than from any central list. `<wallet-id>` is a lowercase ASCII name (`lace`, `eternl`, `vespr`, ...)
that MUST equal the `wallet_id` field of the attestation document served on `<wallet-domain>`; it
also appears in the advisory `wallet-registry.json` catalogued in Appendix B, which is a
non-normative convenience list only.

**Per-wallet custom schemes (security-critical).** Every wallet that implements CIP-30-DeepLink MUST
declare its custom scheme as `cip30dl-<wallet-id>:` rather than a shared `cip30dl:` namespace. On iOS,
multiple apps claiming the same custom scheme produce non-deterministic resolution (most-recent-
install-wins, silently), which is a well-documented hijack vector ([Temu Universal-Link AASA hijack
case](https://medium.com/@m.habibgpi/universal-link-hijacking-via-misconfigured-aasa-file-on-temu-com-eadfcb745e4e),
[Lauritz Holtmann &mdash; Android App Links autoVerify hijack](https://security.lauritz-holtmann.de/post/sso-android-autoverify/)).
Embedding `<wallet-id>` in the scheme itself eliminates the namespace collision: only the specific
wallet vendor can register `cip30dl-lace:` or `cip30dl-eternl:` etc. The HTTPS form MUST be attempted
first by dApps. The custom-scheme form is used only when the HTTPS form fails to launch (iOS will
degrade silently if the wallet is not installed; the dApp SHOULD detect non-launch via a 2-second
timer and fall back).

Augmented BNF for the URI, defined per
[RFC 5234 (ABNF)](https://datatracker.ietf.org/doc/html/rfc5234) and reusing the `pct-encoded` and
`unreserved` productions from [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986):

```abnf
cip30dl-uri      = https-form / scheme-form
https-form       = "https://" wallet-domain "/cip30dl/v1/" method "?" param-list
scheme-form      = "cip30dl-" wallet-id ":/v1/" method "?" param-list

wallet-domain    = 1*( ALPHA / DIGIT / "-" / "." )
wallet-id        = 1*( ALPHA / DIGIT / "-" )

method           = "connect" / "disconnect" / "signTx" / "signData"
                 / "getUsedAddresses" / "getUnusedAddresses"
                 / "getRewardAddresses" / "getNetworkId"
                 / "getPubDRepKey"                        ; CIP-95, governance wallets
                 / "getRegisteredPubStakeKeys"            ; CIP-95, governance wallets
                 / "getUnregisteredPubStakeKeys"          ; CIP-95, governance wallets
                 / "submitTx"        ; OPTIONAL

param-list       = param *( "&" param )
param            = key "=" value
key              = request-key / response-key
request-key      = "v" / "dapp" / "dappKey" / "redirect"
                 / "nonce" / "commit" / "session"
                 / "payload" / "chain" / "ttl" / "page"
                 / "aead"
response-key     = "response" / "walletKey" / "nonce" / "payload"
                 / "signature" / "method" / "echo"
                 / "errorCode" / "errorMessage"

value            = 1*( unreserved / pct-encoded )
unreserved       = ALPHA / DIGIT / "-" / "." / "_" / "~"
pct-encoded      = "%" HEXDIG HEXDIG
```

All `value`s are percent-encoded. Binary fields (keys, nonces, ciphertext, commit) are
base64url-encoded ([RFC 4648 Section 5](https://datatracker.ietf.org/doc/html/rfc4648#section-5),
no padding) before percent-encoding. Hex is NOT used; base64url shortens URIs by roughly 25%
which matters because iOS Safari enforces a practical 8 KB URL ceiling.

**base64url strict-decode rule.** Implementations MUST use a strict base64url decoder that rejects:
(a) inputs containing characters outside the base64url alphabet (`A-Z`, `a-z`, `0-9`, `-`, `_`); (b)
inputs containing padding (`=`) characters; (c) inputs whose final 6-bit group has non-zero
unused-bit content (per [RFC 4648 Section 3.5](https://datatracker.ietf.org/doc/html/rfc4648#section-3.5)
on canonical decoding). Permissive decoders allow signature-malleability where two distinct base64url
strings decode to the same bytes; this defeats the response-signing layer's authenticity guarantee.

### Relationship to CIP-13 `web+cardano:` URI scheme

[CIP-13](https://cips.cardano.org/cip/CIP-13) ("Cardano URI Scheme", Proposed) defines the
`web+cardano:` URI family and its grammar (CIP-13:85-90):
`cardanouri = "web+cardano:" (paymentref | authorityref)`. CIP-13 is explicitly extensible by
subsequent CIPs declaring new authorities, as done by [CIP-162](https://cips.cardano.org/cip/CIP-162)
for the `drep` authority, [CIP-45](https://cips.cardano.org/cip/CIP-45) for the `connect` authority
(CIP-45:91-99 uses `web+cardano://connect/v1?identifier=<public_key>`), and
[CIP-158](https://cips.cardano.org/cip/CIP-158) for the `browse` authority
(`web+cardano://browse/v1?uri=<percent_encoded_uri>`, navigation-only and explicitly out of scope
for signing flows or callback paths per CIP-158's own Rationale). These authorities &mdash; together
with the `null`, `stake`, `claim`, `transaction`, `block`, and `addr` authorities catalogued
elsewhere &mdash; are coordinated through
[CPS-16](https://cips.cardano.org/cps/CPS-16) ("Cardano URIs", Open), authored by Adam Dean and
Mad Orkestra to serve as the central reference and collision-prevention registry for emerging
`web+cardano://` authority registrations.

CIP-30-DeepLink does NOT adopt a `web+cardano://<authority>` form for its primary URI. The reason
is operational: a single shared `web+cardano:` scheme has every wallet vendor competing for the
same OS protocol-handler claim, which causes the OS to prompt the user with a wallet-chooser dialog
on every link click. The deep-link payload of a CIP-30-DeepLink request must route deterministically
to ONE named wallet (the wallet the dApp's `connect` flow paired with), not surface a chooser. We
therefore host each wallet's deep-link handler on the wallet vendor's own domain
(`https://<wallet-domain>/cip30dl/v1/...`) backed by Universal-Link / App-Link claims on that
domain; this gives deterministic routing because only the wallet vendor's app can claim its own
AASA / assetlinks file. The custom-scheme fallback `cip30dl:<wallet-id>/v1/...` is similarly
disambiguated by the embedded `<wallet-id>`.

For interoperability, a future minor revision MAY define a CIP-13-grammar-compliant alternate form
`web+cardano://cip30dl/v1/<wallet-id>/<method>?<params>` (mirroring CIP-158's `browse` grammar
precedent as the established CIP-13 extension shape, and registered through CPS-16's authority
registry to avoid collisions with other emerging `web+cardano://` authorities) that routes through
the user's OS-default Cardano-URI handler when the dApp does not know which wallet to address. This is deferred to a
follow-up CIP because the chooser-mode UX is materially worse for the same-device dApp-to-wallet
flow this CIP is optimised for.

The differentiating rationale from CIP-13:156-164 ("Why not use Universal links, deep links or
other non-protocol-based Solution?") was that Universal-Link routing "requires a centralized system
which makes it unsuitable for a multi-app standard". CIP-30-DeepLink avoids the centralization
concern by splitting the Universal-Link domain across each wallet vendor's own DNS &mdash; there is
no central gatekeeper because the registry (Appendix B) is a flat list of independently-owned
wallet domains.

### Conway transaction body extraction

The `commit` URL parameter binds the wallet to a specific transaction; that binding is meaningful
only if the dApp and wallet agree on which bytes constitute the `tx_body`. Conway-era transactions
(see [Conway CDDL `cardano-ledger`](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/conway/impl/cddl-files/conway.cddl))
are encoded as:

```text
transaction =
  [ transaction_body            ; element 0 -- the body
  , transaction_witness_set     ; element 1
  , bool                        ; element 2 -- isValid
  , auxiliary_data / null       ; element 3
  ]
```

The wallet MUST extract the **literal** byte range of `transaction_body` (element index 0 of the
top-level CBOR array) as it appears in the source transaction CBOR, and compute
`commit = BLAKE2b-256` over those exact bytes. The wallet MUST NOT re-encode, canonicalise, or
otherwise mutate the extracted bytes. The literal-bytes rule is load-bearing: the chain's `tx_id`
is `BLAKE2b-256` of the same source `transaction_body` bytes the ledger validated, and any
divergence between the wallet's `commit` and the chain's `tx_id` (introduced by, e.g., a wallet
re-canonicaliser that disagrees with the source encoder on definite-vs-indefinite-length encoding,
or on sort order for non-text-key maps) breaks every downstream layer that pins the transaction by
hash. The dApp MUST supply a Conway-era canonical CBOR encoding per
[RFC 8949 §4.2](https://datatracker.ietf.org/doc/html/rfc8949#section-4.2) so the literal-bytes
extraction is well-defined; wallets MAY reject a transaction whose source CBOR is non-canonical
with `errorCode=-9 UnsupportedVersion` (`errorMessage="non-canonical CBOR encoding"`) but are not
required to do this check.

**Reference encoder.** Implementations needing to produce canonical Conway-era CBOR SHOULD use the
[`cardano-ledger`](https://github.com/IntersectMBO/cardano-ledger) Haskell reference encoder, the
[`pallas-codec`](https://github.com/txpipe/pallas) Rust reference encoder, or the
[`cardano-multiplatform-lib`](https://github.com/dcSpark/cardano-multiplatform-lib) JavaScript/Rust
encoder. Conformance against any of these is sufficient; conformance against none is
non-interoperable.

**Auxiliary data consistency rule.** If element index 3 (`auxiliary_data`) is non-null, the wallet
MUST verify that `transaction_body.auxiliary_data_hash` (an OPTIONAL field inside `transaction_body`)
equals `BLAKE2b-256(canonical-cbor(auxiliary_data))` where `canonical-cbor` is the same Conway-era
canonical encoding referenced above. If the hashes disagree the wallet MUST reject with
`errorCode=-11 AuxiliaryDataHashMismatch`. Unlike the `tx_body` extraction (which is byte-literal),
the auxiliary-data hash check intentionally re-canonicalises because it is verifying a
chain-recorded hash, not extracting bytes the chain will validate. This closes a class of attacks
where a malicious intermediary swaps the auxiliary-data payload between the wallet's signing-time
view and the final-submitted transaction: the chain enforces `auxiliary_data_hash` consistency at
validation, but without this wallet-side check the user could sign a transaction whose displayed
metadata is unrelated to the on-chain effect.

The dApp SHOULD perform the same extraction + hash locally so it can re-verify the wallet's
`commit` after receiving the witness set; if the dApp's locally-computed `commit` differs from
the wallet's, the dApp MUST treat the response as invalid (`errorCode=-2 CommitMismatch`,
signalled by the dApp to the user even though the wallet did not signal it).

### Methods

Each method follows the same envelope: the dApp constructs a URL, the OS launches the wallet, the
wallet redirects back to `redirect` with the result.

**AEAD envelope (formal definition).** Below, `enc(x)` denotes the authenticated encryption of the
plaintext byte string `x` under the elliptic-curve Diffie-Hellman keypair established at `connect`.
The default suite is **NaCl-box** (X25519 over Curve25519 per
[RFC 7748](https://datatracker.ietf.org/doc/html/rfc7748), XSalsa20 stream cipher, Poly1305 MAC,
24-byte random nonce; combined construction
[`crypto_box_curve25519xsalsa20poly1305`](https://doc.libsodium.org/public-key_cryptography/authenticated_encryption)).
Wallets MAY additionally implement the **ChaCha20-Poly1305 IETF** suite as defined in
[RFC 8439](https://datatracker.ietf.org/doc/html/rfc8439) with X25519-derived shared secret (
[`crypto_box_curve25519chacha20poly1305`](https://doc.libsodium.org/secret-key_cryptography/aead/chacha20-poly1305/ietf_chacha20-poly1305_construction)).
The dApp signals which suite it expects via the OPTIONAL `aead` URL parameter at `connect` time
(`aead=xsalsa20poly1305` is the default; `aead=chacha20poly1305-ietf` is the alternate). Wallets
that implement only the default suite MUST reject `aead=chacha20poly1305-ietf` with
`errorCode=-9 UnsupportedVersion`.

**Curve25519 low-order key rejection.** Per [RFC 7748 §6.1](https://datatracker.ietf.org/doc/html/rfc7748#section-6.1),
both the wallet AND the dApp MUST reject any received X25519 public key whose Diffie-Hellman output
is the all-zero string. The eight low-order points of Curve25519 produce this output regardless of
the local secret; failing to reject them allows a man-in-the-middle to force a known shared secret.
On rejection the receiver MUST abort the session with `errorCode=-7 DecryptFailed`. Reference:
[Curves mailing list discussion (Bernstein, 2017)](https://moderncrypto.org/mail-archive/curves/2017/000896.html).

**Ed25519 verification profile.** All Ed25519 signature verifications (including the response-signing
layer below) MUST follow the strict-mode profile equivalent to ZCash
[ZIP-215](https://github.com/zcash/zips/blob/main/zip-0215.rst): non-canonical scalar `s` rejected,
non-canonical group element `R` rejected, cofactored verification with `8·([s]B - R - [k]A) = O`.
Implementations SHOULD use libsodium's `crypto_sign_verify_detached` (which conforms to ZIP-215),
or Tink's Ed25519Verify; see Chalkias et al.
[*"Taming the many EdDSAs"* (FC '21)](https://eprint.iacr.org/2020/1244) for why permissive
verification is dangerous in multi-implementation settings.

**Authenticity caveat (repudiation).** The AEAD envelope provides confidentiality and integrity
against eavesdroppers, but the recipient cannot prove to a third party that the *sender* (not
themselves) produced the ciphertext: NaCl-box and ChaCha20-Poly1305 are both *repudiable*. This is
why the wallet response-signing layer below is REQUIRED rather than reliant solely on the AEAD
envelope. Implementers MUST NOT omit the response-signature on the false assumption that the AEAD
already provides authenticity.

All ciphertext is base64url.

#### connect

Request:

```text
https://wallet.example/cip30dl/v1/connect
    ?v=1
    &dapp=<base64url(dapp-info-json)>
    &dappKey=<base64url(X25519 dApp public key, 32 bytes)>
    &redirect=<percent-encoded universal link>
    &chain=<cardano:mainnet | cardano:preprod | cardano:preview>
    &nonce=<base64url(24)>
```

`dapp-info-json` is `{ "name": "Aegis", "url": "https://aegis.fluxpointstudios.com", "iconUrl": "..." }`.
The wallet SHOULD display `name`, `url`, and `iconUrl` to the user on the authorisation screen exactly
as on CIP-30 `enable()`.

Response (wallet appends to `redirect`):

```text
<redirect>
    ?response=approved
    &method=connect
    &walletKey=<base64url(wallet X25519 public key)>
    &nonce=<base64url(wallet-chosen nonce, 24 bytes)>
    &echo=<base64url(the request's nonce, copied verbatim, 24 bytes)>
    &payload=<base64url(ciphertext(session-json))>
    &signature=<base64url(Ed25519 over the canonical subject)>
```

The `connect` response is signed like every other response (*Security model § Response
signing*), and carries two `connect`-specific parameters. `method=connect` is a domain-separation
tag inside the signed subject, so a signature minted for any other method cannot be re-presented as
a `connect`. `echo` is the request's `nonce` copied back verbatim, binding the response to the
specific request the dApp issued. Because `connect` is first contact, the verifying
`signingPublicKey` is delivered *inside this same response's* encrypted `payload`: the dApp MUST
(1) box-decrypt `payload`, (2) re-derive the canonical subject and verify `signature` against the
decrypted `signingPublicKey` — rejecting `errorCode=-10 ResponseSignatureInvalid` on failure, or if
`method=connect`, `signature`, or `echo` is absent — and (3) check that the (present) `echo` equals
the `nonce` it sent — rejecting `errorCode=-5 NonceReplay` on mismatch. This proves the response is untampered, bound to
this request, and pins `signingPublicKey` for the session. It does NOT by itself prove *which*
wallet replied (first contact has no prior key to check against); that assurance comes from
deterministic OS routing of the scheme to the paired wallet plus the in-wallet consent screen,
exactly as for the encryption layer.

`session-json` decrypts to:

```json
{
  "session":          "<opaque base64url, >=32 bytes random>",
  "network":          0,
  "addresses":        ["<hex bech32 payment address>"],
  "chain":            "cardano:preprod",
  "walletId":         "lace",
  "expiresAt":        1810000000,
  "signingPublicKey": "<base64url(ed25519 vkey, 32 bytes)>"
}
```

The `signingPublicKey` is the session-binding Ed25519 vkey the dApp uses to verify the
authenticity of every subsequent response from this wallet (see *Security model § Response
signing*). It is per-session and per-dApp; the dApp MUST persist it for the lifetime of the
session and MUST use it to verify EVERY response URL the wallet emits.

On rejection:

```text
<redirect>?response=rejected&errorCode=<int>&errorMessage=<short string>
```

#### signTx

Request:

```text
https://wallet.example/cip30dl/v1/signTx
    ?v=1
    &dappKey=<...>
    &redirect=<...>
    &nonce=<base64url(24)>
    &commit=<base64url(BLAKE2b-256 of tx_body)>
    &ttl=<unix seconds>
    &payload=<base64url(ciphertext(signTx-json))>
```

`signTx-json` decrypts to:

```json
{
  "session":      "<from connect>",
  "tx":           "<base64url(full transaction CBOR)>",
  "partialSign":  true,
  "vkeyHints":    ["<hex addr_pubkey>"]
}
```

The wallet MUST verify `BLAKE2b-256(tx_body extracted from the CBOR) == commit` before rendering the
signing UI. If they differ, the wallet MUST reject with `errorCode=-2` and
`errorMessage="commit mismatch"`.

Response (success):

```text
<redirect>?response=approved&nonce=<base64url(24)>&payload=<ciphertext(result-json)>
```

`result-json`:

```json
{
  "commit":     "<base64url, echo of request commit>",
  "witnessSet": "<base64url(CBOR of transaction_witness_set, CIP-30 shape)>",
  "txHash":     "<base64url(BLAKE2b-256(tx_body))>"
}
```

If `partialSign=false`, the wallet MUST return a witness set whose vkey witnesses are sufficient to
produce a valid transaction (i.e. if the wallet cannot fully sign it MUST return `errorCode=-1` per
CIP-30:347 `TxSignError.ProofGeneration`). If `partialSign=true`, the wallet returns only the vkey
witnesses it controls and does no completeness check. Both semantics are inherited verbatim from
CIP-30:343-347 `api.signTx(tx: cbor<transaction>, partialSign: bool = false)`. The witness-set
return shape is `cbor<transaction_witness_set>` (CIP-30:343); on the wire we base64url-encode the
same CBOR.

**`result-json.commit` echo verification (MUST).** The dApp MUST verify that
`result-json.commit` equals the `commit` value it sent in the request. Mismatch indicates that the
wallet returned a witness set for a different transaction body than the one the dApp asked it to
sign; the dApp MUST reject the response with `errorCode=-2 CommitMismatch`, discard the witness
set, and terminate the session (`disconnect`). The echo invariant is the dApp-side complement of
the wallet's pre-render `BLAKE2b-256(tx_body) == commit` check: together they make tx-body
substitution impossible across the full request/response loop.

**Witness-set merge semantics for `partialSign=true`.** When the dApp combines a wallet-returned
partial witness set into an in-flight `transaction_witness_set` that already carries vkey witnesses
(e.g. from a prior co-signer), it MUST concatenate the returned `vkey_witnesses` array (map key `0`
of the `transaction_witness_set` map per CIP-30:343 and Conway CDDL) to the existing array, NOT
replace it. Replace semantics would silently drop the prior co-signer's witnesses and produce a
transaction that fails ledger validation. Non-vkey witness fields (native scripts at key `1`, Plutus
scripts at keys `3`/`6`/`7`, datums at key `4`, redeemers at key `5`) MUST be merged with the same
array-append semantics if both maps populate the same field. dApps SHOULD reject a wallet response
whose returned `transaction_witness_set` carries non-empty entries at any key the dApp did not
expect the wallet to produce (e.g. unexpected native scripts), as this constitutes injection of
non-vkey policy material outside the wallet's mandate.

#### signData

Mirrors CIP-30 `signData(addr, payload)` (CIP-30:349). Request encrypted payload:

```json
{ "session": "...", "addr": "<bech32 stake or payment>", "payload": "<base64url>" }
```

Response payload returns a CIP-30 `DataSignature` (CIP-30:64-69), where `signature` and `key` are
each `cbor<COSE_Sign1>` and `cbor<COSE_Key>` respectively per CIP-30's `cbor<T>` definition
(CIP-30:58 &mdash; "a hex-encoded string representing CBOR corresponding to T"):

```json
{ "signature": "<hex of CBOR-encoded COSE_Sign1>", "key": "<hex of CBOR-encoded COSE_Key>" }
```

The COSE structure ([CIP-8](https://cips.cardano.org/cip/CIP-8):90-94) and header set MUST follow
CIP-30:355-368 verbatim: `alg`=`EdDSA` (-8), `"address"`=raw address bytes (no CBOR wrapper),
`kid` optional, payload unhashed, no `external_aad`. The `COSE_Key` MUST set `kty`=`OKP` (1),
`alg`=`EdDSA` (-8), `crv`=`Ed25519` (6), `x`=public key bytes. CIP-30-DeepLink defines only the
deep-link transport for these bytes; the cryptographic structure is owned by CIP-8 and CIP-30 and
is not re-specified here.

#### getUsedAddresses / getUnusedAddresses / getRewardAddresses / getNetworkId

Read-only. Same envelope. Wallet MAY short-circuit and answer without showing UI if the session is
fresh and the user has previously approved the same dApp for the same chain. Wallet MUST NOT return
more than 50 used addresses per call (privacy budget; the dApp can paginate via `?page=`). The
50-per-page limit mirrors CIP-30's existing pagination convention (CIP-30:319 `Paginate.limit`).

`addresses` values are returned hex-encoded per CIP-30:51 ("All return types containing `Address`
must return the hex-encoded bytes format, but must accept either format for inputs"). dApps that
need bech32 for display MAY re-encode locally.

Request body for paginated calls:

```json
{ "session": "...", "page": 0, "limit": 50 }
```

Response body:

```json
{ "addresses": ["<hex bytes per CIP-30:51>"], "nextPage": 1 }
```

`getNetworkId` follows CIP-30:272: returns `0` for testnet, `1` for mainnet; other values reserved.

#### submitTx (OPTIONAL)

Wallets MAY accept a fully signed tx and submit it. This is OPTIONAL because the dApp can submit
through its own backend (the Aegis case). When implemented, request payload is
`{ "session": "...", "tx": "<base64url(signed CBOR)>" }`; response payload is
`{ "txHash": "<base64url>" }`.

#### CIP-95 governance profile

[CIP-95](https://cips.cardano.org/cip/CIP-95) (Web-Wallet Bridge &mdash; Conway ledger era, Active)
extends CIP-30 with governance support. Its surface (CIP-95:243-499) adds three methods
(`api.cip95.getPubDRepKey`, `api.cip95.signData` accepting a `DRepID`,
`api.cip95.getUnregisteredPubStakeKeys`) plus extends `api.signTx` and `api.getRegisteredPubStakeKeys`
to recognise Conway certificate types (CIP-95:328-376). CIP-30-DeepLink carries the entire CIP-95
governance surface in `v=1` over the transport already specified above, with NO envelope, encryption,
or callback change. Conway governance certificates already sit inside the `signTx` request's CBOR
`tx`, and the CIP-95 read methods reuse the same request-response envelope as the base read methods;
the governance surface therefore rides the existing transport unchanged. A wallet that implements
CIP-95 MUST advertise it by setting `"supports_governance": true` in its vendor-attestation manifest
(*Security model &sect; Vendor attestation manifest*) and MUST implement the following:

- **Governance certificates in `signTx`.** The wallet MUST recognise the Conway governance and
  stake-key certificate types (CIP-95:328) &mdash; DRep registration/update/retirement, vote
  delegation, and constitutional-committee hot-key authorisation &mdash; when they appear inside
  the `signTx` request's decrypted `tx` CBOR, and MUST surface them on the signing screen exactly
  as CIP-95 requires for the injected `api.signTx`. This is the same `signTx` method and the same
  `commit` binding already defined; no new wire method is introduced.

- **`getPubDRepKey`.** Read-only, using the same envelope as `getRewardAddresses`. The decrypted
  response payload is `{ "dRepKey": "<hex Ed25519 DRep public key per CIP-95:281>" }`.

- **`getRegisteredPubStakeKeys` / `getUnregisteredPubStakeKeys`.** Read-only, using the same
  paginated envelope as `getUsedAddresses`. Each decrypted response payload is
  `{ "stakeKeys": ["<hex Ed25519 stake public key per CIP-95:302,318>"], "nextPage": <int | null> }`.
  As with `getUsedAddresses`, the wallet MUST NOT return more than 50 keys per page and MUST NOT
  expose the derivation path.

- **DRep `signData`.** The existing `signData` method (*&sect; signData*) is the transport for
  `api.cip95.signData`: a governance wallet MUST accept a
  [CIP-129](https://cips.cardano.org/cip/CIP-129) `DRepID` (CIP-95:421) in the
  `signData` request's `addr` field in addition to a bech32 payment or stake address, and MUST
  return the CIP-30 `DataSignature` (`COSE_Sign1` / `COSE_Key`) unchanged. The DRep signing envelope
  is thus identical to the base `signData` envelope; only the accepted `addr` value set is widened.

A wallet that does not implement CIP-95 MUST reject `getPubDRepKey`,
`getRegisteredPubStakeKeys`, and `getUnregisteredPubStakeKeys` with `errorCode=-9 UnsupportedVersion`
per the strict unknown-method rule (*&sect; Unknown-key policy*), and MUST reject a `signData`
request whose `addr` is a `DRepID` with the same code.

### Callback contract

A wallet MUST redirect back to the `redirect` URL provided in the request exactly once. The `redirect`
URL MUST be:

1. Either a Universal Link / App Link claimed by the dApp's bundle ID (verified by the OS), OR
2. A custom-scheme URL where the scheme is the dApp's reverse-DNS bundle ID prefix (e.g.
   `com.fluxpointstudios.aegis://...`).

A wallet MUST NOT redirect to any URL whose host does not match the host declared in the `connect`-time
`dapp-info-json.url`. Cross-host redirect is the single most dangerous lever in this protocol and the
validator MUST be implemented before the wallet ships.

If the user dismisses the wallet without acting, the wallet MUST redirect with `response=cancelled`
after at most 60 seconds OR when the user explicitly hits a cancel button, whichever comes first.
The 60-second cancel timer starts when the **signing UI is rendered to the user**, NOT when the
URL is first received. This is the meaningful timer because per-request decryption + validation can
itself consume meaningful wall-clock time (especially on cold-start, where Keychain unlock plus AASA
fetch plus CBOR decode can take several seconds on low-end devices). Starting the timer at
URL-receipt risks `response=cancelled` firing before the user even sees the prompt.

### Security model

The threat model assumes (a) a malicious app installed on the same device, (b) a network attacker who
can read but not modify HTTPS, (c) a curious-but-honest OS that may surface URL contents in logs and
notification previews, and (d) a buggy-but-not-malicious dApp. The protocol does not defend against a
malicious wallet &mdash; by construction, the user has chosen to trust their wallet with their seed.

#### Replay protection

Every request URL carries a 24-byte random `nonce`. The wallet MUST reject any request whose
`(dappKey, nonce)` tuple it has seen in the last `ttl + 600` seconds. `ttl` is a unix timestamp; the
wallet MUST refuse to sign once the system clock passes `ttl`. dApps SHOULD set `ttl = now + 300`
(5 minutes) for `signTx`. The wallet's nonce cache MUST be persistent across wallet-process
restarts (iOS app backgrounding/killing, Android Activity recreation, system-initiated process
death). An in-memory-only cache is non-conformant because an attacker can race the cache with a
forced process kill (e.g., by triggering an out-of-memory condition on a low-end device). The
cache MAY be implemented as a SQLite table or an append-only encrypted log; entries older than
`ttl + 600` MAY be garbage-collected. **Defence-in-depth (testable):** a conformance test (a)
submits the exact same URL twice within 10 seconds and observes `errorCode=-5 NonceReplay` on the
second submission; (b) submits a URL, force-kills the wallet process, relaunches it, and resubmits
the same URL &mdash; the second submission MUST still observe `errorCode=-5`.

For `connect` specifically &mdash; which has no prior session and thus no wallet-side nonce cache to
consult &mdash; replay is bound on the **dApp** side. The wallet MUST copy the request's `nonce`
verbatim into the response `echo` parameter (which is covered by the response `signature`), and the
dApp MUST reject with `errorCode=-5 NonceReplay` any `connect` response whose `echo` does not equal
the `nonce` it generated for that request. This binds the session-establishing response to the
specific request the dApp issued, so a captured `connect` response cannot be replayed into a later
pairing attempt. **Defence-in-depth (testable):** a conformance test feeds the dApp a `connect`
response whose `echo` differs from the request `nonce` (signature otherwise valid) and asserts
`errorCode=-5`.

#### Callback host binding (anti-phish)

`redirect` MUST be one of:

- A Universal Link / App Link whose `apple-app-site-association` / `assetlinks.json` claim is on the
  same registered domain as `dapp-info-json.url` (proven during `connect`), OR
- A custom scheme matching `<reverse-DNS of dapp bundle ID>:`.

The wallet MUST persist the `redirect` URL host from `connect` and reject any *subsequent* request
whose `redirect` host differs. The `errorCode=-4 RedirectHostMismatch` envelope MUST be delivered to
the `connect`-time persisted `redirect` URL, NOT to the offending request's `redirect` URL. Delivering
to the offending host would defeat the security purpose: the legitimate dApp would never observe the
attack attempt and would be unable to tear down the session. Wallets MAY additionally surface the
mismatch in their own UI before redirecting. **Defence-in-depth (testable):** a conformance test
that connects with `redirect=https://aegis.example/cb` and then calls `signTx` with
`redirect=https://evil.example/cb` MUST observe `errorCode=-4 RedirectHostMismatch` delivered to
`https://aegis.example/cb`.

#### Commit binding (anti-swap)

The `commit` URL parameter is a 32-byte BLAKE2b-256 over the canonical CBOR encoding of
`transaction_body` (Conway era; CIP-30 already standardises this as `txHash`). The wallet MUST
re-compute this hash from the decrypted CBOR and reject on mismatch. The URL bar &mdash; which iOS will
display in the wallet's app-switcher card and which security-conscious users do read &mdash; anchors to the
exact transaction. A MITM who alters the encrypted payload but leaves `commit` alone will be rejected;
a MITM who alters both will produce a URL that no longer matches what the dApp showed pre-handoff
(and which the dApp re-verifies on receipt of the witness set).
**Defence-in-depth (testable):** swap one byte in the encrypted `payload`'s embedded CBOR while
keeping `commit` unchanged; the wallet MUST observe `errorCode=-2 CommitMismatch`.

#### Source-app identity binding (anti-impersonation)

The dApp's identity for every request MUST be bound to its callback host, and the callback host MUST
be cryptographically attested by the platform's deep-link claim file. The mechanism is:

- On Android, the wallet MUST call `getCallingPackage()` / `Intent.getReferrer()` to obtain the
  source-app's package name. The wallet MUST then fetch
  `https://<redirect-host>/.well-known/assetlinks.json` (cached for 24h, refresh on host change)
  and assert that the discovered package name appears in some entry's
  `target.package_name` whose `target.sha256_cert_fingerprints` matches the source package's
  signing certificate. If either lookup fails, the wallet MUST emit
  `errorCode=-13 SourceAppUnverified` and abort before rendering the signing screen.
- On iOS, `UIApplication.open(_:)` does NOT expose the source bundle ID after iOS 11. Instead, the
  wallet MUST treat the `redirect` host as the dApp identity, and MUST require that the dApp's
  `apple-app-site-association` (fetched from `https://<redirect-host>/.well-known/apple-app-site-association`,
  cached for 24h) lists at least one `applinks.details[*].appIDs` entry. The bundle ID inside
  that entry is then displayed on the signing screen as "Signing for: &lt;bundle-id&gt; (verified
  via &lt;redirect-host&gt;)". If the AASA fetch fails or contains no `applinks` block, the wallet
  MUST emit `errorCode=-13 SourceAppUnverified`.

Both platforms therefore reach the same invariant: **the bundle ID rendered on the wallet's
signing screen is the bundle ID the OS itself attests at the network layer**, not a self-claim
from `dapp-info-json`. A malicious app cannot copy a victim dApp's bundle ID without also
controlling DNS for the victim's `redirect` host.

**Defence-in-depth (testable):**
- Android conformance: a second app with a different signing cert calls `signTx` with
  `redirect=https://aegis.example/cb`; the wallet MUST emit `errorCode=-13`.
- iOS conformance: a `redirect` host with no AASA file is supplied; the wallet MUST emit
  `errorCode=-13`. Conversely, a valid AASA with bundle ID `studios.fluxpoint.aegis` causes that
  exact string to appear on the rendered signing screen.

#### Vendor attestation manifest

Wallets MUST publish a vendor-attestation manifest at
`https://<wallet-domain>/.well-known/cip30dl-attestation.json` (HTTPS-only, served with
`Content-Type: application/json` and `Cache-Control: max-age=86400`). This origin-anchored manifest,
resolved at runtime from the wallet's own domain, is the NORMATIVE and sole authoritative source for
the wallet's CIP-30-DeepLink commitments. The advisory `wallet-registry.json` in Appendix B is a
convenience catalogue only and is NEVER consulted for runtime validation; where the two disagree, the
origin-anchored manifest governs. Schema:

```json
{
  "$schema": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0186/cip30dl-attestation.schema.json",
  "wallet_id": "<lowercase ASCII id matching Appendix B>",
  "protocol_versions": ["1"],
  "methods": ["connect", "signTx", "signData", "getUsedAddresses", "getRewardAddresses", "getNetworkId"],
  "https_prefix": "https://<wallet-domain>/cip30dl/v1/",
  "scheme": "cip30dl-<wallet-id>",
  "supports_governance": false,
  "supports_submit": false,
  "max_payload_bytes": 12288,
  "audit_reports": [
    {"vendor": "Trail of Bits", "url": "https://...", "report_date": "2026-08-01"}
  ],
  "vulnerability_disclosure": "https://<wallet-domain>/.well-known/security.txt"
}
```

dApps SHOULD probe this manifest before sending the first `connect` and SHOULD refuse to proceed
if the advertised `https_prefix` is not hosted on the wallet's own `<wallet-domain>`, or if
`protocol_versions` does not include `"1"`. The conformance suite asserts that every wallet under
test serves a manifest that validates against `cip30dl-attestation.schema.json`.

#### In-process WebView dApps (special case)

A dApp running inside a wallet-controlled WebView (e.g. Lace's in-app browser, Eternl's dApp
explorer) is NOT a deep-link dApp &mdash; it already has `window.cardano` injected per CIP-30 and
MUST use that interface instead. Wallets MUST detect this case (the navigation arrives from their
own WebView host) and either (a) refuse the deep-link with `errorCode=-14 UseInjectedAPI` and a
human-readable hint, or (b) silently route the request to the injected CIP-30 path. The conformance
suite asserts that a `signTx` originating from the wallet's own WebView host is handled by exactly
one of the two paths, never both, and never silently dropped.

#### URI length budget

iOS Safari and Android Chrome handle URLs up to roughly 32 KB, but App Switcher and Universal Link
payload preview can truncate around 8 KB. Cardano transaction CBOR for a typical Aegis insurance buy
is 1.2 to 3 KB. After base64url + percent-encoding (approximately 1.5x expansion), the URL is
1.8 to 4.5 KB &mdash; well inside budget. dApps that need to sign larger transactions (multi-asset, many
native script witnesses) SHOULD split the transaction logically or pre-publish reference scripts via
CIP-31. A wallet MUST accept URLs up to 12 KB. A wallet MAY refuse URLs larger than 12 KB with
`errorCode=-32 PayloadTooLarge`; the dApp can then degrade to a wallet-server submission via
`submitTx`. **Defence-in-depth (testable):** a conformance test pads `payload` to 13 KB and asserts
either successful sign (wallet accepts >12 KB) or `errorCode=-32`.

#### Privacy budget

A `connect` response leaks at most 5 addresses. `getUsedAddresses` is paginated at 50 per page,
mirroring CIP-30. A wallet MUST NOT include UTxOs in any response without an explicit user prompt,
and MUST NOT include the user's stake key derivation path. The protocol intentionally exposes less
than CIP-30's `getUtxos()` does (which Aegis and other backends already gather from the chain
themselves). **URL-bar metadata leak (acknowledged residual).** The OS surfaces the inbound deep-link
URL in the App Switcher card, the Recently Used list, and (on iOS) Spotlight indexing on some
versions. The URL therefore leaks (a) which dApp host invoked which wallet, (b) the request's
`method`, and (c) the encrypted-but-fingerprintable `payload` length. This is intrinsic to deep-link
transport on both platforms and cannot be eliminated short of switching to WebSocket/WebRTC (see
Rationale &mdash; "Why not CIP-45"). Wallets SHOULD truncate the displayed URL in their app-switcher
card by setting the `UIApplicationSceneManifest` accordingly on iOS and by using
`FLAG_SECURE` on Android where the threat model warrants. Users with adversaries who can read their
unlocked device screen are outside the scope of this protocol's threat model. **Defence-in-depth
(testable):** a conformance test asserts that the JSON response to `connect` contains no key named
`utxos` and that the `addresses` array length is &le; 5.

#### Encryption

X25519 + XSalsa20-Poly1305 via NaCl `crypto_box_easy`
([NaCl docs](https://nacl.cr.yp.to/box.html),
[libsodium docs](https://doc.libsodium.org/public-key_cryptography/authenticated_encryption)).
This is the exact construction used by Phantom and Petra and is implemented natively on iOS
(CryptoKit), Android (Tink), and every language we expect a Cardano dApp to be written in.
ed25519-only wallets MUST still implement an X25519 keypair for this protocol; the two key types are
derivable from a common Curve25519 scalar (RFC 7748 / Signal's `XEdDSA`) and the X25519 pair is
ephemeral so a fresh keypair per `connect` is acceptable.
**Defence-in-depth (testable):** a conformance test flips one byte of `payload` ciphertext and asserts
`errorCode=-7 DecryptFailed` (Poly1305 MAC failure).

#### Response signing (Cardano-native authenticity)

CIP-30-DeepLink REQUIRES the wallet to sign every callback payload with a session-binding Ed25519
key. This is in addition to the NaCl box encryption, and is the load-bearing authenticity proof
the dApp consumes before assembling the final transaction. Rationale: NaCl box proves "someone with
the wallet's ephemeral X25519 secret key produced this message"; it does NOT prove *which* wallet,
because the X25519 keypair is ephemeral and rotates per `connect`. The session-binding signing key
proves THIS specific wallet &mdash; and by extension, the user &mdash; produced the response. The pattern
mirrors how [CIP-95](https://cips.cardano.org/cip/CIP-95) handles governance payloads (signed by the
user's DRep key), how WalletConnect v2 binds sessions to CAIP-25 namespaced keys, and how Solana
MWA pairs TLS with an Ed25519 wallet key over WebSocket. This requirement is the Cardano-ethos
divergence from the Phantom / Petra pattern, which encrypts but does not separately sign.

**Session-binding key derivation.** At `connect`, the wallet derives a non-rotating Ed25519
`session_vkey` using HKDF-SHA512 ([RFC 5869](https://datatracker.ietf.org/doc/html/rfc5869)) as
follows:

```
IKM   = wallet_root_secret || session_entropy   (wallet-controlled; MUST contain ≥ 256 bits of fresh entropy per session)
salt  = SHA-256("cip30dl/v1/session_vkey")      (fixed, 32 bytes)
info  = "cip30dl/v1/session_vkey/" || dapp_host || "/" || session_id
OKM   = HKDF-SHA512(IKM, salt, info, L = 32)
session_signingPrivateKey = clamp_ed25519_scalar(OKM)
session_vkey              = Ed25519.publicKey(session_signingPrivateKey)
```

`wallet_root_secret` MUST NOT be the user's CIP-1852 root private key, the stake key, or the DRep
key directly &mdash; it is a wallet-internal secret derived once at first launch and persisted in
secure storage (iOS Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`, Android Keystore
with `setUserAuthenticationRequired(true)` where the wallet UX allows). `session_entropy` MUST be
freshly drawn from the platform CSPRNG (`SecRandomCopyBytes` / `SecureRandom`) on every `connect`.
Reusing `session_entropy` across `connect` events with the same `dapp_host` MUST cause the wallet to
return `errorCode=-12 SessionEntropyReuse`; this mirrors the Signal X3DH "no key reuse" invariant
(cf. [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) Section 8.5 on deterministic
nonces). The wallet's `session-json` response MUST include the field
`"signingPublicKey": "<base64url(session_vkey, 32 bytes)>"` so the dApp can verify subsequent
responses. The signing key is per-session, per-dApp; compromise of one session does not leak
`wallet_root_secret`, the stake key, or the DRep key.

**Signature construction.** For every response URL the wallet returns, the wallet computes the
signature over a **canonicalised** form of the URL, with the `signature` parameter itself removed.
The canonical form is constructed as:

1. Start with the literal domain-separator string `"cip30dl-v1\n"` (11 octets, UTF-8, including the
   trailing LF). This MUST be the leading prefix of every signed message so that a signature
   minted for CIP-30-DeepLink can never be replayed against a different protocol that happens to
   reuse the same `session_signingPrivateKey`.
2. Append `<scheme>://<host_lowercased>[:<port>]<path>` (host case-folded per
   [RFC 3986 §3.2.2](https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.2); path preserved
   byte-for-byte). The explicit port MUST be included if and only if it appears literally in the
   URL authority. Default ports for the scheme (`443` for `https`, `80` for `http`) MUST NOT be
   emitted even if equivalent under RFC 3986 §3.2.3. This rule keeps the canonical form
   byte-deterministic across implementations that disagree on default-port omission.
3. Append `?`.
4. Collect every query parameter except `signature`. Sort the parameters by key in **lexicographic
   byte order** (ASCII). For ties (repeated keys), preserve emission order.
5. Re-encode every key and value with **strict-unreserved percent-encoding**: only the unreserved
   set `[A-Za-z0-9._~-]` is emitted literally; every other octet is percent-encoded; percent-encoded
   octets MUST use **uppercase** hex digits (`%2F`, never `%2f`); space MUST encode as `%20`
   (never `+`).
6. Join the re-encoded `key=value` pairs with `&`.

The wallet appends the signature as the FINAL parameter on the emitted URL:
`&signature=<base64url(Ed25519.sign(canonical_subject, session_signingPrivateKey))>`. The
**emitted** URL MAY use different (positional) parameter ordering than the canonical form &mdash;
the canonical form is solely the byte-string fed to Ed25519.

**dApp verification.** Before consuming the witness set, signing data response, or any
informational payload from the wallet, the dApp MUST:

1. Decrypt and validate the NaCl box payload (existing layer).
2. Re-derive the canonical subject string per the six-step procedure above. The dApp MUST
   independently re-encode &mdash; it MUST NOT trust the wallet to deliver a "pre-canonicalised"
   form alongside the URL, because the attacker controls the URL.
3. Verify the Ed25519 signature against the `session.signingPublicKey` from the `connect` response,
   under the strict ZIP-215 verification profile defined in the *Methods* preamble.
4. On verification failure, the dApp MUST discard the entire response, terminate the session
   (issue `disconnect`), and surface the failure to the user as a wallet authenticity error.

**First contact (`connect`).** The `connect` response is signed like every other response, but the
`session.signingPublicKey` used to verify it is delivered *inside that same response's* encrypted
`payload`. The dApp therefore decrypts first, then verifies `signature` against the just-decrypted
`signingPublicKey`, and additionally requires the `method=connect` domain tag and an `echo` of the
request `nonce` (see *§ connect* and *§ Replay protection*). This is a trust-on-first-use pin: it
proves the response is internally consistent, untampered, and bound to this request, and it fixes
`signingPublicKey` for the session &mdash; but, lacking a prior key, it does not by itself
authenticate *which* wallet replied. That authentication rests on deterministic OS routing of the
scheme to the paired wallet plus the user's in-wallet consent, exactly as for the encryption layer.

**Defence-in-depth (testable):** a conformance test (a) replays a valid response URL with a
flipped signature byte and asserts dApp rejection, (b) substitutes the response from a different
wallet's `session.signingPublicKey` and asserts dApp rejection, (c) re-orders the **canonical
subject** parameters (forcing the dApp to re-sort) and asserts the signature still verifies
(canonical form is order-invariant under lex-sort), (d) flips one bit of the domain-separator
prefix and asserts dApp rejection, (e) submits the same URL with `%2f` lowercase instead of `%2F`
and asserts dApp rejection (encoding is uppercase-only); (f) feeds the dApp a `connect` response
whose (present) `echo` differs from the request `nonce` and asserts `-5 NonceReplay`, and a `connect`
response missing `method=connect`, `signature`, or `echo` and asserts `-10 ResponseSignatureInvalid`. The wallet side
is tested by a
conformance harness that drives `signTx` and inspects the emitted URL: the final parameter MUST be
`signature`, the signature MUST verify against the advertised `session.signingPublicKey`, and the
bytes signed MUST be the canonical form defined above.

### iOS platform considerations

- **Universal Links are the PREFERRED transport; the custom scheme is FALLBACK ONLY.** dApps MUST
  attempt the HTTPS Universal-Link form (`https://<wallet-domain>/cip30dl/v1/...`) first and MUST use
  the `cip30dl-<wallet-id>:` custom scheme only when the Universal Link fails to launch (the
  wallet is installed but its AASA claim has not yet been fetched, or was cleared by a
  delete/re-install). The custom scheme is retained purely as defence-in-depth for that
  install-but-no-AASA-yet window; it is never the primary path and MUST NOT be used when the
  Universal Link resolves.
- **AASA in v=1 (OPTIONAL).** The wallet SHOULD publish an `apple-app-site-association` file at
  `https://<wallet-domain>/.well-known/apple-app-site-association` whose `applinks.details[*].paths`
  includes `/cip30dl/*`. When published, this makes `https://<wallet-domain>/cip30dl/v1/...` a
  Universal Link rather than a Safari navigation. **AASA in v=2 (MUST).** Wallets implementing
  `protocol_versions: ["2"]` (a future profile) MUST publish AASA so the wallet-domain HTTPS prefix
  is the sole entry point and the `cip30dl-<wallet-id>:` custom scheme can be retired. The v=1
  optionality is a pragmatic concession that no Cardano wallet ships AASA today; the v=2 mandate
  ensures the protocol does not permanently depend on custom schemes.
- The wallet MUST register the `cip30dl-<wallet-id>` URL type in its `Info.plist` under
  `CFBundleURLTypes` so the custom-scheme fallback works when the user has previously deleted and
  re-installed the wallet (which clears Universal Link claims until next AASA fetch) or when the
  wallet has not yet shipped AASA.
- iOS 17+: a dApp probing for installed wallets via `canOpenURL` MUST list each candidate scheme in
  `LSApplicationQueriesSchemes`. The CIP wallet registry (Appendix B) doubles as a recommended
  `LSApplicationQueriesSchemes` array.
- **WKWebView callback handling.** dApps that render their UI inside a `WKWebView` (e.g. the
  Capacitor wrapper used by Aegis) MUST handle two cases distinctly:
  1. **Outbound (sending the wallet request).** `WKWebView` does NOT forward `cip30dl-<wallet-id>:`
     URLs to the OS by default. The dApp's `WKNavigationDelegate.webView(_:decidePolicyFor:decisionHandler:)`
     MUST detect the scheme, call `UIApplication.shared.open(url, options: [:], completionHandler: nil)`,
     and pass `.cancel` to the decision handler so the WebView itself does not attempt navigation.
  2. **Inbound (receiving the wallet response).** When iOS resumes the dApp via its own AASA-claimed
     Universal Link, the inbound URL arrives at `AppDelegate.application(_:continue:restorationHandler:)`
     (or the `SceneDelegate` equivalent). The dApp MUST forward the URL into the embedded WebView via
     a JS bridge (`webView.evaluateJavaScript("window.handleCip30DeepLinkResponse('\(escapedUrl)')")`)
     **after** the response signature has been verified per *Response signing*. The dApp MUST NOT
     load the response URL into the WebView with `WKWebView.load(URLRequest:)`, because doing so would
     trigger a full navigation that flushes the in-page session state.
- The Solana MWA iOS post raises three valid concerns: context-switch fatigue, no wallet-picker, and
  Apple review risk. This CIP addresses them: context-switch is one round-trip per signature
  (acceptable for DeFi tempo); wallet-picker is handled by Universal Link disambiguation when
  multiple wallets claim the same path (this CIP places the claim on each *wallet's own domain*,
  eliminating disambiguation); Apple review risk is the reason this CIP defaults to Universal Links
  over custom schemes (Universal Links have no App Store policy friction).

### Android platform considerations

- **App Links are the PREFERRED transport; the custom scheme is FALLBACK ONLY.** As on iOS, dApps
  MUST attempt the HTTPS App-Link form first and MUST fall back to the `cip30dl-<wallet-id>:` custom
  scheme only when the App Link fails to launch (the wallet is installed but its `assetlinks.json`
  auto-verification has not completed). The custom scheme is retained purely as defence-in-depth for
  that window and is never the primary path.
- **App Links in v=1 (OPTIONAL).** The wallet SHOULD publish `/.well-known/assetlinks.json` with a
  `delegate_permission/common.handle_all_urls` claim for `https://<wallet-domain>/cip30dl/*`,
  making the HTTPS form an *Auto-Verified* App Link (Android 12+). **App Links in v=2 (MUST).**
  As with iOS AASA, v=2 mandates auto-verified App Links so the wallet-domain HTTPS prefix is the
  sole entry point.
- The custom scheme `cip30dl-<wallet-id>:` MUST be declared in `AndroidManifest.xml` with
  `<data android:scheme="cip30dl-<wallet-id>"/>`.
- The wallet MUST call `getCallingPackage()` / `Intent.getReferrer()` and validate the source-app
  identity against `assetlinks.json` per *Source-app identity binding* above (this is no longer
  advisory).
- The dApp SHOULD use `Intent.FLAG_ACTIVITY_NEW_TASK` so the wallet animates as a foreground activity
  rather than nested inside the dApp's task.

### Reference flow diagram

```text
+----------+                                              +-----------+
|  dApp    |                                              |  Wallet   |
|  (iOS)   |                                              |   (iOS)   |
+----+-----+                                              +-----+-----+
     |                                                          |
     |  1. build txBody locally, commit = blake2b256(txBody)    |
     |                                                          |
     |  2. UIApplication.open(                                  |
     |       https://lace.io/cip30dl/v1/signTx?                 |
     |         v=1&dappKey=...&redirect=aegis://cb              |
     |         &nonce=...&commit=...&ttl=...&payload=enc(tx) )  |
     +---- Universal Link --------------------------------------->
     |                                                          |
     |                                          3. OS launches  |
     |                                          Lace; Lace      |
     |                                          decrypts payload|
     |                                          verifies commit |
     |                                          shows tx UI     |
     |                                          user taps Sign  |
     |                                                          |
     |   4. UIApplication.open(                                 |
     |        aegis://cb?response=approved                      |
     |          &nonce=...&payload=enc(witnessSet) )            |
     <-----------------------------------------------------------+
     |                                                          |
     |  5. dApp decrypts, re-verifies commit, assembles signed  |
     |     tx, POSTs to its own /api/tx/submit                  |
     |                                                          |
```

### Versioning

The `v` URL parameter (e.g. `v=1`) carries the protocol version. Wallets and dApps MUST encode it as a
decimal integer with no leading zeros.

- The current protocol version is `v=1`. All methods, parameters, error codes, and JSON payload
  shapes defined in this document constitute version 1.
- A wallet that receives a request whose `v` it does not implement MUST reject with
  `errorCode=-9 UnsupportedVersion` and MUST NOT attempt a best-effort parse.
- Backwards-compatible additions (new OPTIONAL methods, new OPTIONAL keys in existing JSON payloads
  that older implementations can safely ignore) remain at `v=1` and SHOULD be guarded by a
  capabilities advertisement returned in `connect`'s session JSON.
- Any breaking change &mdash; renaming a key, changing a value's encoding, narrowing an enum, repurposing
  an existing error code, altering the commit-binding algorithm, or changing the encryption suite &mdash;
  MUST increment the version to `v=2` and be specified in a successor CIP. dApps MUST then send
  `v=2`; legacy `v=1` wallets will respond with `UnsupportedVersion` and the dApp can fall back.
- The version negotiation is one-shot: the dApp picks `v` per request. There is no in-band downgrade
  handshake; if the dApp wants both, it sends `v=2` first and on `-9` rebuilds the same request as
  `v=1`.

### Unknown-key policy

CIP-30-DeepLink intentionally splits unknown-field handling by boundary, mirroring the TLS-extensions
pattern (critical-by-default at the wire layer, lenient at the application layer) rather than the
permissive HTTP/Postel convention. The two layers have different threat models and require
different defaults.

- **URL-level (transport boundary) &mdash; strict reject.** A wallet MUST reject any request URL that
  contains a query-string `key` not listed in the `request-key` ABNF production for the wallet's
  implemented version, with `errorCode=-9 UnsupportedVersion` and an `errorMessage` naming the
  offending key. A dApp MUST apply the same strict-reject rule against any response URL it receives
  that contains a key not listed in the `response-key` ABNF production. Every URL parameter in this
  protocol carries security-sensitive state (`redirect` host binding, `nonce` replay window,
  `commit` binding, encrypted `payload`, `ttl` window, `signature` authenticity). Silent ignore at
  this layer would let an attacker smuggle additional state past the parser without surfacing in
  the user-visible signing UI. The wallet's and the dApp's own ABNF parsers MUST be the gate.

- **JSON-payload-level (application boundary) &mdash; lenient ignore.** A wallet and dApp MUST tolerate
  unknown fields inside the encrypted JSON payload (`signTx-json`, `session-json`, etc.) and
  silently drop them after decrypt. The encrypted payload is already authenticated by NaCl box; new
  fields here are reserved for future minor versions of the spec and adding one MUST be a
  backwards-compatible change (no rename, no semantic re-use, OPTIONAL only). dApps MAY use this
  channel for vendor-specific advisory metadata (e.g. dApp-supplied hints to the wallet's signing
  UI like `"highlightedFeeBreakdown": [...]`) that wallets MAY display but MUST NOT treat as
  load-bearing.

This split is the load-bearing reason a wallet can refuse a URL with an unrecognised key and still
support forward-compatible application-layer evolution. It mirrors how TLS handles unknown
extensions (ignore unless critical-bit set), how HSTS handles unknown directives (ignore), and how
HTTP/3 frames handle unknown frame types (drop without close). The CIP rejects the unqualified
Postel rule because every URL key here is in the critical set.

## Rationale: How does this CIP achieve its goals?

**Why borrow Phantom/Petra over Solana MWA?** Solana MWA optimises for *high-throughput in-app gaming*
(Saga phone) and pays for that with WebSocket transport, an association keypair, and a 30-second
reflector wait on remote. Cardano's dApp tempo (insurance buys, lending borrows, governance votes,
DEX swaps) is closer to Phantom's: one sign-per-action, latency tolerable up to a second, primary
device is the user's phone. Phantom and Petra both ship a deep-link protocol of the exact shape
proposed here and both have years of mainnet evidence that it works.

**Why Universal Links primary, custom-scheme fallback?** Custom schemes (`metamask://`) suffer the
well-documented hijacking risk: any app can register `metamask://` after install and capture the
redirect. Universal Links bind the path to a domain claim that the OS verifies via AASA. The
custom-scheme fallback is retained only for the install-but-no-AASA-yet edge case and is rate-limited
by the `redirect` host binding (a hijacker can launch the wallet but cannot redirect anywhere except
the legitimate dApp's bundle ID).

**Why encrypt the payload when the URL is already HTTPS?** Because the URL is *also* visible to the
OS, the app switcher, Shortcuts automations, and any screen recorder. Encryption ensures the only
place the transaction CBOR exists in plaintext is inside the wallet process after decryption &mdash; the
same place CIP-30 puts it.

**Why a commit hash separate from the encrypted payload?** Defence in depth. If NaCl is ever broken,
or if the dApp's encryption keypair is leaked, the commit-hash check still prevents an attacker from
substituting a transaction. Conversely, if the commit field is ever stripped or manipulated, the
wallet will see a mismatch with its own re-computed hash and reject. Two independent checks; no
single point of failure.

**Why not just use CIP-45 or WalletConnect?** [CIP-45](https://cips.cardano.org/cip/CIP-45)
(Decentralized WebRTC dApp-Wallet Communication, Active) uses WebTorrent trackers for peer
discovery (CIP-45:42-67), avoiding a central signaling server, then opens a WebRTC channel for RPC.
WalletConnect uses a hosted relay. Both keep a persistent session open between the two peers,
which is the right shape for desktop-browser-to-mobile-wallet (no shared OS to deep-link through)
and for cross-device hand-offs. For same-device mobile-to-mobile, the persistent channel is
overhead: the dApp does not need a stateful session, it needs one signature and a callback.
CIP-30-DeepLink handles the same-device case with no relay, no peer-discovery tracker, and no
WebRTC stack. CIP-45 (cross-device, persistent) and CIP-30-DeepLink (same-device, one-shot) are
complementary entries in a wallet's transport menu, both addressing CPS-0010 from different
angles.

**Why a separate CIP rather than extending CIP-30?** CIP-30 is the JavaScript-injection contract;
extending it with URI-encoded methods would muddy its scope. This CIP cites CIP-30 by reference for
method semantics (`signTx` does exactly what CIP-30 `signTx` does) and only specifies the transport.
The shape mirrors CIP-30's spirit while keeping it independently versionable.

### Answers to CPS-0010 Open Questions

[CIP-9999](https://cips.cardano.org/cip/CIP-9999) (CPS Process, Active) requires that a CIP claiming
to solve a CPS provide argued answers to the CPS's Open Questions in its Rationale (CIP-9999:48
"Solutions in the form of CIP should thereby include these questions as part of their *Rationale*
section and provide an argued answer to each"). CPS-0010 lists four Open Questions
(CPS-0010:283-300):

**Q1 (CPS-0010:285): Can a universal connector be pursued?** Partially yes, in layers.
CIP-30-DeepLink is a *transport* layer that is API-agnostic &mdash; the same encrypted JSON payloads
used here can carry CIP-30 base methods, CIP-95 governance methods, CIP-103 bulk-signing methods, or
any future CIP-30-extension method without changing the transport. A universal connector emerges
when CIP-30 + CIP-45 + CIP-30-DeepLink are all implemented by a wallet: browser-extension dApps use
CIP-30, cross-device dApps use CIP-45, same-device mobile dApps use CIP-30-DeepLink.

**Q2 (CPS-0010:289): Can a universal API be pursued?** Outside the scope of this CIP. CIP-30-DeepLink
defines a transport for the existing CIP-30 method surface; it does not unify the API. A universal
API would require CIP-95 / CIP-103 / CIP-104 / CIP-106 to converge on a single namespace, which is
a governance question for the CIP editors, not a transport question for this CIP.

**Q3 (CPS-0010:294): How interoperable can standards be with those of other ecosystems?** This CIP
deliberately mirrors the Phantom (Solana) and Petra (Aptos) deep-link patterns (see the
*Motivation* table) so a developer who has built a Solana / Aptos mobile dApp can port to Cardano
with minimal cognitive load. The wire format (X25519 + XSalsa20-Poly1305, base64url, redirect
callback) is the cross-ecosystem common denominator; the Cardano-specific divergence is the
BLAKE2b-256 commit binding and the session-binding Ed25519 response signature.

**Q4 (CPS-0010:299): How can we effectively police API scope?** CIP-30-DeepLink's transport defers
method-level semantics to the source CIP (CIP-30 for `signTx`, `signData`, etc.). Scope policing is
therefore inherited: this CIP cannot accept a method that CIP-30 does not document. New methods
require a new CIP that registers the method, which is the same gate CIP-30 extensions go through
today.

## Path to Active

### Acceptance criteria

1. At least one production Cardano wallet (Lace OR Eternl OR Vespr OR Typhon OR Nami) ships
   CIP-30-DeepLink support on iOS App Store and Google Play, with both Universal Link / App Link
   claims and the `cip30dl:` custom scheme registered, and passing the conformance test suite
   referenced below.
2. At least one production Cardano dApp, independent of the wallet vendor, ships a mobile-native
   client that uses CIP-30-DeepLink to obtain signatures on at least **1,000 mainnet transactions**
   across at least **100 distinct payment addresses** over a contiguous **30-day window**. The dApp
   publishes the on-chain hashes alongside the corresponding `commit` values for reproducibility.
3. A conformance test suite covering all mandatory methods, replay rejection (`-5`),
   commit-mismatch rejection (`-2`), redirect-host binding (`-4`), payload decryption failure (`-7`),
   and unsupported-version rejection (`-9`) is published under the `cardano-foundation` organisation
   and passed end-to-end by all implementing wallets. "Passed" means **100% of the suite's mandatory
   test cases return the expected error code or success result.**
4. A second wallet implements the spec and interoperates with the same dApp without code changes on
   the dApp side (proving the spec, not the implementation, is what's standard). Interoperability is
   demonstrated by at least **10 mainnet transactions** signed by each wallet against the unchanged
   dApp.

### Implementation Plan

- Stage 1 (this PR): Draft merged. Reference TypeScript client SDK published
  (`@aegis/cip30-deeplink-client`) demonstrating the dApp side.
- Stage 2 (T+8 weeks): Vespr mobile and Yuti both publish feature-flagged builds with the
  `cip30dl-<wallet-id>` URL handler; closed beta with Flux Point Studios (Aegis). Vespr is the lead
  external wallet target because (a) Alex Dochioiu's team already publishes an open-source SDK,
  (b) Vespr's signing engine separation matches the patch shape we recommend, and (c) the team is
  responsive to CIP-aligned work.
- Stage 3 (T+12 weeks): Lace, Eternl, Typhon, Yoroi, and SecondFi review the draft against their
  signing engines; feedback merged as a v1.1 revision.
- Stage 4 (T+20 weeks): At least two production wallets ship the protocol. dApp ecosystem onboarded
  via a `CIP-30-DeepLink for dApp builders` guide.
- Stage 5 (T+24 weeks): Active.

## Appendices

### Reference Implementation

**Status at draft submission**: two reference implementations are in active development at Flux Point
Studios. Neither has shipped yet at the time this CIP is opened as Draft; both are targeted to land
inside the typical Cardano-Foundation review window for new CIPs. The spec is being published ahead
of the implementations on purpose, so that editors and other wallet teams can shape the design
before code calcifies around it.

- **dApp-side TypeScript SDK** &mdash; will be published as
  [`Flux-Point-Studios/cip30-deeplink-client`](https://github.com/Flux-Point-Studios/cip30-deeplink-client)
  (Apache-2.0 licensed, public repository created at draft submission). The SDK is consumed by the
  Aegis iOS app (Aegis itself is not open-source; only the on-chain validator suite at
  [`Flux-Point-Studios/aegis-contracts`](https://github.com/Flux-Point-Studios/aegis-contracts) is
  public). The Aegis iOS app is already wrapped with Capacitor 8 as of 2026-05-13; the deep-link
  client is the next mobile-wave deliverable. Anticipated shape:

  ```typescript
  import { DeepLinkClient } from "@fluxpoint/cip30-deeplink-client";

  const client = new DeepLinkClient({ wallet: "yuti", chain: "cardano:preprod" });
  const session = await client.connect({ name: "Aegis", url: "https://aegis.fluxpointstudios.com" });
  const { witnessSet, txHash } = await client.signTx({ tx: cborHex, partialSign: false });
  const signedTx = client.assemble(cborHex, witnessSet);
  await fetch("/api/tx/submit", { method: "POST", body: signedTx });
  ```

- **Wallet-side reference handler** &mdash; will land in [`Flux-Point-Studios/yuti`](https://github.com/Flux-Point-Studios/yuti),
  a Flutter Cardano mobile wallet (iOS deployment target 12.0, Flutter 3.4+). The receiver patch
  surface is estimated at ~290 lines across 8 files (Swift URL handler, Dart payload decrypt
  service, MethodChannel bridge, Android intent filter + Kotlin handler, AASA / assetlinks files).
  Yuti's existing CIP-30 signing engine is reused; only the deep-link transport is new. The patch
  shape is what we propose Lace, Eternl, Vespr, Typhon, Yoroi, and SecondFi could adapt against
  their own signing UIs. (Nami was archived on 2025-02-06 by Emurgo and is no longer a target.)

- **Conformance test runner** &mdash; will drive a wallet under test through
  `connect / signTx (valid) / signTx (commit mismatch &mdash; MUST reject -2) / signTx (replayed nonce &mdash; MUST reject -5) / disconnect`,
  plus the negative cases from Appendix C below. Will be published under
  [`Flux-Point-Studios/cip30-deeplink-conformance`](https://github.com/Flux-Point-Studios/cip30-deeplink-conformance)
  (repository to be created alongside the first conformance pass); if editors prefer a
  vendor-neutral home under `cardano-foundation/` we will migrate.

The spec authors will surface real preprod transaction hashes (Aegis &harr; Yuti) and the conformance
test pass status to the Discussions thread on this PR as those milestones land, so editors can track
progress empirically rather than on promises.

### Appendix A &mdash; Error codes

These codes appear ONLY in the deep-link callback URL's `errorCode` parameter. They form a separate
code space from CIP-30's `APIErrorCode` enum (CIP-30:113-118), which uses integer values -1..-4
inside the JavaScript `APIError.code` field. The numeric overlap is intentional in spirit &mdash;
both spaces start at -1 and decrement &mdash; but the two spaces are never composed: a
CIP-30-DeepLink wallet never returns a CIP-30 `APIError` JSON object, and a CIP-30 browser bridge
never returns a deep-link `errorCode` URL parameter. dApps that consume both surfaces MUST keep the
two error tables namespaced in their codebase.

| Code | Name                     | Meaning                                                       |
|------|--------------------------|---------------------------------------------------------------|
| -1   | UserRejected             | User dismissed the signing prompt                             |
| -2   | CommitMismatch           | `commit` URL param did not match `BLAKE2b-256(tx_body)`       |
| -3   | SessionExpired           | `session` is unknown or `expiresAt < now`                     |
| -4   | RedirectHostMismatch     | `redirect` host differs from `connect`-time `dapp-info.url`   |
| -5   | NonceReplay              | `(dappKey, nonce)` was seen within `ttl + 600s`               |
| -6   | TtlExpired               | `ttl < now`                                                   |
| -7   | DecryptFailed            | `payload` failed NaCl box authentication                      |
| -8   | UnsupportedChain         | Wallet does not have an account on the requested chain        |
| -9   | UnsupportedVersion       | `v` is not understood by the wallet, OR URL contains unknown query-string key |
| -10  | ResponseSignatureInvalid | dApp-side: Ed25519 verification of `signature` failed against `session.signingPublicKey` (for `connect`, against the `signingPublicKey` inside the just-decrypted payload), or a `connect` response is missing `method=connect`/`signature`/`echo` |
| -11  | AuxiliaryDataHashMismatch | `auxiliary_data_hash` in `transaction_body` did not match the supplied `auxiliary_data`, OR a hash is present without data, OR data is present without a hash |
| -12  | SessionEntropyReuse      | Wallet detected `session_entropy` reuse across `connect` events for the same `dapp_host` |
| -13  | SourceAppUnverified      | Source app's bundle ID could not be verified against the `redirect` host's AASA / `assetlinks.json` |
| -14  | UseInjectedAPI           | Request originated from a WebView hosted by the wallet; dApp MUST use the injected CIP-30 surface instead |
| -32  | PayloadTooLarge          | Request URL exceeded the wallet's accepted size               |
| -100 | InternalError            | Wallet bug or unrecoverable state                             |

### Appendix B &mdash; Wallet registry (v1 draft, advisory)

Maintained as `wallet-registry.json` and `wallet-registry.schema.json` in the CIP folder, matching
the [CIP-10](https://cips.cardano.org/cip/CIP-10) registry-file pattern. **This central registry is
ADVISORY-ONLY, never normative.** Wallets MUST NOT be required to appear in the registry to be
conformant, and no implementation may treat it as a source of truth for a wallet's protocol
commitments; the registry exists purely so dApps that want to compile a static "wallet picker" have
a single human-curated starting list. The NORMATIVE, runtime-authoritative source is the
origin-anchored vendor-attestation manifest each wallet publishes under a well-known path on its own
domain, `https://<wallet-domain>/.well-known/cip30dl-attestation.json` (see *Vendor attestation
manifest*), resolved at runtime. This decouples the registry's editorial maintenance from the
protocol's correctness, and means wallets that join after v1.0 do not require a CIP-editor merge to
be usable.

`wallet-registry.json`:

```json
[
  { "id": "lace",   "scheme": "cip30dl-lace",   "https": "https://lace.io/cip30dl/v1/" },
  { "id": "eternl", "scheme": "cip30dl-eternl", "https": "https://eternl.io/cip30dl/v1/" },
  { "id": "vespr",  "scheme": "cip30dl-vespr",  "https": "https://vespr.xyz/cip30dl/v1/" },
  { "id": "yuti",   "scheme": "cip30dl-yuti",   "https": "https://yuti.fluxpointstudios.com/cip30dl/v1/" }
]
```

`wallet-registry.schema.json` (JSON-schema-draft-07, `additionalProperties: false`,
`required: [id, scheme, https]`) MUST be enforced on every registry-modifying PR. The schema
enforces lowercase ASCII `id`, per-wallet `scheme` matching `^cip30dl-[a-z0-9][a-z0-9_-]{0,30}[a-z0-9]$`,
and HTTPS-only `https` value with the trailing slash. The schema file is shipped in the same PR
that introduces the registry. New wallet entries are added by PR against this folder.

Per-wallet schemes (`cip30dl-lace:`, `cip30dl-eternl:`, ...) prevent the "shared scheme hijack"
class of attack where any installed app can register the bare `cip30dl:` scheme and intercept
fallback URIs intended for a specific wallet. The HTTPS form uses each wallet's own domain so
Universal Link claims do not collide.

### Appendix C &mdash; Test vectors

The keys, nonces, addresses, and CBOR below are obviously fake (the dapp X25519 key is `01` repeated
32 times) but the shape and encoding is exactly what a conforming implementation MUST accept or
reject. Linebreaks in URLs are for readability only; on the wire each URL is a single line.

#### C.1 Valid `connect` request and response

dApp constants:

- `dappKey` (X25519 public, 32 bytes hex): `0101010101010101010101010101010101010101010101010101010101010101`
- base64url(`dappKey`): `AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE`
- `nonce` (24 bytes hex): `020202020202020202020202020202020202020202020202`
- base64url(`nonce`): `AgICAgICAgICAgICAgICAgICAgICAgIC`
- `dapp-info-json` minified: `{"name":"Aegis","url":"https://aegis.example","iconUrl":"https://aegis.example/icon.png"}`
- base64url(`dapp-info-json`):
  `eyJuYW1lIjoiQWVnaXMiLCJ1cmwiOiJodHRwczovL2FlZ2lzLmV4YW1wbGUiLCJpY29uVXJsIjoiaHR0cHM6Ly9hZWdpcy5leGFtcGxlL2ljb24ucG5nIn0`

Request URL (line-wrapped for display only):

```text
https://lace.io/cip30dl/v1/connect
  ?v=1
  &dapp=eyJuYW1lIjoiQWVnaXMiLCJ1cmwiOiJodHRwczovL2FlZ2lzLmV4YW1wbGUiLCJpY29uVXJsIjoiaHR0cHM6Ly9hZWdpcy5leGFtcGxlL2ljb24ucG5nIn0
  &dappKey=AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE
  &redirect=https%3A%2F%2Faegis.example%2Fcb
  &chain=cardano%3Apreprod
  &nonce=AgICAgICAgICAgICAgICAgICAgICAgIC
```

Response URL (wallet appends to the dApp's redirect; `walletKey`, `nonce`, `payload`, and
`signature` are deterministic-looking but illustrative, NOT cryptographically real). Note the
`signature` parameter MUST be the FINAL key; it covers the canonical form of the URL with the
`signature` parameter itself removed. `method=connect` is the domain-separation tag and `echo` is
the request's `nonce` copied back verbatim.

```text
https://aegis.example/cb
  ?response=approved
  &method=connect
  &walletKey=AwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM
  &nonce=BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE
  &echo=AgICAgICAgICAgICAgICAgICAgICAgIC
  &payload=ZXhhbXBsZS1jaXBoZXJ0ZXh0LWZvci1zZXNzaW9uLWpzb24
  &signature=ZmFrZS1lZDI1NTE5LXNpZ25hdHVyZS1leGFtcGxlLWZvci1jb25uZWN0LXJlc3BvbnNl
```

After NaCl box decryption with `(dappKey-secret, walletKey, nonce=wallet-nonce)`, the dApp obtains:

```json
{
  "session":          "c2Vzc2lvbi1pZC0wMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA",
  "network":          0,
  "addresses":        ["addr_test1qz...exampleAEgis0000000000000000000000000000000000000000000000000"],
  "chain":            "cardano:preprod",
  "walletId":         "lace",
  "expiresAt":        1810000000,
  "signingPublicKey": "c2Vzc2lvbi12a2V5LWVkMjU1MTktZXhhbXBsZS0zMi1ieXRlcy0wMA"
}
```

The dApp MUST verify the `signature` parameter against `session.signingPublicKey` BEFORE trusting
any field in the session JSON. Verification subject is the canonical-form response URL with the
`&signature=...` suffix stripped. The dApp MUST additionally reject the response with
`errorCode=-10 ResponseSignatureInvalid` if `method=connect`, `signature`, or `echo` is absent, and
with `errorCode=-5 NonceReplay` if a present `echo` does not equal the `nonce` the dApp sent in the request. A
byte-exact, cryptographically real known-answer vector for this flow (fixed keys/nonces &rArr;
reproducible `signature` and response URL, plus the `-5` / `-10` negatives) is published in the
reference implementation and exercised by `tests/vectors/sign_006_canonical_subject_connect_method_echo.json`.

#### C.2 Valid `signTx` request and response

Assume `tx_body` CBOR is the 32-byte zero word repeated; its BLAKE2b-256 is the deterministic
fake-but-shape-correct value below (in a real test vector the wallet recomputes and matches).

- `commit` (32 bytes hex): `0000000000000000000000000000000000000000000000000000000000000000`
- base64url(`commit`): `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`
- `ttl` (unix seconds): `1810000300`
- `nonce` (24 bytes): base64url `BQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUF`
- `payload`: base64url of `nacl.box({"session":"c2Vzc2lvbi1pZC0...","tx":"<base64url(tx_cbor)>","partialSign":false,"vkeyHints":[]})`
  &mdash; for the test vector the dApp transmits the literal token below as a stand-in:
  `cGF5bG9hZC1zaWdudHgtdmFsaWQtZml4dHVyZS1iYXNlNjR1cmw`

Request URL:

```text
https://lace.io/cip30dl/v1/signTx
  ?v=1
  &dappKey=AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE
  &redirect=https%3A%2F%2Faegis.example%2Fcb
  &nonce=BQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUF
  &commit=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
  &ttl=1810000300
  &payload=cGF5bG9hZC1zaWdudHgtdmFsaWQtZml4dHVyZS1iYXNlNjR1cmw
```

Expected response (success). The `signature` parameter is appended LAST and signs the canonical
form of the URL with the `signature` suffix removed:

```text
https://aegis.example/cb
  ?response=approved
  &nonce=BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYG
  &payload=cmVzdWx0LXdpdG5lc3Mtc2V0LWNpcGhlcnRleHQtYmFzZTY0dXJs
  &signature=ZmFrZS1lZDI1NTE5LXNpZ25hdHVyZS1zaWdudHgtcmVzcG9uc2UtY29ucnJ0
```

Decrypted `result-json`:

```json
{
  "commit":     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
  "witnessSet": "<base64url(CBOR of transaction_witness_set)>",
  "txHash":     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
}
```

The dApp verifies the `signature` against the `session.signingPublicKey` it received during
`connect`. If verification fails, the dApp MUST treat the response as if it never arrived,
discard the witness set, and surface `errorCode=-10 ResponseSignatureInvalid` to the user.

#### C.3 `signTx` that MUST be rejected with `errorCode=-2 CommitMismatch`

This request is byte-identical to C.2 *except* that `commit` is the all-ones word instead of the
all-zeros word. The encrypted `payload` still carries the all-zeros `tx_body`, so when the wallet
decrypts and recomputes `BLAKE2b-256(tx_body)` it gets the all-zeros commit, which disagrees with the
URL `commit`. The wallet MUST reject before showing the signing UI.

Request URL (note `commit=____________________________________________8`, base64url of 32 bytes of
`0xFF`):

```text
https://lace.io/cip30dl/v1/signTx
  ?v=1
  &dappKey=AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQE
  &redirect=https%3A%2F%2Faegis.example%2Fcb
  &nonce=BQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUF
  &commit=_____________________________________________w
  &ttl=1810000300
  &payload=cGF5bG9hZC1zaWdudHgtdmFsaWQtZml4dHVyZS1iYXNlNjR1cmw
```

Required wallet response:

```text
https://aegis.example/cb
  ?response=rejected
  &errorCode=-2
  &errorMessage=commit%20mismatch
```

A conformance suite that submits this exact URL MUST observe `response=rejected` and
`errorCode=-2`. The wallet MUST NOT render its signing UI for this request.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
