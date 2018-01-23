#
#Copyright (c) 2018 Jie Zheng
#
from e3net.common.e3exception import e3_exception
from e3net.db.db_base import db_sessions
from e3net.db.db_base import DB_BASE
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import and_
from uuid import uuid4
from e3net.common.e3log import get_e3loger
import traceback

e3loger=get_e3loger('e3vswitch_controller')

DB_NAME='E3NET_VSWITCH'

E3VSWITCH_INTERFACE_STATUS_UNKNOWN='unknown'
E3VSWITCH_INTERFACE_STATUS_ACTIVE='active'
E3VSWITCH_INTERFACE_STATUS_INACTIVE='inactive'
E3VSWITCH_INTERFACE_STATUS_MAINTENANCE='maintenance'


E3VSWITCH_INTERFACE_TYPE_SHARED='shared'
E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE='exclusive'


class E3VswitchInterface(DB_BASE):
    __tablename__='vswitch_interface'
    
    id=Column(String(64),primary_key=True)
    hostname=Column(String(64),ForeignKey('vswitch_host.name'),nullable=False)
    dev_address=Column(Text,nullable=False)
    interface_status=Column(Enum(E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
            E3VSWITCH_INTERFACE_STATUS_ACTIVE,
            E3VSWITCH_INTERFACE_STATUS_INACTIVE,
            E3VSWITCH_INTERFACE_STATUS_MAINTENANCE),
                nullable=False,
                default=E3VSWITCH_INTERFACE_STATUS_UNKNOWN)
    interface_type=Column(Enum(E3VSWITCH_INTERFACE_TYPE_SHARED,
            E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE),
                nullable=False,
                default=E3VSWITCH_INTERFACE_TYPE_SHARED)
    #infrastructure lan zone is the area that the interface is attached to
    lan_zone=Column(String(64),ForeignKey('vswitch_lan_zone.name'),nullable=False)
    reference_count=Column(Integer(),default=0,nullable=False)

    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['hostname']=self.hostname
        ret['dev_address']=self.dev_address
        ret['interface_status']=self.interface_status
        ret['interface_type']=self.interface_type
        ret['lan_zone']=self.lan_zone
        ret['reference_count']=self.reference_count
        return str(ret)
def db_register_e3vswitch_interface(hostname,dev_addr,
    lan_zone,
    iface_status=E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
    iface_type=E3VSWITCH_INTERFACE_TYPE_SHARED):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        iface=session.query(E3VswitchInterface).filter(and_(E3VswitchInterface.hostname==hostname,
            E3VswitchInterface.dev_address==dev_addr)).first()
        if iface:
            iface.interface_status=iface_status
            iface.interface_type=iface_type
            iface.lan_zone=lan_zone
        else:
            iface=E3VswitchInterface()
            iface.id=str(uuid4())
            iface.hostname=hostname
            iface.dev_address=dev_addr
            iface.lan_zone=lan_zone
            iface.reference_count=0
            iface.interface_status=iface_status
            iface.interface_type=iface_type
            session.add(iface)
        session.commit()
        e3loger.info('register/update E3VswitchInterface:%s'%(iface))
    except:
        session.rollback()
        raise e3_exception('invalid arguments to resgiter an interface')
    finally:
        session.close()
def db_list_e3vswitch_interfaces():
    session=db_sessions[DB_NAME]()
    lst=None
    try:
        session.begin()
        lst=session.query(E3VswitchInterface).all()
    except:
        lst=list()
        session.rollback()
    finally:
        session.close()
    return lst
def db_get_e3vswitch_interface(host,dev_addr):
    session=db_sessions[DB_NAME]()
    iface=None
    try:
        session.begin()
        iface=session.query(E3VswitchInterface).filter(and_(E3VswitchInterface.hostname==host,E3VswitchInterface.dev_address==dev_addr)).first()
    except:
        iface=None
    finally:
        session.close()
    return iface
def db_unregister_e3vswitch_interface(host,dev_addr):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        iface=session.query(E3VswitchInterface).filter(and_(E3VswitchInterface.hostname==host,E3VswitchInterface.dev_address==dev_addr)).first()
        if iface and iface.reference_count==0:
            session.delete(iface)
            session.commit()
            e3loger.info('unregister E3VswitchInterface:%s'%(iface))
    except:
        session.rollback()
        raise e3_exception('make sure interface ref count is zero')
    finally:
        session.close()
                   
if __name__=='__main__':
    from e3net.db.db_base import init_database
    from e3net.db.db_base import create_database_entries
    from e3net.db.db_vswitch_host import *
    init_database(DB_NAME,'mysql+pymysql://e3net:e3credientials@localhost/E3NET_VSWITCH',True)
    create_database_entries(DB_NAME)                                                                                                                                                            
