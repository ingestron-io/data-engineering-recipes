# Take a local recipe to your platform

[Recipe home](../README.md)

DuckDB exercises the data rule with small inputs. Before using it in a native
pipeline, check the SQL dialect, source semantics, storage and permissions.

| Platform           | Start with                                  | Verify in the native environment                              |
| ------------------ | ------------------------------------------- | ------------------------------------------------------------- |
| Databricks         | [MERGE and quality checks](databricks.md)   | Duplicate matching, Delta state, job target and reader roles  |
| Microsoft Fabric   | [Notebook and lakehouse release](fabric.md) | Runtime, table paths, target bindings and data permissions    |
| Azure Data Factory | [Incremental copy and recovery](adf.md)     | Connectivity, cursor range, sink retry and release parameters |

These pages are adaptation and review guides. The repository’s execution evidence
covers local DuckDB/Python and its existing local Spark exercise. No native-cloud
run, screenshot or deployment is claimed. Cloud runs need an authorised account
and may consume capacity or compute.
