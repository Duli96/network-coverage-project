from aiohttp import web
from app.models import *
from app import db


async def start(request: web.Request):
    data='This is a test'
    return web.json_response({'data':data} , status=200)