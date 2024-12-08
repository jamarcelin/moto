"""KafkaBackend class with methods for supported APIs."""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.utils import get_partition

from ..utilities.tagging_service import TaggingService


class FakeKafkaCluster(BaseModel):
    def __init__(
        self,
        cluster_name: str,
        account_id: str,
        region_name: str,
        cluster_type: str,
        tags: dict = None,
        broker_node_group_info: dict = None,
        kafka_version: str = None,
        number_of_broker_nodes: int = None,
        configuration_info=None,
        serverless_config: dict = None,
        encryption_info: dict = None,
        enhanced_monitoring: str = "DEFAULT",
        open_monitoring: dict = None,
        logging_info: dict = None,
        storage_mode: str = "LOCAL",
        current_version: str = "1.0",
        client_authentication: dict = None,
        state: str = "CREATING",
        active_operation_arn: str = None,
        zookeeper_connect_string: str = None,
        zookeeper_connect_string_tls: str = None,
    ):
        # General attributes
        self.cluster_id = str(uuid.uuid4())
        self.cluster_name = cluster_name
        self.account_id = account_id
        self.region_name = region_name
        self.cluster_type = cluster_type
        self.tags = tags or {}
        self.state = state
        self.creation_time = datetime.now().isoformat()
        self.current_version = current_version
        self.active_operation_arn = active_operation_arn
        self.arn = self._generate_arn()

        # Attributes specific to PROVISIONED clusters
        self.broker_node_group_info = broker_node_group_info
        self.kafka_version = kafka_version
        self.number_of_broker_nodes = number_of_broker_nodes
        self.configuration_info = configuration_info
        self.encryption_info = encryption_info
        self.enhanced_monitoring = enhanced_monitoring
        self.open_monitoring = open_monitoring
        self.logging_info = logging_info
        self.storage_mode = storage_mode
        self.client_authentication = client_authentication
        self.zookeeper_connect_string = zookeeper_connect_string
        self.zookeeper_connect_string_tls = zookeeper_connect_string_tls

        # Attributes specific to SERVERLESS clusters
        self.serverless_config = serverless_config

    def _generate_arn(self) -> str:
        resource_type = (
            "cluster" if self.cluster_type == "PROVISIONED" else "serverless-cluster"
        )
        partition = get_partition(self.region_name)
        return f"arn:{partition}:kafka:{self.region_name}:{self.account_id}:{resource_type}/{self.cluster_id}"

    def to_dict(self) -> dict:
        cluster_info = {
            "ClusterName": self.cluster_name,
            "ClusterArn": self.arn,
            "ClusterType": self.cluster_type,
            "State": self.state,
            "CreationTime": self.creation_time,
            "CurrentVersion": self.current_version,
            "Tags": self.tags,
            "ActiveOperationArn": self.active_operation_arn,
        }

        if self.cluster_type == "PROVISIONED":
            cluster_info["Provisioned"] = {
                "BrokerNodeGroupInfo": self.broker_node_group_info,
                "KafkaVersion": self.kafka_version,
                "NumberOfBrokerNodes": self.number_of_broker_nodes,
                "EncryptionInfo": self.encryption_info,
                "EnhancedMonitoring": self.enhanced_monitoring,
                "OpenMonitoring": self.open_monitoring,
                "LoggingInfo": self.logging_info,
                "StorageMode": self.storage_mode,
                "ClientAuthentication": self.client_authentication,
                "ZookeeperConnectString": self.zookeeper_connect_string,
                "ZookeeperConnectStringTls": self.zookeeper_connect_string_tls,
            }

        elif self.cluster_type == "SERVERLESS":
            cluster_info["Serverless"] = {
                "VpcConfigs": self.serverless_config.get("VpcConfigs", []),
                "ClientAuthentication": self.serverless_config.get(
                    "ClientAuthentication", {}
                ),
            }

        return cluster_info


class KafkaBackend(BaseBackend):
    """Implementation of Kafka APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.clusters: Dict[str, FakeKafkaCluster] = {}
        self.tagger = TaggingService()

    def create_cluster_v2(self, cluster_name, tags, provisioned, serverless):
        if provisioned:
            cluster_type = "PROVISIONED"
            broker_node_group_info = provisioned.get("BrokerNodeGroupInfo")
            kafka_version = provisioned.get("KafkaVersion", "default-kafka-version")
            number_of_broker_nodes = provisioned.get("NumberOfBrokerNodes", 1)
            storage_mode = provisioned.get("StorageMode", "LOCAL")
            serverless_config = None
        elif serverless:
            cluster_type = "SERVERLESS"
            broker_node_group_info = None
            kafka_version = None
            number_of_broker_nodes = None
            storage_mode = None
            serverless_config = serverless

        new_cluster = FakeKafkaCluster(
            cluster_name=cluster_name,
            account_id=self.account_id,
            region_name=self.region_name,
            cluster_type=cluster_type,
            broker_node_group_info=broker_node_group_info,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            serverless_config=serverless_config,
            tags=tags,
            state="CREATING",
            storage_mode=storage_mode,
            current_version="1.0",
        )

        self.clusters[new_cluster.arn] = new_cluster

        if tags:
            tags_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            self.tagger.tag_resource(new_cluster.arn, tags_list)

        return (
            new_cluster.arn,
            new_cluster.cluster_name,
            new_cluster.state,
            new_cluster.cluster_type,
        )

    def describe_cluster_v2(self, cluster_arn):
        cluster = self.clusters.get(cluster_arn)

        cluster_info = {
            "ClusterInfo": {
                "ActiveOperationArn": cluster.active_operation_arn
                or "arn:aws:kafka:region:account-id:operation/active-operation",
                "ClusterArn": cluster.arn,
                "ClusterName": cluster.cluster_name,
                "ClusterType": cluster.cluster_type,
                "CreationTime": cluster.creation_time,
                "CurrentVersion": cluster.current_version,
                "State": cluster.state,
                "StateInfo": {
                    "Code": "string",
                    "Message": "Cluster state details.",
                },
                "Tags": self.list_tags_for_resource(cluster.arn),
            }
        }

        if cluster.cluster_type == "PROVISIONED":
            cluster_info["ClusterInfo"].update(
                {
                    "BrokerNodeGroupInfo": cluster.broker_node_group_info or {},
                    "ClientAuthentication": cluster.client_authentication or {},
                    "CurrentBrokerSoftwareInfo": {
                        "ConfigurationArn": (cluster.configuration_info or {}).get(
                            "Arn", "string"
                        ),
                        "ConfigurationRevision": (cluster.configuration_info or {}).get(
                            "Revision", 1
                        ),
                        "KafkaVersion": cluster.kafka_version,
                    },
                    "EncryptionInfo": cluster.encryption_info or {},
                    "EnhancedMonitoring": cluster.enhanced_monitoring,
                    "OpenMonitoring": cluster.open_monitoring or {},
                    "LoggingInfo": cluster.logging_info or {},
                    "NumberOfBrokerNodes": cluster.number_of_broker_nodes or 0,
                    "ZookeeperConnectString": cluster.zookeeper_connect_string
                    or "zookeeper.example.com:2181",
                    "ZookeeperConnectStringTls": cluster.zookeeper_connect_string_tls
                    or "zookeeper.example.com:2181",
                    "StorageMode": cluster.storage_mode,
                    "CustomerActionStatus": "NONE",
                }
            )

        elif cluster.cluster_type == "SERVERLESS":
            cluster_info["ClusterInfo"].update(
                {
                    "Serverless": {
                        "VpcConfigs": cluster.serverless_config.get("VpcConfigs", []),
                        "ClientAuthentication": cluster.serverless_config.get(
                            "ClientAuthentication", {}
                        ),
                    }
                }
            )

        return cluster_info

    def list_clusters_v2(
        self, cluster_name_filter, cluster_type_filter, max_results, next_token
    ):
        cluster_info_list = [
            {
                "ClusterArn": cluster.arn,
                "ClusterName": cluster.cluster_name,
                "ClusterType": cluster.cluster_type,
                "State": cluster.state,
                "CreationTime": cluster.creation_time,
            }
            for cluster in self.clusters.values()
        ]

        return cluster_info_list, None

    def create_cluster(
        self,
        broker_node_group_info,
        client_authentication,
        cluster_name,
        configuration_info=None,
        encryption_info=None,
        enhanced_monitoring="DEFAULT",
        open_monitoring=None,
        kafka_version="2.8.1",
        logging_info=None,
        number_of_broker_nodes=1,
        tags=None,
        storage_mode="LOCAL",
    ):
        new_cluster = FakeKafkaCluster(
            cluster_name=cluster_name,
            account_id=self.account_id,
            region_name=self.region_name,
            cluster_type="PROVISIONED",
            broker_node_group_info=broker_node_group_info,
            client_authentication=client_authentication,
            kafka_version=kafka_version,
            number_of_broker_nodes=number_of_broker_nodes,
            configuration_info=configuration_info,
            encryption_info=encryption_info,
            enhanced_monitoring=enhanced_monitoring,
            open_monitoring=open_monitoring,
            logging_info=logging_info,
            storage_mode=storage_mode,
        )

        self.clusters[new_cluster.arn] = new_cluster

        if tags:
            tags_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            self.tagger.tag_resource(new_cluster.arn, tags_list)

        return new_cluster.arn, new_cluster.cluster_name, new_cluster.state

    def describe_cluster(self, cluster_arn):
        cluster = self.clusters.get(cluster_arn)

        return {
            "ClusterInfo": {
                "ActiveOperationArn": cluster.active_operation_arn
                or "arn:aws:kafka:region:account-id:operation/active-operation",
                "BrokerNodeGroupInfo": cluster.broker_node_group_info or {},
                "ClientAuthentication": cluster.client_authentication or {},
                "ClusterArn": cluster.arn,
                "ClusterName": cluster.cluster_name,
                "CreationTime": cluster.creation_time,
                "CurrentBrokerSoftwareInfo": {
                    "ConfigurationArn": (cluster.configuration_info or {}).get(
                        "Arn", "string"
                    ),
                    "ConfigurationRevision": (cluster.configuration_info or {}).get(
                        "Revision", 1
                    ),
                    "KafkaVersion": cluster.kafka_version,
                },
                "CurrentVersion": cluster.current_version,
                "EncryptionInfo": cluster.encryption_info or {},
                "EnhancedMonitoring": cluster.enhanced_monitoring,
                "OpenMonitoring": cluster.open_monitoring or {},
                "LoggingInfo": cluster.logging_info or {},
                "NumberOfBrokerNodes": cluster.number_of_broker_nodes or 0,
                "State": cluster.state,
                "StateInfo": {
                    "Code": "string",
                    "Message": "Cluster state details.",
                },
                "Tags": self.list_tags_for_resource(cluster.arn),
                "ZookeeperConnectString": cluster.zookeeper_connect_string
                or "zookeeper.example.com:2181",
                "ZookeeperConnectStringTls": cluster.zookeeper_connect_string_tls
                or "zookeeper.example.com:2181",
                "StorageMode": cluster.storage_mode,
                "CustomerActionStatus": "NONE",
            }
        }

    def list_clusters(
        self, cluster_name_filter, max_results, next_token
    ) -> List[Dict[str, Any]]:
        cluster_info_list = [
            {
                "ClusterArn": cluster.arn,
                "ClusterName": cluster.cluster_name,
                "State": cluster.state,
                "CreationTime": cluster.creation_time,
                "ClusterType": cluster.cluster_type,
            }
            for cluster_arn, cluster in self.clusters.items()
        ]

        return cluster_info_list, None

    def delete_cluster(self, cluster_arn, current_version):
        cluster = self.clusters.pop(cluster_arn)
        return cluster_arn, cluster.state

    def list_tags_for_resource(self, resource_arn) -> List[Dict[str, str]]:
        tags = self.tagger.get_tag_dict_for_resource(resource_arn)
        Tags = []
        for key, value in tags.items():
            Tags.append({"Key": key, "Value": value})
        return Tags

    def tag_resource(self, resource_arn, tags):
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn, tag_keys):
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)


kafka_backends = BackendDict(KafkaBackend, "kafka")