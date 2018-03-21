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
from e3net.inventory.invt_base import get_inventory_base

_taskflow_backend = None
_taskflow_queue = queue.Queue()
invt_taskflow_factory = dict()

root_key = 'taskflow'
E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN = 'unknown'
E3TASKFLOW_SCHEDULE_STATUS_ISSUED = 'issued'
E3TASKFLOW_SCHEDULE_STATUS_SUCCESSFUL = 'successful'
E3TASKFLOW_SCHEDULE_STATUS_FAILED = 'failed'
e3_taskflow_nr_worker = 4


def _taskflow_backend_init():
    global _taskflow_backend
    connection = get_config(None, 'taskflow', 'backend_connection')
    if not connection:
        raise Exception(
            'can not find taskflow:backend_connection from configuration file')
    _taskflow_backend = backends.fetch(conf={'connection': connection})


def _taskflow_base_worker_init():
    for i in range(e3_taskflow_nr_worker):
        t = threading.Thread(target=taskflow_base_worker, args=[i])
        t.start()


def taskflow_base_worker(arg):
    while True:
        self = _taskflow_queue.get()
        try:
            flow = invt_taskflow_factory[self.category]()
            book = models.LogBook('logbook-%s' % (self.category))
            flow_detail = models.FlowDetail('flowdetail-%s' % (self.category),
                                            str(uuid.uuid4()))
            book.add(flow_detail)
            with contextlib.closing(
                    _taskflow_backend.get_connection()) as conn:
                conn.save_logbook(book)
            self.book_id = book.uuid
            self.flow_id = flow_detail.uuid
            #
            #todo:optimize the engine execution process later
            #use a parallel engine instead of a serial one
            #and may be we could share a executor, please refer to
            #https://docs.openstack.org/taskflow/latest/user/examples.html#sharing-a-thread-pool-executor-in-parallel
            self.engine = engines.load(
                flow,
                backend=_taskflow_backend,
                flow_detail=flow_detail,
                book=book,
                store=self.store)
            self.engine.run()
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_SUCCESSFUL
            if self.callback:
                self.callback(self)
        except Exception as e:
            self.failure = str(e)
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_FAILED
            if self.callback:
                self.callback(self, e)
        finally:
            self.sync_state()


def register_taskflow_category(category, flow_generator):
    invt_taskflow_factory[category] = flow_generator


class e3_taskflow:
    def __init__(self, category, store=None, sync=True, callback=None):
        self.category = category  #this field acts as root_key
        self.schedule_node = None
        base = get_inventory_base()
        if base:
            self.schedule_node = base._getSelfNodeAddr()
        self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN
        self.book_id = None
        self.flow_id = None
        self.sync = sync
        self.callback = callback
        self.store = store
        self.engine = None
        self.failure = None
        self.guard = threading.Lock()

    def _generate_sync_state(self):
        ret = dict()
        ret['category'] = self.category
        ret['schedule_node'] = self.schedule_node
        ret['schedule_status'] = self.schedule_status
        ret['book_id'] = self.book_id
        ret['flow_id'] = self.flow_id
        ret['sync'] = self.sync
        if self.engine:
            ret['store'] = self.engine.storage.fetch_all()
        else:
            ret['store'] = {}
        ret['failure'] = self.failure
        return ret

    #synchronize taskflow state among cluster
    def sync_state(self):
        tf_obj = self._generate_sync_state()
        base = get_inventory_base()
        if not base:
            return False, 'inventory base not found'
        sub_key = self.book_id
        return base.set_raw_object(root_key, sub_key, tf_obj)

    def issue(self, auto_sync=True):
        try:
            self.guard.acquire()
            if self.schedule_status != E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN:
                return True
            if self.sync:
                #create the flow using registered flow creator
                flow = invt_taskflow_factory[self.category]()
                book = models.LogBook('logbook-%s' % (self.category))
                flow_detail = models.FlowDetail('flowdetail-%s' %
                                                (self.category),
                                                str(uuid.uuid4()))
                book.add(flow_detail)
                with contextlib.closing(
                        _taskflow_backend.get_connection()) as conn:
                    conn.save_logbook(book)
                self.book_id = book.uuid
                self.flow_id = flow_detail.uuid
                self.engine = engines.load(
                    flow,
                    backend=_taskflow_backend,
                    flow_detail=flow_detail,
                    book=book,
                    store=self.store)
                self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_ISSUED
                #prior to the flow,synchronize state in case the tasks need it
                if auto_sync:
                    self.sync_state()
                self.engine.run()
                self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_SUCCESSFUL
                if self.callback:
                    self.callback(self)
            else:
                self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_ISSUED
                _taskflow_queue.put(self)
        except Exception as e:
            self.failure = str(e)
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_FAILED
            if self.callback:
                self.callback(self, e)
            else:
                raise e
        finally:
            self.guard.release()
            if auto_sync:
                self.sync_state()


def invt_get_taskflow(logbook_id):
    base = get_inventory_base()
    if not base:
        return False, 'inventory base not found'
    sub_key = logbook_id
    return base.get_raw_object(root_key, sub_key)


def invt_list_taskflows():
    base = get_inventory_base()
    if not base:
        return False, 'inventory base not found'
    return base.list_raw_objects(root_key)


def invt_unset_taskflow(logbook_id):
    try:
        with contextlib.closing(_taskflow_backend.get_connection()) as conn:
            conn.destroy_logbook(logbook_id)
    except Exception as e:
        e3loger.warning('error occurs when dstroying log book:%s' %
                        (logbook_id))
    base = get_inventory_base()
    if not base:
        return False, 'inventory base not found'
    sub_key = logbook_id
    return base.unset_raw_object(root_key, sub_key)


def taskflow_init():
    _taskflow_backend_init()
    _taskflow_base_worker_init()


class do_foo(task.Task):
    default_provides = 'meeeow'

    def execute(self, spec):
        print('hello world:', spec)
        #raise Exception('cute')
        return 'meeow foo'


def generate_vm_creation_flow():
    return do_foo()


register_taskflow_category('vm-creation', generate_vm_creation_flow)


def cb_vm_create(self, error=None):
    print('callback:', self.engine.storage.fetch_all(), type(error))


if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    taskflow_init()
    ts = e3_taskflow(
        'vm-creation',
        sync=True,
        callback=cb_vm_create,
        store={'spec': 'ucte meeow'})
    ts.issue()
    ts.sync_state()
    e3_taskflow(
        'vm-creation',
        sync=False,
        callback=cb_vm_create,
        store={
            'spec': 'ucte meeow122'
        }).issue()
    print(ts._generate_sync_state())
