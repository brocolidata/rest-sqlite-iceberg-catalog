import os
import uvicorn
from fastapi import FastAPI
from rest_sqlite_iceberg_catalog.routes import router

app = FastAPI(title="SQLite Iceberg REST Catalog")
app.include_router(router)

def cli():
    """Executable function called by `rest-sqlite-iceberg-catalog` CLI script."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("rest_sqlite_iceberg_catalog.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    cli()
