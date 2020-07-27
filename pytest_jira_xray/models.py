import json
from typing import List

class TestReportDTO:
    """
    Example of test report in JSON format
    {
        "testKey": "DIP-3",
        "start": "2014-08-30T11:47:35+01:00",
        "finish": "2014-08-30T11:50:56+01:00",
        "comment": "Successful execution",
        "status": "FAILED"
    } 
    """

    def __init__(self, test_key, start, finish, status, duration):
        self.testKey = test_key
        self.start = start
        self.finish = finish
        self.status = status
        self.comment = 'This is automated test execution report. This test was active for ' + str(duration) + 'seconds'

    def as_json(self):
        return json.dumps(self.__dict__)

class TestExecutionReportDTO:
    """
    Example of test execution report in JSON format:

    "info": {
            "summary": "Execution of automated tests for release v1.3",
            "description": "This execution is automatically created when importing execution results from an external source",
            "revision": "1.0.42134",
            "startDate": "2014-08-30T11:47:35+01:00",
            "finishDate": "2014-08-30T11:53:00+01:00",
            "testPlanKey": "DIP-4",
            "testEnvironments": []
        },
        "tests": [{...}, {...}]
    } 
    """
    
    def __init__(self, test_plan_key, start_date, finish_date, tests):
        self.info = {}
        self.info.summary = 'Execution of automated tests from PyTest plugin'
        self.info.description = 'This execution is automatically created when importing execution results from an external source'
        self.info.startDate = start_date
        self.info.finishDate = finish_date
        self.info.testPlanKey = test_plan_key
        self.info.testEnvironments = []
        self.info.tests = tests

    def as_json(self):
        return json.dumps(self.__dict__)