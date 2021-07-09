import os
os.environ["CLICK_TABLE"] = 'dev-one-click-data-table'
os.environ["LOGGING_LEVEL"] = 'DEBUG'
import pytest
import services.dynamodb_service as dbs

import boto3
session = boto3.session.Session(profile_name='power-user')


os.environ["SECRET"] = "SyqT8jTGkyBUNBH1IFrcqb"
os.environ["ALG"] = 'HS256'

@pytest.fixture(scope="module")
def get_db():
    table_name = 'dev-one-click-data-table'
    return dbs.DynamoService(table_name)