import sys , os
print(sys.path)



test_item = {
    'PK': "CLICK|oneclick|2019_01_12",
    'SK': "2018-05-04T23:26:33.747Z",
    'clickType': "SINGLE",
    'action': "START",
    'deviceInfo': {
        "deviceInfo": {
            "attributes": {
                "key3": "value3",
                "key1": "value1",
                "key4": "value4"
            },
            "type": "button",
            "deviceId": " G030PMXXXXXXXXXX ",
            "remainingLife": 5.00
        }
    },
    'placementInfo': {
        "placementInfo": {
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
    }
}

item={
    'pk':  "KID_SCHEDULE|2020|Delia",
    'sk':  "PERIOD|8",
    'start':  "15:11",
    'end': "15:55"
}

# {
#     PK: CLICK|oneclick|date.strftime("%Y_%d_%m"),
#     SK: buttonClicked.reportedTime
#     clickType: buttonClicked.clickType
#     action: START | STOP
#     deviceInfo: deviceInfo
#     placementInfo: placementInfo
# }



# Run tests from src directory /c/git/one_click/backend/src
# ../venv_linux/bin/python -m pytest -s ../tests/services/test_dynamodb_service.py
# python -m pytest -s tests/services/test_dynamodb_service.py >> printout.txt
# ../venv_linux/bin/python -m pytest -s ../tests/services/test_dynamodb_service.py -k "sortKey"

class TestDynamoService:

    def test_get_data(self, get_db):
        self.service = get_db
        actual_item = self.service.get_data('KID_SCHEDULE|2020|Delia', 'PERIOD|8')
        # runThis = galvestonCounty.GalvestonCountyRunner()
        # runThis.get_friendswood_detail()
        # print ('Gathering Friendswood Data')
        print(actual_item)
        assert actual_item == item           

    def test_get_data_by_sortKey(self, get_db):
        self.service = get_db

        print("|".join(['SCHOOL', ""]))
        actual_item = self.service.queryOnSortKey('SCHEDULE')
        expected_item = dict({
            'pk':  "SCHOOL|2020|FISD",
            'sk':  "SCHEDULE",
            'start':  "08/31/2020",
            'end':  "05/27/2021"
            })
        print(actual_item)
        assert actual_item == [expected_item]          

    def test_put_data(self, get_db):
        self.service = get_db
        pk = test_item.get('pk')
        sk = test_item.get('sk')
        self.service.delete_data(pk, sk)
        assert self.service.get_data(pk, sk) == None

        self.service.put_data(pk, sk, start='10/1/2001', end='12/12/2012', databit='empty')
        assert self.service.get_data(pk, sk) == test_item

    def test_update_data(self, get_db):
        expected_item = test_item.copy()
        expected_item.update({'updated_attr': 'updated'})
        self.service = get_db
        pk = test_item.get('pk')
        sk = test_item.get('sk')
        self.service.put_data(pk, sk, start='10/1/2001', end='12/12/2012', databit='empty')
        assert self.service.get_data(pk, sk) == test_item

        self.service.update_data(pk, sk, 'updated_attr', 'updated')
        assert self.service.get_data(pk, sk) == expected_item