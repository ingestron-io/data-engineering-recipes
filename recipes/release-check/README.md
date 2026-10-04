# Stop a release when reviewed files change

[Recipe home](../../README.md) · [Local setup](../../docs/local-development.md)

A query was tested and reviewed. Someone changed the file before release. The
old review no longer describes the files being shipped.

## Run it

From the repository root:

```sh
python scripts/run_recipe.py release-check
```

You should see `unchanged_release: "passed"`. The changed release reports:
`Files changed since review; run checks and approve again`.

## Read the check

[evidence.py](evidence.py) builds a SHA-256 map for the files in a selected folder.
The demonstration records a query, verifies it, changes it and tries verification
again. The tests also reject added and removed files.

## Apply the idea

Keep the checked source revision, test report, deployment target and approver in
a real release record. A local hash comparison does not authenticate who approved
it or prove the tests were trustworthy. Review only the intended release folder;
keep credentials and generated scratch files elsewhere.

The [release template](../../templates/release.md) is a starting point. Use
[platform release tooling](../../platforms/README.md) for the actual deployment.
This example performs no remote action.
