#
#Copyright (c) 2017 Jie Zheng
#
import configparser
cfg_files=list()
cfg=configparser.ConfigParser()

def add_config_file(f):
    global cfg_files
    cfg_files.append(f)

def load_configs():
    global cfg
    cfg=configparser.ConfigParser()
    cfg.read(cfg_files)
def get_config(default_conf,section,key):
    if section in cfg and\
         key in cfg[section]:
        return cfg[section][key]
    if default_conf is not None and \
         section in default_conf and \
         key in default_conf[section]:
        return default_conf[section][key]
    raise Exception('value not found')

if __name__=='__main__':
    add_config_file('/etc/e3net/e3datapath.ini')
    load_configs()
    default={'test':{'pbp_pci_addr1':123}}
    print(get_config(default,'test','pbp_pci_addr1'))
