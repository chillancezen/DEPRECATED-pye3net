#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_client import publish_stub_inventory
from e3net.rpc.protos_base import label_distribution_pb2
from e3net.rpc.protos_base import label_distribution_pb2_grpc
from e3net.rpc.grpc_client import get_stub

rpc_service = 'label_distribution'


def rpc_client_deposit_labels(stub):
    pass
def rpc_client_withdraw_labels(stub):
    pass
def rpc_client_pull_labels(stub):
    pass

publish_stub_inventory(rpc_service, label_distribution_pb2_grpc.label_distributionStub)
