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
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT

default_user_time=60
root_key='vswitch_interface'


def invt_register_vswitch_interface(host_id,
        dev_addr,
        lanzone_id,
        iface_status=E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
        iface_type=E3VSWITCH_INTERFACE_TYPE_SHARED,
        user_sync=False,
        user_timeout=default_user_time):
    if iface_status not in [E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
                                E3VSWITCH_INTERFACE_STATUS_ACTIVE,
                                E3VSWITCH_INTERFACE_STATUS_INACTIVE,
                                E3VSWITCH_INTERFACE_STATUS_MAINTENANCE]:
        raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT,'invalid iface_status:%s'%(iface_status))
    if iface_type not in [E3VSWITCH_INTERFACE_TYPE_SHARED,E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE]:
        raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT,'invalid iface_type:%s'%(iface_type))
    base=get_inventory_base()
    assert(base)
    args={
        'host_id':host_id,
        'lanzone_id':lanzone_id,
        'dev_addr':dev_addr,
        'iface_status':iface_status,
        'iface_type':iface_type
    }
    return base.register_object(root_key,user_sync=user_sync,user_timeout=user_timeout,**args)

def invt_update_vswitch_interface(iface_uuid,fields_change_dict,user_sync=False,user_timeout=default_user_time):
    base=get_inventory_base()
    assert(base)
    sub_key=iface_uuid
    base.update_object(root_key,sub_key,fields_change_dict,user_sync=user_sync,user_timeout=user_timeout)
    
def invt_unregister_vswitch_interface(uuid,user_sync=False,user_timeout=default_user_time):
    base=get_inventory_base()
    assert(base)
    sub_key=uuid
    return base.unregister_object(root_key,sub_key,user_sync=user_sync,user_timeout=user_timeout)

def invt_get_vswitch_interface(uuid):
    sub_key=uuid
    base=get_inventory_base()
    assert(base)
    return base.get_object(root_key,sub_key)

def invt_list_vswitch_interfaces():
    base=get_inventory_base()
    assert(base)
    return base.list_objects(root_key)

