import networkx as nx
import uuid

# Generate a unique UUID
def generate_id():
    return uuid.uuid4()


# Create point of a location using longitude and latitude
def create_point(longitude, latitude):
    point = 'POINT({} {})'.format(longitude, latitude)
    return point


# Create a graph by parsing graphml content
def create_graph_by_graphml(content):
    graph = nx.parse_graphml(content)
    return graph


# Create a networkx graph using the db data
def create_graph_by_db_data(node_list, edge_list):
    print("MYNODE",node_list)
    graph = nx.DiGraph()
    graph.add_nodes_from([(
        node['node_id'],
        {"id": node['id'],
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


# create dict for tower dat
def convert_tower_data_to_dict(tower):
    data = {
        "id": tower.id,
        "node_id": tower.node_id,
        "name": tower.name,
        "type": tower.type,
        "latitude": tower.latitude,
        "longitude": tower.longitude,
        "radius": tower.radius
    }
    return data
