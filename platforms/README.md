# Find the native equivalent

The runnable SQL examples use SQLite. Adapt semantics deliberately rather than
copying a dialect into a different engine.

| Platform | Start here | Check before release |
| --- | --- | --- |
| ADF | [CI/CD](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery) | Parameterisation, trigger handling, private source reachability and retry boundaries |
| Databricks | [MERGE](https://docs.databricks.com/aws/en/delta/merge) | Duplicate source matches, version ordering, runtime-specific behaviour and tombstones |
| Microsoft Fabric | [Deployment pipelines](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines) | Item support, connection/configuration changes and reader permissions |
| Spark | [SQL guide](https://spark.apache.org/docs/latest/sql-programming-guide.html) | Types, nulls, joins, partitions and checkpoint/state semantics |

Native execution and screenshots are not yet qualified in this repository.
