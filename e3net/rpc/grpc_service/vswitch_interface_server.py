#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.inventory.invt_vswitch_interface import invt_register_vswitch_interface
from e3net.inventory.invt_vswitch_interface import invt_update_vswitch_interface
from e3net.inventory.invt_vswitch_interface import invt_unregister_vswitch_interface
from e3net.inventory.invt_vswitch_interface import invt_get_vswitch_interface
from e3net.inventory.invt_vswitch_interface import invt_list_vswitch_interfaces
from e3net.rpc.protos_base import vswitch_interface_pb2
from e3net.rpc.protos_base import vswitch_interface_pb2_grpc
from e3net.rpc.protos_base import common_pb2
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT

def to_vswitch_interface_pb2(iface):
    pb2_iface = vswitch_interface_pb2.res_vswitch_interface()
    pb2_iface.id = iface.id
    pb2_iface.host_id = iface.host_id
    pb2_iface.dev_address = iface.dev_address
    pb2_iface.lanzone_id = iface.lanzone_id
    pb2_iface.interface_status = iface.interface_status
    pb2_iface.interface_type = iface.interface_type
    return pb2_iface

class vswitch_interface_service(vswitch_interface_pb2_grpc.vswitch_interfaceServicer):
    def rpc_get_vswitch_interface(self, request, context):
        iface = invt_get_vswitch_interface(request.uuid)
        return to_vswitch_interface_pb2(iface)

    def rpc_list_vswitch_interfaces(self, request_iterator, context):
        ifaces = invt_list_vswitch_interfaces()
        raw_ifaces = dict()
        key_null = True
        for key in request_iterator:
            key_null = False
            if key.uuid_type == 0:
                #interface uuid type
                raw_ifaces[key.uuid] = invt_get_vswitch_interface(key.uuid)
            elif key.uuid_type == 1:
                #host uuid type
                for _iface_id in ifaces:
                    _iface = ifaces[_iface_id]
                    if _iface.host_id == key.uuid:
                        raw_ifaces[_iface_id] = _iface
            elif key.uuid_type == 2:
                #lanzone uuid type
                for _iface_id in ifaces:
                    _iface = ifaces[_iface_id]
                    if _iface.lanzone_id == key.uuid:
                        raw_ifaces[_iface_id] = _iface
        _raw_ifaces = ifaces if key_null else raw_ifaces
        for _iface_id in _raw_ifaces:
            _iface = _raw_ifaces[_iface_id]
            yield to_vswitch_interface_pb2(_iface)

    def rpc_register_vswitch_interface(self, request, context):
        create_spec = dict()
        create_spec['host_id'] = request.host_id
        create_spec['dev_address'] = request.dev_address
        create_spec['lanzone_id'] = request.lanzone_id
        if request.interface_type != '':
            create_spec['interface_type'] = request.interface_type
        if request.interface_status != '':
            create_spec['interface_status'] != request.interface_status
        iface = invt_register_vswitch_interface(create_spec, user_sync = True)
        return to_vswitch_interface_pb2(iface)

    def rpc_unregister_vswitch_interface(self, request, context):
        invt_unregister_vswitch_interface(request.uuid, user_sync = True)
        return common_pb2.null()

    def rpc_update_vswitch_interface(self, request, context):
        iface_uuid = request.id
        change_spec = dict()
        #host_id and dev_address are not allowed to be changed
        if request.interface_status != '':
            change_spec['interface_status'] = request.interface_status
        if request.interface_type != '':
            change_spec['interface_type'] = request.interface_type
        if request.lanzone_id != '':
            change_spec['lanzone_id'] =request.lanzone_id
        invt_update_vswitch_interface(iface_uuid, change_spec, user_sync = True)
        return common_pb2.null()

publish_rpc_service(vswitch_interface_pb2_grpc.add_vswitch_interfaceServicer_to_server, vswitch_interface_service)
