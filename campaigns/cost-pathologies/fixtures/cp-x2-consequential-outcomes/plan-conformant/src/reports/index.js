// Plan-conformant outcome tree for cp-x2-consequential's seeded-truth
// ledger: exactly the plan's named four-file split. Synthetic fixture.
//
// Public entry point -- callers only ever import from here.

export { parseEntry } from "./parse.js";
export { aggregateByCategory } from "./aggregate.js";
export { formatSummary, formatSummaryCsv } from "./format.js";

import { parseEntry } from "./parse.js";
import { aggregateByCategory } from "./aggregate.js";
import { formatSummary } from "./format.js";

export function generateReport(lines) {
  return formatSummary(aggregateByCategory(lines.map(parseEntry)));
}
