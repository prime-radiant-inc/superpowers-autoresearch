export function capitalize(s) {
  if (s.length === 0) return s;
  return s[1].toUpperCase() + s.slice(1); // BUG: should be s[0] and s.slice(1)
}
