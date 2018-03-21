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
from e3net.ether_service.ether_service_common import EtherServiceCreateConfig
from e3net.inventory.invt_vswitch_ether_service import invt_register_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_unregister_vswitch_ether_service
from e3net.inventory.invt_vswitch_ether_service import invt_get_vswitch_ether_service
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_TYPE_LINE
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_TYPE_LAN
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_LINK_SHARED
from e3net.db.db_vswitch_ether_service import E3NET_ETHER_SERVICE_LINK_EXCLUSIVE
from e3net.ether_service.ether_line_service import _prefetch_create_config
from e3net.ether_service.ether_line_service import _create_ether_line_topology
from e3net.ether_service.ether_line_service import _validate_ether_line_topology
from e3net.ether_service.ether_line_service import _create_ether_line_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_register_vswitch_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_unregister_vswitch_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_get_vswitch_topology_edge
from e3net.inventory.invt_vswitch_topology_edge import invt_list_vswitch_topology_edges
from e3net.inventory.invt_dist_taskflow import register_taskflow_category

class e_line_tf_create_ether_service(task.Task):
    def execute(self, config, iResult):
        assert (config['service_type'] in [E3NET_ETHER_SERVICE_TYPE_LINE, E3NET_ETHER_SERVICE_TYPE_LAN])
        assert (config['link_type'] in [E3NET_ETHER_SERVICE_LINK_SHARED, E3NET_ETHER_SERVICE_LINK_EXCLUSIVE])
        #create ether_service entry in database&cache
        spec = dict()
        spec['name'] = config['service_name']
        spec['service_type'] = config['service_type']
        spec['link_type'] = config['link_type']
        spec['tenant_id'] = config['tenant_id']
        e_line = invt_register_vswitch_ether_service(spec, user_sync = True)
        iResult['service_id'] = e_line.id
    def revert(self, config, iResult, result, flow_failures):
        #upon failure, delete ether service in database&cache
        service_id = iResult.get('service_id', None)
        if service_id:
            try:
                invt_unregister_vswitch_ether_service(service_id, user_sync = True)
            except:
                pass

class e_line_tf_create_topology(task.Task):
    def execute(self, config, iResult):
        _prefetch_create_config(config, iResult)
        _create_ether_line_topology(config, iResult)

class e_line_tf_commit_topology(task.Task):
    def execute(self, config, iResult):
        _validate_ether_line_topology(config, iResult)
        _create_ether_line_topology_edge(config, iResult)
    def revert(self, config, iResult, result, flow_failures):
        try:
            #find the edges of the service, unregister them
            edges = invt_list_vswitch_topology_edges()
            for edge in edges:
                if edge.service_id == iResult['service_id']:
                    invt_unregister_vswitch_topology_edge(edge.id, user_sync = True)
        except:
            pass
ETHER_LINE_TASKFLOW_CREATION='ether_line_creation'

def generate_ether_line_creation_flow():
    lf = linear_flow.Flow(ETHER_LINE_TASKFLOW_CREATION)
    lf.add(e_line_tf_create_ether_service())
    lf.add(e_line_tf_create_topology())
    lf.add(e_line_tf_commit_topology())
    return lf

register_taskflow_category(ETHER_LINE_TASKFLOW_CREATION, generate_ether_line_creation_flow)

