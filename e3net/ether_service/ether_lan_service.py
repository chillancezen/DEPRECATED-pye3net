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
from e3net.ether_service.ether_service_common import EtherLANServiceUpdateConfig
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
from e3net.db.db_vswitch_lan_zone import E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER
from e3net.db.db_vswitch_lan_zone import E3VSWITCH_LAN_ZONE_TYPE_BACKBONE
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_TYPE_LINE
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_TYPE_LAN
from e3net.inventory.invt_vswitch_topology_edge import invt_list_vswitch_topology_edges
from e3net.common.e3log import get_e3loger
from e3net.inventory.invt_vswitch_topology_edge import invt_register_vswitch_topology_edge
#share the same config prefetch function
from e3net.ether_service.ether_line_service import _prefetch_create_config
e3loger = get_e3loger('e3vswitch_controller')


def _create_ether_lan_topology(config, iResult):
    if len(iResult['initial_lanzones']) == 1:
        return
    assert (len(iResult['initial_lanzones']) >= 2)
    assert (len(config['initial_lanzones']) >= 2)
    #
    #use Prim's algorithm to determine the minimum spanning tree aamong lanzones
    #
    e_lan = iResult['ether_service']
    infinite_weight = 0x7fffffff
    lanzones = invt_list_vswitch_lan_zones()
    hosts = invt_list_vswitch_hosts()
    interfaces = invt_list_vswitch_interfaces()
    edges = invt_list_vswitch_topology_edges()
    iface_weight = dict()
    e3loger.debug('original lanzones set:')
    for lanzone_id in lanzones:
        e3loger.debug('\t%s' % (lanzones[lanzone_id]))
    e3loger.debug('original host set:')
    for host_id in hosts:
        e3loger.debug('\t%s' % (hosts[host_id]))
    e3loger.debug('original interface set:')
    for iface_id in interfaces:
        e3loger.debug('\t%s' % (interfaces[iface_id]))
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
    e3loger.debug('interface weight:')
    for iface_id in iface_weight:
        e3loger.debug('\t%s:%s' % (iface_id, iface_weight[iface_id]))
    #
    #remove the banned lanzones
    #
    for banned_lanzone in iResult['ban_lanzones']:
        assert (banned_lanzone in lanzones)
        del lanzones[banned_lanzone]
        e3loger.debug('banned lanzone:', banned_lanzone)
    #
    #remove the banned hosts
    #
    for banned_host in iResult['ban_hosts']:
        assert (banded_host in hosts)
        del hosts[banded_host]
        e3loger.debug('banned host:', banded_host)
    #
    #remove the banned Interface
    #
    for banned_iface in iResult['ban_interfaces']:
        assert (banned_iface in interfaces)
        del interfaces[banned_iface]
        e3loger.debug('banned interface:', banned_iface)
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
    e3loger.debug('lanzone to interface mapping:')
    for lanzone_id in lanzone_2_iface:
        e3loger.debug('    lanzone id:%s' % (lanzone_id))
        for iface_id in lanzone_2_iface[lanzone_id]:
            e3loger.debug('        %s' % (iface_id))
    e3loger.debug('host to interface mapping:')
    for host_id in host_2_iface:
        e3loger.debug('   host id:%s' % (host_id))
        for iface_id in host_2_iface[host_id]:
            e3loger.debug('        %s' % (iface_id))
    #
    #setup intermediate variables
    #
    permanent_lanzone_set = dict()
    temporary_lanzone_set = set()
    unused_lanzone_set = set()
    start_lanzone_id = config['initial_lanzones'][0]
    for lanzone_id in lanzones:
        lanzone = lanzones[lanzone_id]
        if lanzone.zone_type==E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER and \
            lanzone_id not in iResult['initial_lanzones']:
            unused_lanzone_set.add(lanzone_id)
        elif lanzone_id == start_lanzone_id:
            permanent_lanzone_set[lanzone_id] = (0, (None, None, None))
        else:
            temporary_lanzone_set.add(lanzone_id)
    e3loger.debug('start lanzone id:%s' % (start_lanzone_id))
    e3loger.debug('permanent lanzone set:%s' % (permanent_lanzone_set))
    e3loger.debug('temporary lanzone set:%s' % (temporary_lanzone_set))
    e3loger.debug('unused_lanzone_set:%s' % (unused_lanzone_set))
    #
    #enter main loop of Prim'a algorithm
    #for each iteration, find the edge with least weight among all temporary neighbors
    debug_counter = 0
    g_degree = dict()
    while True:
        _next_least_edge_weight = infinite_weight
        _next_lanzone_id = None
        _next_iface0_id = None
        _next_iface1_id = None
        _next_host_id = None
        e3loger.debug('enter round %s' % (debug_counter))
        debug_counter = debug_counter + 1
        for p_lanzone_id in permanent_lanzone_set:
            e3loger.debug('choose permanent lanzone:%s' % (p_lanzone_id))
            #find the bottom half of the topology edge
            intermediate_host = dict()
            for _iface_id in lanzone_2_iface[p_lanzone_id]:
                iface = interfaces[_iface_id]
                if e_lan.link_type == E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
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
            e3loger.debug('intermediate_host:%s' % (intermediate_host))
            #find the top half of the topology edge
            intermediate_lanzone = dict()
            for _host_id in intermediate_host:
                host = hosts[_host_id]
                for _iface_id in host_2_iface[_host_id]:
                    iface = interfaces[_iface_id]
                    if iface.lanzone_id not in temporary_lanzone_set:
                        continue
                    if e_lan.link_type == E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
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
            e3loger.debug('intermediate_lanzone:%s' % (intermediate_lanzone))
            #find the least weighted topology edge for p_lanzone_id
            for _immediate_lanzone_id in intermediate_lanzone:
                iface0_id, host_id, iface1_id = intermediate_lanzone[
                    _immediate_lanzone_id]
                _edge_weight = iface_weight[iface0_id] + iface_weight[iface1_id]
                #prevent customer lanzone from being a immediate backbone lanzone
                #i.e. if the customer lanzone is already in the permanent lanzone set,
                #skip it.
                _iface1 = interfaces[iface1_id]
                if _iface1.lanzone_id in g_degree and \
                    lanzones[_iface1.lanzone_id].zone_type==E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER and \
                    g_degree[_iface1.lanzone_id]==1:
                    continue
                #two customer lanzones can not constitute a topology edge
                _iface0 = interfaces[iface0_id]
                if lanzones[_iface1.lanzone_id].zone_type==E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER and \
                    lanzones[_iface0.lanzone_id].zone_type==E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER:
                    continue
                if not _next_lanzone_id or \
                    _edge_weight<_next_least_edge_weight:
                    _next_lanzone_id = _immediate_lanzone_id
                    _next_iface0_id = iface0_id
                    _next_iface1_id = iface1_id
                    _next_host_id = host_id
                    _next_least_edge_weight = _edge_weight
        if not _next_lanzone_id:
            break
        #update g_degree for every edge
        if _next_lanzone_id not in g_degree:
            g_degree[_next_lanzone_id] = 1
        else:
            g_degree[_next_lanzone_id] = g_degree[_next_lanzone_id] + 1
        iface1 = interfaces[_next_iface1_id]
        if iface1.lanzone_id not in g_degree:
            g_degree[iface1.lanzone_id] = 1
        else:
            g_degree[iface1.lanzone_id] = g_degree[iface1.lanzone_id] + 1
        permanent_lanzone_set[_next_lanzone_id] = (_next_least_edge_weight,
                                                   (_next_iface0_id,
                                                    _next_host_id,
                                                    _next_iface1_id))
        temporary_lanzone_set.remove(_next_lanzone_id)
        e3loger.debug('add topology %s:%s' %
                      (_next_lanzone_id,
                       permanent_lanzone_set[_next_lanzone_id]))
    #
    #remove those backbones to which no customer lanzones are attached,
    #we call these lanzones orphaned
    while True:
        should_terminate = True
        degree = dict()
        for lanzone_id in permanent_lanzone_set:
            weight, path = permanent_lanzone_set[lanzone_id]
            iface0_id, host_id, iface1_id = path
            if not host_id:
                continue
            iface1 = interfaces[iface1_id]
            if lanzone_id not in degree:
                degree[lanzone_id] = 1
            else:
                degree[lanzone_id] = degree[lanzone_id] + 1
            if iface1.lanzone_id not in degree:
                degree[iface1.lanzone_id] = 1
            else:
                degree[iface1.lanzone_id] = degree[iface1.lanzone_id] + 1
        for lanzone_id in degree:
            lanzone = lanzones[lanzone_id]
            if degree[lanzone_id] == 1 and lanzone.zone_type == E3VSWITCH_LAN_ZONE_TYPE_BACKBONE:
                del permanent_lanzone_set[lanzone_id]
                should_terminate = False
        if should_terminate:
            break
    for lanzone_id in permanent_lanzone_set:
        e3loger.debug('lanzone id:%s %s  %s' %
                      (lanzone_id, lanzones[lanzone_id].name,
                       permanent_lanzone_set[lanzone_id]))
    iResult['permanent_lanzone_set'] = permanent_lanzone_set
    iResult['temporary_lanzone_set'] = temporary_lanzone_set
    iResult['start_lanzone_id'] = start_lanzone_id
    iResult['lanzones'] = lanzones
    iResult['hosts'] = hosts
    iResult['interfaces'] = interfaces


def _validate_ether_lan_topology(config, iResult):
    lanzones = iResult['lanzones']
    hosts = iResult['hosts']
    interfaces = iResult['interfaces']
    start_lanzone_id = iResult['start_lanzone_id']
    temporary_lanzone_set = iResult['temporary_lanzone_set']
    permanent_lanzone_set = iResult['permanent_lanzone_set']
    initial_lanzone_set = iResult['initial_lanzones']
    e_lan = iResult['ether_service']
    iface_type = E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE
    if e_lan.link_type != E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
        iface_type = E3VSWITCH_INTERFACE_TYPE_SHARED
    degree = dict()
    for lanzone_id in permanent_lanzone_set:
        weight, path = permanent_lanzone_set[lanzone_id]
        iface0_id, host_id, iface1_id = path
        if not host_id:
            continue
        iface0 = interfaces[iface0_id]
        iface1 = interfaces[iface1_id]
        host = hosts[host_id]
        assert (iface0.interface_type == iface_type)
        assert (iface1.interface_type == iface_type)
        assert (iface0.host_id == host_id)
        assert (iface1.host_id == host_id)
        assert (iface0.lanzone_id == lanzone_id)
        if iface0.lanzone_id not in degree:
            degree[iface0.lanzone_id] = 1
        else:
            degree[iface0.lanzone_id] = degree[iface0.lanzone_id] + 1
        if iface1.lanzone_id not in degree:
            degree[iface1.lanzone_id] = 1
        else:
            degree[iface1.lanzone_id] = degree[iface1.lanzone_id] + 1
    for lanzone_id in degree:
        lanzone = lanzones[lanzone_id]
        if lanzone.zone_type == E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER:
            assert (degree[lanzone_id] == 1)
        else:
            assert (degree[lanzone_id] > 1)
    for lanzone_id in initial_lanzone_set:
        assert (lanzone_id in permanent_lanzone_set)
    #check whether a circle present
    #by search the path in Depth First manner
    vertext = dict()
    for _lanzone_id in permanent_lanzone_set:
        _, _path = permanent_lanzone_set[_lanzone_id]
        _iface0_id, _host_id, _iface1_id = _path
        if not _host_id:
            continue
        _lanzone0_id = interfaces[_iface0_id].lanzone_id
        _lanzone1_id = interfaces[_iface1_id].lanzone_id
        if _lanzone0_id not in vertext:
            vertext[_lanzone0_id] = set()
        vertext[_lanzone0_id].add(_lanzone1_id)
        if _lanzone1_id not in vertext:
            vertext[_lanzone1_id] = set()
        vertext[_lanzone1_id].add(_lanzone0_id)
    e3loger.debug('adjacency matrix:%s' % (vertext))
    assert (start_lanzone_id in vertext)
    used = set()
    path_stack = list()
    path_stack.append(start_lanzone_id)
    used.add(start_lanzone_id)
    e3loger.debug('circle tedection: push lanzone:%s' % (start_lanzone_id))
    next_lanzone_id = None
    while len(path_stack):
        current_lanzone_id = path_stack[-1]
        neighbors = vertext[current_lanzone_id]
        next_lanzone_id = None
        for _lanzone_id in neighbors:
            if _lanzone_id not in used:
                next_lanzone_id = _lanzone_id
                break
        if next_lanzone_id:
            assert (next_lanzone_id not in path_stack)
            path_stack.append(next_lanzone_id)
            used.add(next_lanzone_id)
            e3loger.debug('circle tedection: push lanzone:%s' %
                          (next_lanzone_id))
        else:
            poped_lanzone_id = path_stack.pop()
            e3loger.debug('circle tedection: pop lanzone:%s' %
                          (poped_lanzone_id))
    for _lanzone_id in initial_lanzone_set:
        assert (_lanzone_id in used)

def _create_ether_lan_topology_edge(config, iResult):
    interfaces = iResult['interfaces']
    permanent_lanzone_set = iResult['permanent_lanzone_set']
    e_lan = iResult['ether_service']
    for _lanzone_id in permanent_lanzone_set:
        _, _path = permanent_lanzone_set[_lanzone_id]
        _iface0_id, _host_id, _iface1_id = _path
        if not _host_id:
            continue
        spec = dict()
        spec['interface0'] = _iface0_id
        spec['interface1'] = _iface1_id
        spec['service_id'] = e_lan.id
        invt_register_vswitch_topology_edge(spec)

def _prefetch_ether_lan_update_config(config,iResult):
    iResult['ether_service']=invt_get_vswitch_ether_service(config['ether_lan_service_id'])
    assert(iResult['ether_service'].service_type==E3NET_ETHER_SERVICE_TYPE_LAN)
    iResult['operation']=config['operation']
    iResult['ban_hosts']=set()
    for _host in config['ban_hosts']:
        iResult['ban_hosts'].add(_host)
    e3loger.debug('banned hosts:%s'%(iResult['ban_hosts']))
    iResult['ban_lanzones']=set()
    for _lanzone in config['ban_lanzones']:
        iResult['ban_lanzones'].add(_lanzone)
    e3loger.debug('banned lanzones:%s'%(iResult['ban_lanzones']))
    iResult['ban_interfaces']=set()
    for _interface in config['ban_interfaces']:
        iResult['ban_interfaces'].add(_interface)
    e3loger.debug('banned interfaces:%s'%(iResult['ban_interfaces']))
    iResult['update_lanzones']=set()
    for _lanzone in config['update_lanzones']:
        iResult['update_lanzones'].add(_lanzone)
    e3loger.debug('lanzones to be updated:%s'%(iResult['update_lanzones']))

def _add_lanzones_to_ether_lan(ether_service_id,lanzones_to_be_added):
    #filter topology edges,only keep those edges whose service_id is equal to e_lan's id
    topology_edges=invt_list_vswitch_topology_edges()
    iResult['topology_edges']=dict()
    for _edge_id in topology_edges:
        edge=topology_edges[_edge_id]
        if edge.service_id!=e_lan.id:
            continue
        iResult['topology_edges'][_edge_id]=edge
     
    
def create_ether_lan_topology(config, iResult):
    _prefetch_create_config(config, iResult)
    _create_ether_lan_topology(config, iResult)
    _validate_ether_lan_topology(config, iResult)
    _create_ether_lan_topology_edge(config, iResult)
