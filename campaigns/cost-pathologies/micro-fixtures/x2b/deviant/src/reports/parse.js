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
