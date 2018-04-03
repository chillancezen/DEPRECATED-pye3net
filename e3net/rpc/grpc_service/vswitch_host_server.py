#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.inventory.invt_vswitch_host import invt_register_vswitch_host
from e3net.inventory.invt_vswitch_host import invt_update_vswitch_host
from e3net.inventory.invt_vswitch_host import invt_unregister_vswitch_host
from e3net.inventory.invt_vswitch_host import invt_get_vswitch_host
from e3net.inventory.invt_vswitch_host import invt_list_vswitch_hosts
from e3net.rpc.protos_base import common_pb2
from e3net.rpc.protos_base import vswitch_host_pb2
from e3net.rpc.protos_base import vswitch_host_pb2_grpc
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT


def to_vswitch_host_pb2(host):
    pb2_host = vswitch_host_pb2.res_vswitch_host()
    pb2_host.id = host.id
    pb2_host.host_status = host.host_status
    if host.description:
        pb2_host.description = host.description
    pb2_host.name = host.name
    pb2_host.host_ip =host.host_ip
    return pb2_host

class vswitch_host_service(vswitch_host_pb2_grpc.vswitch_hostServicer):
    def rpc_get_vswitch_host(self, request, context):
        host = None
        if request.per_uuid == True:
            host = invt_get_vswitch_host(request.uuid)
        else:
            hosts = invt_list_vswitch_hosts()
            for _host_id in hosts:
                _host = hosts[_host_id]
                if _host.name == request.host_name:
                    host = _host
                    break
            if not host:
                raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return to_vswitch_host_pb2(host)

    def rpc_list_vswitch_hosts(self, request_iterator, context):
        hosts = invt_list_vswitch_hosts()
        raw_hosts = list()
        for key in request_iterator:
            if key.per_uuid == True:
                raw_hosts.append(invt_get_vswitch_host(key.uuid))
            else:
                host = None
                for _host_id in hosts:
                    _host = hosts[_host_id]
                    if _host.name == key.host_name:
                        host = _host
                        break
                if not host:
                    raise e3_exception(E3_EXCEPTION_NOT_FOUND)
                raw_hosts.append(host)
        _raw_hosts = raw_hosts if len(raw_hosts) else list(hosts.values())
        for _host in _raw_hosts:
            yield to_vswitch_host_pb2(_host)
    def rpc_register_vswiitch_host(self, request, context):
        create_spec = dict()
        create_spec['name'] = request.name
        create_spec['host_ip'] = request.host_ip
        create_spec['description'] = request.description
        if request.host_status != '':
            create_spec['host_status'] = request.host_status
        host = invt_register_vswitch_host(create_spec, user_sync = True)
        return to_vswitch_host_pb2(host)

    def rpc_unregister_vswitch_host(self, request, context):
        invt_unregister_vswitch_host(request.uuid, user_sync = True)
        return common_pb2.null()

    def rpc_update_vswitch_host(self, request, context):
        uuid = request.id
        change_spec = dict()
        if request.host_status != '':
            change_spec['host_status'] = request.host_status
        if request.description != '':
            change_spec['description'] = request.description
        if request.name != '':
            change_spec['name'] = request.name
        if request.host_ip != '':
            change_spec['host_ip'] = request.host_ip
        invt_update_vswitch_host(uuid, change_spec, user_sync = True)
        return common_pb2.null()

publish_rpc_service(vswitch_host_pb2_grpc.add_vswitch_hostServicer_to_server, vswitch_host_service)

if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    from e3net.rpc.grpc_server import grpc_server_init
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    grpc_server_init()
    import time
    time.sleep(1000)
