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

DB_NAME='E3NET_VSWITCH'
token_alive_time=30 #token alove in minutes
e3loger=get_e3loger('e3vswitch_controller')

class Tenant(DB_BASE):
    __tablename__='tenant'

    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    passwd=Column(String(64),nullable=False)
    description=Column(Text,nullable=True)
    enabled=Column(Boolean,nullable=False,default=False)
    role_id=Column(String(64),ForeignKey('role.id'))

    def __str__(self):
        obj=dict()
        obj['id']=self.id
        obj['name']=self.name
        obj['passwd']=self.passwd
        obj['description']=self.description
        obj['enabled']=self.enabled
        obj['role_id']=self.role_id
        return str(obj)

    def to_key(self):
        return str(self.id)


def db_register_tenant(fields_create_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.name==fields_create_dict['name']).first()
        if tenant:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        tenant=Tenant()
        tenant.id=str(uuid4())
        for field in fields_create_dict:
            setattr(tenant,field,fields_create_dict[field])
        session.add(tenant)
        session.commit()
        e3loger.info('registering Tenant(Tenant):%s succeeds'%(tenant))
        return tenant
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_update_tenant(uuid,fields_change_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.id==uuid).first()
        if not tenant:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        for field in fields_change_dict:
            if not hasattr(tenant,field):
                raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)
            setattr(tenant,field,fields_change_dict[field])
        session.commit()
        e3loger.info('update Tenant(Tenant):%s with change:%s'%(uuid,fields_change_dict))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_get_tenant(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.id==uuid).first()
        if not tenant:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return tenant
    finally:
        session.close()
 
def db_list_tenants():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenants=session.query(Tenant).all()
        return tenants
    finally:
        session.close()
    
def db_unregister_tenant(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.id==uuid).first()
        if not tenant:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(tenant)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

