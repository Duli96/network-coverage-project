import imp
import json
import networkx as nx
import uuid

def generate_id():
    return uuid.uuid4()

def create_point(longitude,latitude):
   
    point = 'POINT({} {})'.format(longitude,latitude)
    return point

def create_graph_by_graphml(content):
    graph = nx.parse_graphml(content)
    # for node in graph.nodes(data=True):
    #     print(node)

    # for edge in graph.edges(data=True):
    #     print(edge)
    print(nx.is_directed(graph))
    return graph

def convert_network_as_respose_data(saved_network):
    network = {
        "id":str(saved_network.id),
        "network name":saved_network.name
    }
    return network