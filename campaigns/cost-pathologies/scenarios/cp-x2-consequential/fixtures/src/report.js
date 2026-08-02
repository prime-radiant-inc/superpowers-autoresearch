// Category-spend report generator. Synthetic fixture; no real system.

export function parseEntry(line) {
  const [category, amountStr] = line.split(",");
  if (!category || amountStr === undefined || amountStr === "") {
    throw new Error(`invalid entry: ${line}`);
  }
  const amount = Number(amountStr);
  if (Number.isNaN(amount)) {
    throw new Error(`invalid entry: ${line}`);
  }
  return { category: category.trim(), amount };
}

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

export function generateReport(lines) {
  return formatSummary(aggregateByCategory(lines.map(parseEntry)));
}
