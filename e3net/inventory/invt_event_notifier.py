#
#Copyright (c) 2018 Jie Zheng
#

from e3net.inventory.invt_base import _event_queue
from e3net.inventory.invt_base import get_inventory_base
from e3net.common.e3rwlock import e3rwlock
import threading
from e3net.common.e3log import get_e3loger

e3loger=get_e3loger('e3vswitch_controller')
_event_inventory_guard=e3rwlock()
_event_inventory=dict()
_event_consumer_nr_worker=4

class e3event():
    def __init__(self,category,obj,action,extra):
        self.category=category
        self.object_id=obj
        self.action=action
        self.extra=extra
    def __str__(self):
        return str(self.__dict__)
    
def invt_register_notification_callback(category,notification_id,callback):
    _event_inventory_guard.write_lock()
    sub=_event_inventory.get(category,None)
    if not sub:
        _event_inventory[category]=dict()
        sub=_event_inventory[category]
    sub[notification_id]=callback
    _event_inventory_guard.write_unlock()

def invt_notify_event(category,obj,action=None,extra=None):
    base=get_inventory_base()
    if not base:
        return False,'inventory not found'
    return base.notify_event(e3event(category,obj,action,extra))

def _event_consumer(arg):
    while True:
        self=_event_queue.get()
        e3loger.info('process evet:%s'%(str(self)))
        try:
            if not isinstance(self,e3event):
                continue
            event_stub=_event_inventory.get(self.category,None)
            if not event_stub:
                continue
            for notification_id in event_stub:
                if event_stub[notification_id]:
                    event_stub[notification_id](self)
        except Exception as e:
            e3loger.error('process event%s with exception:%s'%(self,str(e)))

def event_init():
    for i in range(_event_consumer_nr_worker):
        t=threading.Thread(target=_event_consumer,args=[i])
        t.start()

#def on_vm_operation(event):
#    print('vm_operation:',event)
#invt_register_notification_callback('vm','node:1212',on_vm_operation)

if __name__=='__main__':
    event_init()
