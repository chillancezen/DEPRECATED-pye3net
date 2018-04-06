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
    #optional options are loaded below
    try:
        host_agent.description = get_config(None, 'vswitch_host', 'description')
    except:
        host_agent.description = ''

    print(host_agent)
