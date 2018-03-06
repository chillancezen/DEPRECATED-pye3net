#
#Copyright (c) 2018 Jie Zheng
#
from e3net.inventory.invt_base import get_inventory_base

default_user_timeout = 60
root_key = 'topology_edge'


def invt_register_vswitch_topology_edge(fields_create_dict,
                                        user_sync=False,
                                        user_timeout=default_user_timeout):
    assert ('interface0' in fields_create_dict)
    assert ('interface1' in fields_create_dict)
    assert ('service_id' in fields_create_dict)
    base = get_inventory_base()
    assert (base)
    return base.register_object(
        root_key,
        fields_create_dict,
        user_sync=user_sync,
        user_timeout=user_timeout)


def invt_unregister_vswitch_topology_edge(edge_id,
                                          user_sync=False,
                                          user_timeout=default_user_timeout):
    sub_key = edge_id
    base = get_inventory_base()
    assert (base)
    base.unregister_object(
        root_key, sub_key, user_sync=user_sync, user_timeout=user_timeout)


def invt_get_vswitch_topology_edge(edge_id):
    sub_key = edge_id
    base = get_inventory_base()
    assert (base)
    return base.get_object(root_key, sub_key)


def invt_list_vswitch_topology_edges():
    base = get_inventory_base()
    assert (base)
    return base.list_objects(root_key)
