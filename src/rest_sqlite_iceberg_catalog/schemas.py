from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# --- Handshake & Auth ---
class ConfigResponse(BaseModel):
    defaults: Dict[str, str] = Field(default_factory=dict)
    overrides: Dict[str, str] = Field(default_factory=dict)

# --- Namespace Requests / Responses ---
class CreateNamespaceRequest(BaseModel):
    namespace: List[str]
    properties: Optional[Dict[str, str]] = Field(default_factory=dict)

class CreateNamespaceResponse(BaseModel):
    namespace: List[str]
    properties: Optional[Dict[str, str]] = Field(default_factory=dict)

class UpdateNamespacePropertiesRequest(BaseModel):
    removals: Optional[List[str]] = Field(default_factory=list)
    updates: Optional[Dict[str, str]] = Field(default_factory=dict)

# --- Table Requests / Responses ---
class CreateTableRequest(BaseModel):
    name: str
    schema_: Dict[str, Any] = Field(..., alias="schema")
    partition_spec: Optional[Dict[str, Any]] = None
    write_order: Optional[Dict[str, Any]] = None
    stage_create: Optional[bool] = False
    properties: Optional[Dict[str, str]] = Field(default_factory=dict)

class CommitTableRequest(BaseModel):
    identifier: Optional[Dict[str, Any]] = None
    requirements: List[Dict[str, Any]] = Field(default_factory=list)
    updates: List[Dict[str, Any]] = Field(default_factory=list)
