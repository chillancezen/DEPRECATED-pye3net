#
#Copyright (c) 2018 Jie Zheng
#
from e3net.common.e3standalone_taskflow import e3standalone_taskflow
from taskflow import task
from taskflow.patterns import linear_flow
from e3net.inventory.invt_base import get_inventory_base
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT
from e3net.common.e3def import ETHER_SERVICE_TASKFLOW_APPLIANCE
from e3net.common.e3standalone_taskflow import register_standalone_taskflow_category
from e3net.rpc.grpc_service.topology_edge_client import rpc_client_list_topology_edges_for_services
from e3net.rpc.grpc_service.topology_edge_client import rpc_service as topology_edge_rpc_service
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_service as vswitch_interface_rpc_service
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_list_vswitch_interfaces
from e3net.rpc.grpc_service.vswitch_lanzone_client import rpc_client_list_vswitch_lanzones
from e3net.rpc.grpc_service.vswitch_lanzone_client import rpc_service as vswitch_lanzone_rpc_service
from e3net.rpc.grpc_service.vswitch_host_client import rpc_client_list_vswitch_hosts
from e3net.rpc.grpc_service.vswitch_host_client import rpc_service as vswitch_host_rpc_service
from e3net.common.e3log import get_e3loger
from e3net.e3neta.e3neta_config import get_host_agent
from e3net.rpc.grpc_client import get_stub

e3loger = get_e3loger('e3neta')


def retrieve_topology_elements(service, iResult):
    agent = get_host_agent()
    topology_edge_stub = get_stub(agent.current_controller,
        agent.controller_port,
        topology_edge_rpc_service)
    vswitch_interface_stub = get_stub(agent.current_controller,
        agent.controller_port,
        vswitch_interface_rpc_service)
    vswitch_lanzone_stub = get_stub(agent.current_controller,
        agent.controller_port,
        vswitch_lanzone_rpc_service)
    vswitch_host_stub = get_stub(agent.current_controller,
        agent.controller_port,
        vswitch_host_rpc_service)
    e3loger.info('applying service: %s' % (service))
    _edges = rpc_client_list_topology_edges_for_services(topology_edge_stub, [service])
    edges = {_edge.id : _edge for _edge in _edges}
    _iface_list = set()
    for _edge_id in edges:
        _edge = edges[_edge_id]
        _iface_list.add(_edge.interface0)
        _iface_list.add(_edge.interface1)
    _ifaces = rpc_client_list_vswitch_interfaces(vswitch_interface_stub, _iface_list)
    ifaces = {_iface.id : _iface for _iface in _ifaces}
    _lanzone_list = set()
    _host_list = set()
    for _iface_id in ifaces:
        _iface = ifaces[_iface_id]
        _lanzone_list.add(_iface.lanzone_id)
        _host_list.add(_iface.host_id)
    _lanzones = rpc_client_list_vswitch_lanzones(vswitch_lanzone_stub, uuid_list = _lanzone_list)
    lanzones = {_lanzone.id : _lanzone for _lanzone in _lanzones}
    _hosts = rpc_client_list_vswitch_hosts(vswitch_host_stub, uuid_list = _host_list)
    hosts = {_host.id : _host for _host in _hosts}
    iResult['edges'] = edges
    iResult['interfaces'] = ifaces
    iResult['lanzones'] = lanzones
    iResult['hosts'] = hosts
    print(iResult)
class ether_service_taskflow_prefetch_service_elements(task.Task):
    def execute(self, config, iResult):
        services = config['services']
        for service in services:
            retrieve_topology_elements(service, iResult)


def generate_ether_service_apply_ops_taskflow():
    lf = linear_flow.Flow(ETHER_SERVICE_TASKFLOW_APPLIANCE)
    lf.add(ether_service_taskflow_prefetch_service_elements())
    return lf

register_standalone_taskflow_category(ETHER_SERVICE_TASKFLOW_APPLIANCE,
    generate_ether_service_apply_ops_taskflow)

if __name__ == '__main__':
    from e3net.common.e3standalone_taskflow import e3standalone_taskflow
    from e3net.common.e3standalone_taskflow import standalone_taskflow_init
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    from e3net.e3neta.e3neta_config import e3neta_config_init
    add_config_file('/etc/e3net/e3neta.ini.1')
    load_configs()
    e3neta_config_init()
    standalone_taskflow_init()
    spec = dict()
    spec['services'] = ['3bfb6124-61e6-4698-b3ad-84f7e36da2ca']
    tf = e3standalone_taskflow(ETHER_SERVICE_TASKFLOW_APPLIANCE,
        sync = False,
        store = {'config' : spec, 'iResult' : dict()})
    tf.issue()
