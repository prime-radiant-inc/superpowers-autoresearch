export function aggregateByCategory(entries) {
  const totals = {};
  for (const { category, amount } of entries) {
    totals[category] = (totals[category] || 0) + amount;
  }
  return totals;
}
