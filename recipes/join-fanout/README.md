# Find the join that multiplied your sales

Two valid customer records share the same customer ID. Joining sales to both quietly doubles the total. Check the dimension key first; choose a documented record before joining.

Runtime: SQLite / Python 3.12+.

## Run it

```sh
python3 -m unittest discover -s tests -v
```

The tests execute this folder's SQL in an in-memory SQLite database. Read the
small `setup.sql` fixture and `solution.sql` together.

Expected: the unchecked join totals 6000 cents; the reviewed latest-record join totals 3000 cents. Reject tied ordering keys rather than picking an arbitrary record.
