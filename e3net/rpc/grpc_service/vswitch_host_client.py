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
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)

    key = vswitch_host_pb2.req_key()
    key.per_uuid = False
    key.host_name = 'nn3'
    try:
        host = stub.rpc_get_vswitch_host(key)
    except grpc.RpcError as e:
        print(e)
        print(e.code())
        print(e.details())
    else:
        print(host)

