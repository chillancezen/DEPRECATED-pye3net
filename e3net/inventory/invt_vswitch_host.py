#
#Copyright (c) 2018 Jie Zheng
#
from e3net.inventory.invt_base import get_inventory_base

'''
root_key is 'vswitch_host'
while sub_key is hostname
'''

root_key='vswitch_host'
def invt_register_vswitch_host(hostname,ip,status,desc='',user_sync=False):
    args={'hostname':hostname,
            'ip':ip,
            'status':status,
            'desc':desc}
    base=get_inventory_base()
    if not base:
        return False,'inventory base not registered'
    sub_key=hostname
    return base.register_object(root_key,sub_key,sync=user_sync,**args)

def invt_unregister_vswitch_host(hostname,user_sync=False):
    




