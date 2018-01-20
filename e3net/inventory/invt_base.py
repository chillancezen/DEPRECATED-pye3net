#
#Copyright (c) 2018 Jie Zheng
#

import traceback
from e3net.common.e3keeper import root_keeper
from pysyncobj import SyncObj
from pysyncobj import SyncObjConf
from pysyncobj import replicated
from e3net.common.e3log import get_e3loger

from e3net.db.db_vswitch_host import db_register_e3vswitch_host
from e3net.db.db_vswitch_interface import db_register_e3vswitch_interface
from e3net.db.db_vswitch_lan_zone import db_register_e3vswitch_lanzone
dispatching_for_registery={
    'vswitch_host':db_register_e3vswitch_host,
    'vswitch_interface':db_register_e3vswitch_interface,
    'vswitch_lan_zone':db_register_e3vswitch_lanzone
}

from e3net.db.db_vswitch_host import db_get_e3vswitch_host
from e3net.db.db_vswitch_interface import db_get_e3vswitch_interface
from e3net.db.db_vswitch_lan_zone import db_get_e3vswitch_lanzone
dispatching_for_retrieval={
    'vswitch_host':db_get_e3vswitch_host,
    'vswitch_interface':db_get_e3vswitch_interface,
    'vswitch_lan_zone':db_get_e3vswitch_lanzone
}
#
#root_key as the table name
#sub_key as object name
#
e3loger=get_e3loger('e3vswitch_controller')
class inventory_base(SyncObj):
    def __init__(self,selfaddr,otheraddress,conf=None):
        super(inventory_base,self).__init__(selfaddr,otheraddress,conf)

    @replicated
    def register_object(self,root_key,sub_key,**args):
        if self._isReady() is False:
            e3loger.warning('synchronization state not ready')
            return None,False
        try:
            #make esure root_key is in the registery dispatching dictionary
            if root_key not in dispatching_for_registery:
                e3loger.error('%s is not in registery dispaching dictionary'%(root_key))
                return None,False
            if self._isLeader() is True:
                ret=dispatching_for_registery[root_key](**args)
            #invalidate the cached object
            obj,valid=root_keeper.get(root_key,sub_key)
            if valid:
                root_keeper.invalidate(root_key,sub_key)
            else:
                root_keeper.set(root_key,sub_key,None,False)
        except:
            e3loger.error('with given root_key:%s,sub_key:%s and arg:%s',str(root_key),str(sub_key),str(args))
            e3loger.error(str(traceback.format_exc()))
            return None,False

    def get_object(self,root_key,sub_key,**args):
        try:
            obj,valid=root_keeper.get(root_key,sub_key)
            print('debug:',obj,valid)
            if not valid:
                obj=dispatching_for_retrieval[root_key](**args)
                print('debug:',obj)
                root_keeper.set(root_key,sub_key,obj,True if obj else False)
            return obj,True if obj else False
        except:
            e3loger.error('with given root_key:%s,sub_key:%s and arg:%s',str(root_key),str(sub_key),str(args))
            e3loger.error(str(traceback.format_exc()))
            return None,False

    @replicated
    def unregister_object(self,root_key,sub_key):
        pass


    


if __name__=='__main__':
    from e3net.db.db_base import init_database
    from e3net.db.db_base import create_database_entries
    DB_NAME='E3NET_VSWITCH'
    init_database(DB_NAME,'mysql+pymysql://e3net:e3credientials@localhost/E3NET_VSWITCH',False)
    base=inventory_base('localhost:507',[])
    import time
    while True:
        time.sleep(1)
        arg=dict()
        arg['ip']='130.140.150.1'
        arg['hostname']='server'
        print(base.register_object('vswitch_host','container_host1',**arg))
