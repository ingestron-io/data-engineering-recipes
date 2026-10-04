"""Run synthetic recipes locally; never connect to a cloud account."""

import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RECIPES = (
    "retry-batch",
    "late-updates",
    "join-fanout",
    "quarantine",
    "file-quality",
    "release-check",
)


def sql(db, key, filename):
    return db.execute((ROOT / "recipes" / key / filename).read_text())


def load_module(key, filename):
    spec = importlib.util.spec_from_file_location(
        key, ROOT / "recipes" / key / filename
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(key):
    if key == "file-quality":
        with tempfile.TemporaryDirectory() as directory:
            return load_module(key, "check_files.py").check(
                ROOT / "recipes/file-quality/orders.csv",
                Path(directory) / "accepted.parquet",
            )
    if key == "release-check":
        module = load_module(key, "evidence.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "query.sql"
            path.write_text("SELECT 1;\n")
            approved = module.manifest(directory)
            module.verify(directory, approved)
            path.write_text("SELECT 2;\n")
            try:
                module.verify(directory, approved)
            except ValueError as error:
                return {"unchanged_release": "passed", "changed_release": str(error)}
            raise AssertionError("Changed release was accepted")
    with duckdb.connect(":memory:") as db:
        sql(db, key, "setup.sql")
        if key == "join-fanout":
            before = db.execute(
                "SELECT SUM(amount_cents) FROM orders JOIN customers USING(customer_id)"
            ).fetchone()[0]
            statements = (
                (ROOT / "recipes" / key / "solution.sql").read_text().split(";")
            )
            duplicate_keys = db.execute(statements[0]).fetchall()
            after = db.execute(statements[1]).fetchone()[0]
            assert (before, after) == (6000, 3000)
            return {
                "naive_total_cents": before,
                "reviewed_total_cents": after,
                "duplicate_customer_keys": duplicate_keys,
            }
        sql(db, key, "solution.sql")
        if key == "retry-batch":
            first = db.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
            sql(db, key, "solution.sql")
            replay = db.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
            assert first == replay
            rows, total = db.execute(
                "SELECT COUNT(*), SUM(amount_cents) FROM orders"
            ).fetchone()
            return {
                "rows": rows,
                "total_cents": total,
                "replay_matches": first == replay,
            }
        if key == "late-updates":
            for version, operation, amount in [
                (2, "U", 1000),
                (4, "D", None),
                (3, "U", 2500),
            ]:
                db.execute("DELETE FROM changes")
                db.execute(
                    "INSERT INTO changes VALUES ('O1', ?, ?, ?)",
                    [version, operation, amount],
                )
                sql(db, key, "solution.sql")
                if version == 2:
                    assert (
                        db.execute(
                            "SELECT source_version FROM current_orders"
                        ).fetchone()[0]
                        == 3
                    )
            version, operation = db.execute(
                "SELECT source_version, op FROM current_orders"
            ).fetchone()
            assert (version, operation) == (4, "D")
            active = db.execute(
                "SELECT COUNT(*) FROM current_orders WHERE op='U'"
            ).fetchone()[0]
            return {
                "stored_version": version,
                "stored_operation": operation,
                "active_rows": active,
            }
        accepted = db.execute("SELECT COUNT(*) FROM accepted").fetchone()[0]
        reasons = db.execute(
            "SELECT failed_rule, COUNT(*) FROM rejected GROUP BY failed_rule ORDER BY failed_rule"
        ).fetchall()
        incoming = db.execute("SELECT COUNT(*) FROM incoming").fetchone()[0]
        rejected = sum(count for _, count in reasons)
        assert accepted + rejected == incoming
        return {
            "incoming": incoming,
            "accepted": accepted,
            "rejected": rejected,
            "reasons": reasons,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", choices=(*RECIPES, "all"))
    args = parser.parse_args()
    selected = RECIPES if args.recipe == "all" else (args.recipe,)
    print(json.dumps({key: run(key) for key in selected}, indent=2))


if __name__ == "__main__":
    main()
