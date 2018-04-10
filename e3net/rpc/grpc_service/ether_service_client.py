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
from e3net.common.e3def import E3NET_ETHER_SERVICE_TYPE_LINE
from e3net.common.e3def import E3NET_ETHER_SERVICE_TYPE_LAN
from e3net.common.e3def import E3NET_ETHER_SERVICE_LINK_SHARED
from e3net.common.e3def import E3NET_ETHER_SERVICE_LINK_EXCLUSIVE

rpc_service = 'ether_service'

def rpc_client_get_ether_service(stub, uuid):
    key = ether_service_pb2.req_ether_service_key()
    key.tenant_id_or_uuid = uuid
    return stub.rpc_get_ether_service(key)

def rpc_client_list_ether_services(stub,uuid_list):
    def __key_generator0(_uuid_list):
        for _uuid in _uuid_list:
            key = ether_service_pb2.req_ether_service_key()
            key.per_tenant = False
            key.tenant_id_or_uuid = _uuid
            yield key
    return stub.rpc_list_ether_services(__key_generator0(uuid_list))

def rpc_client_list_ether_services_for_tenants(stub, tenant_list):
    def __key_generator1(_tenant_list):
        for _tenant in _tenant_list:
            key = ether_service_pb2.req_ether_service_key()
            key.per_tenant = True
            key.tenant_id_or_uuid = _tenant
            yield key
    return stub.rpc_list_ether_services(__key_generator1(tenant_list))

def rpc_client_unregister_ether_service(stub, uuid):
    key = ether_service_pb2.req_ether_service_key()
    key.tenant_id_or_uuid = uuid
    return stub.rpc_unregister_ether_service(key)

def rpc_client_register_ether_service(stub,
                                        name,
                                        tenant_id,
                                        service_type = E3NET_ETHER_SERVICE_TYPE_LINE,
                                        link_type = E3NET_ETHER_SERVICE_LINK_SHARED):
    e_service = ether_service_pb2.res_ether_service()
    e_service.name = name
    e_service.service_type = service_type
    e_service.tenant_id = tenant_id
    e_service.link_type = link_type
    return stub.rpc_register_ether_service(e_service)

def rpc_client_pull_ether_services(stub, host_uuid):
    key = ether_service_pb2.req_ether_service_key()
    key.tenant_id_or_uuid = host_uuid
    return stub.rpc_pull_ether_services(key)

publish_stub_inventory(rpc_service, ether_service_pb2_grpc.ether_serviceStub)

if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)
    print(rpc_client_get_ether_service(stub, '387a7139-550b-4556-8589-e4e0d61870ca'))
    services = rpc_client_list_ether_services(stub, ['387a7139-550b-4556-8589-e4e0d61870ca',
            '5664f898-1d2c-47ac-ab8c-a604344af411'])
    services = rpc_client_list_ether_services_for_tenants(stub, ['7b155a2d-a4da-4f97-b35e-45e5c3dff1872'])
    for _service_id in services:
        print(_service_id)
    service = rpc_client_register_ether_service(stub, 'cute-lan-service','7b155a2d-a4da-4f97-b35e-45e5c3dff187')
    rpc_client_unregister_ether_service(stub, service.id)
    services = rpc_client_pull_ether_services(stub, '3d92affb-4d80-42ff-bbf0-cde2743ac7ab')
    for service in services:
        print(service)
