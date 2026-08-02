// Plan-conformant outcome tree for cp-x2-consequential's seeded-truth
// ledger: exactly the plan's named four-file split. Synthetic fixture.

export function formatSummary(totals) {
  return Object.entries(totals)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([category, amount]) => `${category}: ${amount}`)
    .join("\n");
}

export function formatSummaryCsv(totals) {
  const rows = Object.entries(totals)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([category, amount]) => `${category},${amount}`);
  return ["category,amount", ...rows].join("\n");
}
