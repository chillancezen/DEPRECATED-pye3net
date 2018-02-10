#
#Copyright (c) 2018 Jie Zheng
#
import time
from e3net.inventory.invt_base import get_inventory_base

def invt_try_lock(lock_path,duration):
    base=get_inventory_base()
    assert(base)
    caller_id=base._SyncObj__selfNodeAddr
    return base.acquire_lock(lock_path,caller_id,time.time(),duration,sync=True)

def invt_unlock(lock_path):
    base=get_inventory_base()
    assert(base)
    caller_id=base._SyncObj__selfNodeAddr
    try:
        base.release_lock(lock_path,caller_id,sync=True)
    except:
        #capture the exceptuion and do nothing
        pass

def invt_is_locked(lock_path):
    base=get_inventory_base()
    assert(base)
    caller_id=base._SyncObj__selfNodeAddr
    return base.is_locked(lock_path,caller_id,time.time())
