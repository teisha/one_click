
import os
from _datetime  import datetime
import decimal
import services.dynamodb_service as db

service = db.DynamoService(os.environ["CLICK_TABLE"])
pk_prefix = "CLICK"

def get_click_data(project: str, dateClicked: str, reportedTime: str):
    pk = "|".join([ pk_prefix, project, dateClicked ])
    result = service.get_data(pk, reportedTime)
    print(result)
    return convert_to_click_object(result)

def get_clicks_for_day(project: str, dateClicked: str):
    pk = "|".join([pk_prefix, project, dateClicked])    
    result = service.queryOnPrimaryKey(pk)
    return list(map(lambda x: convert_to_click_object(x) , result  ) )

def save_click(click_object: dict):
    if not is_valid(click_object):
        return {
            'statusCode': 400, 
            'message': "Malformed Request"
        }
    click_db_object = convert_to_db_object(click_object)
    result = service.put_data(
            pk=click_db_object.get("pk"),
            sk=click_db_object.get("sk"),
            clickType=click_db_object.get("clickType"),
            action=click_db_object.get("action"),
            deviceInfo=click_db_object.get("deviceInfo"),
            placementInfo=click_db_object.get("placementInfo")
        ) 
    print(result)
    message = f'Successfully Saved: {click_object.get("clickType")} at {click_object.get("reportedTime")}' if result.get('http_status') == 200 else \
        f'An error occurred while saving {click_object.get("clickType")} at {click_object.get("reportedTime")}'
    return { 'statusCode': result.get("http_status", 500),
        'message': message}   


def is_valid(schedule: dict):
    valid: bool = True
    if schedule.get("project", None) == None or \
        schedule.get("dateClicked", None) == None:
        print("Click Object doesn't contain key data")
        valid=False
    if schedule.get("clickType", None) == None or \
        schedule.get("deviceInfo", None) == None or \
        schedule.get("placementInfo", None) == None:
        print('Click Object does not contain click event data')
        valid=False
    return valid



# {
#     PK: CLICK|oneclick|date.strftime("%Y_%d_%m"),
#     SK: buttonClicked.reportedTime
#     clickType: buttonClicked.clickType
#     action: START | STOP
#     deviceInfo: deviceInfo
#     placementInfo: placementInfo
# }

# {
#     project: project
#     dateClicked: dateClicked
#     reportedTime: buttonClicked.reportedTime
#     clickType:  buttonClicked.clickType
#     action: 
#     deviceInfo
#     placementInfo
# }

def convert_to_click_object(data: dict): 
    print('CONVERT DB TO CLICK')
    pk = data.get("pk").split("|")
    return dict(
        project=pk[1],
        dateClicked=pk[2],
        reportedTime=data.get("sk"),
        clickType=data.get("clickType"),
        action=data.get("action"),
        deviceInfo=data.get("deviceInfo"),
        placementInfo=data.get("placementInfo")
    )

def convert_to_db_object(click_object: dict):
    converted_deviceInfo = click_object.get("deviceInfo")
    if converted_deviceInfo.get("remainingLife", None) != None:
        converted_deviceInfo["remainingLife"] = decimal.Decimal(str(converted_deviceInfo.get("remainingLife") ))

    db_object = dict ( 
        pk="|".join([pk_prefix, click_object.get("project"), click_object.get("dateClicked")]),
        sk=click_object.get("reportedTime"),
        clickType=click_object.get("clickType"),
        action=click_object.get("action"),
        deviceInfo=converted_deviceInfo,
        placementInfo=click_object.get("placementInfo"),
    )   
    return db_object
