"""Execute the real Spark example and export inspected, local-only evidence."""

import hashlib
import html
import json
import platform
from pathlib import Path
import subprocess

from pyspark.sql import functions as F
from src.order_feed import load_fixture, local_spark, records, resolve, total


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/order-feed"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_json(value):
    return json.dumps(value, indent=2, default=str)


def table(rows, columns):
    heading = "".join("<th>" + html.escape(name) + "</th>" for name in columns)
    body = "".join("<tr>" + "".join("<td>" + html.escape(str(row.get(name, ""))) + "</td>"
                                  for name in columns) + "</tr>" for row in rows)
    return f"<table><thead><tr>{heading}</tr></thead><tbody>{body}</tbody></table>"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    spark = local_spark()
    try:
        initial = load_fixture(spark, ROOT / "fixtures/initial.json")
        changes = load_fixture(spark, ROOT / "fixtures/changes.json")
        retried = initial.unionByName(changes).unionByName(changes)
        good = resolve(retried)
        candidate = resolve(load_fixture(spark, ROOT / "fixtures/orders.json"))
        active = records(good.active)
        current = records(good.current.select("order_id", "version", "operation", "amount"))
        retry = resolve(retried.unionByName(changes))
        assert active == records(retry.active)
        assert str(total(good.active)) == "240.00"
        assert good.rejected.count() == 0 and good.conflicts.count() == 0
        rejected = [r.asDict() for r in candidate.rejected.select("order_id", "version", "amount", "reason")
                    .orderBy("reason", "order_id").collect()]
        naive = retried.agg(F.sum(F.expr("try_cast(amount as decimal(18,2))")).alias("total")).first()["total"]
        assert str(naive) == "600.00" and len(rejected) == 3
        version = subprocess.run(["java", "-version"],capture_output=True,text=True,check=True).stderr.splitlines()[0]
        evidence = {
            "classification": "Actual local Apache Spark run on original synthetic data; not Databricks or Fabric execution",
            "python": platform.python_version(), "spark": spark.version, "java": version,
            "sourceSha256": {name:sha(ROOT/name) for name in ["src/order_feed.py", "src/run_lab.py", "fixtures/orders.json", "fixtures/initial.json", "fixtures/changes.json"]},
            "initialOrderCount": initial.count(), "deliveredRowsWithRetry": retried.count(),
            "naiveAppendTotalNZD": str(naive), "correctActiveTotalNZD": str(total(good.active)),
            "currentStateCount": len(current), "activeOrderCount": len(active),
            "retrySameResult": True, "invalidRowCount": len(rejected),
            "validFeedQualityPassed": True, "feedWithInvalidRowsReleaseReady": False,
            "activeOrders": active, "currentState": current, "rejectedRows": rejected,
            "limits": ["Retained-ledger rebuild, not Delta MERGE", "No atomic persistence/checkpoint or concurrent writer qualification",
                       "Source versions must be reliable and increase per order", "Delete markers must be retained",
                       "Serving projection removes email; raw access permissions are not enforced by this code",
                       "Local runtime only; native platform tests and captures remain pending"],
        }
        (OUT / "run-record.json").write_text(as_json(evidence)+"\n")
        (OUT / "active-orders.json").write_text(as_json(active)+"\n")
        source = (ROOT / "src/order_feed.py").read_text()
        excerpt = source[source.index("    conflict_keys ="):source.index("    return Result")]
        (OUT / "tested-code-excerpt.py").write_text(excerpt)
        (OUT / "source-excerpt-record.json").write_text(as_json({"source":"src/order_feed.py", "sourceSha256":sha(ROOT/"src/order_feed.py"), "excerptSha256":sha(OUT/"tested-code-excerpt.py")})+"\n")
        report = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Order feed Spark results</title>
<style>body{{font:18px/1.5 system-ui;margin:0;background:#f4f7fa;color:#172c40}}main{{max-width:1120px;margin:40px auto;padding:32px;background:white;border-radius:16px}}h1{{font-size:40px;line-height:1.15}}h2{{margin-top:36px}}.note{{background:#eaf1f7;padding:18px;border-radius:8px}}.metrics{{display:flex;gap:24px}}.metric{{flex:1;padding:20px;background:#edf5f1;border-radius:10px}}strong{{display:block;font-size:36px}}table{{width:100%;border-collapse:collapse;font-size:17px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #dce4eb}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#172c40;color:#e8f0f6;padding:24px;border-radius:10px;font-size:16px}}footer{{margin-top:32px;color:#425b70}}@media(max-width:700px){{main{{margin:0;padding:20px}}.metrics{{display:block}}.metric{{margin-bottom:12px}}}}</style>
<main><p>DATA ENGINEERING FIELD LAB · ACTUAL LOCAL RESULTS</p><h1>A retried order feed: NZD 600 becomes NZD 240</h1>
<p class="note">Apache Spark {html.escape(spark.version)} · Python {html.escape(platform.python_version())} · Original synthetic order data.<br>This is a local execution report, not a Databricks, ADF or Fabric screen.</p>
<div class="metrics"><div class="metric">Naive append total<strong>NZD {naive}</strong>Updates and retries are counted as extra orders.</div><div class="metric">Current active orders<strong>NZD {total(good.active)}</strong>Source versions and deletion markers select the intended state.</div></div>
<h2>Three active orders after the fix</h2>{table(active,["order_id","version","amount","currency"])}
<h2>Keep the deleted order in current state</h2><p>O-1002 remains as a deletion marker. An older replay cannot bring it back.</p>{table(current,["order_id","version","operation","amount"])}
<h2>Invalid records block release</h2><p>The valid feed passes. Adding these three invalid records keeps them visible for review and prevents calling the complete feed release-ready.</p>{table(rejected,["order_id","version","amount","reason"])}
<h2>The code that chooses current state</h2><pre>{html.escape(excerpt)}</pre>
<footer>Replay leaves the same active rows. Email is excluded from the serving projection. Atomic commits, roles, native MERGE and concurrent writers require separate platform tests.</footer></main></html>'''
        (OUT / "report.html").write_text(report)
        print(f"Spark {spark.version}: naive NZD {naive}; current NZD {total(good.active)}; 3 active orders; repeat matches; 3 invalid rows block release.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
