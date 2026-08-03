function sortedEntries(totals) {
  return Object.entries(totals).sort(([a], [b]) => a.localeCompare(b));
}

export function aggregateByCategory(entries) {
  const totals = {};
  for (const { category, amount } of entries) {
    totals[category] = (totals[category] || 0) + amount;
  }
  return totals;
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
