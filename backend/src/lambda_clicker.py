
import services.click_schema as clicky

def handler(event: any, context: any):
    logger.info("event: {}".format(json.dumps(event) ))

    # "deviceEvent": {
    #   "buttonClicked": {
    #     "clickType": "SINGLE",
    #     "reportedTime": "2018-05-04T23:26:33.747Z"
    # }
    clickType = event["deviceEvent"]["clickType"]
    reportedTime = event["deviceEvent"]["reportedTime"]
    deviceInfo = event["deviceEvent"]["deviceInfo"]
    placementInfo = event["deviceEvent"]["placementInfo"]
    projectName = "OneClick"
    if placementInfo != None:
        projectName = placementInfo.get("projectName", projectName)
    action = get_next_action(projectName, dateClicked, clickType)

    click_to_save = dict(
            project=projectName,
            dateClicked=getISOTimeAsDate(reportedTime),
            reportedTime=reportedTime,
            clickType=clickType,
            action=action, 
            deviceInfo=deviceInfo
            placementInfo=placementInfo
        )


    try: 
        clicky.save_click()
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
        if todays_clicks == None || len(todays_clicks) == 0:
            return "START"
        last_click = sorted(todays_clicks, key = lambda i: getISOTimeAsDate( i['reportedTime'] ),reverse=True)[0]
        return action_dict.get(last_click.get("action", 'NONE'))

    
    def getISOTimeAsDate(reportedTime: str):
        return datetime.fromisoformat(reportedTime.replace('Z',''))