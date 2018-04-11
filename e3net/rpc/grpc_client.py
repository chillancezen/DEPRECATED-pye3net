#
#Copyright (c) 2018 Jie Zheng
#
from e3net.common.e3config import get_config
from e3net.common.e3log import get_e3loger
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUCCESSFUL
from e3net.common.e3exception import E3_EXCEPTION_NOT_READY
from e3net.common.e3rwlock import e3rwlock
import grpc


channels = dict()
channel_lock = e3rwlock()

stub_inventory = dict()
def publish_stub_inventory(rpc_service_name, stub_entry):
    print('adding rpc stub: %s' % (stub_entry))
    stub_inventory[rpc_service_name] = stub_entry


class grpc_channel():
    def __init__(self):
        self.channel = None
        self.stubs = dict()
        self.guard = e3rwlock()

def _get_channel(address, port):
    try:
        channel_lock.read_lock()
        key = '%s:%s' % (address, port)
        cha = channels.get(key, None)
        return cha
    finally:
        channel_lock.read_unlock()
def get_channel(address, port, auto_create = True):
    key = '%s:%s' % (address, port)
    write_locked = False
    try:
        channel = _get_channel(address, port)
        if not channel and auto_create:
            channel_lock.write_lock()
            write_locked = True
            #create the channel if not present
            secure_channel = get_config(None, 'grpc', 'secure_channel')
            channel = None
            if secure_channel == 'True':
                public_crt_path = get_config(None, 'grpc', 'public_crt_path')
                public_crt = None
                with open(public_crt_path) as f:
                    public_crt = f.read().encode()
                credentials = grpc.ssl_channel_credentials(root_certificates = public_crt)
                channel = grpc.secure_channel(key, credentials)
            else:
                channel = grpc.insecure_channel(key)
            gchannel = grpc_channel()
            gchannel.channel = channel
            channels[key] = gchannel 
            channel_lock.write_unlock()
            write_locked = False
            channel = _get_channel(address, port)
        if not channel:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return channel
    finally:
        if write_locked:
            channel_lock.write_unlock()
def _get_stub(self, service_name):
    try:
        self.guard.read_lock()
        stub = self.stubs.get(service_name)
        return stub
    finally:
        self.guard.read_unlock()
def get_stub(address, port, service_name, auto_create = True):
    channel = get_channel(address, port, auto_create)
    assert (channel)
    write_locked = False
    try:
        stub = _get_stub(channel, service_name)
        if not stub and auto_create:
            channel.guard.write_lock()
            write_locked = True
            assert (service_name in stub_inventory)
            stub = stub_inventory[service_name](channel.channel)
            channel.stubs[service_name] = stub
            channel.guard.write_unlock()
            write_locked = False
            stub = _get_stub(channel, service_name)
        if not stub:
            raise e3_exception(E3_EXCEPTION_NOT_FOUND)
        return stub
    finally:
        if write_locked:
            channel.guard.write_unlock()
if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    print(get_stub('130.140.150.2',9418,'vswitch_host'))
    print(get_channel('130.140.150.2',9418))
