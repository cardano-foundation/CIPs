#!/usr/bin/env python3
"""
Dead-link checker for CIP/CPS markdown documents.

This is a standalone, out-of-band tool: it is intentionally NOT run in CI
(external link checking from GitHub runners is unreliable due to anti-bot
measures, CAPTCHAs, and rate limiting). Run it locally, e.g.:

    python3 .github/scripts/check-links.py                  # all CIP/CPS READMEs
    python3 .github/scripts/check-links.py CIP-0030         # one proposal directory
    python3 .github/scripts/check-links.py CIP-0030/README.md --internal-only

Checks performed:
  - Internal (relative) links: the target file or directory must exist;
    '#anchor' fragments must match a heading in the target markdown file.
  - External (http/https) links: the URL must respond without a client or
    server error (HEAD request, falling back to GET where HEAD is refused).

Exit codes: 0 = no broken links (warnings allowed), 1 = broken links found,
2 = usage or I/O error.

Requires only the Python 3 standard library.
"""

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0 '
    'CIP-link-checker (+https://github.com/cardano-foundation/CIPs)'
)


class Link(NamedTuple):
    source: Path
    line: int
    target: str


class Problem(NamedTuple):
    source: Path
    line: int
    message: str
    is_warning: bool


def strip_code(content: str) -> str:
    """Blank out fenced code blocks and inline code spans, preserving line count."""
    lines = content.split('\n')
    out = []
    in_fence = False
    fence_marker = ''
    for line in lines:
        stripped = line.lstrip()
        if in_fence:
            out.append('')
            if stripped.startswith(fence_marker):
                in_fence = False
            continue
        m = re.match(r'(`{3,}|~{3,})', stripped)
        if m:
            in_fence = True
            fence_marker = m.group(1)[0] * 3
            out.append('')
            continue
        out.append(re.sub(r'`[^`\n]*`', '', line))
    return '\n'.join(out)


def extract_links(content: str) -> List[Tuple[int, str]]:
    """Extract link targets with 1-based line numbers from markdown content.

    Handles inline links [text](target), reference definitions [label]: target,
    and autolinks <http://...>. Image links are included (their targets must
    exist too).
    """
    links = []
    stripped = strip_code(content)
    for lineno, line in enumerate(stripped.split('\n'), start=1):
        # Inline links/images: capture the (...) target, tolerating one level
        # of nested parentheses (common in Wikipedia URLs)
        for m in re.finditer(r'!?\[[^\]]*\]\(\s*<?([^()<>\s]*(?:\([^()]*\)[^()\s]*)*)>?\s*(?:"[^"]*")?\)', line):
            if m.group(1):
                links.append((lineno, m.group(1)))
        # Reference-style definitions: [label]: target
        m = re.match(r'^\s*\[[^\]]+\]:\s+<?(\S+?)>?(?:\s+"[^"]*")?\s*$', line)
        if m:
            links.append((lineno, m.group(1)))
        # Autolinks: <http://...>
        for m in re.finditer(r'<(https?://[^>\s]+)>', line):
            links.append((lineno, m.group(1)))
    return links


def github_slug(heading: str, seen: Dict[str, int]) -> str:
    """Compute the GitHub anchor slug for a heading, handling duplicates."""
    # Strip inline code/emphasis markers and links ([text](url) -> text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', heading)
    text = text.strip().lower()
    text = re.sub(r'[^\w\- ]', '', text, flags=re.UNICODE)
    slug = text.replace(' ', '-')
    if slug in seen:
        seen[slug] += 1
        return f"{slug}-{seen[slug]}"
    seen[slug] = 0
    return slug


def heading_slugs(md_path: Path) -> Set[str]:
    """Return the set of GitHub anchor slugs for all headings in a markdown file."""
    try:
        content = md_path.read_text(encoding='utf-8')
    except Exception:
        return set()
    slugs: Set[str] = set()
    seen: Dict[str, int] = {}
    for line in strip_code(content).split('\n'):
        m = re.match(r'^ {0,3}(#{1,6})\s+(.*?)(?:\s+#+\s*)?$', line)
        if m:
            slugs.add(github_slug(m.group(2), seen))
        # Explicit HTML anchors: <a name="..."> / id="..." on any tag
        for m in re.finditer(r'\b(?:id|name)\s*=\s*["\']([^"\']+)["\']', line):
            slugs.add(m.group(1).lower())
    return slugs


def check_internal(link: Link, slug_cache: Dict[Path, Set[str]]) -> Optional[Problem]:
    """Check a relative link; return a Problem if broken, else None."""
    target, _, fragment = link.target.partition('#')
    target = urllib.parse.unquote(target)
    fragment = urllib.parse.unquote(fragment)

    if target:
        resolved = (link.source.parent / target).resolve()
        if not resolved.exists():
            return Problem(link.source, link.line,
                           f"broken internal link '{link.target}' (no such file or directory)", False)
    else:
        resolved = link.source.resolve()  # '#anchor' refers to the source file

    if fragment and resolved.is_file() and resolved.suffix.lower() in ('.md', '.markdown'):
        if resolved not in slug_cache:
            slug_cache[resolved] = heading_slugs(resolved)
        # GitHub's rendered-anchor prefix (e.g. #user-content-...) is also accepted
        slug = fragment.lower()
        candidates = {slug, slug.removeprefix('user-content-')}
        if not (candidates & slug_cache[resolved]):
            return Problem(link.source, link.line,
                           f"broken anchor '{link.target}' (no heading '#{fragment}' in {resolved.name})", False)
    return None


class ExternalChecker:
    """Checks external URLs with per-host rate limiting and global deduplication."""

    def __init__(self, timeout: float, delay: float, verbose: bool):
        self.timeout = timeout
        self.delay = delay
        self.verbose = verbose
        self.results: Dict[str, Optional[Tuple[str, bool]]] = {}  # url -> (message, is_warning) or None if OK
        self.last_request: Dict[str, float] = {}

    def _throttle(self, url: str) -> None:
        host = urllib.parse.urlsplit(url).netloc
        elapsed = time.monotonic() - self.last_request.get(host, 0)
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request[host] = time.monotonic()

    def _request(self, url: str, method: str) -> int:
        req = urllib.request.Request(url, method=method, headers={
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.status

    def check(self, url: str) -> Optional[Tuple[str, bool]]:
        """Return (message, is_warning) if the URL is broken/suspect, else None."""
        if url in self.results:
            return self.results[url]
        if self.verbose:
            print(f"  checking {url}", file=sys.stderr)
        result: Optional[Tuple[str, bool]] = None
        try:
            self._throttle(url)
            status = self._request(url, 'HEAD')
            if status >= 400:
                result = (f"HTTP {status}", False)
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 501):
                # Some servers refuse HEAD or block bots on HEAD; retry with GET
                try:
                    self._throttle(url)
                    status = self._request(url, 'GET')
                    if status >= 400:
                        result = (f"HTTP {status}", False)
                except urllib.error.HTTPError as e2:
                    result = self._classify_http_error(e2.code)
                except Exception as e2:
                    result = (f"request failed ({e2})", True)
            else:
                result = self._classify_http_error(e.code)
        except TimeoutError as e:
            # Could be a slow server or a local network issue; verify manually
            result = ("timed out (verify manually)", True)
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, TimeoutError):
                result = ("timed out (verify manually)", True)
            else:
                # DNS failure, connection refused, TLS error...
                result = (f"request failed ({reason})", False)
        except Exception as e:
            result = (f"request failed ({e})", True)
        self.results[url] = result
        return result

    @staticmethod
    def _classify_http_error(code: int) -> Tuple[str, bool]:
        if code == 429:
            return ("HTTP 429 (rate limited; likely fine, retry later)", True)
        if code == 403:
            return ("HTTP 403 (may be bot protection; verify manually)", True)
        return (f"HTTP {code}", False)


def collect_files(paths: List[str], repo_root: Path) -> List[Path]:
    if not paths:
        files = sorted(repo_root.glob('CIP-*/README.md')) + sorted(repo_root.glob('CPS-*/README.md'))
        if not files:
            print(f"error: no CIP-*/README.md or CPS-*/README.md found under {repo_root}", file=sys.stderr)
            sys.exit(2)
        return files
    files = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            found = sorted(path.rglob('*.md'))
            if not found:
                print(f"error: no markdown files under directory {path}", file=sys.stderr)
                sys.exit(2)
            files.extend(found)
        elif path.is_file():
            files.append(path)
        else:
            print(f"error: no such file or directory: {path}", file=sys.stderr)
            sys.exit(2)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Check CIP/CPS markdown files for dead internal and external links.')
    parser.add_argument('paths', nargs='*',
                        help='markdown files or directories to check '
                             '(default: all CIP-*/README.md and CPS-*/README.md)')
    parser.add_argument('--internal-only', action='store_true',
                        help='skip external (http/https) link checking')
    parser.add_argument('--timeout', type=float, default=10,
                        help='per-request timeout in seconds (default: 10)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='minimum delay between requests to the same host (default: 0.5)')
    parser.add_argument('--verbose', action='store_true',
                        help='print each external URL as it is checked')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    files = collect_files(args.paths, repo_root)

    problems: List[Problem] = []
    slug_cache: Dict[Path, Set[str]] = {}
    checker = ExternalChecker(args.timeout, args.delay, args.verbose)
    total_links = 0

    for md_file in files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"error: cannot read {md_file}: {e}", file=sys.stderr)
            sys.exit(2)

        for lineno, target in extract_links(content):
            total_links += 1
            link = Link(md_file, lineno, target)
            scheme = urllib.parse.urlsplit(target).scheme
            if scheme in ('http', 'https'):
                if args.internal_only:
                    continue
                result = checker.check(target)
                if result:
                    message, is_warning = result
                    label = 'suspect' if is_warning else 'broken'
                    problems.append(Problem(md_file, lineno,
                                            f"{label} external link '{target}': {message}", is_warning))
            elif scheme:
                continue  # mailto:, ipfs:, etc. — not checkable
            else:
                problem = check_internal(link, slug_cache)
                if problem:
                    problems.append(problem)

    broken = [p for p in problems if not p.is_warning]
    warnings = [p for p in problems if p.is_warning]

    current: Optional[Path] = None
    for p in sorted(problems, key=lambda p: (str(p.source), p.line)):
        if p.source != current:
            current = p.source
            print(f"\n{p.source}:")
        print(f"  line {p.line}: {p.message}")

    print(f"\nChecked {total_links} link(s) in {len(files)} file(s): "
          f"{len(broken)} broken, {len(warnings)} warning(s)")
    sys.exit(1 if broken else 0)


if __name__ == '__main__':
    main()
