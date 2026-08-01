export function isPalindrome(s) {
  for (let i = 0; i < s.length / 2; i++) {
    if (s[i] !== s[s.length - i]) return false; // BUG: should be s.length - 1 - i
  }
  return true;
}
