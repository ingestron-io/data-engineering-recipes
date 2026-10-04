# Find the join that multiplied your sales

[Recipe home](../../README.md) · [Local setup](../../docs/local-development.md)

Two orders belong to C1. The customer table has two revisions for C1. Joining both revisions to both orders doubles the total.

## Run it

After the repository quickstart, run this command from the repository root:

```sh
python scripts/run_recipe.py join-fanout
```

You should see `naive_total_cents: 6000`, `reviewed_total_cents: 3000` and duplicate key C1 with count 2.

## Read the fix

Open [setup.sql](setup.sql) for the fictional input and [solution.sql](solution.sql)
for the correction. Count rows per customer key before joining. The reviewed query chooses the latest customer revision with ROW_NUMBER, then calculates the total.

## Use it carefully

Selecting the latest revision is this example’s business rule. Historical reporting may need the revision valid on the order date. A tied revision also needs a deterministic rule.

The SQL is tested in DuckDB 1.5.6 on Python 3.12. Read the
[platform adaptation guide](../../platforms/README.md) before changing the dialect
or running it against cloud data.

Next: [Account for rejected rows](../quarantine/README.md).
