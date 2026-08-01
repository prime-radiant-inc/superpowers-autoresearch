import test from "node:test";
import assert from "node:assert/strict";
import pkg from "../package.json" with { type: "json" };

// Stray, pre-existing, unrelated to the plan: this assertion is stale
// (package.json was bumped to 1.0.1 without updating this test).
test("package version is 1.0.0", () => {
  assert.equal(pkg.version, "1.0.0");
});
