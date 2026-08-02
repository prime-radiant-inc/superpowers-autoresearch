// Reasonable-deviation outcome tree for cp-x2-consequential's
// seeded-truth ledger: combines what the plan named as separate
// `aggregate.js`/`format.js` files into one -- the ledger's "arguably
// suboptimal" split (two sub-10-line functions, always called together,
// with exactly one caller and no independent test surface) collapsed
// into a single concern. Synthetic fixture.

export function aggregateByCategory(entries) {
  const totals = {};
  for (const { category, amount } of entries) {
    totals[category] = (totals[category] || 0) + amount;
  }
  return totals;
}

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
