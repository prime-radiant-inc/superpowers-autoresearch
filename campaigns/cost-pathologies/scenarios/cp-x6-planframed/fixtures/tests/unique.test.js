import test from "node:test";
import assert from "node:assert/strict";
import { unique } from "../util/unique.js";

test("removes duplicate values", () => {
  assert.deepEqual(unique([1, 2, 2, 3, 1]), [1, 2, 3]);
});
