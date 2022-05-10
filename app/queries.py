import logging
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from sqlalchemy import func, or_, and_
from app.models import models
from app import db
from gino.loader import ColumnLoader
from geopy.distance import geodesic
from .constants import (
    CABLES,
    CENTER_REGION,
    COST,
    REGION_TOWER,
    REGIONS,
    SOURCE_NODE,
    TARGET_NODE,
    TOWER_COUNT,
    TOWERS,
    CENTER_HUB,
    NODE_ID,
    REGION_HUB,
    TOWER,
    NAME,
    TYPE,
    RADIUS,
    LATITUDE,
    LONGITUDE,
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

    network_uuid = generate_id()
    nodes_to_save = []
    towers_to_save = []
    for node in graph.nodes(data=True):
        print("NODE",node)
        new_node_id = generate_id()
        node_id: str = node[0]
        data: dict = node[1]
        point = create_point(data[LONGITUDE], data[LATITUDE])
        if data[TYPE] == TOWER:
            continue
        if data[TYPE] == CENTER_HUB:
            network_name = data[NAME]
            new_network = models.Network(id=network_uuid, name=network_name)
            print("SAVED",await new_network.create())
            saved_network = await new_network.create()
            
        if data[TYPE] == REGION_HUB:
            new_region_node = models.Node(
                id=new_node_id,
                network_id=network_uuid,
                node_id=node_id,
                name=data[NAME],
                type=data[TYPE],
                latitude=data[LATITUDE],
                longitude=data[LONGITUDE],
                geo_point=point,
            )
            nodes_to_save.append(new_region_node.to_dict())
            tower_list = nx.neighbors(graph, node_id)
            if tower_list:
                for tower_node_id in tower_list:
                    tower_node = [
                        tower
                        for tower in graph.nodes(data=True)
                        if tower[0] == tower_node_id
                    ]
                    tower_data_id: str = tower_node[0][0]
                    tower_data: dict = tower_node[0][1]
                    tower_point = create_point(
                        tower_data[LONGITUDE], tower_data[LATITUDE]
                    )
                    new_tower_node = models.Node(
                        id=generate_id(),
                        network_id=network_uuid,
                        node_id=tower_data_id,
                        name=tower_data[NAME],
                        type=tower_data[TYPE],
                        radius=tower_data[RADIUS],
                        latitude=tower_data[LATITUDE],
                        longitude=tower_data[LONGITUDE],
                        geo_point=tower_point,
                        parent_region_hub=new_node_id,
                    )
                    nodes_to_save.append(new_tower_node.to_dict())
        else:
            new_center_node = models.Node(
                id=new_node_id,
                network_id=network_uuid,
                node_id=node_id,
                name=data[NAME],
                type=data[TYPE],
                latitude=data[LATITUDE],
                longitude=data[LONGITUDE],
                geo_point=point,
            )
            nodes_to_save.append(new_center_node.to_dict())
    edges_to_save = []
    for edge in graph.edges(data=True):
        new_edge = models.Edge(
            id=generate_id(),
            network_id=network_uuid,
            source_node=edge[0],
            target_node=edge[1],
        )
        edges_to_save.append(new_edge.to_dict())
    print("SAVED1",nodes_to_save)
    print("SAVED1",edges_to_save)

    await models.Node.insert().gino.all(nodes_to_save)
    await models.Edge.insert().gino.all(edges_to_save)
    return saved_network


# Execute queries for retrive network data from the database
async def get_network_list_with_details():
    logging.info("In get_network_list_with_details query method")

    response_network_list = []
    network_nodes_edges_list = await load_networks_with_nodes_and_edges()
    for network in network_nodes_edges_list:
        nodes_list = [node.to_dict() for node in network.nodes]
        edges_list = [edge.to_dict() for edge in network.edges]
        filtered_edges = [(edge[SOURCE_NODE], edge[TARGET_NODE]) for edge in edges_list]
        graph = create_graph_by_db_data(nodes_list, filtered_edges)
        node_data_list = []
        for node in graph.nodes(data=True):
            node_data: dict = node[1]
            towers = []
            if node_data[TYPE] == REGION_HUB:
                neighbors_list = nx.neighbors(graph, node[0])
                for neighbor in neighbors_list:
                    tower = next(
                        filter(
                            lambda node: node[1][TYPE] != CENTER_HUB
                            and node[1][NODE_ID] == neighbor,
                            graph.nodes(data=True),
                        ),
                        None,
                    )
                    towers.append(tower[1])
                node_data[TOWERS] = towers
                del node_data[RADIUS]
                node_data_list.append(node_data)
            elif node_data[TYPE] == CENTER_HUB:
                network = network.to_dict()
                network[LATITUDE] = node_data[LATITUDE]
                network[LONGITUDE] = node_data[LONGITUDE]
                network[NODE_ID] = node_data[NODE_ID]
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
        tower_list = list(filter(lambda node: node.type == TOWER, network.nodes))
        central_hub = next(filter(lambda node: node.type == TOWER, network.nodes), None)
        if tower_list:
            tower_list_dict = [
                convert_tower_data_to_dict(tower) for tower in tower_list
            ]
            network = network.to_dict()
            network[LATITUDE] = central_hub.latitude
            network[LONGITUDE] = central_hub.longitude
            network[TOWERS] = tower_list_dict
            network[TOWER_COUNT] = len(tower_list_dict)
            coverage_network_list.append(network)
    return sorted(coverage_network_list, key=lambda x: len(x[TOWERS]), reverse=True)


# Execute queries to calculate total cost
async def calculate_total_cost(network_id, cost_details):
    logging.info("In calculate_total_cost query method")

    network = await get_network_from_db(network_id)
    if network is None:
        raise HTTPNotFound(text=f"Network not found for network id:{network_id}")
    central_hub_total_cost = 0
    region_hub_total_cost = 0
    tower_total_cost = 0
    central_region_total_cost = 0
    region_tower_total_cost = 0
    node_parent_list = await get_nodes_with_parents(network_id)
    if node_parent_list:
        central_hub = next(
            filter(lambda node: node.type == CENTER_HUB, node_parent_list), None
        )
        central_hub_coords = (central_hub.latitude, central_hub.longitude)
        central_hub_total_cost = cost_details[CENTER_HUB][COST]
        for node in node_parent_list:
            if node.type == REGION_HUB:
                region_hub_total_cost += cost_details[REGION_HUB][COST]
                regional_hub_coords = (node.latitude, node.longitude)
                distance_central_regional = round(
                    geodesic(central_hub_coords, regional_hub_coords).km, 2
                )
                central_region_total_cost += (
                    cost_details[CABLES][CENTER_REGION][COST]
                    * distance_central_regional
                )
            elif node.type == TOWER:
                tower_total_cost += cost_details[TOWER][COST]
                tower_coords = (node.latitude, node.longitude)
                parent_regional_coords = (node.parent.latitude, node.parent.longitude)
                distance_regional_tower = round(
                    geodesic(parent_regional_coords, tower_coords).km, 2
                )
                region_tower_total_cost += (
                    cost_details[CABLES][REGION_TOWER][COST] * distance_regional_tower
                )

    total_cost = (
        central_region_total_cost
        + region_tower_total_cost
        + central_hub_total_cost
        + region_hub_total_cost
        + tower_total_cost
    )
    return total_cost


# get nodes with their parents if the node is a tower node
async def get_nodes_with_parents(network_id):
    Parent = models.Node.alias()
    query = models.Node.load(
        parent=Parent.on(models.Node.parent_region_hub == Parent.id)
    ).where(models.Node.network_id == network_id)
    nodes_list = await query.gino.all()
    return nodes_list


# get network data from db using network id
async def get_network_from_db(network_id):
    try:
        network = await models.Network.get(network_id)
        return network
    except Exception:
        raise HTTPBadRequest(
            text=f"Invalid network id: {network_id} length must be between 32..36 characters"
        )


# Load all the nodes and edges that belongs to each network from db
async def load_networks_with_nodes_and_edges():
    query = models.Node.outerjoin(models.Network).outerjoin(models.Edge).select()
    network_nodes_edges = await query.gino.load(
        models.Network.distinct(models.Network.id).load(
            add_node=models.Node.distinct(models.Node.id),
            add_edge=models.Edge.distinct(models.Edge.id),
        )
    ).all()
    return network_nodes_edges


# Load all the nodes and edges that belongs to each network from db
async def load_networks_with_tower_nodes(location_geo_point):
    distance = func.ST_DistanceSphere(location_geo_point, models.Node.geo_point)
    query = (
        db.select([models.Node, models.Network, distance])
        .select_from(models.Node.outerjoin(models.Network))
        .where(
            or_(
                func.ST_DistanceSphere(location_geo_point, models.Node.geo_point) / 1000
                < (models.Node.radius),
                models.Node.type == CENTER_HUB,
            )
        )
    )
    network_nodes = await query.gino.load(
        (
            models.Network.distinct(models.Network.id).load(
                add_node=models.Node.distinct(models.Node.id).load(
                    add_distance=ColumnLoader(distance)
                )
            )
        )
    ).all()
    return network_nodes
