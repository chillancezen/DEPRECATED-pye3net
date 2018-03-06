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
from sqlalchemy import Boolean
from datetime import datetime
from e3net.common.e3log import get_e3loger
from uuid import uuid4
import json
import hashlib
from e3net.common.e3keeper import root_keeper
from e3net.db.db_base import register_database_load_entrance

DB_NAME = 'E3NET_VSWITCH'
token_alive_time = 30  #token alove in minutes
e3loger = get_e3loger('e3vswitch_controller')


class Role(DB_BASE):
    __tablename__ = 'role'

    id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    def __str__(self):
        obj = dict()
        obj['id'] = self.id
        obj['name'] = self.name
        obj['description'] = self.description
        return str(obj)

    def to_key(self):
        return str(self.id)

    def clone(self):
        c = Role()
        c.id = self.id
        c.name = self.name
        c.description = self.description
        c.is_admin = self.is_admin
        return c


def load_roles_from_db():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        roles = session.query(Role).all()
        for role in roles:
            root_keeper.set('role', role.id, role.clone())
    finally:
        session.close()


register_database_load_entrance('role', load_roles_from_db)


def db_register_role(fields_create_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        role = session.query(Role).filter(
            Role.name == fields_create_dict['name']).first()
        if role:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        else:
            role = Role()
            role.id = str(uuid4())
            for field in fields_create_dict:
                setattr(role, field, fields_create_dict[field])
            session.add(role)
            session.commit()
            e3loger.info('registering role:%s succeeds' % (str(role)))
            return role.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_update_role(uuid, fields_change_dict):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        role = session.query(Role).filter(Role.id == uuid).first()
        if not role:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        for field in fields_change_dict:
            if not hasattr(role, field):
                raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)
            setattr(role, field, fields_change_dict[field])
        session.commit()
        e3loger.info('update Role:%s with change:%s' % (uuid,
                                                        fields_change_dict))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_list_roles():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        roles = session.query(Role).all()
        return [role.clone() for role in roles]
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_get_role(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        role = session.query(Role).filter(Role.id == uuid).first()
        if not role:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return role.clone()
    except Exception as e:
        raise e
    finally:
        session.close()


def db_unregister_role(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        role = session.query(Role).filter(Role.id == uuid).first()
        if not role:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(role)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
