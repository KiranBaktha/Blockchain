import grpc
from concurrent import futures
import time

# import the generated classes
import dns_seed_pb2
import dns_seed_pb2_grpc

# The ip list of the nodes
ip_list = []

# create a class to define the server functions, derived from
# dns_seed_pb2_grpc.CommunicatorServicer
class CommunicatorServicer(dns_seed_pb2_grpc.CommunicatorServicer):
	def Registrar(self, request, context):
		global ip_list
		response = dns_seed_pb2.List()
		if len(ip_list)==0:
			response.ip.append('')
		else:
			response.ip.append(ip_list[len(ip_list)-1]) # Adds the last registered full node's IP address
		print("Received node ip: {}".format(request.addrMe))
		ip_list.append(request.addrMe) # Add the node's ip back to the list
		return response
# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_CommunicatorServicer_to_server`
# to add the defined class to the server
dns_seed_pb2_grpc.add_CommunicatorServicer_to_server(
        CommunicatorServicer(), server)

# listen on port 50051
print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
