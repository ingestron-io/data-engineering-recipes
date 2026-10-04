"""Correctness checks for the reader's Spark example, including failure cases."""

from pathlib import Path
from decimal import Decimal
import unittest

from src.order_feed import FIELDS, SERVING_COLUMNS, frame, load_fixture, local_spark, records, resolve, total


ROOT = Path(__file__).resolve().parents[1]


def event(order="O-1001", version="1", amount="100.00", operation="U", **changes):
    row = dict(order_id=order, version=version, operation=operation, amount=amount,
               currency="NZD", event_time="2026-09-30T09:00:00Z",
               customer_email="reader@example.test")
    row.update(changes)
    return row


class OrderFeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = local_spark()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_identical_retry_keeps_the_same_rows_and_total(self):
        raw = load_fixture(self.spark, ROOT / "fixtures/orders.json")
        first = resolve(raw)
        second = resolve(raw.unionByName(raw))
        self.assertEqual(records(first.active), records(second.active))
        self.assertEqual(total(second.active), Decimal("240.00"))

    def test_arrival_order_cannot_overwrite_a_newer_source_version(self):
        result = resolve(frame(self.spark, [event(version="2", amount="120.00"), event()]))
        self.assertEqual(records(result.active)[0]["amount"], Decimal("120.00"))

    def test_delete_marker_prevents_old_replay_resurrection(self):
        result = resolve(frame(self.spark, [event(version="3", operation="D", amount=None), event()]))
        self.assertEqual(result.active.count(), 0)
        self.assertEqual(records(result.current)[0]["version"], 3)

    def test_explicit_newer_update_can_reactivate_under_agreed_source_rule(self):
        result = resolve(frame(self.spark, [event(version="2", operation="D"), event(version="3")]))
        self.assertEqual(result.active.count(), 1)
        self.assertEqual(records(result.active)[0]["version"], 3)

    def test_conflicting_version_holds_the_whole_order(self):
        result = resolve(frame(self.spark, [event(), event(amount="101.00"), event(version="2")]))
        self.assertEqual(result.conflicts.count(), 2)
        self.assertEqual(result.active.count(), 0)

    def test_bad_records_remain_visible_with_reasons(self):
        bad = [event(order=""), event(version="two"), event(amount="-1.00"),
               event(amount="not-money"), event(currency="USD"), event(event_time="bad-time"),
               event(operation="X"), event(version="2147483648"), event(version="1.5")]
        result = resolve(frame(self.spark, bad))
        self.assertEqual(result.rejected.count(), len(bad))
        self.assertEqual(result.active.count(), 0)
        reasons = {r["reason"] for r in result.rejected.collect()}
        self.assertTrue({"missing_order_id", "invalid_version", "invalid_amount", "invalid_event_time"}.issubset(reasons))

    def test_serving_output_excludes_email_and_other_raw_columns(self):
        result = resolve(frame(self.spark, [event()]))
        self.assertEqual(result.active.columns, SERVING_COLUMNS)
        self.assertNotIn("customer_email", result.active.columns)
        self.assertIn("customer_email", result.accepted.columns)

    def test_schema_drift_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "source fields"):
            frame(self.spark, [event(unreviewed_field="new")])

    def test_empty_feed_has_valid_empty_outputs(self):
        result = resolve(frame(self.spark, []))
        self.assertEqual(result.active.count(), 0)
        self.assertEqual(total(result.active), Decimal("0.00"))

    def test_repartitioning_does_not_change_current_state(self):
        raw = load_fixture(self.spark, ROOT / "fixtures/orders.json")
        self.assertEqual(records(resolve(raw).current), records(resolve(raw.repartition(3)).current))


if __name__ == "__main__":
    unittest.main()
