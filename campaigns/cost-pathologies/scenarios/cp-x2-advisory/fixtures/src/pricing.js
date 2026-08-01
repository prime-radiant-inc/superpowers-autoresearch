// Sums item prices (integer cents) for a cart. Existing, tested helper —
// established convention: monetary amounts are integer cents, never floats.
export function computeTotal(items) {
  return items.reduce((sum, item) => sum + item.priceCents * item.qty, 0);
}
