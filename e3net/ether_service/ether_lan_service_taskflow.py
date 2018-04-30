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
from e3net.ether_service.ether_lan_service import _prefetch_ether_lan_update_config
from e3net.ether_service.ether_lan_service import _add_lanzones_to_ether_lan
from e3net.ether_service.ether_lan_service import _synchronize_ether_topology_update
from e3net.ether_service.ether_lan_service import _remove_lanzones_from_ether_lan
from e3net.ether_service.ether_lan_service import _push_ether_lan_topology_on_creation
from e3net.common.e3def import ETHER_LAN_TASKFLOW_CREATION
from e3net.common.e3def import ETHER_LAN_TASKFLOW_UPDATE
from e3net.common.e3def import ETHER_LAN_TASKFLOW_DELETION

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
class e_lan_tf_push_topology(task.Task):
    def execute(self, config, iResult):
        _push_ether_lan_topology_on_creation(config, iResult)

def generate_ether_lan_creation_flow():
    lf = linear_flow.Flow(ETHER_LAN_TASKFLOW_CREATION)
    lf.add(e_lan_tf_create_ether_service())
    lf.add(e_lan_tf_create_topology())
    lf.add(e_lan_tf_commit_topology())
    lf.add(e_lan_tf_push_topology())
    return lf

register_taskflow_category(ETHER_LAN_TASKFLOW_CREATION, generate_ether_lan_creation_flow)

class e_lan_tf_add_topology(task.Task):
    def execute(self, config, iResult):
        _prefetch_ether_lan_update_config(config, iResult)
        _add_lanzones_to_ether_lan(config, iResult)

class e_lan_tf_commit_topology_addition(task.Task):
    def execute(self, config, iResult):
        _validate_ether_lan_topology(config, iResult)
        _synchronize_ether_topology_update(config, iResult)

def  generate_ether_lan_addition_flow():
    lf = linear_flow.Flow(ETHER_LAN_TASKFLOW_UPDATE)
    lf.add(e_lan_tf_add_topology())
    lf.add(e_lan_tf_commit_topology_addition())
    return lf

register_taskflow_category(ETHER_LAN_TASKFLOW_UPDATE, generate_ether_lan_addition_flow)

class e_lan_tf_remove_topology(task.Task):
    def execute(self, config, iResult):
        _prefetch_ether_lan_update_config(config, iResult)
        _remove_lanzones_from_ether_lan(config, iResult)

class e_lan_tf_commit_topology_removal(task.Task):
    def execute(self, config, iResult):
        _validate_ether_lan_topology(config, iResult)
        _synchronize_ether_topology_update(config, iResult)

def generate_ether_lan_removal_flow():
    lf = linear_flow.Flow(ETHER_LAN_TASKFLOW_DELETION)
    lf.add(e_lan_tf_remove_topology())
    lf.add(e_lan_tf_commit_topology_removal())
    return lf

register_taskflow_category(ETHER_LAN_TASKFLOW_DELETION, generate_ether_lan_removal_flow)
