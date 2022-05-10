from pathlib import Path
import uuid
from app.utils import (
    generate_id,
    create_point,
    create_graph_by_graphml,
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


def test_convert_tower_to_dict(test_tower_data):
    test_data = {
        "id": "c8b60c12-94c7-4243-a74f-c6ced3b16841",
        "node_id": "R4T1",
        "name": "B-R4T1",
        "type": "Tower",
        "latitude": 52.8008717,
        "longitude": -2.3302296,
        "radius": 15,
        "distance": 24.33,
    }
    response = convert_tower_data_to_dict(test_tower_data)
    assert response == test_data
