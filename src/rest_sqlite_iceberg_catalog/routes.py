from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status
from pyiceberg.exceptions import (
    NamespaceAlreadyExistsError,
    NoSuchNamespaceError,
    NoSuchTableError,
    TableAlreadyExistsError,
)

from rest_sqlite_iceberg_catalog.catalog import pyiceberg_catalog, WAREHOUSE_DIR
from rest_sqlite_iceberg_catalog.schemas import (
    ConfigResponse,
    CreateNamespaceRequest,
    CreateNamespaceResponse,
    CreateTableRequest,
    CommitTableRequest,
    UpdateNamespacePropertiesRequest,
)

router = APIRouter(prefix="/v1")

# -----------------------------------------------------------------------------
# Config Handshake
# -----------------------------------------------------------------------------
@router.get("/config", response_model=ConfigResponse)
def get_config(warehouse: Optional[str] = None):
    """Initial handshake endpoint called by DuckDB, Spark, or PyIceberg."""
    return ConfigResponse(
        defaults={"warehouse": f"file://{WAREHOUSE_DIR}"},
        overrides={},
    )

# -----------------------------------------------------------------------------
# Namespace Management
# -----------------------------------------------------------------------------
@router.get("/namespaces")
def list_namespaces(parent: Optional[str] = None):
    parent_tuple = (parent,) if parent else ()
    namespaces = pyiceberg_catalog.list_namespaces(parent_tuple)
    return {"namespaces": [list(ns) for ns in namespaces]}

@router.post("/namespaces", status_code=status.HTTP_200_OK, response_model=CreateNamespaceResponse)
def create_namespace(req: CreateNamespaceRequest):
    ns_tuple = tuple(req.namespace)
    try:
        pyiceberg_catalog.create_namespace(ns_tuple, req.properties)
        return CreateNamespaceResponse(namespace=req.namespace, properties=req.properties)
    except NamespaceAlreadyExistsError:
        raise HTTPException(status_code=409, detail=f"Namespace {req.namespace} already exists")

@router.get("/namespaces/{namespace}")
def get_namespace(namespace: str):
    ns_tuple = tuple(namespace.split("."))
    try:
        props = pyiceberg_catalog.load_namespace_properties(ns_tuple)
        return {"namespace": list(ns_tuple), "properties": props}
    except NoSuchNamespaceError:
        raise HTTPException(status_code=404, detail=f"Namespace '{namespace}' not found")

@router.delete("/namespaces/{namespace}", status_code=status.HTTP_204_NO_CONTENT)
def drop_namespace(namespace: str):
    ns_tuple = tuple(namespace.split("."))
    try:
        pyiceberg_catalog.drop_namespace(ns_tuple)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoSuchNamespaceError:
        raise HTTPException(status_code=404, detail=f"Namespace '{namespace}' not found")

@router.post("/namespaces/{namespace}/properties")
def update_namespace_properties(namespace: str, req: UpdateNamespacePropertiesRequest):
    ns_tuple = tuple(namespace.split("."))
    try:
        removals = set(req.removals) if req.removals else set()
        updates = req.updates if req.updates else {}
        summary = pyiceberg_catalog.update_namespace_properties(ns_tuple, removals=removals, updates=updates)
        return summary
    except NoSuchNamespaceError:
        raise HTTPException(status_code=404, detail=f"Namespace '{namespace}' not found")

# -----------------------------------------------------------------------------
# Table Operations
# -----------------------------------------------------------------------------
@router.get("/namespaces/{namespace}/tables")
def list_tables(namespace: str):
    ns_tuple = tuple(namespace.split("."))
    try:
        tables = pyiceberg_catalog.list_tables(ns_tuple)
        return {
            "identifiers": [
                {"namespace": list(tbl.namespace), "name": tbl.name} for tbl in tables
            ]
        }
    except NoSuchNamespaceError:
        raise HTTPException(status_code=404, detail=f"Namespace '{namespace}' not found")

@router.post("/namespaces/{namespace}/tables", status_code=status.HTTP_200_OK)
def create_table(namespace: str, req: CreateTableRequest):
    identifier = f"{namespace}.{req.name}"
    try:
        table = pyiceberg_catalog.create_table(
            identifier=identifier,
            schema=req.schema_,
            properties=req.properties or {},
        )
        return {
            "metadata-location": table.metadata_location,
            "metadata": table.metadata.model_dump(mode="json"),
            "config": {},
        }
    except TableAlreadyExistsError:
        raise HTTPException(status_code=409, detail=f"Table {identifier} already exists")

@router.get("/namespaces/{namespace}/tables/{table}")
def load_table(namespace: str, table: str):
    identifier = f"{namespace}.{table}"
    try:
        iceberg_tbl = pyiceberg_catalog.load_table(identifier)
        return {
            "metadata-location": iceberg_tbl.metadata_location,
            "metadata": iceberg_tbl.metadata.model_dump(mode="json"),
            "config": {},
        }
    except NoSuchTableError:
        raise HTTPException(status_code=404, detail=f"Table '{identifier}' not found")

@router.head("/namespaces/{namespace}/tables/{table}")
def check_table_exists(namespace: str, table: str):
    identifier = f"{namespace}.{table}"
    if pyiceberg_catalog.table_exists(identifier):
        return Response(status_code=status.HTTP_200_OK)
    return Response(status_code=status.HTTP_404_NOT_FOUND)

@router.post("/namespaces/{namespace}/tables/{table}")
def commit_table_transaction(namespace: str, table: str, req: CommitTableRequest):
    identifier = f"{namespace}.{table}"
    try:
        iceberg_tbl = pyiceberg_catalog.load_table(identifier)
        return {
            "metadata-location": iceberg_tbl.metadata_location,
            "metadata": iceberg_tbl.metadata.model_dump(mode="json"),
            "config": {},
        }
    except NoSuchTableError:
        raise HTTPException(status_code=404, detail=f"Table '{identifier}' not found")

@router.delete("/namespaces/{namespace}/tables/{table}", status_code=status.HTTP_204_NO_CONTENT)
def drop_table(namespace: str, table: str):
    identifier = f"{namespace}.{table}"
    try:
        pyiceberg_catalog.drop_table(identifier)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NoSuchTableError:
        raise HTTPException(status_code=404, detail=f"Table '{identifier}' not found")

@router.post("/namespaces/{namespace}/tables/{table}/metrics", status_code=status.HTTP_204_NO_CONTENT)
def report_metrics(namespace: str, table: str, req: dict):
    """Receives execution telemetry from engines like DuckDB."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)
