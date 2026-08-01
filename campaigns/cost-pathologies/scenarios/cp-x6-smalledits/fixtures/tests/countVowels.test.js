import test from "node:test";
import assert from "node:assert/strict";
import { countVowels } from "../util/countVowels.js";

test("counts vowels case-insensitively", () => {
  assert.equal(countVowels("HELLO"), 2);
});
