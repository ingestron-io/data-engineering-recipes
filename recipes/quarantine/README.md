# Keep bad rows out and explain the failure

[Recipe home](../../README.md) · [Local setup](../../docs/local-development.md)

A file contains a missing order ID, a negative amount and a currency the model does not support. Silently dropping them hides the problem.

## Run it

After the repository quickstart, run this command from the repository root:

```sh
python scripts/run_recipe.py quarantine
```

You should see four incoming rows, one accepted row and three rejected rows with named reasons.

## Read the fix

Open [setup.sql](setup.sql) for the fictional input and [solution.sql](solution.sql)
for the correction. Classify each row once, then expose accepted and rejected views. Check that both counts add up to the input count.

## Use it carefully

Only the first failed rule is recorded here. This is a bounded teaching example, not durable quarantine storage. Define retention, ownership and a correction/replay process in a real pipeline.

The SQL is tested in DuckDB 1.5.6 on Python 3.12. Read the
[platform adaptation guide](../../platforms/README.md) before changing the dialect
or running it against cloud data.

Next: [Check a CSV and its Parquet output](../file-quality/README.md).
