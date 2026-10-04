CREATE TABLE orders(order_id TEXT PRIMARY KEY, amount_cents INTEGER NOT NULL CHECK(amount_cents>=0));
CREATE TABLE batch(order_id TEXT, amount_cents INTEGER);
INSERT INTO batch VALUES ('O1',1000),('O2',2000);
