#
#Copyright (c) 2018 Jie Zheng
#
import grpc
from concurrent import futures
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


rpc_service_invt = list()
def publish_rpc_service(func,service_class):
    rpc_service_invt.append((func, service_class))

e3loger = get_e3loger('vswitch_controller')

def grpc_server_init():
    
    secure_channel = get_config(None, 'grpc', 'secure_channel')
    max_threads = get_config(None, 'grpc', 'max_threads')
    grpc_port = get_config(None, 'grpc', 'grpc_port')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = int(max_threads)))
    #load rpc service
    for rpc in rpc_service_invt:
        service_add_func, service_class = rpc
        print('adding rpc service:%s' % (service_class))
        service_add_func(service_class(), server)
    if secure_channel == 'True':
        private_key_path = get_config(None, 'grpc', 'private_key_path')
        public_crt_path = get_config(None, 'grpc', 'public_crt_path')
        private_key = None
        public_crt = None
        with open(private_key_path) as f:
            private_key = f.read().encode()
        with open(public_crt_path) as f:
            public_crt = f.read().encode()
        server_creds = grpc.ssl_server_credentials(((private_key, public_crt,),))
        server.add_secure_port('0.0.0.0:%s' % (grpc_port), server_creds)
    else:
        server.add_insecure_port('0.0.0.0:%s' % (grpc_port))
    server.start()
    #preserve the exit implementation
    import time
    while True:
        time.sleep(1000)
if __name__ == '__main__':
    from e3net.common.e3config import add_config_file
    from e3net.common.e3config import load_configs
    add_config_file('/etc/e3net/e3vswitch.ini')
    load_configs()
    grpc_server_init()
    import time
    time.sleep(1000)
