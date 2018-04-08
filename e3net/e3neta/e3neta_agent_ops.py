#
#Copyright (c) 2018 Jie Zheng
#
import grpc
from e3net.e3neta.e3neta_config import get_host_agent
from e3net.rpc.grpc_client import get_stub
from e3net.rpc.grpc_service.vswitch_host_client import rpc_client_get_vswitch_host
from e3net.rpc.grpc_service.vswitch_host_client import rpc_client_list_vswitch_hosts
from e3net.rpc.grpc_service.vswitch_host_client import rpc_client_register_vswitch_host
from e3net.rpc.grpc_service.vswitch_host_client import rpc_client_unregister_vswitch_host
from e3net.rpc.grpc_service.vswitch_host_client import rpc_client_update_vswitch_host
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_get_vswitch_interface
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_list_vswitch_interfaces
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_list_vswitch_interfaces_for_hosts
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_list_vswitch_interfaces_for_lanzone
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_register_vswitch_interface
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_unregister_vswitch_interface
from e3net.rpc.grpc_service.vswitch_interface_client import rpc_client_update_vswitch_interface
from e3net.rpc.grpc_service.vswitch_lanzone_client import rpc_client_get_vswitch_lanzone
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT
from e3net.common.e3exception import err_invt
from e3net.common.e3log import get_e3loger
from e3net.common.e3def import E3VSWITCH_HOST_STATUS_ACTIVE
from e3net.common.e3def import E3VSWITCH_INTERFACE_STATUS_ACTIVE
e3loger = get_e3loger('e3neta')

invt_err = dict()
for err in err_invt:
    invt_err[err_invt[err]] = err

def e3neta_intercept_exception(agent, e):
    import random
    assert (type(e) == grpc._channel._Rendezvous)
    code = e.code()
    detail = e.details()
    user_exception_string = 'Exception calling application'
    #if service not available or torn down,choose another controller
    e.user_error = False
    e.user_exception = None
    if code in [grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                grpc.StatusCode.UNIMPLEMENTED]:
        found = False
        agent.guard.write_lock()
        agent.ban_controller_list.append(agent.current_controller)
        e3loger.warning('decommission controller: %s' % (agent.current_controller))
        start_index = random.randint(0,len(agent.controller_list) - 1)
        for i in range(len(agent.controller_list)):
            index = (i + start_index) % len(agent.controller_list)
            if agent.controller_list[index] in agent.ban_controller_list:
                continue
            agent.current_controller = agent.controller_list[index]
            found = True
            break
        if not found:
            agent.ban_controller_list.clear()
            agent.current_controller = agent.controller_list[start_index]
        e3loger.warning('choose new controller: %s' % (agent.current_controller))
        agent.guard.write_unlock()
    elif code is grpc.StatusCode.UNKNOWN and \
        detail.startswith(user_exception_string):
        lst = detail.split(':')
        if len(lst) >= 2:
            user_exception = lst[1].strip(' ').strip('\'')
            if user_exception in invt_err:
                e.user_error = True
                e.user_exception = invt_err[user_exception]

def e3neta_agent_connect():
    agent = get_host_agent()
    if agent.connected == True:
        return
    vswitch_host_stub = get_stub(agent.current_controller, agent.controller_port, 'vswitch_host')
    vswitch_iface_stub = get_stub(agent.current_controller, agent.controller_port, 'vswitch_interface')
    vswitch_lanzone_stub = get_stub(agent.current_controller, agent.controller_port, 'vswitch_lanzone')
    vswitch_host = None
    vswitch_ifaces = None
    try:
        vswitch_host = rpc_client_get_vswitch_host(vswitch_host_stub, agent.hostname, False)
    except grpc.RpcError as e:
        e3neta_intercept_exception(agent, e)
        if e.user_error and e.user_exception == E3_EXCEPTION_NOT_FOUND:
            vswitch_host = rpc_client_register_vswitch_host(vswitch_host_stub,
                                                            name = agent.hostname,
                                                            host_ip = agent.local_ip,
                                                            description = agent.description,
                                                            host_status = E3VSWITCH_HOST_STATUS_ACTIVE)
    assert (vswitch_host)
    if agent.hostname != vswitch_host.name or \
        agent.local_ip != vswitch_host.host_ip or \
        agent.description != vswitch_host.description or \
        vswitch_host.host_status != E3VSWITCH_HOST_STATUS_ACTIVE:
        vswitch_host = rpc_client_update_vswitch_host(vswitch_host_stub,
                                                        uuid = vswitch_host.id,
                                                        name = agent.hostname,
                                                        host_ip = agent.local_ip,
                                                        description = agent.description,
                                                        host_status = E3VSWITCH_HOST_STATUS_ACTIVE)
    agent.vswitch_host = vswitch_host
    vswitch_ifaces = rpc_client_list_vswitch_interfaces_for_hosts(vswitch_iface_stub, [vswitch_host.id])
    local_devs = {agent.interfaces[_iface].dev_address: agent.interfaces[_iface] for _iface in agent.interfaces}
    registered_devs = list()
    for viface in vswitch_ifaces:
        assert (viface.host_id == vswitch_host.id)
        if viface.dev_address in local_devs:
            local_dev = local_devs[viface.dev_address]
            registered_devs.append(viface.dev_address)
            lanzone = rpc_client_get_vswitch_lanzone(vswitch_lanzone_stub,
                                                        local_devs[viface.dev_address].lanzone,
                                                        False)
            iface = viface
            if viface.interface_type != local_dev.iface_type or \
                viface.lanzone_id != lanzone.id or \
                viface.interface_status != E3VSWITCH_INTERFACE_STATUS_ACTIVE:
                iface = rpc_client_update_vswitch_interface(vswitch_iface_stub,
                                                            viface.id,
                                                            interface_status = E3VSWITCH_INTERFACE_STATUS_ACTIVE,
                                                            interface_type = local_dev.iface_type,
                                                            lanzone_id = lanzone.id)
            for _iface in agent.interfaces:
                if agent.interfaces[_iface].dev_address == viface.dev_address:
                    agent.interfaces[_iface].vswitch_interface = iface
        else:
            #delete the viface if it's not in local-dev list
            rpc_client_unregister_vswitch_interface(vswitch_iface_stub,viface.id)
    #register those who are not registered yet
    for dev in local_devs:
        if dev in registered_devs:
            continue
        lanzone = rpc_client_get_vswitch_lanzone(vswitch_lanzone_stub,
                                                    local_devs[dev].lanzone,
                                                    False)
        iface = rpc_client_register_vswitch_interface(vswitch_iface_stub,
                                                host_id = vswitch_host.id,
                                                dev_address = dev,
                                                lanzone_id = lanzone.id,
                                                interface_status = E3VSWITCH_INTERFACE_STATUS_ACTIVE,
                                                interface_type = local_devs[dev].iface_type)
        for _iface in agent.interfaces:
            if agent.interfaces[_iface].dev_address == dev:
                agent.interfaces[_iface].vswitch_interface = iface
