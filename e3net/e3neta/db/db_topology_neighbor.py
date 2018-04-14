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
from sqlalchemy import and_
from uuid import uuid4
from e3net.common.e3rwlock import e3rwlock
DB_NAME = 'e3net_agent'

#all services share same neighbors set
class topology_neighbor(DB_BASE):
    __tablename__ = 'topology_neighbor'
    id = Column(String(64), primary_key = True)
    local_interface_id = Column(String(64), nullable = False)
    remote_interface_id = Column(String(64), nullable = False)

    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['local_interface_id'] = self.local_interface_id
        ret['remote_interface_id'] = self.remote_interface_id
        return str(ret)

    def clone(self):
        t = topology_neighbor()
        t.id = self.id
        t.local_interface_id = self.local_interface_id
        t.remote_interface_id = self.remote_interface_id
        return t

def get_topology_neighbor(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        neighbor = session.query(topology_neighbor).filter(topology_neighbor.id == uuid).first()
        if not neighbor:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return neighbor.clone()
    finally:
        session.close()

def get_topology_neighbor_by_interfaces(local_interface_id, remote_interface_id):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        neighbor = session.query(topology_neighbor).filter(and_(
            topology_neighbor.local_interface_id == local_interface_id,
            topology_neighbor.remote_interface_id == remote_interface_id)).first()
        if not neighbor:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return neighbor.clone()
    finally:
        session.close()

def list_topology_neighbors():
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        lst = session.query(topology_neighbor).all()
        return [n.clone() for n in lst]
    finally:
        session.close()
registry_guard = e3rwlock()
def register_topology_neighbor(local_interface_id, remote_interface_id):
    session = db_sessions[DB_NAME]()
    try:
        registry_guard.write_lock()
        session.begin()
        neighbor = session.query(topology_neighbor).filter(and_(
            topology_neighbor.local_interface_id == local_interface_id,
            topology_neighbor.remote_interface_id == remote_interface_id)).first()
        if neighbor:
            return neighbor.clone()
        neighbor = topology_neighbor()
        neighbor.id = str(uuid4())
        neighbor.local_interface_id = local_interface_id
        neighbor.remote_interface_id = remote_interface_id
        session.add(neighbor)
        session.commit()
        return neighbor.clone()
    finally:
        session.close()
        registry_guard.write_unlock()
def unregister_topology_neighbor(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        neighbor = session.query(topology_neighbor).filter(topology_neighbor.id == uuid).first()
        if not neighbor:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(neighbor)
        session.commit()
    finally:
        session.close()

if __name__ == '__main__':
    from e3net.db.db_base import init_database
    init_database('e3net_agent', 'sqlite:////var/run/e3net/e3neta.db', False)
    n = register_topology_neighbor('hello', 'world')
    print(n)
    print(get_topology_neighbor(n.id))
    print(get_topology_neighbor_by_interfaces('hello','world'))
    for i in list_topology_neighbors():
        print(i)
    unregister_topology_neighbor(n.id)
