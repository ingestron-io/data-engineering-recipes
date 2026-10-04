# Retry a batch without doubling the total

A job writes its batch, then loses the acknowledgement. The retry must not count the same order twice. Use a stable order key and an upsert; do not append the replay as another sale.

Runtime: SQLite 3.35+ / Python 3.12+.

## Run it

```sh
python3 -m unittest discover -s tests -v
```

The tests execute this folder's SQL in an in-memory SQLite database. Read the
small `setup.sql` fixture and `solution.sql` together.

Expected: two orders totalling 3000 cents after both the first run and the retry. This only covers a stable key, not full CDC ordering.
