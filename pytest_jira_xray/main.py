import os
import requests
import json
import pytest
from typing import List

from pytest_jira_xray.api_paths import XRAY_CREATE_TEST_EXECUTION_URL, XRAY_AUTHENTICATION_URL
from pytest_jira_xray.config import XRAY_MARKER_TEST_ID, XRAY_CMD_LINE_ARG_TEST_PLAN, XRAY_CMD_LINE_ARG_SILENT
from pytest_jira_xray.models import TestReportDTO, TestExecutionReportDTO

# Env variables
XRAY_API_CLIENT_ID = os.environ.get('XRAY_API_CLIENT_ID')
XRAY_API_CLIENT_SECRET = os.environ.get('XRAY_API_CLIENT_SECRET')

# Mapping 'nodeid' from pytest's test to Jira's test id from marker
test_keys = {}


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


def pytest_addoption(parser) -> None:
    group = parser.getgroup('silent')
    group.addoption('--' + XRAY_CMD_LINE_ARG_SILENT, action='store_true', help='Do not send the data to the Xray (Jira)')

    parser.addoption('--' + XRAY_CMD_LINE_ARG_TEST_PLAN, action="store", default=None, help='Test plan ID from Jira')


def pytest_configure(config):
    # Register custom markers that our plugin uses
    config.addinivalue_line(
        'markers', XRAY_MARKER_TEST_ID + '(id): set Jira test ID for this test'
    )


def pytest_runtest_setup(item) -> None:
    global test_keys

    marker = item.get_closest_marker(XRAY_MARKER_TEST_ID)
    
    if marker is not None:
        test_id = marker.args[0]
        test_keys[item.nodeid] = test_id


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    global test_keys

    # Check if required environment variables exist
    if XRAY_API_CLIENT_ID is None or XRAY_API_CLIENT_SECRET is None:
        print('[ERROR] Xray API client ID or SECRET are not set as environment variables')
        return
    
    # Silent mode is activated so we wont send any data to the Xray    
    if config.getoption(XRAY_CMD_LINE_ARG_SILENT):
        print("[INFO] Silent mode activated: We won't send any data to the Xray (Jira)")
        return

    jira_test_plan_id = config.getoption(XRAY_CMD_LINE_ARG_TEST_PLAN)

    if jira_test_plan_id is None:
        print('[WARNING] In order to send the data to the Xray (Jira) you must pass Test Plan ID from Jira')
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
        # TODO: sta ako kljuc u test_keys ne postoji
        t = TestReportDTO(test_keys[test.nodeid], '2014-08-30T11:47:35+01:00', 
            '2014-08-30T11:47:35+01:00', test.outcome, test.duration
        )
        tests.append(t)

    for test in failed_tests:
        # TODO: sta ako kljuc u test_keys ne postoji
        t = TestReportDTO(test_keys[test.nodeid], '2014-08-30T11:47:35+01:00', 
            '2014-08-30T11:47:35+01:00', test.outcome, test.duration
        )
        tests.append(t)
        
    test_execution_report = TestExecutionReportDTO(jira_test_plan_id, 
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

    if (response.status_code == 200):
        print('[INFO] Reports have been sent to the Xray (Jira)')
    else:
        print('[ERROR] There was an error while sending the data to Xray (Jira)')
        print('\t' + response.json()['error'])
