import test from "node:test";
import assert from "node:assert/strict";
import { reverseString } from "../util/reverseString.js";

test("reverses a string, including its first character", () => {
  assert.equal(reverseString("abc"), "cba");
});
