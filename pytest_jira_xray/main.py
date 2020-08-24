import os
import requests
import json
import pytest
from typing import List

from pytest_jira_xray.api_paths import XRAY_CREATE_TEST_EXECUTION_URL, XRAY_AUTHENTICATION_URL
from pytest_jira_xray.config import XRAY_MARKER_TEST_ID, XRAY_CMD_LINE_ARG_TEST_PLAN, XRAY_CMD_LINE_ARG_SILENT, ENV_XRAY_API_CLIENT_ID, ENV_XRAY_API_CLIENT_SECRET
from pytest_jira_xray.models import TestReportDTO, TestExecutionReportDTO
from pytest_jira_xray.utils import get_current_datetime, get_current_datetime_normal

# Env variables
XRAY_API_CLIENT_ID = os.environ.get(ENV_XRAY_API_CLIENT_ID)
XRAY_API_CLIENT_SECRET = os.environ.get(ENV_XRAY_API_CLIENT_SECRET)

# Mapping 'nodeid' from pytest's test to Jira's test id from marker
test_keys = {}
start_time = get_current_datetime()
start_time_normal = get_current_datetime_normal()


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


def send_test_execution_to_jira(test_execution_report, token):
    if 'error' in token:
        print('[ERROR] There was an error while authenticating user.')
        print('\t' + token['error'])
        return None

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    request_body = test_execution_report.as_json()
    response = requests.post(XRAY_CREATE_TEST_EXECUTION_URL, data=request_body, headers=headers)
    return response


def create_test_description(test) -> str:
    comment = 'This is automated test execution report.\nThis test was active for ' + str(test.duration) + ' seconds.\n'

    if test.longrepr != None:
        comment += '\nERROR LOG:\n' + str(test.longrepr)

    return comment


def create_report_description(tests) -> str:
    report_description = 'Test execution report:\n\nTesting started at: ' + start_time_normal + '\nTesting ended at: ' + get_current_datetime_normal() + '\n\n'

    for test in tests:
        report_description += test.nodeid + '..........' + test.outcome + '\n'

    return report_description


def create_test_report_dto_list(tests) -> List[TestReportDTO]:
    end_time = get_current_datetime()
    testsDto: List[TestReportDTO] = []

    for test in tests:
        # TODO: sta ako kljuc u test_keys ne postoji
        t = TestReportDTO(test_keys[test.nodeid], start_time, end_time, 
            test.outcome, create_test_description(test)
        )
        testsDto.append(t)

    return testsDto


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
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
    except KeyError:
        pass

    try:
        failed_tests = terminalreporter.stats['failed']
    except KeyError:
        pass

    # Filter out tests that don't have Jira Test ID
    passed_tests = [t for t in passed_tests if t.nodeid in test_keys]
    failed_tests = [t for t in failed_tests if t.nodeid in test_keys]

    # Create test execution description
    report_description = create_report_description(passed_tests + failed_tests)

    # TODO: treba razresiti parametrizovane testove
    # ako ih ima u obe liste treba ukloniti one iz passed_tests
    # u suprotnom ostaviti kako treba, iako ce biti duplikata
    # jira moze da izbori sa tim jer ce smatrati prvi test
    # onim koji treba da objavi na kartici
    # [x for x in myList if x.n == 30]

    to_delete = []
    for i in range(len(passed_tests)):
        found_tests = [x for x in failed_tests if test_keys[x.nodeid] == test_keys[passed_tests[i].nodeid]]

        if len(found_tests) > 0:
            to_delete.append(i)

    for i in sorted(to_delete, reverse=True):
        del passed_tests[i]


    tests: List[TestReportDTO] = create_test_report_dto_list(passed_tests + failed_tests)

    test_execution_report = TestExecutionReportDTO(jira_test_plan_id, 
        report_description,
        '2014-08-30T11:47:35+01:00', 
        '2014-08-30T11:47:35+01:00', 
        tests
    )

    token = get_authentication_token()
    response = send_test_execution_to_jira(test_execution_report, token)

    if response is None:
        return

    if (response.status_code == 200):
        print('[INFO] Reports have been sent to the Xray (Jira)')
        print('\tNew Test Execution with ID ' + response.json()['key'] + ' has been created.')
    else:
        print('[ERROR] There was an error while sending the data to Xray (Jira)')
        print('\t' + response.json()['error'])
