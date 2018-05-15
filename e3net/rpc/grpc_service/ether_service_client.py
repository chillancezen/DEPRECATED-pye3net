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
from e3net.common.e3def import E_LAN_OPERATION_ADDITION
from e3net.common.e3def import E_LAN_OPERATION_REMOVAL
rpc_service = 'ether_service'

def rpc_client_get_ether_service(stub, uuid):
    key = ether_service_pb2.req_ether_service_key()
    key.tenant_id_or_uuid = uuid
    return stub.rpc_get_ether_service(key)

def rpc_client_list_ether_services(stub,uuid_list = []):
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
def rpc_client_taskflow_create_ether_service(stub,
    service_name,
    tenant_id,
    initial_lanzones,
    ban_hosts = [],
    ban_lanzones = [],
    ban_interfaces = [],
    service_type = E3NET_ETHER_SERVICE_TYPE_LINE,
    link_type = E3NET_ETHER_SERVICE_LINK_SHARED,
    is_synced = True):
    spec = ether_service_pb2.req_service_create_spec()
    spec.service_name = service_name
    spec.service_type = service_type
    spec.tenant_id = tenant_id
    spec.link_type = link_type
    spec.is_synced = is_synced
    for il in initial_lanzones:
        spec.initial_lanzones.append(il)
    for bh in ban_hosts:
        spec.ban_hosts.append(bh)
    for bl in ban_lanzones:
        spec.ban_lanzones.append(bl)
    for bi in ban_interfaces:
        spec.ban_interfaces.append(bi)
    stub.rpc_taskflow_create_ether_service(spec)

def rpc_client_taskflow_delete_ether_service(stub,
    service_ids,
    is_synced = True):
    spec = ether_service_pb2.req_service_delete_spec()
    for _service_id in service_ids:
        spec.service_ids.append(_service_id)
    spec.is_synced = is_synced
    stub.rpc_taskflow_delete_ether_service(spec)
def rpc_client_taskflow_update_ether_lan_service(stub,
    service_id,
    operation,
    initial_lanzones,
    ban_hosts = [],
    ban_lanzones = [],
    ban_interfaces =[],
    is_synced = True):
    spec = ether_service_pb2.req_lan_service_update_spec()
    spec.service_id = service_id
    spec.operation = operation
    for il in initial_lanzones:
        spec.initial_lanzones.append(il)
    for bh in ban_hosts:
        spec.ban_hosts.append(bh)
    for bl in ban_lanzones:
        spec.ban_lanzones.append(bl)
    for bi in ban_interfaces:
        spec.ban_interfaces.append(bi)
    spec.is_synced =is_synced
    stub.rpc_taslflow_update_ether_lan_service(spec)

publish_stub_inventory(rpc_service, ether_service_pb2_grpc.ether_serviceStub)

if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    import sys
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)
    if False: 
        rpc_client_taskflow_create_ether_service(stub,
        service_name = 'ether_line_0',
        tenant_id = 'c2204787-df90-473b-8ed6-52838eab1c32',
        initial_lanzones = ['1bcd32a0-444d-41cb-a3fd-786f6f3ef83c',
            '2ddc6ac9-5216-4e25-8414-9e088c33a94f',
            'abe1b66e-7f34-4857-bdb8-ec27b76373a3'],
        service_type = E3NET_ETHER_SERVICE_TYPE_LAN,
        is_synced = True)
    rpc_client_taskflow_update_ether_lan_service(stub,'f666831e-7e02-4b12-a39f-f0bca96ef6ab',E_LAN_OPERATION_REMOVAL,initial_lanzones = ['1bcd32a0-444d-41cb-a3fd-786f6f3ef83c'], is_synced = True)
    rpc_client_taskflow_update_ether_lan_service(stub,'f666831e-7e02-4b12-a39f-f0bca96ef6ab',E_LAN_OPERATION_ADDITION,initial_lanzones = ['1bcd32a0-444d-41cb-a3fd-786f6f3ef83c'], is_synced = True)
    #services =  rpc_client_list_ether_services(stub)
    #print(services)
    #rpc_client_taskflow_delete_ether_service(stub, [e.id for e in services])
    #rpc_client_taskflow_delete_ether_service(stub, ['a3383c77-c5de-46f3-928a-60626196f36b'])
    sys.exit()
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
