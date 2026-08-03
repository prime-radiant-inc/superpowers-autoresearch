function sortedEntries(totals) {
  return Object.entries(totals).sort(([a], [b]) => a.localeCompare(b));
}

export function formatSummary(totals) {
  return sortedEntries(totals)
    .map(([category, amount]) => `${category}: ${amount}`)
    .join("\n");
}

export function formatSummaryCsv(totals) {
  return [
    "category,amount",
    ...sortedEntries(totals).map(([category, amount]) => `${category},${amount}`),
  ]
    .join("\n");
}
