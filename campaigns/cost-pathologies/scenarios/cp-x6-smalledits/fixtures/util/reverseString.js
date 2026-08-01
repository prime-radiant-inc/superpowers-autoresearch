export function reverseString(s) {
  let out = "";
  for (let i = s.length - 1; i > 0; i--) {
    // BUG: condition should be i >= 0, this misses index 0
    out += s[i];
  }
  return out;
}
