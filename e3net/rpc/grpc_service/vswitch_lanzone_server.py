#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.inventory.invt_vswitch_lan_zone import invt_register_vswitch_lan_zone
from e3net.inventory.invt_vswitch_lan_zone import invt_update_vswitch_lan_zone
from e3net.inventory.invt_vswitch_lan_zone import invt_unregister_vswitch_lan_zone
from e3net.inventory.invt_vswitch_lan_zone import invt_get_vswitch_lan_zone
from e3net.inventory.invt_vswitch_lan_zone import invt_list_vswitch_lan_zones
from e3net.rpc.protos_base import vswitch_lanzone_pb2
from e3net.rpc.protos_base import vswitch_lanzone_pb2_grpc
from e3net.rpc.protos_base import common_pb2

def to_vswitch_lanzone_pb2(lanzone):
    lanzone_pb2 = vswitch_lanzone_pb2.res_vswitch_lanzone()
    lanzone_pb2.id = lanzone.id
    lanzone_pb2.name = lanzone.name
    lanzone_pb2.zone_type = lanzone.zone_type
    lanzone_pb2.min_vlan = lanzone.min_vlan
    lanzone_pb2.max_vlan = lanzone.max_vlan
    return lanzone_pb2

class vswitch_lanzone_service(vswitch_lanzone_pb2_grpc.vswitch_lanzoneServicer):
    def rpc_get_vswitch_lanzone(self, request, context):
        lanzone = None
        if request.per_uuid == True:
            lanzone = invt_get_vswitch_lan_zone(request.uuid)
        else:
            lanzones = invt_list_vswitch_lan_zones()
            for _lanzone_id in lanzones:
                _lanzone = lanzones[_lanzone_id]
                if _lanzone.name == request.lanzone_name:
                    lanzone = _lanzone
                    break
            assert(lanzone)
        return to_vswitch_lanzone_pb2(lanzone)        
    def rpc_list_vswitch_lanzones(self, request_iterator, context):
        lanzones = invt_list_vswitch_lan_zones()
        raw_lanzones = dict()
        for _key in request_iterator:
            if _key.per_uuid == True:
                raw_lanzones[_key.uuid] = invt_get_vswitch_lan_zone(_key.uuid)
            else:
                lanzone = None
                for _lanzone_id in lanzones:
                    _lanzone = lanzones[_lanzone_id]
                    if _lanzone.name == _key.lanzone_name:
                        lanzone = _lanzone
                        break
                assert(lanzone)
                raw_lanzones[lanzone.id] = lanzone
        _raw_lanzones = raw_lanzones if len(raw_lanzones) else lanzones
        for _lanzone_id in _raw_lanzones:
            _lanzone = _raw_lanzones[_lanzone_id]
            yield to_vswitch_lanzone_pb2(_lanzone)
    def rpc_register_vswitch_lanzone(self, request, context):
        create_spec = dict()
        create_spec['name'] = request.name
        create_spec['zone_type'] = request.zone_type
        create_spec['min_vlan'] = request.min_vlan
        create_spec['max_vlan'] = request.max_vlan
        lanzone = invt_register_vswitch_lan_zone(create_spec, user_sync = True)
        return to_vswitch_lanzone_pb2(lanzone)
    def rpc_unregister_vswitch_lanzone(self, request, context):
        invt_unregister_vswitch_lan_zone(request.uuid, user_sync = True)
        return common_pb2.null()
    def rpc_update_vswitch_lanzone(self, request, context):
        lanzone_uuid = request.id
        change_spec = dict()
        if request.zone_type != '':
            change_spec['zone_type'] = request.zone_type
        if request.min_vlan != 0:
            change_spec['min_vlan'] = request.min_vlan
        if request.max_vlan != 0:
            change_spec['max_vlan'] = request.max_vlan
        invt_update_vswitch_lan_zone(lanzone_uuid, change_spec, user_sync = True)
        return common_pb2.null()

publish_rpc_service(vswitch_lanzone_pb2_grpc.add_vswitch_lanzoneServicer_to_server, vswitch_lanzone_service)
