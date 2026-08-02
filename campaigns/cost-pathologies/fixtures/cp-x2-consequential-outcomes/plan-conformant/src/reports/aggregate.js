// Plan-conformant outcome tree for cp-x2-consequential's seeded-truth
// ledger: exactly the plan's named four-file split. Synthetic fixture.

export function aggregateByCategory(entries) {
  const totals = {};
  for (const { category, amount } of entries) {
    totals[category] = (totals[category] || 0) + amount;
  }
  return totals;
}
