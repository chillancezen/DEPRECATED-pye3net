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
from uuid import uuid4

DB_NAME='E3NET_VSWITCH'
E3VSWITCH_HOST_STATUS_UNKNOWN='unknown'
E3VSWITCH_HOST_STATUS_ACTIVE='active'
E3VSWITCH_HOST_STATUS_INACTIVE='inactive'
E3VSWITCH_HOST_STATUS_MAINTENANCE='maintenance'

class E3VswitchHost(DB_BASE):
    __tablename__='vswitch_host'
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    description=Column(Text,nullable=True)
    host_ip=Column(String(32),nullable=False,unique=True)
    host_status=Column(Enum(E3VSWITCH_HOST_STATUS_UNKNOWN,
            E3VSWITCH_HOST_STATUS_ACTIVE,
            E3VSWITCH_HOST_STATUS_INACTIVE,
            E3VSWITCH_HOST_STATUS_MAINTENANCE),
                nullable=False,
                default=E3VSWITCH_HOST_STATUS_UNKNOWN)

    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['name']=self.name
        ret['description']=self.description
        ret['host_ip']=self.host_ip
        ret['host_status']=self.host_status
        return str(ret)

def register_e3vswitch_host(hostname,ip,desc=''):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.name==hostname).first()
        if host:
            host.description=desc
            host.host_ip=ip
        else:
            host=E3VswitchHost()
            host.id=str(uuid4())
            host.name=hostname
            host.description=desc
            host.host_ip=ip
            session.add(host)
        session.commit()
    except:
        session.rollback()
        raise e3_exception('make sure host\'s IP and hotsname are unique')
    finally:
        session.close()
def get_e3vswicth_host(hostname):
    session=db_sessions[DB_NAME]()
    host=None
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.name==hostname).first()
    except:
        host=None
        session.rollback()
    finally:
        session.close()
    return host

def list_e3vswitch_hosts():
    session=db_sessions[DB_NAME]()
    lst=None
    try:
        session.begin()
        lst=session.query(E3VswitchHost).all()
    except:
        lst=list()
        session.rollback()
    finally:
        session.close()
    return lst

def unregister_e3vswitch_host(hostname):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        host=session.query(E3VswitchHost).filter(E3VswitchHost.name==hostname).first()
        if host:
            session.delete(host)
            session.commit()
    except:
        session.rollback()
        raise e3_exception('host does not being in use by other entrities')
    finally:
        session.close()

if __name__=='__main__':
    from e3net.db.db_base import init_database
    from e3net.db.db_base import create_database_entries
    init_database(DB_NAME,'mysql+pymysql://e3net:e3credientials@localhost/E3NET_VSWITCH',False)
    create_database_entries(DB_NAME)
    register_e3vswitch_host('my-container-host','10.0.2.15','spine vswitch host')
    register_e3vswitch_host('my-container-host1','10.0.2.16','spine vswitch host')
    #unregister_e3vswitch_host('my-container-host')
    #unregister_e3vswitch_host('my-container-host2')
    #print(get_e3vswicth_host('my-container-host'))
    #print(get_e3vswicth_host('my-container-host1'))
    #print(get_e3vswicth_host('my-container-host2'))
    for i in list_e3vswitch_hosts():
        print(i)
    
