import os

import boto3
import pytest
from moto import mock_dynamodb2

MURALS_TABLE = "murals-test"


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture()
def aws_region():
    return "eu-central-1"


@pytest.fixture()
def fake_environment(monkeypatch):
    monkeypatch.setenv("MURALS_TABLE", MURALS_TABLE)


@pytest.fixture()
def dynamodb_client(aws_credentials, aws_region):
    with mock_dynamodb2():
        yield boto3.client("dynamodb", region_name=aws_region)


@pytest.fixture()
def dynamodb_resource(aws_credentials, aws_region):
    with mock_dynamodb2():
        yield boto3.resource("dynamodb", region_name=aws_region)


@pytest.fixture()
def murals_table(dynamodb_resource):
    dynamodb_resource.create_table(
        TableName=MURALS_TABLE,
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "artist_name_en", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "artist_name_en", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "artist_name_en-index",
                "KeySchema": [
                    {"AttributeName": "artist_name_en", "KeyType": "HASH"},
                    {"AttributeName": "id", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table = dynamodb_resource.Table(MURALS_TABLE)

    yield table
