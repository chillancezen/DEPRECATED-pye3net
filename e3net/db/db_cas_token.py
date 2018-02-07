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
from e3net.db.db_cas_tenant import  Tenant

DB_NAME='E3NET_VSWITCH'
token_alive_time=30 #token alove in minutes
e3loger=get_e3loger('e3vswitch_controller')


class Token(DB_BASE):
    __tablename__='token'

    id=Column(String(64),primary_key=True)
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


def db_register_token(fields_create_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        assert('name' in fields_create_dict)
        assert('passwd' in fields_create_dict)
        tenant=session.query(Tenant).filter(Tenant.name==fields_create_dict['name']).first()
        if not tenant or tenant.passwd!=fields_create_dict['passwd']:
            raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)
        token=Token()
        token.id=str(uuid4())
        token.tenant_id=tenant.id
        session.add(token)
        session.commit()
        e3loger.info('registering Token:%s succeeds'%(token))
        return token
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_update_token(uuid,fields_change_dict=None):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        token=session.query(Token).filter(Token.id==uuid).first()
        if not token:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        token.created_at=datetime.now()
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
def db_get_token(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        token=session.query(Token).filter(Token.id==uuid).first()
        if not token:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return token
    except Exception as e:
        raise e
    finally:
        session.close()

def db_list_tokens():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        lst=session.query(Token).all()
        return lst
    except Exception as e:
        raise e
    finally:
        session.close()

def db_unregister_token(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        token=session.query(Token).filter(Token.id==uuid).first()
        if not token:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(token)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


