from app import db
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID


class Network(db.Model):
    __tablename__ = "networks"

    id = db.Column(UUID(), primary_key=True)
    name = db.Column(db.Unicode(), nullable=False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._nodes = list()
        self._edges = list()

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @nodes.setter
    def add_node(self, node):
        self._nodes.append(node)

    @edges.setter
    def add_edge(self, edge):
        self._edges.append(edge)


class Node(db.Model):
    __tablename__ = "nodes"

    def __init__(self, **kw):
        super().__init__(**kw)
        self._distance = 0

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def add_distance(self, distance):
        self._distance = distance

    id = id = db.Column(UUID(), primary_key=True)
    network_id = db.Column(UUID(), db.ForeignKey("networks.id"))
    node_id = db.Column(db.Unicode(), nullable=False)
    name = db.Column(db.Unicode(), nullable=False)
    type = db.Column(db.Unicode(), nullable=False)
    latitude = db.Column(db.Float(), nullable=False)
    longitude = db.Column(db.Float(), nullable=False)
    radius = db.Column(db.Float(), nullable=True)
    geo_point = db.Column(Geometry(geometry_type="POINT"))
    parent_region_hub = db.Column(UUID(), db.ForeignKey("nodes.id"))


class Edge(db.Model):
    __tablename__ = "edges"

    id = id = db.Column(UUID(), primary_key=True)
    network_id = db.Column(UUID(), db.ForeignKey("networks.id"))
    source_node = db.Column(db.Unicode(), nullable=False)
    target_node = db.Column(db.Unicode(), nullable=False)
