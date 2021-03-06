from aiohttp import web
from app import logging
from .utils import create_graph_by_graphml
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
)
from .queries import (
    add_new_network,
    get_network_list_with_details,
    get_network_coverage_details,
    calculate_total_cost,
)
from .connexion_utils import response
from http import HTTPStatus
import json


async def add_network(request: web.Request):
    """
    This method adds new network to the database

    :param request: request object from the network call
    :return: network name, network id
    :raises: BadRequest
    """
    logging.info("In add_network method")

    form_data = await request.post()
    if form_data["Graph File"].filename.endswith(".graphml"):
        graph_ml_file = form_data["Graph File"].file
        content = graph_ml_file.read()
        graph = create_graph_by_graphml(content)
        saved_network = await add_new_network(graph)
        return response(saved_network.to_dict(), HTTPStatus.CREATED)
    else:
        raise HTTPBadRequest(text=str("File extension must be .graphml"))


async def get_all_networks():
    """
    This method shows all network details in the database

    :return: network details as a dict
    :raises: InternalServerError
    """
    logging.info("In get_all_networks method")

    try:
        response_data = await get_network_list_with_details()
        return response(response_data, HTTPStatus.OK)
    except Exception as e:
        raise HTTPInternalServerError(text=str(e))


async def get_network_coverage(latitude, longitude):
    """
    This method shows the network coverage for a given location

    :param latitude: latitude of the location
    :param longitude: longitude of the location
    :return: network coverage details with the list of towers
    :raises: BadRequest
    """
    logging.info("In get_network_coverage method")

    response_data = await get_network_coverage_details(latitude, longitude)
    return response(response_data, HTTPStatus.OK)


async def get_total_cost_for_network(request: web.Request):
    """
    This method shows the total cost to build a given network

    :param request: request from the network call
    :return: total cost
    :raises: BadRequest, NotFound
    """
    logging.info("In get_total_cost_for_network method")

    form_data = await request.post()
    if form_data["Cost File"] == "" or form_data["Network id"] == "":
        raise HTTPBadRequest(text=str("Invalid request body"))
    if form_data["Cost File"].filename.endswith(".json"):
        file = form_data["Cost File"].file
        network_id = form_data["Network id"]
        cost_details = json.loads(file.read().decode("utf-8"))
        total_cost = await calculate_total_cost(network_id, cost_details)
        return response({"total cost": total_cost}, HTTPStatus.OK)
    else:
        raise HTTPBadRequest(text=str("File extension must be .json"))
