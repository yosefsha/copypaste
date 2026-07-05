import pytest

from copypaste import db
from copypaste.app import create_app


@pytest.fixture
def integration_table():
    resource = db.get_resource()
    table = db.create_table(resource, table_name="pastes-integration-test")
    yield table
    table.delete()
    table.wait_until_not_exists()


@pytest.fixture
def app(integration_table):
    return create_app(table=integration_table)


@pytest.fixture
def client(app):
    return app.test_client()
