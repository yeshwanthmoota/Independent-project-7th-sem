from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import time
import requests
from urllib.parse import urlparse
import json
from Blockchain import *



# Creating a Web app

app = Flask(__name__)
app.secret_key = "6b8aff760b701265494ae0d98a5058fa"

node_address = "Person 5001"
blockchain = Blockchain() # Creating a Blockchain
# blockchain.add_node("http://127.0.0.1:5000/")



# Get the Full Blockchain
@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


    
@app.route("/get_blockchain", methods = ["GET"])
def get_blockchain():
    # blockchain.update_chain()
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response), 200 # 200 is the http code for success.

@app.route("/get_transactions", methods = ["GET"])
def get_transactions():
    response = {
        'transactions': blockchain.transactions
    }
    return jsonify(response), 200 # 200 is the http code for success.



# Mining a new Block

@app.route("/mine_block", methods = ["GET"])
def mine_block():
    # previous_proof = previous_block["proof"]
    start_time = time.time()    
    # proof = blockchain.POW(previous_proof=previous_proof)
    blockchain.add_transaction({
            "sender": "Coinbase", 
            "reciever": node_address, 
            "amount": 50
            })
    block = blockchain.POW()
    end_time = time.time()
    time_taken = end_time - start_time
    response = {
            'message': 'Congratulations! You just mined a block!',
            'index': block['index'],
            'timestamp': block['timestamp'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'hash': block['hash'],
            'time taken to mine the block(in seconds)': time_taken,
            "transactions": block["transactions"]
        }
    blockchain.update_chain()
    return jsonify(response), 200 # 200 is the http code for success.



# Checking if the chain is valid
@app.route("/is_valid", methods = ["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        return "<h1>The Chain is VALID All good to go</h1>"
    else:
        return "<h1>The Chain is NOT VALID</h1>"



@app.route("/update_transactions", methods = ["GET", "POST"])
def update_transactions():
    if request.method == "POST":
        updated_transactions = request.get_json(force=True)
        print(updated_transactions)
    

        if blockchain.transactions == updated_transactions:
            flash("Mempool updated!", category="success")
            return redirect(url_for("home")) # break
        blockchain.transactions = updated_transactions # else


    return redirect(url_for("get_transactions"))
        



# Adding a new transaction
@app.route("/add_new_transaction", methods = ["GET", "POST"])
def add_new_transaction():
    if request.method == "GET":
        return render_template("new_transaction.html")
    else: # request.method is "POST"
        """Transmit this new transaction to all the nodes""" # WORK TO DO HERE
        sender = request.form["sender"]
        reciever = request.form["reciever"]
        amount = request.form["amount"]
        # Checking if any field in the form was empty
        if sender == "" or reciever == "" or amount == 0:
            flash("Required Fields not filled", category="danger")
            return redirect(url_for("add_new_transaction"))
        else:
            json_obj = {
                "sender": sender,
                "reciever": reciever,
                "amount": amount
            }
            blockchain.add_transaction(json_obj)
            for node in blockchain.nodes:
                post_data = json.dumps(blockchain.transactions)
                response = requests.post(f"http://{node}/update_transactions", data=post_data)
                if response.status_code == 200:
                    flash("Transaction added to Mempool!", category="success")
                elif response.status_code == 400:
                    flash("Transactions Failed!", category="danger")
            return redirect(url_for("get_transactions"))




# Part - 3 Decentralizing the Blockchain

# connecting new nodes to the network
@app.route("/connect_node", methods = ["GET", "POST"])
def connect_node():
    if request.method == "GET":
        return render_template("new_node.html")
    else:
        nodes = request.form["node_addresses"]
        nodes = nodes.split(",")
        if nodes is None:
            return "No nodes to connect", 400
        else:
            for node in nodes:
                blockchain.add_node(node)
            response = {
                "message": "All the nodes are successfully connected to the network. The following nodes are present in the Bitcoin Blockchain Network:",
                "nodes": list(blockchain.nodes)
                }
            return jsonify(response), 200

# Updating the chain by the longest chain if necessary
@app.route("/update_chain", methods = ["GET"])
def update_chain():
    blockchain.update_chain()
    # flash("Chain Updated", category="success")
    return "<h1>The Chain is Updated, All good to go!</h1>"
    


# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


