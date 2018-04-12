#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.rpc.protos_base import topology_edge_pb2
from e3net.rpc.protos_base import topology_edge_pb2_grpc
from e3net.rpc.protos_base import common_pb2
from e3net.inventory.invt_vswitch_topology_edge import invt_register_vswitch_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_unregister_vswitch_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_get_vswitch_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_list_vswitch_topology_edges

def to_topology_edge_pb2(edge):
    edge_pb2 = topology_edge_pb2.res_topology_edge()
    edge_pb2.id = edge.id
    edge_pb2.interface0 = edge.interface0
    edge_pb2.interface1 = edge.interface1
    edge_pb2.service_id = edge.service_id
    return edge_pb2

class topology_edge_service(topology_edge_pb2_grpc.topology_edgeServicer):
    def rpc_get_topology_edge(self, request, context):
        edge = invt_get_vswitch_topology_edge(request.uuid_or_service_id)
        return to_topology_edge_pb2(edge)

    def rpc_list_topology_edges(self, request_iterator, context):
        edges = invt_list_vswitch_topology_edges()
        empty_key_list = True
        raw_edges = dict()
        for key in request_iterator:
            empty_key_list = False
            if key.per_uuid:
                raw_edges[key.uuid_or_service_id] = \
                    invt_get_vswitch_topology_edge(key.uuid_or_service_id)
            else:
                for _edge_id in edges:
                    _edge = edges[_edge_id]
                    if _edge.service_id == key.uuid_or_service_id:
                        raw_edges[_edge_id] = _edge
        _raw_edges = raw_edges if not empty_key_list else edges
        for _edge_id in _raw_edges:
            yield to_topology_edge_pb2(_raw_edges[_edge_id])

publish_rpc_service(topology_edge_pb2_grpc.add_topology_edgeServicer_to_server,
    topology_edge_service)
