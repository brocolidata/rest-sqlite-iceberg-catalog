# import pytest
# from fastapi.testclient import TestClient
# from pyiceberg.catalog import load_catalog

# import rest_sqlite_iceberg_catalog.catalog as catalog_module
# from rest_sqlite_iceberg_catalog.main import app

# @pytest.fixture(autouse=True)
# def setup_tmp_catalog(tmp_path):
#     """Re-routes PyIceberg catalog to a clean temp directory for each test."""
#     tmp_warehouse = tmp_path / "warehouse"
#     tmp_warehouse.mkdir()
#     tmp_db = tmp_warehouse / "catalog.db"

#     test_catalog = load_catalog(
#         "test_sqlite",
#         **{
#             "type": "sql",
#             "uri": f"sqlite:///{tmp_db}",
#             "warehouse": f"file://{tmp_warehouse}",
#         },
#     )

#     catalog_module.pyiceberg_catalog = test_catalog
#     catalog_module.WAREHOUSE_DIR = str(tmp_warehouse)

#     yield test_catalog

# @pytest.fixture
# def client():
#     """FastAPI TestClient fixture."""
#     return TestClient(app)
#

import pytest
from fastapi.testclient import TestClient
from pyiceberg.catalog import load_catalog

import rest_sqlite_iceberg_catalog.catalog as catalog_module
import rest_sqlite_iceberg_catalog.routes as routes_module
from rest_sqlite_iceberg_catalog.main import app

@pytest.fixture(autouse=True)
def setup_tmp_catalog(tmp_path, monkeypatch):
    """Re-routes PyIceberg catalog to a clean isolated temp directory for each test."""
    tmp_warehouse = tmp_path / "warehouse"
    tmp_warehouse.mkdir()
    tmp_db = tmp_warehouse / "catalog.db"

    test_catalog = load_catalog(
        "test_sqlite",
        **{
            "type": "sql",
            "uri": f"sqlite:///{tmp_db}",
            "warehouse": f"file://{tmp_warehouse}",
        },
    )

    # Monkeypatch catalog instance in BOTH catalog module and routes module
    monkeypatch.setattr(catalog_module, "pyiceberg_catalog", test_catalog)
    monkeypatch.setattr(routes_module, "pyiceberg_catalog", test_catalog)
    monkeypatch.setattr(catalog_module, "WAREHOUSE_DIR", str(tmp_warehouse))
    monkeypatch.setattr(routes_module, "WAREHOUSE_DIR", str(tmp_warehouse))

    yield test_catalog

@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)
