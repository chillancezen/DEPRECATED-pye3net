#
#Copyright (c) 2018 Jie Zheng
#
from e3net.common.e3config import add_config_file
from e3net.common.e3config import load_configs
from e3net.db.db_base import init_database
from e3net.db.db_base import load_database
from e3net.inventory.invt_base import e3inventory_base_init
from e3net.inventory.invt_dist_taskflow import taskflow_init
from e3net.rpc.grpc_server import grpc_server_init
from e3net.rpc.grpc_service import invt_server_service
from e3net.inventory.invt_event_notifier import event_init

def main():
    #initialize config as the 1st step
    add_config_file('/etc/e3net/e3vswitch-standalone.ini')
    load_configs()
    #initilize database options
    DB_NAME='E3NET_VSWITCH'
    init_database(DB_NAME,'mysql+pymysql://e3net:e3credientials@localhost/E3NET_VSWITCH',False)
    load_database()
    #initialize inventory
    e3inventory_base_init()
    #initialize taskflow
    taskflow_init()
    #initialize event notification
    event_init()
    #initialize grpc
    grpc_server_init()
if __name__ == '__main__':
    main()

