import sys
import os
import json

from node.flask_api import app
from node.raft_node import RaftNode
from node.bank_node import BankNode

node_id = sys.argv[1]
config_path = os.path.join("instances", node_id, "config.json")

if not os.path.exists(config_path):
    print(f"No se encontró el archivo: {config_path}")
    sys.exit(1)

with open(config_path) as f:
    config = json.load(f)

from node import flask_api
flask_api.bank = BankNode()
flask_api.raft = RaftNode(
    node_id=config["id"],
    peers=config["peers"],
    bank=flask_api.bank
)

print(f"Iniciando nodo {node_id} en puerto {config['port']}...")
app.run(host="0.0.0.0", port=config["port"])
