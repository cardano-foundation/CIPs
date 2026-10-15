# Reference implementation

Working reference for the two verification builtins proposed in this CIP.

- `envelope.ts` is the versioned encoding, the registry, the encoder and the decoder. The decoder dispatches on the declared identifier and never on body length.
- `verify.ts` implements `verifyMlDsaSignature` and `verifySlhDsaSignature` exactly as the specification defines them, over the versioned objects.
- `verify.test.ts` checks that a valid ML-DSA and SLH-DSA signature verifies, a tampered message fails, a public key and signature of different schemes are refused, and an object of the wrong scheme is refused.
- `vectors.json` is a language neutral set of valid and reject vectors for the encoding.

## Test

```
npm install
npm test
```

The in evaluator Plutus builtin and its cost model are the work of the ledger and Plutus maintainers, and their adoption requires a hardfork. This reference fixes the encoding and the verification semantics so that the builtin can be implemented against a precise target with test vectors.
