// Formats an integer-cents amount as a display string, e.g. 1234 -> "$12.34".
export function formatPrice(amountCents) {
  const dollars = Math.floor(Math.abs(amountCents) / 100);
  const cents = Math.abs(amountCents) % 100;
  const sign = amountCents < 0 ? "-" : "";
  return `${sign}$${dollars}.${String(cents).padStart(2, "0")}`;
}
