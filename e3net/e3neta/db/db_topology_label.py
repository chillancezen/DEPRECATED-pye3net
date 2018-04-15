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

class topology_label(DB_BASE):
    __tablename__ = 'topology_label'
    id = Column(String(64), primary_key = True)
    customer_lanzone = Column(String(64), nullable = False)
    neighbor_id = Column(String(64), ForeignKey('topology_neighbor.id'), nullable = False)
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
        ret['label_id'] = self.label_id
        ret['direction'] = self.direction
        ret['service_id'] = self.service_id
        ret['is_unicast'] = self.is_unicast
        return str(ret)

    def __init__(self):
        l = topology_label()
        l.id = self.id
        l.customer_lanzone =self.customer_lanzone
        l.neighbor_id = self.neighbor_id
        l.label_id = self.label_id
        l.direction = self.direction
        l.service_id = self.service_id
        l.is_unicast = self.is_unicast
        return l

#calculate the label_id for the nexthop
def register_topology_label(customer_lanzone,
    neighbor_id,
    direction,
    service_id):
    session = db_sessions[DB_NAME]()
    try:
        session.begin()
        labels = session.query(topology_label).filter( \
            topology_label.service_id == service_id).order_by( \
            topology_label.label_id).all()
        for _label in labels:
            if _label.neighbor_id == neighbor_id:
                #label entry already exist, return it immediately
                return _label
    finally:
        session.close()
