#! /usr/bin/python
from e3net.common.e3exception import e3_exception
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
        return self.id
    
class Tenant(DB_BASE):
    __tablename__='tenant'
    
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    passwd=Column(String(64),nullable=False)
    description=Column(Text,nullable=True)
    enabled=Column(Boolean,nullable=False)
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
        return self.id

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
        return self.id

def db_register_role(role_name,is_admin=False,desc=''):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        role=session.query(Role).filter(Role.name==role_name).first()
        if role:
            role.is_admin=is_admin
            role.description=desc
        else:
            role=Role()
            role.id=str(uuid4())
            role.name=role_name
            role.description=desc
            role.is_admin=is_admin
            session.add(role)
        session.commit()
        e3loger.info('register/update role:%s'%(str(role)))
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def db_list_roles():
    roles=None
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        roles=session.query(Role).all()
    except:
        roles=list()
        session.rollback()
    finally:
        session.close()
    return roles;

def db_get_role(role_id):
    role=None
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        role=session.query(Role).filter(Role.id==role_id).first()
    except:
        pass
    finally:
        session.close()
    return role


def get_role_id_by_name(role_name):
    role_id=None
    role=get_role_by_name(role_name)
    if role:
        role_id=role.id
    return role_id
def unregister_role(role_name):
    role=get_role_by_name(role_name)
    if role:
        try:
            session=db_sessions[DB_NAME]()
            session.begin()
            session.delete(role)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

def register_tenant(username,passwd,role_id=None,desc=''):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=Tenant()
        tenant.id=str(uuid4())
        tenant.name=username
        tenant.passwd=passwd
        tenant.description=desc
        tenant.enabled=False
        tenant.role_id=role_id
        if not role_id:
            tenant.role_id=get_role_id_by_name('member')
        session.add(tenant)
        session.commit()
    except:
        session.rollback()
        return False
    finally:
        session.close()
    return True

def find_tenant_by_name(username):
    tenant=None
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.name==username).first()
    except:
        tenant=None
    finally:
        session.close()
    return tenant
def get_tenant_by_id(id):
    tenant=None
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.id==id).first()
    except:
        tenant=None
    finally:
        session.close()
    return tenant
def get_tenants():
    lst=list()
    session=db_sessions[DB_NAME]()
    try:
        lst=session.query(Tenant).all()
    except:
        lst=list()
    finally:
        session.close()
    return lst
def _change_tenant_status(id,status):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.id==id).first()
        if tenant:
            tenant.enabled=status
            session.commit()
    except:
        session.rollback()
        return False
    finally:
        session.close()
    return True
def enable_tenant(id):
    return _change_tenant_status(id,True)

def disable_tenant(id):
    return _change_tenant_status(id,False)

def unregister_tenant(id):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        tenant=session.query(Tenant).filter(Tenant.id==id).first()
        if tenant :
            session.delete(tenant)
            session.commit()
    except:
        session.rollback()
        return False
    finally:
        session.close()
    return True
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
    db_register_role('admin',True,'unique admin role,void')
    db_register_role('non-admin',False,'none-admin role')
    print([str(r) for r in db_list_roles()])
    #init_e3common_database('mysql+pymysql://e3net:e3credientials@localhost/E3common',True)
    #create_e3common_database_entries()
    #print(register_role('member'))
    #print register_role('admin',desc='administrator role')
    #print register_role('__member__')
    #print get_role_id_by_name('admin')
    #unregister_role('admin')
    #unregister_role('member')
    #print(register_tenant('jzheng1','181218zj',desc='my beloved',role_id=get_role_id_by_name('admin')))
    #print find_tenant_by_name('jzheng')
    #print get_role_by_id('78eeab15-3118-4fac-aa3d-2ab6f8a920d0')
    #print get_role_by_id('c6bf5a3b-6159-4167-a6b7-91499a74ec2a')
    #print get_tenant_by_id('98761cbc-0c6f-40ce-a274-2b896f5809ad')
    #print disable_tenant('98761cbc-0c6f-40ce-a274-2b896f5809ad')
    #print unregister_tenant('447c2cb9-eb7e-4f25-b821-5ffa503b87c8')
    #print(generate_token('jzheng1','181218zj'))
    #print validate_token(get_token_by_id('a564f7e86682f6b1ff50ded5f3e7968d2cc46ca2')) 
    #print(validate_token(get_token_by_id(generate_token('jzheng1','181218zj'))))
    #print generate_token('jzheng','181218zjs')
    #clean_invalid_token()
