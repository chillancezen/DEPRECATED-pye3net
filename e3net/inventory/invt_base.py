#
#Copyright (c) 2018 Jie Zheng
#

import traceback
from e3net.common.e3keeper import root_keeper
from pysyncobj import SyncObj
from pysyncobj import SyncObjConf
from pysyncobj import replicated
from e3net.common.e3log import get_e3loger
from e3net.common.e3config import get_config
 
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

from e3net.db.db_vswitch_host import db_unregister_e3vswitch_host
from e3net.db.db_vswitch_interface import db_unregister_e3vswitch_interface
from e3net.db.db_vswitch_lan_zone import db_unregister_e3vswitch_lanzone
dispatching_for_deletion={
    'vswitch_host':db_unregister_e3vswitch_host,
    'vswitch_interface':db_unregister_e3vswitch_interface,
    'vswitch_lan_zone':db_unregister_e3vswitch_lanzone,
}
sub_key_to_args={
    'vswitch_host':lambda x:{'hostname':x},    
    #the delimiter is -->,'server-1121-->0000:00:0.2'
    #or 'server-1121-->eth_pcap0,iface=eth0'
    'vswitch_interface':lambda x:{'host':x.split('-->')[0],'dev_addr':x.split('-->')[1]},
    'vswitch_lan_zone':lambda x:{'name':x}
}


cluster_conf={
    'cluster':
        {
            'local_address':'localhost:8333',
            'peer_addresses':''
    }
}

#
#root_key as the table name
#sub_key as object name
#right here we also implement distributed lock primitive
#
e3loger=get_e3loger('e3vswitch_controller')
class inventory_base(SyncObj):
    def __init__(self,selfaddr,otheraddress,conf=None):
        #a dictionary which contains tuple <locakpath,expiry-time>
        self._locks=dict()
        super(inventory_base,self).__init__(selfaddr,otheraddress,conf)

    @replicated
    def register_object(self,root_key,sub_key,user_callback=None,**args):
        if self._isReady() is False:
            e3loger.warning('synchronization state not ready')
            return False,'sync base not ready'
        try:
            #make esure root_key is in the registery dispatching dictionary
            if root_key not in dispatching_for_registery:
                e3loger.error('%s is not in registery dispaching dictionary'%(root_key))
                return False,'%s not in inventory base'%(root_key)
            if self._isLeader() is True:
                ret=dispatching_for_registery[root_key](**args)
                e3loger.debug('invoking register_object_post for <%s,%s>'%(root_key,sub_key))
                self.register_object_post(root_key,sub_key,True,callback=user_callback)
                return True,'invoking the bottom half of registery process'
            return True,'non-Leader invocation'
        except:
            e3loger.error('with given root_key:%s,sub_key:%s and arg:%s'%(str(root_key),str(sub_key),str(args)))
            e3loger.error(str(traceback.format_exc()))
            return False,'%s'%(str(traceback.format_exc()))

    @replicated
    def register_object_post(self,root_key,sub_key,success):
        e3loger.debug('post registery call:<%s,%s> %s'%(root_key,sub_key,success))
        if success:
            obj,valid=root_keeper.get(root_key,sub_key)
            if valid:
                root_keeper.invalidate(root_key,sub_key)
            else:
                root_keeper.set(root_key,sub_key,None,False)

    '''
    return <False/True,failure reason/Object>
    '''
    def get_object(self,root_key,sub_key):
        try:
            obj,valid=root_keeper.get(root_key,sub_key)
            if not valid:
                obj=dispatching_for_retrieval[root_key](**sub_key_to_args[root_key](sub_key))
                #if the object can not be retrieved, leave the keeper entry empty
                if obj:
                    root_keeper.set(root_key,sub_key,obj,True)
            return True if obj else False,obj if obj else 'database lookup fails'
        except:
            e3loger.error('with given root_key:%s,sub_key:%s'%(str(root_key),str(sub_key)))
            e3loger.error(str(traceback.format_exc()))
            return False,'%s'%(str(traceback.format_exc()))

    '''
    return <True/False,list/failure reason> tuple
    '''
    def list_objects(self,root_key):
        ret=dict()
        try:
            sub_lst=root_keeper.list(root_key)
            for sub_key in sub_lst:
                ret[sub_key]=self.get_object(root_key,sub_key)
            return True,ret
        except:
            e3loger.error(str(traceback.format_exc()))
            return False,'%s'%(str(traceback.format_exc()))
        

    '''
    https://github.com/bakwc/PySyncObj/issues/76
    here no known way to get the infomation
    whether it's synchronous invocation or
    whether the callback is set, to work this around, the user_ prefixed
    callback and sync are introdduced,
    often the caller should only specify user_callback instead callback,
    and if conducting synchronuously this operation, specify both user_sync and sync
    updates:do not use user_sync, this will cause errors
    use user_callback instead of callback
    '''
    @replicated
    def unregister_object(self,root_key,sub_key,user_callback=None):
        if self._isReady() is False:
            e3loger.warning('synchronization state not ready')
            return False,'synchronization state not ready'
        try:
            if self._isLeader() is True:
                dispatching_for_deletion[root_key](**sub_key_to_args[root_key](sub_key))
                #if no exception thrown,things go normal
                #try to invoke another post callback with the same manner
                e3loger.debug('invoking unregister_object_post for<%s,%s>'%(root_key,sub_key))
                self.unregister_object_post(root_key,sub_key,callback=user_callback)
                return True,'unregister_object_post invoked'
            return True,'no-leader invocation'
        except:
            e3loger.error('with given root_key:%s,sub_key:%s '%(str(root_key),str(sub_key)))
            e3loger.error(str(traceback.format_exc()))
            return False,'%s'%(str(traceback.format_exc()))

    @replicated
    def unregister_object_post(self,root_key,sub_key):
        e3loger.debug('unset<%s,%s>'%(root_key,sub_key))
        root_keeper.unset(root_key,sub_key)
    
    #
    #distributed lock implementation
    #use caller's time to synchronize the lock, DO NOT use local tome,
    #because different nodes' time do not be the same.
    #this must be a LESSON, and use NTP service to synchronize the time to almost the same.
    #
    @replicated
    def acquire_lock(self,lock_path,caller_id,current_time,lock_duration):
        lock=self._locks.get(lock_path,None)
        lock_id=None
        expiry_time=0
        #release previous in case of expiry
        if lock:
            lock_id,expiry_time=lock
            if expiry_time<current_time:
                lock=None
        if not lock or lock_id==caller_id:
            self._locks[lock_path]=(caller_id,current_time+lock_duration)
            return True
        return False
    def is_locked(self,lock_path,caller_id,current_time):
        lock=self._locks.get(lock_path,None)
        if lock:
            lock_id,expiry_time=lock
            if lock_id==caller_id and expiry_time >current_time:
                return True
        return False

    @replicated
    def release_lock(self,lock_path,caller_id):
        lock=self._locks.get(lock_path,None)
        if not lock:
            return True
        lock_id,expiry_time=lock
        if lock_id == caller_id:
            del self._locks[lock_path]
            return True
        return False
            
invt_base=None
def e3inventory_base_init():
    global invt_base
    local_address=get_config(cluster_conf,'cluster','local_address')
    peer_addresses=get_config(cluster_conf,'cluster','peer_addresses')
    local=local_address.strip()
    peer=list()
    for addr in peer_addresses.split(','):
        addr=addr.strip()
        if addr=='':
            continue
        peer.append(addr)
    e3loger.info('try to instantiate inventory service with local:%s and peer(s):%s'%(local,peer))
    invt_base=inventory_base(local,peer)

def get_inventory_base():
    return invt_base

if __name__=='__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    e3inventory_base_init()
        
    '''
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
    '''
