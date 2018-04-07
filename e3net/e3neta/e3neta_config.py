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
from e3net.common.e3rwlock import e3rwlock
from e3net.common.e3config import get_config
from e3net.common.e3log import get_e3loger
from e3net.common.e3def import E3VSWITCH_HOST_STATUS_UNKNOWN
from e3net.common.e3def import E3VSWITCH_HOST_STATUS_ACTIVE
from e3net.common.e3def import E3VSWITCH_HOST_STATUS_INACTIVE
from e3net.common.e3def import E3VSWITCH_HOST_STATUS_MAINTENANCE
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_UNKNOWN
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_ACTIVE
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_INACTIVE
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_MAINTENANCE
from e3net.common.e3def import E3VSWITCH_INTERFACE_TYPE_SHARED
from e3net.common.e3def import E3VSWITCH_INTERFACE_TYPE_EXCLUSIVE
#import role definition from dataplne library
from pye3datapath.e3iface import E3IFACE_ROLE_PROVIDER_BACKBONE_PORT
from pye3datapath.e3iface import E3IFACE_ROLE_CUSTOMER_BACKBONE_FACING_PORT
from pye3datapath.e3iface import E3IFACE_ROLE_CUSTOMER_USER_FACING_PORT
from pye3datapath.e3iface import E3IFACE_MODEL_GENERIC_SINGLY_QUEUE

port_role_mapping = {
    'csp':E3IFACE_ROLE_CUSTOMER_USER_FACING_PORT,
    'cbp':E3IFACE_ROLE_CUSTOMER_BACKBONE_FACING_PORT,
    'pbp':E3IFACE_ROLE_PROVIDER_BACKBONE_PORT
}

port_model_mapping = {
    'generic.singly_queue':E3IFACE_MODEL_GENERIC_SINGLY_QUEUE
}

e3loger = get_e3loger('e3neta')

DEFAULT_SERVICE_PORT = 9418

class interface_config():
    def __init__(self):
        self.local_name = None
        self.dev_address = None
        self.role = None
        self.hw_model = None
        self.lanzone = None
        self.vswitch_interface = None
    def __str__(self):
        return str(self.__dict__)

class host_config():
    def __init__(self):
        self.hostname = None
        self.local_ip = None
        self.description = None
        self.controller_list = list()
        self.current_controller = None
        self.controller_port = DEFAULT_SERVICE_PORT
        self.interfaces = dict()
        self.guard = e3rwlock()
        self.vswitch_host = None
        #configuration space
        self.connected = False
        self.ban_controller_list = list()
    def __str__(self):
        return str(self.__dict__)
host_agent = host_config()
def get_host_agent():
    return host_agent

def e3neta_config_init():
    global host_agent
    host_agent.hostname = get_config(None, 'vswitch_host', 'hostname')
    host_agent.local_ip = get_config(None, 'vswitch_host', 'host_ip')
    controller_string = get_config(None, 'controller', 'service_address_list')
    controller_list = controller_string.split(',')
    for _controller in controller_list:
        controller = _controller.strip()
        if controller == '':
            continue
        host_agent.controller_list.append(controller)
    host_agent.controller_port = get_config(None, 'controller', 'service_port')
    assert(len(host_agent.controller_list))
    #randomly assign controller as current controller
    import random
    index = int(random.random() * 10) % len(host_agent.controller_list)
    host_agent.current_controller = host_agent.controller_list[index]
    #load interfaces options
    ifaces_string = get_config(None, 'vswitch_interface', 'interfaces')
    ifaces = ifaces_string.split(',')
    for _iface in ifaces:
        iface = _iface.strip()
        if iface == '':
            continue
        host_agent.interfaces[iface] = interface_config()
        host_agent.interfaces[iface].local_name = iface
    for _iface in host_agent.interfaces:
        host_agent.interfaces[_iface].dev_address = get_config(None,
                                                         'vswitch_interface',
                                                         '%s.dev_address' % (_iface))
        role = get_config(None, 'vswitch_interface', '%s.role' % (_iface))
        role = role.strip()
        host_agent.interfaces[_iface].role = port_role_mapping[role]
        model = get_config(None, 'vswitch_interface', '%s.hw_model' % (_iface))
        model = model.strip()
        host_agent.interfaces[_iface].hw_model = port_model_mapping[model]
        host_agent.lanzone = get_config(None, 'vswitch_interface', '%s.lanzone' % (_iface))
    #optional options are loaded below
    try:
        host_agent.description = get_config(None, 'vswitch_host', 'description')
    except:
        host_agent.description = ''
    e3loger.info('host config:\n%s' % (host_agent))
    for _iface in host_agent.interfaces:
        e3loger.info('interface config:%s' %(host_agent.interfaces[_iface]))
