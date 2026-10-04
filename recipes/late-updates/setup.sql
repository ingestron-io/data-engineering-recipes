CREATE TABLE current_orders(order_id TEXT PRIMARY KEY, source_version INTEGER NOT NULL, op TEXT NOT NULL CHECK(op IN ('U','D')), amount_cents INTEGER);
CREATE TABLE changes(order_id TEXT, source_version INTEGER, op TEXT, amount_cents INTEGER);
INSERT INTO changes VALUES ('O1',3,'U',2500);
