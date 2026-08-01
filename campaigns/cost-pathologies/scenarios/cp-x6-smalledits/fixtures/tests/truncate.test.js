import test from "node:test";
import assert from "node:assert/strict";
import { truncate } from "../util/truncate.js";

test("truncates to exactly n characters plus an ellipsis", () => {
  assert.equal(truncate("hello world", 5), "hello...");
});
