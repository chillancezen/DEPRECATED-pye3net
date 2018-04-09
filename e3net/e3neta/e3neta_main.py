#
#Copyright (c) 2018 Jie Zheng
#
from e3net.db.db_base import init_database
from e3net.db.db_base import load_database
from e3net.common.e3config import add_config_file
from e3net.common.e3config import load_configs
from e3net.e3neta.e3neta_config import e3neta_config_init

#from e3net.rpc.grpc_service import invt_e3neta_client_service

def main():
    add_config_file('/etc/e3net/e3neta.ini')
    load_configs()
    e3neta_config_init()


if __name__ == '__main__':
    main()
    from e3net.e3neta.e3neta_agent_ops import e3neta_agent_connect
    e3neta_agent_connect()
