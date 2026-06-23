#!/usr/bin/env python3
"""Build /tmp/sp-var-<name> plugin roots for named bootstrap variants.

Each root is a minimal copy of the superpowers plugin (the dirs --plugin-dir
needs) with `skills/using-superpowers/SKILL.md` swapped for the variant file in
`variants/bootstrap/<name>.md`. These roots are what quorum-matrix.sh points
SUPERPOWERS_ROOT at, so an eval run injects the variant bootstrap.

Reuses build_scratch_root/swap_skill from compression-loop.py so the root layout
can't drift from the -p screen's.

Usage: python3 harnesses/build-variant-roots.py k-digraph-only l-no-access ...
       (no args -> builds the default Q-variant ablation set)
"""
import importlib.util
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AR_ROOT = os.path.dirname(HERE)
REPO_PARENT = os.path.dirname(AR_ROOT)
SUPERPOWERS_REPO = os.path.join(REPO_PARENT, "superpowers")
VARIANTS_DIR = os.path.join(AR_ROOT, "variants", "bootstrap")

DEFAULT = ["k-digraph-only", "l-no-access", "m-no-subagent-stop", "o-lean-description"]

# Per-harness plugin manifests beyond build_scratch_root's claude set. Needed so a
# variant root works for codex/gemini/kimi/cursor/pi/opencode, not just claude
# --plugin-dir. Each harness's provisioner stages SUPERPOWERS_ROOT and reads its own
# manifest + the (swapped) skills/using-superpowers/SKILL.md.
EXTRA_MANIFESTS = [
    ".codex-plugin",
    ".cursor-plugin",
    ".kimi-plugin",
    ".pi",
    ".opencode",
    "gemini-extension.json",
    "GEMINI.md",
    "AGENTS.md",
    "CLAUDE.md",
]


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


loop = _load("loop", os.path.join(HERE, "compression-loop.py"))


def add_cross_harness_manifests(root):
    """Copy the non-claude harness manifests build_scratch_root omits, so the root
    provisions on codex/gemini/kimi/etc. too (idempotent)."""
    for item in EXTRA_MANIFESTS:
        src = os.path.join(SUPERPOWERS_REPO, item)
        dst = os.path.join(root, item)
        if not os.path.exists(src) or os.path.exists(dst):
            continue
        if os.path.isdir(src):
            shutil.copytree(src, dst, symlinks=True)
        else:
            shutil.copy2(src, dst)


def main(names):
    for name in names:
        skill_md = os.path.join(VARIANTS_DIR, f"{name}.md")
        if not os.path.isfile(skill_md):
            print(f"SKIP {name}: no variant file {skill_md}")
            continue
        root = f"/tmp/sp-var-{name}"
        loop.build_scratch_root(root)
        loop.swap_skill(root, skill_md)
        add_cross_harness_manifests(root)
        print(f"built {root}  <- {os.path.basename(skill_md)}  (+cross-harness manifests)")


if __name__ == "__main__":
    main(sys.argv[1:] or DEFAULT)
