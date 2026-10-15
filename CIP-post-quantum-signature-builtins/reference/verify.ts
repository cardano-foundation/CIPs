import { ml_dsa44, ml_dsa65, ml_dsa87 } from '@noble/post-quantum/ml-dsa.js';
import { slh_dsa_sha2_128s } from '@noble/post-quantum/slh-dsa.js';
import { decode, KIND } from './envelope.ts';

const MLDSA = new Map<number, { verify: (s: Uint8Array, m: Uint8Array, p: Uint8Array) => boolean }>([
  [0x0001, ml_dsa44],
  [0x0002, ml_dsa65],
  [0x0003, ml_dsa87],
]);

function verifyWith(
  classes: Map<number, { verify: (s: Uint8Array, m: Uint8Array, p: Uint8Array) => boolean }>,
  versionedPublicKey: Uint8Array,
  message: Uint8Array,
  versionedSignature: Uint8Array,
): boolean {
  const pk = decode(versionedPublicKey);
  const sig = decode(versionedSignature);
  if (pk.kind !== KIND.publicKey || sig.kind !== KIND.signature) {
    throw new Error('object kind does not match its position');
  }
  if (pk.algId !== sig.algId) {
    throw new Error('public key and signature use different schemes');
  }
  const scheme = classes.get(pk.algId);
  if (scheme === undefined) {
    throw new Error('scheme is not a member of this builtin');
  }
  return scheme.verify(sig.body, message, pk.body);
}

export function verifyMlDsaSignature(
  versionedPublicKey: Uint8Array,
  message: Uint8Array,
  versionedSignature: Uint8Array,
): boolean {
  return verifyWith(MLDSA, versionedPublicKey, message, versionedSignature);
}

export function verifySlhDsaSignature(
  versionedPublicKey: Uint8Array,
  message: Uint8Array,
  versionedSignature: Uint8Array,
): boolean {
  return verifyWith(new Map([[0x0004, slh_dsa_sha2_128s]]), versionedPublicKey, message, versionedSignature);
}
