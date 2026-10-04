import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def module(path):
    spec=importlib.util.spec_from_file_location("recipe",ROOT/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class SQLRecipes(unittest.TestCase):
    def db(self, key):
        c=sqlite3.connect(":memory:");self.addCleanup(c.close)
        c.executescript((ROOT/f"recipes/{key}/setup.sql").read_text());return c
    def run_sql(self,c,key):c.executescript((ROOT/f"recipes/{key}/solution.sql").read_text())
    def test_retry_is_idempotent(self):
        c=self.db("retry-batch");self.run_sql(c,"retry-batch")
        before=c.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
        self.run_sql(c,"retry-batch");self.assertEqual(before,c.execute("SELECT * FROM orders ORDER BY order_id").fetchall())
        self.assertEqual(c.execute("SELECT COUNT(*),SUM(amount_cents) FROM orders").fetchone(),(2,3000))
    def test_late_update_and_delete_replay(self):
        c=self.db("late-updates");self.run_sql(c,"late-updates")
        for version,op,amount in [(2,"U",1000),(4,"D",None),(3,"U",2500)]:
            c.execute("DELETE FROM changes");c.execute("INSERT INTO changes VALUES ('O1',?,?,?)",(version,op,amount));self.run_sql(c,"late-updates")
            if version==2:self.assertEqual(c.execute("SELECT source_version,amount_cents FROM current_orders").fetchone(),(3,2500))
        self.assertEqual(c.execute("SELECT source_version,op FROM current_orders").fetchone(),(4,"D"))
        self.assertEqual(c.execute("SELECT COUNT(*) FROM current_orders WHERE op='U'").fetchone()[0],0)
    def test_fanout_exposed_then_corrected(self):
        c=self.db("join-fanout")
        self.assertEqual(c.execute("SELECT SUM(amount_cents) FROM orders JOIN customers USING(customer_id)").fetchone()[0],6000)
        statements=(ROOT/"recipes/join-fanout/solution.sql").read_text().split(";")
        self.assertEqual(c.execute(statements[0]).fetchall(),[("C1",2)])
        self.assertEqual(c.execute(statements[1]).fetchone()[0],3000)
    def test_quarantine_reconciles_counts_and_rules(self):
        c=self.db("quarantine");self.run_sql(c,"quarantine")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM accepted").fetchone()[0],1)
        self.assertEqual(c.execute("SELECT failed_rule FROM rejected ORDER BY row_id").fetchall(),[("missing_order_id",),("invalid_amount",),("unsupported_currency",)])
        self.assertEqual(c.execute("SELECT (SELECT COUNT(*) FROM accepted)+(SELECT COUNT(*) FROM rejected)").fetchone()[0],4)
    def test_changed_release_refused(self):
        m=module("recipes/release-check/evidence.py")
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.sql";p.write_text("SELECT 1")
            approved=m.manifest(d);self.assertTrue(m.verify(d,approved))
            p.write_text("SELECT 2")
            with self.assertRaises(ValueError):m.verify(d,approved)
            p.write_text("SELECT 1");q=Path(d)/"extra.sql";q.write_text("SELECT 3")
            with self.assertRaises(ValueError):m.verify(d,approved)
            q.unlink();p.unlink()
            with self.assertRaises(ValueError):m.verify(d,approved)

class MaskProbeTests(unittest.TestCase):
    def test_masking_requires_identity_rows_and_permission_denial(self):
        probe=module("recipes/masking/probe.py").probe
        class Cursor:
            def __init__(self,user="reader",rows=None,error="PERMISSION_DENIED"):self.user=user;self.rows=rows if rows is not None else [("[hidden]",)];self.error=error
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def execute(self,sql):
                if sql.startswith("DELETE"):
                    if self.error:raise RuntimeError(self.error)
            def fetchone(self):return (self.user,)
            def fetchall(self):return self.rows
        class Connection:
            def __init__(self,**kw):self.kw=kw
            def cursor(self):return Cursor(**self.kw)
        self.assertEqual(probe(Connection(),"demo.test.orders","reader","reader")["write_check"],"denied")
        for kw in [{"user":"admin"},{"rows":[]},{"rows":[("raw@example.test",)]},{"error":"NETWORK_ERROR"},{"error":""}]:
            with self.assertRaises((AssertionError,RuntimeError)):probe(Connection(**kw),"demo.test.orders","reader","reader")
        with self.assertRaises(ValueError):probe(Connection(),"orders; DROP TABLE orders","reader","reader")
    def test_notebook_executes_the_documented_sql(self):
        import json,os
        from contextlib import chdir
        folder=ROOT/"recipes/late-updates"
        nb=json.loads((folder/"demo.ipynb").read_text())
        with chdir(folder):
            namespace={}
            for cell in nb["cells"]:
                if cell["cell_type"]=="code":exec("".join(cell["source"]),namespace)
            namespace["db"].close()

if __name__=="__main__":unittest.main()
