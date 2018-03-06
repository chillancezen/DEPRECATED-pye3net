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
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from uuid import uuid4
from e3net.common.e3log import get_e3loger
import traceback
from e3net.common.e3keeper import root_keeper
from e3net.db.db_base import register_database_load_entrance

e3loger = get_e3loger('e3vswitch_controller')

DB_NAME = 'E3NET_VSWITCH'

E3VSWITCH_LAN_ZONE_TYPE_BACKBONE = 'backbone'
E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER = 'customer'


class E3VswitchLANZone(DB_BASE):
    __tablename__ = 'vswitch_lan_zone'

    id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=False, index=True, unique=True)
    zone_type = Column(
        Enum(E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER,
             E3VSWITCH_LAN_ZONE_TYPE_BACKBONE),
        nullable=False,
        default=E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER)
    min_vlan = Column(Integer(), default=1, nullable=False)
    max_vlan = Column(Integer(), default=4095, nullable=False)

    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['name'] = self.name
        ret['zone_type'] = self.zone_type
        ret['min_vlan'] = self.min_vlan
        ret['max_vlan'] = self.max_vlan
        return str(ret)

    def to_key(self):
        return str(self.id)

    def clone(self):
        c = E3VswitchLANZone()
        c.id = self.id
        c.name = self.name
        c.zone_type = self.zone_type
        c.min_vlan = self.min_vlan
        c.max_vlan = self.max_vlan
        return c


def load_e3switch_lanzone_from_db():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        lanzones = session.query(E3VswitchLANZone).all()
        for lanzone in lanzones:
            root_keeper.set('vswitch_lan_zone', lanzone.id, lanzone.clone())
    finally:
        session.close()


register_database_load_entrance('vswitch_lan_zone',
                                load_e3switch_lanzone_from_db)


def db_register_e3vswitch_lanzone(fields_create_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        lanzone = session.query(E3VswitchLANZone).filter(
            E3VswitchLANZone.name == fields_create_dict['name']).first()
        if lanzone:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT,
                               'item:%s already in database' % (lanzone))
        else:
            lanzone = E3VswitchLANZone()
            lanzone.id = str(uuid4())
            for field in fields_create_dict:
                setattr(lanzone, field, fields_create_dict[field])
            session.add(lanzone)
            session.commit()
            e3loger.info('registering lanzone:%s succeeds' % (lanzone))
            return lanzone.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_update_e3vswitch_lanzone(uuid, fields_change_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        lanzone = session.query(E3VswitchLANZone).filter(
            E3VswitchLANZone.id == uuid).first()
        if not lanzone:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND,
                               'vswitch lanzone %s not found' % (uuid))
        for field in fields_change_dict:
            if not hasattr(lanzone, field):
                raise e3_exception(
                    E3_EXCEPTION_INVALID_ARGUMENT,
                    '%s is not a valid field of E3VswitchLANZone' % (field))
            setattr(lanzone, field, fields_change_dict[field])
        session.commit()
        e3loger.info('update E3VswitchLANZone:%s with change:%s' %
                     (uuid, fields_change_dict))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_list_e3vswitch_lanzones():
    session = db_sessions[DB_NAME]()
    lst = None
    try:
        session.begin()
        lst = session.query(E3VswitchLANZone).all()
        return [zone.clone() for zone in lst]
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_get_e3vswitch_lanzone(uuid):
    session = db_sessions[DB_NAME]()
    lanzone = None
    try:
        session.begin()
        lanzone = session.query(E3VswitchLANZone).filter(
            E3VswitchLANZone.id == uuid).first()
        if not lanzone:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return lanzone.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_unregister_e3vswitch_lanzone(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        lanzone = session.query(E3VswitchLANZone).filter(
            E3VswitchLANZone.id == uuid).first()
        if lanzone:
            session.delete(lanzone)
            session.commit()
            e3loger.info('unregister E3VswitchLANZone:%s' % (lanzone))
        else:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
