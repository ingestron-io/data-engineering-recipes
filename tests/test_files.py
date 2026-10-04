import importlib.util
from pathlib import Path
import tempfile
import unittest

import duckdb

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "check_files", ROOT / "recipes/file-quality/check_files.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FileQuality(unittest.TestCase):
    def test_parquet_has_only_accepted_rows_and_typed_amounts(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "accepted.parquet"
            result = module.check(ROOT / "recipes/file-quality/orders.csv", output)
            self.assertEqual(
                (result["incoming"], result["accepted"], result["rejected"]), (6, 2, 4)
            )
            with duckdb.connect(":memory:") as db:
                self.assertEqual(
                    db.execute(
                        "SELECT * FROM read_parquet(?) ORDER BY order_id", [str(output)]
                    ).fetchall(),
                    [("O1", 1000, "NZD"), ("O2", 2000, "NZD")],
                )
                self.assertEqual(
                    db.execute(
                        "DESCRIBE SELECT * FROM read_parquet(?)", [str(output)]
                    ).fetchall()[1][1],
                    "BIGINT",
                )

    def test_unexpected_header_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "changed.csv"
            source.write_text("order_id,amount,currency\nO1,100,NZD\n")
            output = Path(directory) / "accepted.parquet"
            with self.assertRaises(ValueError):
                module.check(source, output)
            self.assertFalse(output.exists())

    def test_empty_accepted_set_still_reconciles(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "rejected.csv"
            source.write_text("order_id,amount_cents,currency\nO1,nope,NZD\n")
            result = module.check(source, Path(directory) / "accepted.parquet")
            self.assertEqual(
                (
                    result["accepted"],
                    result["rejected"],
                    result["accepted_total_cents"],
                ),
                (0, 1, 0),
            )
