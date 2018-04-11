#more ether_service_client.py
#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_client import publish_stub_inventory
from e3net.rpc.protos_base import ether_service_pb2
from e3net.rpc.protos_base import ether_service_pb2_grpc
from e3net.rpc.grpc_client import get_stub
from e3net.rpc.grpc_service.ether_service_server import ether_service_to_pb2

rpc_service = 'ether_service_agent'
def rpc_client_push_ether_services(stub, service_list):
    def __key_generator0(_service_list):
        for _service in _service_list:
            yield ether_service_to_pb2(_service)
    return stub.rpc_push_ether_services(__key_generator0(service_list))

publish_stub_inventory(rpc_service, ether_service_pb2_grpc.ether_serviceStub)
