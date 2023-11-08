from pathlib import Path
from typing import Any, Callable

import pytest
import requests

from asgi_lifespan import LifespanManager
from bson import ObjectId, json_util
from httpx import AsyncClient, Response
from humps import camelize
from tekst.app import app
from tekst.auth import _create_user
from tekst.config import TekstConfig, get_config
from tekst.db import DatabaseClient
from tekst.dependencies import get_db_client
from tekst.models.user import UserCreate


"""
pytest fixtures go in here...
"""


@pytest.fixture(scope="session")
def config() -> TekstConfig:
    """Returns the app config according to passed env vars, env file or defaults"""
    return get_config()


@pytest.fixture(scope="session")
def api_path(config) -> TekstConfig:
    """Returns the configured app root path"""
    return config.api_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def get_test_file_path(request) -> Callable[[str], Any]:
    """Returns the absolute path to a file relative to tests/data"""

    def _get_test_file_path(rel_path: str) -> Any:
        datadir = Path(request.config.rootdir) / "tests/data"
        return datadir / rel_path

    return _get_test_file_path


@pytest.fixture
def get_test_data(request) -> Callable[[str], Any]:
    """Returns the object representation of a JSON file relative to tests/data"""

    def _get_test_data(rel_path: str, for_http: bool = False) -> Any:
        datadir = Path(request.config.rootdir) / "tests/data"
        data = json_util.loads((datadir / rel_path).read_text())
        if for_http:
            data = camelize(
                [
                    {k: str(v) if isinstance(v, ObjectId) else v for k, v in o.items()}
                    for o in data
                ]
            )
        return data

    return _get_test_data


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
    db_client: DatabaseClient = DatabaseClient(config.db_get_uri())
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
    await get_db_client_override.drop_database(config.db_name)


@pytest.fixture
async def test_client(test_app) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def reset_db(get_db_client_override, config):
    for collection in ("texts", "nodes", "layers", "units", "users"):
        await get_db_client_override[config.db_name][collection].drop()


@pytest.fixture
async def insert_test_data(config, reset_db, get_test_data) -> Callable:
    """
    Returns an asynchronous function to insert
    test data into their respective database collections
    """

    async def _insert_test_data(*collections: str) -> dict[str, list[str]]:
        db = get_db_client()[config.db_name]
        ids = dict()
        for collection in collections:
            result = await db[collection].insert_many(
                get_test_data(f"db/{collection}.json")
            )
            if not result.acknowledged:
                raise Exception(f"Failed to insert test {collection}")
            ids[collection] = [str(id_) for id_ in result.inserted_ids]
        return ids

    return _insert_test_data


@pytest.fixture
def new_user_data() -> dict:
    return dict(
        email="foo@bar.de",
        username="test_user",
        password="poiPOI098",
        first_name="Foo",
        last_name="Bar",
        affiliation="Some Institution",
    )


@pytest.fixture
async def register_test_user(new_user_data) -> Callable:
    async def _register_test_user(
        *, is_active: bool = True, is_verified: bool = True, is_superuser: bool = False
    ) -> dict:
        user = UserCreate(**new_user_data)
        user.is_active = is_active
        user.is_verified = is_verified
        user.is_superuser = is_superuser
        created_user = await _create_user(user)
        return {"id": str(created_user.id), **new_user_data}

    return _register_test_user


@pytest.fixture
async def get_session_cookie(
    config, test_client, api_path, status_fail_msg
) -> Callable:
    async def _get_session_cookie(user_data: dict) -> dict:
        endpoint = f"{api_path}/auth/cookie/login"
        payload = {"username": user_data["email"], "password": user_data["password"]}
        resp = await test_client.post(
            endpoint,
            data=payload,
        )
        assert resp.status_code == 204, status_fail_msg(204, resp)
        assert resp.cookies.get(config.security_auth_cookie_name)
        return resp.cookies

    return _get_session_cookie


@pytest.fixture(scope="session")
def status_fail_msg() -> Callable:
    def _status_fail_msg(expected_status: int, response: Response) -> tuple[bool, str]:
        resp_json = "No JSON response data."
        try:
            resp_json = response.json()
        except Exception:
            pass
        return (
            f"HTTP {response.status_code} (expected: {expected_status})"
            f" -- {resp_json}"
        )

    return _status_fail_msg


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Prevents outside network access while testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
