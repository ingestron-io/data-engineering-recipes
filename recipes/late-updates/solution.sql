-- Keep deletion markers in state; filter them only in the serving view.
INSERT INTO current_orders SELECT * FROM changes WHERE true
ON CONFLICT(order_id) DO UPDATE SET source_version=excluded.source_version,
 op=excluded.op, amount_cents=excluded.amount_cents
WHERE excluded.source_version > current_orders.source_version;
