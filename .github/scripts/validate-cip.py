#!/usr/bin/env python3
"""
Validation script for CIP README.md files.
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


# Required fields for CIP headers (in required order)
CIP_REQUIRED_FIELDS_ORDER = [
    'CIP', 'Title', 'Category', 'Status', 'Authors',
    'Implementors', 'Discussions', 'Created', 'License'
]
CIP_REQUIRED_FIELDS = set(CIP_REQUIRED_FIELDS_ORDER)

# Optional fields (allowed but not required)
CIP_OPTIONAL_FIELDS = {'Solution To'}

# Canonical order of all known fields; optional fields, when present,
# must appear in their position here (Solution To goes between Discussions and Created).
CIP_FIELDS_ORDER = [
    'CIP', 'Title', 'Category', 'Status', 'Authors',
    'Implementors', 'Discussions', 'Solution To', 'Created', 'License'
]

# Required sections (H2 headers) in required order
CIP_REQUIRED_SECTIONS_ORDER = [
    'Abstract',
    'Motivation: Why is this CIP necessary?',
    'Specification',
    'Rationale: How does this CIP achieve its goals?',
    'Path to Active',
    'Copyright',
]
CIP_REQUIRED_SECTIONS = set(CIP_REQUIRED_SECTIONS_ORDER)

# Optional H2 sections (allowed but not required)
# These should appear after the required sections, before Copyright
CIP_OPTIONAL_SECTIONS = {
    'Versioning',
    'References',
    'Appendix',
    'Appendices',
    'Acknowledgments',
    'Acknowledgements',
}

# Required H3 subsections under "Path to Active"
PATH_TO_ACTIVE_SUBSECTIONS = {
    'Acceptance Criteria',
    'Implementation Plan',
}

# Load CIP header schema
SCHEMA_PATH = Path(__file__).parent.parent / 'schemas' / 'cip-header.schema.json'
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    CIP_HEADER_SCHEMA = json.load(f)


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], Optional[str], Optional[List[str]]]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, remaining_content, raw_lines) or (None, content, None) if no frontmatter
    """
    # Check for frontmatter delimiters - must start with ---
    if not content.startswith('---'):
        return None, content, None

    # Find the closing delimiter (--- on its own line)
    lines = content.split('\n')
    if lines[0] != '---':
        return None, content, None

    # Find the closing ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i] == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, content, None

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
            return None, content, None
        return frontmatter, remaining_content, frontmatter_lines
    except yaml.YAMLError:
        return None, content, None
    except ValueError:
        # Catches invalid date values that YAML tries to parse (e.g., month 13)
        return None, content, None


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


def extract_section_body(content: str, section_name: str) -> str:
    """Extract the body text under a specific H2 section, until the next H2 or EOF.

    H2 boundaries inside fenced code blocks are ignored so that example
    markdown in code fences does not split or terminate a section body.
    """
    lines = content.split('\n')
    masked_lines = _strip_fenced_code_blocks(content).split('\n')
    body_lines = []
    in_section = False

    for line, masked in zip(lines, masked_lines):
        h2_match = re.match(r'^##\s+(.+)$', masked)
        if h2_match:
            if in_section:
                break
            current_section = h2_match.group(1).strip()
            in_section = (current_section == section_name)
            continue

        if in_section:
            body_lines.append(line)

    return '\n'.join(body_lines)


def extract_h3_headers_under_section(content: str, section_name: str) -> List[str]:
    """Extract H3 headers (###) that appear under a specific H2 section.

    Both H2 boundary detection and H3 capture ignore fenced code blocks.
    """
    lines = _strip_fenced_code_blocks(content).split('\n')
    h3_headers = []
    in_section = False

    for line in lines:
        h2_match = re.match(r'^##\s+(.+)$', line)
        if h2_match:
            current_section = h2_match.group(1).strip()
            in_section = (current_section == section_name)
            continue

        if in_section:
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match:
                h3_headers.append(h3_match.group(1).strip())
            elif line.startswith('## '):
                break

    return h3_headers


def validate_line_endings(file_path: Path) -> List[str]:
    """Validate that file uses UNIX line endings (LF, not CRLF).

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    try:
        with open(file_path, 'rb') as f:
            content_bytes = f.read()

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


def _validate_field_order(frontmatter: Dict) -> List[str]:
    """Validate that header fields appear in the correct order.

    Both required and optional fields are checked against CIP_FIELDS_ORDER:
    when an optional field (e.g., Solution To) is present, it must appear in
    its canonical position. Unknown fields are caught by schema validation.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    actual_fields = list(frontmatter.keys())

    known_fields = CIP_REQUIRED_FIELDS | CIP_OPTIONAL_FIELDS
    actual_known = [f for f in actual_fields if f in known_fields]

    expected_order = [f for f in CIP_FIELDS_ORDER if f in actual_known]

    if actual_known != expected_order:
        errors.append(
            f"Header fields are not in the correct order. "
            f"Expected: {', '.join(expected_order)}. "
            f"Got: {', '.join(actual_known)}"
        )

    return errors


def _validate_cip_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the CIP number field.

    Leading-zero detection is performed separately against raw lines.
    """
    errors = []
    if 'CIP' not in frontmatter:
        return errors
    value = frontmatter['CIP']
    if isinstance(value, bool):
        errors.append(
            f"'CIP' must be a positive integer (e.g., 30) or '?' if unassigned. Got: {value!r}"
        )
        return errors
    if isinstance(value, int):
        if value < 1:
            errors.append(
                f"'CIP' must be a positive integer (1 or greater) or '?' if unassigned. Got: {value}"
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
            f"'CIP' must be a positive integer (e.g., 30) or '?' if unassigned. Got: {value!r}"
        )
        return errors
    errors.append(
        f"'CIP' must be a positive integer or '?' if unassigned. Got: {value!r}"
    )
    return errors


def _validate_title_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the Title field."""
    errors = []
    if 'Title' not in frontmatter:
        return errors
    value = frontmatter['Title']
    if not isinstance(value, str):
        return errors
    if len(value) > 100:
        errors.append(
            f"'Title' must be at most 100 characters. Got {len(value)} characters: {value!r}"
        )
    if not value.strip():
        errors.append("'Title' must not be empty")
    return errors


def _validate_status_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the Status field."""
    errors = []
    if 'Status' not in frontmatter:
        return errors
    value = frontmatter['Status']
    if not isinstance(value, str):
        return errors
    if re.fullmatch(r'Proposed|Active|Inactive\s+\(.+\)', value):
        return errors
    errors.append(
        f"'Status' must be 'Proposed', 'Active', or 'Inactive (reason)' "
        f"(with a reason in parentheses, e.g. 'Inactive (superseded by CIP-NNNN)'). "
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


def _validate_implementors_field(frontmatter: Dict) -> List[str]:
    """Friendly validation of the Implementors field.

    Accepts:
      - the string 'N/A' (not applicable),
      - an empty list [] (no implementor yet), or
      - a list of 'Name <email-or-URI>' strings (mirroring 'Authors';
        the bracketed contact may be an email address or a project URI).
    """
    errors = []
    if 'Implementors' not in frontmatter:
        return errors
    value = frontmatter['Implementors']
    if isinstance(value, str):
        if value != 'N/A':
            errors.append(
                f"'Implementors' must be 'N/A' (not applicable), '[]' (no implementor yet), "
                f"or a list of 'Name <email-or-URI>' strings. Got: {value!r}"
            )
        return errors
    if isinstance(value, list):
        pattern = re.compile(r'^.+\s+<.+>$')
        for i, item in enumerate(value):
            if not isinstance(item, str) or not pattern.match(item):
                errors.append(
                    f"'Implementors' entry {i+1}: must be in the form 'Name <email-or-URI>'. "
                    f"Got: {item!r}. Examples: 'John Doe <john.doe@email.domain>' "
                    f"or 'Project Catalyst <https://projectcatalyst.io/>'"
                )
        return errors
    errors.append(
        f"'Implementors' must be 'N/A', '[]', or a list of 'Name <email-or-URI>' strings. "
        f"Got: {value!r}"
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


def _validate_solution_to_format(frontmatter: Dict) -> List[str]:
    """Validate 'Solution To' entries.

    Each entry is ``CPS-NNNN[?] [| optional title]: URL`` (string form) or
    ``{CPS-NNNN[?] [| optional title]: URL}`` (single-key dict form).

    - The number must be zero-padded to at least 4 digits and refer to a
      positive number.
    - Bare ``CPS-NNNN`` requires a ``/tree/<branch>/CPS-NNNN`` or
      ``/blob/<branch>/CPS-NNNN`` URL whose referent matches the label.
    - ``CPS-NNNN?`` requires a ``/pull/<N>`` URL.
    """
    errors = []
    entries = frontmatter.get('Solution To')
    if not isinstance(entries, list):
        return errors

    label_pattern = re.compile(r'^CPS-(\d+)(\?)?(?:\s*\|\s*[^:]+)?$')
    github_url_pattern = re.compile(
        r'^https://github\.com/cardano-foundation/CIPs/'
        r'(?:pull/\d+|tree/[^/]+/CPS-\d+|blob/[^/]+/CPS-\d+)(?:[/?#]|$)'
    )
    pr_url_pattern = re.compile(
        r'^https://github\.com/cardano-foundation/CIPs/pull/\d+(?:[/?#]|$)'
    )
    merged_url_pattern = re.compile(
        r'^https://github\.com/cardano-foundation/CIPs/(?:tree|blob)/[^/]+/CPS-(\d+)(?:[/?#]|$)'
    )

    for i, entry in enumerate(entries):
        # Parse (label, url) from string or single-key dict form
        if isinstance(entry, dict) and len(entry) == 1:
            label, url = next(iter(entry.items()))
            if not isinstance(label, str) or not isinstance(url, str):
                errors.append(
                    f"'Solution To' entry {i+1}: dict form must have string label and URL. "
                    f"Got: {entry!r}"
                )
                continue
        elif isinstance(entry, str):
            m = re.match(r'^([^:]+):\s+(.+)$', entry)
            if not m:
                errors.append(
                    f"'Solution To' entry {i+1}: must be in the form "
                    f"'CPS-NNNN[?] [| optional title]: URL'. Got: {entry!r}"
                )
                continue
            label, url = m.groups()
        else:
            errors.append(
                f"'Solution To' entry {i+1}: must be a 'Label: URL' string or "
                f"single-key dict mapping label to URL. Got: {entry!r}"
            )
            continue

        label = label.strip()
        url = url.strip()

        label_match = label_pattern.match(label)
        if not label_match:
            errors.append(
                f"'Solution To' entry {i+1}: label must be 'CPS-NNNN' "
                f"(or 'CPS-NNNN?' for a CPS still in PR), optionally followed by "
                f"' | descriptive title'. Got label: {label!r}"
            )
            continue

        digits = label_match.group(1)
        is_candidate = label_match.group(2) == '?'

        if len(digits) < 4 or int(digits) == 0:
            errors.append(
                f"'Solution To' entry {i+1}: CPS number must be zero-padded to at "
                f"least 4 digits and refer to a positive number. Got label: {label!r}"
            )
            continue

        ref_number = int(digits)

        if not github_url_pattern.match(url):
            errors.append(
                f"'Solution To' entry {i+1}: URL must be a GitHub CIPs repository "
                f"link (a pull request, or tree/blob pointing to a CPS folder). "
                f"Got: {url}"
            )
            continue

        is_pr = pr_url_pattern.match(url) is not None
        merged_match = merged_url_pattern.match(url)

        if is_candidate:
            if not is_pr:
                errors.append(
                    f"'Solution To' entry {i+1}: 'CPS-{ref_number:04d}?' indicates a "
                    f"candidate (in PR), so URL must be a pull-request URL. "
                    f"Got: {url}"
                )
        else:
            if not merged_match:
                errors.append(
                    f"'Solution To' entry {i+1}: bare 'CPS-{ref_number:04d}' requires a "
                    f"/tree/<branch>/CPS-NNNN or /blob/<branch>/CPS-NNNN URL "
                    f"(use 'CPS-{ref_number:04d}?' with a /pull/<N> URL for an in-PR CPS). "
                    f"Got: {url}"
                )
            else:
                url_number = int(merged_match.group(1))
                if url_number != ref_number:
                    errors.append(
                        f"'Solution To' entry {i+1}: label 'CPS-{ref_number:04d}' "
                        f"does not match URL referent 'CPS-{url_number:04d}'."
                    )

    return errors


def _validate_discussions_format(entries: list) -> List[str]:
    """Validate that string Discussions entries follow the 'Label: URL' form.

    String entries must be of the form 'Label: URL' (with whitespace after the
    colon). Dict entries ({Label: URL}) are validated by the JSON schema.

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
                f"'Discussions' entry {i+1}: must be in the form 'Label: URL'. "
                f"Got: {entry!r}. "
                f"Example: 'Original PR: https://github.com/cardano-foundation/CIPs/pull/123'"
            )
    return errors


def _validate_label_entries(entries: list, field_name: str, label_prefixes: List[str]) -> List[str]:
    """Validate semantic rules for labeled 'Label: URL' entries.

    When a label matches one of the given prefixes followed by -NNNN (e.g., CIP-0030):
    - URL must be a GitHub CIPs repository link (PR or merged document)
    - Pull request URLs require '?' suffix on the number (candidate)
    - Merged URLs must NOT have '?' suffix

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
    pr_pattern = re.compile(r'https://github\.com/cardano-foundation/CIPs/pull/\d+')
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

        is_pr = pr_pattern.search(url) is not None
        is_merged = merged_pattern.search(url) is not None

        if is_pr and not has_question_mark:
            errors.append(
                f"'{field_name}' entry {i+1}: Pull request URL requires '?' suffix on the reference "
                f"(use '{ref_id}?' instead of '{ref_id}' to indicate candidate status)"
            )
        elif is_merged and has_question_mark:
            errors.append(
                f"'{field_name}' entry {i+1}: Merged document should not have '?' suffix "
                f"(use '{ref_id}' instead of '{ref_id}?' since this document is merged)"
            )

    return errors


def _entry_url(entry) -> Optional[str]:
    """Extract URL from a Discussions entry (string 'Label: URL', plain URL, or {Label: URL})."""
    if isinstance(entry, dict) and len(entry) == 1:
        _, url = next(iter(entry.items()))
        return url.strip() if isinstance(url, str) else None
    if isinstance(entry, str):
        match = re.match(r'^([^:]+):\s+(.+)$', entry)
        if match:
            return match.group(2).strip()
        return entry.strip()
    return None


def _validate_discussions_has_pr(entries) -> List[str]:
    """Validate that Discussions includes at least one PR link to the CIPs repo."""
    errors = []
    if not isinstance(entries, list):
        return errors

    pr_pattern = re.compile(r'^https://github\.com/cardano-foundation/CIPs/pull/\d+(?:[/?#].*)?$')
    for entry in entries:
        url = _entry_url(entry)
        if url and pr_pattern.match(url):
            return errors

    errors.append(
        "'Discussions' must include at least one pull request link of the form "
        "'https://github.com/cardano-foundation/CIPs/pull/<N>'"
    )
    return errors


def validate_header(frontmatter: Dict) -> List[str]:
    """Validate the YAML frontmatter header for CIPs.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate field order
    errors.extend(_validate_field_order(frontmatter))

    # Normalize and run JSON Schema validation
    try:
        frontmatter_for_schema = {}
        for key, value in frontmatter.items():
            if key == 'Created' and hasattr(value, 'isoformat'):
                # Handle date objects from PyYAML (datetime.date or datetime.datetime)
                frontmatter_for_schema[key] = value.isoformat()
            elif key == 'Discussions' and isinstance(value, list):
                # Convert dictionary entries to string format "Label: URL"
                normalized_list = []
                for item in value:
                    if isinstance(item, dict):
                        if len(item) == 1:
                            label, url = next(iter(item.items()))
                            normalized_list.append(f"{label}: {url}")
                        else:
                            normalized_list.append(": ".join(f"{k}: {v}" for k, v in item.items()))
                    elif isinstance(item, str):
                        normalized_list.append(item)
                    else:
                        normalized_list.append(str(item))
                frontmatter_for_schema[key] = normalized_list
            else:
                frontmatter_for_schema[key] = value

        jsonschema.validate(instance=frontmatter_for_schema, schema=CIP_HEADER_SCHEMA)
    except jsonschema.ValidationError as e:
        error_path = '.'.join(str(p) for p in e.path) if e.path else 'root'
        errors.append(f"Header validation error at '{error_path}': {e.message}")
    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")

    # Friendly per-field value checks (schema enforces only type/structure for these)
    errors.extend(_validate_cip_field(frontmatter))
    errors.extend(_validate_title_field(frontmatter))
    errors.extend(_validate_status_field(frontmatter))
    errors.extend(_validate_authors_field(frontmatter))
    errors.extend(_validate_implementors_field(frontmatter))
    errors.extend(_validate_created_field(frontmatter))
    errors.extend(_validate_license_field(frontmatter))
    errors.extend(_validate_solution_to_format(frontmatter))

    # Validate CIP/CPS label semantic rules on Discussions
    if 'Discussions' in frontmatter:
        errors.extend(_validate_discussions_format(frontmatter['Discussions']))
        errors.extend(_validate_label_entries(frontmatter['Discussions'], 'Discussions', ['CIP', 'CPS']))
        errors.extend(_validate_discussions_has_pr(frontmatter['Discussions']))

    return errors


def validate_copyright_references_license(frontmatter: Dict, content: str) -> List[str]:
    """Validate that the Copyright section references the License field's abbreviation."""
    errors = []

    license_value = frontmatter.get('License')
    if not isinstance(license_value, str):
        return errors  # License presence/type handled by schema validation

    h2_headers = extract_h2_headers(content)
    copyright_header = next((h for h in h2_headers if h.lower() == 'copyright'), None)
    if copyright_header is None:
        return errors  # Missing-section error reported by validate_sections

    body = extract_section_body(content, copyright_header)
    if license_value not in body:
        errors.append(
            f"'Copyright' section must reference the License abbreviation '{license_value}'"
        )

    return errors


def validate_sections(content: str) -> List[str]:
    """Validate required sections exist at H2 level for CIPs.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    h2_headers = extract_h2_headers(content)
    found_sections = set(h2_headers)

    # Normalize headers to lowercase for case-insensitive comparison
    found_sections_lower = {h.lower() for h in found_sections}
    required_sections_lower = {h.lower() for h in CIP_REQUIRED_SECTIONS}
    optional_sections_lower = {h.lower() for h in CIP_OPTIONAL_SECTIONS}

    # Check for missing required sections (case-insensitive)
    missing_sections_lower = required_sections_lower - found_sections_lower
    if missing_sections_lower:
        missing_sections = {orig for orig in CIP_REQUIRED_SECTIONS
                            if orig.lower() in missing_sections_lower}
        errors.append(f"Missing required sections: {', '.join(sorted(missing_sections))}")

    # Check for unknown sections (not in required or optional)
    allowed_sections_lower = required_sections_lower | optional_sections_lower
    for header in h2_headers:
        if header.lower() not in allowed_sections_lower:
            errors.append(f"Unknown section: '{header}'. Only required and optional sections are allowed.")

    # Build a mapping from lowercase to expected capitalization
    expected_capitalization = {}
    for section in CIP_REQUIRED_SECTIONS:
        expected_capitalization[section.lower()] = section
    for section in CIP_OPTIONAL_SECTIONS:
        expected_capitalization[section.lower()] = section

    # Check for incorrect capitalization
    for header in h2_headers:
        header_lower = header.lower()
        if header_lower in expected_capitalization:
            expected = expected_capitalization[header_lower]
            if header != expected:
                errors.append(f"Section '{header}' has incorrect capitalization. Expected: '{expected}'")

    # Map found headers to their canonical names (for order comparison)
    canonical_headers = []
    for header in h2_headers:
        header_lower = header.lower()
        if header_lower in expected_capitalization:
            canonical_headers.append(expected_capitalization[header_lower])
        else:
            canonical_headers.append(header)

    # Extract just the required sections in the order they appear
    found_required_order = [h for h in canonical_headers if h in CIP_REQUIRED_SECTIONS]

    expected_required_order = [s for s in CIP_REQUIRED_SECTIONS_ORDER if s in found_required_order]

    if found_required_order != expected_required_order:
        errors.append(
            f"Sections are not in the correct order. "
            f"Expected: {', '.join(expected_required_order)}. "
            f"Got: {', '.join(found_required_order)}"
        )

    # Check that optional sections appear only between the last non-Copyright
    # required section ("Path to Active") and "Copyright".
    optional_sections_normalized = {s.lower() for s in CIP_OPTIONAL_SECTIONS}
    required_before_optional = [s for s in CIP_REQUIRED_SECTIONS_ORDER if s != 'Copyright']

    for i, header in enumerate(canonical_headers):
        header_lower = header.lower()
        if header_lower in optional_sections_normalized:
            for j in range(i + 1, len(canonical_headers)):
                following_header = canonical_headers[j]
                if following_header in required_before_optional:
                    errors.append(
                        f"Optional section '{header}' appears before required section '{following_header}'. "
                        f"Optional sections must appear after 'Path to Active' and before 'Copyright'."
                    )
                    break
            if 'Copyright' in canonical_headers[:i]:
                errors.append(
                    f"Optional section '{header}' appears after 'Copyright'. "
                    f"Optional sections must appear after 'Path to Active' and before 'Copyright'."
                )

    # CIP-specific: validate Path to Active H3 subsections
    path_to_active_found = any(h.lower() == 'path to active' for h in found_sections)
    if path_to_active_found:
        # Find the actual header text used (may have wrong capitalization)
        actual_header = next((h for h in h2_headers if h.lower() == 'path to active'), 'Path to Active')
        h3_headers = extract_h3_headers_under_section(content, actual_header)
        found_subsections_lower = {h.lower() for h in h3_headers}
        required_subsections_lower = {h.lower() for h in PATH_TO_ACTIVE_SUBSECTIONS}
        missing_subsections_lower = required_subsections_lower - found_subsections_lower
        if missing_subsections_lower:
            missing_subsections = {orig for orig in PATH_TO_ACTIVE_SUBSECTIONS
                                   if orig.lower() in missing_subsections_lower}
            errors.append(
                f"'Path to Active' section missing required subsections: "
                f"{', '.join(sorted(missing_subsections))}"
            )

    return errors


def validate_header_whitespace(raw_lines: List[str]) -> List[str]:
    """Validate that header lines have no trailing whitespace.

    PyYAML strips trailing whitespace on load, so e.g. ``License: CC-BY-4.0  ``
    passes header validation despite the trailing spaces. This check inspects
    the raw frontmatter lines preserved by ``parse_frontmatter``.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    for line in raw_lines:
        if line and line != line.rstrip():
            errors.append(f"Header line has trailing whitespace: '{line}'")
    return errors


def _strip_code(content: str) -> str:
    """Strip fenced and inline code spans from markdown content."""
    no_fences = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    return re.sub(r'`[^`\n]*`', '', no_fences)


def _ref_folder_exists(repo_root: Path, prefix: str, number: int) -> bool:
    """Check whether a CIP/CPS folder exists at the repo root."""
    return (repo_root / f"{prefix}-{number:04d}").is_dir()


def validate_solution_to(frontmatter: Dict, file_path: Path) -> List[str]:
    """Validate Solution To entries against on-disk CPS folders.

    A bare ``CPS-NNNN`` must point to an existing CPS folder; a ``CPS-NNNN?``
    must point to one that does not exist yet (still in PR). Entry parsing
    accepts both ``"Label: URL"`` strings (with optional ``| title``) and
    single-key ``{Label: URL}`` dicts; format errors are reported by
    ``_validate_solution_to_format`` and silently skipped here.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    entries = frontmatter.get('Solution To')
    if not isinstance(entries, list):
        return errors

    repo_root = file_path.parent.parent
    label_pattern = re.compile(r'^CPS-(\d+)(\?)?(?:\s*\|\s*[^:]+)?$')

    for entry in entries:
        # Extract label from string ("Label: URL") or dict ({Label: URL}) form
        if isinstance(entry, dict) and len(entry) == 1:
            label = next(iter(entry.keys()))
            if not isinstance(label, str):
                continue
        elif isinstance(entry, str):
            m = re.match(r'^([^:]+):\s+.+$', entry)
            if not m:
                continue
            label = m.group(1)
        else:
            continue

        match = label_pattern.match(label.strip())
        if not match:
            continue  # Format error reported by _validate_solution_to_format
        number = int(match.group(1))
        is_candidate = match.group(2) == '?'
        canonical = f"CPS-{number:04d}"
        exists = _ref_folder_exists(repo_root, 'CPS', number)

        if is_candidate and exists:
            errors.append(
                f"'Solution To' entry '{canonical}?' indicates a candidate but "
                f"{canonical} folder exists; drop the '?'"
            )
        elif not is_candidate and not exists:
            errors.append(
                f"'Solution To' entry '{canonical}' references a CPS that has no folder; "
                f"add '?' if it is still in PR"
            )

    return errors


def validate_cross_references(content: str, frontmatter: Dict, file_path: Path) -> List[str]:
    """Validate that CIP-NNNN and CPS-NNNN references in the body point to existing folders.

    References inside fenced or inline code blocks are ignored (treated as examples).
    References suffixed with '?' are treated as candidates (still in PR) and skipped.
    Self-references to the CIP's own number are skipped.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    repo_root = file_path.parent.parent

    own_number = None
    own_value = frontmatter.get('CIP')
    if isinstance(own_value, int):
        own_number = own_value
    elif isinstance(own_value, str):
        try:
            own_number = int(own_value)
        except ValueError:
            own_number = None

    stripped = _strip_code(content)
    pattern = re.compile(r'\b(CIP|CPS)-(\d{1,5})(?!\d)(\??)')

    seen: Set[Tuple[str, int]] = set()
    for match in pattern.finditer(stripped):
        prefix, digits, candidate = match.group(1), match.group(2), match.group(3)
        number = int(digits)
        if candidate == '?':
            continue
        if prefix == 'CIP' and own_number is not None and number == own_number:
            continue
        key = (prefix, number)
        if key in seen:
            continue
        seen.add(key)
        if not _ref_folder_exists(repo_root, prefix, number):
            canonical = f"{prefix}-{number:04d}"
            errors.append(
                f"Body references '{canonical}' but no such folder exists in the repository "
                f"(use '{canonical}?' if it is still in PR)"
            )

    return errors


def validate_directory_name(frontmatter: Dict, file_path: Path) -> List[str]:
    """Validate that a CIP with an assigned number lives in a correctly-named directory.

    For CIP number N, the parent directory must be 'CIP-NNNN' (zero-padded to 4 digits;
    no truncation for numbers >= 10000). Unassigned CIPs ('?', '??', etc.) skip this check.
    """
    errors = []

    cip_value = frontmatter.get('CIP')
    if cip_value is None:
        return errors  # Missing field is reported by header validation

    # Skip unassigned CIPs ('?', '??', etc.)
    if isinstance(cip_value, str) and cip_value.startswith('?'):
        return errors

    # Parse to integer; non-numeric strings are caught by header validation
    try:
        cip_num = int(cip_value)
    except (ValueError, TypeError):
        return errors

    expected_dir = f"CIP-{cip_num:04d}"
    actual_dir = file_path.parent.name

    if actual_dir != expected_dir:
        errors.append(
            f"Directory name '{actual_dir}' does not match the CIP number {cip_num}. "
            f"Expected: '{expected_dir}'"
        )

    return errors


def is_cip_file(file_path: Path) -> bool:
    """Check if file path indicates a CIP document."""
    path_str = str(file_path)
    normalized_path = path_str.replace('\\', '/')
    return bool(re.search(r'(^|/)CIP-', normalized_path, re.IGNORECASE))


def validate_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single CIP README.md file.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if not is_cip_file(file_path):
        return False, [f"File path does not indicate a CIP document: {file_path}"]

    # Validate line endings (must check raw file bytes)
    line_ending_errors = validate_line_endings(file_path)
    errors.extend(line_ending_errors)

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    frontmatter, remaining_content, raw_lines = parse_frontmatter(content)
    if frontmatter is None:
        errors.append("Missing or invalid YAML frontmatter (must start with '---' and end with '---')")
        return False, errors

    # Check for leading zeros in CIP field (YAML loses this information)
    if raw_lines:
        for line in raw_lines:
            if re.match(r'^CIP:\s+0\d+', line):
                errors.append("CIP number must not have leading zeros")
                break

    if raw_lines:
        errors.extend(validate_header_whitespace(raw_lines))

    # Validate the directory name matches the assigned CIP number
    dir_errors = validate_directory_name(frontmatter, file_path)
    errors.extend(dir_errors)

    header_errors = validate_header(frontmatter)
    errors.extend(header_errors)

    errors.extend(validate_solution_to(frontmatter, file_path))

    h1_errors = validate_no_h1_headings(remaining_content)
    errors.extend(h1_errors)

    section_errors = validate_sections(remaining_content)
    errors.extend(section_errors)

    errors.extend(validate_cross_references(remaining_content, frontmatter, file_path))

    copyright_errors = validate_copyright_references_license(frontmatter, remaining_content)
    errors.extend(copyright_errors)

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    """Main entry point for the validation script."""
    if len(sys.argv) < 2:
        print("Usage: validate-cip.py <file1> [file2] ...", file=sys.stderr)
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
