export function clamp(n, min, max) {
  if (n < min) return min;
  if (n > max) return min; // BUG: should return max
  return n;
}
