# node/api.py
from flask import Flask, request, jsonify
from .raft_node import RaftNode
from .bank_node import BankNode
from .storage import save_state, load_state

app = Flask(__name__)
raft = RaftNode(None, [])
bank = BankNode()

@app.route("/status", methods=["GET"])
def status():
    return jsonify(raft.get_status())

@app.route("/balance", methods=["GET"])
def balance():
    return jsonify(bank.get_balances())

@app.route("/deposit", methods=["POST"])
def deposit():
    data = request.get_json()
    account = data.get("account")
    amount = data.get("amount")
    new_balance = bank.deposit(account, amount)
    save_state("state.json", bank.get_balances())
    return jsonify({account: new_balance})

@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.get_json()
    success = bank.transfer(data["from"], data["to"], data["amount"])
    save_state("state.json", bank.get_balances())
    return jsonify({"success": success, "balances": bank.get_balances()})

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
