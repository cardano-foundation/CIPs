#!/usr/bin/env python3
"""
Validation script for CPS README.md files.
Validates YAML headers and required sections.

Rules shared with the CIP validator live in validation_common.py.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import jsonschema
except ImportError:
    print("Error: jsonschema library is required. Install it with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

from validation_common import (
    parse_frontmatter,
    extract_h2_headers,
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
    errors.extend(validate_number_field(frontmatter, 'CPS'))
    errors.extend(_validate_title_field(frontmatter))
    errors.extend(_validate_status_field(frontmatter))
    errors.extend(validate_authors_field(frontmatter))
    errors.extend(validate_created_field(frontmatter))
    errors.extend(validate_license_field(frontmatter))

    # Validate 'Label: URL' string format, then the CIP label semantic rules
    for field in ('Proposed Solutions', 'Discussions'):
        if field in frontmatter:
            errors.extend(validate_label_url_format(
                frontmatter[field], field,
                'CIP-0001?: https://github.com/cardano-foundation/CIPs/pull/1'
            ))
            errors.extend(validate_label_entries(frontmatter[field], field, ['CIP']))

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

    # Check for unquoted leading zeros in the CPS field (YAML loses this
    # information when it parses the value as a number)
    errors.extend(validate_leading_zero_lines(raw_lines, frontmatter, 'CPS'))

    if raw_lines:
        errors.extend(validate_unquoted_question_marks(raw_lines, 'CPS'))

    # Validate the directory name matches the assigned CPS number
    dir_errors = validate_directory_name(frontmatter, file_path, 'CPS')
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
