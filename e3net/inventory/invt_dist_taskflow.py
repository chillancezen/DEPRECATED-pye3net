#
#Copyright (c) 2018 Jie Zheng
#
from taskflow import engines
from taskflow import task
from taskflow.persistence import models
from taskflow.patterns import linear_flow as lf
from taskflow.patterns import unordered_flow as uf
from taskflow.persistence import backends
from e3net.common.e3log import get_e3loger
from e3net.common.e3config import get_config
import uuid
import threading
import queue
import time
import contextlib

_taskflow_backend=None
_taskflow_queue=queue.Queue()
invt_taskflow_factory=dict()

E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN='unknown'
E3TASKFLOW_SCHEDULE_STATUS_ISSUED='issued'

e3_taskflow_nr_worker=4

def taskflow_backend_init():
    global _taskflow_backend
    connection=get_config(None,'taskflow','backend_connection')
    if not connection:
        raise Exception('can not find taskflow:backend_connection from configuration file')
    _taskflow_backend=backends.fetch(conf={'connection':connection})

def taskflow_base_worker_init():
    for i in range(e3_taskflow_nr_worker):
        t=threading.Thread(target=taskflow_base_worker,args=[i])
        t.start()

def taskflow_base_worker(arg):
    while True:
        self=_taskflow_queue.get()
        try:
            flow=invt_taskflow_factory[self.category]()
            book=models.LogBook('logbook-%s'%(self.category))
            flow_detail=models.FlowDetail('flowdetail-%s'%(self.category),str(uuid.uuid4()))
            book.add(flow_detail)
            with contextlib.closing(_taskflow_backend.get_connection()) as conn:
                conn.save_logbook(book)
            self.book_id=book.uuid
            self.flow_id=flow_detail.uuid
            #
            #todo:optimize the engine execution process later
            #use a parallel engine instead of a serial one
            #and may be we could share a executor, please refer to
            #https://docs.openstack.org/taskflow/latest/user/examples.html#sharing-a-thread-pool-executor-in-parallel
            self.engine=engines.load(flow,
                backend=_taskflow_backend,
                flow_detail=flow_detail,
                book=book,
                store=self.store)
            self.engine.run()
            if self.callback:
                self.callback(self)
        except Exception as e:
            if self.callback:
                self.callback(self,e)

def register_taskflow_category(category,flow_generator):
    invt_taskflow_factory[category]=flow_generator

class e3_taskflow:
    def __init__(self,category,store=None,sync=True,callback=None):
        self.category=category
        self.schedule_node=None
        self.schedule_status=E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN
        self.book_id=None
        self.flow_id=None
        self.sync=sync
        self.callback=callback
        self.store=store
        self.engine=None
        self.guard=threading.Lock()
        
    def issue(self):
        try:
            self.guard.acquire()
            if self.schedule_status!=E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN:
                return True
            if self.sync:
                #create the flow using registered flow creator
                flow=invt_taskflow_factory[self.category]()
                book=models.LogBook('logbook-%s'%(self.category))
                flow_detail=models.FlowDetail('flowdetail-%s'%(self.category),str(uuid.uuid4()))
                book.add(flow_detail)
                with contextlib.closing(_taskflow_backend.get_connection()) as conn:
                    conn.save_logbook(book)
                self.book_id=book.uuid
                self.flow_id=flow_detail.uuid
                self.engine=engines.load(flow,
                        backend=_taskflow_backend,
                        flow_detail=flow_detail,
                        book=book,
                        store=self.store)
                self.schedule_status=E3TASKFLOW_SCHEDULE_STATUS_ISSUED
                self.engine.run()
                if self.callback:
                    self.callback(self)
            else:
                self.schedule_status=E3TASKFLOW_SCHEDULE_STATUS_ISSUED
                _taskflow_queue.put(self)
        except Exception as e:
            if self.callback:
                self.callback(self,e)
            else:
                raise e 
        finally:
            self.guard.release()
        

def taskflow_init():
    taskflow_backend_init()
    taskflow_base_worker_init()

class do_foo(task.Task):
    default_provides='meeeow'
    def execute(self,spec):
        print('hello world:',spec)
        return 'meeow foo'
    def __del__(self):
        print('del:',self)
def generate_vm_creation_flow():
    return do_foo()
register_taskflow_category('vm-creation',generate_vm_creation_flow)


def cb_vm_create(self,error=None):
    print('callback:',self.engine.storage.fetch_all(),type(error))
if __name__=='__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    taskflow_init()
    e3_taskflow('vm-creation',sync=True,callback=cb_vm_create,store={'spec':'ucte meeow'}).issue()
    e3_taskflow('vm-creation',sync=False,callback=cb_vm_create,store={'spec':'ucte meeow122'}).issue()
    #time.sleep(100)
