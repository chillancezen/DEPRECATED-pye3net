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
root_key is 'ether_service'
while sub_key is the uuid of the ether_service
'''

default_user_timeout = 60
root_key = 'ether_service'


def invt_register_vswitch_ether_service(fields_create_dict,
                                        user_sync=False,
                                        user_timeout=default_user_timeout):
    assert ('name' in fields_create_dict)
    assert ('service_type' in fields_create_dict)
    assert ('tenant_id' in fields_create_dict)
    base = get_inventory_base()
    assert (base)
    return base.register_object(
        root_key,
        fields_create_dict,
        user_sync=user_sync,
        user_timeout=user_timeout)


def invt_unregister_vswitch_ether_service(service_uuid,
                                          user_sync=False,
                                          user_timeout=default_user_timeout):
    sub_key = service_uuid
    base = get_inventory_base()
    assert (base)
    base.unregister_object(
        root_key, sub_key, user_sync=user_sync, user_timeout=user_timeout)


def invt_get_vswitch_ether_service(service_uuid):
    sub_key = service_uuid
    base = get_inventory_base()
    assert (base)
    return base.get_object(root_key, sub_key)


def invt_list_vswitch_ether_services():
    base = get_inventory_base()
    assert (base)
    return base.list_objects(root_key)
