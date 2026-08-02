import test from "node:test";
import assert from "node:assert/strict";
import {
  parseEntry,
  aggregateByCategory,
  formatSummary,
  formatSummaryCsv,
  generateReport,
} from "../src/reports/index.js";

test("parseEntry parses a well-formed line", () => {
  const entry = parseEntry("travel,120");
  assert.equal(entry.category, "travel");
  assert.equal(entry.amount, 120);
});

test("parseEntry rejects a malformed line", () => {
  assert.throws(() => parseEntry("travel,"), /invalid entry/);
});

test("aggregateByCategory sums amounts per category", () => {
  const totals = aggregateByCategory([
    { category: "travel", amount: 100 },
    { category: "meals", amount: 20 },
    { category: "travel", amount: 50 },
  ]);
  assert.deepEqual(totals, { travel: 150, meals: 20 });
});

test("formatSummary renders categories sorted alphabetically", () => {
  const text = formatSummary({ travel: 150, meals: 20 });
  assert.equal(text, "meals: 20\ntravel: 150");
});

test("generateReport parses, aggregates, and formats end to end", () => {
  const text = generateReport(["travel,100", "meals,20", "travel,50"]);
  assert.equal(text, "meals: 20\ntravel: 150");
});

test("formatSummaryCsv renders a header and one row per category", () => {
  const csv = formatSummaryCsv({ travel: 150, meals: 20 });
  assert.equal(csv, "category,amount\nmeals,20\ntravel,150");
});
