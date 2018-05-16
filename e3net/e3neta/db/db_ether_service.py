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
from sqlalchemy import Boolean
from sqlalchemy import and_
from sqlalchemy import ForeignKey
from uuid import uuid4
from e3net.common.e3rwlock import e3rwlock
from e3net.common.e3def import E3NET_ETHER_SERVICE_TYPE_LINE
from e3net.common.e3def import E3NET_ETHER_SERVICE_TYPE_LAN
from e3net.common.e3def import E3NET_ETHER_SERVICE_LINK_SHARED
from e3net.common.e3def import E3NET_ETHER_SERVICE_LINK_EXCLUSIVE
from e3net.rpc.grpc_service.ether_service_client import rpc_client_get_ether_service
from e3net.rpc.grpc_service.ether_service_client import rpc_service as ether_service_rpc_service
from e3net.e3neta.e3neta_config import get_host_agent
from e3net.rpc.grpc_client import get_stub

DB_NAME = 'e3net_agent'
ether_service_guard = e3rwlock()

class agent_ether_service(DB_BASE):
    __tablename__ = 'agent_ether_service'
    id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=False)
    service_type = Column(
        Enum(E3NET_ETHER_SERVICE_TYPE_LINE, E3NET_ETHER_SERVICE_TYPE_LAN),
        nullable=False)
    tenant_id = Column(String(64), nullable=False)
    created_at = Column(String(64), nullable=False)
    link_type = Column(
        Enum(E3NET_ETHER_SERVICE_LINK_SHARED,
        E3NET_ETHER_SERVICE_LINK_EXCLUSIVE),
        nullable=False)
    def clone(self):
        c = agent_ether_service()
        c.id = self.id
        c.name = self.name
        c.service_type = self.service_type
        c.tenant_id = self.tenant_id
        c.created_at = self.created_at
        c.link_type = self.link_type
        return c
    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['name'] = self.name
        ret['service_type'] = self.service_type
        ret['tenant_id'] = self.tenant_id
        ret['created_at'] = self.created_at
        ret['link_type'] = self.link_type
        return str(ret)

def db_update_ether_service(service_id):
    agent = get_host_agent()
    ether_service_stub = get_stub(agent.current_controller,
        agent.controller_port,
        ether_service_rpc_service)
    session = db_sessions[DB_NAME]()
    try:
        ether_service_guard.write_lock()
        session.begin()
        local_service = session.query(agent_ether_service).filter(
            agent_ether_service.id == service_id).first()
        if local_service:
            return local_service.clone()
        local_service = agent_ether_service()
        shadow_service = rpc_client_get_ether_service(ether_service_stub, service_id)
        local_service.id = shadow_service.id
        local_service.name = shadow_service.name
        local_service.service_type = shadow_service.service_type
        local_service.tenant_id = shadow_service.tenant_id
        local_service.created_at = shadow_service.created_at
        local_service.link_type = shadow_service.link_type
        session.add(local_service)
        session.commit()
        return local_service.clone()
    finally:
        session.close()
        ether_service_guard.write_unlock()
def db_list_ether_service():
    session = db_sessions[DB_NAME]()
    try:
        ether_service_guard.read_lock()
        session.begin()
        services = session.query(agent_ether_service).all()
        return [s.clone() for s in services]
    finally:
        session.close()
        ether_service_guard.read_unlock()
def db_get_ether_service(service_id):
    session = db_sessions[DB_NAME]()
    try:
        ether_service_guard.read_lock()
        session.begin()
        service = session.query(agent_ether_service).filter(
            agent_ether_service.id == service_id).first()
        if not service:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return service.clone()
    finally:
        session.close()
        ether_service_guard.read_unlock()

def db_delete_ether_service(service_id):
    session = db_sessions[DB_NAME]()
    try:
        ether_service_guard.write_lock()
        session.begin()
        service = session.query(agent_ether_service).filter(
            agent_ether_service.id == service_id).first()
        if not service:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(service)
        session.commit()
    finally:
        session.close()
        ether_service_guard.write_unlock()
