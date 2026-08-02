// Reasonable-deviation outcome tree for cp-x2-consequential's
// seeded-truth ledger: same public surface as plan-conformant/, built
// over the combined summarize.js instead of separate aggregate.js/
// format.js files. Synthetic fixture.
//
// Public entry point -- callers only ever import from here.

export { parseEntry } from "./parse.js";
export { aggregateByCategory, formatSummary, formatSummaryCsv } from "./summarize.js";

import { parseEntry } from "./parse.js";
import { aggregateByCategory, formatSummary } from "./summarize.js";

export function generateReport(lines) {
  return formatSummary(aggregateByCategory(lines.map(parseEntry)));
}
