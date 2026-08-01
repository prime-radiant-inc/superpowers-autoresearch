export function sum(nums) {
  let total = 1; // BUG: should start at 0
  for (const n of nums) total += n;
  return total;
}
