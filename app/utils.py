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

def create_graph_by_db_data(node_list,edge_list):
    graph = nx.DiGraph()
    graph.add_nodes_from([(
        node['node_id'],
        {   "id":node['id'],
            "network_id":node['network_id'],
            "node_id":node['node_id'],
            "name":node['name'],
            "type":node['type'],
            "latitude":node['latitude'],
            "longitude":node['longitude'],
            "radius":node['radius']
        })for node in node_list])
    graph.add_edges_from(edge_list)
    return graph

def convert_network_as_respose_data(saved_network):
    network = {
        "id":str(saved_network.id),
        "network name":saved_network.name
    }
    return network

def convert_region_node_to_dict(node,tower_list):
    data = {
                    "id":node[1]['id'],
                    "node_id":node[1]['node_id'],
                    "name":node[1]['name'],
                    "type":node[1]['type'],
                    "latitude":node[1]['latitude'],
                    "longitude":node[1]['longitude'],
                    "towers":tower_list
                    }
    return data

def convert_node_to_dict(node):
    data = {
                    "id":node[1]['id'],
                    "node_id":node[1]['node_id'],
                    "name":node[1]['name'],
                    "type":node[1]['type'],
                    "latitude":node[1]['latitude'],
                    "longitude":node[1]['longitude'],
                }
    return data

def convert_network_to_dict(network,node_list):
    data = {
                    "id":network['id'],
                    "name":network['name'],
                    "nodes":node_list
                }
    return data
