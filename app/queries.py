from asyncio import constants
from unicodedata import name
from numpy import ediff1d

from sqlalchemy import and_
from app.models import models
from app import db
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
    convert_network_to_dict
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
    network_list = await get_network_list(limit)
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
        
   
    
async def get_network_list(limit):
    network_object_list = await models.Network.query.limit(limit).gino.all()
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
    ).where(models.Node.network_id == network['id']).gino.all()
    print(node_list)
    return node_list

    
   

