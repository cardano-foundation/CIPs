#!/usr/bin/env python3
"""
Validation script for the CIP-0203 Block Producer Identifier Registry.

Checks CIP-0203/registry.json against CIP-0203/registry.schema.json, then
against the registry rules in CIP-0203 that the schema cannot express.

With --base, it also compares the registry with an earlier version of the file
(normally the target branch) and checks that no entry was removed and no
retired entry was reactivated. With --author, it warns when an existing entry
is changed by someone who is not one of its listed maintainers.

With --fetch-payload-definitions, it downloads each payload_definition that is
new or changed relative to --base (every one, when no --base is given) and
checks it against the payload definition format schema and the structural
constraints in CIP-0203.

--payload-definition checks standalone payload definition documents, given as
local paths or http(s) URLs, without reading the registry.

Usage:
  validate-cip203-registry.py [--registry PATH] [--base PATH] [--author LOGIN]
                              [--fetch-payload-definitions]
  validate-cip203-registry.py --payload-definition PATH_OR_URL [...]

Exits 1 when any error is found. Warnings do not fail the run.
"""

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import jsonschema
except ImportError:
    print("Error: jsonschema library is required. Install it with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parents[2]
CIP_DIR = REPO_ROOT / 'CIP-0203'
DEFAULT_REGISTRY = CIP_DIR / 'registry.json'
REGISTRY_SCHEMA = CIP_DIR / 'registry.schema.json'

# CIP-0203 "Field rules": only scheme 0 is defined; 1, 2 and 3 are reserved for future CIPs.
DEFINED_SCHEMES = {0}

# CIP-0203 "Reserved identifiers" for scheme 0. Only 16 to 254 are assignable.
ASSIGNABLE_IDS = range(16, 255)
RESERVED_IDS = {0: 'no signal'}
RESERVED_IDS.update({i: 'legacy cardano-node' for i in range(1, 16)})
RESERVED_IDS[255] = 'deliberate opt-out'

# CIP-0203 "Reserved names" for payload definition fields.
RESERVED_FIELD_NAMES = {'name', 'id', 'scheme', 'definition_format'}

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
URI_RE = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$')

FETCH_TIMEOUT_SECONDS = 20
FETCH_MAX_BYTES = 1024 * 1024
USER_AGENT = 'cip-0203-registry-validator'


# A source is a file path, or a (file path, context) pair when the problem sits in something the
# file points to, such as a payload definition linked from a registry entry.
Source = Union[str, Tuple[str, str]]


class Report:
    """Collects errors and warnings, each tied to the file it concerns."""

    def __init__(self) -> None:
        self.errors: List[Tuple[Source, str]] = []
        self.warnings: List[Tuple[Source, str]] = []
        self.notes: List[str] = []

    def error(self, source: Source, message: str) -> None:
        self.errors.append((source, message))

    def warning(self, source: Source, message: str) -> None:
        self.warnings.append((source, message))

    def note(self, message: str) -> None:
        self.notes.append(message)

    def emit(self) -> None:
        in_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
        for message in self.notes:
            print(message)
        sys.stdout.flush()
        for level, items in (('error', self.errors), ('warning', self.warnings)):
            for source, message in items:
                file, context = source if isinstance(source, tuple) else (source, '')
                if context:
                    message = f'{context}: {message}'
                if in_actions:
                    print(f"::{level} file={_escape_property(file)},title=CIP-0203 registry::{_escape_data(message)}")
                else:
                    print(f"{level.upper()}: {file}: {message}", file=sys.stderr)
        sys.stdout.flush()


def _escape_data(value: str) -> str:
    return value.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')


def _escape_property(value: str) -> str:
    return _escape_data(value).replace(':', '%3A').replace(',', '%2C')


def _reject_duplicate_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate key "{key}" in one object; JSON parsers keep only one of them')
        result[key] = value
    return result


def _reject_constant(name: str) -> Any:
    raise ValueError(f'{name} is not valid JSON')


def parse_json(text: str) -> Any:
    """Parse strict JSON: no duplicate keys, no NaN or Infinity."""
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant)


def load_json_file(path: Path, report: Report, source: str) -> Optional[Any]:
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        report.error(source, f'cannot read file: {exc}')
        return None
    if '\r' in text:
        report.error(source, 'file must use LF line endings')
    try:
        return parse_json(text)
    except json.JSONDecodeError as exc:
        report.error(source, f'invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}')
    except ValueError as exc:
        report.error(source, f'invalid JSON: {exc}')
    return None


def build_format_checker() -> 'jsonschema.FormatChecker':
    """Format checks used by the CIP-0203 schemas, independent of optional jsonschema extras."""
    checker = jsonschema.FormatChecker(formats=())

    @checker.checks('date', raises=ValueError)
    def is_date(value: Any) -> bool:
        if not isinstance(value, str):
            return True
        if not DATE_RE.match(value):
            return False
        datetime.date.fromisoformat(value)
        return True

    @checker.checks('uri')
    def is_uri(value: Any) -> bool:
        if not isinstance(value, str):
            return True
        return bool(URI_RE.match(value))

    return checker


def _path_text(path: Any) -> str:
    text = ''
    for part in path:
        text += f'[{part}]' if isinstance(part, int) else f'.{part}'
    return text.lstrip('.') or '(document root)'


def _short(value: Any, limit: int = 80) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit - 3] + '...'


def humanize_schema_error(error: 'jsonschema.ValidationError') -> List[Tuple[Any, str]]:
    """Turn one schema error into (path, message) pairs a registrant can act on."""
    path = list(error.absolute_path)
    instance = error.instance

    if error.validator in ('oneOf', 'anyOf'):
        # Payload definition root: exactly one of fields or layout_version.
        if isinstance(instance, dict) and 'definition_format' in instance:
            present = [k for k in ('fields', 'layout_version') if k in instance]
            if len(present) != 1:
                return [(path, 'must contain exactly one of "fields" or "layout_version"')]
        # Payload field: the branch whose "type" matched explains the failure.
        branches: Dict[int, List['jsonschema.ValidationError']] = {}
        for sub in error.context or []:
            branches.setdefault(sub.relative_schema_path[0], []).append(sub)
        matching = [errs for errs in branches.values()
                    if not any(e.validator == 'const' and list(e.relative_path) == ['type'] for e in errs)]
        if len(matching) == 1:
            return [pair for sub in matching[0] for pair in humanize_schema_error(sub)]
        if isinstance(instance, dict) and 'type' in instance and not matching:
            return [(path + ['type'], f'{_short(instance["type"])} is not a supported field type '
                                      '(integer, boolean, or enum)')]
        return [(path, f'{_short(instance)} does not match any allowed form')]

    if error.validator == 'not' and isinstance(error.validator_value, dict) and 'enum' in error.validator_value:
        return [(path, f'{_short(instance)} is a reserved name and must not be used')]

    if path and path[-1] == 'payload_documentation' and error.validator == 'type' and error.validator_value == 'null':
        return [(path, 'must be null when payload_definition is null; documentation accompanies a '
                       'payload definition and cannot replace it')]

    return [(path, error.message if len(error.message) <= 200 else error.message[:197] + '...')]


def schema_errors(instance: Any, schema: Dict[str, Any]) -> List[Tuple[Any, str]]:
    validator_class = jsonschema.validators.validator_for(schema)
    validator = validator_class(schema, format_checker=build_format_checker())
    errors = sorted(validator.iter_errors(instance), key=lambda e: [str(p) for p in e.absolute_path])
    return [pair for e in errors for pair in humanize_schema_error(e)]


def entry_label(entry: Any) -> str:
    """Scheme, id and name of an entry, as far as they are present."""
    if not isinstance(entry, dict):
        return ''
    parts = []
    if 'scheme' in entry:
        parts.append(f"scheme {entry['scheme']}")
    if 'id' in entry:
        parts.append(f"id {entry['id']}")
    if isinstance(entry.get('name'), str):
        parts.append(f'"{entry["name"]}"')
    return ', '.join(parts)


def describe_entry(index: int, entry: Any) -> str:
    label = entry_label(entry)
    return f'entry [{index}] ({label})' if label else f'entry [{index}]'


def entry_key(entry: Any) -> Optional[Tuple[int, int]]:
    if not isinstance(entry, dict):
        return None
    scheme, ident = entry.get('scheme'), entry.get('id')
    if type(scheme) is int and type(ident) is int:
        return (scheme, ident)
    return None


# Registry checks


def check_registry_schema(entries: Any, report: Report, source: str) -> None:
    schema = load_json_file(REGISTRY_SCHEMA, report, str(REGISTRY_SCHEMA.relative_to(REPO_ROOT)))
    if schema is None:
        return
    for path, message in schema_errors(entries, schema):
        if path and isinstance(path[0], int) and isinstance(entries, list):
            where = describe_entry(path[0], entries[path[0]])
            field = _path_text(path[1:])
            report.error(source, f'{where}: {field}: {message}' if path[1:] else f'{where}: {message}')
        else:
            report.error(source, f'{_path_text(path)}: {message}')


def check_registry_rules(entries: List[Any], report: Report, source: str) -> None:
    seen_keys: Dict[Tuple[int, int], int] = {}
    seen_names: Dict[Tuple[int, str], int] = {}

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        where = describe_entry(index, entry)

        for field in ('scheme', 'id'):
            value = entry.get(field)
            if isinstance(value, float):
                report.error(source, f'{where}: {field} must be written as a whole number, not {value!r}')

        key = entry_key(entry)
        if key is not None:
            scheme, ident = key
            if scheme not in DEFINED_SCHEMES:
                report.error(source, f'{where}: scheme {scheme} is not defined; CIP-0203 defines scheme 0 only, '
                                     'and 1 to 3 are reserved for future CIPs')
            elif ident in RESERVED_IDS:
                report.error(source, f'{where}: id {ident} is reserved ({RESERVED_IDS[ident]}) and must not be '
                                     f'registered; assignable ids are {ASSIGNABLE_IDS.start} to '
                                     f'{ASSIGNABLE_IDS.stop - 1}')

            if key in seen_keys:
                other = seen_keys[key]
                report.error(source, f'{where}: (scheme {scheme}, id {ident}) is already used by '
                                     f'{describe_entry(other, entries[other])}; each (scheme, id) pair must be unique')
            else:
                seen_keys[key] = index

            name = entry.get('name')
            if isinstance(name, str) and name.strip():
                name_key = (scheme, ' '.join(name.split()).casefold())
                if name_key in seen_names:
                    other = seen_names[name_key]
                    report.error(source, f'{where}: name "{name}" is already registered as '
                                         f'{describe_entry(other, entries[other])}; one id per implementation')
                else:
                    seen_names[name_key] = index

        for field in ('name', 'description'):
            value = entry.get(field)
            if isinstance(value, str):
                if not value.strip():
                    report.error(source, f'{where}: {field} must not be empty')
                elif value != value.strip():
                    report.error(source, f'{where}: {field} has leading or trailing whitespace')

        status = entry.get('status')
        retired = entry.get('retired')
        registered = entry.get('registered')
        if status == 'active' and retired is not None:
            report.error(source, f'{where}: status is "active" but retired is {retired!r}; '
                                 'an active entry has retired set to null')
        if status == 'retired' and not retired:
            report.error(source, f'{where}: status is "retired" but no retirement date is set in retired')
        if (isinstance(retired, str) and isinstance(registered, str)
                and DATE_RE.match(retired) and DATE_RE.match(registered) and retired < registered):
            report.error(source, f'{where}: retired date {retired} is earlier than registered date {registered}')


def check_against_base(base: List[Any], entries: List[Any], author: Optional[str],
                       report: Report, source: str) -> None:
    head_by_key: Dict[Tuple[int, int], Tuple[int, Dict[str, Any]]] = {}
    for index, entry in enumerate(entries):
        key = entry_key(entry)
        if key is not None and key not in head_by_key:
            head_by_key[key] = (index, entry)

    base_keys = set()
    for base_index, base_entry in enumerate(base):
        key = entry_key(base_entry)
        if key is None:
            continue
        base_keys.add(key)
        if key not in head_by_key:
            report.error(source, f'the entry for {entry_label(base_entry)} was removed; registry entries are '
                                 'never deleted (set status to "retired" instead)')
            continue

        index, entry = head_by_key[key]
        where = describe_entry(index, entry)
        if base_entry.get('status') == 'retired' and entry.get('status') != 'retired':
            report.error(source, f'{where}: a retired identifier is never reassigned, so its status must '
                                 'stay "retired"')

        if entry != base_entry:
            changed = sorted(f for f in set(entry) | set(base_entry) if entry.get(f) != base_entry.get(f))
            report.note(f'changed: {where}: {", ".join(changed)}')
            maintainers = base_entry.get('maintainers')
            if author and isinstance(maintainers, list):
                listed = [m for m in maintainers if isinstance(m, str)]
                if author.casefold() not in (m.casefold() for m in listed):
                    report.warning(source, f'{where} is changed by {author}, who is not one of its listed maintainers '
                                           f'({", ".join(listed)}); CIP-0203 requires a PR from a listed maintainer '
                                           'or their visible consent')

    for key, (index, entry) in sorted(head_by_key.items()):
        if key not in base_keys:
            report.note(f'added: {describe_entry(index, entry)}')


# Payload definition checks


def fetch_json(url: str, report: Report, source: Source) -> Optional[Any]:
    """Fetch a JSON document. Unreachable or bot-protected URLs are warnings, a missing document is an error."""
    scheme = urllib.parse.urlsplit(url).scheme.lower()
    if scheme not in ('http', 'https'):
        report.warning(source, f'cannot fetch {scheme}:// URLs; check this payload definition by hand')
        return None
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json, */*'})
    try:
        with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
            body = response.read(FETCH_MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 429) or exc.code >= 500:
            report.warning(source, f'fetch returned HTTP {exc.code}; check this payload definition by hand')
        else:
            report.error(source, f'fetch returned HTTP {exc.code}; a payload definition must be published at a '
                                 'stable URL')
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, 'reason', exc)
        report.warning(source, f'fetch failed ({reason}); check this payload definition by hand')
        return None
    if len(body) > FETCH_MAX_BYTES:
        report.error(source, f'document is larger than {FETCH_MAX_BYTES} bytes')
        return None
    try:
        return parse_json(body.decode('utf-8'))
    except UnicodeDecodeError:
        report.error(source, 'document is not UTF-8 text')
    except json.JSONDecodeError as exc:
        report.error(source, f'invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}')
    except ValueError as exc:
        report.error(source, f'invalid JSON: {exc}')
    return None


def payload_schema_path(definition_format: int) -> Path:
    return CIP_DIR / f'payload-definition.format-{definition_format}.schema.json'


def check_payload_definition(doc: Any, report: Report, source: Source) -> None:
    if not isinstance(doc, dict):
        report.error(source, 'a payload definition must be a JSON object')
        return
    definition_format = doc.get('definition_format')
    if type(definition_format) is not int:
        report.error(source, 'definition_format is required and must be an integer')
        return
    schema_path = payload_schema_path(definition_format)
    if not schema_path.is_file():
        report.error(source, f'definition_format {definition_format} has no schema in CIP-0203 '
                             f'({schema_path.relative_to(REPO_ROOT)} does not exist)')
        return
    schema = load_json_file(schema_path, report, str(schema_path.relative_to(REPO_ROOT)))
    if schema is None:
        return
    errors = schema_errors(doc, schema)
    for path, message in errors:
        report.error(source, f'{_path_text(path)}: {message}')
    if errors:
        return
    if definition_format == 0:
        check_format0_structure(doc, report, source)


def _width(bits: List[int]) -> int:
    return bits[1] - bits[0] + 1


def check_format0_structure(doc: Dict[str, Any], report: Report, source: Source) -> None:
    """Structural constraints 1 to 7 from CIP-0203 "Structural constraints"."""
    layout_version = doc.get('layout_version')
    if layout_version is None:
        check_format0_fields(doc['fields'], 'fields', None, report, source)
        return

    lv_bits = layout_version['bits']
    if lv_bits[0] > lv_bits[1]:
        report.error(source, f'layout_version.bits {lv_bits}: the first value must not exceed the second')
        lv_bits = None
    for key, layout in layout_version['layouts'].items():
        context = f'layout_version.layouts["{key}"]'
        if lv_bits is not None and int(key) >= 1 << _width(lv_bits):
            report.error(source, f'{context}: layout key {key} does not fit in the {_width(lv_bits)}-bit '
                                 f'layout_version range {lv_bits}')
        check_format0_fields(layout['fields'], f'{context}.fields', lv_bits, report, source)


def check_format0_fields(fields: List[Dict[str, Any]], context: str, lv_bits: Optional[List[int]],
                         report: Report, source: Source) -> None:
    ranges: List[Tuple[int, int, str]] = []
    names: Dict[str, int] = {}

    for index, field in enumerate(fields):
        name = field['name']
        where = f'{context}[{index}] ("{name}")'
        low, high = field['bits']

        if name in names:
            report.error(source, f'{where}: name is already used by {context}[{names[name]}]; '
                                 'field names within a layout must be unique')
        else:
            names[name] = index
        if name.casefold() in RESERVED_FIELD_NAMES and name not in RESERVED_FIELD_NAMES:
            report.warning(source, f'{where}: consumers compare field names case-insensitively, so this '
                                   f'collides with the reserved name "{name.casefold()}"')

        if low > high:
            report.error(source, f'{where}: bits [{low}, {high}]: the first value must not exceed the second')
            continue
        if field['type'] == 'boolean' and low != high:
            report.error(source, f'{where}: a boolean field reads exactly one bit, so both bits values must be equal')
        if field['type'] == 'enum':
            limit = 1 << (high - low + 1)
            for key in field['values']:
                if int(key) >= limit:
                    report.error(source, f'{where}: enum value {key} does not fit in the {high - low + 1}-bit range '
                                         f'[{low}, {high}]')
        if lv_bits is not None and low <= lv_bits[1] and lv_bits[0] <= high:
            report.error(source, f'{where}: bits [{low}, {high}] overlap the layout_version bits {lv_bits}')
        ranges.append((low, high, where))

    ranges.sort()
    for (low_a, high_a, where_a), (low_b, high_b, where_b) in zip(ranges, ranges[1:]):
        if low_b <= high_a:
            report.error(source, f'{where_b}: bits [{low_b}, {high_b}] overlap {where_a} bits [{low_a}, {high_a}]')


def payload_definitions_to_check(entries: List[Any], base: Optional[List[Any]]) -> List[Tuple[int, Dict[str, Any]]]:
    base_urls: Dict[Tuple[int, int], Any] = {}
    if base is not None:
        for base_entry in base:
            key = entry_key(base_entry)
            if key is not None:
                base_urls[key] = base_entry.get('payload_definition')
    selected = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get('payload_definition'), str):
            continue
        key = entry_key(entry)
        if base is None or key not in base_urls or base_urls[key] != entry['payload_definition']:
            selected.append((index, entry))
    return selected


# Entry points


def validate_registry(args: argparse.Namespace, report: Report) -> None:
    registry_path = Path(args.registry) if args.registry else DEFAULT_REGISTRY
    source = args.registry or str(DEFAULT_REGISTRY.relative_to(REPO_ROOT))
    entries = load_json_file(registry_path, report, source)
    if entries is None:
        return

    check_registry_schema(entries, report, source)
    if not isinstance(entries, list):
        return
    check_registry_rules(entries, report, source)

    base = None
    if args.base:
        base = load_json_file(Path(args.base), report, f'{args.base} (base)')
        if base is not None and not isinstance(base, list):
            report.warning(source, 'the base registry is not a JSON array; comparison with it skipped')
            base = None
        if base is not None:
            check_against_base(base, entries, args.author, report, source)

    if args.fetch_payload_definitions:
        for index, entry in payload_definitions_to_check(entries, base):
            url = entry['payload_definition']
            definition_source = (source, f'{describe_entry(index, entry)}: payload_definition <{url}>')
            report.note(f'fetching payload definition for {describe_entry(index, entry)}: {url}')
            doc = fetch_json(url, report, definition_source)
            if doc is not None:
                check_payload_definition(doc, report, definition_source)


def validate_payload_definitions(targets: List[str], report: Report) -> None:
    for target in targets:
        if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', target):
            doc = fetch_json(target, report, target)
        else:
            doc = load_json_file(Path(target), report, target)
        if doc is not None:
            check_payload_definition(doc, report, target)


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate the CIP-0203 Block Producer Identifier Registry.')
    parser.add_argument('--registry', help='registry file to validate (default: CIP-0203/registry.json)')
    parser.add_argument('--base', help='earlier registry file to compare against, normally the target branch')
    parser.add_argument('--author', help='GitHub login of the pull request author')
    parser.add_argument('--fetch-payload-definitions', action='store_true',
                        help='download and check payload definitions that are new or changed relative to --base')
    parser.add_argument('--payload-definition', action='append', metavar='PATH_OR_URL',
                        help='check a standalone payload definition instead of the registry (repeatable)')
    args = parser.parse_args()

    report = Report()
    if args.payload_definition:
        validate_payload_definitions(args.payload_definition, report)
        checked = f'{len(args.payload_definition)} payload definition(s)'
    else:
        validate_registry(args, report)
        checked = 'the registry'
    report.emit()

    if report.errors:
        print(f'\nValidation failed for {checked}: {len(report.errors)} error(s), '
              f'{len(report.warnings)} warning(s)', file=sys.stderr)
        sys.exit(1)
    print(f'\nValidation passed for {checked} with {len(report.warnings)} warning(s)', file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    main()
