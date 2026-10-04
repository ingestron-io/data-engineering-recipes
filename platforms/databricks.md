# Adapt retries and quality checks to Databricks

[Platform home](README.md) · [Selected references](https://github.com/ingestron-io/awesome-data-engineering-practice/blob/main/resources/databricks.md)

Start with the [late-update recipe](../recipes/late-updates/README.md). Decide which
source version wins and how a deletion remains visible to replay logic.

## Change the implementation deliberately

1. Use a Delta table and native MERGE syntax rather than DuckDB ON CONFLICT.
2. Check [MERGE duplicate-match rules](https://learn.microsoft.com/en-us/azure/databricks/delta/merge)
   for the exact runtime. Decide what happens when two source rows match one key.
3. Select the failed-row behaviour from [pipeline expectations](https://learn.microsoft.com/en-us/azure/databricks/ldp/expectations).
   Agree whether the pipeline retains, drops or stops on those rows.
4. Test table access with the actual reader identity. Use the
   [masking probe](../recipes/masking/README.md) for a disposable synthetic table.

## Review the release

Keep transformation code and job configuration in a bundle. Current documentation
calls these Declarative Automation Bundles; older examples say Asset Bundles.
In an existing bundle project with authenticated CLI access and a configured
`dev` target, the documented validation command is:

```sh
databricks bundle validate -t dev
```

Validation checks the bundle configuration. Run separate data tests before a
native deployment. This guide does not deploy or run a cloud job.
The [bundle workflow reference](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/work-tasks)
explains targets and the remaining native steps.
