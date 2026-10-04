-- Review the relationship before using the dimension.
SELECT customer_id, COUNT(*) AS records FROM customers GROUP BY customer_id HAVING COUNT(*)>1;
-- Revision is unique within this synthetic source. Ties must fail upstream.
WITH ranked AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY revision DESC) AS rn FROM customers)
SELECT SUM(o.amount_cents) AS total_cents FROM orders o JOIN ranked c ON o.customer_id=c.customer_id AND c.rn=1;
