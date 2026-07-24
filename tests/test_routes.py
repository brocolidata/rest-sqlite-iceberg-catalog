# def test_get_config(client):
#     """Test the initial handshake endpoint."""
#     response = client.get("/v1/config")
#     assert response.status_code == 200
#     data = response.json()
#     assert "defaults" in data
#     assert "warehouse" in data["defaults"]


# def test_namespace_crud(client):
#     """Test creating, fetching, listing, and deleting a namespace."""
#     ns_name = "test_namespace"

#     # 1. List namespaces (should be empty initially)
#     res = client.get("/v1/namespaces")
#     assert res.status_code == 200
#     assert res.json()["namespaces"] == []

#     # 2. Create namespace
#     res = client.post("/v1/namespaces", json={"namespace": [ns_name]})
#     assert res.status_code == 200
#     assert res.json()["namespace"] == [ns_name]

#     # 3. Create duplicate namespace (should conflict)
#     res = client.post("/v1/namespaces", json={"namespace": [ns_name]})
#     assert res.status_code == 409

#     # 4. Get namespace details
#     res = client.get(f"/v1/namespaces/{ns_name}")
#     assert res.status_code == 200
#     assert res.json()["namespace"] == [ns_name]

#     # 5. List namespaces again (should contain the new one)
#     res = client.get("/v1/namespaces")
#     assert res.status_code == 200
#     assert [ns_name] in res.json()["namespaces"]

#     # 6. Delete namespace
#     res = client.delete(f"/v1/namespaces/{ns_name}")
#     assert res.status_code == 204

#     # 7. Get deleted namespace (should 404)
#     res = client.get(f"/v1/namespaces/{ns_name}")
#     assert res.status_code == 404


# def test_table_operations(client, setup_tmp_catalog):
#     """Test table operations directly via PyIceberg + API routes."""
#     catalog = setup_tmp_catalog
#     ns_name = "analytics"
#     table_name = "events"

#     # Create namespace first
#     client.post("/v1/namespaces", json={"namespace": [ns_name]})

#     # Check table existence (should be false)
#     res = client.head(f"/v1/namespaces/{ns_name}/tables/{table_name}")
#     assert res.status_code == 404

#     # Create an actual table using PyIceberg's catalog
#     from pyiceberg.schema import Schema
#     from pyiceberg.types import IntegerType, StringType, NestedField

#     schema = Schema(
#         NestedField(1, "id", IntegerType(), required=True),
#         NestedField(2, "data", StringType(), required=False),
#     )
#     catalog.create_table(f"{ns_name}.{table_name}", schema=schema)

#     # 1. Check table existence via HEAD
#     res = client.head(f"/v1/namespaces/{ns_name}/tables/{table_name}")
#     assert res.status_code == 200

#     # 2. List tables in namespace
#     res = client.get(f"/v1/namespaces/{ns_name}/tables")
#     assert res.status_code == 200
#     identifiers = res.json()["identifiers"]
#     assert len(identifiers) == 1
#     assert identifiers[0]["name"] == table_name

#     # 3. Load table metadata (DuckDB uses this to read schema & manifest locations)
#     res = client.get(f"/v1/namespaces/{ns_name}/tables/{table_name}")
#     assert res.status_code == 200
#     data = res.json()
#     assert "metadata" in data
#     assert "metadata-location" in data

#     # 4. Drop table
#     res = client.delete(f"/v1/namespaces/{ns_name}/tables/{table_name}")
#     assert res.status_code == 204

#     # Verify drop
#     res = client.head(f"/v1/namespaces/{ns_name}/tables/{table_name}")
#     assert res.status_code == 404

def test_get_config(client):
    res = client.get("/v1/config")
    assert res.status_code == 200
    assert "defaults" in res.json()

def test_namespace_lifecycle(client):
    ns = "demo"

    # List (empty initially)
    res = client.get("/v1/namespaces")
    assert res.status_code == 200
    assert res.json()["namespaces"] == []

    # Create
    res = client.post("/v1/namespaces", json={"namespace": [ns]})
    assert res.status_code == 200

    # Get
    res = client.get(f"/v1/namespaces/{ns}")
    assert res.status_code == 200
    assert res.json()["namespace"] == [ns]

    # Delete
    res = client.delete(f"/v1/namespaces/{ns}")
    assert res.status_code == 204

def test_table_lifecycle(client, setup_tmp_catalog):
    catalog = setup_tmp_catalog
    ns, table = "analytics", "users"

    client.post("/v1/namespaces", json={"namespace": [ns]})

    # Create table via PyIceberg engine
    from pyiceberg.schema import Schema
    from pyiceberg.types import IntegerType, StringType, NestedField

    schema = Schema(
        NestedField(1, "id", IntegerType(), required=True),
        NestedField(2, "name", StringType(), required=False),
    )
    catalog.create_table(f"{ns}.{table}", schema=schema)

    # HEAD check
    res = client.head(f"/v1/namespaces/{ns}/tables/{table}")
    assert res.status_code == 200

    # GET metadata
    res = client.get(f"/v1/namespaces/{ns}/tables/{table}")
    assert res.status_code == 200
    assert "metadata" in res.json()

    # DELETE
    res = client.delete(f"/v1/namespaces/{ns}/tables/{table}")
    assert res.status_code == 204
