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

# venv_linux/bin/python -m pip install boto3
# venv_linux/bin/python ssm_service.py
if __name__ == "__main__":
    session = Session(profile_name='power-user')
    # boto3.Session(profile_name='namexyz')
    credentials = session.get_credentials()
    # Credentials are refreshable, so accessing your access key / secret key
    # separately can lead to a race condition. Use this to get an actual matched
    # set.
    current_credentials = credentials.get_frozen_credentials()
    parameter_name= '/Connect/dev/Hubitat'  
    print(get_ssm_parameter(parameter_name))      