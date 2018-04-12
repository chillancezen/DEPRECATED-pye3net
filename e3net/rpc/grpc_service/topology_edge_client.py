#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_client import publish_stub_inventory
from e3net.rpc.protos_base import topology_edge_pb2
from e3net.rpc.protos_base import topology_edge_pb2_grpc
from e3net.rpc.grpc_client import get_stub

rpc_service = 'topology_edge'


def rpc_client_get_topology_edge(stub, uuid):
    key = topology_edge_pb2.req_edge_key()
    key.uuid_or_service_id = uuid
    return stub.rpc_get_topology_edge(key)

def rpc_client_list_topology_edges(stub, uuid_list):
    def __key_generator0(_uuid_list):
        for _uuid in _uuid_list:
            key = topology_edge_pb2.req_edge_key()
            key.per_uuid = True
            key.uuid_or_service_id = _uuid
            yield key
    return stub.rpc_list_topology_edges(__key_generator0(uuid_list))

def rpc_client_list_topology_edges_for_services(stub, service_list):
    def __key_generator1(_service_list):
        for _service in _service_list:
            key = topology_edge_pb2.req_edge_key()
            key.per_uuid = False
            key.uuid_or_service_id = _service
            yield key
    return stub.rpc_list_topology_edges(__key_generator1(service_list))

publish_stub_inventory(rpc_service, topology_edge_pb2_grpc.topology_edgeStub)


if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)
    print(rpc_client_get_topology_edge(stub, '4ba573ea-84eb-4ed6-8be9-f3831f9e72ee'))
    edges = rpc_client_list_topology_edges(stub,['53183c64-fb52-4593-8ea2-ed1bdf668548',
        '82d688e1-44d1-4ae4-9ddb-3eda02a6c794'])
    edges = rpc_client_list_topology_edges_for_services(stub,['add0e8b7-95db-4033-8aae-207576d9d019'])
    for edge in edges:
        print(edge)
