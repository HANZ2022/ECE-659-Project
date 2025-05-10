from tinydb import TinyDB, Query
from datetime import datetime
import os

db = TinyDB(f"data/experiment.json")
nodes_table = db.table("iot_nodes")

class IoTNodeData:

    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 0

    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items()
            if not callable(v) and not k.startswith('_')
        }
    
    @classmethod
    def from_dict(cls, document):
        res = cls()
        for k, v in document.items():
            setattr(res, k, v)
        return res
    
    def update_db(self):
        Node = Query()
        if nodes_table.get(Node.port == self.port):
            nodes_table.update(self.to_dict(), Node.port == self.port)
        else:
            nodes_table.insert(self.to_dict())

def get_available_nodes():
    return [IoTNodeData.from_dict(d) for d in nodes_table.all()]
