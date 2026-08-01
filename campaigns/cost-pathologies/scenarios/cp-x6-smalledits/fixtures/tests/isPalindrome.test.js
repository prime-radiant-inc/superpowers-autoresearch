import test from "node:test";
import assert from "node:assert/strict";
import { isPalindrome } from "../util/isPalindrome.js";

test("recognizes a palindrome", () => {
  assert.equal(isPalindrome("level"), true);
});

test("recognizes a non-palindrome", () => {
  assert.equal(isPalindrome("hello"), false);
});
