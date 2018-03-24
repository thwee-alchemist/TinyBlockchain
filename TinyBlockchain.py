
# coding: utf-8

# # Building a Blockchain
# following the tutorial at [medium.com](https://medium.com/crypto-currently/lets-build-the-tiniest-blockchain-e70965a248b).

import hashlib
import json
import datetime
from flask import Flask
from flask import request
node = Flask(__name__)
from sys import argv


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()
        
    def hash_block(self):
        sha = hashlib.sha256()
        sha.update(
            str(self.index) + 
            str(self.timestamp) + 
            str(self.data) + 
            str(self.previous_hash))
        return sha.hexdigest()
    
    def __repr__(self):
        return json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        })
    
    def repr(self):
        return self.__repr__()


def create_genesis_block():
    block = Block(
        0, 
        datetime.datetime.now().isoformat(), 
        {
            'proof-of-work': 9,
            'transactions': None
        }, 
        '0'
    )
    return block


miner_address = 'miner address 1'
blockchain = [create_genesis_block()]
previous_block = blockchain[0]
transactions = []
peer_nodes = []


@node.route('/transaction', methods=['POST'])
def transaction():
    if request.method == "POST":
        transaction = request.get_json()
        transactions.append(transaction)

        print('New Transaction')
        print(json.dumps(transaction))
        
        return "Transaction submission successful.\n"

def proof_of_work(last_proof):
    incrementor = last_proof + 1
    while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
        incrementor += 1
        
    return incrementor

@node.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain[-1]
    last_proof = last_block.data['proof-of-work']
    proof = proof_of_work(last_proof)
    transactions.append(
        {"from": "network", "to": miner_address, "amount": 1}
    )
    
    mined_block = Block(
        last_block.index + 1,
        datetime.datetime.now().isoformat(),
        {
            'proof-of-work': proof,
            'transactions': list(transactions)
        },
        last_block.hash
    )
    
    blockchain.append(mined_block)
    
    transactions[:] = []
    
    return repr(mined_block) + '\n'


@node.route('/add_node', methods=['POST'])
def add_node():
    if request.method == 'POST':
        n = request.get_json()
        peer_nodes.append(n['node'])
        return "Added node \n"
    
@node.route('/blocks', methods=['GET'])
def get_blocks():
    consensus()
    
    chain_to_send = blockchain
    
    for block in chain_to_send:
        block = {
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'hash': block.hash
        }
        
        chain_to_send = json.dumps(chain_to_send)
        return chain_to_send
    
def find_new_chains():
    other_chains = []
    for node_url in peer_nodes:
        
        try:
            block = request.get(node_url + '/blocks').content
            block = json.loads(block)
            other_chains.append(block)

        except:
            peer_nodes.remove(node_url)
            print('removed ', node_url)
            
        return other_chains
    
def consensus():
    other_chains = find_new_chains()
    longest_chain = blockchain
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain
    blockchain = longest_chain


if __name__ == "__main__":
    print(argv)
    node.run(port=int(argv[1]))


# In bash: 
# 
#     curl "localhost:16001/transaction" \
#     -H "Content-Type: application/json" \
#     -d '{"from": "akjflw", "to":"fjlakdj", "amount": 3}'

# and
# 
#     curl "localhost:5000/mine"

# and 
# 
#     curl "localhost:16001/add_node" \
#     -H "Content-Type: application/json" \
#     -d '{"node": "localhost:16602"}'
