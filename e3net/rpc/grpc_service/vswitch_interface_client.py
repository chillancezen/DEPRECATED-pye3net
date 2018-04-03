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

def rpc_client_get_vswitch_interface(stub, uuid):
    key = vswitch_interface_pb2.req_interface_key()
    key.uuid = uuid
    return stub.rpc_get_vswitch_interface(key)

def rpc_client_list_vswitch_interfaces(stub, uuid_list):
    def _key_generator0(uuid_list):
        for uuid in uuid_list:
            key = vswitch_interface_pb2.req_interface_key()
            key.uuid_type = 0
            key.uuid = uuid
            yield key
    return stub.rpc_list_vswitch_interfaces(_key_generator0(uuid_list))

def rpc_client_list_vswitch_interfaces_for_hosts(stub, host_list):
    def _key_generator1(host_list):
        for host in host_list:
            key = vswitch_interface_pb2.req_interface_key()
            key.uuid_type = 1
            key.uuid = host
            yield key
    return stub.rpc_list_vswitch_interfaces(_key_generator1(host_list))

def rpc_client_list_vswitch_interfaces_for_lanzone(stub, lanzone_list):
    def _key_generator2(lanzone_list):
        for lanzone in lanzone_list:
            key = vswitch_interface_pb2.req_interface_key()
            key.uuid_type = 2
            key.uuid = lanzone
            yield key
    return stub.rpc_list_vswitch_interfaces(_key_generator2(lanzone_list))

def rpc_client_register_vswitch_interface(stub,
                                            host_id,
                                            dev_address,
                                            lanzone_id,
                                            interface_status = None,
                                            interface_type = None):
    iface_pb2 = vswitch_interface_pb2.res_vswitch_interface()
    iface_pb2.host_id = host_id
    iface_pb2.dev_address = dev_address
    iface_pb2.lanzone_id = lanzone_id
    if interface_status:
        iface_pb2.interface_status = interface_status
    if interface_type:
        iface_pb2.interface_type = interface_type
    return stub.rpc_register_vswitch_interface(iface_pb2)

if __name__ == '__main__':
    import grpc
    import sys
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    stub = get_stub('127.0.0.1', 9418, rpc_service)

    #print(rpc_client_get_vswitch_interface(stub, 'aef0a53a-b90c-4a51-afa9-ee3b3db77a6b'))
    ifaces = rpc_client_list_vswitch_interfaces(stub, ['6a59b7bd-e04e-47e6-8797-8da2e7bdf151','aef0a53a-b90c-4a51-afa9-ee3b3db77a6b'])
    ifaces = rpc_client_list_vswitch_interfaces_for_hosts(stub, ['bf2e1bfe-1e85-4205-b9db-0b234e920017'])
    ifaces = rpc_client_list_vswitch_interfaces_for_lanzone(stub,['763cfbf2-f014-479e-a522-5ceb9926de4f'])
    for iface in ifaces:
        print(iface)
    print(rpc_client_register_vswitch_interface(stub, 'a8c07386-d5d1-43cc-bcd1-06e2a37c225e', '00.0.0', '4e8d1fca-6398-416a-aa78-2e0d50270338'))
    sys.exit()
    key = vswitch_interface_pb2.req_interface_key()
    key.uuid = 'aef0a53a-b90c-4a51-afa9-ee3b3db77a6b'
    print(stub.rpc_get_vswitch_interface(key))

    def foo():
        keys = ['']
        for i in keys:
            key=vswitch_interface_pb2.req_interface_key()
            key.uuid_type = 2
            key.uuid = i
            yield key

    ifaces = stub.rpc_list_vswitch_interfaces(foo())
    for iface in ifaces:
        print(iface)
    iface = vswitch_interface_pb2.res_vswitch_interface()
    iface.host_id = 'a8c07386-d5d1-43cc-bcd1-06e2a37c225e'
    iface.dev_address = '0001:00.0.0'
    iface.lanzone_id = '4e8d1fca-6398-416a-aa78-2e0d50270338'
    iface = stub.rpc_register_vswitch_interface(iface)
    #print(stub.rpc_register_vswitch_interface(iface))
    key = vswitch_interface_pb2.req_interface_key()
    key.uuid = iface.id
    print(stub.rpc_unregister_vswitch_interface(key))
