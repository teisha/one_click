import sys , os
print(sys.path)
import pytest
import lambda_clicker as clicker

# Run tests from src directory /c/git/one_click/backend/src
# ../venv_linux/bin/python -m pytest -s ../tests/test_lambda_clicker.py

class TestClicker:
    def test_next_start_data(self, mocker):
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

        actual_item = clicker.get_next_action("oneclick","2019_01_12","SINGLE")
        expected_next_action = "START"
        print(actual_item)
        assert actual_item == expected_next_action

    def test_next_stop_data(self, mocker):
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
            ), dict(
                project='oneclick', 
                dateClicked='2019_01_12',
                reportedTime="2018-05-04T23:35:33.747Z",
                clickType="SINGLE",
                action="START",
                deviceInfo=dict(),
                placementInfo=dict()
            ), dict(
                project='oneclick', 
                dateClicked='2019_01_12',
                reportedTime="2018-05-04T23:39:33.747Z",
                clickType="DOUBLE",
                action="STOP",
                deviceInfo=dict(),
                placementInfo=dict()
            )]
        )

        actual_item = clicker.get_next_action("oneclick","2019_01_12","SINGLE")
        expected_next_action = "STOP"
        print(actual_item)
        assert actual_item == expected_next_action        

    def test_next_no_data(self, mocker):
        mocker.patch(
            'services.click_schema.get_clicks_for_day',
            return_value=[]
        )

        actual_item = clicker.get_next_action("oneclick","2019_01_12","SINGLE")
        expected_next_action = "START"
        print(actual_item)
        assert actual_item == expected_next_action

    def test_next_start_data(self, mocker):
        mocker.patch(
            'services.click_schema.get_clicks_for_day',
            return_value=[dict(
                project='oneclick', 
                dateClicked='2019_01_12',
                reportedTime="2018-05-04T23:26:33.747Z",
                clickType="LONG",
                action="START",
                deviceInfo=dict(),
                placementInfo=dict()
            ), dict(
                project='oneclick', 
                dateClicked='2019_01_12',
                reportedTime="2018-05-04T23:29:33.747Z",
                clickType="LONG",
                action="STOP",
                deviceInfo=dict(),
                placementInfo=dict()
            )]
        )

        actual_item = clicker.get_next_action("oneclick","2019_01_12","SINGLE")
        expected_next_action = "START"
        print(actual_item)
        assert actual_item == expected_next_action 