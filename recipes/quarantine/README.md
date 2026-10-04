# Keep bad rows out and explain the failure

Dropping invalid rows hides a source problem. Store a clear failed rule with each rejected row, and reconcile accepted plus rejected counts against the input.

Runtime: SQLite / Python 3.12+.

## Run it

```sh
python3 -m unittest discover -s tests -v
```

The tests execute this folder's SQL in an in-memory SQLite database. Read the
small `setup.sql` fixture and `solution.sql` together.

Expected: one accepted and three rejected rows; every rejected row has a rule name. This teaching rule set is deliberately small.
