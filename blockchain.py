'''
This file contains the object representation of a Block, Block Header, Transaction and some 
helper functions similar to the Bitcoin Blockchain.
'''

from merkel_tree import Merkel_Tree
import time
import hashlib

class Block(object):
    def __init__(self):
        self.__MagicNumber = 0xD9B4BEF9
        self.__Blocksize = 0
        self.__BlockHeader = ''
        self.__TransactionCounter = 0
        self.__Transactions = []
        self.__Blockhash = '0'*64
        self.__maxtxn = 10 # In this case, each block can have max 10 transactions
    # Setters
    def setBlocksize(self,size):
        self.__Blocksize = size
    def setBlockHeader(self,header):
        self.__BlockHeader = header
    def setTransactionCounter(self,count):
        self.__TransactionCounter = count
    def addTransaction(self,transaction):
        if self.__TransactionCounter < self.__maxtxn:
            self.__Transactions.append(transaction)
            return True
        else:
            return False
    def setBlockhash(self,has):
        self.__Blockhash = has
    # Getters
    def getMagicNumber(self):
        return self.__MagicNumber
    def getBlocksize(self):
        return self.__Blocksize
    def getBlockHeader(self):
        return self.__BlockHeader
    def getTransactionCounter(self):
        return self.__TransactionCounter
    def getTransactions(self):
        return self.__Transactions
    def getBlockhash(self):
         return self.__Blockhash
    def printBlock(self):  # Custom print function (Can also use __str__)
        return "Block Transactions Merkle Root: {}. \n  Previous Block Hash: {}. \n  Block Timestamp: {}. \n The block has {} \
               transactions whose hashes are: ".format(self.__BlockHeader.gethashMerkleRoot(), self.__BlockHeader.gethashPrevBlock(), 
               self.__BlockHeader.getTimestamp(), len(self.getTransactions())) + ';'.join([tx_hash for tx_hash in self.getTransactions()])

class Header(object):
    def __init__(self):
        self.__version = 1
        self.__Nonce = 0
        self.__hashPrevBlock = '0'*64
        self.__hashMerkleRoot = '0'*64
        self.__Timestamp = 1531696808 # Just a default value which is overwritten on creation
        self.__Bits  = 0
    # Setters
    def sethashPrevBlock(self,hash_prev):
        self.__hashPrevBlock = hash_prev
    def sethashMerkleRoot(self,merkle_root):
        self.__hashMerkleRoot = merkle_root
    def setTimestamp(self,timestamp):
        self.__Timestamp = timestamp
    def setBits(self,bits):
        self.__Bits = bits
    def setNonce(self,nonce):
        self.__Nonce = nonce
    # Getters
    def getVersion(self):
        return self.__version
    def gethashPrevBlock(self):
        return self.__hashPrevBlock
    def gethashMerkleRoot(self):
        return self.__hashMerkleRoot
    def getTimestamp(self):
        return self.__Timestamp
    def getBits(self):
        return self.__Bits
    def getNonce(self):
        return self.__Nonce



class Transaction(object):
    def __init__(self):
        self.__VersionNumber = 1
        self.__InCounter = 0
        self.__OutCounter = 0
        self.__ListOfInputs = []
        self.__ListOfOutputs = []
        self.__TransactionHash = '0'*64
    # Setters
    def setVersionNumber(self,number):
        self.__VersionNumber = number
    def setInCounter(self,count):
        self.__InCounter = count
    def setListOfInputs(self,lisin):
        self.__ListOfInputs = lisin
    def setOutCounter(self,count):
        self.__OutCounter = count
    def setListOfOutputs(self,lisout):
        self.__ListOfOutputs = lisout
    def setTransactionHash(self,has):
        self.__TransactionHash = has
    # Getters
    def getVersionNumber(self):
        return self.__VersionNumber
    def getInCounter(self):
        return self.__InCounter
    def getListOfInputs(self):
        return self.__ListOfInputs
    def getOutCounter(self):
        return self.__OutCounter
    def getListOfOutputs(self):
        return self.__ListOfOutputs
    def getTransactionHash(self):
        return self.__TransactionHash
    def printTransaction(self): # Custom print function (Can also use __str__)
        return "Transaction Hash: {} \n . With Inputs: ".format(self.__TransactionHash) + \
               ';'.join([inp for inp in self.__ListOfInputs]) + '\n and Outputs: ' + ';'.join([out for out in self.__ListOfOutputs])


# Hash function that takes a string and double hashes the string


def compute_double_hash(string):
    '''
    Takes a string and returns it SHA256 double hashed.
    '''
    string = string.encode('utf-8').hex()
    string_endian = "".join(reversed([string[i:i+2] for i in range(0, len(string), 2)]))
    string_bytes = bytes.fromhex(string_endian)
    single_hash=  hashlib.sha256(string_bytes).hexdigest()
    double_hash = hashlib.sha256(bytes.fromhex(single_hash)).hexdigest()
    double_hash = "".join(reversed([double_hash[i:i+2] for i in range(0, len(double_hash), 2)]))
    return double_hash


class Output(object):
    '''
    Transaction Output representation.
    '''
    def __init__(self,value,index,script):
        self.__value = value
        self.__index = index
        self.__script = script
        self.compute_hash()
    def compute_hash(self):
        self.__outputhash = compute_double_hash(str(self.__value) + str(self.__index) + str(self.__script))
    def get_hash(self):
        return self.__outputhash

#Helper functions   
def computeTransactionHash(transaction):
    '''
    Function that computes the transaction hash for a given transaction.
    In this case, just concatenates the individual attributes and hashes them.
    '''
    concatenated = str(transaction.getVersionNumber()) + str(transaction.getInCounter()) + \
                   ''.join([tx for tx in transaction.getListOfInputs()]) + str(transaction.getOutCounter()) + \
                   ''.join([tx for tx in transaction.getListOfOutputs()])
    concatenated = concatenated.encode('utf-8').hex() # Convert to hex string because Merkel Tree handles hex strings in hash
    return compute_double_hash(concatenated)

def computeHeaderHash(header):
    '''
    Function that computes the header hash for a block.
    In this case, just concatenats the individual attributes and hashes them.
    '''
    concatenated = str(header.getTimestamp()) + str(header.gethashMerkleRoot()) + str(header.getBits()) + \
                   str(header.getNonce()) + str(header.gethashPrevBlock())
    concatenated = concatenated.encode('utf-8').hex() # Convert to hex string because Merkel Tree handles hex strings in hash
    return compute_double_hash(concatenated)
