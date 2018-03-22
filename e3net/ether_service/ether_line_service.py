#
#Copyright (c) 2018 Jie Zheng
#
from e3net.inventory.invt_base import get_inventory_base
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT
from e3net.ether_service.ether_service_common import EtherServiceCreateConfig
from e3net.inventory.invt_vswitch_lan_zone import invt_get_vswitch_lan_zone
from e3net.inventory.invt_vswitch_host import invt_get_vswitch_host
from e3net.inventory.invt_vswitch_interface import invt_get_vswitch_interface
from e3net.inventory.invt_vswitch_ether_service import invt_get_vswitch_ether_service
from e3net.inventory.invt_vswitch_lan_zone import invt_list_vswitch_lan_zones
from e3net.inventory.invt_vswitch_interface import invt_list_vswitch_interfaces
from e3net.inventory.invt_vswitch_host import invt_list_vswitch_hosts
from e3net.inventory.invt_vswitch_topology_edge import invt_list_vswitch_topology_edges
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_LINK_SHARED
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_LINK_EXCLUSIVE
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_TYPE_SHARED
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE
from e3net.common.e3log import get_e3loger
from e3net.inventory.invt_vswitch_topology_edge import invt_register_vswitch_topology_edge

e3loger = get_e3loger('e3vswitch_controller')


#
#make sure
#   'service_id' in iResult is prepared
#this phase will prepare lanzones/hosts/interfaces in iResult
#and remove any duplicated items
def _prefetch_create_config(config, iResult):
    assert (len(config['initial_lanzones']))
    #prepare all essential object
    #this will remove those duplicated ITEM. and may raise an exception if not found
    iResult['initial_lanzones'] = list()
    for l in config['initial_lanzones']:
        iResult['initial_lanzones'].append(l)
    e3loger.debug('initial lanzones:%s' % (iResult['initial_lanzones']))

    iResult['ban_hosts'] = list()
    for h in config['ban_hosts']:
        iResult['ban_hosts'].append(h)
    e3loger.debug('banned hosts:%s' % (iResult['ban_hosts']))

    iResult['ban_lanzones'] = list()
    for l in config['ban_lanzones']:
        iResult['ban_lanzones'].append(l)
    e3loger.debug('banned lanzones:%s' % (iResult['ban_lanzones']))

    iResult['ban_interfaces'] = list()
    for i in config['ban_interfaces']:
        iResult['ban_interfaces'].append(i)
    e3loger.debug('banned interfaces:%s' % (iResult['ban_interfaces']))
    #make sure initial_lanzones do not overlap with ban_lanzones
    bl = iResult['ban_lanzones']
    for il in iResult['initial_lanzones']:
        if il in bl:
            raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)


def _create_ether_line_topology(config, iResult):
    #if it's a solo customer lan zone,it's a NULL graphic
    if len(iResult['initial_lanzones']) == 1:
        return
    assert (len(iResult['initial_lanzones']) == 2)
    assert (len(config['initial_lanzones']) == 2)
    e_line = invt_get_vswitch_ether_service(iResult['service_id'])
    #
    #using Dijkstra Algorithm to determine the shortest path
    #between the two customer lan zones.
    #
    #let the tuple lanzone_id:<path_wright,<downstream_iface,host(vswitch),upstream_iface>> to
    #denote the lanzone-2-lanzone graphic edge
    infinite_weight = 0x7fffffff
    lanzones = invt_list_vswitch_lan_zones()
    hosts = invt_list_vswitch_hosts()
    interfaces = invt_list_vswitch_interfaces()
    edges = invt_list_vswitch_topology_edges()
    iface_weight = dict()
    permanent_lanzone_set = dict()
    permanent_host_set = list()
    temporary_lanzone_set = dict()
    start_lanzone = config['initial_lanzones'][0]
    end_lanzone = config['initial_lanzones'][1]

    #
    #initialize the edge's weight
    #and calculate the weight of these interfaces which are already in the topology
    for iface_id in interfaces:
        iface_weight[iface_id] = 0
    for edge_id in edges:
        edge = edges[edge_id]
        iface0 = edge.interface0
        iface1 = edge.interface1
        iface_weight[iface0] = iface_weight[iface0] + 1
        iface_weight[iface1] = iface_weight[iface1] + 1
    #
    #remove the banned lanzones
    #
    for banned_lanzone in iResult['ban_lanzones']:
        assert (banned_lanzone in lanzones)
        e3loger.debug('banned lanzone:', banned_lanzone)
    #
    #remove the banned hosts
    #
    for banned_host in iResult['ban_hosts']:
        assert (banded_host in hosts)
        e3loger.debug('banned host:', banded_host)
    #
    #remove the banned Interface
    #
    for banned_iface in iResult['ban_interfaces']:
        assert (banned_iface in interfaces)
        e3loger.debug('banned interface:', banned_iface)
    #
    #initialize the temporary lanzone set,
    #with the format:lanzone_id:<path_wright,<iface0,node,iface1>>
    #
    for lanzone_id in lanzones:
        if lanzone_id != start_lanzone:
            temporary_lanzone_set[lanzone_id] = (infinite_weight, (None, None, None))
        else:
            temporary_lanzone_set[lanzone_id] = (0, (None, None, None))
    #
    #to improve the efficiency to search interfaces with lanzone/host
    #split interfaces list into these two maps. note this will ve used several times
    #
    lanzone_2_iface = dict()
    host_2_iface = dict()
    for _iface_id in interfaces:
        iface = interfaces[_iface_id]
        lanzone_id = iface.lanzone_id
        host_id = iface.host_id
        if lanzone_id not in lanzone_2_iface:
            lanzone_2_iface[lanzone_id] = set()
        assert (lanzone_id in lanzone_2_iface)
        lanzone_2_iface[lanzone_id].add(_iface_id)
        if host_id not in host_2_iface:
            host_2_iface[host_id] = set()
        assert (host_id in host_2_iface)
        host_2_iface[host_id].add(_iface_id)
    #
    #main loop to find shortest path fpr E-LINE service
    #
    while True:
        #find a lanzone from temporary lanzone set with least path weight
        target_lanzone_id = None
        for lanzone_id in temporary_lanzone_set:
            weight, path = temporary_lanzone_set[lanzone_id]
            if weight >= infinite_weight:
                continue
            if not target_lanzone_id:
                target_lanzone_id = lanzone_id
            elif temporary_lanzone_set[target_lanzone_id][0] > weight:
                target_lanzone_id = lanzone_id
        if not target_lanzone_id:
            break
        #now target_lanzone_id is the one that should go to permanent lanzone set
        weight, path = temporary_lanzone_set[target_lanzone_id]
        iface0, host, iface1 = path
        permanent_host_set.append(host)
        permanent_lanzone_set[target_lanzone_id] = (weight, path)
        del temporary_lanzone_set[target_lanzone_id]
        if target_lanzone_id == end_lanzone:
            break
        #update all the neighbors(which are still in the temporary set)' weight
        p_lanzone_id = target_lanzone_id
        #find the possible hosts in the path, and record their weight along with interfaces
        intermediate_host = dict()
        for _iface_id in lanzone_2_iface[p_lanzone_id]:
            if _iface_id in iResult['ban_interfaces']:
                continue
            iface = interfaces[_iface_id]
            if iface.host_id in permanent_host_set or \
                iface.host_id in iResult['ban_hosts']:
                continue
            if e_line.link_type == E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
                if iface.interface_type!=E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE or \
                    iface_weight[_iface_id]!=0:
                    continue
            else:
                if iface.interface_type != E3VSWITCH_INTERFACE_TYPE_SHARED:
                    continue
            if iface.host_id not in intermediate_host:
                intermediate_host[iface.host_id] = _iface_id
            elif iface_weight[_iface_id] < iface_weight[intermediate_host[iface.
                                                                          host_id]]:
                intermediate_host[iface.host_id] = _iface_id
        #until now, the first part of the edge composition is finished
        #next ro do is to find the possible next lanzone in the path
        intermediate_lanzone = dict()
        for _host_id in intermediate_host:
            assert (_host_id not in permanent_host_set)
            host = hosts[_host_id]
            for _iface_id in host_2_iface[_host_id]:
                iface = interfaces[_iface_id]
                if iface.lanzone_id not in temporary_lanzone_set or \
                    iface.lanzone_id in iResult['ban_lanzones']:
                    continue
                if e_line.link_type == E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
                    if iface.interface_type!=E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE or \
                        iface_weight[_iface_id]!=0:
                        continue
                else:
                    if iface.interface_type != E3VSWITCH_INTERFACE_TYPE_SHARED:
                        continue
                if iface.lanzone_id not in intermediate_lanzone:
                    intermediate_lanzone[iface.lanzone_id] = (
                        _iface_id, _host_id, intermediate_host[_host_id])
                elif iface_weight[_iface_id]+iface_weight[intermediate_host[_host_id]]< \
                    iface_weight[intermediate_lanzone[iface.lanzone_id][0]]+ \
                    iface_weight[intermediate_lanzone[iface.lanzone_id][2]]:
                    intermediate_lanzone[iface.lanzone_id] = (
                        _iface_id, _host_id, intermediate_host[_host_id])
        #until now,let's update the neighbours's weight along with previous path
        for _lanzone_id in intermediate_lanzone:
            iface0_id = intermediate_lanzone[_lanzone_id][0]
            host_id = intermediate_lanzone[_lanzone_id][1]
            iface1_id = intermediate_lanzone[_lanzone_id][2]
            iface1 = interfaces[iface1_id]
            edge_weight = iface_weight[iface0_id] + iface_weight[iface1_id]
            _prev_lanzone_id = iface1.lanzone_id
            assert (_prev_lanzone_id == target_lanzone_id)
            _prev_weight, _ = permanent_lanzone_set[_prev_lanzone_id]
            _neighbor_weight, _ = temporary_lanzone_set[_lanzone_id]
            if _neighbor_weight > (_prev_weight + edge_weight):
                temporary_lanzone_set[_lanzone_id] = (
                    _prev_weight + edge_weight, (iface0_id, host_id,
                                                 iface1_id))
    #dump the calculation footprint
    e3loger.debug('permanent lanzone set:')
    for lanzone_id in permanent_lanzone_set:
        weight, path = permanent_lanzone_set[lanzone_id]
        iface0, host, iface1 = path
        e3loger.debug('\tlanzone_id:%s' % (
            lanzone_id) + ':<weight:%d,<iface0:%s,host:%s,iface1:%s>>' %
                      (weight, iface0, host, iface1))
    e3loger.debug('temporary lanzone set:')
    for lanzone_id in temporary_lanzone_set:
        weight, path = temporary_lanzone_set[lanzone_id]
        iface0, host, iface1 = path
        e3loger.debug('\tlanzone_id:%s' % (
            lanzone_id) + ':<weight:%d,<iface0:%s,host:%s,iface1:%s>>' %
                      (weight, iface0, host, iface1))
    e3loger.debug('permanent host set:')
    for host_id in permanent_host_set:
        e3loger.debug('\thost_id:%s' % (host_id))
    iResult['permanent_lanzone_set'] = permanent_lanzone_set
    iResult['temporary_lanzone_set'] = temporary_lanzone_set
    iResult['permanent_host_set'] = permanent_host_set


def _validate_ether_line_topology(config, iResult):
    permanent_lanzone_set = iResult['permanent_lanzone_set']
    temporary_lanzone_set = iResult['temporary_lanzone_set']
    permanent_host_set = iResult['permanent_host_set']
    lanzones = invt_list_vswitch_lan_zones()
    hosts = invt_list_vswitch_hosts()
    interfaces = invt_list_vswitch_interfaces()
    start_lanzone_id = config['initial_lanzones'][0]
    end_lanzone_id = config['initial_lanzones'][1]
    e_line = invt_get_vswitch_ether_service(iResult['service_id'])
    iface_type = E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE
    if e_line.link_type != E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
        iface_type = E3VSWITCH_INTERFACE_TYPE_SHARED
    target_lanzone_id = end_lanzone_id
    while True:
        weight, path = permanent_lanzone_set[target_lanzone_id]
        iface0_id, host_id, iface1_id = path
        if not host_id:
            assert (target_lanzone_id == start_lanzone_id)
            break
        iface0 = interfaces[iface0_id]
        host = hosts[host_id]
        iface1 = interfaces[iface1_id]
        assert (iface0.lanzone_id == target_lanzone_id)
        assert (iface0.host_id == host_id)
        assert (iface0.interface_type == iface_type)
        assert (iface1.host_id == host_id)
        assert (iface1.interface_type == iface_type)
        target_lanzone_id = iface1.lanzone_id


def _create_ether_line_topology_edge(config, iResult):
    permanent_lanzone_set = iResult['permanent_lanzone_set']
    lanzones = invt_list_vswitch_lan_zones()
    hosts = invt_list_vswitch_hosts()
    interfaces = invt_list_vswitch_interfaces()
    start_lanzone_id = config['initial_lanzones'][0]
    end_lanzone_id = config['initial_lanzones'][1]
    e_line = invt_get_vswitch_ether_service(iResult['service_id'])
    target_lanzone_id = end_lanzone_id
    while True:
        weight, path = permanent_lanzone_set[target_lanzone_id]
        iface0_id, host_id, iface1_id = path
        if not host_id:
            break
        spec = dict()
        spec['interface0'] = iface0_id
        spec['interface1'] = iface1_id
        spec['service_id'] = e_line.id
        invt_register_vswitch_topology_edge(spec)
        target_lanzone_id = interfaces[iface1_id].lanzone_id

def create_ether_line_topology(config, iResult):
    _prefetch_create_config(config, iResult)
    _create_ether_line_topology(config, iResult)
    _validate_ether_line_topology(config, iResult)
    _create_ether_line_topology_edge(config, iResult)
