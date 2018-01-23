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
from uuid import uuid4
from e3net.common.e3log import get_e3loger
import traceback

e3loger=get_e3loger('e3vswitch_controller')

DB_NAME='E3NET_VSWITCH'

E3VSWITCH_LAN_ZONE_TYPE_BACKBONE='backbone'
E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER='customer'

class E3VswitchLANZone(DB_BASE):
    __tablename__='vswitch_lan_zone'
    
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    zone_type=Column(Enum(E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER,
            E3VSWITCH_LAN_ZONE_TYPE_BACKBONE),
                nullable=False,
                default=E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER)

    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['name']=self.name
        ret['zone_type']=self.zone_type
        return str(ret)
def db_register_e3vswitch_lanzone(name,zone_type=E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        lanzone=session.query(E3VswitchLANZone).filter(E3VswitchLANZone.name==name).first()
        if lanzone:
            lanzone.zone_type=zone_type
        else:
            lanzone=E3VswitchLANZone()
            lanzone.id=str(uuid4())
            lanzone.name=name
            lanzone.zone_type=zone_type
            session.add(lanzone)
        session.commit()
        e3loger.info('register/update lanzone:%s'%(lanzone))
    except:
        session.rollback()
        raise e3_exception('make sure lan zone name is unique')
    finally:
        session.close()
def db_list_e3vswitch_lanzones():
    session=db_sessions[DB_NAME]()
    lst=None
    try:
        session.begin()
        lst=session.query(E3VswitchLANZone).all()
    except:
        lst=list()
        session.rollback()
    finally:
        session.close()
    return lst
def db_get_e3vswitch_lanzone(name):
    session=db_sessions[DB_NAME]()
    lanzone=None
    try:
        session.begin()
        lanzone=session.query(E3VswitchLANZone).filter(E3VswitchLANZone.name==name).first()
    except:
        session.rollback()
        lanzone=None
    finally:
        session.close()
    return lanzone
def db_unregister_e3vswitch_lanzone(name):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        lanzone=session.query(E3VswitchLANZone).filter(E3VswitchLANZone.name==name).first()
        if lanzone:
            session.delete(lanzone)
            session.commit()
            e3loger.info('unregister E3VswitchLANZone:%s'%(lanzone))
    except:
        session.rollback()
        raise e3_exception('lan zone can not unregistered and may it be in use')
    finally:
        session.close()
