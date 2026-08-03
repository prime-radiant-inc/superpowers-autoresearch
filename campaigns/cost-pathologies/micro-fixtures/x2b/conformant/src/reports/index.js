import { aggregateByCategory } from "./aggregate.js";
import { formatSummary, formatSummaryCsv } from "./format.js";
import { parseEntry } from "./parse.js";

export { aggregateByCategory, formatSummary, formatSummaryCsv, parseEntry };

export function generateReport(lines) {
  return formatSummary(aggregateByCategory(lines.map(parseEntry)));
}
