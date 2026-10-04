"""Run separately with an actual admin/reader Databricks SQL connection.
Requires databricks-sql-connector installed in your own isolated environment.
No tokens are stored or printed. The pre-existing table must be synthetic and
its email mask must return [hidden] to the reader. Do not use a customer table.
"""

import os
import re


def probe(connection, table, mode, expected_user):
    if not re.fullmatch(r"[A-Za-z_]\w*\.[A-Za-z_]\w*\.[A-Za-z_]\w*", table):
        raise ValueError("Use a three-part synthetic table name")
    if mode not in ("admin", "reader"):
        raise ValueError("Choose admin or reader")
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_user()")
        assert cursor.fetchone()[0] == expected_user, "Wrong test identity"
        cursor.execute(f"SELECT email FROM {table} ORDER BY order_id")
        values = [row[0] for row in cursor.fetchall()]
        assert values, "A test with no rows proves nothing"
        assert (
            all(v == "[hidden]" for v in values)
            if mode == "reader"
            else any(v != "[hidden]" for v in values)
        )
        if mode == "reader":
            try:
                cursor.execute(f"DELETE FROM {table} WHERE false")
            except Exception as error:
                # Only an explicit permission-denied error qualifies the negative test.
                if "PERMISSION_DENIED" not in str(error):
                    raise RuntimeError(
                        "Write test failed for another reason; inconclusive"
                    ) from error
            else:
                raise AssertionError("Reader unexpectedly has DELETE permission")
    return {
        "mode": mode,
        "mask_check": "passed",
        "write_check": "denied" if mode == "reader" else "not tested",
    }


if __name__ == "__main__":
    from databricks import sql

    with sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    ) as connection:
        print(
            probe(
                connection,
                os.environ["MASKING_TABLE"],
                os.environ["MASKING_MODE"],
                os.environ["EXPECTED_USER"],
            )
        )
