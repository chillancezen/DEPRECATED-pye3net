#
#Copyright (c) 2017 Jie Zheng
#

import uuid
_moid_invt=set()

class E3MO():
    def __init__(self):
        self.moid=None
        while True:
            self.moid=str(uuid.uuid4())
            if id not in _moid_invt:
                break
        _moid_invt.add(self.moid)
        #_mo_invt[self.moid]=self
    def moid(self):
        return self.moid

    def __del__(self):
        _moid_invt.remove(self.moid)


if __name__=='__main__':
    class A(E3MO):
        def __init__(self):
            self.foo=123
            self.foo1=True
            self.foo2='sdsds'
            super(A,self).__init__()
        def foo(self):
            pass
    class B(A):
        def __init__(self):
            self.bar=dict()
            self.bar1=list()
            super(B,self).__init__()
    a=A()
    b=B()
    import time
    print(_moid_invt)
    a=A()
    print(isinstance(b,E3MO),b.__dict__)
    print(_moid_invt)
    time.sleep(2)
    a=None
    b=None
    print(_moid_invt)
