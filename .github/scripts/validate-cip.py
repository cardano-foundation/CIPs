#!/usr/bin/env python3
"""
Validation script for CIP README.md files.
Validates YAML headers and required sections.

Rules shared with the CPS validator live in validation_common.py.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import jsonschema
except ImportError:
    print("Error: jsonschema library is required. Install it with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

from validation_common import (
    parse_frontmatter,
    _strip_fenced_code_blocks,
    extract_h2_headers,
    extract_h1_headers,
    validate_line_endings,
    validate_no_h1_headings,
    humanize_schema_error,
    validate_number_field,
    validate_leading_zero_lines,
    validate_unquoted_question_marks,
    validate_authors_field,
    validate_created_field,
    validate_license_field,
    validate_label_url_format,
    validate_label_entries,
    validate_directory_name,
)


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
        # Translate the raw library error into a friendly, actionable message
        errors.append(humanize_schema_error(e))
    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")

    # Friendly per-field value checks (schema enforces only type/structure for these)
    errors.extend(validate_number_field(frontmatter, 'CIP'))
    errors.extend(_validate_title_field(frontmatter))
    errors.extend(_validate_status_field(frontmatter))
    errors.extend(validate_authors_field(frontmatter))
    errors.extend(_validate_implementors_field(frontmatter))
    errors.extend(validate_created_field(frontmatter))
    errors.extend(validate_license_field(frontmatter))
    errors.extend(_validate_solution_to_format(frontmatter))

    # Validate CIP/CPS label semantic rules on Discussions
    if 'Discussions' in frontmatter:
        errors.extend(validate_label_url_format(
            frontmatter['Discussions'], 'Discussions',
            'Original PR: https://github.com/cardano-foundation/CIPs/pull/123'
        ))
        errors.extend(validate_label_entries(frontmatter['Discussions'], 'Discussions', ['CIP', 'CPS']))
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
            if header.lower() == 'open questions':
                errors.append(
                    "'Open Questions' is not a valid CIP section (it is a CPS-only section). "
                    "Move open questions into 'Rationale: How does this CIP achieve its goals?', "
                    "e.g. as an '### Open Questions' subsection."
                )
            else:
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
                f"'Solution To' entry '{canonical}' references a CPS that has no folder in this "
                f"repository. Check the number is correct; you may mark it '{canonical}?' if it "
                f"intentionally references a not-yet-merged CPS."
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

    # Check for unquoted leading zeros in the CIP field (YAML loses this
    # information when it parses the value as a number)
    errors.extend(validate_leading_zero_lines(raw_lines, frontmatter, 'CIP'))

    if raw_lines:
        errors.extend(validate_unquoted_question_marks(raw_lines, 'CIP'))
        errors.extend(validate_header_whitespace(raw_lines))

    # Validate the directory name matches the assigned CIP number
    dir_errors = validate_directory_name(frontmatter, file_path, 'CIP')
    errors.extend(dir_errors)

    header_errors = validate_header(frontmatter)
    errors.extend(header_errors)

    errors.extend(validate_solution_to(frontmatter, file_path))

    h1_errors = validate_no_h1_headings(remaining_content)
    errors.extend(h1_errors)

    section_errors = validate_sections(remaining_content)
    errors.extend(section_errors)

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
