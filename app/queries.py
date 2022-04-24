from asyncio import constants
from unicodedata import name
from psycopg2 import DataError
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID, insert
from numpy import ediff1d
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from sqlalchemy import and_, func
from app.models import models
from app import db
from geoalchemy2 import func
from .constants import (
    CENTER_HUB,
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
    convert_region_node_to_dict,
    convert_node_to_dict,
    convert_network_to_dict,
    convert_tower_data_to_dict,
    coverage_network_sorting_criteria
    )


async def add_new_network(graph):
    network_id = generate_id()
    
    for node in graph.nodes(data=True):
        new_node_id = generate_id()
        point = create_point(node[1][LONGITUDE],node[1][LATITUDE])

        if(node[1][TYPE] == TOWER):
            continue
        if(node[1][TYPE] == CENTER_HUB):
            network_name = node[1][NAME].split("-")[0]
            new_network = models.Network(
                id = network_id,
                name = network_name
                )
            await new_network.create()

        if(node[1][TYPE] == REGION_HUB):
            new_region_node = models.Node(
                     id = new_node_id,
                     network_id = network_id,
                     node_id = node[0],
                     name = node[1][NAME],
                     type = node[1][TYPE],
                     latitude = node[1][LATITUDE],
                     longitude = node[1][LONGITUDE],
                     geo_point = point
                   )
            await new_region_node.create()

            tower_list = list(nx.neighbors(graph,node[0]))
            if(tower_list):
                for node_id in tower_list:
                    tower_node = [node for node in graph.nodes(data=True) if node[0] == node_id]
                    tower_point = create_point(tower_node[0][1][LONGITUDE],tower_node[0][1][LATITUDE])
                    new_tower_node = models.Node(
                     id = generate_id(),
                     network_id = network_id,
                     node_id = tower_node[0][0],
                     name = tower_node[0][1][NAME],
                     type = tower_node[0][1][TYPE],
                     radius = tower_node[0][1][RADIUS],
                     latitude = tower_node[0][1][LATITUDE],
                     longitude = tower_node[0][1][LONGITUDE],
                     geo_point = tower_point,
                     parent_region_hub = new_node_id
                   )
                    await new_tower_node.create()
        else:
             new_center_node = models.Node(
                     id = new_node_id,
                     network_id = network_id,
                     node_id = node[0],
                     name = node[1][NAME],
                     type = node[1][TYPE],
                     latitude = node[1][LATITUDE],
                     longitude = node[1][LONGITUDE],
                     geo_point = point
                   )
             await new_center_node.create()


    for edge in graph.edges(data=True):
        
        new_edge = models.Edge(
            id =  generate_id(),
            network_id = network_id,
            source_node = edge[0],
            target_node = edge[1]
        )
        await new_edge.create()

        # point = create_point(node[1]['longitude'],node[1]['latitude'])
        # new_node = models.Node(
        #     id = generate_id(),
        #     network_id = network_id,
        #     node_id = node[0],
        #     name = node[1]['name'],
        #     type = node[1]['type'],
        #     latitude = node[1]['latitude'],
        #     longitude = node[1]['longitude'],
        #     geo_point = point
        # )
        # # await new_node.create()
        
        # # print(node)
        # print(node[0],end="")
        # print(list(nx.neighbors(graph,node[0])))
    return new_network

async def get_network_list_with_details(limit):
    network_list = await get_network_list()
    response_network_list = []
    for network in network_list:
        node_list = await get_node_list(network)
        edge_list = await  models.Edge.select("source_node","target_node").where(models.Edge.network_id == network['id']).gino.all()

        graph = create_graph_by_db_data(node_list,edge_list)
        
        node_data_list = []
        for node in graph.nodes(data=True):
            towers = []
            if(node[1]['type'] == "Region Hub"):
                
                neighbors_list = list(graph.neighbors(node[0]))
                for neighbor in neighbors_list:
                    
                    tower = list(filter(lambda x:x[1]['node_id'] == neighbor,graph.nodes(data=True)))
                    towers.append(tower[0][1])
                
                data = convert_region_node_to_dict(node,towers)
                
                node_data_list.append(data)
            elif(node[1]['type'] == "Center Hub") :
                
                data = convert_node_to_dict(node)
                
                node_data_list.append(data)
        network_details = convert_network_to_dict(network,node_data_list)
        response_network_list.append(network_details)
    return response_network_list
        
            
            

    # for d in node_data_list:
    #     print("_____________________________________________")
    #     print(d)



        # center_hub_list = []
        # region_hub_list = []
        # tower_list = []
        
        # for node in node_list:
        #     if(node.type == "Center Hub"):
        #         center_hub_list.append(node)
        #     elif(node.type == "Tower"):
        #         tower_list.append(node)
       
        # for node in tower_list:
        #     # towers = list(filter(lambda x: x.parent.id == node.parent.id , tower_list))
        #     data = {
        #         "id":node.parent.id,
        #         "name":node.parent.name,
        #         "towers":[tower.to_dict() for tower in list(filter(lambda x: x.parent.id == node.parent.id , tower_list)) ]
        #     }
        #     region_hub_list.append(data)
        # print(region_hub_list)


        # response_data = {
        #     "network_id":network['id'],
        #     "network_name":network['name'],
        #     "center_Hub":center_hub_list
        #     ""
        # }
        
   
    
async def get_network_list():
    network_object_list = await models.Network.query.gino.all()
    print("TOWER",network_object_list)
    network_list = [network.to_dict() for network in network_object_list]
    return network_list

async def get_node_list(network):
    print("CAME")
#     Parent = models.Node.alias()
#     parents = db.select([models.Node.parent_region_hub])
#     query = models.Node.load(parent=Parent.on(
#     models.Node.parent_region_hub == Parent.id
# ))
# .where(
#      and_(
#     models.Node.type == "Center Hub",
#     models.Node.type == "Tower"
#      )
# )
    # async for c in query.gino.iterate():
    #     print(f'Leaf: {c.id}, Parent: {c.parent.id}')
    # query = (
    #     models.Node.outerjoin(models.Node).select().where(models.Node.network_id == network['id'])
    # )
    # node_object_list = await query.gino.all()
    # print(node_object_list[1].id)
    # print(node_object_list[2].parent.type)
    # node_list = []
    # for node in node_object_list:
    #     if(node.type == "Center Hub" or node.type == "Tower"):
    #         node_list.append(node)
    
    node_list = await models.Node.select(
        'id',
        'network_id',
        'node_id',
        'name',
        'type',
        'latitude',
        'longitude',
        'radius',
    ).where(models.Node.network_id == network.id).gino.all()
    print(node_list)
    return node_list

async def get_network_coverage_details(latitude,longitude):
    location_geo_point = create_point(latitude,longitude)   
    network_list = await get_network_list()
    coverage_network_list = []
    for network in network_list:
        tower_list = await get_tower_list(network,location_geo_point)
        if tower_list:
            tower_list_dict = [convert_tower_data_to_dict(tower) for tower in tower_list]
            coverage_network = convert_network_to_dict(network,tower_list_dict)   
            coverage_network_list.append(coverage_network)
    return sorted(coverage_network_list, key=lambda tower: (len(tower['nodes']), tower),reverse=True)         
                            #    list(filter(lambda x:x[1]['node_id'] == neighbor,graph.nodes(data=True)))
        
        # list(filter(lambda x: (func.ST_DistanceSphere(x.geo_point,location_geo_point ) < x.radius),all_towers_in_network))

        # for tower in all_towers_in_network:
        #     distance = func.ST_DistanceSphere(tower.geo_point,location_geo_point)
        #     print("DISTANCE",distance)

    # data_points =  await models.Node.query.where(
    #     func.ST_DistanceSphere(
    #     models.Node.geo_point,
    #     location_geo_point
    # ) <= (models.Node.radius)).gino.all()
    # print(data_points)
    # .gino.all()
        
async def get_tower_list(network,location_geo_point):
    query = (models.Node.select(
        'id',
        'network_id',
        'node_id',
        'name',
        'type',
        'latitude',
        'longitude',
        'radius',
        'geo_point'
    ).where(
       and_(
        models.Node.network_id == network['id'],
        models.Node.type == "Tower",
        func.ST_DistanceSphere(models.Node.geo_point,location_geo_point) < (models.Node.radius)
        )))
    tower_list = await query.gino.all()
    return tower_list 

async def calculate_total_cost(network_id,cost_details):
    network = await get_network_from_db(network_id)

    if(network is None):
            raise HTTPNotFound(text=f"Network not found for network id:{network_id}")
    node_list = await get_node_list(network)
    edge_list = await  models.Edge.select("source_node","target_node").where(models.Edge.network_id == network.id).gino.all()
    # print(node_list)

    if node_list is None or edge_list is None:
        raise HTTPNotFound(text=f"Network nodes or edges not found for network id:{network_id}")

    graph = create_graph_by_db_data(node_list,edge_list)
    print("LENGTH",len(list(filter(lambda node:node.type == 'Region Hub',node_list))))
    center_hub_total_cost = len(list(filter(lambda node:node.type == 'Center Hub',node_list))) * cost_details['Center Hub']['cost']
    region_hub_total_cost = len(list(filter(lambda node:node.type == 'Region Hub',node_list))) * cost_details['Region Hub']['cost']
    tower_total_cost = len(list(filter(lambda node:node.type == 'Tower',node_list))) * cost_details['Tower']['cost']
    center_region_total_cost = 0
    region_tower_total_cost = 0
    for edge in graph.edges(data=True):
        source_node = list(filter(lambda node:node[0] == edge[0],graph.nodes(data=True)))
        target_node = list(filter(lambda node:node[0] == edge[1],graph.nodes(data=True)))

        print("SOURCE",source_node[0][1]['type'])
        print("TARGET",target_node)
            
        if(source_node[0][1]['type'] == "Center Hub" and target_node[0][1]['type'] == "Region Hub"):
            center_region_total_cost += cost_details['Cables']['Center-Region']["cost"]
        elif(source_node[0][1]['type'] == "Region Hub" and target_node[0][1]['type'] == "Tower"):
            region_tower_total_cost += cost_details['Cables']['Region-Tower']["cost"]
    total_cost = center_region_total_cost + region_tower_total_cost + center_hub_total_cost + region_hub_total_cost + tower_total_cost
    return total_cost

async def get_network_from_db(network_id):
    try:
        network = await models.Network.get(network_id)

        return network

    #TODO: find the exception type and put
    except DataError:
        raise HTTPBadRequest(text=f"Invalid network id: {network_id} length must be between 32..36 characters")
