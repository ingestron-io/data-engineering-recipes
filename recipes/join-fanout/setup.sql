CREATE TABLE orders(order_id TEXT PRIMARY KEY, customer_id TEXT, amount_cents INTEGER);
CREATE TABLE customers(customer_id TEXT, revision INTEGER, region TEXT, PRIMARY KEY(customer_id,revision));
INSERT INTO orders VALUES ('O1','C1',1000),('O2','C1',2000);
INSERT INTO customers VALUES ('C1',1,'Auckland'),('C1',2,'Wellington');
