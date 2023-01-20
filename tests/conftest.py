import json

import pytest
import requests
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from textrig.app import app
from textrig.config import TextRigConfig, get_config
from textrig.db import DatabaseClient
from textrig.dependencies import get_db_client
from textrig.layer_types import get_layer_type
from textrig.models.text import Node, Text


"""
pytest fixtures go in here...
"""


@pytest.fixture(scope="session")
def config() -> TextRigConfig:
    """Returns the app config according to passed env vars, env file or defaults"""
    return get_config()


@pytest.fixture(scope="session")
def root_path(config) -> TextRigConfig:
    """Returns the configured app root path"""
    return config.root_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def test_data(shared_datadir) -> dict:
    """Returns all shared test data"""
    return json.loads((shared_datadir / "test-data.json").read_text())


# @pytest.fixture(scope="session")
# def event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session")
async def get_db_client_override(config) -> DatabaseClient:
    """Dependency override for the database client dependency"""
    db_client: DatabaseClient = DatabaseClient(config.db.get_uri())
    yield db_client
    # close db connection
    db_client.close()


@pytest.fixture(scope="session")
async def test_app(config, get_db_client_override):
    """Provides an app instance with overridden dependencies"""
    app.dependency_overrides[get_db_client] = lambda: get_db_client_override
    async with LifespanManager(app):
        yield app
    # cleanup data
    await get_db_client_override.drop_database(config.db.name)


@pytest.fixture
async def test_client(test_app) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def reset_db(get_db_client_override, config):
    await get_db_client_override.drop_database(config.db.name)


@pytest.fixture
async def insert_test_data(test_app, reset_db, root_path, test_data) -> callable:
    """
    Returns an asynchronous function to insert
    test data into their respective database collections
    """

    async def _insert_test_data(*collections: str) -> str | None:
        if "texts" in collections:
            text = Text(**test_data["texts"][0])
            await text.create()
        if "nodes" in collections:
            for doc in test_data["nodes"]:
                await Node(text=text.id, **doc).create()
        if "layers" in collections:
            for doc in test_data["layers"]:
                LayerModel = get_layer_type(doc["layerType"]).get_layer_model()
                await LayerModel(text=text.id, **doc).create()

        return str(text.id) if text else None

    return _insert_test_data


# @pytest.fixture(scope="session")
# def json_compat() -> callable:
#     """
#     Returns a function that forces JSON encodability of the passed object.
#     """

#     def _json_compat(obj):
#         if isinstance(obj, dict):
#             return {str(k): _json_compat(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [_json_compat(i) for i in obj]
#         else:
#             try:
#                 json.dumps(obj)
#             except Exception:
#                 return str(obj)
#             return obj

#     return _json_compat


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Prevents outside network access while testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
