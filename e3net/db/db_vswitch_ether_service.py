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
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from datetime import datetime
from uuid import uuid4

from e3net.common.e3log import get_e3loger
import traceback


e3loger=get_e3loger('e3vswitch_controller')

DB_NAME='E3NET_VSWITCH'

E3NET_ETHER_SERVICE_TYPE_LINE='e-line'
E3NET_ETHER_SERVICE_TYPE_LAN='e-lan'


class E3EtherService(DB_BASE):
    __tablename__='ether_service'
    
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False)
    service_type=Column(Enum(E3NET_ETHER_SERVICE_TYPE_LINE,E3NET_ETHER_SERVICE_TYPE_LAN),nullable=False)
    #preserve this field for multi-tenancy purpose
    #tenant_id=Column(String(64),nullable=False,ForeignKey('***.**'))
    created_at=Column(DateTime(),nullable=False,default=datetime.now)

