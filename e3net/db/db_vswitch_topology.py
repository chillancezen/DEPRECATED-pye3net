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
from sqlalchemy import and_
from sqlalchemy import or_
from datetime import datetime
from uuid import uuid4
from e3net.common.e3log import get_e3loger
DB_NAME='E3NET_VSWITCH'
e3loger=get_e3loger('e3vswitch_controller')

#note this is undirected edge
class E3TopologyEdge(DB_BASE):
    __tablename__='topology_edge'

    id=Column(String(64),primary_key=True)
    interface0=Column(String(64),ForeignKey('vswitch_interface.id'),nullable=False)
    interface1=Column(String(64),ForeignKey('vswitch_interface.id'),nullable=False)
    service_id=Column(String(64),ForeignKey('ether_service.id'),nullable=False)
    

    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['interface0']=self.interface0
        ret['interface1']=self.interface1
        ret['service_id']=self.service_id
        return str(ret)

    def to_key(self):
        return str(self.id)

    def clone(self):
        edge=E3TopologyEdge()
        edge.id=self.id
        edge.interface0=self.interface0
        edge.interface1=self.interface1
        edge.service_id=self.service_id
        return edge

def db_register_vswitch_topology_edge(fields_create_dict):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        edge=session.query(E3TopologyEdge).filter(or_(
            and_(E3TopologyEdge.interface0==fields_create_dict['interface0'],
                E3TopologyEdge.interface1==fields_create_dict['interface1'],
                E3TopologyEdge.service_id==fields_create_dict['service_id']),
            and_(E3TopologyEdge.interface0==fields_create_dict['interface1'],
                E3TopologyEdge.interface1==fields_create_dict['interface0'],
                E3TopologyEdge.service_id==fields_create_dict['service_id']))).first()
        if edge:
            raise e3_exception(E3_EXCEPTION_BE_PRESENT)
        edge=E3TopologyEdge()
        edge.id=str(uuid4())
        edge.interface0=fields_create_dict['interface0']
        edge.interface1=fields_create_dict['interface1']
        edge.service_id=fields_create_dict['service_id']
        session.add(edge)
        session.commit()
        return edge.clone()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def db_get_vswitch_topology_edge(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        edge=session.query(E3TopologyEdge).filter(E3TopologyEdge.id==uuid).first()
        if not edge:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return edge
    finally:
        session.close()

def db_list_vswitch_topology_edges():
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        edges=session.query(E3TopologyEdge).all()
        return edges
    finally:
        session.close()

def db_unregister_vswitch_topology_edge(uuid):
    session=db_sessions[DB_NAME]()
    try:
        session.begin()
        edge=session.query(E3TopologyEdge).filter(E3TopologyEdge.id==uuid).first()
        if not edge:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(edge)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
