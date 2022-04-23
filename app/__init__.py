from __future__ import annotations
from curses import meta
import imp
from importlib_metadata import metadata
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
import connexion
from typing import Any
from app.config import Config
from aiohttp import web


import gino
from gino.schema import GinoSchemaVisitor

logging.basicConfig(level=logging.INFO)
db = gino.Gino()
metadata = MetaData()
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
        pythonic_params=True,
        pass_context_arg_name="request",
    )

    async def on_startup(app: web.Application):
        
        if test_db_uri:
            uri = test_db_uri
        else:
            uri = config.SQLALCHEMY_DATABASE_URI
        print(uri) 
        app["engine"] = await gino.create_engine(uri)
        # con = await app["engine"].acquire()
        # print()
        from .models.models import db
        db.bind = app["engine"]
        # db.gino.create_all()
        
        # db.create_all()
        
        # db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=app["engine"]))
        # print(db)
        # async with db.with_bind(uri)
        # db.gino.create_all()       
       
       

    connexion_app.app.on_startup.append(on_startup)

    return connexion_app
