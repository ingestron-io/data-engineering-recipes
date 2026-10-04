# Make an incremental ADF copy recoverable

[Platform home](README.md) · [Selected references](https://github.com/ingestron-io/awesome-data-engineering-practice/blob/main/resources/adf.md)

A successful copy followed by a failed cursor update can replay the same rows.
A cursor advanced before a failed write can lose them. Define recovery for both cases.

## Agree the source behaviour

Confirm the key, update position, deletes and network route. Choose between the
[incremental-copy approaches](https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-overview).
A timestamp on surviving rows is not a delete feed. Check integration-runtime
reachability before designing the rest of the flow.

## Review the copy

Use the [watermark tutorial](https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-portal)
to inspect the lookup, bounded copy and cursor-update steps. Define which successful
sink result permits cursor advancement. Test a retry and a failure between those steps.
The [local retry recipe](../recipes/retry-batch/README.md) teaches the sink rule;
it is not an ADF pipeline export.

## Prepare the release

Microsoft’s [automated publishing guide](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery-improvements)
describes the utilities package for factory validation and template export.
Review exported changes, environment parameters and trigger handling using the
[ADF CI/CD guide](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery).

Keep a factory validation result separate from a real copy run. Native connectivity,
permissions, row counts and recovery remain unverified until run in an authorised
ADF environment. The local exercises activate no Azure resource.
