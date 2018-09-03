'''
Code for Merkel Tree
'''

import hashlib
import math

class Merkel_Tree():
    def __init__(self,transactions):
        self.transactions = transactions
        self.dict = dict() # Dictionary to have hash as key and value as tuple (depth, branch no)
        self.minimal_set = [] # Minimal set of hashes to verify

    def construct_tree(self):
        '''
        Builds the Merkel Tree
        '''
        self.depth = math.ceil(math.log(len(self.transactions),2))
        while len(self.transactions)!=1:
            if len(self.transactions)%2!=0:
                self.transactions.append(self.transactions[-1])
            self.tx_pairs = list(zip(self.transactions[::2],self.transactions[1::2]))
            self.transactions = self.compute_one_level(self.tx_pairs,self.depth)
            self.depth-=1
        self.merkelroot = self.transactions[0]
        return  

    def return_parent_hash(self,left_child,right_child):
        '''Takes in 2 child nodes and returns the parent hash'''
        left_endian = "".join(reversed([left_child[i:i+2] for i in range(0, len(left_child), 2)]))
        right_endian = "".join(reversed([right_child[i:i+2] for i in range(0, len(right_child), 2)]))
        combined = left_endian + right_endian
        combined_bytes = bytes.fromhex(combined)
        single_hash=  hashlib.sha256(combined_bytes).hexdigest()
        double_hash = hashlib.sha256(bytes.fromhex(single_hash)).hexdigest()
        double_hash = "".join(reversed([double_hash[i:i+2] for i in range(0, len(double_hash), 2)]))
        return double_hash

    def compute_one_level(self, transaction_pairs, depth):
        '''Computes 1 level in the Merkel Tree'''
        start = 0
        parents = []
        for pair in transaction_pairs:
            start+=1
            self.dict[pair[0]] = (depth, start)
            start+=1
            self.dict[pair[1]] = (depth, start)
            parent = self.return_parent_hash(pair[0],pair[1])
            parents.append(parent)
        return parents

    def get_sister_and_parent(self,hash_value):
        '''Computes the sister hash value and the parent branch value'''
        child_branches = [0,0]
        location = ''
        for key in self.dict:
            if key == hash_value:
                if self.dict[key][1]%2==0: # Sister is left sibling
                    child_branches[0] = self.dict[key][1] - 1
                    child_branches[1] = self.dict[key][1]
                    sister_value = (self.dict[key][0],self.dict[key][1]-1)  # Value of sister hash in dictionary
                    location = 'left'
                else: # Sister is right sibling
                    child_branches[0] = self.dict[key][1]
                    child_branches[1] = self.dict[key][1] + 1
                    sister_value = (self.dict[key][0],self.dict[key][1]+1)
                    location = 'right'
        for key in self.dict:
            if self.dict[key] ==sister_value:
                sister_hash = key
        return (sister_hash, child_branches[1]//2, location)

    def compute_all_required_hashes(self,hash_value):
        '''Stores the minimal set of required hashes to verify if the given hash exists
        in the merkel tree using recursion. '''
        depth = self.dict[hash_value][0]
        sister,parent,location = self.get_sister_and_parent(hash_value)
        self.minimal_set.append((sister,location))
        for key in self.dict:
            if self.dict[key] == (depth-1,parent):
                parent_hash = key
        if depth != 1:
            self.compute_all_required_hashes(parent_hash)

    def get_all_required_hashes(self):
        '''Returns the minimal set of required hashes.'''
        self.minimal_set.append(self.merkelroot) # Add the merkel root to the minimal set for verification
        return self.minimal_set

    def reset_minimal_set(self):
        '''Resets the minimal test to check for another hash'''
        self.minimal_set = []

    def set_minimal_set(self,minimal_hashes):
        '''Sets the minimal set of hashes to verify an hash'''
        self.minimal_set = minimal_hashes


    def check_existence(self,target_hash):
        '''Checks the existence of a hash in the merkel tree'''
        current_hash = target_hash
        for i in range(len(self.minimal_set)-1): # Subtract 1 because we don't want to check merkel root yet
            sha_hash,location = self.minimal_set[i]
            if location =='left': # The given hash is a left sibing
                parent_hash = self.return_parent_hash(sha_hash,current_hash)
            else: # The given hash is a right sibling
                parent_hash = self.return_parent_hash(current_hash, sha_hash)
            current_hash = parent_hash # The parent hash becomes the next current hash
        if current_hash == self.merkelroot: # Check with the actual merkel root
            print("Hash present in the tree")
        else:
            print("Hash not present in the tree")
        return 
