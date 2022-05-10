import os
from pathlib import Path
import uuid
import pytest
import gino
from sqlalchemy import create_engine
from app import create_app
from app import db as _db
from app.models.models import db as database, Node
from dotenv import load_dotenv
from app.config import Config
import networkx as nx
from test_data import test_data_list


test_db_uri1 = "postgresql://user:password@localhost:5432/test_db_tower"
resources = Path(__file__).parent


@pytest.fixture
def config(monkeypatch):
    for key, value in environment.items():
        monkeypatch.setenv(key, value)
    return Config.from_env()


environment = {
    # "HTTPS": "0",
    # "AUTH_SERVICE_URL": PUBLIC_KEY_PATH,
    # "SCRIPT_NAME": "/myapi",
    "SQLALCHEMY_DATABASE_URI": test_db_uri1,
    # "ASSET_DATABASE_URL": "MOCKED",
    # "BWT_API_URL": "MOCKED",
    # "ASSET_DATABASE_USERNAME": "MOCKED",
    # "ASSET_DATABASE_PASSWORD": "MOCKED",
    # "OPENREACH_API_URL": "http://openreach-api",
    # "OPENREACH_API_CLIENT_ID": "openreach-client-id",
    # "OPENREACH_API_CLIENT_SECRET": "openreach-client-secret",
    # "OPENREACH_API_DUNS": "openreach-duns",
}


@pytest.fixture
def app():
    return create_app(test_db_uri=test_db_uri1)


@pytest.fixture
def test_client(event_loop, aiohttp_client, app):
    client = aiohttp_client(app.app)
    return event_loop.run_until_complete(client)


@pytest.fixture
def alembic_engine():
    return create_engine(test_db_uri1)


@pytest.fixture
def alembic_config():
    return {
        "script_location": "alembic",
    }


@pytest.fixture
async def db(event_loop, alembic_runner):
    if _db.bind is None:
        _db.bind = await gino.create_engine(test_db_uri1)
    try:
        alembic_runner.migrate_up_to("head")
        yield _db
    finally:
        alembic_runner.migrate_down_to("base")


@pytest.fixture
async def graph_one():
    content = open(resources / "test_data/data-1.graphml", "r")
    graph = nx.parse_graphml(content.read())
    return graph


@pytest.fixture
async def graph_two():
    # content = open(resources/'test_data/data.graphml', "r")
    # graph = nx.parse_graphml(content.read())
    graph = nx.DiGraph()
    graph.add_nodes_from(test_data_list.node_list)
    graph.add_edges_from(test_data_list.edge_list)
    return graph


@pytest.fixture
def test_node_list():
    test_node_list = test_data_list.node_list
    return test_node_list


@pytest.fixture
def test_edge_list():
    test_edge_list = test_data_list.edge_list
    return test_edge_list


@pytest.fixture
async def test_tower_data():
    tower = Node()
    tower.id = "c8b60c12-94c7-4243-a74f-c6ced3b16841"
    tower.node_id = "R4T1"
    tower.name = "B-R4T1"
    tower.type = "Tower"
    tower.latitude = 52.8008717
    tower.longitude = -2.3302296
    tower.radius = 15
    return tower
