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


class CommonConfig():
    def __getitem__(self, idx):
        if idx not in self.__dict__:
            raise e3_exception(E3_EXCEPTION_INVALID_ARGUMENT)
        return getattr(self, idx)

    def __setitem__(self, idx, value):
        if idx not in self.__dict__:
            raise e3_exception(E3_EXCEPTION_NOT_SUPPORT)
        setattr(self, idx, value)

    def keys(self):
        return [k for k in self.__dict__]

    def __str__(self):
        return str(self.__dict__)


class EtherServiceCreateConfig(CommonConfig):
    def __init__(self):
        self.service_name = None
        self.service_type = None
        self.link_type = None
        self.tenant_id = None
        self.initial_lanzones = []
        self.ban_hosts = []
        self.ban_lanzones = []
        self.ban_interfaces = []

class EtherLANServiceUpdateConfig(CommonConfig):
    def __init__(self):
        self.service_id=None
        self.operation=None
        self.ban_hosts=[]
        self.ban_lanzones=[]
        self.ban_interfaces=[]
        self.initial_lanzones=[]

def util_create_interface(host_name, lanzone_name, dev_address):
    from e3net.inventory.invt_vswitch_lan_zone import invt_list_vswitch_lan_zones
    from e3net.inventory.invt_vswitch_host import invt_list_vswitch_hosts
    from e3net.inventory.invt_vswitch_interface import invt_register_vswitch_interface
    hosts = invt_list_vswitch_hosts()
    lanzones = invt_list_vswitch_lan_zones()
    host_id = None
    for _host in hosts:
        host = hosts[_host]
        if host.name == host_name:
            host_id = host.id
            break
    lanzones = invt_list_vswitch_lan_zones()
    lanzone_id = None
    for _lanzone in lanzones:
        lanzone = lanzones[_lanzone]
        if lanzone.name == lanzone_name:
            lanzone_id = lanzone.id
            break
    spec = dict()
    spec['host_id'] = host_id
    spec['dev_address'] = dev_address
    spec['lanzone_id'] = lanzone_id
    invt_register_vswitch_interface(spec)
