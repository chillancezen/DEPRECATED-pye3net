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
from e3net.inventory.invt_vswitch_lan_zone import invt_get_vswitch_lan_zone
from e3net.inventory.invt_vswitch_ether_service_vlan import invt_list_vswitch_ether_service_vlans

#
#try to find a free vlan id for a lanzone,
#but do not lock or preserve it,
#there is still a chance that a found vlan id will fail to be registered
#but it seldom occurs
def invt_search_vlan_id_for_lanzone(lanzone_id):
    lanzone=invt_get_vswitch_lan_zone(lanzone_id)
    vlans=invt_list_vswitch_ether_service_vlans()
    flag=bytearray(4096)
    for vlan_id in vlans:
        vlan=vlans[vlan_id]
        if vlan.lanzone_id!=lanzone_id:
            continue
        assert(not flag[vlan.vlan_id])
        flag[vlan.vlan_id]=1
    min_vlan=lanzone.min_vlan if lanzone.min_vlan>=1 and lanzone.min_vlan<=4095 else 1
    max_vlan=lanzone.max_vlan if lanzone.max_vlan<=4095 and lanzone.max_vlan>=1 else 4095
    for i in range(min_vlan,max_vlan):
        if not flag[i]:
            return i
    raise e3_exception(E3_EXCEPTION_OUT_OF_RESOURCE)
