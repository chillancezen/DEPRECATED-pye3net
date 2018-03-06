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
'''
root_key is 'vswitch_lan_zone'
while sub_key is name
'''

root_key = 'vswitch_lan_zone'

default_user_time = 60
from e3net.db.db_vswitch_lan_zone import E3VSWITCH_LAN_ZONE_TYPE_BACKBONE, E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER


def invt_register_vswitch_lan_zone(fields_create_dict,
                                   user_sync=False,
                                   user_timeout=default_user_time):
    assert ('name' in fields_create_dict)
    assert ('zone_type' in fields_create_dict)
    assert (fields_create_dict['zone_type'] in [
        E3VSWITCH_LAN_ZONE_TYPE_BACKBONE, E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER
    ])
    base = get_inventory_base()
    assert (base)
    return base.register_object(
        root_key,
        fields_create_dict,
        user_sync=user_sync,
        user_timeout=user_timeout)


def invt_update_vswitch_lan_zone(uuid,
                                 fields_change_dict,
                                 user_sync=False,
                                 user_timeout=default_user_time):
    base = get_inventory_base()
    assert (base)
    sub_key = uuid
    base.update_object(
        root_key,
        sub_key,
        fields_change_dict,
        user_sync=user_sync,
        user_timeout=user_timeout)


def invt_unregister_vswitch_lan_zone(uuid,
                                     user_sync=False,
                                     user_timeout=default_user_time):
    sub_key = uuid
    base = get_inventory_base()
    assert (base)
    base.unregister_object(
        root_key, sub_key, user_sync=user_sync, user_timeout=user_timeout)


def invt_get_vswitch_lan_zone(uuid):
    sub_key = uuid
    base = get_inventory_base()
    assert (base)
    return base.get_object(root_key, sub_key)


def invt_list_vswitch_lan_zones():
    base = get_inventory_base()
    assert (base)
    return base.list_objects(root_key)
