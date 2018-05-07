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
DB_NAME = 'e3net_agent'

LABEL_DIRECTION_INGRESS = 'ingress'
LABEL_DIRECTION_EGRESS = 'egress'

DUMMY_MULTICAST_LANZONE = 'dummy_multicast_lanzone'

class topology_label(DB_BASE):
    __tablename__ = 'topology_label'
    id = Column(String(64), primary_key = True)
    customer_lanzone = Column(String(64), nullable = False)
    neighbor_id = Column(String(64), ForeignKey('topology_neighbor.id'), nullable = False)
    interface_id = Column(String(64), nullable = False)
    label_id = Column(Integer(), nullable = False)
    direction = Column(Enum(LABEL_DIRECTION_INGRESS,
        LABEL_DIRECTION_EGRESS),nullable = False)
    service_id = Column(String(64), nullable = False)
    is_unicast = Column(Boolean(), nullable = False, default = True)

    def __str__(self):
        ret = dict()
        ret['id'] = self.id
        ret['customer_lanzone'] = self.customer_lanzone
        ret['neighbor_id'] = self.neighbor_id
        ret['interface_id'] = self.interface_id
        ret['label_id'] = self.label_id
        ret['direction'] = self.direction
        ret['service_id'] = self.service_id
        ret['is_unicast'] = self.is_unicast
        return str(ret)

    def clone(self):
        l = topology_label()
        l.id = self.id
        l.customer_lanzone =self.customer_lanzone
        l.neighbor_id = self.neighbor_id
        l.interface_id = self.interface_id
        l.label_id = self.label_id
        l.direction = self.direction
        l.service_id = self.service_id
        l.is_unicast = self.is_unicast
        return l

topology_label_guard = e3rwlock()
#calculate the label_id for the nexthop
def db_update_topology_label(customer_lanzone,
    interface_id,
    neighbor_id,
    direction,
    service_id,
    allocated_label_id = None):
    assert (direction in [LABEL_DIRECTION_INGRESS,
        LABEL_DIRECTION_EGRESS])
    assert (allocated_label_id if \
        direction == LABEL_DIRECTION_EGRESS else True)
    session = db_sessions[DB_NAME]()
    try:
        topology_label_guard.write_lock()
        session.begin()
        labels = session.query(topology_label).filter(and_(
            topology_label.interface_id == interface_id,
            topology_label.direction == direction)).order_by(
            topology_label.label_id).all()
        target_label = None
        least_label_id = 1
        for _label in labels:
            if _label.service_id == service_id and \
                _label.customer_lanzone == customer_lanzone:
                target_label = _label
                break
            if _label.label_id == least_label_id:
                least_label_id += 1
        if target_label:
            #if a ingress is allocated, it will not change
            target_label.label_id = allocated_label_id if \
                direction == LABEL_DIRECTION_EGRESS else \
                target_label.label_id
            session.commit()
        else:
            target_label = topology_label()
            target_label.id =str(uuid4())
            target_label.service_id = service_id
            target_label.customer_lanzone = customer_lanzone
            target_label.neighbor_id = neighbor_id
            target_label.interface_id = interface_id
            target_label.direction = direction
            target_label.is_unicast = True if \
                customer_lanzone == DUMMY_MULTICAST_LANZONE else \
                False
            target_label.label_id = allocated_label_id if \
                direction == LABEL_DIRECTION_EGRESS else \
                least_label_id
            session.add(target_label)
            session.commit()
        return target_label.clone()
    finally:
        session.close()
        topology_label_guard.write_unlock()
def db_get_topology_label(service_id,
    customer_lanzone,
    direction,
    interface_id = None):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        topology_label_guard.read_lock()
        filter_condition = None
        if interface_id:
            filter_condition = and_(
                topology_label.service_id == service_id,
                topology_label.customer_lanzone == customer_lanzone,
                topology_label.direction == direction,
                topology_label.interface_id == interface_id)
        else:
            filter_condition = and_(
                topology_label.service_id == service_id,
                topology_label.customer_lanzone == customer_lanzone,
                topology_label.direction == direction)
        labels = session.query(topology_label).filter(filter_condition).all()
        return [l.clone() for l in labels]
    finally:
        topology_label_guard.read_unlock()
        session.close()
def db_list_topology_labels(service_id = None, direction = None):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        topology_label_guard.read_lock()
        filter_condition = and_()
        if service_id and direction:
            filter_condition = and_(
                topology_label.service_id == service_id,
                topology_label.direction == direction)
        elif service_id and not direction:
            filter_condition = and_(topology_label.service_id == service_id)
        elif not service_id and direction:
            filter_condition = and_(topology_label.direction == direction)
        labels = session.query(topology_label).filter(filter_condition).all()
        return [l.clone() for l in labels]
    finally:
        topology_label_guard.read_unlock()
        session.close()
def db_delete_topology_label(uuid):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        topology_label_guard.write_lock()
        label = session.query(topology_label).filter(topology_label.id == uuid).first()
        if not label:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        session.delete(label)
        session.commit()
    finally:
        topology_label_guard.write_unlock()
        session.close()
if __name__ == '__main__':
    from e3net.db.db_base import init_database
    from e3net.db.db_base import create_database_entries
    from e3net.e3neta.db.db_topology_neighbor import topology_neighbor
    init_database('e3net_agent','sqlite:////var/run/e3net/e3neta.db',False)
    create_database_entries('e3net_agent')
    from e3net.e3neta.db.db_topology_neighbor import register_topology_neighbor
    n = register_topology_neighbor('hello', 'world')
    print(n)
    l = db_update_topology_label('customer.lan0',n.local_interface_id, n.id, LABEL_DIRECTION_INGRESS,'service.0')
    l = db_update_topology_label('customer.lan0',n.local_interface_id+'1', n.id, LABEL_DIRECTION_INGRESS,'service.0')
    l = db_update_topology_label('customer.lan0',n.local_interface_id, n.id, LABEL_DIRECTION_INGRESS,'service.1')
    l = db_update_topology_label('customer.lan0',n.local_interface_id, n.id, LABEL_DIRECTION_INGRESS,'service.1')
    l = db_update_topology_label('customer.lan0',n.local_interface_id, n.id, LABEL_DIRECTION_INGRESS,'service.1', 332)
    l = db_update_topology_label('DUMMY_MULTICAST_LANZONE',n.local_interface_id, n.id, LABEL_DIRECTION_INGRESS, 'service.0')
    l = db_update_topology_label('DUMMY_MULTICAST_LANZONE',n.local_interface_id, n.id, LABEL_DIRECTION_EGRESS, 'service.0', 23)
    l = db_update_topology_label('DUMMY_MULTICAST_LANZONE',n.local_interface_id, n.id, LABEL_DIRECTION_EGRESS, 'service.1', 2323)
    #l = register_topology_label('customer.lan2', n.id, LABEL_DIRECTION_INGRESS,'service.0')
    #labels = db_get_topology_label('service.0', 'customer.lan0', LABEL_DIRECTION_EGRESS, n.local_interface_id)
    labels = db_list_topology_labels()
    for l in labels:
        #db_delete_topology_label(l.id)
        print(l)
