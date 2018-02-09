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
from e3net.common.e3keeper import root_keeper
from e3net.db.db_base import register_database_load_entrance

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

    def clone(self):
        c=E3VswitchHost()
        c.id=self.id
        c.name=self.name
        c.description=self.description
        c.host_ip=self.host_ip
        c.host_status=self.host_status
        return c

def load_e3vswitch_hosts_from_db():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        hosts=session.query(E3VswitchHost).all()
        for host in hosts:
            root_keeper.set('vswitch_host',host.id,host.clone())
    finally:
        session.close()
register_database_load_entrance('vswitch_host',load_e3vswitch_hosts_from_db)


def db_register_e3vswitch_host(fields_create_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.name==fields_create_dict['name']).first()
        if host:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        else:
            host=E3VswitchHost()
            host.id=str(uuid4())
            for field in fields_create_dict:
                setattr(host,field,fields_create_dict[field])
            session.add(host)
            session.commit()
            e3loger.info('registering E3VswitchHost:%s succeeds'%(str(host)))
            return host.clone()
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
        e3loger.info('update E3VswitchHost:%s with change:%s'%(uuid,fields_change_dict))
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
        return host.clone()
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
        return [host.clone() for host in lst]
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
