import sys , os
from datetime import datetime
print(sys.path)
import services.click_schema as clicky

deviceInfo = {
        "attributes": {
            "key3": "value3",
            "key1": "value1",
            "key4": "value4"
        },
        "type": "button",
        "deviceId": " G030PMXXXXXXXXXX ",
        "remainingLife": 5.00
    }
placementInfo = {
        "projectName": "test",
        "placementName": "myPlacement",
        "attributes": {
            "location": "Seattle",
            "equipment": "printer"
        },
        "devices": {
            "myButton": " G030PMXXXXXXXXXX "
        }
    }    

test_item = {
    'project': 'oneclick',
    'dateClicked': '2019_01_12',
    'reportedTime': "2018-05-04T23:26:33.747Z",
    'clickType': "SINGLE",
    'action': "START",
    'deviceInfo': deviceInfo,
    'placementInfo': placementInfo
}

item = {
    'PK': "CLICK|oneclick|2019_01_12",
    'SK': "2018-05-04T23:26:33.747Z",
    'clickType': "SINGLE",
    'action': "START",
    'deviceInfo': deviceInfo,
    'placementInfo': placementInfo
}

# Run tests from src directory
# ../venv_linux/bin/python -m pytest -s ../tests/services/test_click_schema.py

class TestDynamoService:

    def test_get_data(self, get_db):
        self.service = get_db

        reportedTime = "2018-05-04T23:26:33.747"
        reportedDate = datetime.fromisoformat(reportedTime)
        print(reportedDate)

        result = clicky.save_click(test_item)
        print("SAVE CLICK")
        print (result)
        actual_item = clicky.get_click_data('oneclick', '2019_01_12', '2018-05-04T23:26:33.747Z')

        print(actual_item)
        assert actual_item == test_item     