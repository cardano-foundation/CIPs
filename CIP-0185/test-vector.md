# Test Vector for CIP-0185

## Common Context

- JSON-LD context: [cip-0185.common.jsonld](./cip-0185.common.jsonld)
- JSON Schema: [cip-0185.common.schema.json](./cip-0185.common.schema.json)

## Author

This is the key published by [CIP-0100](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/test-vector.md) and [CIP-0108](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0108/test-vector.md). It MUST NOT be used for anything but tests.

- Private extended signing key (hex): `105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652`
- Public verification key (hex): `7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a`
- Public key hash (blake2b-224, hex): `0fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`
- Mainnet reward account with that key hash: `stake1uy8ac7qqy0vtulyl7wntmsxc6wex80gvcyjy33qffrhm7ssz4x9un`

## Example

[examples/update.jsonld](./examples/update.jsonld) is a `Clarification` signed by the author above. It is author-complete if, for the purposes of this vector, that key is the only member of `O`.

- Blake2b-256 of the file content (the anchor's `dataHash`): `d48431b0d0d50febbd099b19e125bcb74fa11bbb058a01a0eeb0532766d8cbe9`
- Canonicalized body: [examples/update.body.nq](./examples/update.body.nq)
- Blake2b-256 of the canonicalized body (the signed payload): `632bc7dce83652ea9f21bbfe8e819405e31de1af6bde583ba2e3c7e197298c49`
- Signature: `688fa6c2c3387cf4389498ede928b34a7daf35a80534b179cb769748a1fdbff6b1962cf191c821c562cbba82daef1ac90463492bd38219a5fc61da4f57b68402`

The body is canonicalized as in CIP-0108: keep only `@context` and `body`, canonicalize, and hash the result including its final newline.

### Governance action ID

- Signed form: `gov_action1g4rurffw7f7neduyc0e6p0c259tqpm59j6fknwsfgk7dsns068esqxgylar`
- Transaction hash: `4547c1a52ef27d3cb784c3f3a0bf0aa15600ee85969369ba0945bcd84e0fd1f3`
- Index: `0`

### On-chain anchor

The URI is the IPFS address of [examples/update.jsonld](./examples/update.jsonld): the CIDv1 (raw codec, sha2-256, base32) of its exact bytes as a single block. It is 66 bytes long, so it is split after 64. The file is not necessarily pinned, so the address may not resolve.

```json
{
  "1694": {
    "@type": "GovernanceActionUpdateAnchor",
    "txHash": "4547c1a52ef27d3cb784c3f3a0bf0aa15600ee85969369ba0945bcd84e0fd1f3",
    "index": 0,
    "dataHash": "d48431b0d0d50febbd099b19e125bcb74fa11bbb058a01a0eeb0532766d8cbe9",
    "uri": [
      "ipfs://bafkreih34yxtgpcxywdqij3wbk35jhkzk7ai3jozfvqbjywbtevpmj5m",
      "o4"
    ]
  }
}
```

## Deposit return account fallback

The same document is a deposit-account update if, for the purposes of this vector, the original metadata is verified and has no valid author witness, and the action's deposit return account is `stake1uy8ac7qqy0vtulyl7wntmsxc6wex80gvcyjy33qffrhm7ssz4x9un`. The public key in the witness hashes to the account's credential. The result is labelled "signed by the deposit return account" and is never author-complete.

## Negative cases

Each case changes one thing in the vector above.

| Change | Expected result |
| --- | --- |
| The anchor's `index` is `1` | Action mismatch: not a verified update to either action |
| `updateContext` is edited after signing, and `dataHash` is recomputed | Hash matches, witness invalid: not an author update |
| The file is edited and `dataHash` is kept | Hash mismatch: not a verified update |
| `O` is empty, and the return account is a different key | Unverified: neither an author update nor a deposit-account update |
| `O` is empty, and the return account has a script credential | Unverified: no fallback in this version |
| `O` contains only another key, and the return account is the one above | Unverified: the fallback does not apply when there are signed authors |
| The original metadata is unavailable, and the return account is the one above | Warning: signed by the deposit return account, authors unknown |
| `O` contains a second key that did not sign | Verified author update, not author-complete |
| `@context` is `[cip-0185, cip-0100]` | CIP-0185 body fields are not covered by signatures: warn |
| The same anchor is submitted again in a later transaction | One update, no sequence conflict |
