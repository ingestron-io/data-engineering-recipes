CREATE TABLE incoming(row_id INTEGER PRIMARY KEY, order_id TEXT, amount_cents INTEGER, currency TEXT);
INSERT INTO incoming VALUES (1,'O1',1000,'NZD'),(2,NULL,1000,'NZD'),(3,'O3',-1,'NZD'),(4,'O4',1000,'USD');
