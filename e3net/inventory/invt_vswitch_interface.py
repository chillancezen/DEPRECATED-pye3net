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


def invt_register_vswitch_interface(fields_create_dict,user_sync=False,user_timeout=default_user_time):
    assert('host_id' in fields_create_dict)
    assert('dev_address' in fields_create_dict)
    assert('lanzone_id' in fields_create_dict)
    if 'interface_status' in fields_create_dict: 
        assert(fields_create_dict['interface_status'] in  [E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
                                E3VSWITCH_INTERFACE_STATUS_ACTIVE,
                                E3VSWITCH_INTERFACE_STATUS_INACTIVE,
                                E3VSWITCH_INTERFACE_STATUS_MAINTENANCE])
    if 'interface_type' in fields_create_dict:
        assert(fields_create_dict['interface_type'] in [E3VSWITCH_INTERFACE_TYPE_SHARED,E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE])
    base=get_inventory_base()
    assert(base)
    return base.register_object(root_key,fields_create_dict,user_sync=user_sync,user_timeout=user_timeout)

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

