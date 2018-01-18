#
#Copyright (c) 2018 Jie Zheng
#

from e3net.common.e3exception import e3_exception
import threading
from e3net.common.e3rwlock import e3rwlock

class root_entry():
    def __init__(self):
        #for now I found no read-write lock in Python Library
        #so I decide to use threading.Lock to guard it.
        self.categories=dict()
        self.category_guard=e3rwlock()
    def __str__(self):
        return str(self.categories.keys())

    def _get_sub_entry(self,root_key):
        sub=None
        if root_key in self.categories:
            if isinstance(self.categories[root_key],sub_entry):
                sub=self.categories[root_key]
        return sub

    def _get_sub_entry_locked(self,root_key):
        sub=None
        self.category_guard.read_lock()
        if root_key in self.categories:
            if isinstance(self.categories[root_key],sub_entry):
                sub=self.categories[root_key]
        self.category_guard.read_unlock()
        return sub

    def _set_sub_entry(self,root_key):
        self.category_guard.write_lock()
        if self._get_sub_entry(root_key) is None:
            self.categories[root_key]=sub_entry()
        self.category_guard.write_unlock()

    def _unset_sub_entry(self,root_key):
        self.category_guard.write_lock()
        if self._get_sub_entry(root_key):
            del self.categories[root_key]
        self.category_guard.write_unlock()
    #
    #set the root_key:leaf_key:to leaf
    #this requires two tiers of LOCKs
    #
    def set(self,root_key,leaf_key,val):
        sub=self._get_sub_entry_locked(root_key)
        if not sub:
            self._set_sub_entry(root_key)
            sub=self._get_sub_entry_locked(root_key)
        leaf=sub._get_entry_locked(leaf_key)
        if not leaf:
            sub._set_entry(leaf_key)
            leaf=sub._get_entry_locked(leaf_key)
        leaf._set(val)

    #
    #read lock acquired
    #
    def get(self,root_key,leaf_key):
        sub=self._get_sub_entry_locked(root_key)
        if sub:
            leaf=sub._get_entry_locked(leaf_key)
            if leaf and leaf.is_valid is True:
                return leaf.obj
        return None

    #
    #tier1 lock is not acquired
    #
    def list(self,root_key):
        sub=self._get_sub_entry_locked(root_key)
        if sub:
            return sub._list()
        return []

    def invalidate(self,root_key,leaf_key):
        sub=self._get_sub_entry_locked(root_key)
        if sub:
            leaf=sub._get_entry_locked(leaf_key)
            if leaf:
                leaf._invalidate()
    #
    #
    #unset the leaf key in root key.
    def unset(self,root_key,leaf_key):
        sub=self._get_sub_entry_locked(root_key)
        if sub:
            sub._unset_entry(leaf_key) 

class sub_entry():
    def __init__(self):
        self.sub_guard=e3rwlock()
        self.sub_entries=dict()

    def __str__(self):
        return str(self.sub_entries.keys())

    def _list(self):
        lst=list()
        self.sub_guard.read_lock()
        for entry in self.sub_entries:
            lst.append(entry)
        self.sub_guard.read_unlock()
        return lst

    def _get_entry_locked(self,key):
        entry=None
        self.sub_guard.read_lock()
        if key in self.sub_entries:
            if isinstance(self.sub_entries[key],leaf_entry):
                entry=self.sub_entries[key]
        self.sub_guard.read_unlock()
        return entry

    def _get_entry(self,key):
        entry=None
        if key in self.sub_entries:
            if isinstance(self.sub_entries[key],leaf_entry):
                entry=self.sub_entries[key]
        return entry

    def _set_entry(self,key):
        self.sub_guard.write_lock()
        if self._get_entry(key) is None:
            self.sub_entries[key]=leaf_entry()
        self.sub_guard.write_unlock()

    def _unset_entry(self,key):
        self.sub_guard.write_lock()
        if key in self.sub_entries:
            del self.sub_entries[key]
        self.sub_guard.write_unlock()

class leaf_entry():
    def __init__(self):
        self.is_valid=False
        self.obj=None

    def _invalidate(self):
        self.is_valid=False
        self.obj=None

    def _set(self,obj):
        self.obj=obj
        self.is_valid=True

   
root=root_entry()

if __name__=='__main__':
    for i in range(10):
        root.set('foo','bar%d'%(i),i)
    print(root.list('foo'))
    root.invalidate('foo','bar%d'%(4))
    for i in range(10):
        print(root.get('foo','bar%d'%(i)))
    print(root.get('foo','bar%d'%(10)))
    #root.set('foo','bar',123)
    #root.invalidate('foo','bar')
    #root.set('foo','bar1',1234)
    #root.unset('foo','bar')
    #print(root.list('foo1'))
    #print(root.get_locked('foo','bar')) 
    #print(root)
