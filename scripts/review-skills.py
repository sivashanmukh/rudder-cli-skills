#!/usr/bin/env python3
# review-skills.py — self-contained linter for this skills repo.
#
# Auto-discovers every SKILL.md under the given root (default: CWD) and checks
# it against a rubric covering frontmatter discipline, description quality,
# progressive disclosure, and security hygiene. No external dependencies —
# uses only the Python 3 stdlib.
#
# Usage:
#   scripts/review-skills.py [repo_root] [--strict] [--quiet] [--only <code,code,...>]
#
# Exit codes:
#   0  all checks pass (or only warnings in non-strict mode)
#   1  one or more errors
#   2  only warnings, but --strict is set
#
# Wired into .githooks/pre-push. Enable once per clone with:
#   git config core.hooksPath .githooks

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ───────────────────────── rubric thresholds ──────────────────────────────────
MAX_DESC_CHARS = 1024           # hard cap (frontmatter limit)
WARN_DESC_CHARS = 300           # soft cap (keep descriptions tight)
MIN_DESC_CHARS = 40             # too-short descriptions under-trigger
MAX_SKILL_LINES = 600           # fail: SKILL.md must not exceed this
WARN_SKILL_LINES = 400          # warn: progressive disclosure recommended

FORBIDDEN_TOP_LEVEL = {"version", "tags", "author"}  # belong in metadata:
REQUIRED_TOP_LEVEL = {"name", "description"}

# heuristic keyword banks
CREDENTIAL_PATTERNS = [
    r"\baccess[_ -]?token\b", r"\bapi[_ -]?key\b", r"\bsecret\b",
    r"\bOAuth\b", r"\bcredential", r"\bpassword\b", r"\bbearer\b",
    r"\.env\b", r"\btfvars\b", r"\btfstate\b",
]
EXTERNAL_CONTENT_PATTERNS = [
    r"\bAPI response", r"\bexternal (code|content|libraries|library)",
    r"\blive events?\b", r"\bwebhook\b", r"\bparse (the )?output",
    r"\bvalidate (the )?output", r"\bimport(ed)? (transformation|workspace)",
    r"\bdry[- ]?run output", r"\bMCP (tool )?response",
]
CURL_PIPE_SHELL = re.compile(r"curl[^\n|]*\|\s*(bash|sh)\b")
NPM_UNPINNED = re.compile(r"\bnpm (install|i)\s+(?!.*@[\d\w])[^\s`]+")
UVX_UNPINNED = re.compile(r"\buvx\s+(?!--)[a-zA-Z0-9_-]+(?!@)\b")
BASH_TOOL_HINT = re.compile(r"```(?:bash|sh|shell|console)\b", re.IGNORECASE)

# ───────────────────────── data model ─────────────────────────────────────────
@dataclass
class Finding:
    code: str
    severity: str          # "error" | "warn"
    path: Path
    message: str
    hint: str = ""

    def format(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        sev = "ERROR" if self.severity == "error" else "WARN "
        head = f"  [{sev}] {self.code}  {rel}"
        body = f"         {self.message}"
        if self.hint:
            body += f"\n         hint: {self.hint}"
        return f"{head}\n{body}"

@dataclass
class SkillCtx:
    skill_md: Path
    dir: Path
    frontmatter: dict = field(default_factory=dict)
    top_level_keys: list = field(default_factory=list)
    body: str = ""
    body_lines: int = 0
    raw: str = ""

# ───────────────────────── minimal frontmatter parser ─────────────────────────
def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text, []
    end_match = re.search(r"\n---\s*(?:\n|$)", text[3:])
    if not end_match:
        return None, text, []
    fm_raw = text[3:3 + end_match.start()].strip("\n")
    body = text[3 + end_match.end():]

    fm: dict = {}
    top_order: list = []
    current_parent: Optional[str] = None

    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        is_nested = line.startswith((" ", "\t"))
        stripped = line.strip()
        if ":" not in stripped:
            continue
        k, _, v = stripped.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith(('"', "'")) and v.endswith(('"', "'")) and len(v) >= 2:
            v = v[1:-1]

        if is_nested and current_parent:
            fm.setdefault(current_parent, {})
            if isinstance(fm[current_parent], dict):
                fm[current_parent][k] = v
        else:
            if v == "":
                current_parent = k
                fm[k] = {}
            else:
                current_parent = None
                fm[k] = v
            top_order.append(k)

    return fm, body, top_order

# ───────────────────────── discovery ──────────────────────────────────────────
def find_skills(root: Path):
    skips = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skips]
        if "SKILL.md" in filenames:
            yield Path(dirpath) / "SKILL.md"

def load_skill(skill_md: Path) -> SkillCtx:
    raw = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body, top_order = parse_frontmatter(raw)
    return SkillCtx(
        skill_md=skill_md,
        dir=skill_md.parent,
        frontmatter=fm or {},
        top_level_keys=top_order,
        body=body,
        body_lines=raw.count("\n") + 1,
        raw=raw,
    )

# ───────────────────────── per-skill checks ───────────────────────────────────
KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

def check_skill(ctx: SkillCtx) -> list:
    findings: list = []
    fm = ctx.frontmatter
    p = ctx.skill_md

    # E001 — frontmatter missing
    if not fm:
        findings.append(Finding("E001", "error", p,
            "SKILL.md has no YAML frontmatter block."))
        return findings

    # E002 / E003 — required fields
    for req in REQUIRED_TOP_LEVEL:
        if req not in fm or not str(fm.get(req, "")).strip():
            findings.append(Finding(
                "E00" + ("2" if req == "name" else "3"), "error", p,
                f"Required frontmatter field missing or empty: '{req}'."
            ))

    name = str(fm.get("name", "")).strip()
    desc = str(fm.get("description", "")).strip()

    # E004 — name matches directory
    if name and name != ctx.dir.name:
        findings.append(Finding("E004", "error", p,
            f"Frontmatter name '{name}' does not match directory '{ctx.dir.name}'."))

    # E005 — kebab-case
    if name and not KEBAB.match(name):
        findings.append(Finding("E005", "error", p,
            f"Skill name '{name}' is not lowercase-kebab-case.",
            hint="use lowercase letters, digits, and hyphens only; start with a letter."))

    # E006 — forbidden top-level fields
    for bad in FORBIDDEN_TOP_LEVEL.intersection(ctx.top_level_keys):
        findings.append(Finding("E006", "error", p,
            f"Forbidden top-level frontmatter field: '{bad}'.",
            hint=f"move '{bad}' under 'metadata:' — top-level is reserved."))

    # description length: E007 (hard) / W002 (soft) / W010 (too short)
    if desc:
        if len(desc) > MAX_DESC_CHARS:
            findings.append(Finding("E007", "error", p,
                f"description is {len(desc)} chars (hard cap {MAX_DESC_CHARS})."))
        elif len(desc) > WARN_DESC_CHARS:
            findings.append(Finding("W002", "warn", p,
                f"description is {len(desc)} chars (soft cap {WARN_DESC_CHARS}).",
                hint="tighten to a single sentence: '<capability>. Use when <trigger>.'"))
        if len(desc) < MIN_DESC_CHARS:
            findings.append(Finding("W010", "warn", p,
                f"description is only {len(desc)} chars — likely under-triggers.",
                hint="add a concrete capability statement and a 'Use when …' clause."))

    # W009 — description starts with 'Use when' (no capability statement first)
    if desc and desc.lower().startswith("use when"):
        findings.append(Finding("W009", "warn", p,
            "description starts with 'Use when …' but has no capability statement first.",
            hint="prepend a concrete capability: 'Creates/manages/validates X. Use when …'"))

    # W001 — description missing 'Use when' trigger clause
    if desc and "use when" not in desc.lower():
        findings.append(Finding("W001", "warn", p,
            "description has no 'Use when …' trigger clause.",
            hint="append 'Use when <user phrasing that should fire this skill>.'"))

    # file size / progressive disclosure: E008 (hard) / W003 (soft)
    refs_dir = ctx.dir / "references"
    if ctx.body_lines > MAX_SKILL_LINES:
        findings.append(Finding("E008", "error", p,
            f"SKILL.md is {ctx.body_lines} lines (hard cap {MAX_SKILL_LINES}).",
            hint="extract deep reference material into 'references/*.md' and link from SKILL.md."))
    elif ctx.body_lines > WARN_SKILL_LINES and not refs_dir.is_dir():
        findings.append(Finding("W003", "warn", p,
            f"SKILL.md is {ctx.body_lines} lines and has no references/ subdirectory.",
            hint="skills >400 lines should use progressive disclosure via references/."))

    # E009 — curl|bash (any shape)
    if CURL_PIPE_SHELL.search(ctx.raw):
        findings.append(Finding("E009", "error", p,
            "found a 'curl … | bash/sh' pattern.",
            hint="link to the official install guide instead of shipping a pipe-to-shell."))

    # W007 — npm install without version pin
    for m in NPM_UNPINNED.finditer(ctx.body):
        snippet = m.group(0)
        if "@" in snippet or snippet.strip().endswith("install"):
            continue
        findings.append(Finding("W007", "warn", p,
            f"npm install without version pin: '{snippet.strip()}'.",
            hint="pin with '@<version>' or link to official install docs."))
        break

    # W008 — uvx without version pin
    for m in UVX_UNPINNED.finditer(ctx.body):
        snippet = m.group(0)
        if "@" in snippet:
            continue
        findings.append(Finding("W008", "warn", p,
            f"uvx invocation without version pin: '{snippet.strip()}'.",
            hint="pin with 'tool@<version>' and add first-party provenance if applicable."))
        break

    body_low = ctx.body.lower()

    # W004 — credential keywords without Credential Security section
    if any(re.search(p_, body_low) for p_ in CREDENTIAL_PATTERNS):
        if "credential security" not in body_low and "## credentials" not in body_low:
            findings.append(Finding("W004", "warn", p,
                "skill references tokens/credentials but has no 'Credential Security' section.",
                hint="add a section covering env-var refs, no echo/log, .env in .gitignore."))

    # W005 — external-content keywords without Handling External Content section
    if any(re.search(p_, body_low) for p_ in EXTERNAL_CONTENT_PATTERNS):
        if "handling external content" not in body_low and "untrusted" not in body_low:
            findings.append(Finding("W005", "warn", p,
                "skill processes external/remote content but has no 'Handling External Content' section.",
                hint="add a section naming untrusted sources and telling the agent to extract only expected structured fields."))

    # W006 — shell-using skill without allowed-tools declared
    if BASH_TOOL_HINT.search(ctx.body) and "allowed-tools" not in fm:
        findings.append(Finding("W006", "warn", p,
            "skill shows shell commands but declares no 'allowed-tools' in frontmatter.",
            hint="pin exact patterns, e.g. 'allowed-tools: \"Bash(rudder-cli *), Read, Write, Edit\"'."))

    return findings

# ───────────────────────── repo-level checks ──────────────────────────────────
def check_repo(root: Path, skills: list) -> list:
    findings: list = []

    # W011 — duplicate/near-duplicate descriptions across skills
    seen_desc: dict = {}
    for ctx in skills:
        desc = str(ctx.frontmatter.get("description", "")).strip().lower()
        if not desc:
            continue
        key = re.sub(r"[^a-z0-9 ]", "", desc)[:80]
        if key in seen_desc:
            findings.append(Finding("W011", "warn", ctx.skill_md,
                f"description starts identically to {seen_desc[key].relative_to(root)} — check distinctiveness.",
                hint="sibling skills must be reliably distinguishable from their descriptions."))
        else:
            seen_desc[key] = ctx.skill_md

    # W012 — no CHANGELOG / changelog mechanism
    if not any((root / n).exists() for n in ("CHANGELOG.md", ".changes", ".changie.yaml")):
        findings.append(Finding("W012", "warn", root,
            "repo has no CHANGELOG.md, .changes/, or .changie.yaml.",
            hint="adopt a changelog mechanism (changie works well) before next release."))

    # W013 — contributor docs
    if not (root / "CONTRIBUTING.md").exists():
        findings.append(Finding("W013", "warn", root,
            "no CONTRIBUTING.md at repo root.",
            hint="ship frontmatter schema, naming rules, placement guide, and PR checklist."))

    # W014 — marketplace-vs-plugin version drift (best-effort)
    mkt = root / ".claude-plugin" / "marketplace.json"
    if mkt.exists():
        try:
            import json
            data = json.loads(mkt.read_text())
            for entry in data.get("plugins", []):
                src = entry.get("source", "")
                ver_marketplace = entry.get("version")
                if not ver_marketplace or not src:
                    continue
                src_path = (root / src).resolve()
                pj = src_path / ".claude-plugin" / "plugin.json"
                if pj.exists():
                    pdata = json.loads(pj.read_text())
                    ver_plugin = pdata.get("version")
                    if ver_plugin and ver_plugin != ver_marketplace:
                        findings.append(Finding("W014", "warn", pj,
                            f"version drift: plugin.json='{ver_plugin}' vs marketplace.json='{ver_marketplace}'.",
                            hint="single-source the version (pick one file and delete the other's version field)."))
        except Exception as e:
            findings.append(Finding("W014", "warn", mkt,
                f"could not parse marketplace.json: {e}"))

    return findings

# ───────────────────────── pretty printing ────────────────────────────────────
RUBRIC = """\
Rubric codes:
  E001 frontmatter missing          E002 name missing         E003 description missing
  E004 name≠dir                     E005 name not kebab-case  E006 forbidden top-level key
  E007 description >1024 chars      E008 SKILL.md >600 lines  E009 curl|bash pipe
  W001 no 'Use when …' clause       W002 description >300 chars
  W003 SKILL.md >400 lines, no references/
  W004 credentials without Credential Security section
  W005 external content without Handling External Content section
  W006 shell commands without allowed-tools declared
  W007 npm install without version pin    W008 uvx without version pin
  W009 description has no capability statement (starts with 'Use when')
  W010 description under 40 chars
  W011 sibling descriptions too similar   W012 no changelog mechanism
  W013 no CONTRIBUTING.md                 W014 marketplace/plugin version drift
"""

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills repo reviewer.")
    ap.add_argument("root", nargs="?", default=".",
                    help="repo root to scan (default: current directory)")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors")
    ap.add_argument("--quiet", action="store_true",
                    help="only print findings and summary")
    ap.add_argument("--only", default="",
                    help="comma-separated list of codes to include (e.g. E006,W004)")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    only = {c.strip().upper() for c in args.only.split(",") if c.strip()}

    skill_paths = list(find_skills(root))
    if not skill_paths:
        print(f"no SKILL.md files found under {root}", file=sys.stderr)
        return 0

    if not args.quiet:
        print(f"skills review: scanning {len(skill_paths)} skill(s) under {root}")

    contexts = [load_skill(p) for p in skill_paths]

    findings: list = []
    for ctx in contexts:
        findings.extend(check_skill(ctx))
    findings.extend(check_repo(root, contexts))

    if only:
        findings = [f for f in findings if f.code in only]

    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    for f in sorted(findings, key=lambda x: (x.severity != "error", str(x.path), x.code)):
        print(f.format(root))

    if not args.quiet:
        print()
        print(f"summary: {len(errors)} error(s), {len(warns)} warning(s), "
              f"across {len(skill_paths)} skill(s).")
        if findings:
            print()
            print(RUBRIC, end="")

    if errors:
        return 1
    if warns and args.strict:
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
