from asyncio import constants
from unicodedata import name
from app.models import models
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
    create_point
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

    
   

