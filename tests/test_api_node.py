import pytest
from beanie import PydanticObjectId
from httpx import AsyncClient
from textrig.models.text import Node, NodeUpdate


@pytest.mark.anyio
async def test_create_node(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    nodes = test_data["nodes"]

    for node in nodes:
        resp = await test_client.post(endpoint, json=node)
        assert (
            resp.status_code == 201
        ), f"HTTP status {resp.status_code} (expected: 201)"


@pytest.mark.anyio
async def test_child_node_io(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]

    # create parent
    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"
    parent: Node = Node(**resp.json())

    # create child
    child: Node = Node(**node)
    child.parent_id = parent.id
    child.level = parent.level + 1
    child.index = 0
    resp = await test_client.post(endpoint, json=child.dict(serialize_ids=True))
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"
    child = Node(**resp.json())
    assert "_id" in resp.json()
    assert "parent_id" in resp.json()
    assert resp.json()["parent_id"] == str(child.parent_id)

    # find children by parent ID
    resp = await test_client.get(
        endpoint, params={"text_slug": parent.text_slug, "parent_id": str(parent.id)}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) is list
    assert len(resp.json()) == 1
    assert resp.json()[0]["_id"] == str(child.id)

    # find children by parent ID using dedicated children endpoint
    resp = await test_client.get(f"{root_path}/nodes/{child.parent_id}/children")
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) is list
    assert len(resp.json()) == 1
    assert resp.json()[0]["_id"] == str(child.id)


@pytest.mark.anyio
async def test_create_node_invalid_text_fail(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]
    node["text_slug"] = "this_does_not_exist"

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"


@pytest.mark.anyio
async def test_create_node_duplicate_fail(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 409, f"HTTP status {resp.status_code} (expected: 409)"


@pytest.mark.anyio
async def test_get_nodes(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts", "nodes")
    endpoint = f"{root_path}/nodes"
    text = test_data["texts"][0]
    text_slug = text["slug"]
    nodes = [n for n in test_data["nodes"] if n["text_slug"] == text_slug]
    # level = 0
    # index = 0
    # parent_id = None
    # limit = 1000

    # test results length limit
    resp = await test_client.get(
        endpoint, params={"text_slug": text_slug, "level": 0, "limit": 2}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) is list
    assert len(resp.json()) == 2

    # test empty results with status 200
    resp = await test_client.get(
        endpoint, params={"text_slug": "this_does_not_exist", "level": 0}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) is list
    assert len(resp.json()) == 0

    # test results contain all nodes of level 0
    resp = await test_client.get(endpoint, params={"text_slug": text_slug, "level": 0})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) is list
    assert len(resp.json()) == len(nodes)

    # test returned nodes have IDs
    assert "_id" in resp.json()[0]
    PydanticObjectId(resp.json()[0]["_id"])

    # test specific index
    resp = await test_client.get(
        endpoint, params={"text_slug": text_slug, "level": 0, "index": 0}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) is list
    assert len(resp.json()) == 1

    # test invalid request
    resp = await test_client.get(endpoint, params={"text_slug": text_slug})
    assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"


@pytest.mark.anyio
async def test_update_node(
    root_path, test_client: AsyncClient, insert_test_data, test_data
):
    await insert_test_data("texts", "nodes")
    text_slug = test_data["texts"][0]["slug"]
    # get node from db
    endpoint = f"{root_path}/nodes"
    resp = await test_client.get(endpoint, params={"text_slug": text_slug, "level": 0})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    node = Node(**resp.json()[0])
    # update node
    node_update = NodeUpdate(id=node.id, label="A fresh label")
    resp = await test_client.patch(endpoint, json=node_update.dict(serialize_ids=True))
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert "_id" in resp.json()
    assert resp.json()["_id"] == str(node.id)
    assert "label" in resp.json()
    assert resp.json()["label"] == "A fresh label"
    # update unchanged node
    resp = await test_client.patch(endpoint, json=node_update.dict(serialize_ids=True))
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    # update invalid node
    node_update = NodeUpdate(id="637b9ad396d541a505e5439b", label="Brand new label")
    resp = await test_client.patch(endpoint, json=node_update.dict(serialize_ids=True))
    assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"


@pytest.mark.anyio
async def test_node_next(
    root_path, test_client: AsyncClient, insert_test_data, test_data
):
    await insert_test_data("texts", "nodes")
    text_slug = test_data["texts"][0]["slug"]
    # get second last node from level 0
    endpoint = f"{root_path}/nodes"
    resp = await test_client.get(endpoint, params={"text_slug": text_slug, "level": 0})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    nodes = [Node(**n) for n in resp.json()]
    node_second_last = nodes[len(nodes) - 2]
    node_last = nodes[len(nodes) - 1]
    # get next node
    endpoint = f"{root_path}/nodes/{node_second_last.id}/next"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == dict
    assert "_id" in resp.json()
    assert resp.json()["_id"] == str(node_last.id)
    # fail to get node after last
    endpoint = f"{root_path}/nodes/{node_last.id}/next"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 404, f"HTTP status {resp.status_code} (expected: 404)"
