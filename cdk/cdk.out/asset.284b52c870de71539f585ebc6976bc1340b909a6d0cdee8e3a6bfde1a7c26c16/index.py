import sys , os, json
print(sys.path)
import logging
from lambda_clicker import handler as clickHandler
from datetime import now

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]) )


def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))
    resource = event["resource"]
    method = event["httpMethod"]
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    single_click = os.environ["SINGLE_CLICK"]
    double_click = os.environ["DOUBLE_CLICK"]
    hold = os.environ["HOLD"]

    clickEvent = dict(buttonClicked=dict(reportedTime=now().isoformat() ))
    if resource == f"/{single_click}": 
        clickEvent["buttonClicked"]["clickType"]="SINGLE"
    elif resource == f"/{hold}":
        clickEvent["buttonClicked"]["clickType"]="LONG"
    elif resource == f"/{double_click}":
        clickEvent["buttonClicked"]["clickType"]="DOUBLE"
    clickHandler(clickEvent, context)