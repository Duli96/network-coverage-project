import os
import pytest
import gino
from sqlalchemy import create_engine
from app import create_app
from app import db as _db
from app.models.models import db as database
from dotenv import load_dotenv
from app.config import Config


test_db_uri1 = "postgresql://user:password@localhost:5432/test_db_tower"



@pytest.fixture
def config(monkeypatch):
    for key, value in environment.items():
        monkeypatch.setenv(key, value)
    return Config.from_env()

environment = {
    # "HTTPS": "0",
    # "AUTH_SERVICE_URL": PUBLIC_KEY_PATH,
    # "SCRIPT_NAME": "/myapi",
    "SQLALCHEMY_DATABASE_URI":test_db_uri1,
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
        # pass
        alembic_runner.migrate_down_to("base")

@pytest.fixture
async def mock_id():
    return("5aea1cec-2127-4eb5-bd76-4d8d6332e3d3")
        
        