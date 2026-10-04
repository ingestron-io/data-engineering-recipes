# Keep a late update from overwriting newer data

Arrival time is not source order. A version-2 update can arrive after version 3. Compare source versions and retain deletion markers, so replay cannot bring a deleted order back.

Runtime: SQLite 3.35+ / Python 3.12+.

## Run it

```sh
python3 -m unittest discover -s tests -v
```

The tests execute this folder's SQL in an in-memory SQLite database. Read the
small `setup.sql` fixture and `solution.sql` together.

Expected: version 3 and 2500 cents survive a late version-2 update. A version-4 delete remains deleted after replaying version 3. Equal-version conflicting payloads require quarantine upstream; this upsert does not detect them.
