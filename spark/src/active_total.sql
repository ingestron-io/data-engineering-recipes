-- This view comes from the validated, conflict-checked current-state resolver.
-- It is not a booked-revenue calculation or a replacement for those checks.
SELECT currency, COUNT(*) AS active_orders, SUM(amount) AS current_value
FROM active_orders
GROUP BY currency
ORDER BY currency;
