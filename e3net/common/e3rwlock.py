#
#Copyright (c) 2017 Jie Zheng
#
import threading
class e3rwlock():
    def __init__(self):
        self.rlock=threading.Lock() 
        self.wlock=threading.Lock()
        self.read_count=0

    def write_lock(self):
        self.wlock.acquire()

    def write_unlock(self):
        self.wlock.release()

    def read_lock(self):
        self.rlock.acquire()
        self.read_count=self.read_count+1
        if self.read_count==1:
            self.wlock.acquire()
        self.rlock.release()

    def read_unlock(self):
        self.rlock.acquire()
        self.read_count=self.read_count-1
        if self.read_count==0:
            self.wlock.release()
        self.rlock.release()

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
