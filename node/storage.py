# node/storage.py
import json, os

def save_state(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def load_state(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}
