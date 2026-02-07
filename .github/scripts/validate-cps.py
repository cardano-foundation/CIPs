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


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Parse YAML frontmatter from markdown content.
    
    Returns:
        Tuple of (frontmatter_dict, remaining_content) or (None, content) if no frontmatter
    """
    # Check for frontmatter delimiters - must start with ---
    if not content.startswith('---'):
        return None, content
    
    # Find the closing delimiter (--- on its own line)
    # Split on '\n---\n' or '\n---' at end of content
    lines = content.split('\n')
    if lines[0] != '---':
        return None, content
    
    # Find the closing ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i] == '---':
            end_idx = i
            break
    
    if end_idx is None:
        return None, content
    
    # Extract frontmatter (lines between the two --- markers)
    frontmatter_lines = lines[1:end_idx]

    # Preprocess: quote standalone '?' values (YAML interprets '?' as explicit key indicator)
    processed_lines = []
    for line in frontmatter_lines:
        # Match lines like "CPS: ?" or "Category: ?" and quote the ?
        if re.match(r'^[A-Za-z][A-Za-z ]*:\s+\?+\s*$', line):
            line = re.sub(r':\s+(\?+)\s*$', r': "\1"', line)
        processed_lines.append(line)

    frontmatter_text = '\n'.join(processed_lines)

    # Extract remaining content (everything after the closing ---)
    remaining_lines = lines[end_idx + 1:]
    remaining_content = '\n'.join(remaining_lines)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if frontmatter is None:
            return None, content
        return frontmatter, remaining_content
    except yaml.YAMLError as e:
        return None, content


def extract_h2_headers(content: str) -> List[str]:
    """Extract all H2 headers (##) from markdown content."""
    h2_pattern = r'^##\s+(.+)$'
    headers = []
    for line in content.split('\n'):
        match = re.match(h2_pattern, line)
        if match:
            headers.append(match.group(1).strip())
    return headers


def extract_h1_headers(content: str) -> List[str]:
    """Extract all H1 headers (#) from markdown content."""
    h1_pattern = r'^#\s+(.+)$'
    headers = []
    for line in content.split('\n'):
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
        # Format JSON Schema validation errors in a user-friendly way
        error_path = '.'.join(str(p) for p in e.path) if e.path else 'root'
        errors.append(f"Header validation error at '{error_path}': {e.message}")
    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")

    # Validate CIP label semantic rules (label/URL relationship)
    if 'Proposed Solutions' in frontmatter:
        errors.extend(_validate_cip_label_entries(frontmatter['Proposed Solutions'], 'Proposed Solutions'))
    if 'Discussions' in frontmatter:
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
    frontmatter, remaining_content = parse_frontmatter(content)
    if frontmatter is None:
        errors.append("Missing or invalid YAML frontmatter (must start with '---' and end with '---')")
        return False, errors
    
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

