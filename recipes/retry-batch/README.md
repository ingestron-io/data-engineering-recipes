# Retry a batch without doubling the total

[Recipe home](../../README.md) · [Local setup](../../docs/local-development.md)

The same two orders arrive twice after a timeout. Appending the second batch would double sales.

## Run it

After the repository quickstart, run this command from the repository root:

```sh
python scripts/run_recipe.py retry-batch
```

You should see two orders, a total of 3000 cents and `replay_matches: true`.

## Read the fix

Open [setup.sql](setup.sql) for the fictional input and [solution.sql](solution.sql)
for the correction. Use `order_id` as the business key. The upsert updates an existing order instead of adding another row. The runner compares the complete first and replayed result.

## Use it carefully

This example assumes one row per key in each batch and no out-of-order changes. It does not commit a source cursor or coordinate concurrent writers. A production load needs those decisions too.

The SQL is tested in DuckDB 1.5.6 on Python 3.12. Read the
[platform adaptation guide](../../platforms/README.md) before changing the dialect
or running it against cloud data.

Next: [Late updates and deletes](../late-updates/README.md).
