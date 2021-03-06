# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import dns_seed_pb2 as dns__seed__pb2


class CommunicatorStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Registrar = channel.unary_unary(
        '/Communicator/Registrar',
        request_serializer=dns__seed__pb2.Registration.SerializeToString,
        response_deserializer=dns__seed__pb2.List.FromString,
        )
    self.handshake = channel.unary_unary(
        '/Communicator/handshake',
        request_serializer=dns__seed__pb2.Handshake.SerializeToString,
        response_deserializer=dns__seed__pb2.List.FromString,
        )


class CommunicatorServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Registrar(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def handshake(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_CommunicatorServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Registrar': grpc.unary_unary_rpc_method_handler(
          servicer.Registrar,
          request_deserializer=dns__seed__pb2.Registration.FromString,
          response_serializer=dns__seed__pb2.List.SerializeToString,
      ),
      'handshake': grpc.unary_unary_rpc_method_handler(
          servicer.handshake,
          request_deserializer=dns__seed__pb2.Handshake.FromString,
          response_serializer=dns__seed__pb2.List.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Communicator', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
