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

#
#make sure
#   'service_id' in iResult is prepared
#this phase will prepare lanzones/hosts/interfaces in iResult
#
def _prefetch_create_config(config,iResult):
    assert(len(config['initial_lanzones']))
    #prepare all essential object
    #this will remove those duplicated ITEM. and may raise an exception if not found
    iResult['initial_lanzones']=dict()
    for l in config['initial_lanzones']:
        iResult['initial_lanzones'][l]=invt_get_vswitch_lan_zone(l)
    iResult['ban_hosts']=dict()
    for h in config['ban_hosts']:
        iResult['ban_hosts'][h]=invt_get_vswitch_hosth(h)
    iResult['ban_lanzones']=dict()
    for l in config['ban_lanzones']:
        iResult['ban_lanzones'][l]=invt_get_vswitch_lan_zone(l)
    iResult['ban_interfaces']=dict()
    for i in config['ban_interfaces']:
        iResult['ban_interfaces'][i]=invt_get_vswitch_interface(i)
    #make sure initial_lanzones do not overlap with ban_lanzones
    bl=iResult['ban_lanzones'].keys()
    for il in iResult['ban_lanzones'].keys():
         if il in bl:
            raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)


def create_ether_line_topology(config,iResult):
    assert('service_id' in iResult)
    _prefetch_create_config(config,iResult)

