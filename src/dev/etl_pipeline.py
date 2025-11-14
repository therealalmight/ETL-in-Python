#!/usr/bin/env python3
"""
Clean, robust ETL pipeline orchestrator.
- Uses existing modules: extract, transform, load, data_validation
- Safe error handling and logging
- Loads parquet files from GOLD layer by default: src/data_lake/gold/

Save this file as `etl_pipeline_clean.py` and run:
    python etl_pipeline_clean.py

You can override the parquet directory with --parquet-dir.
"""
import argparse
import logging
import sys
from pathlib import Path

# Local module imports (assumes these are in PYTHONPATH or same directory)
from extract import extract
from transform import transform
from load import MySQLDataLoader
from data_validation import DataValidation


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("etl_pipeline")


def run_pipeline(
    json_source: str = "data/fake_property_data_new.json",
    bronze_csv: str = "src/data_lake/bronze/fake_property_data_new.csv",
    silver_csv: str = "src/data_lake/silver/fake_property_data_new.csv",
    gold_dir: str = "src/data_lake/gold",
    mysql_uri: str = "mysql+pymysql://root:6equj5_root@127.0.0.1:3306/home_db",
    sql_file: str = "src/dev/func_data_model.sql",
):
    """Orchestrate the ETL pipeline with robust error handling."""

    mysql = None

    try:
        # ----------------------
        # Extract
        # ----------------------
        logger.info("Starting extraction")
        extractor = extract(json_source, bronze_csv)
        extractor.load_json()
        extractor.json_to_csv()
        logger.info("Extraction complete — bronze CSV written: %s", bronze_csv)

        # ----------------------
        # Transform
        # ----------------------
        logger.info("Starting transform")
        transformer = transform(bronze_csv, silver_csv, gold_dir)
        transformer.clean()
        transformer.transform()
        logger.info("Transform complete — silver/gold artifacts created in %s", gold_dir)

        # ----------------------
        # Data validation
        # ----------------------
        logger.info("Starting data validation")
        validator = DataValidation()
        validator.runner()
        logger.info("Validation complete — check logs in gold layer")

        # ----------------------
        # Load
        # ----------------------
        logger.info("Starting load to MySQL")
        mysql = MySQLDataLoader(mysql_uri)

        # run any SQL DDL or function definitions required
        if Path(sql_file).exists():
            logger.info("Running SQL file: %s", sql_file)
            mysql.run_sql_file(sql_file)
        else:
            logger.warning("SQL file not found: %s — skipping run_sql_file", sql_file)

        # Load all parquet files from the gold layer
        gold_path = Path(gold_dir)
        if not gold_path.exists():
            logger.error("Gold directory does not exist: %s", gold_dir)
            raise FileNotFoundError(f"Gold directory not found: {gold_dir}")

        # This method expects a directory path
        logger.info("Loading parquet files from directory: %s", gold_dir)
        mysql.load_parquet_directory(str(gold_path))

        logger.info("Load complete")

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        raise

    finally:
        # Ensure DB engine is disposed if present
        if mysql is not None and hasattr(mysql, "engine"):
            try:
                mysql.engine.dispose()
                logger.info("Database connection closed")
            except Exception:
                logger.exception("Error disposing DB engine")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ETL pipeline (extract -> transform -> validate -> load)")
    parser.add_argument("--json-source", default="data/fake_property_data_new.json", help="Source JSON file for extraction")
    parser.add_argument("--bronze-csv", default="src/data_lake/bronze/fake_property_data_new.csv", help="Bronze CSV output path")
    parser.add_argument("--silver-csv", default="src/data_lake/silver/fake_property_data_new.csv", help="Silver CSV output path")
    parser.add_argument("--gold-dir", default="src/data_lake/gold", help="Gold directory containing parquet files to load")
    parser.add_argument("--mysql-uri", default="mysql+pymysql://root:6equj5_root@127.0.0.1:3306/home_db", help="SQLAlchemy connection URI")
    parser.add_argument("--sql-file", default="src/dev/func_data_model.sql", help="SQL file to run before loading")

    args = parser.parse_args()

    try:
        run_pipeline(
            json_source=args.json_source,
            bronze_csv=args.bronze_csv,
            silver_csv=args.silver_csv,
            gold_dir=args.gold_dir,
            mysql_uri=args.mysql_uri,
            sql_file=args.sql_file,
        )
        logger.info("Pipeline finished successfully")
    except Exception:
        logger.error("Pipeline exited with errors")
        sys.exit(1)
