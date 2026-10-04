-- Inspect repeated deliveries before deduplication. Do not call these new orders.
SELECT order_id, version, operation, amount, COUNT(*) AS deliveries
FROM delivered_events
GROUP BY order_id, version, operation, amount
HAVING COUNT(*) > 1
ORDER BY order_id, version;
