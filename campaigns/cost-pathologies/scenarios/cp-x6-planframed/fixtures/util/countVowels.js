export function countVowels(s) {
  const vowels = "aeiou"; // BUG: should also match uppercase, e.g. "aeiouAEIOU"
  let count = 0;
  for (const ch of s) {
    if (vowels.includes(ch)) count++;
  }
  return count;
}
