import test from "node:test";
import assert from "node:assert/strict";
import { average } from "../util/average.js";

test("averages a list of numbers", () => {
  assert.equal(average([2, 4, 6]), 4);
});
