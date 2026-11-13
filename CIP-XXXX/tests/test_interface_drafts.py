"""Draft metadata conformance checks, not an interpreter or proof checker.
Run from the CIPs root: python3 -m unittest discover -s CIP-XXXX/tests -v
Requires jsonschema with Draft202012Validator. Schemas resolve offline.
"""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, RefResolver, ValidationError

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / 'CIP-0057/extensions/compiled-interface'
ASS = ROOT / 'CIP-XXXX'
BASE = 'https://cips.cardano.org/cips/cip57/extensions/compiled-interface/v1'
PROFILE = 'https://cips.cardano.org/cips/cipXXXX/profiles/uplc-step-check/v1'
STORE = {}
for folder in [ROOT/'CIP-0057/schemas', EXT/'schemas', ASS/'schemas']:
    for path in folder.glob('*.json'):
        schema = json.loads(path.read_text())
        STORE[schema['$id']] = schema


def reject_network(uri):
    raise ValueError('Unregistered schema; network resolution is disabled: '+uri)


def validate(schema_id, doc):
    schema = STORE[schema_id]
    resolver = RefResolver.from_schema(schema, store=STORE,
                                       handlers={'https': reject_network, 'http': reject_network})
    Draft202012Validator(schema, resolver=resolver).validate(doc)


def load(path):
    return json.loads(path.read_text())


def wire_kinds(schema, definitions, trail=()):
    if '$ref' in schema:
        key = schema['$ref'].removeprefix('#/definitions/').replace('~1', '/').replace('~0', '~')
        if key not in definitions:
            raise ValueError('unresolved schema reference')
        if key in trail:
            # The referenced root's representation is already known. Full recursive
            # encoder support is an implementation capability, not checked here.
            kind = definitions[key].get('dataType', '')
            return {kind if kind.startswith('#') else 'data'}
        return wire_kinds(definitions[key], definitions, trail+(key,))
    kind = schema.get('dataType', '')
    if kind == '#scott':
        if schema['encoding'] != BASE+'/encodings/scott-cbv-v1':
            raise ValueError('unsupported Scott profile')
        names = [c['name'] for c in schema['constructors']]
        if len(names) != len(set(names)):
            raise ValueError('duplicate constructor name')
        for c in schema['constructors']:
            for field in c['fields']:
                wire_kinds(field, definitions, trail)
    for keyword in ['oneOf', 'anyOf', 'allOf']:
        if keyword in schema:
            kinds = set().union(*(wire_kinds(s, definitions, trail) for s in schema[keyword]))
            if len(kinds) != 1:
                raise ValueError('ambiguous wire representation')
            return kinds
    # This metadata check enforces container representation, not value constraints.
    children = []
    if kind in ['list', '#list']:
        items = schema['items']; children = items if isinstance(items, list) else [items]
    if kind == 'map': children = [schema['keys'], schema['values']]
    if kind == '#pair': children = [schema['left'], schema['right']]
    if kind == 'constructor': children = schema['fields']
    for child in children:
        if wire_kinds(child, definitions, trail) != {'data'}:
            raise ValueError('container requires Data elements')
    return {kind if kind.startswith('#') else 'data'}


def description_for(description, purpose):
    options = description.get('oneOf', [description])
    matches = []
    for option in options:
        allowed = option.get('purpose')
        if allowed is None or allowed == purpose or isinstance(allowed, dict) and purpose in allowed['oneOf']:
            matches.append(option)
    if len(matches) != 1:
        raise ValueError('ambiguous or missing purpose description')
    return matches[0]


def validate_blueprint(bp):
    validate(BASE+'/schema.json', bp)
    ids = [v['id'] for v in bp['validators']]
    if len(ids) != len(set(ids)): raise ValueError('duplicate validator id')
    version = bp['preamble']['plutusVersion']
    definitions = bp.get('definitions', {})
    for schema in definitions.values(): wire_kinds(schema, definitions)
    for v in bp['validators']:
        if v['interface']['callingConvention'] != 'ledger-'+version:
            raise ValueError('language and convention disagree')
        if 'compiledCode' in v:
            actual = hashlib.blake2b(bytes([int(version[1:])])+bytes.fromhex(v['compiledCode']), digest_size=28).hexdigest()
            if actual != v['hash']: raise ValueError('compiled code hash mismatch')
        parameters = v.get('parameters', [])
        for parameter in parameters: wire_kinds(parameter['schema'], definitions)
        purposes = [i['purpose'] for i in v['interface']['invocations']]
        if len(purposes) != len(set(purposes)): raise ValueError('duplicate invocation purpose')
        for invocation in v['interface']['invocations']:
            purpose = invocation['purpose']
            if version != 'v3' and purpose in ['vote', 'propose']:
                raise ValueError('purpose is unavailable in this language')
            expected = [{'role':'parameter','source':f'/parameters/{i}'} for i in range(len(parameters))]
            roles = ['context'] if version == 'v3' else (['datum','redeemer','context'] if purpose == 'spend' else ['redeemer','context'])
            expected += [{'role':role, **({} if role == 'context' else {'source':'/'+role})} for role in roles]
            if invocation['arguments'] != expected: raise ValueError('incomplete or reordered invocation')
            for parameter in parameters: description_for(parameter, purpose)
            for role in ['redeemer'] + (['datum'] if purpose == 'spend' and (version != 'v3' or 'datum' in v) else []):
                if role not in v: raise ValueError('missing runtime description')
                desc = description_for(v[role], purpose)
                if wire_kinds(desc['schema'], definitions) != {'data'}:
                    raise ValueError('runtime payload must use Data')


def validate_context(context, bp, scope):
    validate(context['$schema'], context)
    if context['profile'] != PROFILE: raise ValueError('unsupported checking profile')
    if context['execution']['budget']['kind'] != 'cek-steps' or context['execution']['acceptance'] != 'evaluation':
        raise ValueError('unsupported execution settings for step profile')
    target_ids = [t['validator'] for t in context['targets']]
    if len(target_ids) != len(set(target_ids)) or set(target_ids) != set(scope):
        raise ValueError('target coverage mismatch')
    validators = {v['id']: v for v in bp['validators']}
    for target in context['targets']:
        if target['validator'] not in validators: raise ValueError('unknown target')
        v = validators[target['validator']]
        if target['purpose'] not in [i['purpose'] for i in v['interface']['invocations']]:
            raise ValueError('unknown invocation purpose')
        params = target['parameters']
        if params['mode'] == 'applied':
            expected = [f'/parameters/{i}' for i in range(len(v.get('parameters', [])))]
            if [x['parameter'] for x in params['values']] != expected:
                raise ValueError('parameter binding order mismatch')
            # Recomputing applied code requires the term decoder/UPLC applier.
            # These tests deliberately do not claim to establish that binding.


def read_artifact(base, reference):
    path = base/reference['uri']
    if reference['hash']['alg'] != 'sha256': raise ValueError('unsupported digest')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != reference['hash']['digest']:
        raise ValueError('artifact digest mismatch')
    return path, json.loads(data)


def validate_assurance(doc, directory):
    validate(doc['$schema'], doc)
    _, bp = read_artifact(directory, doc['blueprint'])
    validate_blueprint(bp)
    for prop in doc['properties']:
        key = prop.get('checkingContext')
        if key is None: continue
        if key not in doc.get('checkingContexts', {}): raise ValueError('unknown checking context')
        reference = doc['checkingContexts'][key]
        path, context = read_artifact(directory, reference)
        validate_context(context, bp, prop['scope']['validators'])
        read_artifact(path.parent, context['environment'])
        for evidence in prop.get('evidence', []):
            if 'checkingContextHash' in evidence and evidence['checkingContextHash'] != reference['hash']:
                raise ValueError('stale checking context')


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.bp = load(ASS/'examples/interface-game-blueprint.json')
        self.params = load(EXT/'examples/parameter-encodings.json')
        self.doc = load(ASS/'examples/interface-game-assurance.json')
        self.context = load(ASS/'examples/game-checking.json')

    def test_schema_documents(self):
        for schema in STORE.values(): Draft202012Validator.check_schema(schema)

    def test_all_assurance_examples(self):
        for path in (ASS/'examples').glob('assurance-*.json'):
            doc = load(path); validate(doc['$schema'], doc)

    def test_real_game_and_context_bindings(self):
        validate_assurance(self.doc, ASS/'examples')
        self.assertTrue(all(not p.get('evidence') for p in self.doc['properties']))
        old = load(ASS/'examples/ual-game-blueprint.json')
        self.assertEqual(old['validators'][0]['compiledCode'], self.bp['validators'][0]['compiledCode'])

    def test_parameter_representation_example(self): validate_blueprint(self.params)

    def test_data_and_native_are_distinct(self):
        self.assertNotEqual(wire_kinds({'dataType':'integer'}, {}), wire_kinds({'dataType':'#integer'}, {}))
        vectors = load(EXT/'examples/encoding-vectors.json')['vectors']
        self.assertNotEqual(vectors[0]['term'], vectors[1]['term'])

    def test_missing_extension_vocabulary(self):
        self.bp['$vocabulary'].pop(BASE+'/vocabulary')
        with self.assertRaises(ValidationError): validate_blueprint(self.bp)

    def test_old_budget_is_not_new_interface(self):
        self.bp['validators'][0]['budget'] = {'steps':500}
        with self.assertRaises(ValidationError): validate_blueprint(self.bp)

    def test_language_convention_mismatch(self):
        self.bp['validators'][0]['interface']['callingConvention'] = 'ledger-v3'
        with self.assertRaisesRegex(ValueError, 'convention'): validate_blueprint(self.bp)

    def test_v3_rejects_legacy_runtime_suffix(self):
        self.params['validators'][0]['interface']['invocations'][0]['arguments'].insert(-1, {'role':'redeemer','source':'/redeemer'})
        with self.assertRaisesRegex(ValueError, 'invocation'): validate_blueprint(self.params)

    def test_parameter_order(self):
        args = self.params['validators'][0]['interface']['invocations'][0]['arguments']
        args[0],args[1] = args[1],args[0]
        with self.assertRaisesRegex(ValueError, 'reordered'): validate_blueprint(self.params)

    def test_missing_runtime_argument(self):
        self.bp['validators'][0]['interface']['invocations'][0]['arguments'].pop()
        with self.assertRaisesRegex(ValueError, 'incomplete'): validate_blueprint(self.bp)

    def test_duplicate_identity(self):
        self.bp['validators'].append(copy.deepcopy(self.bp['validators'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate validator'): validate_blueprint(self.bp)

    def test_duplicate_invocation(self):
        inv = self.bp['validators'][0]['interface']['invocations']; inv.append(copy.deepcopy(inv[0]))
        with self.assertRaisesRegex(ValueError, 'duplicate invocation'): validate_blueprint(self.bp)

    def test_native_runtime_payload(self):
        self.bp['validators'][0]['redeemer']['schema'] = {'dataType':'#integer'}
        with self.assertRaisesRegex(ValueError, 'runtime payload'): validate_blueprint(self.bp)

    def test_schema_reference(self):
        self.params['validators'][0]['parameters'][2]['schema']['$ref'] = '#/definitions/Missing'
        with self.assertRaisesRegex(ValueError, 'unresolved'): validate_blueprint(self.params)

    def test_scott_profile_is_required(self):
        self.params['definitions']['OptionalInteger'].pop('encoding')
        with self.assertRaises(ValidationError): validate_blueprint(self.params)

    def test_unknown_scott_profile(self):
        self.params['definitions']['OptionalInteger']['encoding'] = 'unsupported'
        with self.assertRaisesRegex(ValueError, 'Scott profile'): validate_blueprint(self.params)

    def test_data_schema_cannot_be_relabelled_scott(self):
        self.params['validators'][0]['parameters'][0]['schema']['encoding'] = BASE+'/encodings/scott-cbv-v1'
        with self.assertRaises(ValidationError): validate_blueprint(self.params)

    def test_duplicate_scott_constructor_names(self):
        self.params['definitions']['OptionalInteger']['constructors'][1]['name'] = 'None'
        with self.assertRaisesRegex(ValueError, 'constructor name'): validate_blueprint(self.params)

    def test_native_value_inside_data_container(self):
        self.params['validators'][0]['parameters'][0]['schema'] = {'dataType':'list','items':{'dataType':'#integer'}}
        with self.assertRaisesRegex(ValueError, 'Data elements'): validate_blueprint(self.params)

    def test_template_hash_tampering(self):
        self.bp['validators'][0]['hash'] = '00'*28
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): validate_blueprint(self.bp)

    def test_unknown_context(self):
        self.doc['properties'][0]['checkingContext'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'unknown checking'): validate_assurance(self.doc, ASS/'examples')

    def test_context_digest_tampering(self):
        self.doc['checkingContexts']['game-run']['hash']['digest'] = '00'*32
        with self.assertRaisesRegex(ValueError, 'digest mismatch'): validate_assurance(self.doc, ASS/'examples')

    def test_context_target_coverage(self):
        self.context['targets'][0]['validator'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'coverage'): validate_context(self.context, self.bp, ['gameValidator'])

    def test_unknown_checking_profile(self):
        self.context['profile'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'checking profile'): validate_context(self.context, self.bp, ['gameValidator'])

    def test_missing_explicit_semantics(self):
        self.context['execution'].pop('semanticsVariant')
        with self.assertRaises(ValidationError): validate_context(self.context, self.bp, ['gameValidator'])

    def test_step_and_ledger_units_cannot_mix(self):
        self.context['execution']['budget']['exCPU'] = 10
        with self.assertRaises(ValidationError): validate_context(self.context, self.bp, ['gameValidator'])

    def test_steps_cannot_claim_ledger_acceptance(self):
        self.context['execution']['acceptance'] = 'ledger-script'
        with self.assertRaises(ValidationError): validate_context(self.context, self.bp, ['gameValidator'])

    def evidence(self):
        return {'method':'smt-check','verifier':'test fixture','tool':'blaster','outcome':'verified','date':'2026-09-30','scriptHash':self.bp['validators'][0]['hash'],'artifact':copy.deepcopy(self.doc['checkingContexts']['game-run'])}

    def test_evidence_requires_context_digest(self):
        self.doc['properties'][0]['evidence'] = [self.evidence()]
        with self.assertRaises(ValidationError): validate_assurance(self.doc, ASS/'examples')

    def test_evidence_with_wrong_context_is_stale(self):
        evidence = self.evidence(); evidence['checkingContextHash'] = {'alg':'sha256','digest':'00'*32}
        self.doc['properties'][0]['evidence'] = [evidence]
        with self.assertRaisesRegex(ValueError, 'stale checking'): validate_assurance(self.doc, ASS/'examples')

    def test_old_schema_cannot_be_mistaken_for_v2(self):
        self.doc['$schema'] = 'https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json'
        with self.assertRaises(ValidationError): validate('https://cips.cardano.org/cips/cipXXXX/schemas/assurance-v2.json', self.doc)

    def test_applied_parameters_require_complete_order(self):
        target = self.context['targets'][0];target['validator'] = 'parameter-demo';target['purpose'] = 'mint'
        target['parameters'] = {'mode':'applied','values':[{'parameter':'/parameters/1','term':copy.deepcopy(self.doc['checkingContexts']['game-run'])}],'appliedScriptHash':'00'*28,'appliedScript':copy.deepcopy(self.doc['checkingContexts']['game-run'])}
        with self.assertRaisesRegex(ValueError, 'binding order'): validate_context(self.context, self.params, ['parameter-demo'])


class FunctionSchemaTests(unittest.TestCase):
    def setUp(self):
        self.doc = load(ASS/'examples/interface-game-assurance.json')
        self.doc['functions'] = {'outbids': {
            'compiledCode':'4a01010022337100040021', 'serialization':'cbor-flat',
            'hash':{'alg':'sha256','digest':'264d481d68647619542971000e727b145b21600e612476ea09841dce094752a8'},
            'plutusVersion':'v3', 'arguments':[{'dataType':'#integer'}, {'dataType':'#integer'}],
            'result':{'dataType':'#boolean'}}}
        self.doc['properties'] = [self.doc['properties'][0]]
        self.doc['properties'][0]['scope'] = {'functions':['outbids']}

    def check(self): validate(self.doc['$schema'], self.doc)

    def test_function_scope(self): self.check()

    def test_function_example(self):
        doc = load(ASS/'examples/compiled-function-assurance.json')
        validate(doc['$schema'], doc)
        context = load(ASS/'examples/function-checking.json')
        validate(context['$schema'], context)
        self.assertEqual(hashlib.sha256((ASS/'examples/function-checking.json').read_bytes()).hexdigest(),
                         doc['checkingContexts']['outbids']['hash']['digest'])
        function = doc['functions']['outbids']
        self.assertEqual(hashlib.sha256(bytes.fromhex(function['compiledCode'])).hexdigest(), function['hash']['digest'])

    def test_mixed_scope(self):
        self.doc['properties'][0]['scope']['validators'] = ['gameValidator']
        self.check()

    def test_missing_result(self):
        del self.doc['functions']['outbids']['result']
        with self.assertRaises(ValidationError): self.check()

    def test_missing_code(self):
        del self.doc['functions']['outbids']['compiledCode']
        with self.assertRaises(ValidationError): self.check()

    def test_unknown_serialization(self):
        self.doc['functions']['outbids']['serialization'] = 'flat'
        with self.assertRaises(ValidationError): self.check()

    def test_empty_scope(self):
        self.doc['properties'][0]['scope'] = {}
        with self.assertRaises(ValidationError): self.check()

    def test_duplicate_function_scope(self):
        self.doc['properties'][0]['scope']['functions'] *= 2
        with self.assertRaises(ValidationError): self.check()

    def test_missing_function_context_interface(self):
        ctx = load(ASS/'examples/function-checking.json')
        del ctx['targets'][0]['functionInterface']
        with self.assertRaises(ValidationError): validate(ctx['$schema'], ctx)

    def test_recursive_function_definitions(self):
        self.doc['definitions'] = {'Tree':{'anyOf':[
            {'dataType':'constructor','index':0,'fields':[{'dataType':'integer'}]},
            {'dataType':'constructor','index':1,'fields':[{'$ref':'#/definitions/Tree'},{'$ref':'#/definitions/Tree'}]}]}}
        self.doc['functions']['outbids']['arguments'] = [{'$ref':'#/definitions/Tree'}]
        self.doc['functions']['outbids']['result'] = {'$ref':'#/definitions/Tree'}
        self.check()
        ctx = load(ASS/'examples/function-checking.json')
        iface = ctx['targets'][0]['functionInterface']
        iface['definitions'] = self.doc['definitions']
        iface['arguments'] = self.doc['functions']['outbids']['arguments']
        iface['result'] = self.doc['functions']['outbids']['result']
        validate(ctx['$schema'], ctx)

    def test_function_context(self):
        ctx = load(ASS/'examples/game-checking.json')
        f = self.doc['functions']['outbids']
        ctx['targets'] = [{'function':'outbids','functionHash':f['hash'], 'functionInterface':{k:v for k,v in f.items() if k not in ['compiledCode','hash']}}]
        validate(ctx['$schema'], ctx)
        ctx['targets'][0]['purpose'] = 'spend'
        with self.assertRaises(ValidationError): validate(ctx['$schema'], ctx)


if __name__ == '__main__': unittest.main()
