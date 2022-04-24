import imp

from aiohttp import web
import networkx as nx
from app import utils
from app.models import models
from app import db,logging
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET
from connexion.lifecycle import ConnexionResponse
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID, insert
import uuid
from .utils import (
    create_graph_by_graphml,
    convert_network_as_respose_data
)
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPConflict,
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound,
)
from .queries import add_new_network,get_network_list_with_details,get_network_coverage_details
from .connexion_utils import response
from http import HTTPStatus
import json


async def add_network(request: web.Request):

    logging.info("In add_network service method")

    
    form_data = await request.post()

    try:
        graph_ml_file = form_data['Graph File'].file
        print(graph_ml_file)


        content = graph_ml_file.read()
   
        # Create graph using graphml content
        graph = create_graph_by_graphml(content)
    except AttributeError:
        return response("Invalid graph file", HTTPStatus.BAD_REQUEST)
    saved_network = await add_new_network(graph)    
    
    response_data = convert_network_as_respose_data(saved_network)
    
    return response(response_data,HTTPStatus.CREATED)
    
async def get_all_networks(limit):
     logging.info("In get_all_networks service method")
     
     try:
        response_data = await get_network_list_with_details(limit)
     except Exception as e:
         return response("Get all networks failed!", HTTPStatus.INTERNAL_SERVER_ERROR)
     
     return response(response_data,HTTPStatus.OK)

async def get_network_coverage(latitude,longitude):
    response_data = await get_network_coverage_details(latitude,longitude)
    return response(response_data,HTTPStatus.OK)

