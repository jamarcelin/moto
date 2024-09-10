"""Handles incoming workspacesweb requests, invokes methods, returns responses."""
import json

from moto.core.responses import BaseResponse
from .models import WorkSpacesWebBackend, workspacesweb_backends


class WorkSpacesWebResponse(BaseResponse):
    """Handler for WorkSpacesWeb requests and responses."""

    def __init__(self):
        super().__init__(service_name="workspaces-web")
        print("TEMP HERE")

    @property
    def workspacesweb_backend(self):
        """Return backend instance specific for this region."""
        # TODO
        # workspacesweb_backends is not yet typed
        # Please modify moto/backends.py to add the appropriate type annotations for this service
        return workspacesweb_backends[self.current_account][self.region]

    def create_network_settings(self) -> str:
        params = json.loads(self.body)
        security_group_ids = params.get("securityGroupIds")
        subnet_ids = params.get("subnetIds")
        tags = params.get("tags")
        vpc_id = params.get("vpcId")
        network_settings = WorkSpacesWebBackend.create_network_settings(
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            tags=tags,
            vpc_id=vpc_id,
        )
        return json.dumps(network_settings)
    
    def create_portal(self):
        params = self._get_params()
        additional_encryption_context = params.get("additionalEncryptionContext")
        authentication_type = params.get("authenticationType")
        client_token = params.get("clientToken")
        customer_managed_key = params.get("customerManagedKey")
        display_name = params.get("displayName")
        instance_type = params.get("instanceType")
        max_concurrent_sessions = params.get("maxConcurrentSessions")
        tags = params.get("tags")
        portal_arn, portal_endpoint = self.workspacesweb_backend.create_portal(
            additional_encryption_context=additional_encryption_context,
            authentication_type=authentication_type,
            client_token=client_token,
            customer_managed_key=customer_managed_key,
            display_name=display_name,
            instance_type=instance_type,
            max_concurrent_sessions=max_concurrent_sessions,
            tags=tags,
        )
        # TODO: adjust response
        return json.dumps(dict(portalArn=portal_arn, portalEndpoint=portal_endpoint))
