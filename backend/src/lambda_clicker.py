import sys , os, json
print(sys.path)
import logging
from datetime import datetime
import services.click_schema as clicky
import services.bulb_service as bulby

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]) )


def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))

    # "deviceEvent": {
    #   "buttonClicked": {
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    # }
    clickType = event["deviceEvent"]["buttonClicked"]["clickType"]
    reportedTime = event["deviceEvent"]["buttonClicked"]["reportedTime"]
    # dateClicked = getISOTimeAsDate(reportedTime).strftime("%Y_%d_%m")
    dateClicked =  datetime.now().strftime("%Y_%d_%m")
    deviceInfo = event["deviceInfo"]
    placementInfo = event["placementInfo"]
    projectName = "OneClick"
    if placementInfo != None:
        projectName = placementInfo.get("projectName", projectName)
    action = get_next_action(projectName, dateClicked, clickType)

    click_to_save = dict(
            project=projectName,
            dateClicked=dateClicked,
            reportedTime=reportedTime,
            clickType=clickType,
            action=action, 
            deviceInfo=deviceInfo,
            placementInfo=placementInfo
        )


    try: 
        clicky.save_click(click_to_save)
        if action == 'START':
            bulby.turn_on("shiny")
            bulby.turn_on("home_office")
        elif action == 'STOP':
            bulby.turn_off("shiny")
            bulby.turn_off("home_office")
    except Exception as ex:
        print("Couldn't save click ")
        print(ex)


    
    # {
    #     project: project
    #     dateClicked: dateClicked
    #     reportedTime: buttonClicked.reportedTime
    #     clickType:  buttonClicked.clickType
    #     action: 
    #     deviceInfo
    #     placementInfo
    # }


    # {
    #     "deviceEvent": {
    #     "buttonClicked": {
    #         "clickType": "SINGLE",
    #         "reportedTime": "2018-05-04T23:26:33.747Z"
    #     }
    #     },
    #     "deviceInfo": {
    #     "attributes": {
    #         "key3": "value3",
    #         "key1": "value1",
    #         "key4": "value4"
    #     },
    #     "type": "button",
    #     "deviceId": " G030PMXXXXXXXXXX ",
    #     "remainingLife": 5.00
    #     },
    #     "placementInfo": {
    #     "projectName": "test",
    #     "placementName": "myPlacement",
    #     "attributes": {
    #         "location": "Seattle",
    #         "equipment": "printer"
    #     },
    #     "devices": {
    #         "myButton": " G030PMXXXXXXXXXX "
    #     }
    #     }
    # }    

def get_next_action(project: str, dateClicked: str, clickType: str):
    action_dict = dict(START='STOP', STOP='START', NONE='START')
    todays_clicks = clicky.get_clicks_for_day(project, dateClicked)
    print("List of clicks", todays_clicks)
    if todays_clicks == None or len(todays_clicks) == 0 \
            or len (list(filter(lambda x: x["clickType"] == clickType, todays_clicks))) == 0:
        print("No clicks - start session")
        return "START"   
    last_click = sorted(
        filter(lambda x: x["clickType"] == clickType, todays_clicks), 
        key = lambda i: getISOTimeAsDate( i['reportedTime'] ),
        reverse=True)[0]
    print("LAST CLICK: ", last_click)        
    return action_dict.get(last_click.get("action", 'NONE'))


def getISOTimeAsDate(reportedTime: str):
    return datetime.fromisoformat(reportedTime.replace('Z',''))


# https://developer.amazon.com/en-US/docs/alexa/smarthome/send-events-to-the-alexa-event-gateway.html
def turn_bulb_color(deviceId: str, clickType: str, action: str):
    api_gateway = "https://api.amazonalexa.com/v3/events"