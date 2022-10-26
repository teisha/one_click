import boto3
from boto3 import Session


def get_ssm_parameter(name: str):
    client = boto3.client('ssm')
    print('Get parameter: ' + name)
    response = client.get_parameter(
            Name=name,
            WithDecryption=True
        )
    return response["Parameter"]["Value"]   

   