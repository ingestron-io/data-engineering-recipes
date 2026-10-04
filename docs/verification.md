# Verification — 2026-10-05

Seven local Python tests pass: retry idempotence, late ordering/deletion replay,
join fanout diagnosis, quarantine reconciliation, changed release-file refusal,
masking-probe control logic and actual notebook execution. SQL executes in SQLite;
masking tests use fake connections and prove no native permission policy.

Ten Spark tests pass against the exact source in this repository with Python
3.12, Java 17 and PySpark 4.0.1. Both documented runners also pass. The fictional
retried feed totals NZD 600.00 with naive append and NZD 240.00 after current-state
selection; three active orders remain, replay matches, and three invalid rows
block release. The SQL runner independently checks the current total and repeated
change IDs. Py4J emits socket ResourceWarnings; all assertions pass and the local
Spark contexts stop. Initial verification attempts needed a corrected Java path
and permission for local sockets; the successful execution is separate evidence.

The original retained-ledger rebuild does not implement atomic persistent commits,
concurrent writers or cloud streaming. Removing email from serving output does
not enforce raw-table roles. Native ADF, Databricks and Fabric runs/screenshots
are not claimed. The native masking probe remains pending actual identity tests.

[SQL/Spark run record](spark-sql-run-record.json) and
[Spark run record](spark-run-record.json) bind the published original files by
SHA-256. They contain fictional data and runtime versions, not user paths/tokens.
[Result card](../assets/retry-result.svg) is an illustration of those observed
synthetic results, not a screenshot of a cloud product.
