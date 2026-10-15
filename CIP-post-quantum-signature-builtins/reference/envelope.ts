export const ENVELOPE_VERSION = 0x01;

export type AlgClass = 'signature' | 'kem' | 'commitment';

export const KIND = {
  publicKey: 0x01,
  signature: 0x02,
  commitment: 0x03,
  ciphertext: 0x04,
  seed: 0x05,
} as const;

export type Kind = (typeof KIND)[keyof typeof KIND];

type Lengths = {
  publicKey?: number;
  signature?: number | { min: number; max: number };
  seed?: number;
  ciphertext?: number;
  commitment?: number;
};

type Entry = { name: string; cls: AlgClass; lengths: Lengths };

export const REGISTRY: ReadonlyMap<number, Entry> = new Map<number, Entry>([
  [0x0001, { name: 'ML-DSA-44', cls: 'signature', lengths: { publicKey: 1312, signature: 2420, seed: 32 } }],
  [0x0002, { name: 'ML-DSA-65', cls: 'signature', lengths: { publicKey: 1952, signature: 3309, seed: 32 } }],
  [0x0003, { name: 'ML-DSA-87', cls: 'signature', lengths: { publicKey: 2592, signature: 4627, seed: 32 } }],
  [0x0004, { name: 'SLH-DSA-SHA2-128s', cls: 'signature', lengths: { publicKey: 32, signature: 7856 } }],
  [0x0005, { name: 'FN-DSA-512', cls: 'signature', lengths: { publicKey: 896, signature: { min: 617, max: 666 } } }],
  [0x0101, { name: 'ML-KEM-768', cls: 'kem', lengths: { publicKey: 1184, ciphertext: 1088 } }],
  [0x0201, { name: 'SHA3-256', cls: 'commitment', lengths: { commitment: 32 } }],
  [0x0202, { name: 'KECCAK-256', cls: 'commitment', lengths: { commitment: 32 } }],
]);

const KIND_CLASSES: Record<number, AlgClass[]> = {
  [KIND.publicKey]: ['signature', 'kem'],
  [KIND.signature]: ['signature'],
  [KIND.commitment]: ['commitment'],
  [KIND.ciphertext]: ['kem'],
  [KIND.seed]: ['signature'],
};

const KIND_FIELD: Record<number, keyof Lengths> = {
  [KIND.publicKey]: 'publicKey',
  [KIND.signature]: 'signature',
  [KIND.commitment]: 'commitment',
  [KIND.ciphertext]: 'ciphertext',
  [KIND.seed]: 'seed',
};

export class EnvelopeError extends Error {}

function rule(algId: number, kind: number): number | { min: number; max: number } {
  const entry = REGISTRY.get(algId);
  if (entry === undefined || algId === 0x0000) {
    throw new EnvelopeError('unknown algorithm identifier');
  }
  const classes = KIND_CLASSES[kind];
  if (classes === undefined || !classes.includes(entry.cls)) {
    throw new EnvelopeError('object kind not valid for this scheme');
  }
  const len = entry.lengths[KIND_FIELD[kind]];
  if (len === undefined) {
    throw new EnvelopeError('object kind not supported by this scheme');
  }
  return len;
}

function lengthOk(len: number, r: number | { min: number; max: number }): boolean {
  return typeof r === 'number' ? len === r : len >= r.min && len <= r.max;
}

export function encode(algId: number, kind: Kind, body: Uint8Array): Uint8Array {
  const r = rule(algId, kind);
  if (!lengthOk(body.length, r)) {
    throw new EnvelopeError('body length does not match the registry rule');
  }
  const out = new Uint8Array(4 + body.length);
  out[0] = ENVELOPE_VERSION;
  out[1] = (algId >>> 8) & 0xff;
  out[2] = algId & 0xff;
  out[3] = kind;
  out.set(body, 4);
  return out;
}

export function decode(envelope: Uint8Array): { algId: number; kind: number; name: string; body: Uint8Array } {
  if (envelope.length < 4) {
    throw new EnvelopeError('envelope shorter than the four byte header');
  }
  if (envelope[0] !== ENVELOPE_VERSION) {
    throw new EnvelopeError('unsupported envelope version');
  }
  const algId = (envelope[1] << 8) | envelope[2];
  const kind = envelope[3];
  const r = rule(algId, kind);
  const body = envelope.subarray(4);
  if (!lengthOk(body.length, r)) {
    throw new EnvelopeError('body length does not match the registry rule');
  }
  return { algId, kind, name: REGISTRY.get(algId)!.name, body };
}
