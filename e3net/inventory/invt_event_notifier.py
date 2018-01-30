#
#Copyright (c) 2018 Jie Zheng
#


from e3net.inventory.invt_base import get_inventory_base
from e3net.common.e3rwlock import e3rwlock

_event_inventory_guard=e3rwlock()
_event_inventory=dict()

class e3event():
    def __init__(self,category,obj,action,extra):
        self.category=category
        self.object_id=obj
        self.action=action
        self.extra=extra
    def __str__(self):
        return str(self.__dict__)
    
def register_notification_callback(category,notification_id,callback):
    _event_inventory_guard.write_lock()
    sub=_event_inventory.get(category,None)
    if not sub:
        _event_inventory[category]=dict()
        sub=_event_inventory[category]
    sub[notification_id]=callback
    _event_inventory_guard.write_unlock()


if __name__=='__main__':
    register_notification_callback('vm-boot','notification-localhost:1212',None)
    print(_event_inventory)
    e=e3event('cyte','obj-id','add',{'meeow':'dds','sds':12})
    print(e)
