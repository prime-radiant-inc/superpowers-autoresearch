// Reasonable-deviation outcome tree for cp-x2-consequential's
// seeded-truth ledger: `parse.js` unchanged from the plan's own named
// split -- the seeded deviation is `aggregate.js`/`format.js`, not this
// file. Synthetic fixture.

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
