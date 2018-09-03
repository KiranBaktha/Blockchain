# Blockchain
Coursework for Introduction to Blockchain class at UChicago Summer 2018.

<p align="justify">
A simple blockchain simulation involving 1 DNS seed and 3 Full Nodes. <a href='https://grpc.io/'>gRPC</a> is used to communicate with other nodes. Initially, each node registers itself with the DNS seed which then sends the previous registered full node as a response back. The first registering node gets a null response back from the DNS seed. When a full node receives a non-null response from the DNS seed, it handshakes with the node from the response. It then continutes handshaking with the response peer nodes from the first handshaked node and this process continutes until all the nodes are aware of it's peers. This procedure is illustrated with the following images with times steps T1 - T4
</p>

<img src="/static/T1.png" alt="T1" width="400" height="200"/>

<img src="/static/T2.png" alt="T2" width="400" height="300"/>

<img src="/static/T3.png" alt="T3" width="400" height="300"/>

<img src="/static/T4.png" alt="T4" width="400" height="300"/>

<p align="justify">
Once each full node has 2 peers, it will then be able to mine. The full nodes create transactions in a seperate thread randomly and communicate with other peers when a new transaction is created or a new block is mined so that the peers can update themselves. When a full node mines a block, all the full nodes (including the winner) will sleep for a random number of seconds between (1-3) to prevent race conditions. For mining, a fixed difficulty of 0x1e200000 is used.
</p>
<img src="/static/T5.png" alt="T5" width="400" height="300"/>

# Source File Description

1. dns_seed has the source code to behave as a dns seed.
<ul>
  <li>dns_seed.proto - proto3 file for dns seed</li>
  <li>dns_seed_pb2 - generated message classes by grpc</li>
  <li>dns_seed_pb2_grpc - generated server and client classes by grpc</li>
  <li>server.py - dns seed server source code</li>
</ul>
2. full_node has the source code to behave as a full node.
<ul>
  <li>blockchain.py - contains the class representation of blockchain components</li>
  <li>full_node.proto - proto3 file for full node</li>
  <li>full_node_pb2 - generated message classes by grpc</li>
  <li>full_node_pb2_grpc - generated server and client classes by grpc</li>
  <li>merkel_tree.py - merkel tree implementation</li>
  <li>server.py - full node server source code</li>
</ul>


# Running Instructions

Docker containers can be used to simulate the dns seed and full nodes. Each full node docker container must be linked to the dns seed on creation.

The following code for instance will link the full node a container called "full_node_a" to the dns seed container called "dns_seed". 

    docker run -it --name full_node_a --link dns_seed:full_node_a ubuntu:16.04

The same to be repeated for full nodes b and c. 

Execute the server.py under dns_seed src package in dns_seed container first and then server.py under full_node src package for each of the full node containers.
