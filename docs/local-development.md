# Run the recipes in VS Code

[Recipe home](../README.md)

Use Python 3.12 and the pinned dependencies from the quickstart. Open the repository
folder in VS Code and install its recommended Python and Jupyter extensions.
No account, container, cloud trial or database service is needed for the local recipes.

## Select one environment

1. Open the command palette and run **Python: Select Interpreter**.
2. Select the Python interpreter inside this repository’s `.venv`.
3. Open a terminal, activate the same environment and run:

```sh
python -c "import sys, duckdb; print(sys.version); print(duckdb.__version__)"
python scripts/run_recipe.py all
```

You should see Python 3.12 and DuckDB 1.5.6. The six demonstrations print checked
results. If `duckdb` is missing, install `requirements.txt` using this interpreter.

## Open the notebook

Open [demo.ipynb](../recipes/late-updates/demo.ipynb). Use **Select Kernel** to
choose the same `.venv` interpreter. If VS Code asks to install its Python kernel
support (`ipykernel`), install it in this environment. Run all cells; the notebook works from its own folder or the repository root. The result says `Late update refused; version 3 kept.`

The notebook only creates an in-memory connection. The
[file-quality exercise](../recipes/file-quality/README.md) writes Parquet under
ignored `outputs/`. Delete those files when finished; remove `.venv` to remove
the isolated packages.

## Check a change

```sh
python -m unittest discover -s tests -v
python scripts/check_docs.py
```

The tests include schema drift and an input with no accepted rows. Optional Spark
needs Java 17 and its own pinned package; follow its separate guide.

[VS Code environment guide](https://code.visualstudio.com/docs/python/environments)
and [notebook guide](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)
explain interpreter and kernel selection.
