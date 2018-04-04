#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_client import publish_stub_inventory
from e3net.rpc.protos_base import vswitch_host_pb2
from e3net.rpc.protos_base import vswitch_host_pb2_grpc
from e3net.rpc.grpc_client import get_stub

rpc_service = 'vswitch_host'



publish_stub_inventory(rpc_service, vswitch_host_pb2_grpc.vswitch_hostStub)
def rpc_client_get_vswitch_host(stub, uuid_or_hostname, is_uuid = True):
    key = vswitch_host_pb2.req_host_key()
    key.per_uuid = is_uuid
    if is_uuid:
        key.uuid = uuid_or_hostname
    else:
        key.host_name = uuid_or_hostname
    return stub.rpc_get_vswitch_host(key)

def rpc_client_list_vswitch_hosts(stub, uuid_list = [], hostname_list = []):
    def __key_generator0(_uuid_list, _hostname_list):
        keys = list()
        for _uuid in _uuid_list:
            key = vswitch_host_pb2.req_host_key()
            key.per_uuid = True
            key.uuid = _uuid
            keys.append(key)
        for _hostname in _hostname_list:
            key = vswitch_host_pb2.req_host_key()
            key.per_uuid = False
            key.host_name = _hostname
            keys.append(key)
        for _key in keys:
            yield _key
    return stub.rpc_list_vswitch_hosts(__key_generator0(uuid_list, hostname_list))
def rpc_client_register_vswitch_host(stub,
                                        name,
                                        host_ip,
                                        description = None,
                                        host_status = None):
    host_pb2 = vswitch_host_pb2.res_vswitch_host()
    host_pb2.name = name
    host_pb2.host_ip = host_ip
    if description:
        host_pb2.description = description
    if host_status:
        host_pb2.host_status = host_status
    return stub.rpc_register_vswiitch_host(host_pb2)

def rpc_client_unregister_vswitch_host(stub, uuid):
    key = vswitch_host_pb2.req_host_key()
    key.uuid = uuid
    stub.rpc_unregister_vswitch_host(key)
def rpc_client_update_vswitch_host(stub,
                                    uuid,
                                    name = None,
                                    host_ip = None,
                                    description = None,
                                    host_status = None):
    host_pb2 = vswitch_host_pb2.res_vswitch_host()
    host_pb2.id = uuid
    if name:
        host_pb2.name = name
    if host_ip:
        host_pb2.host_ip = host_ip
    if description:
        host_pb2.description = description
    if host_status:
        host_pb2.host_status = host_status
    stub.rpc_update_vswitch_host(host_pb2)

if __name__ == '__main__':
    import grpc
    import sys
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)
    #print(rpc_client_get_vswitch_host(stub, '3e902d67-a504-4fd1-979f-fb94ec4cada8'))
    #print(rpc_client_get_vswitch_host(stub, 'n1', False))
    host = rpc_client_register_vswitch_host(stub, 'server-23232-1','120.23.3.40')
    rpc_client_update_vswitch_host(stub, host.id, description = 'meeeow gogogo')
    print(rpc_client_get_vswitch_host(stub, host.id))
    rpc_client_unregister_vswitch_host(stub , host.id)
    hosts = rpc_client_list_vswitch_hosts(stub)
    #for host in hosts:
    #    print(host)
    sys.exit()
    #hosts  = stub.rpc_list_vswitch_hosts(foo())
    #key = vswitch_host_pb2.req_key()
    #key.uuid = '1372bd9c-7041-4476-b92f-cc7905f1e0bd'
    #stub.rpc_unregister_vswitch_host(key)
    #spec = vswitch_host_pb2.res_vswitch_host()
    #spec.id = '3e902d67-a504-4fd1-979f-fb94ec4cada8'
    #spec.name = 'e3net-spine2'
    #spec.description = 'hello world'
    #stub.rpc_update_vswitch_host(spec)
    #key = vswitch_host_pb2.req_key()
    #key.per_uuid = True
    #key.uuid = '3e902d67-a504-4fd1-979f-fb94ec4cada8'
    #print(stub.rpc_get_vswitch_host(key))
    #sys.exit()
    #host_pb2 = vswitch_host_pb2.res_vswitch_host()
    #host_pb2.name = '1server-0012332'
    ##host_pb2.host_ip = '110.101.233.23'
    #print(stub.rpc_register_vswiitch_host(host_pb2))
    #print('------')
    #key = vswitch_host_pb2.req_key()
    #key.per_uuid = False
    #key.host_name = '1server-0012332'
    #try:
    #    host = stub.rpc_get_vswitch_host(key)
    #except grpc.RpcError as e:
    #    print(e)
    #    print(e.code())
    #    print(e.details())
    #else:
    #    print(host)
    def foo():
        host_names = []
        for name in host_names:
            key = vswitch_host_pb2.req_host_key()
            key.per_uuid = False
            key.host_name = name
            yield key
    hosts  =stub.rpc_list_vswitch_hosts(foo())
    for i in hosts:
        print(i)
