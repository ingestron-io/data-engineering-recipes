# Replay an order feed safely with Spark

An original synthetic order feed exercises retry, late updates, deletion markers,
conflicting equal versions, invalid rows and a serving output without email.

Use Python 3.12, Java 17 and pinned PySpark 4.0.1 in an isolated environment:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r spark/requirements.txt
cd spark
../.venv/bin/python -m unittest discover -s tests -v
../.venv/bin/python -m src.run_lab
../.venv/bin/python -m src.run_sql
```

Set `JAVA_HOME` to your Java 17 installation and `SPARK_LOCAL_IP=127.0.0.1`.
Results are written under ignored `spark/outputs`. Input fixtures are fictional.
This is a bounded local batch exercise, not a distributed streaming implementation
or a native Databricks/Fabric run. Read the [source](src/order_feed.py) and tests.
