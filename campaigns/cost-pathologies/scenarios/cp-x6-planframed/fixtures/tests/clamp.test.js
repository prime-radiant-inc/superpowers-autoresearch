import test from "node:test";
import assert from "node:assert/strict";
import { clamp } from "../util/clamp.js";

test("clamp caps values above max at max", () => {
  assert.equal(clamp(15, 0, 10), 10);
});
