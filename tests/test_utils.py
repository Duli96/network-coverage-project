from pathlib import Path
from platform import node
from uuid import UUID
import uuid
import pytest
from app.utils import (
    generate_id,
    create_point,
    create_graph_by_graphml,
    create_graph_by_db_data,
    convert_tower_data_to_dict,
)


resources = Path(__file__).parent


def test_generate_id():
    response = generate_id()
    assert uuid.UUID(response.hex).version == 4


def test_create_point():
    longitude = -2.3302296
    latitude = 52.8008717
    response = create_point(longitude, latitude)
    assert response == "POINT(-2.3302296 52.8008717)"


def test_create_graph_by_graphml(graph_one):
    content = open(resources / "test_data/data-1.graphml", "r")
    response = create_graph_by_graphml(content.read())
    assert response.nodes == graph_one.nodes
    assert response.edges == graph_one.edges


# def test_create_graph_by_db_data(graph_two,test_node_list,test_edge_list):
#     pass
#     node_list = test_node_list
#     edge_list = [edge for edge in graph_two.edges]

#     response = create_graph_by_db_data(node_list,edge_list)

#     print("--------------------------------",graph_two.edges (data=True))
#     assert response.nodes(data=False) == graph_two.nodes(data=False)
#     assert response.edges == graph_two.edges


def test_convert_tower_to_dict(test_tower_data):
    test_data = {
        "id": "c8b60c12-94c7-4243-a74f-c6ced3b16841",
        "node_id": "R4T1",
        "name": "B-R4T1",
        "type": "Tower",
        "latitude": 52.8008717,
        "longitude": -2.3302296,
        "radius": 15,
    }
    response = convert_tower_data_to_dict(test_tower_data)
    assert response == test_data
