import sys , os
print(sys.path)
import pytest
import lambda_reporter as reporter

# Run tests from src directory /c/git/one_click/backend/src
# ../venv_linux/bin/python -m pytest -s ../tests/test_lambda_reporter.py

class TestReporter:
    def test_get_time_for_date(self, mocker):
        mocker.patch(
            'services.click_schema.get_clicks_for_day',
            return_value=[dict(
                project='oneclick', 
                dateClicked='2019_01_12',
                reportedTime="2018-05-04T23:26:33.747Z",
                clickType="SINGLE",
                action="START",
                deviceInfo=dict(),
                placementInfo=dict()
            ), dict(
                project='oneclick', 
                dateClicked='2019_01_12',
                reportedTime="2018-05-04T23:29:33.747Z",
                clickType="SINGLE",
                action="STOP",
                deviceInfo=dict(),
                placementInfo=dict()
            )]
        )

        actual_item = reporter.get_daily_total("oneclick","2019_01_12")
        expected_list = [{'startTime': '2018-05-04T23:26:33.747Z', 'stopTime': '2018-05-04T23:29:33.747Z', 'minutes': 3.0}]
        print(actual_item)
        assert actual_item == dict(totalTime=3.0,records=expected_list)