# CIP-0186 conformance suite

Canonical test vectors + verifier for [CIP-0186](../README.md) wallet implementations.

## Install

```sh
cd CIP-0186/tests
npm install
```

## Verify a wallet implementation

1. Implement the `WalletAdapter` interface in `verify.ts`:

   - `decodeUrl(url) -> DecodeResult` — parse CIP-0186 deep-link URI.
   - `decodeBase64Url(s) -> bytes` — strict base64url (no padding, alphabet-only, canonical tail bits).
   - `blake2b256(bytes) -> 32 bytes` — commit hash.
   - `extractTxBody(tx_cbor) -> bytes` — element 0 of Conway transaction array.
   - `mergeWitnessSet(tx, ws) -> tx` — splice wallet witness set into outer transaction.
   - `canonicalSubject(input) -> bytes` — Response-signing canonical form (§Response signing).
   - `checkReplay(input) -> {accepted | errorCode}` — `(dappKey, nonce)` + `ttl` enforcement.

2. Run the verifier against your adapter:

   ```ts
   import { verifyImplementation } from "./verify.ts";
   import { myAdapter } from "./my-wallet-adapter.ts";
   const result = verifyImplementation(myAdapter);
   ```

3. Or run the supplied reference stub end-to-end:

   ```sh
   npx tsx verify.ts
   ```

   Exits non-zero if any vector fails. Per-vector pass/fail prints to stdout.

## What ships

- `vectors/*.json` — 57 canonical vectors across 13 spec paths. Every vector cites the spec section it exercises.
- `verify.ts` — the verifier. `verifyImplementation(impl)` returns per-vector results.
- `reference-impl-stub.ts` — minimal correct adapter. Documentation-by-running-code; not a production implementation.
- `package.json` — pins `@noble/hashes`, `ajv`, `tweetnacl`, `tsx`.

## Coverage

Negative vectors are 34/57. Categories covered: deep-link decode, base64url strict-decode, attestation manifest, wallet registry, CBOR commit + tx-body extraction, witness-set splice, response-signing canonical subject, replay/nonce/TTL, every error code in Appendix A, every method JSON shape from §Methods.
