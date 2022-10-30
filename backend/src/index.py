import sys , os, json
print(sys.path)
import logging
from lambda_clicker import handler as clickHandler
from datetime import datetime as dt
import traceback

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]) )

# { "resource": "/workbutton/48a74731-3b5f-4acd-b7f2-1e1c707c1c39", "httpMethod":"GET"} - click
# { "resource": "/workbutton/d902d1cd-784f-4bce-b1e7-36c1dc603d9d", "httpMethod":"GET"} - hold
# { "resource": "/workbutton/941967c0-26cc-4b3a-a36c-99b85e2ad568", "httpMethod":"GET"} - double click
def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))
    resource = event["resource"]
    method = event["httpMethod"]
    parameters = event["pathParameters"]
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    SINGLE_CLICK = os.environ["SINGLE_CLICK"]
    DOUBLE_CLICK = os.environ["DOUBLE_CLICK"]
    HOLD = os.environ["HOLD"]


    deviceInfo=dict(attributes=dict(button_key=1))
    placementInfo = dict(projectName=parameters.get("buttonType", None))
    clickEvent = dict(buttonClicked=dict(reportedTime=dt.now().isoformat() ))
    clickType = parameters.get("clickType", None)
    if clickType == SINGLE_CLICK: 
        clickEvent["buttonClicked"]["clickType"]="SINGLE"
    elif clickType == HOLD:
        clickEvent["buttonClicked"]["clickType"]="LONG"   # OneClick terminology
    elif clickType == DOUBLE_CLICK:
        clickEvent["buttonClicked"]["clickType"]="DOUBLE"

    response = {}
    if clickEvent["buttonClicked"].get("clickType", None) == None:
        response["statusCode"] = 300
        response["body"] = "Nope"
    else:
        try: 
            clickHandler(dict(deviceEvent=clickEvent, deviceInfo=deviceInfo, placementInfo=placementInfo), context)
            response["statusCode"] = 200
            response["body"] = f"Button Clicked:: {clickEvent}"
        except Exception:
            print(f"Call To Click Failed::")
            response["statusCode"] = 503
            response["body"] = "NopeClick"
            traceback.print_exc()

    print(f"RETURNING RESPONSE:: {response}")    
    return response 