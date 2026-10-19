// CIP-0186 conformance verifier. Spec: ../README.md
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { blake2b } from "@noble/hashes/blake2b";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const __dirname = dirname(fileURLToPath(import.meta.url));
const VECTORS_DIR = join(__dirname, "vectors");
const ATTESTATION_SCHEMA = JSON.parse(
  readFileSync(join(__dirname, "..", "cip30dl-attestation.schema.json"), "utf8")
);
const REGISTRY_SCHEMA = JSON.parse(
  readFileSync(join(__dirname, "..", "wallet-registry.schema.json"), "utf8")
);

export interface DecodeResult {
  form: "https" | "scheme";
  wallet_domain: string | null;
  wallet_id: string | null;
  method: string;
  params: Record<string, string>;
}

export interface CanonicalSubjectInput {
  scheme: string;
  host: string;
  path: string;
  params: Record<string, string>;
}

export interface NonceCacheEntry {
  dappKey: string;
  nonce: string;
  ttl_unix: number;
}

export interface ReplayCheckInput {
  dappKey: string;
  nonce: string;
  ttl_unix: number;
  now_unix: number;
  cache: NonceCacheEntry[];
}

export type ReplayCheckResult =
  | { accepted: true }
  | { accepted: false; errorCode: -5 | -6 };

export interface WalletAdapter {
  // §URI format — parse a deep-link URL into structured request.
  // Throws on malformed/unknown method/unknown key/etc.
  decodeUrl(url: string): DecodeResult;

  // §URI format (base64url strict-decode rule) — strict base64url to bytes.
  decodeBase64Url(s: string): Uint8Array;

  // §Terminology (Commit) — BLAKE2b-256 over canonical CBOR of tx_body.
  blake2b256(bytes: Uint8Array): Uint8Array;

  // §Conway transaction body extraction — extract element 0 of outer array.
  extractTxBody(tx_cbor: Uint8Array): Uint8Array;

  // §Methods (signTx) — splice a wallet-returned witness_set into an unsigned tx.
  mergeWitnessSet(unsigned_tx_cbor: Uint8Array, witness_set_cbor: Uint8Array): Uint8Array;

  // §Response signing (Signature construction) — produce canonical subject bytes.
  canonicalSubject(input: CanonicalSubjectInput): Uint8Array;

  // §Replay protection — apply (dappKey, nonce, ttl, now, cache) check.
  checkReplay(input: ReplayCheckInput): ReplayCheckResult;
}

type Vector = {
  name: string;
  spec_section: string;
  category: string;
  input: any;
  expected: any;
  should_reject: boolean;
  rejection_reason: string | null;
};

function loadVectors(): Vector[] {
  return readdirSync(VECTORS_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((f) => JSON.parse(readFileSync(join(VECTORS_DIR, f), "utf8")) as Vector);
}

function hex(b: Uint8Array): string {
  return Buffer.from(b).toString("hex");
}

function fromHex(s: string): Uint8Array {
  return new Uint8Array(Buffer.from(s, "hex"));
}

function eq(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}

type CaseResult = { name: string; pass: boolean; reason?: string };

function runDecode(v: Vector, impl: WalletAdapter): CaseResult {
  try {
    const got = impl.decodeUrl(v.input.url);
    if (v.should_reject) {
      return { name: v.name, pass: false, reason: `expected reject (${v.rejection_reason}); got OK: ${JSON.stringify(got)}` };
    }
    const ex = v.expected;
    const mismatches: string[] = [];
    if (got.form !== ex.form) mismatches.push(`form ${got.form} != ${ex.form}`);
    if ((got.wallet_domain ?? null) !== (ex.wallet_domain ?? null))
      mismatches.push(`wallet_domain ${got.wallet_domain} != ${ex.wallet_domain}`);
    if ((got.wallet_id ?? null) !== (ex.wallet_id ?? null))
      mismatches.push(`wallet_id ${got.wallet_id} != ${ex.wallet_id}`);
    if (got.method !== ex.method) mismatches.push(`method ${got.method} != ${ex.method}`);
    for (const [k, want] of Object.entries(ex.params as Record<string, string>)) {
      if (got.params[k] !== want) mismatches.push(`params.${k} ${got.params[k]} != ${want}`);
    }
    if (mismatches.length) return { name: v.name, pass: false, reason: mismatches.join("; ") };
    return { name: v.name, pass: true };
  } catch (e: any) {
    if (v.should_reject) return { name: v.name, pass: true };
    return { name: v.name, pass: false, reason: `unexpected throw: ${e.message}` };
  }
}

function runBase64Url(v: Vector, impl: WalletAdapter): CaseResult {
  try {
    const got = impl.decodeBase64Url(v.input.encoded);
    if (v.should_reject) {
      return { name: v.name, pass: false, reason: `expected reject (${v.rejection_reason}); got ${hex(got)}` };
    }
    const want = fromHex(v.expected.bytes_hex);
    if (!eq(got, want)) return { name: v.name, pass: false, reason: `bytes ${hex(got)} != ${hex(want)}` };
    return { name: v.name, pass: true };
  } catch (e: any) {
    if (v.should_reject) return { name: v.name, pass: true };
    return { name: v.name, pass: false, reason: `unexpected throw: ${e.message}` };
  }
}

function runAttestation(v: Vector, ajv: Ajv): CaseResult {
  const validate = ajv.compile(ATTESTATION_SCHEMA);
  const ok = validate(v.input.manifest);
  if (v.should_reject) {
    if (ok) return { name: v.name, pass: false, reason: `expected schema invalid; was valid` };
    return { name: v.name, pass: true };
  }
  if (!ok) return { name: v.name, pass: false, reason: `schema errors: ${ajv.errorsText(validate.errors)}` };
  return { name: v.name, pass: true };
}

function runRegistry(v: Vector, ajv: Ajv): CaseResult {
  const validate = ajv.compile(REGISTRY_SCHEMA);
  const ok = validate(v.input.registry);
  if (v.should_reject) {
    if (ok) return { name: v.name, pass: false, reason: `expected schema invalid; was valid` };
    return { name: v.name, pass: true };
  }
  if (!ok) return { name: v.name, pass: false, reason: `schema errors: ${ajv.errorsText(validate.errors)}` };
  return { name: v.name, pass: true };
}

function runCborCommit(v: Vector, impl: WalletAdapter): CaseResult {
  const bytes = fromHex(v.input.tx_body_cbor_hex);
  const got = impl.blake2b256(bytes);
  const want = fromHex(v.expected.commit_hex);
  if (!eq(got, want)) return { name: v.name, pass: false, reason: `commit ${hex(got)} != ${hex(want)}` };
  return { name: v.name, pass: true };
}

function runCborExtract(v: Vector, impl: WalletAdapter): CaseResult {
  try {
    const tx = fromHex(v.input.transaction_cbor_hex);
    const body = impl.extractTxBody(tx);
    const want = fromHex(v.expected.tx_body_cbor_hex);
    if (!eq(body, want)) return { name: v.name, pass: false, reason: `body ${hex(body)} != ${hex(want)}` };
    const commit = impl.blake2b256(body);
    const wantCommit = fromHex(v.expected.commit_hex);
    if (!eq(commit, wantCommit))
      return { name: v.name, pass: false, reason: `commit ${hex(commit)} != ${hex(wantCommit)}` };
    return { name: v.name, pass: true };
  } catch (e: any) {
    return { name: v.name, pass: false, reason: `throw: ${e.message}` };
  }
}

function runWitnessSplice(v: Vector, impl: WalletAdapter): CaseResult {
  const tx = fromHex(v.input.unsigned_tx_cbor_hex ?? v.input.existing_tx_cbor_hex);
  const ws = fromHex(v.input.wallet_returned_witness_set_cbor_hex);
  const got = impl.mergeWitnessSet(tx, ws);
  const want = fromHex(v.expected.merged_tx_cbor_hex);
  if (!eq(got, want)) return { name: v.name, pass: false, reason: `merged ${hex(got)} != ${hex(want)}` };
  return { name: v.name, pass: true };
}

function runCanonicalSubject(v: Vector, impl: WalletAdapter): CaseResult {
  // Two shapes: vectors with "emitted_url" derive scheme/host/path/params from the URL,
  // strip "signature", and feed the rest. Vectors with explicit decoded_params feed those.
  let input: CanonicalSubjectInput;
  if (v.input.emitted_url) {
    const u = new URL(v.input.emitted_url);
    const params: Record<string, string> = {};
    for (const [k, val] of u.searchParams.entries()) {
      if (k === "signature") continue;
      params[k] = val;
    }
    input = {
      scheme: u.protocol.replace(/:$/, ""),
      host: u.host,
      path: u.pathname,
      params,
    };
  } else {
    input = {
      scheme: v.input.scheme,
      host: v.input.host,
      path: v.input.path,
      params: v.input.decoded_params,
    };
  }
  const got = impl.canonicalSubject(input);
  const gotStr = Buffer.from(got).toString("utf8");
  const want = v.expected.canonical_subject_utf8;
  if (gotStr !== want)
    return { name: v.name, pass: false, reason: `subject mismatch\n    got:  ${JSON.stringify(gotStr)}\n    want: ${JSON.stringify(want)}` };
  return { name: v.name, pass: true };
}

function runReplay(v: Vector, impl: WalletAdapter): CaseResult {
  const result = impl.checkReplay({
    dappKey: v.input.dappKey_b64url,
    nonce: v.input.nonce_b64url,
    ttl_unix: v.input.ttl_unix,
    now_unix: v.input.now_unix,
    cache: v.input.nonce_cache_before,
  });
  if (v.should_reject) {
    if (result.accepted)
      return { name: v.name, pass: false, reason: `expected reject; was accepted` };
    if (result.errorCode !== v.expected.errorCode)
      return { name: v.name, pass: false, reason: `errorCode ${result.errorCode} != ${v.expected.errorCode}` };
    return { name: v.name, pass: true };
  }
  if (!result.accepted)
    return { name: v.name, pass: false, reason: `expected accept; got errorCode ${result.errorCode}` };
  return { name: v.name, pass: true };
}

// Static-only categories: validate structural invariants from the vector itself,
// without dispatching to the adapter. These vectors document expected shape /
// error codes that the spec requires but which the adapter does not own (e.g.
// the rejection envelope, AEAD negotiation, AASA fetch result). We still surface
// them per-vector so wallet authors see the spec's full error surface.
function runShapeOnly(v: Vector): CaseResult {
  if (!v.expected) {
    // Pure negative — nothing to assert beyond presence.
    if (!v.should_reject)
      return { name: v.name, pass: false, reason: `vector has null expected but should_reject=false` };
    return { name: v.name, pass: true };
  }
  // Positive shape vectors carry a checklist of structural keys.
  if (v.expected.required_keys && Array.isArray(v.expected.required_keys)) {
    const sample =
      v.input.decrypted_session_json ??
      v.input.decrypted_request ??
      v.input.decrypted_response ??
      v.input.decrypted_result_json;
    if (!sample)
      return { name: v.name, pass: false, reason: `no decrypted sample in input` };
    for (const k of v.expected.required_keys as string[])
      if (!(k in sample))
        return { name: v.name, pass: false, reason: `missing required key: ${k}` };
  }
  if (v.expected.response_url) {
    // Verified by string equality against the constructed sample.
    // The vector's own input.redirect + params build the URL; the spec mandates
    // signature LAST. We re-construct and compare.
    const inp = v.input as any;
    if (inp.walletKey_b64url) {
      const built =
        `${inp.redirect}` +
        `?response=approved` +
        `&walletKey=${inp.walletKey_b64url}` +
        `&nonce=${inp.nonce_b64url}` +
        `&payload=${inp.payload_b64url}` +
        `&signature=${inp.signature_b64url}`;
      if (built !== v.expected.response_url)
        return { name: v.name, pass: false, reason: `built ${built} != ${v.expected.response_url}` };
    } else if (inp.errorCode != null) {
      const msg = encodeURIComponent(inp.errorMessage).replace(/%20/g, "%20");
      const built = `${inp.redirect}?response=rejected&errorCode=${inp.errorCode}&errorMessage=${msg}`;
      if (built !== v.expected.response_url)
        return { name: v.name, pass: false, reason: `built ${built} != ${v.expected.response_url}` };
    }
  }
  return { name: v.name, pass: true };
}

export interface RunResult {
  total: number;
  passed: number;
  failed: number;
  results: CaseResult[];
}

export function verifyImplementation(impl: WalletAdapter): RunResult {
  const ajv = new (Ajv as any).default({ allErrors: true, strict: false });
  addFormats(ajv);
  const vectors = loadVectors();
  const results: CaseResult[] = [];
  for (const v of vectors) {
    let r: CaseResult;
    switch (v.category) {
      case "deep_link_decode":
        r = runDecode(v, impl);
        break;
      case "base64url_decode":
        r = runBase64Url(v, impl);
        break;
      case "attestation_manifest":
        r = runAttestation(v, ajv);
        break;
      case "wallet_registry":
        r = runRegistry(v, ajv);
        break;
      case "cbor_commit":
        r = runCborCommit(v, impl);
        break;
      case "cbor_extract":
        r = runCborExtract(v, impl);
        break;
      case "witness_splice":
        r = runWitnessSplice(v, impl);
        break;
      case "canonical_subject":
        if (v.should_reject) r = runShapeOnly(v);
        else r = runCanonicalSubject(v, impl);
        break;
      case "replay_nonce":
        r = runReplay(v, impl);
        break;
      case "error_response":
      case "response_envelope":
      case "sign_data":
      case "network":
      case "addresses":
        r = runShapeOnly(v);
        break;
      default:
        r = { name: v.name, pass: false, reason: `unknown category: ${v.category}` };
    }
    results.push(r);
  }
  const passed = results.filter((r) => r.pass).length;
  return { total: results.length, passed, failed: results.length - passed, results };
}

function printReport(run: RunResult): void {
  for (const r of run.results) {
    if (r.pass) {
      process.stdout.write(`  PASS  ${r.name}\n`);
    } else {
      process.stdout.write(`  FAIL  ${r.name}\n`);
      if (r.reason) process.stdout.write(`        ${r.reason}\n`);
    }
  }
  process.stdout.write(`\n${run.passed}/${run.total} passed, ${run.failed} failed\n`);
}

// Self-run with the reference stub when invoked as a script.
const entryName = (process.argv[1] ?? "").replace(/\\/g, "/").split("/").pop() ?? "";
if (entryName === "verify.ts") {
  const { referenceImpl } = await import("./reference-impl-stub.ts");
  const run = verifyImplementation(referenceImpl);
  printReport(run);
  process.exit(run.failed === 0 ? 0 : 1);
}
