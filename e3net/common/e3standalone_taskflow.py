#
#Copyright (c) 2018 Jie Zheng
#

from taskflow import engines
from taskflow import task
from taskflow.persistence import models
from taskflow.patterns import linear_flow as lf
from taskflow.patterns import unordered_flow as uf
from uuid import uuid4
import threading
import queue
import time
import contextlib
from e3net.common.e3def import E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN
from e3net.common.e3def import E3TASKFLOW_SCHEDULE_STATUS_ISSUED
from e3net.common.e3def import E3TASKFLOW_SCHEDULE_STATUS_SUCCESSFUL
from e3net.common.e3def import E3TASKFLOW_SCHEDULE_STATUS_FAILED
from e3net.common.e3def import taskflow_root_key as root_key
from e3net.common.e3keeper import root_keeper
import traceback
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT

_invt_standalone_taskflow_factory = dict()
_standalone_taskflow_queue = queue.Queue()
_e3_standalone_taskflow_nr_worker = 4

def register_standalone_taskflow_category(category, flow_generator):
    print('register standalone taskflow:', category, flow_generator)
    _invt_standalone_taskflow_factory[category] = flow_generator

def standalone_taskflow_base_worker(arg):
    while True:
        self = _standalone_taskflow_queue.get()
        try:
            flow = _invt_standalone_taskflow_factory[self.category]()
            self.engine = engines.load(flow, store = self.store)
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_ISSUED
            self.sync_state()
            self.engine.run()
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_SUCCESSFUL
            if self.callback:
                self.callback(self)
        except Exception as e:
            self.failure = str(traceback.format_exc())
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_FAILED
            if self.callback:
                self.callback(self, e)
            else:
                raise e
        finally:
            self.sync_state()

class e3standalone_taskflow:
    def __init__(self, category, store = None, sync = True, callback = None):
        self.id = str(uuid4())
        self.category = category
        self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN
        self.sync = sync
        self.callback = callback
        self.store = store
        self.engine = None
        self.failure = None
        self.guard = threading.Lock()
    def _generate_sync_state(self):
        ret = dict()
        ret['id'] = self.id
        ret['category'] = self.category
        ret['schedule_status'] = self.schedule_status
        ret['sync'] = self.sync
        ret['store'] = self.store
        ret['failure'] = self.failure
        return ret
    def __str__(self):
        return str(self._generate_sync_state())
    def sync_state(self):
        root_keeper.set(root_key, self.id, self)
    def issue(self, auto_sync = True):
        try:
            self.guard.acquire()
            if self.schedule_status != E3TASKFLOW_SCHEDULE_STATUS_UNKNOWN:
                return
            if self.sync:
                flow = _invt_standalone_taskflow_factory[self.category]()
                self.engine = engines.load(flow, store = self.store)
                self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_ISSUED
                if auto_sync:
                    self.sync_state()
                self.engine.run()
                self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_SUCCESSFUL
                if self.callback:
                    self.callback(self)
            else:
                self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_ISSUED
                _standalone_taskflow_queue.put(self)
        except Exception as e:
            self.failure = str(traceback.format_exc())
            self.schedule_status = E3TASKFLOW_SCHEDULE_STATUS_FAILED
            if self.callback:
                self.callback(self, e)
            else:
                raise e
        finally:
            self.guard.release()
            if auto_sync:
                self.sync_state()

def standalone_taskflow_init():
    for i in range(_e3_standalone_taskflow_nr_worker):
        t = threading.Thread(target = standalone_taskflow_base_worker, args = [i])
        t.start()

class do_foo(task.Task):
    default_provides = 'meeeow'
    def execute(self, spec):
        print('hello world:', spec)
        time.sleep(5)
        return 'meeow foo'
def generate_vm_creation_flow():
    return do_foo()


def list_standalone_taskflows():
    id_list = root_keeper.list(root_key)
    ret = list()
    for id in id_list:
        task, _ = root_keeper.get(root_key, id)
        if not _:
            continue
        ret.append(task)
    return ret

def get_standalone_taskflow(task_id):
    task, _ = root_keeper.get(root_key, task_id)
    if not _:
        raise e3_exception(E3_EXCEPTION_NOT_FOUND)
    return task


register_standalone_taskflow_category('do-foo', generate_vm_creation_flow)

if __name__ == '__main__':
    standalone_taskflow_init()

    tf = e3standalone_taskflow('do-foo', sync = True, store = {'spec' : 'cute-eeepw'})
    tf1 = e3standalone_taskflow('do-foo', sync = True, store = {'spec' : 'cute-eeepw'})
    tf.issue()
    tf1.issue()
    for task in list_standalone_taskflows():
        print(task)
