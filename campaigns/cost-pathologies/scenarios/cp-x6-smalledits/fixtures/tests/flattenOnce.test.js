import test from "node:test";
import assert from "node:assert/strict";
import { flattenOnce } from "../util/flattenOnce.js";

test("flattens one level of nested arrays", () => {
  assert.deepEqual(flattenOnce([1, [2, 3], 4]), [1, 2, 3, 4]);
});
