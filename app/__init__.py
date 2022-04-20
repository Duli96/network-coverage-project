from __future__ import annotations

import connexion
from typing import Any
from app.config import Config
from aiohttp import web

import gino


db = gino.Gino()
__version__ = "dev"


def create_app(test_db_uri: str | None = None) -> Any:

    config = Config()
    options = {"swagger_ui": True}
    connexion_app = connexion.AioHttpApp(
        __name__,
        host="localhost",
        port=8000,
        options=options,
        only_one_api=False,
    )
    connexion_app.add_api(
        "api-spec.yaml",
        arguments={"title": "test"},
        pythonic_params=True,
        pass_context_arg_name="request",
    )

    async def on_startup(app: web.Application):
        if test_db_uri:
            uri = test_db_uri
        else:
            uri = config.SQLALCHEMY_DATABASE_URI
        app["engine"] = await gino.create_engine(uri)
        db.bind = app["engine"]

    connexion_app.app.on_startup.append(on_startup)

    return connexion_app
