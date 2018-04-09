#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.inventory.invt_vswitch_ether_service import invt_register_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_unregister_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_get_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_list_vswitch_ether_services
from e3net.rpc.protos_base import ether_service_pb2
from e3net.rpc.protos_base import ether_service_pb2_grpc
from e3net.rpc.protos_base import common_pb2

def ether_service_to_pb2(e_service):
    e_service_pb2 = ether_service_pb2.res_ether_service()
    e_service_pb2.id = e_service.id
    e_service_pb2.name = e_service.name
    e_service_pb2.service_type = e_service.service_type
    e_service_pb2.tenant_id = e_service.tenant_id
    e_service_pb2.created_at = e_service.created_at.ctime()
    e_service_pb2. link_type = e_service.link_type
    return e_service_pb2

class ether_service_service(ether_service_pb2_grpc.ether_serviceServicer):
    def rpc_get_ether_service(self, request, context):
        e_service = invt_get_vswitch_ether_service(request.tenant_id_or_uuid)
        return ether_service_to_pb2(e_service)

publish_rpc_service(ether_service_pb2_grpc.add_ether_serviceServicer_to_server,
                    ether_service_service)
