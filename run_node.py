import sys
import os
import json


from node.flask_api import app, raft, bank


node_id = sys.argv[1]
config_path = os.path.join("instances", node_id, "config.json")

if not os.path.exists(config_path):
    print(f"No se encontró el archivo: {config_path}")
    sys.exit(1)

with open(config_path) as f:
    config = json.load(f)

raft.node_id = config["id"]
raft.peers = config["peers"]
bank.accounts = {"A": 1000, "B": 1000} 

print(f"Iniciando nodo {node_id} en puerto {config['port']}...")
app.run(host="0.0.0.0", port=config["port"])
