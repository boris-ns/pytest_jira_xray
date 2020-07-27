import os
import requests
import json
import pytest

from pytest_jira_xray.api_paths import XRAY_CREATE_TEST_EXECUTION_URL, XRAY_AUTHENTICATION_URL
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
    body = {
        'client_id': XRAY_API_CLIENT_ID, 
        'client_secret': XRAY_API_CLIENT_SECRET
    }
    
    headers = {
        'Content-Type': 'application/json'
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


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    # Silent mode is activated so we wont send any data to the Xray    
    if config.getoption('silent'):
        print("Silent mode activated: We won't send any data to the Xray (Jira)")
        return
    
    passed_tests = terminalreporter.stats['passed']
    failed_tests = terminalreporter.stats['failed']
    tests = []

    print(test.as_json())

    # TODO: prebaci ovu petlju u neku fju
    for test in passed_tests:
        t = TestReportDTO('KEY-TODO', '2014-08-30T11:47:35+01:00', 
            '2014-08-30T11:47:35+01:00', test.outcome, test.duration
        )
        tests.append(t.as_json())

    for test in failed_tests:
        t = TestReportDTO('KEY-TODO', '2014-08-30T11:47:35+01:00', 
            '2014-08-30T11:47:35+01:00', test.outcome, test.duration
        )
        tests.append(t)
        

    test_execution_report = TestExecutionReportDTO('DIP-4', '2014-08-30T11:47:35+01:00', '2014-08-30T11:47:35+01:00', tests)

    print('Reports has been sent to the Xray (Jira)')
