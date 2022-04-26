from app import db
from geoalchemy2 import Geometry
import gino
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID, insert


class Network(db.Model):
    __tablename__ = "networks"

    id = db.Column(UUID(),primary_key=True)
    name = db.Column(db.Unicode(),nullable=False)

class Node(db.Model):
    __tablename__ = "nodes"

    id = id = db.Column(UUID(),primary_key=True)
    network_id = db.Column(UUID(),db.ForeignKey('networks.id'))   
    node_id = db.Column(db.Unicode(),nullable=False)
    name = db.Column(db.Unicode(),nullable=False)
    type = db.Column(db.Unicode(),nullable=False)
    latitude = db.Column(db.Float(),nullable=False)
    longitude = db.Column(db.Float(),nullable=False)
    radius = db.Column(db.Float(),nullable=True)
    geo_point = db.Column(Geometry(geometry_type="POINT"))
    parent_region_hub = db.Column(UUID(),db.ForeignKey('nodes.id'))
        
class Edge(db.Model):
    __tablename__ = "edges"

    id = id = db.Column(UUID(),primary_key=True)
    network_id = db.Column(UUID(),db.ForeignKey('networks.id')) 
    source_node = db.Column(db.Unicode(),nullable=False) 
    target_node = db.Column(db.Unicode(),nullable=False) 