#
#Copyright (c) 2018 Jie Zheng
#
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT
from e3net.db.db_base import db_sessions
from e3net.db.db_base import DB_BASE
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Column
from sqlalchemy import Enum
from uuid import uuid4
from e3net.common.e3log import get_e3loger
import traceback 

e3loger=get_e3loger('e3vswitch_controller')

DB_NAME='E3NET_VSWITCH'
E3VSWITCH_HOST_STATUS_UNKNOWN='unknown'
E3VSWITCH_HOST_STATUS_ACTIVE='active'
E3VSWITCH_HOST_STATUS_INACTIVE='inactive'
E3VSWITCH_HOST_STATUS_MAINTENANCE='maintenance'

class E3VswitchHost(DB_BASE):
    __tablename__='vswitch_host'
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    description=Column(Text,nullable=True)
    host_ip=Column(String(32),nullable=False,unique=True)
    host_status=Column(Enum(E3VSWITCH_HOST_STATUS_UNKNOWN,
            E3VSWITCH_HOST_STATUS_ACTIVE,
            E3VSWITCH_HOST_STATUS_INACTIVE,
            E3VSWITCH_HOST_STATUS_MAINTENANCE),
                nullable=False,
                default=E3VSWITCH_HOST_STATUS_UNKNOWN)

    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['name']=self.name
        ret['description']=self.description
        ret['host_ip']=self.host_ip
        ret['host_status']=self.host_status
        return str(ret)

    def to_key(self):
        return str(self.id)

def db_register_e3vswitch_host(hostname,ip,status,desc=''):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.name==hostname).first()
        if host:
            #host.description=desc
            #host.host_ip=ip
            #host.host_status=status
            raise e3_exception(E3_EXCEPTION_BE_PRESENT,'item:%s already in database'%(host))
        else:
            host=E3VswitchHost()
            host.id=str(uuid4())
            host.name=hostname
            host.description=desc
            host.host_ip=ip
            host.host_status=status
            session.add(host)
            session.commit()
            e3loger.info('registering E3VswitchHost:%s succeeds'%(str(host)))
            return host
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_update_e3vswitch_host(uuid,fields_change_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.id==uuid).first()
        if not host:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND,'vswitch host %s not found'%(uuid))
        for field in fields_change_dict:
            if not hasattr(host,field):
                raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT,'%s is not a valid field of E3VswitchHost'%(field))
            setattr(host,field,fields_change_dict[field])
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_get_e3vswitch_host(uuid):
    session=db_sessions[DB_NAME]()
    host=None
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.id==uuid).first()
        if not host:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        e3loger.debug('retrieve E3VswitchHost:%s'%(str(host)))
        return host
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_list_e3vswitch_hosts():
    session=db_sessions[DB_NAME]()
    lst=None
    try:
        session.begin()
        lst=session.query(E3VswitchHost).all()
        return lst
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_unregister_e3vswitch_host(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.id==uuid).first()
        if host:
            session.delete(host)
            session.commit()
            e3loger.info('unregister E3VswitchHost:%s'%(host))
        else:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

if __name__=='__main__':
    from e3net.db.db_base import init_database
    from e3net.db.db_base import create_database_entries
    init_database(DB_NAME,'mysql+pymysql://e3net:e3credientials@localhost/E3NET_VSWITCH',False)
    create_database_entries(DB_NAME)
    db_register_e3vswitch_host('my-container-host','10.0.2.15','spine vswitch host')
    db_register_e3vswitch_host('my-container-host1','10.0.2.16','spine vswitch host')
    db_unregister_e3vswitch_host('my-container-host')
    #unregister_e3vswitch_host('my-container-host2')
    #print(get_e3vswicth_host('my-container-host'))
    print(db_get_e3vswitch_host('my-container-host1'))
    #print(get_e3vswicth_host('my-container-host2'))
    for i in db_list_e3vswitch_hosts():
        print(i)
    
