import sys , os, json
print(sys.path)
import logging
from datetime import datetime
import decimal
import pytz
import services.click_schema as clicky

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]) )


def handler(event: any, context: any):
    action = event.get("Action", None)
    if action == None:
        return (dict(Message="Could Not Determine Action",Status=300))
    projectName = "OneClick"
    if event.get("action", None) == "getTotalForDay":
        tzCST = pytz.timezone('US/Central')
        todayClicked =  datetime.now(tzCST).strftime("%Y_%d_%m") 
        return get_daily_total(projectName, todayClicked)


# {
#     project: project
#     dateClicked: dateClicked
#     reportedTime: buttonClicked.reportedTime    2021-07-12T18:13:38.564Z
#     clickType:  buttonClicked.clickType
#     action: 
#     deviceInfo
#     placementInfo
# }

def get_daily_total(projectName: str, reportDate: str):
    todays_clicks = clicky.get_clicks_for_day(projectName, reportDate)
    print("List of clicks", todays_clicks)
    filterType = "SINGLE" 
    if todays_clicks == None or len(todays_clicks) == 0 \
            or len (list(filter(lambda x: x["clickType"] == filterType, todays_clicks))) == 0:
        print("No clicks - start session")
        return 0   
    sorted_clicks = sorted(
        filter(lambda x: x["clickType"] == filterType, todays_clicks), 
        key = lambda i: clicky.getISOTimeAsDate( i['reportedTime'] ))
    print("CLICKS: ", sorted_clicks) 

    totals_list = []
    accumulated_minutes: int = 0
    for click in sorted_clicks:
        if click.get("action") == "START":
            startTime = click.get("reportedTime")
        elif click.get("action") == "STOP":
            stopTime = click.get("reportedTime")
            time_difference = clicky.getISOTimeAsDate(stopTime) - clicky.getISOTimeAsDate(startTime)
            print("Time Difference: ", time_difference)
            minute_difference: int = time_difference.total_seconds() // 60
            accumulated_minutes = accumulated_minutes + minute_difference
            totals_list.append(dict(startTime=startTime,stopTime=stopTime, minutes=minute_difference ))

            startTime=None
    print ("Sum of all minutes = " + str(accumulated_minutes))
    print(totals_list)
    return dict(totalTime=accumulated_minutes,records=totals_list)








if __name__ == "__main__":
    print("lambda")