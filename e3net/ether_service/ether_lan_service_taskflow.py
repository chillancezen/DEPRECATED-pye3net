#
#Copyright (c) 2018 Jie Zheng
#
from taskflow import task
from taskflow.patterns import linear_flow
from e3net.inventory.invt_base import get_inventory_base
from e3net.common.e3exception import e3_exception
from e3net.common.e3exception import E3_EXCEPTION_IN_USE
from e3net.common.e3exception import E3_EXCEPTION_NOT_FOUND
from e3net.common.e3exception import E3_EXCEPTION_INVALID_ARGUMENT
from e3net.common.e3exception import E3_EXCEPTION_OUT_OF_RESOURCE
from e3net.common.e3exception import E3_EXCEPTION_NOT_SUPPORT
from e3net.common.e3exception import E3_EXCEPTION_BE_PRESENT
from e3net.inventory.invt_vswitch_ether_service import invt_register_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_unregister_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_get_vswitch_ether_service
from e3net.inventory.invt_dist_taskflow import register_taskflow_category
from e3net.ether_service.ether_line_service_taskflow import e_line_tf_create_ether_service as e_lan_tf_create_ether_service
from e3net.ether_service.ether_line_service import _prefetch_create_config
from e3net.ether_service.ether_lan_service import _create_ether_lan_topology
from e3net.ether_service.ether_lan_service import _validate_ether_lan_topology
from e3net.ether_service.ether_lan_service import _create_ether_lan_topology_edge



ETHER_LAN_TASKFLOW_CREATION='ether_lan_creation'

class e_lan_tf_create_topology(task.Task):
    def execute(self, config, iResult):
        _prefetch_create_config(config, iResult)
        _create_ether_lan_topology(config, iResult)

class e_lan_tf_commit_topology(task.Task):
    def execute(self, config, iResult):
        _validate_ether_lan_topology(config, iResult)
        _create_ether_lan_topology_edge(config, iResult)
    def revert(self, config, iResult, result, flow_failures):
        pass

def generate_ether_lan_creation_flow():
    lf = linear_flow.Flow(ETHER_LAN_TASKFLOW_CREATION)
    lf.add(e_lan_tf_create_ether_service())
    lf.add(e_lan_tf_create_topology())
    lf.add(e_lan_tf_commit_topology())
    return lf

register_taskflow_category(ETHER_LAN_TASKFLOW_CREATION, generate_ether_lan_creation_flow)
