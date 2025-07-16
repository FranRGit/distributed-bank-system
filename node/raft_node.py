# node/raft_node.py
import threading
import time
import random
import requests
import json
import os

def load_config():
    with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
        return json.load(f)


class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers  # Lista de URLs de los otros nodos
        self.role = "follower"
        self.current_term = 1
        self.voted_for = None
        self.leader_id = None
        self.last_heartbeat = time.time()
        self.election_in_progress = False
        self.lock = threading.Lock()

        # Cargar configuración desde JSON
        config = load_config()
        self.heartbeat_interval = config["heartbeat_interval"]
        self.election_timeout_min = config["election_timeout_min"]
        self.election_timeout_max = config["election_timeout_max"]
        self.request_timeout = config["request_timeout"]

        self.reset_election_timeout()

        threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        threading.Thread(target=self.election_timeout_checker, daemon=True).start()

    def reset_election_timeout(self):
        self.timeout = random.uniform(self.election_timeout_min, self.election_timeout_max)
        self.last_heartbeat = time.time()
        print(f"[{self.node_id}] Timeout reiniciado a {self.timeout:.2f} segundos")

    def heartbeat_loop(self):
        while True:
            if self.role == "leader":
                for peer in self.peers:
                    try:
                        requests.post(f"{peer}/heartbeat", json={
                            "term": self.current_term,
                            "leader_id": self.node_id
                        }, timeout=self.request_timeout)
                    except:
                        pass
            time.sleep(self.heartbeat_interval)

    def election_timeout_checker(self):
        while True:
            if self.role != "leader":
                elapsed = time.time() - self.last_heartbeat
                if elapsed >= self.timeout:
                    self.start_election()
                else:
                    time.sleep(0.05)
            else:
                time.sleep(0.1)

    def start_election(self):
        with self.lock:
            if self.election_in_progress:
                return
            self.election_in_progress = True

            self.role = "candidate"
            self.current_term += 1
            self.voted_for = self.node_id
            self.reset_election_timeout()

            print(f"[{self.node_id}] Iniciando elección en término {self.current_term}")
            votes = 1  # Voto a sí mismo
            majority = (len(self.peers) + 1) // 2 + 1

            for peer in self.peers:
                try:
                    response = requests.post(f"{peer}/vote", json={
                        "term": self.current_term,
                        "candidate_id": self.node_id
                    }, timeout=self.request_timeout)
                    if response.json().get("vote_granted"):
                        votes += 1
                except:
                    pass

            if votes >= majority:
                self.role = "leader"
                self.leader_id = self.node_id
                print(f"[{self.node_id}] Elegido líder con {votes} votos")
            else:
                print(f"[{self.node_id}] Elección fallida con {votes} votos")

            self.election_in_progress = False
            self.reset_election_timeout()

    def receive_heartbeat(self, term, leader_id):
        with self.lock:
            if term >= self.current_term:
                if self.role != "follower":
                    print(f"[{self.node_id}] Cambiando a follower por heartbeat")
                self.role = "follower"
                self.current_term = term
                self.voted_for = None
                self.leader_id = leader_id
                self.election_in_progress = False
                self.reset_election_timeout()
                print(f"[{self.node_id}] Heartbeat recibido de {leader_id} en término {term}")
            return True

    def receive_vote_request(self, term, candidate_id):
        with self.lock:
            vote_granted = False
            if term > self.current_term:
                self.current_term = term
                self.voted_for = candidate_id
                vote_granted = True
            elif term == self.current_term:
                if self.voted_for is None or self.voted_for == candidate_id:
                    vote_granted = True

            if vote_granted:
                self.reset_election_timeout()
                self.role = "follower"
                self.leader_id = None
                print(f"[{self.node_id}] Voto concedido a {candidate_id} en término {term}")
            return vote_granted

    def get_status(self):
        return {
            "node_id": self.node_id,
            "role": self.role,
            "term": self.current_term,
            "leader_id": self.leader_id
        }
