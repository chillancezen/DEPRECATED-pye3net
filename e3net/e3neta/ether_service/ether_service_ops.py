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
from e3net.common.e3def import E3VSWITCH_LAN_ZONE_TYPE_BACKBONE
from e3net.common.e3def import E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER
from e3net.e3neta.db.db_topology_label import db_list_topology_labels
from e3net.e3neta.db.db_topology_label import db_update_topology_label
from e3net.e3neta.db.db_topology_label import db_get_topology_label
from e3net.e3neta.db.db_topology_label import db_delete_topology_label
from e3net.e3neta.db.db_topology_label import LABEL_DIRECTION_INGRESS
from e3net.e3neta.db.db_topology_label import DUMMY_MULTICAST_LANZONE
from e3net.e3neta.db.db_topology_neighbor import register_topology_neighbor
from e3net.e3neta.db.db_topology_neighbor import get_topology_neighbor_by_interfaces
from e3net.e3neta.db.db_ether_service import db_update_ether_service
from e3net.e3neta.db.db_ether_service import db_list_ether_service
from e3net.e3neta.db.db_ether_service import db_get_ether_service
from e3net.e3neta.db.db_ether_service import db_delete_ether_service

e3loger = get_e3loger('e3neta')


def retrieve_topology_elements(service_id, iResult):
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
    e3loger.info('applying service: %s' % (service_id))
    _edges = rpc_client_list_topology_edges_for_services(topology_edge_stub, [service_id])
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
    iResult['service_id'] = service_id
    iResult['service'] = db_update_ether_service(service_id)

def resolve_rechability_information(iResult):
    edges = iResult['edges']
    lanzones = iResult['lanzones']
    interfaces = iResult['interfaces']
    hosts = iResult['hosts']
    agent = get_host_agent()
    initial_edge_id = None
    local_host_id = agent.vswitch_host.id
    local_iface_ids = [agent.interfaces[_iface_name].vswitch_interface.id \
        for _iface_name in agent.interfaces]
    #map lanzone to interfaces
    lanzone_to_interface = dict()
    for _edge_id in edges:
        _edge = edges[_edge_id]
        _iface0_id = _edge.interface0
        _iface1_id = _edge.interface1
        _lanzone0_id = interfaces[_iface0_id].lanzone_id
        _lanzone1_id = interfaces[_iface1_id].lanzone_id
        if _lanzone0_id not in lanzone_to_interface:
            lanzone_to_interface[_lanzone0_id] = set()
        if _lanzone1_id not in lanzone_to_interface:
            lanzone_to_interface[_lanzone1_id] = set()
        lanzone_to_interface[_lanzone0_id].add(_iface0_id)
        lanzone_to_interface[_lanzone1_id].add(_iface1_id)
    #hostinterface_mapping
    host_interface_mappping = dict()
    for _edge_id in edges:
        _edge = edges[_edge_id]
        _iface0_id = _edge.interface0
        _iface1_id = _edge.interface1
        assert (interfaces[_iface0_id].host_id == interfaces[_iface1_id].host_id)
        _host_id = interfaces[_iface0_id].host_id
        if not initial_edge_id and local_host_id == _host_id:
            initial_edge_id = _edge_id
        if _host_id not in host_interface_mappping:
            host_interface_mappping[_host_id] = set()
        host_interface_mappping[_host_id].add(_iface0_id)
        host_interface_mappping[_host_id].add(_iface1_id)
    #interfaces neighbor mapping
    interface_neighbor_mapping = dict()
    for _lanzone_id in lanzone_to_interface:
        if len(lanzone_to_interface[_lanzone_id]) == 1:
            continue
        assert (len(lanzone_to_interface[_lanzone_id]) == 2)
        iface_lst = list(lanzone_to_interface[_lanzone_id])
        _iface0_id = iface_lst[0]
        _iface1_id = iface_lst[1]
        interface_neighbor_mapping[_iface0_id] = _iface1_id
        interface_neighbor_mapping[_iface1_id] = _iface0_id
    for _iface_id in interface_neighbor_mapping:
        _iface = interfaces[_iface_id]
        if _iface.host_id == local_host_id:
            register_topology_neighbor(_iface_id, interface_neighbor_mapping[_iface_id])
    #calculate the reachability information
    rechability_mapping = dict()
    used_edges = set()
    iface_stack = list()
    assert(initial_edge_id)
    used_edges.add(initial_edge_id)
    initial_edge = edges[initial_edge_id]
    initial_iface0_id = initial_edge.interface0
    initial_iface1_id = initial_edge.interface1
    lanzone0_id = interfaces[initial_iface0_id].lanzone_id
    lanzone1_id = interfaces[initial_iface1_id].lanzone_id
    rechability_mapping[lanzone0_id] = initial_iface0_id
    rechability_mapping[lanzone1_id] = initial_iface1_id
    iface_stack.append(initial_iface0_id)
    iface_stack.append(initial_iface1_id)
    next_iface = None
    while len(iface_stack):
        current_iface = iface_stack.pop()
        if interfaces[current_iface].host_id == local_host_id:
            next_iface = current_iface
        #find a free edge which is connected to current_iface
        current_lanzone = interfaces[current_iface].lanzone_id
        next_edge = None
        for _edge_id in edges:
            if _edge_id in used_edges:
                continue
            _edge = edges[_edge_id]
            _iface0_id = _edge.interface0
            _iface1_id = _edge.interface1
            _lanzone0_id = interfaces[_iface0_id].lanzone_id
            _lanzone1_id = interfaces[_iface1_id].lanzone_id
            if current_lanzone == _lanzone0_id or \
                current_lanzone == _lanzone1_id:
                next_edge = _edge
                break
        if next_edge:
            used_edges.add(next_edge.id)
            iface0_id = next_edge.interface0
            iface1_id = next_edge.interface1
            lanzone0_id = interfaces[iface0_id].lanzone_id
            lanzone1_id = interfaces[iface1_id].lanzone_id
            if lanzone0_id == current_lanzone:
                iface_stack.append(iface0_id)
                iface_stack.append(iface1_id)
                rechability_mapping[lanzone1_id] = iface1_id if \
                    interfaces[iface1_id].host_id == local_host_id else \
                    next_iface
            elif lanzone1_id == current_lanzone:
                iface_stack.append(iface1_id)
                iface_stack.append(iface0_id)
                rechability_mapping[lanzone0_id] = iface0_id if \
                    interfaces[iface0_id].host_id == local_host_id else \
                    next_iface
            else:
                assert(False)
    nexthop_ifaces = set(rechability_mapping.values())
    for _iface_id in nexthop_ifaces:
        assert (_iface_id in local_iface_ids)
    for lanzone_id in rechability_mapping:
        lanzone = lanzones[lanzone_id]
        if lanzone.zone_type == E3VSWITCH_LAN_ZONE_TYPE_BACKBONE:
            assert (rechability_mapping[lanzone_id] in interface_neighbor_mapping)
    iResult['interface_neighbor_mapping'] = interface_neighbor_mapping
    iResult['rechability_mapping'] = rechability_mapping
    iResult['host_interface_mappping'] = host_interface_mappping

def synchronize_topology_label(iResult):
    agent = get_host_agent()
    local_host_id = agent.vswitch_host.id
    interface_neighbor_mapping = iResult['interface_neighbor_mapping']
    host_interface_mappping = iResult['host_interface_mappping']
    rechability_mapping = iResult['rechability_mapping']
    service_id = iResult['service_id']
    service = iResult['service']
    interfaces = iResult['interfaces']
    lanzones = iResult['lanzones']
    hosts = iResult['hosts']
    edges = iResult['edges']
    interfaces_in_topology = [iface for iface in interface_neighbor_mapping if \
        interfaces[iface].host_id == local_host_id]
    backbone_interfaces = list()
    for _iface_id in interfaces_in_topology:
        _iface = interfaces[_iface_id]
        _lanzone_id = _iface.lanzone_id
        _lanzone = lanzones[_lanzone_id]
        if _lanzone.zone_type == E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER:
            continue
        backbone_interfaces.append(_iface_id)
    labels_in_vswitch = db_list_topology_labels(service_id)
    labels_to_apply = dict()
    for _lanzone_id in rechability_mapping:
        _nexthop = rechability_mapping[_lanzone_id]
        _lanzone = lanzones[_lanzone_id]
        if _lanzone.zone_type == E3VSWITCH_LAN_ZONE_TYPE_BACKBONE:
            continue
        for _adjacent_iface_id in backbone_interfaces:
            if _adjacent_iface_id == _nexthop:
                continue
            neighbor = get_topology_neighbor_by_interfaces(_adjacent_iface_id,
                interface_neighbor_mapping[_adjacent_iface_id])
            label = db_update_topology_label(customer_lanzone = _lanzone_id,
                interface_id = _adjacent_iface_id,
                neighbor_id = neighbor.id,
                direction = LABEL_DIRECTION_INGRESS,
                service_id = service_id)
            labels_to_apply[label.id] = label
    for _iface_id in backbone_interfaces:
        neighbor = get_topology_neighbor_by_interfaces(_iface_id,
            interface_neighbor_mapping[_iface_id])
        label = db_update_topology_label(customer_lanzone = DUMMY_MULTICAST_LANZONE,
            interface_id = _iface_id,
            neighbor_id = neighbor.id,
            direction = LABEL_DIRECTION_INGRESS,
            service_id = service_id)
        labels_to_apply[label.id] = label
    for _label_id in labels_to_apply:
        print(labels_to_apply[_label_id])
class ether_service_taskflow_prefetch_service_elements(task.Task):
    def execute(self, config, iResult):
        services = config['services']
        for service in services:
            _iResult = dict()
            retrieve_topology_elements(service, _iResult)
            resolve_rechability_information(_iResult)
            synchronize_topology_label(_iResult)
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
    from e3net.e3neta.e3neta_db import e3neta_db_init
    from e3net.e3neta.e3neta_agent_ops import e3neta_agent_connect
    add_config_file('/etc/e3net/e3neta.ini.1')
    load_configs()
    e3neta_config_init()
    standalone_taskflow_init()
    e3neta_db_init()
    e3neta_agent_connect()
    spec = dict()
    spec['services'] = ['3bfb6124-61e6-4698-b3ad-84f7e36da2ca']
    tf = e3standalone_taskflow(ETHER_SERVICE_TASKFLOW_APPLIANCE,
        sync = False,
        store = {'config' : spec, 'iResult' : dict()})
    tf.issue()
