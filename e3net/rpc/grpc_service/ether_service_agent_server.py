#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.rpc.protos_base import ether_service_pb2
from e3net.rpc.protos_base import ether_service_pb2_grpc
from e3net.rpc.protos_base import common_pb2


class ether_service_agent_service(ether_service_pb2_grpc.ether_serviceServicer):
    def rpc_push_ether_services(self, request_iterator, context):
        services = list()
        for _service in request_iterator:
            services.append(_service)
        print('pushed service list:', services)
        return common_pb2.null()
publish_rpc_service(ether_service_pb2_grpc.add_ether_serviceServicer_to_server,
    ether_service_agent_service)




