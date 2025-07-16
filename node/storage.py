import json
import os

def save_state(filename, state):
    with open(filename, "w") as f:
        json.dump(state, f)

def load_state(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return {}

def save_log(filename, log):
    with open(filename, "w") as f:
        json.dump(log, f)

def load_log(filename):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(path):
        print("ENCONTRADO", path)
        with open(path) as f:
            return json.load(f)
    print("NO ENCONTRADO", path)
    return []

