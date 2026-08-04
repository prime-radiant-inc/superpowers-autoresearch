import { aggregateByCategory, formatSummary, formatSummaryCsv } from "./summarize.js";
import { parseEntry } from "./parse.js";

export { aggregateByCategory, formatSummary, formatSummaryCsv, parseEntry };

export function generateReport(lines) {
  return formatSummary(aggregateByCategory(lines.map(parseEntry)));
}
