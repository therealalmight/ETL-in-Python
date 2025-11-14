import pandas as pd
from sqlalchemy import create_engine, exc
import os

def load_to_mysql(df, table_name, engine):
    """
    Load a pandas DataFrame to MySQL with error handling.
    """
    try:
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        print(f"Data loaded successfully into '{table_name}'.")

    except exc.OperationalError as e:
        print(f"Operational error while loading '{table_name}': {e}")

    except exc.ProgrammingError as e:
        print(f"Programming error in '{table_name}': {e}")

    except exc.IntegrityError as e:
        print(f"Integrity error in '{table_name}': {e}")

    except Exception as e:
        print(f"Unexpected error occurred while loading '{table_name}': {e}")


def load_all_parquets_to_mysql(directory, connection_url, table_name_map=None):
    """
    Load all parquet files in a directory into MySQL tables.
    - directory: path containing parquet files
    - connection_url: SQLAlchemy MySQL connection string
    - table_name_map: optional dict mapping filenames to table names
    """
    engine = create_engine(connection_url)

    try:
        for file in os.listdir(directory):
            if file.endswith(".parquet"):
                file_path = os.path.join(directory, file)
                df = pd.read_parquet(file_path)

                # Determine table name
                base_name = os.path.splitext(file)[0]
                table_name = table_name_map.get(base_name, base_name) if table_name_map else base_name

                print(f"\n🚀 Loading '{file}' into table '{table_name}'...")
                load_to_mysql(df, table_name, engine)

    finally:
        engine.dispose()
        print("\n🔒 Database connection closed.")


# === Example usage ===
connection_url = "mysql+pymysql://db_user:6equj5_root@127.0.0.1:3306/home_db"
gold_path = "src/data_lake/gold/"

# Optional mapping (if parquet names differ from table names)
table_name_map = {
    "DimProperty": "DimProperty",
    "DimLeads": "DimLeads",
    "FactsValuation": "FactsValuation",
    "DimHoa": "DimHoa",
    "DimRehab": "DimRehab",
    "DimTaxes": "DimTaxes"
}

load_all_parquets_to_mysql(gold_path, connection_url, table_name_map)
