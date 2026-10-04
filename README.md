# Data engineering recipes

Small, runnable examples for the problems that waste a data engineer’s afternoon.
Use fictional data to reproduce a failure, make a change and check the result.

## Start here

Use Python 3.12. From the repository root, run:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_recipe.py retry-batch
```

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv`
and activate it with `.venv\Scripts\Activate.ps1`.

You should see `rows: 2`, `total_cents: 3000` and `replay_matches: true`.
The SQL runs in an in-memory DuckDB process; there is no database server to set up.

## Pick the problem

| Problem                                   | Guide                                                      | Local result                       |
| ----------------------------------------- | ---------------------------------------------------------- | ---------------------------------- |
| A retried load doubles sales              | [Retry a batch](recipes/retry-batch/README.md)             | Same two rows and 3000 cents       |
| An older update replaces newer data       | [Late updates and deletes](recipes/late-updates/README.md) | Version 4 deletion survives replay |
| A join multiplies the total               | [Join fanout](recipes/join-fanout/README.md)               | 6000 becomes 3000 cents            |
| Bad rows disappear without an explanation | [Reject rows with a reason](recipes/quarantine/README.md)  | All four input rows accounted for  |
| A CSV contains surprising values          | [CSV to checked Parquet](recipes/file-quality/README.md)   | Two accepted rows; four rejected   |
| Files changed after review                | [Check release files](recipes/release-check/README.md)     | Changed release refused            |
| A masked preview looks safe               | [Test the reader account](recipes/masking/README.md)       | Native Databricks test required    |

Run all six local demonstrations with `python scripts/run_recipe.py all`.
For a larger transformation example, try the [Spark order feed](spark/README.md).

## Use these in your own work

- [Work in VS Code](docs/local-development.md): interpreter, notebook kernel and tests.
- [Adapt a recipe to Databricks, Fabric or ADF](platforms/README.md): what must change and what to check.
- [Requirements](templates/requirements.md), [architecture](templates/architecture.md) and [release](templates/release.md) notes.
- [Curated platform references](https://github.com/ingestron-io/awesome-data-engineering-practice).

The examples use Python 3.12 and pinned DuckDB 1.5.6. Spark has separate prerequisites.
Cloud permissions and SQL dialects need native checks; a local pass is not cloud evidence.
[Verification](docs/verification.md) records the exact scope.

## Check a contribution

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/check_docs.py
ruff format --check recipes tests scripts
```

Original code, text and synthetic fixtures are MIT licensed. See
[CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md).
