


def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))

    # "deviceEvent": {
    #   "buttonClicked": {
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    # }
    clickType = event["deviceEvent"]["clickType"]
    reportedTime = event["deviceEvent"]["reportedTime"]

    