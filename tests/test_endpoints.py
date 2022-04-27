import json
import resource
from unittest.mock import patch
from wsgiref.headers import Headers
import pytest
import requests
import json
from unittest import mock
from pathlib import Path
from app.models import models

resources = Path(__file__).parent


async def test_get_all_networks(test_client, db):
    response = await test_client.get("/api/network")
    assert response.status == 200


async def test_add_new_network(test_client, db):
    data = {"Graph File": (resources / "test_data/data-1.graphml").open("rb")}
    response = await test_client.post("/api/network", data=data)
    response_text = await response.text()
    assert json.loads(response_text)["name"] == "Mobi-London"
    assert response.status == 201


async def test_add_new_network_with_wrong_file(test_client, db):
    data = {"Graph File": (resources / "test_data/rate-card-1.json").open("rb")}
    response = await test_client.post("/api/network", data=data)
    response_text = await response.text()
    assert json.loads(response_text)["detail"] == "File extension must be .graphml"
    assert response.status == 400


async def test_get_network_coverage(test_client, db):
    longitude = -1.8007318041255194
    latitude = 51.67787236789842
    response = await test_client.get(f"/api/network/{latitude}/{longitude}")
    response_text = await response.text()
    assert response.status == 200


async def test_get_network_coverage_wrong_params(test_client, db):
    longitude = -1.8007318041255194
    latitude = None
    response = await test_client.get(f"/api/network/{latitude}/{longitude}")
    response_text = await response.text()
    assert (
        json.loads(response_text)["detail"]
        == "Wrong type, expected 'number' for path parameter 'latitude'"
    )
    assert response.status == 400


@mock.patch("app.queries.create_graph_by_db_data")
@mock.patch("app.queries.get_network_from_db")
async def test_get_total_cost_for_network(
    get_network, create_graph, test_client, graph_one, db
):
    get_network.return_value = models.Network()
    create_graph.return_value = graph_one
    data = {
        "Cost File": (resources / "test_data/rate-card-1.json").open("rb"),
        "Network id": "c8b60c12-94c7-4243-a74f-c6ced3b16841",
    }
    response = await test_client.post("/api/network/cost", data=data)
    response_text = await response.text()
    assert json.loads(response_text)["total cost"] == 7400
    assert response.status == 200


async def test_get_total_cost_for_network_invalid_network_id(test_client, db):
    data = {
        "Cost File": (resources / "test_data/rate-card-1.json").open("rb"),
        "Network id": "-94c7-4243-a74f-c6ced3b16841",
    }
    response = await test_client.post("/api/network/cost", data=data)
    response_text = await response.text()
    assert (
        json.loads(response_text)["detail"]
        == "Invalid network id: -94c7-4243-a74f-c6ced3b16841 length must be between 32..36 characters"
    )
    assert response.status == 400


async def test_get_total_cost_for_network_not_found(test_client, db):
    data = {
        "Cost File": (resources / "test_data/rate-card-1.json").open("rb"),
        "Network id": "c8b60c12-94c7-4243-a74f-c6ced3b16841",
    }
    response = await test_client.post("/api/network/cost", data=data)
    response_text = await response.text()
    assert (
        json.loads(response_text)["detail"]
        == "Network not found for network id:c8b60c12-94c7-4243-a74f-c6ced3b16841"
    )
    assert response.status == 404


async def test_get_total_cost_for_network_with_wrong_file(test_client, db):
    data = {
        "Cost File": (resources / "test_data/data-1.graphml").open("rb"),
        "Network id": "c8b60c12-94c7-4243-a74f-c6ced3b16841",
    }
    response = await test_client.post("/api/network/cost", data=data)
    response_text = await response.text()
    assert json.loads(response_text)["detail"] == "File extension must be .json"
    assert response.status == 400
