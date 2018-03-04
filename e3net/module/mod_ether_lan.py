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
from e3net.module.mod_common import EtherServiceCreateConfig
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
from e3net.common.e3log import get_e3loger
from e3net.inventory.invt_vswitch_topology_edge import invt_register_vswitch_topology_edge
#share the same config prefetch function
from e3net.module.mod_ether_line import _prefetch_create_config

e3loger=get_e3loger('e3vswitch_controller')
def _create_ether_lan_topology(config,iResult):
    if len(iResult['initial_lanzones'])==1:
        return
    assert(len(iResult['initial_lanzones'])>=2)
    assert(len(config['initial_lanzones'])>=2)
    #
    #use Prim's algorithm to determine the minimum spanning tree aamong lanzones
    #
    e_lan=iResult['ether_service']
    infinite_weight=0x7fffffff
    lanzones=invt_list_vswitch_lan_zones()
    hosts=invt_list_vswitch_hosts()
    interfaces=invt_list_vswitch_interfaces()
    edges=invt_list_vswitch_topology_edges()
    iface_weight=dict()
    #
    #initialize the edge's weight
    #and calculate the weight of these interfaces which are already in the topology
    for iface_id in interfaces:
        iface_weight[iface_id]=0
    for edge_id in edges:
        edge=edges[edge_id]
        iface0=edge.interface0
        iface1=edge.interface1
        iface_weight[iface0]=iface_weight[iface0]+1
        iface_weight[iface1]=iface_weight[iface1]+1
    #
    #remove the banned lanzones
    #
    for banned_lanzone in iResult['ban_lanzones']:
        assert(banned_lanzone in lanzones)
        del lanzones[banned_lanzone]
        e3loger.debug('banned lanzone:',banned_lanzone)
    #
    #remove the banned hosts
    #
    for banned_host in iResult['ban_hosts']:
        assert(banded_host in hosts)
        del hosts[banded_host]
        e3loger.debug('banned host:',banded_host)
    #
    #remove the banned Interface
    #
    for banned_iface in iResult['ban_interfaces']:
        assert(banned_iface in interfaces)
        del interfaces[banned_iface]
        e3loger.debug('banned interface:',banned_iface)
    #
    #to improve the efficiency to search interfaces with lanzone/host
    #split interfaces list into these two maps. note this will ve used several times
    #
    lanzone_2_iface=dict()
    host_2_iface=dict()
    for _iface_id in interfaces:
        iface=interfaces[_iface_id]
        lanzone_id=iface.lanzone_id
        host_id=iface.host_id
        if lanzone_id not in lanzone_2_iface:
            lanzone_2_iface[lanzone_id]=set()
        assert(lanzone_id in lanzone_2_iface)
        lanzone_2_iface[lanzone_id].add(_iface_id)
        if host_id not in host_2_iface:
            host_2_iface[host_id]=set()
        assert(host_id in host_2_iface)
        host_2_iface[host_id].add(_iface_id)
    #
    #setup intermediate variables
    #
    permanent_lanzone_set=dict()
    permanent_host_set=set()
    temporary_lanzone_set=set()
    unused_lanzone_set=set()
    start_lanzone_id=iResult['initial_lanzones'][0]
    for lanzone_id in lanzones:
        lanzone=lanzones[lanzone_id]
        if lanzone.zone_type==E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER and \
            lanzone_id not in iResult['initial_lanzones']:
            unused_lanzone_set.add(lanzone_id)
        elif lanzone_id==start_lanzone_id:
            permanent_lanzone_set.add(lanzone_id)
        else:
            temporary_lanzone_set.add(lanzone_id)
    #
    #enter main loop of Prim'a algorithm
    #for each iteration, find the edge with least weight among all temporary neighbors
    while True:
        _next_least_edge_weight=infinite_weight
        _next_lanzone_id=None
        _next_iface0_id=None
        _next_iface1_id=None
        _next_host_id=None
        for p_lanzone_id in permanent_lanzone_set:
            #find the bottom half of the topology edge
            intermediate_host=dict()
            for _iface_id in lanzone_2_iface[p_lanzone_id]:
                iface=interfaces[_iface_id]
                if iface.host_id in permanent_host_set:
                    continue
                if e_lan.link_type==E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
                    if iface.interface_type!=E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE or \
                        iface_weight[_iface_id]!=0:
                        continue
                else:
                    if iface.interface_type!=E3VSWITCH_INTERFACE_TYPE_SHARED:
                        continue
                if iface.host_id not in intermediate_host:
                    intermediate_host[iface.host_id]=_iface_id
                elif iface_weight[_iface_id]<iface_weight[intermediate_host[iface.host_id]]:
                    intermediate_host[iface.host_id]=_iface_id
            #find the top half of the topology edge
            intermediate_lanzone=dict()
            for _host_id in intermediate_host:
                assert(_host_id not in permanent_host_set)
                host=hosts[_host_id]
                for _iface_id in host_2_iface[_host_id]:
                    iface=interfaces[_iface_id]
                    if iface.lanzone_id not in temporary_lanzone_set:
                        continue
                    if e_line.link_type==E3NET_ETHER_SERVICE_LINK_EXCLUSIVE:
                        if iface.interface_type!=E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE or \
                            iface_weight[_iface_id]!=0:
                            continue
                    else:
                        if iface.interface_type!=E3VSWITCH_INTERFACE_TYPE_SHARED:
                            continue
                    if iface.lanzone_id not in intermediate_lanzone:
                        intermediate_lanzone[iface.lanzone_id]=(_iface_id,_host_id,intermediate_host[_host_id])
                    elif iface_weight[_iface_id]+iface_weight[intermediate_host[_host_id]]< \
                        iface_weight[intermediate_lanzone[iface.lanzone_id][0]]+ \
                        iface_weight[intermediate_lanzone[iface.lanzone_id][2]]:
                        intermediate_lanzone[iface.lanzone_id]=(_iface_id,_host_id,intermediate_host[_host_id])
            #find the least weighted topology edge for p_lanzone_id
            for _immediate_lanzone_id in intermediate_lanzone:
                iface0_id,host_id,iface1_id=intermediate_lanzone[_immediate_lanzone_id]
                _edge_weight=iface_weight[iface0_id]+iface_weight[iface1_id]
                if not _next_lanzone_id or \
                    _edge_weight<_next_least_edge_weight:
                    _next_lanzone_id=_immediate_lanzone_id
                    _next_iface0_id=iface0_id
                    _next_iface1_id=iface1_id
                    _next_host_id=host_id
                    _next_least_edge_weight=_edge_weight
        if not _next_lanzone_id:
            break
        permanent_lanzone_set[_next_lanzone_id]=(_next_least_edge_weight,(_next_iface0_id,_next_host_id,_next_iface1_id))
        permanent_host_set.add(_next_host_id)
        temporary_lanzone_set.remove(_next_lanzone_id)

def create_ether_lan_topology(config,iResult):
    _prefetch_create_config(config,iResult)
    _create_ether_lan_topology(config,iResult)
