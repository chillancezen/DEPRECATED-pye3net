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

class Role(DB_BASE):
    __tablename__='role'
    
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    description=Column(Text,nullable=True)
    is_admin=Column(Boolean,nullable=False,default=False)

    def __str__(self):
        obj=dict()
        obj['id']=self.id
        obj['name']=self.name
        obj['description']=self.description
        return str(obj)

    def to_key(self):
        return str(self.id)
    
class Tenant(DB_BASE):
    __tablename__='tenant'
    
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    passwd=Column(String(64),nullable=False)
    description=Column(Text,nullable=True)
    enabled=Column(Boolean,nullable=False,default=False)
    role_id=Column(String(64),ForeignKey('role.id'))
   
    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['name']=self.name
        ret['passwd']=self.passwd
        ret['description']=self.description
        ret['enabled']=self.enabled
        ret['role_id']=self.role_id
        return str(ret)

    def to_key(self):
        return str(self.id)

class Token(DB_BASE):
    __tablename__='token'

    id=Column(String(64),primary_key=True) # sha1.update(uuid) as token id
    tenant_id=Column(String(64),ForeignKey('tenant.id'))
    created_at=Column(DateTime(),nullable=False,default=datetime.now)

    def __str__(self):
        obj=dict()
        obj['id']=self.id
        obj['tenant_id']=self.tenant_id
        obj['created_at']=self.created_at.ctime()
        return str(obj)

    def to_key(self):
        return str(self.id)

def db_register_role(fields_create_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        role=session.query(Role).filter(Role.name==fields_create_dict['name']).first()
        if role:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        else:
            role=Role()
            role.id=str(uuid4())
            for field in fields_create_dict:
                setattr(role,field,fields_create_dict[field])
            session.add(role)
            session.commit()
            e3loger.info('registering role:%s succeeds'%(str(role)))
            return role
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_update_role(uuid,fields_change_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        role=session.query(Role).filter(Role.id==uuid).first()
        if not role:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        for field in fields_change_dict:
            if not hasattr(role,field):
                raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)
            setattr(role,field,fields_change_dict[field])
        session.commit()
        e3loger.info('update Role:%s with change:%s'%(uuid,fields_change_dict))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_list_roles():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        roles=session.query(Role).all()
        return roles
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_get_role(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        role=session.query(Role).filter(Role.id==uuid).first()
        if not role:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return role
    except Exception as e:
        raise e
    finally:
        session.close()

def db_unregister_role(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        role=session.query(Role).filter(Role.id==uuid).first()
        if not role:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(role)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_register_tenant(fields_create_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.name==fields_create_dict['name']).first()
        if tenant:
            e3_exception(E3_EXCEPTION_BE_PRESENT)
        tenant=Tenant()
        tenant.id=str(uuid4())
        for field in fields_create_dict:
            setattr(tenant,field,fields_create_dict[field])
        session.add(tenant)
        session.commit()
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
                raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT,'%s is not a valid field of Tenant'%(field))
            setattr(tenant,field,fields_change_dict[field])
        session.commit()
        e3loger.info('update Tenant:%s with change:%s'%(uuid,fields_change_dict))
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
    except Exception as e:
        raise e
    finally:
        session.close()

def db_list_tenants():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        lst=session.query(Tenant).all()
        return lst
    except Exception as e:
        raise e
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
        e3loger.info('unregister Tenant:%s'%(tenant))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def generate_token(username,passwd):
    token_id=None
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.name==username).first()
        if not tenant:
            return None
        if tenant.passwd != passwd :
            return None
        token=Token()
        sha=hashlib.sha1()
        uuid_str=str(uuid4()).encode('utf-8')
        sha.update(uuid_str)
        token.id=sha.hexdigest()
        token.tenant_id=tenant.id
        session.add(token)
        session.commit()
        token_id=token.id
    except:
        session.rollback()
    finally:
        session.close()
    return token_id

def get_token_by_id(token_id):
    session=db_sessions[DB_NAME]()
    token=None
    try:
        session.begin()
        token=session.query(Token).filter(Token.id==token_id).first()
    except:
        token=None
    finally:
        session.close()
    return token

def validate_token(token):
    if not token:
        return False
    now=datetime.now()
    diff=now-token.created_at
    minutes,seconds=divmod(diff.days * 86400 + diff.seconds, 60)
    if  token_alive_time<minutes:
        return False    
    return True

def clean_invalid_token():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tokens=session.query(Token).all()
        for token in tokens:
            now=datetime.now()
            diff=now-token.created_at
            minutes,seconds=divmod(diff.days * 86400 + diff.seconds, 60)
            if token_alive_time<minutes:
                session.delete(token)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()
if __name__=='__main__':
    from e3net.db.db_base import init_database
    from e3net.db.db_base import create_database_entries
    init_database(DB_NAME,'mysql+pymysql://e3net:e3credientials@localhost/E3NET_VSWITCH',False)
    create_database_entries('E3NET_VSWITCH')
    db_register_role({'name':'administrator@vsphere.remote','description':'meeeow'})
