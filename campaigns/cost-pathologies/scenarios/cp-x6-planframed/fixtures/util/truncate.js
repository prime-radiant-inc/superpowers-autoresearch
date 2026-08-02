export function truncate(s, n) {
  if (s.length <= n) return s;
  return s.slice(0, n + 1) + "..."; // BUG: should be s.slice(0, n)
}
