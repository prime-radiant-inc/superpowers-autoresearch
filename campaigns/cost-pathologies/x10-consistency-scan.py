#!/usr/bin/env python3
"""A general-purpose cross-module consistency scanner (backlog campaign,
2026-08-02, Task 5, X10). Not fixture-hardcoded -- runs against any Python
tree and reports the shape of defect prior battery `cp-x1-wavecap` seeded
45 of (queue-execution campaign, 2026-08-01): each task's own brief
independently pins a naming, constant, message, or vocabulary choice for
what is really one shared concept, and nothing routes those choices
through a per-task reviewer, whose diff is scoped to one task at a time.
All 45 were greppable; whole-branch final reviewers still found 0/45.

Reports three kinds of finding, each with file:line pairs:

  1. same-identifier-different-value constants -- a module-level ALL_CAPS
     name assigned a literal scalar in two or more files, with two or
     more distinct values.
  2. near-miss identifier pairs for the same string-literal context --
     (a) two differently-named module constants across files bound to
     the SAME literal value, whose names share at least one
     underscore-delimited token (candidate naming drift for one config
     knob); (b) two differently-named custom exceptions, raised in
     different files, whose message templates share at least one
     significant word (candidate divergent wording for one error class).
  3. string-literal sets used across files with asymmetric membership --
     short, enum-like string literals (function-scoped, or attached to a
     named module-level container) that co-occur in one file's group and
     a different file's group with only partial overlap (candidate
     status/enum drift: one module has learned a value the others have
     not).

This WILL produce noise on a real repo (same-named constants and
near-miss identifiers are also legitimately unrelated much of the time).
Output is therefore ranked by confidence and capped at the top 20
findings; anything past the cap is rolled into a single suppressed-count
line rather than printed.

Usage: python3 x10-consistency-scan.py [PATH] [--top N] [--json]

Everything here is a static-analysis heuristic, not proof of a bug --
each finding is a candidate for a human (or a fix dispatch) to look at,
not an assertion.
"""
import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_EXCLUDE_DIRS = {
    "__pycache__", ".venv", "venv", ".git", "node_modules", "build", "dist",
    ".pytest_cache", ".mypy_cache", ".tox", "egg-info",
}

# Constant names that legitimately vary by design and would otherwise be
# the single biggest noise source for detector 1 -- kept short and
# generic (not tied to any one repo's vocabulary).
CONSTANT_NAME_BLOCKLIST = {"__all__", "VERSION", "__version__", "DEBUG"}

_CONST_NAME_RE = re.compile(r"^_*[A-Z][A-Z0-9_]*$")
_ENUM_TOKEN_RE = re.compile(r"^[a-z][a-z0-9_-]{0,19}$")
_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "in",
    "on", "for", "or", "and", "not", "this", "that", "it", "its", "with",
    "than", "no", "must", "should", "will", "at", "as", "by",
}


@dataclass
class Finding:
    category: str
    description: str
    confidence: float
    sites: list = field(default_factory=list)  # list of (file, lineno, label)

    def format(self):
        site_text = "; ".join(f"{f}:{l} ({label})" for f, l, label in self.sites)
        return f"[{self.confidence:.2f}] {self.category}: {self.description} -- {site_text}"


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def iter_python_files(root, include_tests=False):
    """Test files are excluded by default: assertion-shaped dict literals
    (`assert parse_x(...) == {"job_id": ..., "status": "queued"}`) create
    structural coincidences across unrelated tests -- shared dict *keys*
    that are not a real shared vocabulary -- and are this heuristic's
    single biggest false-positive source. The defects this scanner targets
    live in implementation modules; pass --include-tests to widen the
    sweep at the cost of that noise.
    """
    root = Path(root)
    for path in sorted(root.rglob("*.py")):
        if any(part in DEFAULT_EXCLUDE_DIRS for part in path.parts):
            continue
        if not include_tests and (path.name.startswith("test_") or path.name.endswith("_test.py")):
            continue
        yield path


# ---------------------------------------------------------------------------
# Per-file AST collection
# ---------------------------------------------------------------------------


class LiteralGroupCollector(ast.NodeVisitor):
    """Collects short, enum-like string literals into named groups: the
    enclosing function's name if inside one, else the target name of the
    nearest enclosing top-level module Assign, else "<module>". Literals
    are pulled from comparisons, container literals (list/set/tuple/dict
    keys and values), and bare return statements -- the three shapes an
    enum/status value most commonly appears in.
    """

    def __init__(self):
        self.groups = defaultdict(list)  # scope_name -> [(literal, lineno)]
        self._scope_stack = ["<module>"]

    def _scope(self):
        return self._scope_stack[-1]

    def _add(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and _ENUM_TOKEN_RE.match(node.value):
            self.groups[self._scope()].append((node.value, getattr(node, "lineno", None)))

    def visit_FunctionDef(self, node):
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node):
        if (
            self._scope() == "<module>"
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            self._scope_stack.append(node.targets[0].id)
            self.generic_visit(node)
            self._scope_stack.pop()
        else:
            self.generic_visit(node)

    def visit_Compare(self, node):
        for operand in [node.left] + list(node.comparators):
            self._add(operand)
        self.generic_visit(node)

    def visit_Return(self, node):
        if node.value is not None:
            self._add(node.value)
        self.generic_visit(node)

    def visit_List(self, node):
        for elt in node.elts:
            self._add(elt)
        self.generic_visit(node)

    visit_Set = visit_List

    def visit_Tuple(self, node):
        for elt in node.elts:
            self._add(elt)
        self.generic_visit(node)

    def visit_Dict(self, node):
        for key in node.keys:
            if key is not None:
                self._add(key)
        for value in node.values:
            self._add(value)
        self.generic_visit(node)


def _module_level_constants(tree):
    """Yields (name, value, lineno) for module-level ALL_CAPS names bound
    directly to a scalar literal (int/float/str/bool), at module scope
    only -- not inside a function, class, or conditional."""
    for stmt in tree.body:
        targets = None
        value = None
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            targets = [stmt.targets[0]]
            value = stmt.value
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            targets = [stmt.target]
            value = stmt.value
        if not targets or not isinstance(targets[0], ast.Name):
            continue
        name = targets[0].id
        if not _CONST_NAME_RE.match(name) or name in CONSTANT_NAME_BLOCKLIST:
            continue
        if isinstance(value, ast.Constant) and isinstance(value.value, (int, float, str, bool)):
            yield name, value.value, stmt.lineno


def _raise_sites(tree):
    """Yields (exception_class_name, message_template, lineno) for every
    `raise SomeError(...)` / `raise mod.SomeError(...)` whose first
    argument is a string constant or an f-string -- the static text
    concatenated, formatted placeholders collapsed to '{}'."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
            continue
        func = node.exc.func
        if isinstance(func, ast.Name):
            class_name = func.id
        elif isinstance(func, ast.Attribute):
            class_name = func.attr
        else:
            continue
        if not node.exc.args:
            continue
        first = node.exc.args[0]
        template = _string_template(first)
        if template is not None:
            yield class_name, template, node.lineno


def _string_template(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append("{}")
        return "".join(parts)
    return None


def _topic_tokens(template):
    words = re.findall(r"[a-z]+", template.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def _name_tokens(name):
    return {t for t in name.strip("_").lower().split("_") if t}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass
class FileFacts:
    path: Path
    constants: list
    raises: list
    literal_groups: dict


def collect_file_facts(path):
    try:
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None
    collector = LiteralGroupCollector()
    collector.visit(tree)
    return FileFacts(
        path=path,
        constants=list(_module_level_constants(tree)),
        raises=list(_raise_sites(tree)),
        literal_groups=dict(collector.groups),
    )


# ---------------------------------------------------------------------------
# Detector 1: same-identifier, different-value constants
# ---------------------------------------------------------------------------


def detect_constant_divergence(facts_by_file):
    by_name = defaultdict(list)  # name -> [(file, value, lineno)]
    for facts in facts_by_file:
        for name, value, lineno in facts.constants:
            by_name[name].append((facts.path, value, lineno))

    findings = []
    for name, occurrences in by_name.items():
        values = {value for _, value, _ in occurrences}
        files = {f for f, _, _ in occurrences}
        if len(values) < 2 or len(files) < 2:
            continue
        sites = [(str(f), l, f"{name} = {v!r}") for f, v, l in occurrences]
        findings.append(
            Finding(
                category="constant-divergence",
                description=f"{name!r} defined with {len(values)} different values across {len(files)} files",
                confidence=0.9,
                sites=sites,
            )
        )
    return findings


# ---------------------------------------------------------------------------
# Detector 2: near-miss identifier pairs
# ---------------------------------------------------------------------------


def detect_naming_drift_constants(facts_by_file):
    """2a: differently-named module constants across files bound to the
    SAME literal value, whose names share at least one token."""
    by_value = defaultdict(list)  # value -> [(file, name, lineno)]
    for facts in facts_by_file:
        for name, value, lineno in facts.constants:
            by_value[value].append((facts.path, name, lineno))

    seen_pairs = set()
    findings = []
    for value, occurrences in by_value.items():
        if len(occurrences) < 2:
            continue
        for i in range(len(occurrences)):
            for j in range(i + 1, len(occurrences)):
                file_a, name_a, line_a = occurrences[i]
                file_b, name_b, line_b = occurrences[j]
                if file_a == file_b or name_a == name_b:
                    continue
                key = tuple(sorted([(str(file_a), name_a), (str(file_b), name_b)]))
                if key in seen_pairs:
                    continue
                similarity = _jaccard(_name_tokens(name_a), _name_tokens(name_b))
                if similarity <= 0:
                    continue
                seen_pairs.add(key)
                findings.append(
                    Finding(
                        category="naming-drift",
                        description=(
                            f"{name_a!r} and {name_b!r} share value {value!r} and a name token "
                            "-- possible two names for one config knob"
                        ),
                        confidence=round(similarity, 2),
                        sites=[
                            (str(file_a), line_a, f"{name_a} = {value!r}"),
                            (str(file_b), line_b, f"{name_b} = {value!r}"),
                        ],
                    )
                )
    return findings


def detect_naming_drift_errors(facts_by_file):
    """2b: differently-named custom exceptions raised in different files
    whose message templates share at least one significant word."""
    all_raises = []  # (file, class_name, template, lineno)
    for facts in facts_by_file:
        for class_name, template, lineno in facts.raises:
            all_raises.append((facts.path, class_name, template, lineno))

    seen_pairs = set()
    findings = []
    for i in range(len(all_raises)):
        for j in range(i + 1, len(all_raises)):
            file_a, class_a, template_a, line_a = all_raises[i]
            file_b, class_b, template_b, line_b = all_raises[j]
            if file_a == file_b or class_a == class_b:
                continue
            key = tuple(sorted([(str(file_a), class_a, line_a), (str(file_b), class_b, line_b)]))
            if key in seen_pairs:
                continue
            tokens_a, tokens_b = _topic_tokens(template_a), _topic_tokens(template_b)
            similarity = _jaccard(tokens_a, tokens_b)
            if similarity <= 0:
                continue
            seen_pairs.add(key)
            findings.append(
                Finding(
                    category="naming-drift",
                    description=(
                        f"{class_a!r} and {class_b!r} raised with topically similar messages "
                        "-- possible one error class, two names/wordings"
                    ),
                    confidence=round(similarity, 2),
                    sites=[
                        (str(file_a), line_a, f"raise {class_a}({template_a!r})"),
                        (str(file_b), line_b, f"raise {class_b}({template_b!r})"),
                    ],
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Detector 3: string-literal sets with asymmetric membership
# ---------------------------------------------------------------------------


def detect_enum_asymmetry(facts_by_file):
    groups = []  # (file, scope_name, set(literals), {literal: lineno})
    for facts in facts_by_file:
        for scope_name, entries in facts.literal_groups.items():
            literals = {lit for lit, _ in entries}
            if len(literals) < 2:
                continue
            lineno_by_literal = {}
            for lit, lineno in entries:
                lineno_by_literal.setdefault(lit, lineno)
            groups.append((facts.path, scope_name, literals, lineno_by_literal))

    seen_pairs = set()
    findings = []
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            file_a, scope_a, literals_a, lines_a = groups[i]
            file_b, scope_b, literals_b, lines_b = groups[j]
            if file_a == file_b:
                continue
            intersection = literals_a & literals_b
            if not intersection:
                continue
            sym_diff = literals_a ^ literals_b
            if not sym_diff:
                continue  # identical vocabularies -- no drift to report
            key = tuple(sorted([(str(file_a), scope_a), (str(file_b), scope_b)]))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            confidence = len(intersection) / min(len(literals_a), len(literals_b))
            only_a = sorted(literals_a - literals_b)
            only_b = sorted(literals_b - literals_a)
            sites = [
                (str(file_a), lines_a[lit], f"{scope_a}: {lit!r} not known to {scope_b}")
                for lit in only_a
            ] + [
                (str(file_b), lines_b[lit], f"{scope_b}: {lit!r} not known to {scope_a}")
                for lit in only_b
            ]
            findings.append(
                Finding(
                    category="enum-asymmetry",
                    description=(
                        f"{scope_a!r} ({file_a.name}) and {scope_b!r} ({file_b.name}) share "
                        f"{sorted(intersection)} but disagree on {only_a or only_b}"
                    ),
                    confidence=round(confidence, 2),
                    sites=sites,
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Top-level scan
# ---------------------------------------------------------------------------


def scan_repo(root, top=20, include_tests=False):
    facts_by_file = []
    for path in iter_python_files(root, include_tests=include_tests):
        facts = collect_file_facts(path)
        if facts is not None:
            facts_by_file.append(facts)

    findings = []
    findings += detect_constant_divergence(facts_by_file)
    findings += detect_naming_drift_constants(facts_by_file)
    findings += detect_naming_drift_errors(facts_by_file)
    findings += detect_enum_asymmetry(facts_by_file)

    findings.sort(key=lambda f: f.confidence, reverse=True)
    total = len(findings)
    capped = findings[:top]
    suppressed = total - len(capped)
    return {"findings": capped, "total_before_cap": total, "suppressed": suppressed}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", default=".", help="repo or directory to scan")
    parser.add_argument("--top", type=int, default=20, help="max findings to print (default: 20)")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument(
        "--include-tests", action="store_true",
        help="also scan test_*.py / *_test.py files (noisier, see module docstring)",
    )
    args = parser.parse_args(argv)

    result = scan_repo(args.path, top=args.top, include_tests=args.include_tests)

    if args.json:
        payload = {
            "total_before_cap": result["total_before_cap"],
            "suppressed": result["suppressed"],
            "findings": [
                {
                    "category": f.category,
                    "description": f.description,
                    "confidence": f.confidence,
                    "sites": [{"file": s[0], "line": s[1], "label": s[2]} for s in f.sites],
                }
                for f in result["findings"]
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not result["findings"]:
        print("x10-consistency-scan: no findings")
        return 0

    print(f"x10-consistency-scan: {result['total_before_cap']} finding(s), showing top {len(result['findings'])}")
    for finding in result["findings"]:
        print(finding.format())
    if result["suppressed"]:
        print(f"... {result['suppressed']} more finding(s) suppressed below the top-{args.top} cutoff")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
