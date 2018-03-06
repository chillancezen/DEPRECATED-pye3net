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
from sqlalchemy import DateTime
from datetime import datetime
from uuid import uuid4
from sqlalchemy import and_

from e3net.common.e3log import get_e3loger
import traceback
from e3net.common.e3keeper import root_keeper
from e3net.db.db_base import register_database_load_entrance

e3loger = get_e3loger('e3vswitch_controller')

DB_NAME = 'E3NET_VSWITCH'


class E3EtherServiceVlan(DB_BASE):
    __tablename__ = 'ether_service_vlan'

    id = Column(String(64), primary_key=True)
    service_id = Column(
        String(64), ForeignKey('ether_service.id'), nullable=False)
    lanzone_id = Column(
        String(64), ForeignKey('vswitch_lan_zone.id'), nullable=False)
    vlan_id = Column(Integer(), nullable=False)

    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['service_id'] = self.service_id
        ret['lanzone_id'] = self.lanzone_id
        ret['vlan_id'] = self.vlan_id
        return str(ret)

    def to_key(self):
        return str(self.id)

    def clone(self):
        c = E3EtherServiceVlan()
        c.id = self.id
        c.service_id = self.service_id
        c.lanzone_id = self.lanzone_id
        c.vlan_id = self.vlan_id
        return c


def load_ether_service_vlans_from_db():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        vlans = session.query(E3EtherServiceVlan).all()
        for vlan in vlans:
            root_keeper.set('ether_service_vlan', vlan.id, vlan.clone())
    finally:
        session.close()


register_database_load_entrance('ether_service_vlan',
                                load_ether_service_vlans_from_db)


def db_register_vswitch_ether_service_vlan(fields_create_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        vlan = session.query(E3EtherServiceVlan).filter(
            and_(E3EtherServiceVlan.lanzone_id == fields_create_dict[
                'lanzone_id'], E3EtherServiceVlan.vlan_id ==
                 fields_create_dict['vlan_id'])).first()
        if vlan:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        else:
            vlan = E3EtherServiceVlan()
            vlan.id = str(uuid4())
            for field in fields_create_dict:
                setattr(vlan, field, fields_create_dict[field])
            session.add(vlan)
            session.commit()
            e3loger.info('registering E3EtherServiceVlan:%s succeeds' % (vlan))
            return vlan.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_get_vswitch_ether_service_vlan(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        vlan = session.query(E3EtherServiceVlan).filter(
            E3EtherServiceVlan.id == uuid).first()
        if not vlan:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return vlan.clone()
    finally:
        session.close()


def db_list_vswitch_ether_service_vlans():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        vlans = session.query(E3EtherServiceVlan).all()
        return [vlan.clone() for vlan in vlans]
    finally:
        session.close()


def db_unregister_vswitch_ether_service_vlan(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        vlan = session.query(E3EtherServiceVlan).filter(
            E3EtherServiceVlan.id == uuid).first()
        if not vlan:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(vlan)
        session.commit()
        e3loger.info('unregister E3EtherServiceVlan:%s' % (uuid))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
