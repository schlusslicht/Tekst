import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_load_openapi_schema(
    config, api_path, test_client: AsyncClient, status_fail_msg
):
    endpoint = f"{api_path}{config.doc.openapi_url}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_load_swaggerui(
    config, api_path, test_client: AsyncClient, status_fail_msg
):
    endpoint = f"{api_path}{config.doc.swaggerui_url}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_load_redoc(config, api_path, test_client: AsyncClient, status_fail_msg):
    endpoint = f"{api_path}{config.doc.redoc_url}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
