import sys , os, json
print(sys.path)
import logging
from datetime import datetime
import decimal
import pytz
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
    # dateClicked = clicky.getISOTimeAsDate(reportedTime).strftime("%Y_%d_%m")

    
    tzCST = pytz.timezone('US/Central')
    dateClicked =  datetime.now(tzCST).strftime("%Y_%d_%m")
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
            placementInfo=placementInfo,
            timestamp=decimal.Decimal(datetime.now(tzCST).timestamp())
        )


    try: 
        clicky.save_click(click_to_save)
        if action == 'START' or action == "RESET_START":
            bulby.turn_on("shiny")
            bulby.turn_on("home_office")
        elif action == 'STOP' or action == "RESET_STOP":
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
    filterType = "SINGLE" if clickType == "LONG" else clickType
    if todays_clicks == None or len(todays_clicks) == 0 \
            or len (list(filter(lambda x: x["clickType"] == filterType, todays_clicks))) == 0:
        print("No clicks - start session")
        return "START"   
    last_click = sorted(
        filter(lambda x: x["clickType"] == filterType, todays_clicks), 
        key = lambda i: clicky.getISOTimeAsDate( i['reportedTime'] ),
        reverse=True)[0]
    print("LAST CLICK: ", last_click) 
    if clickType == "SINGLE":       
        return action_dict.get(last_click.get("action", 'NONE'))
    elif clickType == "LONG":
        return "RESET_" + last_click.get("action", 'START')
    else:
        return "UNDEFINED"





# https://developer.amazon.com/en-US/docs/alexa/smarthome/send-events-to-the-alexa-event-gateway.html
def turn_bulb_color(deviceId: str, clickType: str, action: str):
    api_gateway = "https://api.amazonalexa.com/v3/events"