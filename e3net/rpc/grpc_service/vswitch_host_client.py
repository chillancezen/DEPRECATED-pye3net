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

if __name__ == '__main__':
    import grpc
    import sys
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)

    #key = vswitch_host_pb2.req_key()
    #key.uuid = '1372bd9c-7041-4476-b92f-cc7905f1e0bd'
    #stub.rpc_unregister_vswitch_host(key)
    spec = vswitch_host_pb2.res_vswitch_host()
    spec.id = '3e902d67-a504-4fd1-979f-fb94ec4cada8'
    spec.name = 'e3net-spine2'
    spec.description = 'hello world'
    stub.rpc_update_vswitch_host(spec)
    key = vswitch_host_pb2.req_key()
    key.per_uuid = True
    key.uuid = '3e902d67-a504-4fd1-979f-fb94ec4cada8'
    print(stub.rpc_get_vswitch_host(key))
    sys.exit()
    host_pb2 = vswitch_host_pb2.res_vswitch_host()
    host_pb2.name = '1server-0012332'
    host_pb2.host_ip = '110.101.233.23'
    print(stub.rpc_register_vswiitch_host(host_pb2))
    print('------')
    key = vswitch_host_pb2.req_key()
    key.per_uuid = False
    key.host_name = '1server-0012332'
    try:
        host = stub.rpc_get_vswitch_host(key)
    except grpc.RpcError as e:
        print(e)
        print(e.code())
        print(e.details())
    else:
        print(host)
    def foo():
        host_names = []
        for name in host_names:
            key = vswitch_host_pb2.req_key()
            key.per_uuid = False
            key.host_name = name
            yield key
    hosts  =list() #=stub.rpc_list_vswitch_host(foo())
    for i in hosts:
        print(i)
