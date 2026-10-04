# Check a CSV before writing Parquet

[Recipe home](../../README.md) · [Local setup](../../docs/local-development.md)

The file looks fine until one amount says `not-a-number`. Read the fields as text,
classify invalid values, then write and check the accepted Parquet rows.

## Run it

From the repository root after the quickstart:

```sh
python recipes/file-quality/check_files.py --output outputs/accepted.parquet
```

You should see six incoming rows, two accepted rows, four rejected rows and an
accepted total of 3000 cents. Rejections include an invalid amount, a missing key
and an unsupported currency. The output file contains only O1 and O2.

## Inspect the output

```sh
python - <<'PYTHON'
import duckdb
print(duckdb.sql("SELECT * FROM 'outputs/accepted.parquet' ORDER BY order_id").fetchall())
PYTHON
```

Expected: `[('O1', 1000, 'NZD'), ('O2', 2000, 'NZD')]`.

Read [check_files.py](check_files.py) and [orders.csv](orders.csv). The script
rejects a changed header before writing output. TRY_CAST gives an invalid amount
a failure reason instead of silently treating it as valid. It reads the written
Parquet back and checks that accepted and rejected counts reconcile.

## Know the boundary

The script reports failure counts; it does not retain rejected raw rows. It
assumes small, well-formed CSV input and does not enforce key uniqueness. A real
landing workflow also needs retained input, rejection details and repeatable
publication. Re-running this exercise replaces the specified output file.
Remove `outputs/accepted.parquet` when finished.

Tested locally with DuckDB 1.5.6 and Python 3.12. See the
[DuckDB CSV reference](https://duckdb.org/docs/current/data/csv/overview.html)
and [Parquet reference](https://duckdb.org/docs/current/data/parquet/overview.html).
