# Data engineering recipes

Small examples for the problems that waste a data engineer's afternoon.
Each guide starts with the failure, includes fictional data and shows a check.

## Pick a problem

- [Retry a batch without doubling the total](recipes/retry-batch/README.md) — SQLite 3.35+ / Python 3.12+.
- [Keep a late update from overwriting newer data](recipes/late-updates/README.md) — SQLite 3.35+ / Python 3.12+.
- [Find the join that multiplied your sales](recipes/join-fanout/README.md) — SQLite / Python 3.12+.
- [Keep bad rows out and explain the failure](recipes/quarantine/README.md) — SQLite / Python 3.12+.
- [Test masking from the reader account](recipes/masking/README.md) — Databricks SQL with Unity Catalog; native execution required.
- [Stop a release when its evidence changed](recipes/release-check/README.md) — Python 3.12+.

## Run the local checks

```sh
python3 -m unittest discover -s tests -v
```

No cloud account, database server or subscription is needed for the local tests.
SQLite examples teach the behaviour; their SQL is not presented as Fabric or
Databricks SQL. The masking probe requires your own approved Databricks workspace
and two real test identities. No native permission result is claimed.

## More to use

- [Spark order feed](spark/README.md): versioned changes, retries, tombstones and quarantine.
- [Platform index](platforms/README.md): ADF, Databricks and Fabric starting points.
- [Requirements brief](templates/requirements.md), [architecture review](templates/architecture.md) and [release checklist](templates/release.md).
- [Curated references](https://github.com/ingestron-io/awesome-data-engineering-practice).

Original code, text and synthetic data are MIT licensed. Linked works retain
upstream terms. There are no customer records, benchmark claims or product dependencies.
