# node/api.py
from flask import Flask, request, jsonify
from .raft_node import RaftNode, load_config 
from .bank_node import BankNode

app = Flask(__name__)
bank = None
raft = None

@app.route("/status", methods=["GET"])
def status():
    return jsonify(raft.get_status())

@app.route("/balance", methods=["GET"])
def balance():
    return jsonify(bank.get_balances())

@app.route("/deposit", methods=["POST"])
def deposit():
    data = request.get_json()
    op = {"type": "deposit", "account": data["account"], "amount": data["amount"]}

    if raft.role != "leader":
        return jsonify({"error": "not_leader", "leader": raft.leader_id}), 403

    if raft.replicate_operation(op):
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "replication_failed"}), 500

@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.get_json()
    op = {"type": "transfer", "from": data["from"], "to": data["to"], "amount": data["amount"]}

    if raft.role != "leader":
        return jsonify({"error": "not_leader", "leader": raft.leader_id}), 403

    if raft.replicate_operation(op):
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "replication_failed"}), 500

@app.route("/replicate", methods=["POST"])
def replicate():
    data = request.get_json()
    op = data["op"]
    term = data["term"]

    return jsonify(raft.append_entry(op, term))

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json()
    raft.receive_heartbeat(data["term"], data["leader_id"])
    return jsonify({"success": True})

@app.route("/vote", methods=["POST"])
def vote():
    data = request.get_json()
    granted = raft.receive_vote_request(data["term"], data["candidate_id"])
    return jsonify({"vote_granted": granted})
