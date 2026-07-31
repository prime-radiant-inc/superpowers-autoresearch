#!/usr/bin/env bash
set -euo pipefail
# Deliberately blank (no cloned template-repo content): the story frames
# this as a brand-new project, and the shipped brainstorming router
# classifies "new project" as architectural (see the pre-registration
# entry's Amendment/anomaly note). create_base_repo would instead clone
# the shared fixtures/template-repo (src/index.js, src/utils.js,
# package.json -- an existing small JS project), which the smoke rep
# showed makes the agent correctly classify the request as BOUNDED
# (a feature added to existing code) rather than ARCHITECTURAL --
# undermining the very thing this scenario is pre-registered to check.
cd "$QUORUM_WORKDIR"
git init -qb main
git config user.email "drill@test.local"
git config user.name "Drill Test"
git commit -q --allow-empty -m "initial commit (blank -- new project)"
