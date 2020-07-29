import os
import requests
import json
import pytest
from typing import List

from pytest_jira_xray.api_paths import XRAY_CREATE_TEST_EXECUTION_URL, XRAY_AUTHENTICATION_URL
from pytest_jira_xray.config import XRAY_MARKER_TEST_ID
from pytest_jira_xray.models import TestReportDTO, TestExecutionReportDTO

# Env variables
XRAY_API_CLIENT_ID = os.environ['XRAY_API_CLIENT_ID']
XRAY_API_CLIENT_SECRET = os.environ['XRAY_API_CLIENT_SECRET']


def main():
    token = get_authentication_token()

    body = json.dumps({
        "info": {
            "summary": "Execution of automated tests for release v1.3",
            "description": "This execution is automatically created when importing execution results from an external source",
            "revision": "1.0.42134",
            "startDate": "2014-08-30T11:47:35+01:00",
            "finishDate": "2014-08-30T11:53:00+01:00",
            "testPlanKey": "DIP-4",
            "testEnvironments": []
        },
        "tests": [
            {
                "testKey": "DIP-2",
                "start": "2014-08-30T11:47:35+01:00",
                "finish": "2014-08-30T11:50:56+01:00",
                "comment": "Successful execution",
                "status": "PASSED"
            },
            {
                "testKey": "DIP-3",
                "start": "2014-08-30T11:47:35+01:00",
                "finish": "2014-08-30T11:50:56+01:00",
                "comment": "Successful execution",
                "status": "FAILED"
            }
        ]
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    response = requests.post(XRAY_CREATE_TEST_EXECUTION_URL, data=body, headers=headers)

    print(body)

    print(response.status_code)
    print(response.json())


def get_authentication_token() -> str:
    headers = { 'Content-Type': 'application/json' }

    body = {
        'client_id': XRAY_API_CLIENT_ID, 
        'client_secret': XRAY_API_CLIENT_SECRET
    }
    
    response = requests.post(XRAY_AUTHENTICATION_URL, body, headers)
    token = response.json()

    return token


# TODO: delete later
# this is just for testing
def pytest_report_header():
    # if (pytest.config.getoption('silent')):
    # if is_silent_mode:
    return "HELOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"


# def pytest_configure(config) -> None:
#     if config.getoption('silent'):
#         print("SILENT MODE IS ACTIVATED")


def pytest_addoption(parser) -> None:
    group = parser.getgroup('silent')
    group.addoption('--silent', action='store_true', help='Do not send the data to the Xray (Jira)')


def pytest_configure(config):
    # Register custom markers that our plugin uses
    config.addinivalue_line(
        'markers', XRAY_MARKER_TEST_ID + '(): set Jira test ID for this test'
    )


def pytest_runtest_setup(item) -> None:
    marker = item.get_closest_marker(XRAY_MARKER_TEST_ID)

    if marker is not None:
        test_id = marker.args[0]
        print('Test ID is: ' + str(test_id))


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    # Silent mode is activated so we wont send any data to the Xray    
    if config.getoption('silent'):
        print("[INFO] Silent mode activated: We won't send any data to the Xray (Jira)")
        return

    passed_tests = []
    failed_tests = []

    try:
        passed_tests = terminalreporter.stats['passed']
        failed_tests = terminalreporter.stats['failed']
    except KeyError:
        pass

    tests: List[TestReportDTO] = []

    # TODO: prebaci ovu petlju u neku fju
    for test in passed_tests:
        print(type(test))

        print(test)

        t = TestReportDTO('DIP-2', '2014-08-30T11:47:35+01:00', 
            '2014-08-30T11:47:35+01:00', test.outcome, test.duration
        )
        tests.append(t)

    for test in failed_tests:
        t = TestReportDTO('DIP-3', '2014-08-30T11:47:35+01:00', 
            '2014-08-30T11:47:35+01:00', test.outcome, test.duration
        )
        tests.append(t)
        
    test_execution_report = TestExecutionReportDTO('DIP-4', 
        '2014-08-30T11:47:35+01:00', 
        '2014-08-30T11:47:35+01:00', 
        tests
    )

    token = get_authentication_token()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    # TODO: treba proveriti kakav ce biti JSON za TestExecutionReportDTO
    # pretpostavljam da i to treba srediti na neki nacin da bude lepo formatirano
    print(test_execution_report.as_json())

    # tests lista kao da se 2x formatira u string tj. json format

    request_body = test_execution_report.as_json()
    response = requests.post(XRAY_CREATE_TEST_EXECUTION_URL, data=request_body, headers=headers)

    print(response.status_code)
    print(response.json())

    if (response.status_code == 200):
        print('[INFO] Reports have been sent to the Xray (Jira)')
    else:
        print('[ERROR] There was an error while sending the data to Xray (Jira)')
