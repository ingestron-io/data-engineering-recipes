CREATE VIEW classified AS SELECT *, CASE
 WHEN order_id IS NULL OR trim(order_id)='' THEN 'missing_order_id'
 WHEN amount_cents IS NULL OR amount_cents<0 THEN 'invalid_amount'
 WHEN currency IS NULL OR currency<>'NZD' THEN 'unsupported_currency'
 ELSE NULL END AS failed_rule FROM incoming;
CREATE VIEW accepted AS SELECT * FROM classified WHERE failed_rule IS NULL;
CREATE VIEW rejected AS SELECT * FROM classified WHERE failed_rule IS NOT NULL;
