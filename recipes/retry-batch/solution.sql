-- One stable key per order; a replay replaces the value instead of appending it.
INSERT INTO orders SELECT order_id, amount_cents FROM batch WHERE true
ON CONFLICT(order_id) DO UPDATE SET amount_cents=excluded.amount_cents;
