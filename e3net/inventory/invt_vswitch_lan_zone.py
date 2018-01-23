#
#Copyright (c) 2018 Jie Zheng
#
from e3net.inventory.invt_base import get_inventory_base


'''
root_key is 'vswitch_lan_zone'
while sub_key is name
'''

root_key='vswitch_lan_zone'

default_user_time=60
from e3net.db.db_vswitch_lan_zone import E3VSWITCH_LAN_ZONE_TYPE_BACKBONE,E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER

def invt_register_vswitch_lan_zone(name,zone_type,user_sync=False,user_timeout=default_user_time):
    args={
        'name':name,
        'zone_type':zone_type
    }
    if zone_type not in [E3VSWITCH_LAN_ZONE_TYPE_BACKBONE,E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER]:
        return False,'%s not in [%s,%s]'%(zone_type,E3VSWITCH_LAN_ZONE_TYPE_BACKBONE,E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER)
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    sub_key=name
    return base.register_object(root_key,sub_key,sync=user_sync,timeout=user_timeout,**args)

def invt_unregister_vswitch_lan_zone(name,user_sync=False,user_timeout=default_user_time):
    sub_key=name
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.unregister_object(root_key,sub_key,sync=user_sync,timeout=user_timeout)

def invt_get_vswitch_lan_zone(name):
    sub_key=name
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.get_object(root_key,sub_key)

def invt_list_vswitch_lan_zones():
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.list_objects(root_key)

