#
#Copyright (c) 2018 Jie Zheng
#
from e3net.db.db_base import init_database
from e3net.common.e3config import get_config
from e3net.db.db_base import create_database_entries
from e3net.common.e3log import get_e3loger
from e3net.e3neta.db import invt_e3neta_database
DB_NAME = 'e3net_agent'

e3loger = get_e3loger('e3neta')

def e3neta_db_init():
    connection = get_config(None, 'database', 'connection')
    e3loger.info('local database connection: %s' % (connection))
    init_database(DB_NAME, connection, False)
    create_database_entries(DB_NAME)
     
