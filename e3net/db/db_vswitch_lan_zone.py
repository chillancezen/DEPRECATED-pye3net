#
#Copyright (c) 2018 Jie Zheng
#
from e3net.db.db_base import db_sessions
from e3net.db.db_base import DB_BASE
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from uuid import uuid4


DB_NAME='E3NET_VSWITCH'

E3VSWITCH_LAN_ZONE_TYPE_BACKBONE='backbone'
E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER='customer'

class E3VswitchLANZone(DB_BASE):
    __tablename__='vswitch_lan_zone'
    
    id=Column(String(64),primary_key=True)
    name=Column(String(64),nullable=False,index=True,unique=True)
    zone_type=Column(Enum(E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER,
            E3VSWITCH_LAN_ZONE_TYPE_BACKBONE),
                nullable=False,
                default=E3VSWITCH_LAN_ZONE_TYPE_CUSTOMER)

    def __str__(self):
        ret=dict()
        ret['id']=self.id
        ret['name']=self.name
        ret['zone_type']=self.zone_type
        return str(ret)
    
