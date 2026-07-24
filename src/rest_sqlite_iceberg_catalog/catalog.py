import os
from pyiceberg.catalog import load_catalog

# Determine warehouse and database location from env vars or defaults
WAREHOUSE_DIR = os.getenv("ICEBERG_WAREHOUSE", os.path.abspath("./warehouse"))
SQLITE_DB_PATH = os.getenv("ICEBERG_SQLITE_PATH", os.path.join(WAREHOUSE_DIR, "catalog.db"))

os.makedirs(WAREHOUSE_DIR, exist_ok=True)

# Instantiate PyIceberg's built-in SqlCatalog
pyiceberg_catalog = load_catalog(
    "local_sqlite",
    **{
        "type": "sql",
        "uri": f"sqlite:///{SQLITE_DB_PATH}",
        "warehouse": f"file://{WAREHOUSE_DIR}",
    },
)
