import test from "node:test";
import assert from "node:assert/strict";
import { capitalize } from "../util/capitalize.js";

test("capitalizes the first letter", () => {
  assert.equal(capitalize("hello"), "Hello");
});
