"""Resolve synthetic order changes with explicit quality and version rules."""

from dataclasses import dataclass
from decimal import Decimal
import json
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession, Window, functions as F
from pyspark.sql.types import StringType, StructField, StructType


FIELDS = ["order_id", "version", "operation", "amount", "currency", "event_time", "customer_email"]
RAW_SCHEMA = StructType([StructField(name, StringType(), True) for name in FIELDS])
SERVING_COLUMNS = ["order_id", "version", "amount", "currency", "event_time"]


@dataclass
class Result:
    accepted: DataFrame
    rejected: DataFrame
    conflicts: DataFrame
    current: DataFrame
    active: DataFrame


def local_spark() -> SparkSession:
    session = (SparkSession.builder.appName("Order feed field lab")
               .master("local[2]")
               .config("spark.ui.enabled", "false")
               .config("spark.sql.shuffle.partitions", "2")
               .config("spark.sql.session.timeZone", "UTC")
               .config("spark.driver.bindAddress", "127.0.0.1")
               .config("spark.driver.host", "127.0.0.1")
               .getOrCreate())
    session.sparkContext.setLogLevel("ERROR")
    return session


def frame(spark: SparkSession, rows: list[dict]) -> DataFrame:
    """Strict tiny-fixture loader; production readers need equivalent schema checks."""
    for row in rows:
        if set(row) != set(FIELDS):
            raise ValueError("Unexpected or missing source fields; review the source schema")
        if any(value is not None and not isinstance(value, str) for value in row.values()):
            raise ValueError("Fixture input values must be strings or null")
    return spark.createDataFrame(rows, RAW_SCHEMA)


def load_fixture(spark: SparkSession, path: Path) -> DataFrame:
    return frame(spark, json.loads(path.read_text()))


def resolve(raw: DataFrame) -> Result:
    """Rebuild candidate current state from a retained event ledger, not a live MERGE."""
    if set(raw.columns) != set(FIELDS):
        raise ValueError("Unexpected or missing source fields")
    parsed = (raw.withColumn("parsed_version", F.expr("try_cast(version as int)"))
              .withColumn("parsed_amount", F.expr("try_cast(amount as decimal(18,2))"))
              .withColumn("parsed_time", F.expr("try_cast(event_time as timestamp)")))
    # A timestamp helps audit the event; source version decides its order.
    reason = (F.when(F.col("order_id").isNull() | (F.trim("order_id") == ""), "missing_order_id")
              .when(~F.col("order_id").rlike(r"^O-[0-9]{4}$"), "invalid_order_id")
              .when(F.col("parsed_version").isNull() | (F.col("parsed_version") < 1)
                    | ~F.col("version").rlike(r"^[1-9][0-9]*$"), "invalid_version")
              .when(F.col("operation").isNull() | ~F.col("operation").isin("U", "D"), "invalid_operation")
              .when(F.col("currency").isNull() | (F.col("currency") != "NZD"), "unsupported_currency")
              .when(F.col("parsed_time").isNull(), "invalid_event_time")
              .when((F.col("operation") == "U") & (F.col("parsed_amount").isNull()
                    | (F.col("parsed_amount") < 0)
                    | ~F.col("amount").rlike(r"^[0-9]+(\.[0-9]{1,2})?$")), "invalid_amount")
              .otherwise(F.lit(None).cast("string")))
    checked = parsed.withColumn("reason", reason)
    rejected = checked.filter(F.col("reason").isNotNull()).select(*FIELDS, "reason")
    accepted = checked.filter(F.col("reason").isNull()).select(
        "order_id", F.col("parsed_version").alias("version"), "operation",
        F.when(F.col("operation") == "D", F.lit(None).cast("decimal(18,2)"))
         .otherwise(F.col("parsed_amount")).alias("amount"),
        "currency", F.col("parsed_time").alias("event_time"), "customer_email",
    ).distinct()
    # Identical deliveries disappear; contradictory events cannot win arbitrarily.
    conflict_keys = (accepted.groupBy("order_id", "version").count()
                     .filter(F.col("count") > 1).drop("count"))
    conflicts = accepted.join(conflict_keys, ["order_id", "version"], "inner")
    # Hold the entire affected order, even if a later version happens to exist.
    safe = accepted.join(conflict_keys.select("order_id").distinct(), "order_id", "left_anti")
    ordering = Window.partitionBy("order_id").orderBy(F.col("version").desc())
    current = (safe.withColumn("position", F.row_number().over(ordering))
               .filter(F.col("position") == 1).drop("position"))
    # Keep delete markers in current state so an older replay cannot revive an order.
    active = current.filter(F.col("operation") == "U").select(*SERVING_COLUMNS)
    return Result(accepted, rejected, conflicts, current, active)


def total(active: DataFrame) -> Decimal:
    value = active.agg(F.sum("amount").alias("total")).first()["total"]
    return value or Decimal("0.00")


def records(data: DataFrame) -> list[dict]:
    return [row.asDict() for row in data.orderBy("order_id", "version").collect()]
