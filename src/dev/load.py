import os
import pandas as pd
from sqlalchemy import create_engine, exc, text


class MySQLDataLoader:
    """
    Encapsulates MySQL loading, SQL execution, and parquet ingestion
    using SQLAlchemy + PyMySQL + Pandas.
    """

    def __init__(self, connection_url: str, echo: bool = False):
        self.connection_url = connection_url
        self.engine = create_engine(connection_url, echo=echo, future=True)

    # ---------------------------------------------------------
    # Run SQL file
    # ---------------------------------------------------------
    def run_sql_file(self, sql_file_path: str):
        """
        Reads a .sql file and executes it using SQLAlchemy.
        Supports multi-statement SQL scripts.
        """
        try:
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_commands = f.read()

            with self.engine.connect() as conn:
                for statement in sql_commands.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        conn.execute(text(stmt))
                conn.commit()

            print(f"✅ Executed SQL file: {sql_file_path}")

        except FileNotFoundError:
            print(f"❌ SQL file not found: {sql_file_path}")

        except Exception as e:
            print(f"❌ Error executing SQL file '{sql_file_path}': {e}")

    # ---------------------------------------------------------
    # Load DataFrame into MySQL
    # ---------------------------------------------------------
    def load_to_mysql(self, df: pd.DataFrame, table_name: str):
        """
        Load a pandas DataFrame to MySQL with error handling.
        """
        try:
            df.to_sql(table_name, con=self.engine, if_exists="append", index=False)
            print(f"✅ Loaded data into table '{table_name}'.")

        except exc.OperationalError as e:
            print(f"❌ Operational error on '{table_name}': {e}")

        except exc.ProgrammingError as e:
            print(f"❌ Programming error on '{table_name}': {e}")

        except exc.IntegrityError as e:
            print(f"❌ Integrity error on '{table_name}': {e}")

        except Exception as e:
            print(f"❌ Unexpected error loading '{table_name}': {e}")

    # ---------------------------------------------------------
    # Load all Parquet files in a directory
    # ---------------------------------------------------------
    def load_parquet_directory(self, directory: str, table_name_map: dict = None):
        """
        Loads all .parquet files in a folder to MySQL.
        table_name_map can override the default table names.
        """
        try:
            for file in os.listdir(directory):
                if file.endswith(".parquet"):
                    file_path = os.path.join(directory, file)
                    df = pd.read_parquet(file_path)

                    base_name = os.path.splitext(file)[0]
                    table_name = (
                        table_name_map.get(base_name, base_name)
                        if table_name_map else base_name
                    )

                    print(f"\n🚀 Loading '{file}' → table '{table_name}'")
                    self.load_to_mysql(df, table_name)

        except Exception as e:
            print(f"❌ Error loading parquet directory: {e}")

        finally:
            self.engine.dispose()
            print("\n🔒 Database connection closed.")