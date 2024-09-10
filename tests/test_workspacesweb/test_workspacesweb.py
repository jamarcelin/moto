"""Unit tests for workspacesweb-supported APIs."""
import boto3
import pytest

from moto import mock_aws

FAKE_SECURITY_GROUP_IDS = ['sg-0123456789abcdef0']
FAKE_SUBNET_IDS = ['subnet-0123456789abcdef0', 'subnet-abcdef0123456789']
FAKE_TAGS = [
    {
        'Key': 'TestKey',
        'Value': 'TestValue'
    },
]
FAKE_VPC_ID = 'vpc-0123456789abcdef0'
FAKE_KMS_KEY_ID = 'abcd1234-5678-90ab-cdef-FAKEKEY'


@mock_aws
def test_create_network_settings():
    client = boto3.client('workspaces-web', region_name='us-west-2')
    response = client.create_network_settings(
        securityGroupIds=FAKE_SECURITY_GROUP_IDS,
        subnetIds=FAKE_SUBNET_IDS,
        tags=FAKE_TAGS,
        vpcId=FAKE_VPC_ID
    )
    assert response['networkSettingsArn'] == "TEMP ARN"


@mock_aws
def test_list_network_settings():
    client = boto3.client('workspaces-web', region_name='us-west-2')
    createResponse = client.create_network_settings(
        securityGroupIds=FAKE_SECURITY_GROUP_IDS,
        subnetIds=FAKE_SUBNET_IDS,
        tags=FAKE_TAGS,
        vpcId=FAKE_VPC_ID
    )
    response = client.list_network_settings()
    assert response['networkSettingsArns'] == [
        createResponse['networkSettingsArn']]


@mock_aws
def test_get_network_settings():
    client = boto3.client('workspaces-web', region_name='us-west-2')
    arn = client.create_network_settings(
        securityGroupIds=FAKE_SECURITY_GROUP_IDS,
        subnetIds=FAKE_SUBNET_IDS,
        tags=FAKE_TAGS,
        vpcId=FAKE_VPC_ID
    )['networkSettingsArn']
    response = client.get_network_settings(networkSettingsArn=arn)
    assert response['networkSettingsArn'] == arn
    assert response['securityGroupIds'] == FAKE_SECURITY_GROUP_IDS
    assert response['subnetIds'] == FAKE_SUBNET_IDS


@mock_aws
def test_delete_network_settings():
    client = boto3.client('workspaces-web', region_name='us-west-2')
    arn = client.create_network_settings(
        securityGroupIds=FAKE_SECURITY_GROUP_IDS,
        subnetIds=FAKE_SUBNET_IDS,
        tags=FAKE_TAGS,
        vpcId=FAKE_VPC_ID
    )['networkSettingsArn']
    client.delete_network_settings(networkSettingsArn=arn)
    assert client.list_network_settings() == {}


@mock_aws
def test_create_browser_settings():
    client = boto3.client('workspaces-web', region_name='us-west-2')
    response = client.create_browser_settings(
        additionalEncryptionContext={'TestKey': 'TestValue'},
        browserPolicy='ALLOWLIST',
        customerManagedKey=FAKE_KMS_KEY_ID,
        tags=FAKE_TAGS
    )
    assert response['browserSettingsArn'] == "TEMP ARN"


@ mock_aws
def test_list_browser_settings():
    client = boto3.client('workspaces-web', region_name='us-west-2')
    arn = client.create_browser_settings(
        additionalEncryptionContext={'TestKey': 'TestValue'},
        browserPolicy='ALLOWLIST',
        customerManagedKey=FAKE_KMS_KEY_ID,
        tags=FAKE_TAGS
    )['browserSettingsArn']
    response = client.list_browser_settings()
    assert response['browserSettingsArns'] == [arn]


@ mock_aws
def test_get_browser_settings():
    assert False


@ mock_aws
def test_delete_browser_settings():
    assert False


@ mock_aws
def test_create_portal():
    assert False


@ mock_aws
def test_list_portals():
    assert False


@ mock_aws
def test_get_portal():
    assert False


@ mock_aws
def test_delete_portal():
    assert False


@ mock_aws
def test_associate_network_settings():
    assert False


@ mock_aws
def test_associate_browser_settings():
    assert False

# See our Development Tips on writing tests for hints on how to write good tests:
# http://docs.getmoto.org/en/latest/docs/contributing/development_tips/tests.html


@mock_aws
def test_create_portal():
    client = boto3.client("workspaces-web", region_name="eu-west-1")
    resp = client.create_portal()

    raise Exception("NotYetImplemented")
