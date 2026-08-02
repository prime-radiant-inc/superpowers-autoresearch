export function flattenOnce(arr) {
  const out = [];
  for (const x of arr) {
    if (Array.isArray(x)) {
      out.push(x); // BUG: should be out.push(...x) to flatten one level
    } else {
      out.push(x);
    }
  }
  return out;
}
