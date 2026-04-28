"""Release driver for click-prism.

Implements the 18-step release process (see design 4.4.4.2). Run via
`make release VERSION=X.Y.Z`. Validates state, bumps version, finalizes
the changelog, freezes README badges, generates the coverage badge,
commits, tags, restores dynamic badges, opens a new Unreleased section,
commits, and pushes main + tag atomically.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
README = REPO_ROOT / "README.md"
PYTHON_VERSIONS_FILE = REPO_ROOT / ".python-versions"
COVERAGE_FILE = REPO_ROOT / "reports" / ".coverage"
BADGES_DIR = REPO_ROOT / "badges"

PACKAGE_NAME = "click-prism"
COVERAGE_FRESHNESS_SECONDS = 600  # 10 minutes
CATEGORIES = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


# ==================================================================================================
#  helpers
# ==================================================================================================
def run(cmd: list[str], **kw) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if result.returncode != 0:
        # Surface command + stderr so the failure is self-diagnosing.
        sys.stderr.write(f"\n$ {' '.join(cmd)}\n")
        if result.stdout:
            sys.stderr.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.stdout


def step(n: int, msg: str) -> None:
    print(f"  [{n:>2}] {msg}")


def fail(msg: str, code: int = 1) -> None:
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_semver(version: str) -> tuple[int, int, int]:
    if not SEMVER_RE.match(version):
        fail(f"VERSION {version!r} is not in X.Y.Z form")
    return tuple(int(p) for p in version.split("."))  # type: ignore[return-value]


def read_pyproject_version() -> str:
    text = PYPROJECT.read_text()
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not m:
        fail("Could not find version in pyproject.toml")
    return m.group(1)


def read_python_versions() -> list[str]:
    return [v.strip() for v in PYTHON_VERSIONS_FILE.read_text().split() if v.strip()]


# ==================================================================================================
#  validation steps (1-8)
# ==================================================================================================
def step_1_check_working_tree() -> None:
    step(1, "working tree on main and clean")
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    if branch != "main":
        fail(f"not on main (currently on {branch})")
    porcelain = run(["git", "status", "--porcelain"])
    if porcelain.strip():
        fail("working tree has uncommitted changes:\n" + porcelain)


def step_2_check_in_sync() -> None:
    step(2, "main in sync with origin")
    run(["git", "fetch", "origin", "main"])
    local = run(["git", "rev-parse", "HEAD"]).strip()
    remote = run(["git", "rev-parse", "origin/main"]).strip()
    if local != remote:
        fail(f"local main ({local[:8]}) does not match origin/main ({remote[:8]})")


def step_3_check_coverage_recent() -> None:
    step(3, f"coverage data exists and is < {COVERAGE_FRESHNESS_SECONDS}s old")
    if not COVERAGE_FILE.exists():
        fail(f"{COVERAGE_FILE} not found. Run `make release` (which runs `make coverage`).")
    age = time.time() - COVERAGE_FILE.stat().st_mtime
    if age > COVERAGE_FRESHNESS_SECONDS:
        fail(f"coverage data is {int(age)}s old (>{COVERAGE_FRESHNESS_SECONDS}s). Re-run `make coverage`.")


def step_4_check_version_upgrade(version: str) -> None:
    step(4, f"VERSION {version} is an upgrade")
    new = parse_semver(version)
    current = parse_semver(read_pyproject_version())
    if new <= current:
        fail(f"VERSION {version} is not greater than current {'.'.join(str(p) for p in current)}")


def step_5_check_tag_doesnt_exist(version: str) -> None:
    step(5, f"tag v{version} does not exist (local + remote)")
    tag = f"v{version}"
    if run(["git", "tag", "-l", tag]).strip():
        fail(f"tag {tag} already exists locally")
    if run(["git", "ls-remote", "--tags", "origin", tag]).strip():
        fail(f"tag {tag} already exists on origin")


def step_6_check_pypi_doesnt_have(version: str) -> None:
    step(6, f"version {version} is not on PyPI")
    url = f"https://pypi.org/pypi/{PACKAGE_NAME}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=10):
            fail(f"version {version} is already published on PyPI")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            fail(f"PyPI check returned HTTP {e.code}")


def step_7_check_classifiers_match() -> None:
    step(7, "Python classifiers in pyproject.toml match .python-versions")
    versions = read_python_versions()
    text = PYPROJECT.read_text()
    declared_classifiers = set(re.findall(r'"Programming Language :: Python :: ([\d.]+)"', text))
    expected = set(versions)
    missing = expected - declared_classifiers
    extra = declared_classifiers - expected
    if missing or extra:
        fail(
            f"classifiers do not match .python-versions. "
            f"Missing: {sorted(missing) or 'none'}; "
            f"Extra: {sorted(extra) or 'none'}"
        )


def step_8_check_changelog_has_entries() -> None:
    step(8, "CHANGELOG.md '## Unreleased' has at least one entry")
    text = CHANGELOG.read_text()
    m = re.search(r"^## Unreleased\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        fail("no '## Unreleased' section in CHANGELOG.md")
    if not re.search(r"^- ", m.group(1), re.MULTILINE):
        fail("'## Unreleased' has no bullet entries")


# ==================================================================================================
#  release commit steps (9-14)
# ==================================================================================================
def step_9_bump_version(version: str) -> None:
    step(9, f"bump version to {version}")
    run(["uv", "version", version])


def step_10_finalize_changelog(version: str) -> None:
    step(10, f"finalize CHANGELOG.md '## Unreleased' -> '## {version} ({date.today().isoformat()})'")
    text = CHANGELOG.read_text()
    # Capture the Unreleased block
    m = re.search(r"^## Unreleased\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        fail("no '## Unreleased' section to finalize")
    body = m.group(1)
    # Drop empty category sub-headers
    new_body_lines = []
    lines = body.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        cat_match = re.match(r"^### (\w+)\s*$", line)
        if cat_match and cat_match.group(1) in CATEGORIES:
            # peek ahead: is the section non-empty before the next ### or end?
            j = i + 1
            has_entry = False
            while j < len(lines) and not re.match(r"^### ", lines[j]):
                if lines[j].lstrip().startswith("- "):
                    has_entry = True
                    break
                j += 1
            if has_entry:
                new_body_lines.append(line)
                i += 1
                while i < len(lines) and not re.match(r"^### ", lines[i]):
                    new_body_lines.append(lines[i])
                    i += 1
            else:
                # skip this empty category and any blank lines that follow
                i += 1
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
        else:
            new_body_lines.append(line)
            i += 1
    new_body = "".join(new_body_lines).rstrip() + "\n"
    new_header = f"## {version} ({date.today().isoformat()})\n"
    text = text[: m.start()] + new_header + new_body + text[m.end() :]
    CHANGELOG.write_text(text)


def step_11_generate_coverage_badge() -> None:
    step(11, "generate coverage badge from ./reports/.coverage")
    BADGES_DIR.mkdir(parents=True, exist_ok=True)
    out = BADGES_DIR / "coverage.svg"
    # genbadge reads Cobertura-style coverage.xml, not the binary .coverage
    # database. Materialize the XML first from the same coverage data.
    coverage_xml = COVERAGE_FILE.parent / "coverage.xml"
    env = {**__import__("os").environ, "COVERAGE_FILE": str(COVERAGE_FILE)}
    run(["uv", "run", "coverage", "xml", "-o", str(coverage_xml)], env=env)
    run(["uv", "run", "genbadge", "coverage", "-i", str(coverage_xml), "-o", str(out)])


def step_12_freeze_badges(version: str) -> None:
    step(12, "freeze README badges (PyPI version, Python, coverage, license)")
    versions = read_python_versions()
    py_range = f"{versions[0]} | ... | {versions[-1]}" if len(versions) > 1 else versions[0]
    py_range_url = py_range.replace(" ", "%20").replace("|", "%7C")
    text = README.read_text()
    text = re.sub(
        r"https://img\.shields\.io/pypi/v/click-prism\.svg",
        f"https://img.shields.io/badge/PyPI-v{version}-blue",
        text,
    )
    text = re.sub(
        r"https://img\.shields\.io/pypi/pyversions/click-prism\.svg",
        f"https://img.shields.io/badge/python-{py_range_url}-blue",
        text,
    )
    # Pin the badge SVG to the tag's raw URL so the PyPI project page
    # (which can't resolve relative paths) renders the right image.
    text = re.sub(
        r"https://codecov\.io/gh/bertpl/click-prism/branch/main/graph/badge\.svg",
        f"https://raw.githubusercontent.com/bertpl/click-prism/v{version}/badges/coverage.svg",
        text,
    )
    # License badge SVG is already static; rewrite for idempotency.
    text = re.sub(
        r"https://img\.shields\.io/badge/license-[A-Za-z0-9-]+-[a-zA-Z]+",
        "https://img.shields.io/badge/license-BSD--3--Clause-blue",
        text,
    )
    # Pin LICENSE link target to the tag for parity with the coverage
    # badge (and so PyPI-rendered v0.1.0 page links to v0.1.0's LICENSE).
    text = re.sub(
        r"https://github\.com/bertpl/click-prism/blob/main/LICENSE",
        f"https://github.com/bertpl/click-prism/blob/v{version}/LICENSE",
        text,
    )
    README.write_text(text)


def step_13_commit_release(version: str) -> None:
    step(13, f"commit 'release: {version}'")
    run(["git", "add", "pyproject.toml", "uv.lock", "CHANGELOG.md", "README.md", "badges/coverage.svg"])
    run(["git", "commit", "-m", f"release: {version}"])


def step_14_tag(version: str) -> None:
    step(14, f"create tag v{version}")
    run(["git", "tag", f"v{version}"])


# ==================================================================================================
#  post-release steps (15-18)
# ==================================================================================================
def step_15_restore_dynamic_badges() -> None:
    step(15, "restore README badges to dynamic")
    text = README.read_text()
    text = re.sub(
        r"https://img\.shields\.io/badge/PyPI-v\d+\.\d+\.\d+-blue",
        "https://img.shields.io/pypi/v/click-prism.svg",
        text,
    )
    text = re.sub(
        r"https://img\.shields\.io/badge/python-[^)\s]+",
        "https://img.shields.io/pypi/pyversions/click-prism.svg",
        text,
    )
    text = re.sub(
        r"https://raw\.githubusercontent\.com/bertpl/click-prism/v[\d.]+/badges/coverage\.svg",
        "https://codecov.io/gh/bertpl/click-prism/branch/main/graph/badge.svg",
        text,
    )
    text = re.sub(
        r"https://github\.com/bertpl/click-prism/blob/v[\d.]+/LICENSE",
        "https://github.com/bertpl/click-prism/blob/main/LICENSE",
        text,
    )
    README.write_text(text)


def step_16_add_unreleased_section() -> None:
    step(16, "add fresh '## Unreleased' section to CHANGELOG.md")
    text = CHANGELOG.read_text()
    # Insert before the first "## " line that comes after the preamble.
    m = re.search(r"^## ", text, re.MULTILINE)
    if not m:
        fail("CHANGELOG.md has no version sections")
    insertion = "## Unreleased\n\n" + "\n".join(f"### {c}\n" for c in CATEGORIES) + "\n"
    text = text[: m.start()] + insertion + text[m.start() :]
    CHANGELOG.write_text(text)


def step_17_commit_next_cycle() -> None:
    step(17, "commit 'chore: begin next development cycle'")
    run(["git", "add", "CHANGELOG.md", "README.md"])
    run(["git", "commit", "-m", "chore: begin next development cycle"])


def step_18_push(version: str) -> None:
    step(18, f"push main + v{version} atomically")
    run(["git", "push", "--atomic", "origin", "main", f"refs/tags/v{version}"])


# ==================================================================================================
#  orchestration
# ==================================================================================================
def post_tag_recovery_hint(failed_step: int, version: str, also_step_17: bool) -> None:
    reset_count = 2 if also_step_17 else 1
    print(
        f"\nERROR: step {failed_step} failed.\n"
        f"Local state: release commit and tag v{version} created, not pushed.\n"
        f"To abort and retry:\n"
        f"  git tag -d v{version}\n"
        f"  git reset --hard HEAD~{reset_count}\n",
        file=sys.stderr,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="X.Y.Z (no leading v)")
    args = parser.parse_args()
    version = args.version
    parse_semver(version)

    print(f"Releasing {PACKAGE_NAME} v{version}\n")

    print("Validation:")
    step_1_check_working_tree()
    step_2_check_in_sync()
    step_3_check_coverage_recent()
    step_4_check_version_upgrade(version)
    step_5_check_tag_doesnt_exist(version)
    step_6_check_pypi_doesnt_have(version)
    step_7_check_classifiers_match()
    step_8_check_changelog_has_entries()

    print("\nRelease commit:")
    step_9_bump_version(version)
    step_10_finalize_changelog(version)
    step_11_generate_coverage_badge()
    step_12_freeze_badges(version)
    step_13_commit_release(version)
    step_14_tag(version)

    print("\nPost-release:")
    also_step_17 = False
    try:
        step_15_restore_dynamic_badges()
        step_16_add_unreleased_section()
        step_17_commit_next_cycle()
        also_step_17 = True
        step_18_push(version)
    except subprocess.CalledProcessError:
        # Identify which step failed by walking backward from the call stack
        # is fragile; just emit a generic recovery hint.
        post_tag_recovery_hint(15, version, also_step_17)
        sys.exit(1)
    except SystemExit:
        post_tag_recovery_hint(15, version, also_step_17)
        raise

    print(f"\nReleased v{version}.")


if __name__ == "__main__":
    main()
