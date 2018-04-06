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
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_UNKNOWN
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_ACTIVE
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_INACTIVE
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_MAINTENANCE
from e3net.common.e3def import E3VSWITCH_INTERFACE_TYPE_SHARED
from e3net.common.e3def import E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE
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
from e3net.common.e3keeper import root_keeper
from e3net.db.db_base import register_database_load_entrance

e3loger = get_e3loger('e3vswitch_controller')

DB_NAME = 'E3NET_VSWITCH'


class E3VswitchInterface(DB_BASE):
    __tablename__ = 'vswitch_interface'

    id = Column(String(64), primary_key=True)
    host_id = Column(String(64), ForeignKey('vswitch_host.id'), nullable=False)
    dev_address = Column(Text, nullable=False)
    interface_status = Column(
        Enum(E3VSWITCH_INTERFACE_STATUS_UNKNOWN,
             E3VSWITCH_INTERFACE_STATUS_ACTIVE,
             E3VSWITCH_INTERFACE_STATUS_INACTIVE,
             E3VSWITCH_INTERFACE_STATUS_MAINTENANCE),
        nullable=False,
        default=E3VSWITCH_INTERFACE_STATUS_UNKNOWN)
    interface_type = Column(
        Enum(E3VSWITCH_INTERFACE_TYPE_SHARED,
             E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE),
        nullable=False,
        default=E3VSWITCH_INTERFACE_TYPE_SHARED)
    #infrastructure lan zone is the area that the interface is attached to
    lanzone_id = Column(
        String(64), ForeignKey('vswitch_lan_zone.id'), nullable=False)
    reference_count = Column(Integer(), default=0, nullable=False)

    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['host_id'] = self.host_id
        ret['dev_address'] = self.dev_address
        ret['interface_status'] = self.interface_status
        ret['interface_type'] = self.interface_type
        ret['lanzone_id'] = self.lanzone_id
        ret['reference_count'] = self.reference_count
        return str(ret)

    def to_key(self):
        return str(self.id)

    def clone(self):
        c = E3VswitchInterface()
        c.id = self.id
        c.host_id = self.host_id
        c.dev_address = self.dev_address
        c.interface_status = self.interface_status
        c.interface_type = self.interface_type
        c.lanzone_id = self.lanzone_id
        c.reference_count = self.reference_count
        return c


def load_e3vswitch_interfaces_from_db():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        ifaces = session.query(E3VswitchInterface).all()
        for iface in ifaces:
            root_keeper.set('vswitch_interface', iface.id, iface.clone())
    finally:
        session.close()


register_database_load_entrance('vswitch_interface',
                                load_e3vswitch_interfaces_from_db)


def db_register_e3vswitch_interface(fields_create_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        iface = session.query(E3VswitchInterface).filter(
            and_(E3VswitchInterface.host_id == fields_create_dict['host_id'],
                 E3VswitchInterface.dev_address == fields_create_dict[
                     'dev_address'])).first()
        if iface:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        else:
            iface = E3VswitchInterface()
            iface.id = str(uuid4())
            for field in fields_create_dict:
                setattr(iface, field, fields_create_dict[field])
            session.add(iface)
            session.commit()
            e3loger.info('registering E3VswitchInterface:%s succeeds' %
                         (iface))
            return iface.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_update_e3vswitch_interface(uuid, fields_change_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        iface = session.query(E3VswitchInterface).filter(
            E3VswitchInterface.id == uuid).first()
        if not iface:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        for field in fields_change_dict:
            if not hasattr(iface, field):
                raise e3_exception(
                    E3_EXCEPTION_INVALID_ARGUMENT,
                    '%s is not a valid field of E3VswitchInterface' % (field))
            setattr(iface, field, fields_change_dict[field])
        session.commit()
        e3loger.info('update E3VswitchLANZone:%s with change:%s' %
                     (uuid, fields_change_dict))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_list_e3vswitch_interfaces():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        lst = session.query(E3VswitchInterface).all()
        return [iface.clone() for iface in lst]
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_get_e3vswitch_interface(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        iface = session.query(E3VswitchInterface).filter(
            E3VswitchInterface.id == uuid).first()
        if not iface:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return iface.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_unregister_e3vswitch_interface(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        iface = session.query(E3VswitchInterface).filter(
            E3VswitchInterface.id == uuid).first()
        if not iface:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        if iface.reference_count != 0:
            raise e3_exception(E3_EXCEPTION_IN_USE)
        session.delete(iface)
        session.commit()
        e3loger.info('unregister E3VswitchInterface:%s' % (iface))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
