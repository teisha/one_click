import sys , os, json
print(sys.path)
import logging
from lambda_clicker import handler as clickHandler
from datetime import datetime as dt

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]) )

# { "resource": "/48a74731-3b5f-4acd-b7f2-1e1c707c1c39", "httpMethod":"GET"} - click
# { "resource": "/d902d1cd-784f-4bce-b1e7-36c1dc603d9d", "httpMethod":"GET"} - hold
# { "resource": "/941967c0-26cc-4b3a-a36c-99b85e2ad568", "httpMethod":"GET"} - double click
def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))
    resource = event["resource"]
    method = event["httpMethod"]
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    single_click = os.environ["SINGLE_CLICK"]
    double_click = os.environ["DOUBLE_CLICK"]
    hold = os.environ["HOLD"]

    clickEvent = dict(buttonClicked=dict(reportedTime=dt.now().isoformat() ))
    if resource == f"/{single_click}": 
        clickEvent["buttonClicked"]["clickType"]="SINGLE"
    elif resource == f"/{hold}":
        clickEvent["buttonClicked"]["clickType"]="LONG"
    elif resource == f"/{double_click}":
        clickEvent["buttonClicked"]["clickType"]="DOUBLE"
    if clickEvent["buttonClicked"]["clickType"] == None:
        response = {}
        response["statusCode"] = 300
        response["message"] = "Nope"
        return response 
    else:
        clickHandler(dict(deviceEvent=clickEvent), context)