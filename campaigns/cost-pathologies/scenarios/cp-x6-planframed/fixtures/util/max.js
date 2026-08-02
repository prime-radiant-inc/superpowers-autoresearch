export function max(nums) {
  let best = 0; // BUG: should start at -Infinity, breaks on all-negative input
  for (const n of nums) {
    if (n > best) best = n;
  }
  return best;
}
