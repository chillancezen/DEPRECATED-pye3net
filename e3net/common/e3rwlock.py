#
#Copyright (c) 2017 Jie Zheng
#
import threading
import ctypes
from ctypes import *
#
#this value can be acuiqre by testing :size of (pthread_rwlock_t) in C
#
X86_PTHREAD_RWLOCK_SIZE=56
_clib=ctypes.CDLL('librt.so', use_errno=True)
class e3rwlock(Structure):
    _pack_=1
    _fields_=[('foo',c_byte*X86_PTHREAD_RWLOCK_SIZE)]
    
    def __init__(self):
        attr=c_uint64(0)
        self.init_ret=_clib.pthread_rwlock_init(byref(self),attr)

    def write_lock(self):
        return _clib.pthread_rwlock_wrlock(byref(self))

    def write_unlock(self):
        return _clib.pthread_rwlock_unlock(byref(self))

    def read_lock(self):
        return _clib.pthread_rwlock_rdlock(byref(self))
    
    def read_unlock(self):
        return _clib.pthread_rwlock_unlock(byref(self))

    def __del__(self):
        return _clib.pthread_rwlock_destroy(byref(self))
if __name__=='__main__':
    l=e3rwlock()
    l.read_lock()
    l.read_lock()

    l.read_unlock()
    l.read_unlock() 
    l.write_lock()
    l.write_unlock()
 
    l.read_lock()
    l.read_unlock()
    l.write_lock()
    l.write_unlock()
