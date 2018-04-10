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
from e3net.common.e3def import E3NET_ETHER_SERVICE_TYPE_LINE
from e3net.common.e3def import E3NET_ETHER_SERVICE_TYPE_LAN
from e3net.common.e3def import E3NET_ETHER_SERVICE_LINK_SHARED
from e3net.common.e3def import E3NET_ETHER_SERVICE_LINK_EXCLUSIVE
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from datetime import datetime
from uuid import uuid4

from e3net.common.e3log import get_e3loger
import traceback
from e3net.common.e3keeper import root_keeper
from e3net.db.db_base import register_database_load_entrance

e3loger = get_e3loger('e3vswitch_controller')

DB_NAME = 'E3NET_VSWITCH'


class E3EtherService(DB_BASE):
    __tablename__ = 'ether_service'

    id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=False)
    service_type = Column(
        Enum(E3NET_ETHER_SERVICE_TYPE_LINE, E3NET_ETHER_SERVICE_TYPE_LAN),
        nullable=False)
    tenant_id = Column(String(64), ForeignKey('tenant.id'), nullable=False)
    created_at = Column(DateTime(), nullable=False, default=datetime.now)
    link_type = Column(
        Enum(E3NET_ETHER_SERVICE_LINK_SHARED,
             E3NET_ETHER_SERVICE_LINK_EXCLUSIVE),
        nullable=False,
        default=E3NET_ETHER_SERVICE_LINK_SHARED)

    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['name'] = self.name
        ret['service_type'] = self.service_type
        ret['tenant_id'] = self.tenant_id
        ret['created_at'] = self.created_at.ctime()
        ret['link_type'] = self.link_type
        return str(ret)

    def to_key(self):
        return str(self.id)

    def clone(self):
        c = E3EtherService()
        c.id = self.id
        c.name = self.name
        c.service_type = self.service_type
        c.tenant_id = self.tenant_id
        c.created_at = self.created_at
        c.link_type = self.link_type
        return c


def laod_ether_services_from_db():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        services = session.query(E3EtherService).all()
        for svc in services:
            root_keeper.set('ether_service', svc.id, svc.clone())
    finally:
        session.close()


register_database_load_entrance('ether_service', laod_ether_services_from_db)


def db_register_vswitch_ether_service(fields_create_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        service = E3EtherService()
        service.id = str(uuid4())
        for field in fields_create_dict:
            setattr(service, field, fields_create_dict[field])
        session.add(service)
        session.commit()
        e3loger.info('registering E3EtherService:%s succeeds' % (service))
        return service.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_get_vswitch_ether_service(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        service = session.query(E3EtherService).filter(
            E3EtherService.id == uuid).first()
        if not service:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return service.clone()
    finally:
        session.close()


def db_list_vswitch_ether_services():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        services = session.query(E3EtherService).all()
        return [svc.clone() for svc in services]
    finally:
        session.close()


def db_unregiser_vswitch_service(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        service = session.query(E3EtherService).filter(
            E3EtherService.id == uuid).first()
        if not service:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(service)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
