import os
import sys
import types
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

# Ensure the tests can import "src" using the project root of fastapi_backend
# When running `pytest` from fastapi_backend, this is already fine; this is a safeguard.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import the app from the backend entrypoint used by uvicorn and OpenAPI generator
from src.api.main import app as fastapi_app

# Supabase client in our code is retrieved via src.api.supabase_client.get_supabase_client
# We will monkeypatch that to return a lightweight in-memory fake client.


class FakeSupabaseTable:
    """In-memory stub for Supabase table operations used in routers.

    Supports chaining semantics similar to supabase-py:
    - insert(...).select(...).single().execute()
    - update(...).eq(...).select(...).single().execute()
    - upsert(..., on_conflict="...").select(...).single().execute()
    - select(...).eq(...).order(...).execute()
    """

    def __init__(self, storage: Dict[str, List[Dict[str, Any]]], name: str):
        self._storage = storage
        self._name = name
        self._chain: Dict[str, Any] = {}

    def _reset_if_new_chain(self):
        # If previous chain was executed, new call should reset state.
        # In our simple fake, we allow reusing the same instance between chains by reinitializing when needed.
        pass  # no-op; pytest creates fresh instances via client.table(...)

    # Chainable methods to simulate supabase-py API
    def insert(self, payload: Dict[str, Any]):
        self._reset_if_new_chain()
        self._chain["op"] = "insert"
        self._chain["payload"] = payload
        return self

    def upsert(self, payload: Dict[str, Any], on_conflict: Optional[str] = None):
        self._reset_if_new_chain()
        self._chain["op"] = "upsert"
        self._chain["payload"] = payload
        self._chain["on_conflict"] = on_conflict
        return self

    def update(self, payload: Dict[str, Any]):
        self._reset_if_new_chain()
        self._chain["op"] = "update"
        self._chain["payload"] = payload
        return self

    def delete(self):
        self._reset_if_new_chain()
        self._chain["op"] = "delete"
        return self

    def select(self, fields: str):
        # Do not override previously stored op; record that a select should be returned after mutation.
        # If there is no op yet, treat as a normal SELECT.
        if "op" not in self._chain or self._chain.get("op") in (None, "select"):
            self._chain["op"] = "select"
        else:
            # Remember that a select was requested after a mutation (insert/update/upsert)
            self._chain["select_after"] = True
        self._chain["fields"] = fields
        return self

    def single(self):
        self._chain["single"] = True
        return self

    def order(self, column: str, desc: bool = False):
        self._chain["order_by"] = (column, desc)
        return self

    def eq(self, field: str, value: Any):
        self._chain.setdefault("filters", []).append(("eq", field, value))
        return self

    def _apply_filters(self, rows: List[Dict[str, Any]]):
        filters = self._chain.get("filters", [])
        for ftype, field, value in filters:
            if ftype == "eq":
                rows = [r for r in rows if r.get(field) == value]
        # order
        if "order_by" in self._chain:
            col, desc = self._chain["order_by"]
            rows = sorted(rows, key=lambda r: r.get(col), reverse=desc)
        return rows

    def _ensure_id(self, row: Dict[str, Any], table: List[Dict[str, Any]]):
        if "id" not in row:
            row["id"] = f"{self._name}_id_{len(table)+1}"

    def execute(self):
        op = self._chain.get("op")
        table = self._storage.setdefault(self._name, [])

        # Helper to wrap return with single() semantics if requested
        def _wrap_data(rows_or_row):
            if self._chain.get("single"):
                if isinstance(rows_or_row, list):
                    return rows_or_row[0] if rows_or_row else None
                return rows_or_row
            return rows_or_row

        if op == "insert":
            payload = dict(self._chain.get("payload") or {})
            self._ensure_id(payload, table)
            table.append(payload)
            if self._chain.get("select_after"):
                # Return inserted row(s) when select() was chained
                return types.SimpleNamespace(data=_wrap_data(payload))
            # Minimal success payload when no select chained (emulates supabase default)
            return types.SimpleNamespace(data=None)

        if op == "upsert":
            payload = dict(self._chain.get("payload") or {})
            key_fields: List[str] = []
            on_conflict = self._chain.get("on_conflict")
            if on_conflict:
                key_fields = [k.strip() for k in str(on_conflict).split(",") if k.strip()]
            # find match
            idx = None
            if key_fields:
                for i, row in enumerate(table):
                    if all(row.get(k) == payload.get(k) for k in key_fields):
                        idx = i
                        break
            if idx is None:
                self._ensure_id(payload, table)
                table.append(payload)
                affected = payload
            else:
                table[idx].update({k: v for k, v in payload.items() if v is not None})
                affected = table[idx]
            if self._chain.get("select_after"):
                return types.SimpleNamespace(data=_wrap_data(affected))
            return types.SimpleNamespace(data=None)

        if op == "update":
            payload = dict(self._chain.get("payload") or {})
            rows = self._apply_filters(table)
            if not rows:
                # No rows matched
                return types.SimpleNamespace(data=_wrap_data(None if self._chain.get("single") else []))
            # Update all matched rows (Supabase would normally update all; .single() narrows return)
            for r in rows:
                r.update(payload)
            if self._chain.get("select_after"):
                return types.SimpleNamespace(data=_wrap_data(rows))
            # No select chained: minimal payload
            return types.SimpleNamespace(data=None)

        if op == "delete":
            rows = self._apply_filters(table)
            to_remove_ids = set(id(row) for row in rows)
            self._storage[self._name] = [r for r in table if id(r) not in to_remove_ids]
            return types.SimpleNamespace(data=None)

        if op == "select":
            rows = self._apply_filters(table)
            return types.SimpleNamespace(data=_wrap_data(rows))

        # default
        return types.SimpleNamespace(data=None)


class FakeStorageBucket:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.files: Dict[str, bytes] = {}

    def upload(self, path: str, content: bytes):
        self.files[path] = content
        return {"path": path}

    def get_public_url(self, path: str):
        # Return a predictable fake URL
        return f"https://example-bucket/{self.bucket_name}/{path}"


class FakeStorage:
    def __init__(self):
        self._buckets: Dict[str, FakeStorageBucket] = {}

    def from_(self, bucket_name: str):
        if bucket_name not in self._buckets:
            self._buckets[bucket_name] = FakeStorageBucket(bucket_name)
        return self._buckets[bucket_name]


class FakeSupabaseClient:
    """Minimal supabase client stub with .table() and .storage for tests."""

    def __init__(self, backing: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self._storage = backing if backing is not None else {}
        self.storage = FakeStorage()

    def table(self, name: str) -> FakeSupabaseTable:
        return FakeSupabaseTable(self._storage, name)


@pytest.fixture
def app_client(monkeypatch):
    """
    Provide a TestClient with Supabase client mocked out across routers.

    This fixture:
    - Builds a FakeSupabaseClient as in-memory store.
    - Patches src.api.supabase_client.get_supabase_client to return the fake.
    - Critically, also patches the locally imported get_supabase_client symbol inside:
        * src.api.routers_lessons
        * src.api.routers_quizzes
        * src.api.routers_assignments
      to ensure the routers use the fake client without needing Supabase env vars.
    - Ensures deterministic storage bucket name for upload tests.
    """
    # In-memory DB across a test case
    backing_store: Dict[str, List[Dict[str, Any]]] = {}
    fake_client = FakeSupabaseClient(backing_store)

    # Monkeypatch module-level factory
    import src.api.supabase_client as sb_module

    def fake_get_client():
        return fake_client

    monkeypatch.setattr(sb_module, "get_supabase_client", fake_get_client, raising=True)

    # Import each router module and patch their locally imported get_supabase_client
    import src.api.routers_lessons as r_lessons
    import src.api.routers_quizzes as r_quizzes
    import src.api.routers_assignments as r_assignments

    monkeypatch.setattr(r_lessons, "get_supabase_client", fake_get_client, raising=True)
    monkeypatch.setattr(r_quizzes, "get_supabase_client", fake_get_client, raising=True)
    monkeypatch.setattr(r_assignments, "get_supabase_client", fake_get_client, raising=True)

    # Also patch settings to avoid .env dependence for storage bucket
    from src.api import config as cfg_module
    settings = cfg_module.get_settings()
    # ensure bucket name deterministic for tests
    settings.supabase_storage_bucket = "test-bucket"

    # Create test client after monkeypatching
    client = TestClient(fastapi_app)
    return client
