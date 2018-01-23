#
#Copyright (c) 2018 Jie Zheng
#
from e3net.inventory.invt_base import get_inventory_base
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_STATUS_UNKNOWN
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_STATUS_ACTIVE
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_STATUS_INACTIVE
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_STATUS_MAINTENANCE
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_TYPE_SHARED
from e3net.db.db_vswitch_interface import E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE
default_user_time=60
root_key='vswitch_interface'


def invt_register_vswitch_interface(hostname,
        dev_addr,
        lan_zone,
        iface_status=E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
        iface_type=E3VSWITCH_INTERFACE_TYPE_SHARED,
        user_sync=False,
        user_timeout=default_user_time):
    if iface_status not in [E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
                                E3VSWITCH_INTERFACE_STATUS_ACTIVE,
                                E3VSWITCH_INTERFACE_STATUS_INACTIVE,
                                E3VSWITCH_INTERFACE_STATUS_MAINTENANCE]:
        return False,'invalid iface_status:%s'%(iface_status)
    if iface_type not in [E3VSWITCH_INTERFACE_TYPE_SHARED,E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE]:
        return False,'invalid iface_type:%s'%(iface_type)
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    args={
        'hostname':hostname,
        'lan_zone':lan_zone,
        'dev_addr':dev_addr,
        'iface_status':iface_status,
        'iface_type':iface_type
    }
    sub_key='%s-->%s'%(hostname,dev_addr)
    return base.register_object(root_key,sub_key,sync=user_sync,timeout=user_timeout,**args)
    
def invt_unregister_vswitch_interface(hostname,dev_addr,user_sync=False,user_timeout=default_user_time):
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    sub_key='%s-->%s'%(hostname,dev_addr)
    return base.unregister_object(root_key,sub_key,sync=user_sync,timeout=user_timeout)

def invt_get_vswitch_interface(hostname,dev_addr):
    sub_key='%s-->%s'%(hostname,dev_addr)
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.get_object(root_key,sub_key)

def invt_list_vswitch_interfaces():
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.list_objects(root_key)

