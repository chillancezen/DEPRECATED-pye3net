#
#Copyright (c) 2018 Jie Zheng
#
import sys
from e3net.rpc import protos_base
sys.path += protos_base.__path__
from e3net.rpc.grpc_server import publish_rpc_service
from e3net.rpc.protos_base import label_distribution_pb2
from e3net.rpc.protos_base import label_distribution_pb2_grpc
from e3net.rpc.protos_base import common_pb2


class label_distribution_service(label_distribution_pb2_grpc.label_distributionServicer):
    def rpc_deposit_labels(self, request_iterator, context):
        pass
    def rpc_withdraw_labels(self, request_iterator, context):
        pass
    def rpc_pull_labels(self, request_iterator, context):
        for _label_request in request_iterator:
            pass

publish_rpc_service(label_distribution_pb2_grpc.add_label_distributionServicer_to_server,
    label_distribution_service)
