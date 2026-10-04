"""Classify a synthetic CSV and reconcile its accepted Parquet output."""

import argparse
import csv
import json
from pathlib import Path

import duckdb

EXPECTED_COLUMNS = ["order_id", "amount_cents", "currency"]


def check(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output:
        raise ValueError("Choose a separate output file")
    with source.open(newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle), None)
    if header != EXPECTED_COLUMNS:
        raise ValueError(f"Expected CSV header {EXPECTED_COLUMNS}; found {header}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(":memory:") as db:
        db.execute(
            "CREATE TABLE incoming AS SELECT * FROM read_csv(?, header=true, all_varchar=true)",
            [str(source)],
        )
        db.execute("""
            CREATE VIEW classified AS
            WITH parsed AS (
                SELECT order_id, TRY_CAST(amount_cents AS BIGINT) AS amount_cents, currency
                FROM incoming
            )
            SELECT *, CASE
                WHEN order_id IS NULL OR trim(order_id)='' THEN 'missing_order_id'
                WHEN amount_cents IS NULL OR amount_cents<0 THEN 'invalid_amount'
                WHEN currency IS NULL OR currency<>'NZD' THEN 'unsupported_currency'
                ELSE NULL END AS failed_rule
            FROM parsed
        """)
        db.execute(
            "COPY (SELECT order_id,amount_cents,currency FROM classified WHERE failed_rule IS NULL) TO ? (FORMAT PARQUET)",
            [str(output)],
        )
        total = db.execute("SELECT COUNT(*) FROM incoming").fetchone()[0]
        accepted, cents = db.execute(
            "SELECT COUNT(*),COALESCE(SUM(amount_cents),0) FROM read_parquet(?)",
            [str(output)],
        ).fetchone()
        reasons = db.execute(
            "SELECT failed_rule,COUNT(*) FROM classified WHERE failed_rule IS NOT NULL GROUP BY failed_rule ORDER BY failed_rule"
        ).fetchall()
        rejected = sum(count for _, count in reasons)
        if accepted + rejected != total:
            raise AssertionError("Input and output counts do not reconcile")
        return {
            "incoming": total,
            "accepted": accepted,
            "rejected": rejected,
            "accepted_total_cents": cents,
            "reasons": reasons,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path(__file__).with_name("orders.csv")
    )
    parser.add_argument("--output", type=Path, default=Path("outputs/accepted.parquet"))
    args = parser.parse_args()
    print(json.dumps(check(args.input, args.output), indent=2))
