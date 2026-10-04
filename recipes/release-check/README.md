# Stop a release when its evidence changed

A passing check belongs to specific files. If a notebook changes after testing, the old result must not qualify the new release. Record file hashes and verify them again before delivery.

Runtime: Python 3.12+.

## Try the failure

```sh
python3 -m unittest discover -s tests -v
```

The release test records a file manifest, changes a SQL file, then confirms the
old manifest is refused. Added and removed files also invalidate review. Hashes
bind bytes, not correctness: pair this with meaningful tests, a reviewed PR,
commit SHA, environment-specific checks and a rollback plan. This local example
does not deploy anything or pretend a hash is a security assurance.
