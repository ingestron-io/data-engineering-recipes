# Review a Fabric notebook and its lakehouse

[Platform home](README.md) · [Selected references](https://github.com/ingestron-io/awesome-data-engineering-practice/blob/main/resources/fabric.md)

A notebook can contain the right transformation and still use the wrong lakehouse.
Treat its code, environment and target bindings as one review.

## Prepare the data check

Run the [local Spark order feed](../spark/README.md) and note its expected totals.
For a native notebook, confirm the Fabric runtime supports the Python/Spark APIs
used. Replace local fixture paths with the authorised lakehouse paths. DuckDB SQL
is not automatically Spark SQL or Fabric warehouse SQL.

## Check the native workflow

1. Inspect Files versus Tables and path handling in the
   [lakehouse loading guide](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-notebook-load-data).
2. Review source, dependencies and lakehouse bindings using the
   [notebook Git/deployment guide](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment).
3. Compare supported items and target rules before choosing deployment pipelines
   or the Microsoft fabric-cicd library. A successful deployment still needs a data check.
4. Test workspace, item and data permissions through the routes your consumers use.

## Inspect with a local CLI

Microsoft’s Fabric CLI uses the `ms-fabric-cli` Python package. In a separate
Python environment, install it using its [upstream instructions](https://github.com/microsoft/fabric-cli).
For an existing authorised tenant, its documented read commands start with:

```sh
fab auth login
fab ls
```

Listing workspaces is an inspection step. No native sign-in, deployment or capacity
is activated by this repository. Keep synthetic local results separate from any
later Fabric run evidence.
