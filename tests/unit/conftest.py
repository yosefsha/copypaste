import pytest
from moto import mock_aws

from copypaste import db
from copypaste.app import create_app


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        resource = db.get_resource()
        yield db.create_table(resource, table_name="pastes-test")


@pytest.fixture
def app(dynamodb_table):
    return create_app(table=dynamodb_table)


@pytest.fixture
def client(app):
    return app.test_client()
