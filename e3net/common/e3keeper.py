#
#Copyright (c) 2018 Jie Zheng
#

from e3net.common.e3exception import e3_exception
import threading

class root_entry():
    def __init__(self):
        #for now I found no read-write lock in Python Library
        #so I decide to use threading.Lock to guard it.
        self.categories=dict()
        self.category_guard=threading.Lock()
    def __str__(self):
        return str(self.categories.keys())
    def _get_sub_entry_locked(self,root_key):
        sub=None
        self.category_guard.acquire()
        if root_key in self.categories:
            if isinstance(self.categories[root_key],sub_entry):
                sub=self.categories[root_key]
        self.category_guard.release()
        return sub

    def _get_sub_entry(self,root_key):
        sub=None
        if root_key in self.categories:
            if isinstance(self.categories[root_key],sub_entry):
                sub=self.categories[root_key]
        return sub

    def _set_sub_entry(self,root_key):
        self.category_guard.acquire()
        if self._get_sub_entry(root_key) is None:
            self.categories[root_key]=sub_entry()
        self.category_guard.release()

    #
    #set the root_key:leaf_key:to leaf
    #this requires two tiers of LOCKs
    #
    def set(self,root_key,leaf_key,leaf):
        sub=self._get_sub_entry_locked(root_key)
        if not sub:
            self._set_sub_entry(root_key)
            sub=self._get_sub_entry_locked(root_key)
        
        pass 
    
class sub_entry():
    def __init__(self):
        self.sub_guard=threading.Lock()
        self.sub_entries=dict() 
    def __str__(self):
        return str(self.sub_entries.keys())

    def _get_entry_locked(self,key):
        entry=None
        self.sub_guard.acquire()
        if key in self.sub_entries:
            if isinstance(self.sub_entries[key],leaf_entry)
                entry=self.sub_entries[key]
        self.sub_guard.release()
        return entry
    def _get_entry(self,key):
        entry=None
        if key in self.sub_entries:
            if isinstance(self.sub_entries[key],leaf_entry)
                entry=self.sub_entries[key]
        return entry
    def _set_entry(self,key):
        self.sub_guard.acquire()
        if self._get_entry(key) is None:
            self.sub_entries[key]=leaf_entry()
        self.sub_guard.acquire()
    def 
class leaf_entry():
    def __init__(self):
        self.is_valid=False
        self.obj=None

    def _invalidate(self):
        self.is_valid=False

    def _validate(self):
        self.is_valid=True

    def _set(self,obj):
        self.obj=obj
        self.is_valid=True

    def _reset(self):
        self.obj=None
        self.is_valid=False
   
root=root_entry()

if __name__=='__main__':
    root._set_sub_entry('vswitch_host')
    print(root._get_sub_entry('vswitch_host'))
    print(root._get_sub_entry_locked('vswitch_host'))
    print(root)
