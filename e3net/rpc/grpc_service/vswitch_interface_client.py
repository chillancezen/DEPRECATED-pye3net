#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_client import publish_stub_inventory
from e3net.rpc.protos_base import vswitch_interface_pb2
from e3net.rpc.protos_base import vswitch_interface_pb2_grpc
from e3net.rpc.grpc_client import get_stub

rpc_service = 'vswitch_interface'

publish_stub_inventory(rpc_service, vswitch_interface_pb2_grpc.vswitch_interfaceStub)



if __name__ == '__main__':
    import grpc
    import sys
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)

    key = vswitch_interface_pb2.req_interface_key()
    key.uuid = 'aef0a53a-b90c-4a51-afa9-ee3b3db77a6b'
    print(stub.rpc_get_vswitch_interface(key))
