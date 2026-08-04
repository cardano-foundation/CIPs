"""Shared validation logic for CIP and CPS README.md files.

Everything here is identical between the two document types, parametrized by
the number field name ('CIP' or 'CPS') where needed. Document-specific rules
(sections, Status values, Solution To, Implementors, ...) live in the
respective validate-cip.py / validate-cps.py scripts.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


# Accepted placeholder values for a not-yet-assigned CIP/CPS number.
# '?' must be quoted in YAML; the word placeholders need no quoting.
UNASSIGNED_WORD_PLACEHOLDERS = ('unassigned', 'pending', 'TBD')
UNASSIGNED_PLACEHOLDERS = {'?', *(w.lower() for w in UNASSIGNED_WORD_PLACEHOLDERS)}

# Fields other than the number field whose template value is a quoted "?"
# placeholder (Category's schema enum includes "?"; Title accepts any text).
QUOTED_PLACEHOLDER_FIELDS = {'Title', 'Category'}

_WORD_PLACEHOLDERS_TEXT = "{}, or {}".format(
    ', '.join(f"'{w}'" for w in UNASSIGNED_WORD_PLACEHOLDERS[:-1]),
    f"'{UNASSIGNED_WORD_PLACEHOLDERS[-1]}'",
)


def number_guidance(field_name: str) -> str:
    """Guidance for CIP/CPS-number errors, derived from UNASSIGNED_PLACEHOLDERS."""
    return (
        f"'{field_name}' must be a positive integer (e.g., 30), or \"?\" (quoted), "
        f"{_WORD_PLACEHOLDERS_TEXT} if not yet assigned."
    )


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
        # Match lines like "CIP: ?" or "Category: ?" and quote the ?
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

    # Fallback: keep the library's message but anchor it to the field.
    return f"'{label}': {error.message}"


def validate_number_field(frontmatter: Dict, field_name: str) -> List[str]:
    """Friendly validation of the CIP/CPS number field.

    Handles quoted string values directly, including leading-zero strings
    (YAML preserves those, unlike unquoted numbers — see
    validate_leading_zero_lines for the unquoted case).
    """
    guidance = number_guidance(field_name)
    errors = []
    if field_name not in frontmatter:
        return errors
    value = frontmatter[field_name]
    if isinstance(value, bool):
        errors.append(f"{guidance} Got: {value!r}")
        return errors
    if isinstance(value, int):
        if value < 1:
            errors.append(f"{guidance} Got: {value}")
        return errors
    if isinstance(value, str):
        if value.lower() in UNASSIGNED_PLACEHOLDERS:
            return errors
        if re.fullmatch(r'[1-9]\d*', value):
            return errors
        if re.fullmatch(r'0\d+', value):
            stripped = value.lstrip('0')
            if stripped:
                errors.append(
                    f"'{field_name}' number must not have leading zeros. Got: {value!r}. "
                    f"Use '{field_name}: {stripped}', not '{field_name}: {value}'."
                )
            else:
                # All zeros: leading-zero advice would suggest '0', which is
                # itself invalid — report the positive-integer rule instead.
                errors.append(f"{guidance} Got: {value!r}")
            return errors
        errors.append(f"{guidance} Got: {value!r}")
        return errors
    errors.append(f"{guidance} Got: {value!r}")
    return errors


def validate_leading_zero_lines(raw_lines: Optional[List[str]], frontmatter: Dict, field_name: str) -> List[str]:
    """Detect unquoted leading-zero number values from the raw header lines.

    YAML normalizes unquoted leading-zero values (e.g. '042' parses as octal
    34), losing the leading zero, so this must be checked against the raw
    line. Only fires when YAML parsed the value as an integer; string values
    keep their leading zeros and are reported by validate_number_field.
    """
    errors = []
    value = frontmatter.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int):
        return errors
    for line in raw_lines or []:
        m = re.match(rf'^{field_name}:\s+(0\d+)', line)
        if m:
            raw = m.group(1)
            stripped = raw.lstrip('0')
            if stripped:
                errors.append(
                    f"'{field_name}' number must not have leading zeros. Got: {raw!r}. "
                    f"Use '{field_name}: {stripped}', not '{field_name}: {raw}'."
                )
            else:
                # All zeros: suggesting '0' would contradict the
                # positive-integer rule — report that rule instead.
                errors.append(
                    f"'{field_name}' number must not have leading zeros. Got: {raw!r}. "
                    f"{number_guidance(field_name)}"
                )
            break
    return errors


def validate_unquoted_question_marks(raw_lines: List[str], number_field: str) -> List[str]:
    """Validate that no header field has an unquoted '?' value.

    A bare '?' is invalid YAML (it denotes an explicit key), which breaks
    GitHub's frontmatter rendering: the header table is not displayed and
    Discussions links are not clickable. Quoted values like ``CIP: "?"``
    are fine and do not match here.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    for line in raw_lines:
        match = re.match(r'^([A-Za-z][A-Za-z -]*):\s+\?+\s*$', line)
        if match:
            field = match.group(1)
            if field == number_field:
                fix_hint = (
                    f'Use {field}: "?" (quoted), or an unquoted word placeholder '
                    f"such as {_WORD_PLACEHOLDERS_TEXT}, until a number is assigned."
                )
            elif field in QUOTED_PLACEHOLDER_FIELDS:
                fix_hint = f'Use {field}: "?" until a value is assigned.'
            else:
                # A quoted "?" is not a valid value for this field either.
                fix_hint = (
                    f"'{field}' does not accept a placeholder; provide a valid value "
                    f"(\"?\" placeholders are only accepted for {number_field}, "
                    f"{', and '.join(sorted(QUOTED_PLACEHOLDER_FIELDS))})."
                )
            errors.append(
                f"'{field}' has an unquoted '?' value; a bare '?' is invalid YAML and breaks "
                f"GitHub's frontmatter rendering (header table / clickable Discussions links). "
                f"{fix_hint}"
            )
    return errors


def validate_authors_field(frontmatter: Dict) -> List[str]:
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


def validate_created_field(frontmatter: Dict) -> List[str]:
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


def validate_license_field(frontmatter: Dict) -> List[str]:
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


def validate_label_url_format(entries: list, field_name: str, example: str) -> List[str]:
    """Validate that entries follow the 'Label: URL' form.

    Accepts a string 'Label: URL' (with whitespace after the colon) or a
    single-key ``{Label: URL}`` dict with string label and URL. Every other
    shape — a bare scalar (int/bool/None), a list, or a multi-key dict — is
    rejected here rather than slipping through: ``validate_header`` normalizes
    dicts to strings before JSON-schema validation, so the schema never sees
    the original type and cannot catch these. Label/URL semantic rules
    (CIP/CPS references, PR vs merged) are validated separately by the
    per-document label-entry checks.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    if not isinstance(entries, list):
        return errors

    pattern = re.compile(r'^[^:\s][^:]*:\s+https?://\S+')
    for i, entry in enumerate(entries):
        if isinstance(entry, str):
            normalized = entry
        elif isinstance(entry, dict) and len(entry) == 1:
            label, url = next(iter(entry.items()))
            # A dict with a non-string label or URL cannot form 'Label: URL'.
            normalized = f"{label}: {url}" if isinstance(label, str) and isinstance(url, str) else None
        else:
            normalized = None

        if normalized is None or not pattern.match(normalized):
            errors.append(
                f"'{field_name}' entry {i+1}: must be in the form 'Label: URL'. "
                f"Got: {entry!r}. "
                f"Example: {example!r}"
            )
    return errors


def validate_directory_name(frontmatter: Dict, file_path: Path, field_name: str) -> List[str]:
    """Validate that a document with an assigned number lives in a correctly-named directory.

    For number N, the parent directory must be '<PREFIX>-NNNN' (zero-padded to
    4 digits; no truncation for numbers >= 10000), where the prefix is the
    number field name ('CIP' or 'CPS'). Unassigned documents (any
    UNASSIGNED_PLACEHOLDERS value) skip the number-match check, but
    a numbered directory must still be correctly zero-padded.
    """
    errors = []

    # Regardless of the number field, a numbered directory must be zero-padded
    # to 4 digits (5+ digits without a leading zero for numbers >= 10000).
    dir_match = re.fullmatch(rf'{field_name}-(\d+)', file_path.parent.name)
    if dir_match:
        digits = dir_match.group(1)
        if len(digits) != 4 and (len(digits) < 4 or digits.startswith('0')):
            errors.append(
                f"Directory name '{file_path.parent.name}' is not zero-padded to 4 digits. "
                f"Expected: '{field_name}-{int(digits):04d}'"
            )
            return errors

    value = frontmatter.get(field_name)
    if value is None or isinstance(value, bool):
        return errors  # Missing field / invalid type is reported by header validation

    # Parse to integer; placeholders ('?', 'unassigned', ...) and other
    # non-numeric strings are handled by header validation
    try:
        num = int(value)
    except (ValueError, TypeError):
        return errors

    expected_dir = f"{field_name}-{num:04d}"
    actual_dir = file_path.parent.name

    if actual_dir != expected_dir:
        errors.append(
            f"Directory name '{actual_dir}' does not match the {field_name} number {num}. "
            f"Expected: '{expected_dir}'"
        )

    return errors


def validate_label_entries(entries: list, field_name: str, label_prefixes: List[str]) -> List[str]:
    """Validate semantic rules for labeled 'Label: URL' entries.

    When a label matches one of the given prefixes followed by -NNNN (e.g., CIP-0030):
    - URL must be a GitHub CIPs repository link (PR or merged document)
    - A '?' suffix on the number optionally marks a candidate (in PR); a PR
      URL without the suffix is also accepted
    - Merged URLs must NOT have '?' suffix (it is stale once merged)

    Other labels are allowed with any valid URL.

    Args:
        entries: List of label-URL entries (strings 'Label: URL' or dicts {Label: URL})
        field_name: Name of the field for error messages
        label_prefixes: List of label prefixes to validate (e.g., ['CIP'], ['CIP', 'CPS'])

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not isinstance(entries, list):
        return errors

    prefix_group = '|'.join(label_prefixes)
    label_pattern = re.compile(rf'^({prefix_group})-\d+(\?)?$')
    merged_pattern = re.compile(
        rf'https://github\.com/cardano-foundation/CIPs/(tree|blob)/[^/]+/({prefix_group})-\d+'
    )
    github_cips_pattern = re.compile(
        rf'^https://github\.com/cardano-foundation/CIPs/(pull/\d+|tree/[^/]+/({prefix_group})-\d+|blob/[^/]+/({prefix_group})-\d+)'
    )

    for i, entry in enumerate(entries):
        if isinstance(entry, dict) and len(entry) == 1:
            label, url = next(iter(entry.items()))
        elif isinstance(entry, str):
            match = re.match(r'^([^:]+):\s+(.+)$', entry)
            if not match:
                continue
            label, url = match.groups()
        else:
            continue

        label = label.strip()
        url = url.strip()

        label_match = label_pattern.match(label)
        if not label_match:
            continue  # Non-matching labels are allowed with any URL

        ref_id = label_match.group(0).rstrip('?')
        has_question_mark = label_match.group(2) == '?'

        if not github_cips_pattern.match(url):
            errors.append(
                f"'{field_name}' entry {i+1}: label '{label}' requires a GitHub CIPs repository URL "
                f"(pull request or merged document). Got: {url}"
            )
            continue

        is_merged = merged_pattern.search(url) is not None

        if is_merged and has_question_mark:
            errors.append(
                f"'{field_name}' entry {i+1}: Merged document should not have '?' suffix "
                f"(use '{ref_id}' instead of '{ref_id}?' since this document is merged)"
            )

    return errors
