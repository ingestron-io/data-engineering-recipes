# Test masking from the reader account

A masked preview in an administrator session does not prove a reader can safely query the table. Run the same checks with the actual reader identity, including a deliberate write attempt. This guide includes an executable identity-specific probe; it has not been run in a native account.

Runtime: Databricks SQL with Unity Catalog; native execution required.

## Prepare a native test

Use a disposable synthetic Unity Catalog table. An administrator creates an
email mask that returns `[hidden]` for the reader, grants SELECT and withholds
write permissions. Ensure the administrator is exempt from the mask. Use the
[official masking guide](https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/)
for supported runtimes, privileges and limitations; configure the policy separately.

Install `databricks-sql-connector` in an isolated environment using its current
official installation guide. Set `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`,
`DATABRICKS_TOKEN`, `MASKING_TABLE` (catalog.schema.table), `MASKING_MODE` and
`EXPECTED_USER`. Use the real admin credentials, then the real reader credentials:

```sh
python3 recipes/masking/probe.py
```

An empty table, wrong identity or unrelated query error does not pass. The reader
write test uses `DELETE ... WHERE false`: it checks permission without deleting
rows. Run only against a disposable table. Review the negative check against
your runtime; administrator write access is not tested. Credentials never belong
in the repository. Local unit tests exercise probe logic with fakes; they do not
prove native access controls.
