import { describe, expect, it } from 'vitest';
import { ml_dsa44, ml_dsa65, ml_dsa87 } from '@noble/post-quantum/ml-dsa.js';
import { slh_dsa_sha2_128s } from '@noble/post-quantum/slh-dsa.js';
import { encode, KIND } from './envelope.ts';
import { verifyMlDsaSignature, verifySlhDsaSignature } from './verify.ts';

const seed = Uint8Array.from({ length: 32 }, (_, i) => i);
const msg = new TextEncoder().encode('cardano post quantum builtin');

describe('post quantum verification builtins', () => {
  const cases: Array<[number, any]> = [
    [0x0001, ml_dsa44],
    [0x0002, ml_dsa65],
    [0x0003, ml_dsa87],
  ];

  it.each(cases)('ML-DSA id %s accepts a valid signature and rejects a tampered one', (algId, scheme) => {
    const k = scheme.keygen(seed);
    const sig = scheme.sign(msg, k.secretKey, { extraEntropy: false });
    const pk = encode(algId, KIND.publicKey, k.publicKey);
    const vsig = encode(algId, KIND.signature, sig);
    expect(verifyMlDsaSignature(pk, msg, vsig)).toBe(true);
    const other = new TextEncoder().encode('a different message');
    expect(verifyMlDsaSignature(pk, other, vsig)).toBe(false);
  });

  it('SLH-DSA accepts a valid signature and rejects a tampered one', () => {
    const k = slh_dsa_sha2_128s.keygen(new Uint8Array(48).fill(1));
    const sig = slh_dsa_sha2_128s.sign(msg, k.secretKey);
    const pk = encode(0x0004, KIND.publicKey, k.publicKey);
    const vsig = encode(0x0004, KIND.signature, sig);
    expect(verifySlhDsaSignature(pk, msg, vsig)).toBe(true);
    expect(verifySlhDsaSignature(pk, new TextEncoder().encode('other'), vsig)).toBe(false);
  });

  it('refuses a public key and signature of different schemes', () => {
    const k = ml_dsa44.keygen(seed);
    const sig = ml_dsa44.sign(msg, k.secretKey, { extraEntropy: false });
    const pk = encode(0x0001, KIND.publicKey, k.publicKey);
    const vsig = encode(0x0001, KIND.signature, sig);
    const k2 = ml_dsa65.keygen(seed);
    const pk2 = encode(0x0002, KIND.publicKey, k2.publicKey);
    expect(() => verifyMlDsaSignature(pk2, msg, vsig)).toThrow();
  });

  it('refuses an SLH-DSA object in the ML-DSA builtin', () => {
    const k = slh_dsa_sha2_128s.keygen(new Uint8Array(48).fill(1));
    const pk = encode(0x0004, KIND.publicKey, k.publicKey);
    const sig = encode(0x0004, KIND.signature, slh_dsa_sha2_128s.sign(msg, k.secretKey));
    expect(() => verifyMlDsaSignature(pk, msg, sig)).toThrow();
  });
});
