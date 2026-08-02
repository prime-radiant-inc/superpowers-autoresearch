export function unique(arr) {
  const seen = new Set();
  const out = [];
  for (const x of arr) {
    if (!seen.has(x)) {
      out.push(x);
      // BUG: missing seen.add(x) here, so duplicates never get filtered
    }
  }
  return out;
}
