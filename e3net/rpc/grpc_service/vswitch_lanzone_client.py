#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_client import publish_stub_inventory
from e3net.rpc.protos_base import vswitch_lanzone_pb2
from e3net.rpc.protos_base import vswitch_lanzone_pb2_grpc
from e3net.rpc.grpc_client import get_stub
rpc_service = 'vswitch_lanzone'

publish_stub_inventory(rpc_service, vswitch_lanzone_pb2_grpc.vswitch_lanzoneStub)

def rpc_client_get_vswitch_lanzone(stub, uuid_or_name, is_uuid = True):
    key = vswitch_lanzone_pb2.req_lanzone_key()
    if is_uuid:
        key.per_uuid = True
        key.uuid = uuid_or_name
    else:
        key.per_uuid = False
        key.lanzone_name = uuid_or_name
    return stub.rpc_get_vswitch_lanzone(key)

def rpc_client_list_vswitch_lanzones(stub, uuid_list = [], name_list = []):
    def __key_generator0(_uuid_list, _name_list):
        keys = list()
        for _uuid in _uuid_list:
            key = vswitch_lanzone_pb2.req_lanzone_key()
            key.per_uuid = True
            key.uuid = _uuid
            keys.append(key)
        for _name in _name_list:
            key = vswitch_lanzone_pb2.req_lanzone_key()
            key.per_uuid = False
            key.lanzone_name = _name
            keys.append(key)
        for _key in keys:
            yield _key
    return stub.rpc_list_vswitch_lanzones(__key_generator0(uuid_list, name_list))

def rpc_client_register_vswitch_lanzone(stub,
                                        name,
                                        zone_type,
                                        min_vlan = 1,
                                        max_vlan = 4094):
    lanzone_pb2 = vswitch_lanzone_pb2.res_vswitch_lanzone()
    lanzone_pb2.name = name
    lanzone_pb2.zone_type = zone_type
    lanzone_pb2.min_vlan = min_vlan
    lanzone_pb2.max_vlan =max_vlan
    return stub.rpc_register_vswitch_lanzone(lanzone_pb2)

def rpc_client_unregister_vswitch_lanzone(stub, uuid):
    key = vswitch_lanzone_pb2.req_lanzone_key()
    key.uuid = uuid
    stub.rpc_unregister_vswitch_lanzone(key)

def rpc_client_update_vswitch_lanzone(stub,
                                        uuid,
                                        zone_type = None,
                                        min_vlan = None,
                                        max_vlan = None):
    lanzone_pb2 = vswitch_lanzone_pb2.res_vswitch_lanzone()
    lanzone_pb2.id = uuid
    if zone_type:
        lanzone_pb2.zone_type = zone_type
    if min_vlan:
        lanzone_pb2.min_vlan = min_vlan
    if max_vlan:
        lanzone_pb2.max_vlan = max_vlan
    stub.rpc_update_vswitch_lanzone(lanzone_pb2)

if __name__ == '__main__':
    import grpc
    import sys
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    lanzones_def = {
        'customer-lan0': 'customer',
        'customer-lan1': 'customer',
        'customer-lan2': 'customer',
        'customer-lan3': 'customer',
        'backbone-lan0': 'backbone',
        'backbone-lan1': 'backbone',
        'backbone-lan2': 'backbone',
    }
    stub = get_stub('127.0.0.1', 9418, rpc_service)
    for _name in lanzones_def:
        lanzone = rpc_client_register_vswitch_lanzone(stub, _name, lanzones_def[_name])
    #print(rpc_client_get_vswitch_lanzone(stub, 'backbone-lan0',False))
    #print(rpc_client_get_vswitch_lanzone(stub,'3be12991-f039-4a2e-a884-005bb6936f58'))
    #lanzone = rpc_client_register_vswitch_lanzone(stub,'lanzone-customer3', 'backbone')
    #rpc_client_update_vswitch_lanzone(stub, lanzone.id, min_vlan = 418, zone_type = 'customer', max_vlan = 512)
    #print(rpc_client_get_vswitch_lanzone(stub,lanzone.id))
    #rpc_client_unregister_vswitch_lanzone(stub,lanzone.id)
    #lanzones = rpc_client_list_vswitch_lanzones(stub)
    #for lanzone in lanzones:
    #    print(lanzone)
