"""Run the SQL extracts against actual local Spark views, then assert the result."""
import hashlib
import json
from pathlib import Path

from src.order_feed import load_fixture, local_spark, resolve

ROOT = Path(__file__).resolve().parents[1]


def main():
    spark = local_spark()
    try:
        initial = load_fixture(spark, ROOT / 'fixtures/initial.json')
        changes = load_fixture(spark, ROOT / 'fixtures/changes.json')
        delivered = initial.unionByName(changes).unionByName(changes)
        delivered.createOrReplaceTempView('delivered_events')
        resolve(delivered).active.createOrReplaceTempView('active_orders')
        duplicates = [row.asDict() for row in spark.sql(
            (ROOT / 'src/retry_diagnostic.sql').read_text()).collect()]
        totals = [row.asDict() for row in spark.sql(
            (ROOT / 'src/active_total.sql').read_text()).collect()]
        assert [(row['order_id'], row['deliveries']) for row in duplicates] == [
            ('O-1001', 2), ('O-1002', 2), ('O-1004', 2)]
        assert len(totals) == 1
        assert totals[0]['currency'] == 'NZD'
        assert totals[0]['active_orders'] == 3
        assert str(totals[0]['current_value']) == '240.00'
        record = {'classification': 'Actual local Spark SQL on original synthetic data',
                  'spark': spark.version, 'repeatedDeliveries': duplicates,
                  'currentTotals': totals, 'assertionsPassed': True,
                  'sourceSha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                   for name in ['src/run_sql.py', 'src/retry_diagnostic.sql',
                                                'src/active_total.sql', 'src/order_feed.py',
                                                'fixtures/initial.json', 'fixtures/changes.json']}}
        out = ROOT / 'outputs/order-feed'
        out.mkdir(parents=True, exist_ok=True)
        (out / 'sql-run-record.json').write_text(json.dumps(record, indent=2, default=str) + '\n')
        print('Spark SQL passed: three retried changes; three active orders worth NZD 240.00.')
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
