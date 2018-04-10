#invt_list_vswitch_interfaces
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
from e3net.inventory.invt_vswitch_topology_edge import invt_list_vswitch_topology_edges
from e3net.inventory.invt_vswitch_interface import invt_list_vswitch_interfaces
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
    def rpc_list_ether_services(self, request_iterator, context):
        services = invt_list_vswitch_ether_services()
        raw_services = dict()
        null_list = True
        for key in request_iterator:
            null_list = False
            if key.per_tenant == True:
                for _service_id in services:
                    _service = services[_service_id]
                    if _service.tenant_id == key.tenant_id_or_uuid:
                        raw_services[_service.id] = _service
            else:
                raw_services[key.tenant_id_or_uuid] = invt_get_vswitch_ether_service(key.tenant_id_or_uuid)
        _raw_services = services if null_list else raw_services
        for _service_id in _raw_services:
            yield ether_service_to_pb2(_raw_services[_service_id])
    def rpc_register_ether_service(self, request, context):
        create_spec = dict()
        create_spec['name'] = request.name
        create_spec['service_type'] = request.service_type
        create_spec['tenant_id'] = request.tenant_id
        create_spec['link_type']  = request.link_type
        e_service = invt_register_vswitch_ether_service(create_spec, user_sync = True)
        return ether_service_to_pb2(e_service)
    def rpc_unregister_ether_service(self, request, context):
        invt_unregister_vswitch_ether_service(request.tenant_id_or_uuid, user_sync = True)
        return common_pb2.null()
    def rpc_pull_ether_services(self, request, context):
        #request.tenant_id_or_uuid as HostID
        #go through the topology edges and find out whichs service involves the host
        #it can consume lots of time
        invt_services = invt_list_vswitch_ether_services()
        services = set()
        interfaces = invt_list_vswitch_interfaces()
        edges = invt_list_vswitch_topology_edges()
        for _edge_id in edges:
            _edge = edges[_edge_id]
            iface0_id = _edge.interface0
            iface1_id = _edge.interface1
            if interfaces[iface0_id].host_id == request.tenant_id_or_uuid:
                services.add(_edge.service_id)
            if interfaces[iface1_id].host_id == request.tenant_id_or_uuid:
                services.add(_edge.service_id)
        for _service_id in services:
            yield ether_service_to_pb2(invt_services[_service_id])
    #do not implement rpc_push_ether_service() here
publish_rpc_service(ether_service_pb2_grpc.add_ether_serviceServicer_to_server,
                    ether_service_service)
