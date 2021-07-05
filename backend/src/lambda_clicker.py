


def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))

    # "deviceEvent": {
    #   "buttonClicked": {
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    # }
    dateClicked = 
    clickType = event["deviceEvent"]["clickType"]
    reportedTime = event["deviceEvent"]["reportedTime"]

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