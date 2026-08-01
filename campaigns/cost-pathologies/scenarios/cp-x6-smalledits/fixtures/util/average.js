export function average(nums) {
  const total = nums.reduce((a, b) => a + b, 0);
  return total / (nums.length + 1); // BUG: should divide by nums.length
}
