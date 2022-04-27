from asyncio import constants
import logging
from typing import Type
from unicodedata import name
from numpy import ediff1d
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from sqlalchemy import and_, func, or_
from app.models import models
from app import db, logging
from geoalchemy2 import func
from .constants import (
    CABLES,
    CENTER_REGION,
    COST,
    GEO_POINT,
    REGION_TOWER,
    REGIONS,
    SOURCE_NODE,
    TARGET_NODE,
    TOWER_COUNT,
    TOWERS,
    UNIQUE_ID,
    CENTER_HUB,
    NETWORK_ID,
    NODE_ID,
    REGION_HUB,
    TOWER,
    NAME,
    TYPE,
    RADIUS,
    LATITUDE,
    LONGITUDE
)
import networkx as nx
from .utils import (
    generate_id,
    create_point,
    create_graph_by_db_data,
    convert_tower_data_to_dict,
)


# Execute queries for add new network to the database
async def add_new_network(graph):
    logging.info("In add_new_network query method")

    network_id = generate_id()
    for node in graph.nodes(data=True):
        new_node_id = generate_id()
        point = create_point(node[1][LONGITUDE], node[1][LATITUDE])
        if (node[1][TYPE] == TOWER):
            continue
        if (node[1][TYPE] == CENTER_HUB):
            network_name = node[1][NAME]
            new_network = models.Network(
                id=network_id,
                name=network_name
            )
            await new_network.create()
        if(node[1][TYPE] == REGION_HUB):
            new_region_node = models.Node(
                id=new_node_id,
                network_id=network_id,
                node_id=node[0],
                name=node[1][NAME],
                type=node[1][TYPE],
                latitude=node[1][LATITUDE],
                longitude=node[1][LONGITUDE],
                geo_point=point
            )
            await new_region_node.create()
            tower_list = list(nx.neighbors(graph, node[0]))
            if(tower_list):
                for node_id in tower_list:
                    tower_node = [node for node in graph.nodes(
                        data=True) if node[0] == node_id]
                    tower_point = create_point(
                        tower_node[0][1][LONGITUDE], tower_node[0][1][LATITUDE])
                    new_tower_node = models.Node(
                        id=generate_id(),
                        network_id=network_id,
                        node_id=tower_node[0][0],
                        name=tower_node[0][1][NAME],
                        type=tower_node[0][1][TYPE],
                        radius=tower_node[0][1][RADIUS],
                        latitude=tower_node[0][1][LATITUDE],
                        longitude=tower_node[0][1][LONGITUDE],
                        geo_point=tower_point,
                        parent_region_hub=new_node_id
                    )
                    await new_tower_node.create()
        else:
            new_center_node = models.Node(
                id=new_node_id,
                network_id=network_id,
                node_id=node[0],
                name=node[1][NAME],
                type=node[1][TYPE],
                latitude=node[1][LATITUDE],
                longitude=node[1][LONGITUDE],
                geo_point=point
            )
            await new_center_node.create()
    for edge in graph.edges(data=True):
        new_edge = models.Edge(
            id=generate_id(),
            network_id=network_id,
            source_node=edge[0],
            target_node=edge[1]
        )
        await new_edge.create()
    return new_network


# Execute queries for retrive network data from the database
async def get_network_list_with_details():
    logging.info("In get_network_list_with_details query method")

    response_network_list = []
    network_nodes_edges_list = await load_networks_with_nodes_and_edges()
    for network in network_nodes_edges_list:
        nodes_list = [node.to_dict() for node in network.nodes]
        edges_list = [edge.to_dict() for edge in network.edges]
        filtered_edges = [(edge[SOURCE_NODE], edge[TARGET_NODE])
                          for edge in edges_list]
        graph = create_graph_by_db_data(nodes_list, filtered_edges)
        node_data_list = []
        for node in graph.nodes(data=True):
            towers = []
            if(node[1][TYPE] == REGION_HUB):
                neighbors_list = list(graph.neighbors(node[0]))
                for neighbor in neighbors_list:
                    tower = list(filter(lambda node: node[1][TYPE] != CENTER_HUB and
                                        node[1][NODE_ID] == neighbor, graph.nodes(data=True)))
                    towers.append(tower[0][1])
                node[1][TOWERS] = towers
                node_data_list.append(node[1])
            elif(node[1][TYPE] == CENTER_HUB):
                network = network.to_dict()
                network[LATITUDE] = node[1][LATITUDE]
                network[LONGITUDE] = node[1][LONGITUDE]
                network[NODE_ID] = node[1][NODE_ID]
        network[REGIONS] = node_data_list
        response_network_list.append(network)
    return response_network_list


# Execute queries to find network coverage
async def get_network_coverage_details(latitude, longitude):
    logging.info("In get_network_coverage_details query method")

    location_geo_point = create_point(longitude, latitude)
    node_list = await load_networks_with_tower_nodes(location_geo_point)
    coverage_network_list = []
    for network in node_list:
        tower_list = list(
            filter(lambda node: node.type == TOWER, network.nodes))
        central_hub = list(
            filter(lambda node: node.type == TOWER, network.nodes))
        if tower_list:
            tower_list_dict = [convert_tower_data_to_dict(
                tower) for tower in tower_list]
            network = network.to_dict()
            network[LATITUDE] = central_hub[0].latitude
            network[LONGITUDE] = central_hub[0].longitude
            network[TOWERS] = tower_list_dict
            network[TOWER_COUNT] = len(tower_list_dict)
            coverage_network_list.append(network)
    return sorted(coverage_network_list, key=lambda x: len(x[TOWERS]), reverse=True)

# Execute queries to calculate total cost
async def calculate_total_cost(network_id, cost_details):
    logging.info("In calculate_total_cost query method")
    
    network = await get_network_from_db(network_id)
    if(network is None):
        raise HTTPNotFound(
            text=f"Network not found for network id:{network_id}")
    node_list = await get_node_list(network_id)
    edge_list = await get_edge_list(network_id)
    if node_list is None or edge_list is None:
        raise HTTPNotFound(
            text=f"Network nodes or edges not found for network id:{network_id}")
    graph = create_graph_by_db_data(node_list, edge_list)
    center_hub_total_cost = len(list(filter(lambda node: node[1][TYPE] == CENTER_HUB, graph.nodes(
        data=True)))) * cost_details[CENTER_HUB][COST]
    region_hub_total_cost = len(list(filter(lambda node: node[1][TYPE] == REGION_HUB, graph.nodes(
        data=True)))) * cost_details[REGION_HUB][COST]
    tower_total_cost = len(list(filter(lambda node: node[1][TYPE] == TOWER, graph.nodes(
        data=True)))) * cost_details[TOWER][COST]
    center_region_total_cost = 0
    region_tower_total_cost = 0
    for edge in graph.edges(data=True):
        source_node = list(
            filter(lambda node: node[0] == edge[0], graph.nodes(data=True)))
        target_node = list(
            filter(lambda node: node[0] == edge[1], graph.nodes(data=True)))
        if(source_node[0][1][TYPE] == CENTER_HUB and target_node[0][1][TYPE] == REGION_HUB):
            center_region_total_cost += cost_details[CABLES][CENTER_REGION][COST]
        elif(source_node[0][1][TYPE] == REGION_HUB and target_node[0][1][TYPE] == TOWER):
            region_tower_total_cost += cost_details[CABLES][REGION_TOWER][COST]
    total_cost = center_region_total_cost + region_tower_total_cost + \
        center_hub_total_cost + region_hub_total_cost + tower_total_cost
    return total_cost


# Get node list for a particular network
async def get_node_list(network_id):
    node_list = await models.Node.select(
        UNIQUE_ID,
        NETWORK_ID,
        NODE_ID,
        NAME,
        TYPE,
        LATITUDE,
        LONGITUDE,
        RADIUS,
    ).where(models.Node.network_id == network_id).gino.all()
    return node_list


# Get edge list for a particular network
async def get_edge_list(network_id):
    edge_list = await models.Edge.select(
        SOURCE_NODE,
        TARGET_NODE
    ).where(models.Edge.network_id == network_id).gino.all()
    return edge_list


# get network data from db using network id
async def get_network_from_db(network_id):
    try:
        network = await models.Network.get(network_id)
        return network
    except Exception:
        raise HTTPBadRequest(
            text=f"Invalid network id: {network_id} length must be between 32..36 characters")


# Load all the nodes and edges that belongs to each network from db
async def load_networks_with_nodes_and_edges():
    query = models.Node.outerjoin(
        models.Network).outerjoin(models.Edge).select()
    network_nodes_edges = await query.gino.load(
        models.Network.distinct(models.Network.id).load(
            add_node=models.Node.distinct(models.Node.id),
            add_edge=models.Edge.distinct(models.Edge.id)
        )
    ).all()
    return network_nodes_edges


# Load all the nodes and edges that belongs to each network from db
async def load_networks_with_tower_nodes(location_geo_point):
    query = models.Node.outerjoin(models.Network).select().where(
        or_(
            func.ST_DistanceSphere(
                location_geo_point, models.Node.geo_point)/1000 < (models.Node.radius),
            models.Node.type == CENTER_HUB
        )
    )
    network_nodes = await query.gino.load(
        models.Network.distinct(models.Network.id).load(
            add_node=models.Node.distinct(models.Node.id)
        )
    ).all()
    return network_nodes
