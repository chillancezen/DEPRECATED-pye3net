#
#Copyright (c) 2018 Jie Zheng
#
from e3net.inventory.invt_base import get_inventory_base

'''
root_key is 'vswitch_host'
while sub_key is hostname
'''

default_user_timeout=60
root_key='vswitch_host'
def invt_register_vswitch_host(hostname,ip,status,desc='',user_sync=False,user_timeout=default_user_timeout):
    args={'hostname':hostname,
            'ip':ip,
            'status':status,
            'desc':desc}
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    sub_key=hostname
    return base.register_object(root_key,sub_key,sync=user_sync,timeout=user_timeout,**args)

def invt_unregister_vswitch_host(hostname,user_sync=False,user_timeout=default_user_timeout):
    sub_key=hostname
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.unregister_object(root_key,sub_key,sync=user_sync,timeout=user_timeout)

def invt_get_vswitch_host(hostname):
    sub_key=hostname
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.get_object(root_key,sub_key)

def invt_list_vswitch_hosts():
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    return base.list_objects(root_key) 
