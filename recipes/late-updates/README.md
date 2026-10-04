# Keep an old update from replacing newer data

[Recipe home](../../README.md) · [Local setup](../../docs/local-development.md)

Order O1 is already at version 3. A delayed version 2 arrives, then version 4 deletes the order. Replaying version 3 must not bring it back.

## Run it

After the repository quickstart, run this command from the repository root:

```sh
python scripts/run_recipe.py late-updates
```

You should see `stored_version: 4`, `stored_operation: "D"` and `active_rows: 0`.

## Read the fix

Open [setup.sql](setup.sql) for the fictional input and [solution.sql](solution.sql)
for the correction. The source version decides which change wins. The update only applies a higher version. A deletion marker stays in state, while the serving query selects rows whose operation is U.

## Use it carefully

The source version must be reliable. This SQL assumes one change per key in a batch; equal-version conflicts need a defined rejection policy. The larger Spark example exercises that policy.

The SQL is tested in DuckDB 1.5.6 on Python 3.12. Read the
[platform adaptation guide](../../platforms/README.md) before changing the dialect
or running it against cloud data.

Next: [Diagnose a join that multiplies rows](../join-fanout/README.md).
