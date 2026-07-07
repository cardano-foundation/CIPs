#!/usr/bin/env python3
"""
Validation script for CPS README.md files.
Validates YAML headers and required sections.
"""

import sys
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

try:
    import jsonschema
except ImportError:
    print("Error: jsonschema library is required. Install it with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


# Required fields for CPS headers (in required order)
CPS_REQUIRED_FIELDS_ORDER = [
    'CPS', 'Title', 'Category', 'Status', 'Authors',
    'Proposed Solutions', 'Discussions', 'Created', 'License'
]
CPS_REQUIRED_FIELDS = set(CPS_REQUIRED_FIELDS_ORDER)

# Required sections (H2 headers) in required order
CPS_REQUIRED_SECTIONS_ORDER = [
    'Abstract',
    'Problem',
    'Use Cases',
    'Goals',
    'Open Questions',
    'Copyright'
]
CPS_REQUIRED_SECTIONS = set(CPS_REQUIRED_SECTIONS_ORDER)

# Optional H2 sections (allowed but not required)
# These should appear after the required sections, before Copyright
CPS_OPTIONAL_SECTIONS = {
    'References',
    'Appendices',
    'Acknowledgments',
    'Acknowledgements'
}

# Load CPS header schema
SCHEMA_PATH = Path(__file__).parent.parent / 'schemas' / 'cps-header.schema.json'
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    CPS_HEADER_SCHEMA = json.load(f)


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], Optional[str], Optional[List[str]], Optional[str]]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, remaining_content, raw_lines, parse_error).
        On success parse_error is None. When the '---' delimiters are present but
        the enclosed YAML cannot be parsed (e.g. an impossible date like month
        13), frontmatter is None and parse_error carries the underlying reason so
        the caller can report it instead of a misleading "missing frontmatter".
    """
    # Check for frontmatter delimiters - must start with ---
    if not content.startswith('---'):
        return None, content, None, None

    # Find the closing delimiter (--- on its own line)
    # Split on '\n---\n' or '\n---' at end of content
    lines = content.split('\n')
    if lines[0] != '---':
        return None, content, None, None

    # Find the closing ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i] == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, content, None, None

    # Extract frontmatter (lines between the two --- markers)
    frontmatter_lines = lines[1:end_idx]

    # Preprocess: quote standalone '?' values (YAML interprets '?' as explicit key indicator)
    processed_lines = []
    for line in frontmatter_lines:
        # Match lines like "CPS: ?" or "Category: ?" and quote the ?
        if re.match(r'^[A-Za-z][A-Za-z -]*:\s+\?+\s*$', line):
            line = re.sub(r':\s+(\?+)\s*$', r': "\1"', line)
        processed_lines.append(line)

    frontmatter_text = '\n'.join(processed_lines)

    # Extract remaining content (everything after the closing ---)
    remaining_lines = lines[end_idx + 1:]
    remaining_content = '\n'.join(remaining_lines)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            return None, content, None, None
        return frontmatter, remaining_content, frontmatter_lines, None
    except yaml.YAMLError as e:
        return None, content, None, str(e)
    except ValueError as e:
        # Catches invalid date values that YAML tries to parse (e.g., month 13)
        return None, content, None, str(e)


def _strip_fenced_code_blocks(content: str) -> str:
    """Blank out lines inside fenced code blocks, preserving line count.

    Recognises CommonMark fenced code blocks: an opening fence is a line
    indented up to 3 spaces whose first non-whitespace run is 3+ backticks or
    3+ tildes. For backtick fences the info string (rest of the line) must
    not contain backticks — this excludes inline code like '```X``` is a ...'
    which is not a valid fence. The closing fence must use the same character
    and be at least as long as the opening, followed only by whitespace.

    Lines inside a fence — including the fence lines themselves — are
    replaced with '' so that line-based regex extraction skips them. An
    unclosed fence treats all trailing lines as fenced, which is the safe
    default for the validator (no false positives).
    """
    backtick_open_re = re.compile(r'^ {0,3}(`{3,})([^`]*)$')
    tilde_open_re = re.compile(r'^ {0,3}(~{3,})')
    result = []
    in_fence = False
    fence_char = None
    fence_len = 0
    for line in content.split('\n'):
        if in_fence:
            close_re = re.compile(
                r'^ {0,3}(' + re.escape(fence_char) + r'{' + str(fence_len) + r',})\s*$'
            )
            if close_re.match(line):
                in_fence = False
                fence_char = None
                fence_len = 0
            result.append('')
        else:
            m_b = backtick_open_re.match(line)
            m_t = tilde_open_re.match(line) if not m_b else None
            if m_b:
                in_fence = True
                fence_char = '`'
                fence_len = len(m_b.group(1))
                result.append('')
            elif m_t:
                in_fence = True
                fence_char = '~'
                fence_len = len(m_t.group(1))
                result.append('')
            else:
                result.append(line)
    return '\n'.join(result)


def extract_h2_headers(content: str) -> List[str]:
    """Extract all H2 headers (##) from markdown content, ignoring fenced code blocks."""
    h2_pattern = r'^##\s+(.+)$'
    headers = []
    for line in _strip_fenced_code_blocks(content).split('\n'):
        match = re.match(h2_pattern, line)
        if match:
            headers.append(match.group(1).strip())
    return headers


def extract_h1_headers(content: str) -> List[str]:
    """Extract all H1 headers (#) from markdown content, ignoring fenced code blocks."""
    h1_pattern = r'^#\s+(.+)$'
    headers = []
    for line in _strip_fenced_code_blocks(content).split('\n'):
        match = re.match(h1_pattern, line)
        if match:
            headers.append(match.group(1).strip())
    return headers


def validate_line_endings(file_path: Path) -> List[str]:
    """Validate that file uses UNIX line endings (LF, not CRLF).
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    try:
        # Read file in binary mode to check line endings
        with open(file_path, 'rb') as f:
            content_bytes = f.read()
        
        # Check for CRLF (\r\n) - Windows line endings
        if b'\r\n' in content_bytes:
            errors.append("File uses Windows line endings (CRLF). Use UNIX line endings (LF) instead.")
        
        # Check for standalone \r without \n (old Mac line endings)
        # Replace CRLF first, then check for remaining CR
        content_without_crlf = content_bytes.replace(b'\r\n', b'')
        if b'\r' in content_without_crlf:
            errors.append("File uses old Mac line endings (CR). Use UNIX line endings (LF) instead.")
    except Exception as e:
        errors.append(f"Error checking line endings: {e}")
    
    return errors


def validate_no_h1_headings(content: str) -> List[str]:
    """Validate that no H1 headings are present in the document.
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    h1_headers = extract_h1_headers(content)
    if h1_headers:
        errors.append(f"H1 headings are not allowed. Found: {', '.join(h1_headers)}")
    
    return errors


def _validate_field_order(frontmatter: Dict) -> List[str]:
    """Validate that header fields appear in the correct order.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Get the actual order of fields in the frontmatter
    actual_fields = list(frontmatter.keys())

    # Filter to only known required fields (ignore any extra fields for order check)
    actual_required = [f for f in actual_fields if f in CPS_REQUIRED_FIELDS]

    # Build expected order based on which required fields are present
    expected_order = [f for f in CPS_REQUIRED_FIELDS_ORDER if f in actual_required]

    if actual_required != expected_order:
        errors.append(
            f"Header fields are not in the correct order. "
            f"Expected: {', '.join(expected_order)}. "
            f"Got: {', '.join(actual_required)}"
        )

    return errors


def _schema_error_label(error) -> str:
    """Human label for the location of a schema error (e.g. 'Category' or 'Authors entry 2')."""
    path = list(error.absolute_path)
    if not path:
        return 'header'
    parts = []
    for p in path:
        parts.append(f"entry {p + 1}" if isinstance(p, int) else str(p))
    return ' '.join(parts)


def _schema_type_name(t) -> str:
    """Friendly name for a JSON Schema type (or list of types)."""
    mapping = {
        'object': 'a mapping', 'array': 'a list', 'string': 'text',
        'integer': 'an integer', 'number': 'a number',
        'boolean': 'true/false', 'null': 'null',
    }
    if isinstance(t, list):
        return ' or '.join(_schema_type_name(x) for x in t)
    return mapping.get(t, str(t))


def humanize_schema_error(error) -> str:
    """Turn a jsonschema ValidationError into a friendly, actionable message.

    Inspects the failed keyword (``error.validator``) and the schema node that
    failed (which carries the field ``description``). Falls back to the
    library's default message for anything unrecognised, so no failure mode is
    ever swallowed — it just may be less pretty.
    """
    label = _schema_error_label(error)
    validator = error.validator
    node = error.schema if isinstance(error.schema, dict) else {}
    description = node.get('description')

    if validator == 'enum':
        allowed = ', '.join(repr(v) for v in error.validator_value)
        return f"'{label}' must be one of: {allowed}. Got: {error.instance!r}"

    if validator == 'type':
        return f"'{label}' must be {_schema_type_name(error.validator_value)}. Got: {error.instance!r}"

    if validator == 'minItems':
        n = error.validator_value
        unit = 'entry' if n == 1 else 'entries'
        return f"'{label}' must contain at least {n} {unit}. Got: {error.instance!r}"

    if validator in ('oneOf', 'anyOf'):
        msg = f"'{label}' does not match any accepted form. Got: {error.instance!r}."
        if description:
            msg += f" Expected: {description}"
        return msg

    if validator == 'additionalProperties':
        properties = node.get('properties', {})
        unexpected = (
            [k for k in error.instance if k not in properties]
            if isinstance(error.instance, dict) else []
        )
        unexpected_str = ', '.join(repr(k) for k in unexpected) if unexpected else 'unknown field(s)'
        return (
            f"Unknown header field(s): {unexpected_str}. "
            f"Allowed fields: {', '.join(properties.keys())}"
        )

    if validator == 'required':
        missing = [
            r for r in error.validator_value
            if isinstance(error.instance, dict) and r not in error.instance
        ]
        missing_str = ', '.join(repr(m) for m in missing) if missing else 'a required field'
        return f"Missing required header field(s): {missing_str}"

    if validator in ('minLength', 'maxLength'):
        limit = error.validator_value
        length = len(error.instance) if isinstance(error.instance, str) else '?'
        bound = 'at least' if validator == 'minLength' else 'at most'
        return f"'{label}' must be {bound} {limit} characters long. Got {length}: {error.instance!r}"

    if validator == 'pattern':
        msg = f"'{label}' has an invalid format. Got: {error.instance!r}."
        if description:
            msg += f" Expected: {description}"
        return msg

    # Fallback: keep the library's message but anchor it to the field.
    return f"'{label}': {error.message}"


def _validate_cps_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the CPS number field.

    Leading-zero detection is performed separately against raw lines.
    """
    errors = []
    if 'CPS' not in frontmatter:
        return errors
    value = frontmatter['CPS']
    if isinstance(value, bool):
        errors.append(
            f"'CPS' must be a positive integer (e.g., 30) or '?' if unassigned. Got: {value!r}"
        )
        return errors
    if isinstance(value, int):
        if value < 1:
            errors.append(
                f"'CPS' must be a positive integer (1 or greater) or '?' if unassigned. Got: {value}"
            )
        return errors
    if isinstance(value, str):
        if re.fullmatch(r'\?+', value):
            return errors
        if re.fullmatch(r'[1-9]\d*', value):
            return errors
        if re.fullmatch(r'0\d*', value):
            return errors  # Leading-zero check handles this
        errors.append(
            f"'CPS' must be a positive integer (e.g., 30) or '?' if unassigned. Got: {value!r}"
        )
        return errors
    errors.append(
        f"'CPS' must be a positive integer or '?' if unassigned. Got: {value!r}"
    )
    return errors


def _validate_title_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the Title field.

    CPS titles must not contain backticks (they disrupt formatting in other
    contexts) and must be at most 100 characters.
    """
    errors = []
    if 'Title' not in frontmatter:
        return errors
    value = frontmatter['Title']
    if not isinstance(value, str):
        return errors
    if not value.strip():
        errors.append("'Title' must not be empty")
    if len(value) > 100:
        errors.append(
            f"'Title' must be at most 100 characters. Got {len(value)} characters: {value!r}"
        )
    if '`' in value:
        errors.append(
            f"'Title' must not contain backticks (`) — they disrupt formatting in other "
            f"contexts (e.g. the CIP/CPS index). Got: {value!r}"
        )
    return errors


def _validate_status_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the Status field."""
    errors = []
    if 'Status' not in frontmatter:
        return errors
    value = frontmatter['Status']
    if not isinstance(value, str):
        return errors
    if re.fullmatch(r'Open|Solved|Inactive(?:\s+\(.*\))?', value):
        return errors
    errors.append(
        f"'Status' must be 'Open', 'Solved', or 'Inactive (reason)' "
        f"(with an optional reason in parentheses, e.g. 'Inactive (superseded by CPS-NNNN)'). "
        f"Got: {value!r}"
    )
    return errors


def _validate_authors_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of Authors entries."""
    errors = []
    entries = frontmatter.get('Authors')
    if not isinstance(entries, list):
        return errors
    pattern = re.compile(r'^.+\s+<.+>$')
    for i, entry in enumerate(entries):
        if not isinstance(entry, str) or not pattern.match(entry):
            errors.append(
                f"'Authors' entry {i+1}: must be in the form 'Name <email>'. "
                f"Got: {entry!r}. Example: 'John Doe <john.doe@email.domain>'"
            )
    return errors


def _validate_created_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the Created field."""
    errors = []
    if 'Created' not in frontmatter:
        return errors
    value = frontmatter['Created']
    if hasattr(value, 'isoformat'):
        value = value.isoformat()
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        errors.append(
            f"'Created' must be an ISO 8601 date in YYYY-MM-DD form. "
            f"Got: {frontmatter['Created']!r}. Example: '2024-05-21'"
        )
    return errors


def _validate_license_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the License field, with a did-you-mean hint on near-misses."""
    errors = []
    if 'License' not in frontmatter:
        return errors
    value = frontmatter['License']
    if not isinstance(value, str):
        return errors
    valid = ['CC-BY-4.0', 'Apache-2.0']
    if value in valid:
        return errors
    normalized = re.sub(r'\s+', '-', value).lower()
    valid_normalized = {v.lower(): v for v in valid}
    suggestion = valid_normalized.get(normalized)
    if suggestion:
        errors.append(
            f"'License' must be one of: {', '.join(valid)}. "
            f"Got: {value!r} (did you mean {suggestion!r}?)"
        )
    else:
        errors.append(
            f"'License' must be one of: {', '.join(valid)}. Got: {value!r}"
        )
    return errors


def _validate_label_url_format(entries: list, field_name: str) -> List[str]:
    """Validate that string entries follow the 'Label: URL' form.

    String entries must be of the form 'Label: URL' (with whitespace after the
    colon). Dict entries ({Label: URL}) are validated by the JSON schema. The
    label/URL semantic rules (CIP references, PR vs merged) are validated
    separately by ``_validate_cip_label_entries``.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if not isinstance(entries, list):
        return errors

    pattern = re.compile(r'^[^:\s][^:]*:\s+https?://\S+')
    for i, entry in enumerate(entries):
        if isinstance(entry, str) and not pattern.match(entry):
            errors.append(
                f"'{field_name}' entry {i+1}: must be in the form 'Label: URL'. "
                f"Got: {entry!r}. "
                f"Example: 'CIP-0001: https://github.com/cardano-foundation/CIPs/pull/1'"
            )
    return errors


def validate_header(frontmatter: Dict) -> List[str]:
    """Validate the YAML frontmatter header for CPSs.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate field order
    errors.extend(_validate_field_order(frontmatter))

    # Validate header fields using JSON Schema
    try:
        # Convert date objects to strings for schema validation
        # JSON Schema expects dates as strings, but PyYAML may parse them as date objects
        # Also normalize dictionary entries in lists to strings (YAML parses "Label: URL" as dict)
        frontmatter_for_schema = {}
        for key, value in frontmatter.items():
            if key == 'Created' and hasattr(value, 'isoformat'):
                # Handle date objects from PyYAML (datetime.date or datetime.datetime)
                frontmatter_for_schema[key] = value.isoformat()
            elif key in ('Proposed Solutions', 'Discussions') and isinstance(value, list):
                # Convert dictionary entries to string format "Label: URL"
                normalized_list = []
                for item in value:
                    if isinstance(item, dict):
                        # Convert dict like {'Label': 'URL'} to string 'Label: URL'
                        if len(item) == 1:
                            label, url = next(iter(item.items()))
                            normalized_list.append(f"{label}: {url}")
                        else:
                            # Multiple keys - join them
                            normalized_list.append(": ".join(f"{k}: {v}" for k, v in item.items()))
                    elif isinstance(item, str):
                        normalized_list.append(item)
                    else:
                        normalized_list.append(str(item))
                frontmatter_for_schema[key] = normalized_list
            else:
                frontmatter_for_schema[key] = value

        jsonschema.validate(instance=frontmatter_for_schema, schema=CPS_HEADER_SCHEMA)
    except jsonschema.ValidationError as e:
        # Translate the raw library error into a friendly, actionable message
        errors.append(humanize_schema_error(e))
    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")

    # Friendly per-field value checks (schema enforces only type/structure for these)
    errors.extend(_validate_cps_field(frontmatter))
    errors.extend(_validate_title_field(frontmatter))
    errors.extend(_validate_status_field(frontmatter))
    errors.extend(_validate_authors_field(frontmatter))
    errors.extend(_validate_created_field(frontmatter))
    errors.extend(_validate_license_field(frontmatter))

    # Validate 'Label: URL' string format, then the CIP label semantic rules
    if 'Proposed Solutions' in frontmatter:
        errors.extend(_validate_label_url_format(frontmatter['Proposed Solutions'], 'Proposed Solutions'))
        errors.extend(_validate_cip_label_entries(frontmatter['Proposed Solutions'], 'Proposed Solutions'))
    if 'Discussions' in frontmatter:
        errors.extend(_validate_label_url_format(frontmatter['Discussions'], 'Discussions'))
        errors.extend(_validate_cip_label_entries(frontmatter['Discussions'], 'Discussions'))

    return errors


def _validate_cip_label_entries(entries: list, field_name: str) -> List[str]:
    """Validate semantic rules for entries with CIP labels.

    When a label matches CIP-NNNN pattern:
    - URL must be a GitHub CIPs repository link (PR or merged CIP)
    - Pull request URLs require '?' suffix on the CIP number (candidate)
    - Merged CIP URLs must NOT have '?' suffix

    Other labels are allowed with any valid URL.

    Args:
        entries: List of label-URL entries
        field_name: Name of the field for error messages

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not isinstance(entries, list):
        return errors

    cip_label_pattern = re.compile(r'^(CIP-\d+)(\?)?$')
    pr_pattern = re.compile(r'https://github\.com/cardano-foundation/CIPs/pull/\d+')
    merged_pattern = re.compile(r'https://github\.com/cardano-foundation/CIPs/(tree|blob)/[^/]+/CIP-\d+')
    github_cips_pattern = re.compile(r'^https://github\.com/cardano-foundation/CIPs/(pull/\d+|tree/[^/]+/CIP-\d+|blob/[^/]+/CIP-\d+)')

    for i, entry in enumerate(entries):
        # Normalize to label and URL
        if isinstance(entry, dict) and len(entry) == 1:
            label, url = next(iter(entry.items()))
        elif isinstance(entry, str):
            # Parse "Label: URL" format
            match = re.match(r'^([^:]+):\s+(.+)$', entry)
            if not match:
                continue
            label, url = match.groups()
        else:
            continue

        label = label.strip()
        url = url.strip()

        # Check if label matches CIP pattern - only then apply extra validation
        label_match = cip_label_pattern.match(label)
        if not label_match:
            continue  # Non-CIP labels are allowed with any URL

        cip_number = label_match.group(1)
        has_question_mark = label_match.group(2) == '?'

        # For CIP labels, URL must be a GitHub CIPs repository link
        if not github_cips_pattern.match(url):
            errors.append(
                f"'{field_name}' entry {i+1}: CIP label '{label}' requires a GitHub CIPs repository URL "
                f"(pull request or merged CIP). Got: {url}"
            )
            continue

        is_pr = pr_pattern.search(url) is not None
        is_merged = merged_pattern.search(url) is not None

        if is_pr and not has_question_mark:
            errors.append(
                f"'{field_name}' entry {i+1}: Pull request URL requires '?' suffix on CIP number "
                f"(use '{cip_number}?' instead of '{cip_number}' to indicate candidate status)"
            )
        elif is_merged and has_question_mark:
            errors.append(
                f"'{field_name}' entry {i+1}: Merged CIP should not have '?' suffix "
                f"(use '{cip_number}' instead of '{cip_number}?' since this CIP is merged)"
            )

    return errors


def validate_sections(content: str) -> List[str]:
    """Validate required sections exist at H2 level for CPSs.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    h2_headers = extract_h2_headers(content)
    found_sections = set(h2_headers)

    # Normalize headers to lowercase for case-insensitive comparison
    found_sections_lower = {h.lower() for h in found_sections}
    required_sections_lower = {h.lower() for h in CPS_REQUIRED_SECTIONS}
    optional_sections_lower = {h.lower() for h in CPS_OPTIONAL_SECTIONS}

    # Check for missing required sections (case-insensitive)
    missing_sections_lower = required_sections_lower - found_sections_lower
    if missing_sections_lower:
        # Map back to original case from required_sections for error message
        missing_sections = {orig for orig in CPS_REQUIRED_SECTIONS
                          if orig.lower() in missing_sections_lower}
        errors.append(f"Missing required sections: {', '.join(sorted(missing_sections))}")

    # Check for unknown sections (not in required or optional)
    allowed_sections_lower = required_sections_lower | optional_sections_lower
    for header in h2_headers:
        if header.lower() not in allowed_sections_lower:
            errors.append(f"Unknown section: '{header}'. Only required and optional sections are allowed.")

    # Build a mapping from lowercase to expected capitalization
    expected_capitalization = {}
    for section in CPS_REQUIRED_SECTIONS:
        expected_capitalization[section.lower()] = section
    for section in CPS_OPTIONAL_SECTIONS:
        expected_capitalization[section.lower()] = section

    # Check for incorrect capitalization
    for header in h2_headers:
        header_lower = header.lower()
        if header_lower in expected_capitalization:
            expected = expected_capitalization[header_lower]
            if header != expected:
                errors.append(f"Section '{header}' has incorrect capitalization. Expected: '{expected}'")

    # Check section order
    # Map found headers to their canonical names (for order comparison)
    canonical_headers = []
    for header in h2_headers:
        header_lower = header.lower()
        if header_lower in expected_capitalization:
            canonical_headers.append(expected_capitalization[header_lower])
        else:
            canonical_headers.append(header)  # Keep unknown headers as-is

    # Extract just the required sections in the order they appear
    found_required_order = [h for h in canonical_headers if h in CPS_REQUIRED_SECTIONS]

    # Build expected order based on which required sections are present
    expected_required_order = [s for s in CPS_REQUIRED_SECTIONS_ORDER if s in found_required_order]

    if found_required_order != expected_required_order:
        errors.append(
            f"Sections are not in the correct order. "
            f"Expected: {', '.join(expected_required_order)}. "
            f"Got: {', '.join(found_required_order)}"
        )

    # Check that optional sections appear only between "Open Questions" and "Copyright"
    # Optional sections must not appear before any required section except Copyright
    optional_sections_normalized = {s.lower() for s in CPS_OPTIONAL_SECTIONS}
    required_before_optional = [s for s in CPS_REQUIRED_SECTIONS_ORDER if s != 'Copyright']

    for i, header in enumerate(canonical_headers):
        header_lower = header.lower()
        if header_lower in optional_sections_normalized:
            # This is an optional section - check what comes after it
            for j in range(i + 1, len(canonical_headers)):
                following_header = canonical_headers[j]
                # If a required section (other than Copyright) follows an optional section, that's an error
                if following_header in required_before_optional:
                    errors.append(
                        f"Optional section '{header}' appears before required section '{following_header}'. "
                        f"Optional sections must appear after 'Open Questions' and before 'Copyright'."
                    )
                    break

    return errors


def validate_unquoted_question_marks(raw_lines: List[str]) -> List[str]:
    """Validate that no header field has an unquoted '?' value.

    A bare '?' is invalid YAML (it denotes an explicit key), which breaks
    GitHub's frontmatter rendering: the header table is not displayed and
    Discussions links are not clickable. Quoted values like ``CPS: "?"``
    are fine and do not match here.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    for line in raw_lines:
        match = re.match(r'^([A-Za-z][A-Za-z -]*):\s+\?+\s*$', line)
        if match:
            field = match.group(1)
            errors.append(
                f"'{field}' has an unquoted '?' value; a bare '?' is invalid YAML and breaks "
                f"GitHub's frontmatter rendering (header table / clickable Discussions links). "
                f'Use {field}: "?" until a number is assigned, or the assigned number.'
            )
    return errors


def validate_directory_name(frontmatter: Dict, file_path: Path) -> List[str]:
    """Validate that a CPS with an assigned number lives in a correctly-named directory.

    For CPS number N, the parent directory must be 'CPS-NNNN' (zero-padded to 4 digits;
    no truncation for numbers >= 10000). Unassigned CPSs ('?', '??', etc.) skip the
    number-match check, but a numbered directory must still be correctly zero-padded.
    """
    errors = []

    # Regardless of the CPS field, a numbered directory must be zero-padded to
    # 4 digits (5+ digits without a leading zero for numbers >= 10000).
    dir_match = re.fullmatch(r'CPS-(\d+)', file_path.parent.name)
    if dir_match:
        digits = dir_match.group(1)
        if len(digits) != 4 and (len(digits) < 4 or digits.startswith('0')):
            errors.append(
                f"Directory name '{file_path.parent.name}' is not zero-padded to 4 digits. "
                f"Expected: 'CPS-{int(digits):04d}'"
            )
            return errors

    cps_value = frontmatter.get('CPS')
    if cps_value is None:
        return errors  # Missing field is reported by header validation

    # Skip unassigned CPSs ('?', '??', etc.)
    if isinstance(cps_value, str) and cps_value.startswith('?'):
        return errors

    # Parse to integer; non-numeric strings are caught by header validation
    try:
        cps_num = int(cps_value)
    except (ValueError, TypeError):
        return errors

    expected_dir = f"CPS-{cps_num:04d}"
    actual_dir = file_path.parent.name

    if actual_dir != expected_dir:
        errors.append(
            f"Directory name '{actual_dir}' does not match the CPS number {cps_num}. "
            f"Expected: '{expected_dir}'"
        )

    return errors


def is_cps_file(file_path: Path) -> bool:
    """Check if file path indicates a CPS document."""
    path_str = str(file_path)
    # Normalize path separators and check for CPS- pattern
    # Handles both absolute (/CPS-123/) and relative (CPS-123/) paths
    # Also handles Windows paths (CPS-123\README.md)
    normalized_path = path_str.replace('\\', '/')
    
    # Check for CPS- pattern (with or without leading slash)
    return bool(re.search(r'(^|/)CPS-', normalized_path, re.IGNORECASE))


def validate_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single CPS README.md file.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check if this is a CPS file
    if not is_cps_file(file_path):
        return False, [f"File path does not indicate a CPS document: {file_path}"]
    
    # Validate line endings (must check raw file bytes)
    line_ending_errors = validate_line_endings(file_path)
    errors.extend(line_ending_errors)
    
    # Read file content
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    # Parse frontmatter
    frontmatter, remaining_content, raw_lines, parse_error = parse_frontmatter(content)
    if frontmatter is None:
        if parse_error:
            errors.append(
                f"Could not parse the YAML frontmatter (between the '---' markers). "
                f"Reason: {parse_error}"
            )
        else:
            errors.append("Missing or invalid YAML frontmatter (must start with '---' and end with '---')")
        return False, errors

    # Check for leading zeros in CPS field (YAML loses this information)
    if raw_lines:
        for line in raw_lines:
            m = re.match(r'^CPS:\s+(0\d+)', line)
            if m:
                stripped = m.group(1).lstrip('0') or '0'
                errors.append(
                    f"'CPS' number must not have leading zeros. Got: {m.group(1)!r}. "
                    f"Use 'CPS: {stripped}', not 'CPS: {m.group(1)}'."
                )
                break

    if raw_lines:
        errors.extend(validate_unquoted_question_marks(raw_lines))

    # Validate the directory name matches the assigned CPS number
    dir_errors = validate_directory_name(frontmatter, file_path)
    errors.extend(dir_errors)

    # Validate header
    header_errors = validate_header(frontmatter)
    errors.extend(header_errors)
    
    # Validate no H1 headings
    h1_errors = validate_no_h1_headings(remaining_content)
    errors.extend(h1_errors)
    
    # Validate sections
    section_errors = validate_sections(remaining_content)
    errors.extend(section_errors)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    """Main entry point for the validation script."""
    if len(sys.argv) < 2:
        print("Usage: validate-cps.py <file1> [file2] ...", file=sys.stderr)
        sys.exit(1)
    
    files_to_validate = [Path(f) for f in sys.argv[1:]]
    all_valid = True
    all_errors = []
    
    for file_path in files_to_validate:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            all_valid = False
            continue
        
        is_valid, errors = validate_file(file_path)
        
        if not is_valid:
            all_valid = False
            print(f"\nValidation failed for {file_path}:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            all_errors.append((file_path, errors))
    
    if not all_valid:
        print(f"\nValidation failed for {len(all_errors)} file(s)", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nAll {len(files_to_validate)} file(s) passed validation", file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    main()

