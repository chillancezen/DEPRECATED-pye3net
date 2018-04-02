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
        pass


publish_rpc_service(vswitch_interface_pb2_grpc.add_vswitch_interfaceServicer_to_server, vswitch_interface_service)
