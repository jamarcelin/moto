"""WorkSpacesWebBackend class with methods for supported APIs."""

import datetime
import uuid

from moto.core.base_backend import BaseBackend, BackendDict
from moto.core.common_models import BaseModel
from moto.utilities.utils import get_partition

from typing import Dict


class FakePortal(BaseModel):

    def __init__(self, encryption_context, authentication_type, client_token, customer_managed_key, display_name, instance_type, max_sessions, tags, region_name, account_id):
        self.arn = self.arn_formatter(account_id, region_name)

    def arn_formatter(self, _id, account_id, region_name):
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:portal/{_id}"


class FakePortal(BaseModel):

    def __init__(
        self,
        encryption_context,
        authentication_type,
        client_token,
        customer_managed_key,
        display_name,
        instance_type,
        max_sessions,
        tags,
        region_name,
        account_id
    ):
        self.portal_id = str(uuid.uuid4())
        self.arn = self.arn_formatter(self.portal_id, account_id, region_name)
        self.encryption_context = encryption_context
        self.authentication_type = authentication_type
        self.client_token = client_token
        self.customer_managed_key = customer_managed_key
        self.display_name = display_name
        self.instance_type = instance_type
        self.max_sessions = max_sessions
        self.creation_date = datetime.datetime.now()
        self.tags = tags

    def arn_formatter(self, _id, account_id, region_name):
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:portal/{_id}"

    def to_dict(self):
        return {
            "portalArn": self.arn,
            "alias": self.alias,
            "networkSettingsArn": self.network_settings_arn,
            "tags": self.tags,
        }


class FakeNetworkSettings(BaseModel):

    def __init__(
        self,
        security_group_ids,
        subnet_ids,
        tags,
        vpc_id,
        region_name,
        account_id,
    ):
        self.network_settings_id = uuid.uuid4()
        self.arn = self.arn_formatter(
            self.network_settings_id, account_id, region_name)
        self.security_group_ids = security_group_ids
        self.subnet_ids = subnet_ids
        self.tags = tags
        self.vpc_id = vpc_id
        self.arn = self.arn_formatter(
            "network-settings", account_id, region_name)

    def arn_formatter(self, _id, account_id, region_name):
        return f"arn:{get_partition(region_name)}:workspaces-web:{region_name}:{account_id}:network-settings/{_id}"

    def to_dict(self):
        return {
            "networkSettingsArn": self.arn,
            "securityGroupIds": self.security_group_ids,
            "subnetIds": self.subnet_ids,
            "tags": self.tags,
            "vpcId": self.vpc_id,
        }


class FakeBrowserSettings(BaseModel):
    def __init__(
        self,
        region_name,
        account_id,
        client_token,
        tags
    ):
        self.browser_settings_id = uuid.uuid4()
        self.arn = self.arn_formatter(
            self.browser_settings_id, account_id, region_name)
        self.client_token = client_token
        self.tags = tags


class WorkSpacesWebBackend(BaseBackend):
    """Implementation of WorkSpacesWeb APIs."""

    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.network_settings: Dict[str, FakeNetworkSettings] = {}
        # self.browser_settings: Dict[str, FakeBrowserSettings] = {}
        # self.portals: Dict[str, FakePortal] = {}

    def create_network_settings(self, security_group_ids, subnet_ids, tags, vpc_id) -> FakeNetworkSettings:
        network_settings_object = FakeNetworkSettings(
            security_group_ids, subnet_ids, tags, vpc_id, self.region_name, self.account_id)
        self.network_settings[network_settings_object.arn] = network_settings_object
        return network_settings_object

    def list_network_settings(self):
        return self.network_settings.values()

    def get_network_settings(self, network_settings_arn):
        return self.network_settings.get(network_settings_arn)

    def delete_network_settings(self, network_settings_arn):
        return self.network_settings.pop(network_settings_arn)

    def create_portal(self, additional_encryption_context, authentication_type, client_token, customer_managed_key, display_name, instance_type, max_concurrent_sessions, tags):
        # implement here
        return portal_arn, portal_endpoint
    

workspacesweb_backends = BackendDict(WorkSpacesWebBackend, "workspaces-web")
