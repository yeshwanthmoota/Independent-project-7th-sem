
import hashlib
import datetime
from urllib.parse import urlparse
import requests


class Blockchain():

    def __init__(self):
        self.chain = [] # initialize an empty Blockchain
        self.transactions = []
        self.nodes = set() # empty set of nodes
        self.prefix_zeros = 5
        """prefix zeros represents mining difficulty """
        print("Hello World!")

        self.add_transaction({
            "sender": "Coinbase", 
            "reciever": "0284bb853a649751efbca489e6132b12", 
            "amount": 50
            })
        self.POW(previous_hash="0") # Genesis Block



    def hasher(self, block, nonce=None): 
        if nonce != None:
            return hashlib.sha256( ( str(block["index"]) + str(block["previous_hash"]) + str(block["transactions"]) + str(nonce) ).encode() ).hexdigest()
        else:
            return hashlib.sha256( ( str(block["index"]) + str(block["previous_hash"]) + str(block["transactions"]) + str(block["proof"]) ).encode() ).hexdigest()
            
     


    def create_block(self, previous_hash=None):
        """ Here the proof is the 'nonce' value associated with each block in the blockchain which change the value of the block's hash
            so that the block's hash is less than or equal to the target hash. set to 0 initially POW() changes it accordingly """
        # index of the block, timestamp of creation of the block, proof found when mining the block, previous hash
        if previous_hash == None:
            temp = self.get_previous_block()
            previous_hash = temp['hash']
            index = temp["index"] + 1
        else:
            index = 0
        block = {
            'index': index,
            'timestamp': str(datetime.datetime.now()),
            'proof': 0,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        return block # we want to display the information(the keys here) about this block in postman


        
    def get_previous_block(self):
        return self.chain[-1]



    def POW(self, previous_hash=None): 

        """ Proof Of Work (POW) function creates the Puzzle that the miners need to solve to gain reward"""

        # if (len(self.chain)) % 3 == 0: # increasing the difficulty of the network every 3 blocks(3 is just for testing in bitcoin it is 2016 blocks)
        #     self.prefix_zeros += 1

        nonce = 0
        block = self.create_block(previous_hash=previous_hash)
        condition = False
        while(not condition):
            block["proof"] = nonce
            hash_operation = self.hasher(block)
            if hash_operation[:self.prefix_zeros] == self.prefix_zeros*"0": # Found the acceptable nonce value
                condition = True
            else:
                nonce +=1
        block["timestamp"] = str(datetime.datetime.now())
        block["hash"] = self.hasher(block)
        self.chain.append(block)
        return block
        

    
    def is_chain_valid(self, chain):
        previous_block = chain[0] # Genesis Block
        block_index = 1
        checker = self.prefix_zeros * "0"
        while block_index < len(chain):
            current_block = chain[block_index]
            if current_block['previous_hash'] != previous_block['hash']:
                print("Test1 failed")
                return False

            hash_operation = current_block["hash"]

            if hash_operation[:self.prefix_zeros] != checker:
                print("Test2 failed")
                return False
            previous_block = current_block
            block_index += 1
        return True
            


    def add_transaction(self, json_obj): # WORK TO DO HERE TO UPDATE ALL NODES WITH MEMPOOL
        # Send post requests to all the nodes in the network

        self.transactions.append({
            "sender": json_obj["sender"], 
            "reciever": json_obj["reciever"],
            "amount": json_obj["amount"]
        })

    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def update_chain(self):
        longest_chain = self.chain
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f"http://{node}/get_blockchain")
            if response.status_code == 200:
                dict1 = response.json()
                length = dict1["length"]
                chain = dict1["chain"]
                if (length > max_length) and self.is_chain_valid(chain): # Also checking if the chain of the node we got using get request is a valid chain
                    print("HERE INSIDE" + "------------------5--------------") ### 5
                    print("\n")
                    max_length = length
                    longest_chain = chain
        self.chain = longest_chain # Updating the chain