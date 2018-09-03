import grpc
from concurrent import futures
import time
import threading
import random
import blockchain
from merkel_tree import Merkel_Tree
import socket

# import the generated classes
import full_node_pb2
import full_node_pb2_grpc

peers = [] # List of peers this node knows about

TxnMemoryPool  = [] # Transaction Memory Pool
Blockchain = []
mine_lock = True # The full node only mines when this lock is True. Useful to have the node sleep when a new block is mined.
generate_tx = True # Transaction generator thread generates transactions only if this this True
node_ip = socket.gethostbyname(socket.gethostname())  # The IP address of the node


# create a class to define the server functions, derived from
# full_node_pb2_grpc.CommunicatorServicer
class CommunicatorServicer(full_node_pb2_grpc.CommunicatorServicer):
        def handshake(self, request, context):
            global peers
            addrMe = request.addrMe
            if addrMe not in peers:
                peers.append(request.addrMe)
            if len(peers)>=2:
                print("Node {} is in mining state".format(node_ip))
            response = full_node_pb2.List()
            for peer in peers:
                response.ip.append(peer)
            return response

        def NewTransactionReceived(self, request, context):
                global TxnMemoryPool
                print("New Transaction Received")
                tr = blockchain.Transaction()
                tr.setVersionNumber(request.VersionNumber)
                tr.setInCounter(request.incounter)
                tr.setOutCounter(request.outcounter)
                tr.setListOfInputs(request.list_of_inputs)
                tr.setListOfOutputs(request.list_of_outputs)
                tr.setTransactionHash(request.transaction_hash)
                TxnMemoryPool.append(tr) # Add the transaction to memory pool
                return response


        def NewBlockReceived(self, request, context):
                global Blockchain
                global mine_lock
                global current_block
                global current_header
                print("New Block Received")
                block = blockchain.Block()
                header = blockchain.Header()
                for transaction in request.transaction:
                        block.addTransaction(transaction_from_serial(transaction))
                block.setTransactionCounter(request.transaction_counter)
                for header in request.Blockheader:
                        header.sethashMerkleRoot(header.hash_merkel_root)
                        header.setTimestamp(header.timestamp)
                        header.sethashPrevBlock(header.hash_prev_block)
                        header.setBits(header.bits)
                block.setBlocksize(request.BlockSize)
                block.setBlockHeader(header)
                block.setBlockhash(request.blockhash)
                Blockchain.append(block) # Add the new block
                mine_lock = False
                time.sleep(random.randint(0,3)) # Sleep for random time
                mine_lock = True
                current_block, current_header = create_new_block_and_header() # Reset the current block and header
                return response


# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_CommunicatorServicer_to_server`
# to add the defined class to the server
full_node_pb2_grpc.add_CommunicatorServicer_to_server(
        CommunicatorServicer(), server)

# listen on port 50051
print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# Register this node with the DNS Seed
print("Registering this node with the DNS Seed")

channel = grpc.insecure_channel('172.17.0.2:50051')
stub = full_node_pb2_grpc.CommunicatorStub(channel) # Get the dns_seed stub 
Registration = full_node_pb2.Registration(nVersion=1, nTime=round(time.time()), addrMe=node_ip) # Send the node's IP Address
response = stub.Registrar(Registration)

if response.ip[0]!= '': # Not the first node to reach DNS Server
# Add DNS_SEED Response to known peers
        # Update with all the existing nodes
        new_ips = [response.ip[0]]
        while len(new_ips)!=0:
                next_new = []
                for new_ip in new_ips:
                        peers.append(new_ip)
                        channel2 = grpc.insecure_channel(new_ip + ':50051')
                        stub2 = full_node_pb2_grpc.CommunicatorStub(channel2)
                        Handshake = full_node_pb2.Handshake(nVersion=1, nTime=round(time.time()), addrMe=node_ip, bestHeight=0)
                        response2 = stub2.handshake(Handshake)
                        for received_ip in response2.ip:
                                if received_ip != node_ip and received_ip not in peers:
                                        next_new.append(received_ip)
                new_ips = next_new

print("Node " + node_ip +" has peers: {}".format(peers))

if len(peers) ==2:
        print("Node {} is in mining state".format(node_ip))


# since server.start() will not block,
# a sleep-loop is added to keep alive

def create_transactions():
    '''
    Starts creating Transactions on the Blockchain. 1 Threads are started and it creates a new
    transaction at a random time interval. 
    '''
    def tx_creater():
        while generate_tx:
            time.sleep(random.randint(2,4)) # Sleep in a random interval
            print("New Transaction generated")
            add()
    def add():
        tr = blockchain.Transaction()
        tr.setVersionNumber(1)
        tr.setInCounter(1)
        tr.setOutCounter(1)
        random_number = round(random.random(),2)
        inp_value = str(round(time.time())) + str(random_number)
        tr.setListOfInputs([blockchain.compute_double_hash(inp_value)])
        tr.setListOfOutputs([blockchain.compute_double_hash(str(10*random_number)+'outputpay')])
        tr.setTransactionHash(blockchain.computeTransactionHash(tr))
        TxnMemoryPool.append(tr) # Add the transaction to memory pool
        newTransactionBroadcast(tr)
    t1 = threading.Thread(target=tx_creater, args=())
    t1.start()
    return


def newTransactionBroadcast(tr):
        '''
        Sends the new transaction created to all the known peers
        '''
        serial_transaction = full_node_pb2.NewTransaction(VersionNumber=tr.getVersionNumber(), incounter=tr.getInCounter(), outcounter=tr.getOutCounter(),
                                                           transaction_hash=tr.getTransactionHash())
        serial_transaction.list_of_inputs.extend(tr.getListOfInputs())
        serial_transaction.list_of_outputs.extend(tr.getListOfOutputs())
        for peer_ip in peers:
                channel2 = grpc.insecure_channel(peer_ip + ':50051')
                stub2 = full_node_pb2_grpc.CommunicatorStub(channel2)
                response = stub2.NewTransactionReceived(serial_transaction)
        return


def newBlockBroadcast(block):
        '''
        Sends the new Block to all the known peers
        '''
        blockheader = block.getBlockHeader()
        header = full_node_pb2.header(version=blockheader.getVersion(), nonce=blockheader.getNonce(), 
                                      hash_prev_block=blockheader.gethashPrevBlock(), hash_merkel_root=blockheader.gethashMerkleRoot(), 
                                      timestamp=blockheader.getTimestamp(), bits=blockheader.getBits())
        transactions = []
        for tr in block.getTransactions():
                tx = full_node_pb2.NewTransaction(VersionNumber=tr.getVersionNumber(), incounter=tr.getInCounter(), outcounter=tr.getOutCounter(),
                                                  transaction_hash=tr.getTransactionHash())
                tx.list_of_inputs.extend(tr.getListOfInputs())
                tx.list_of_outputs.extend(tr.getListOfOutputs())
                transactions.append(tx)
        serial_block = full_node_pb2.NewBlock(MagicNumber=block.getMagicNumber(), BlockSize=block.getBlocksize(), Blockheader=header, 
                                               transaction_counter=block.getTransactionCounter(),blockhash=block.getBlockhash(), maxtxn=10)
        serial_block.transaction.extend(transactions)
        for peer_ip in peers: # Send the block to all peers
                channel2 = grpc.insecure_channel(peer_ip + ':50051')
                stub2 = full_node_pb2_grpc.CommunicatorStub(channel2)
                response = stub2.NewBlockReceived(serial_block)
        return


def transaction_from_serial(serial_data):
        '''
        Returns a python transaction from received serial data
        '''
        tx = blockchain.Transaction()
        tx.setVersionNumber(serial_data.VersionNumber)
        tx.setInCounter(serial_data.incounter)
        tx.setOutCounter(serial_data.outcounter)
        tx.setListOfInputs(serial_data.list_of_inputs)
        tx.setListOfOutputs(serial_data.list_of_outputs)
        tx.setTransactionHash(serial_data.transaction_hash)
        return tx


def create_new_block_and_header():
        '''Creates a new block and header with the coinbase transaction included and returns them.'''
        block = blockchain.Block()
        header = blockchain.Header()
        # Create the coinbase Transaction
        coinbase_tx = blockchain.Transaction()
        coinbase_tx.setVersionNumber(len(Blockchain)) # Becomes a unique identifier for the transaction
        coinbase_tx.setInCounter(1)
        coinbase_tx.setOutCounter(1)
        coinbase_tx.setListOfInputs([blockchain.compute_double_hash('coinbase')])
        coinbase_tx.setListOfOutputs([blockchain.compute_double_hash('minerpay')])
        coinbase_tx.setTransactionHash(blockchain.computeTransactionHash(coinbase_tx))
        # Add to block and update header
        block.addTransaction(coinbase_tx)
        block.setTransactionCounter(block.getTransactionCounter() + 1)
        Tree = Merkel_Tree(list(block.getTransactions()[0].getTransactionHash()))
        Tree.construct_tree()
        header.sethashMerkleRoot(Tree.merkelroot) # Set Merkel Root
        header.setTimestamp(int(time.time()));
        header.sethashPrevBlock(Blockchain[-1].getBlockhash()) # Set Previous Block
        header.setBits(0x1e200000) # Set the difficulty bits
        block.setBlocksize(179)
        block.setBlockHeader(header)
        block.setBlockhash(blockchain.computeHeaderHash(block.getBlockHeader()))
        return block,header



def generate_genesis_block():
    '''Generates the genesis block'''
    # Genesis Transaction
    genesis_transaction = blockchain.Transaction()
    genesis_transaction.setVersionNumber(0)
    genesis_transaction.setOutCounter(1)
    genesis_transaction.setInCounter(1)
    genesis_transaction.setListOfInputs(['genin'])
    genesis_transaction.setListOfOutputs(['genesis07'])
    genesis_transaction.setTransactionHash(blockchain.computeTransactionHash(genesis_transaction))
    # Genesis Header
    genesis_header = blockchain.Header()
    genesis_header.sethashPrevBlock('0'*64) # Previous Hash of all 0's
    Tree = Merkel_Tree([genesis_transaction.getTransactionHash()])
    Tree.construct_tree()
    genesis_header.sethashMerkleRoot(Tree.merkelroot)
    # Genesis Block
    genesis_block = blockchain.Block()
    genesis_block.setBlockHeader(genesis_header)
    genesis_block.setTransactionCounter(1)
    genesis_block.addTransaction(genesis_transaction)
    genesis_block.setBlocksize(179)
    genesis_block.setBlockhash(blockchain.computeHeaderHash(genesis_block.getBlockHeader()))
    return genesis_block

Blockchain.append(generate_genesis_block())  # Add the genesis block to the blockchain
current_block, current_header = create_new_block_and_header() # Current block and header being mined



def mine():
    '''
    The miner
    '''
    target_hash = '0x0000200000000000000000000000000000000000000000000000000000000000' # Since we have a fixed difficulty, target hash is precomputed.
    global current_block
    global current_header
    global TxnMemoryPool
    try:
        while True:
            if len(peers)> 0: # Eligible to mine
                while current_block.getTransactionCounter() < 10 and len(TxnMemoryPool) > 0: # We can still add a transaction
                    print("Adding a transaction to the current block")
                    current_block.addTransaction(TxnMemoryPool.pop(0))
                    current_block.setTransactionCounter(current_block.getTransactionCounter() + 1)
                    current_block.setBlocksize(78 + (current_block.getTransactionCounter() * 101))
                    transaction_hashes = []
                    for transaction in current_block.getTransactions():
                        transaction_hashes.append(transaction.getTransactionHash())
                    Tree = Merkel_Tree(transaction_hashes) # Recompute Merkel Root
                    Tree.construct_tree()
                    current_header.sethashMerkleRoot(Tree.merkelroot) # Set Merkel Root
                    time.sleep(1)
                if current_header.getNonce() == 65535: # Reset nonce because it is of short type in block size
                    current_header.setNonce(1)
                else:
                    current_header.setNonce(current_header.getNonce() + 1)
                current_block.setBlockHeader(current_header) # Change Header
                current_block.setBlockhash(blockchain.computeHeaderHash(current_block.getBlockHeader()))
                if int(current_block.getBlockhash(),16) < int(target_hash,16):
                    Blockchain.append(current_block)
                    newBlockBroadcast(current_block) # Broadcast the block
    except KeyboardInterrupt:
        server.stop(0)
        global generate_tx
        generate_tx = False # Stop generating transactions
        
        
if __name__=='__main__':
    create_transactions()
    mine()        
        
        
