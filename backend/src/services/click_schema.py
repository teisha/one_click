
import os
import dynamodb_service as db
from _datetime  import datetime

service = db.DynamoService(os.environ["CLICK_TABLE"])
pk_prefix = "CLICK"

def get_click_data(project: str, dateClicked: str, reportedTime: str):
    pk = "|".join([ pk_prefix, project, dateClicked ])
    result = service.get_data(pk, reportedTime)
    return convert_to_click_object(result)

def get_clicks_for_day(project: str, dateClicked: str):
    pk = "|".join([pk_prefix, project, dateClicked])    
    result = service.queryOnPrimaryKey(pk)
    return list(map(lambda x: convert_to_click_object(x) , result  ) )

def save_click(click_object: dict):
    if not is_valid(button_event):
        return {
            'statusCode': 400, 
            'message': "Malformed Request"
        }
    result = service.put_data(convert_to_db_object(click_object)) 
    print(result)
    message = f'Successfully Saved: {click_object.get("clickType")} at {click_object.get("reportedTime")}' if result.get('http_status') == 200 else \
        f'An error occurred while saving {click_object.get("clickType")} at {click_object.get("reportedTime")}'
    return { 'statusCode': result.get("http_status", 500),
        'message': message}   


def is_valid(schedule: dict):
    valid: bool = True
    if schedule.get("buttonClicked", None) == None or \
        schedule.get("deviceInfo", None) == None or \
        schedule.get("placementInfo", None) == None:
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
    pk = data.get("PK").split("|")
    return dict(
        project=pk[1],
        dateClicked=pk[2],
        reportedTime=data.get("SK"),
        clickType=data.get("clickType"),
        action=data.get("action"),
        deviceInfo=data.get("deviceInfo"),
        placementInfo=data.get("placementInfo")
    )

def convert_to_db_object(click_object: dict):
    db_object = dict ( 
        PK="|".join([pk_prefix, click_object.get("project"), click_object.get("dateClicked")]),
        SK=click_object.get("reportedTime"),
        clickType=click_object.get("clickType"),
        action=click_object.get("action"),
        deviceInfo=click_object.get("deviceInfo"),
        placementInfo=click_object.get("placementInfo"),
    )   
    return db_object
