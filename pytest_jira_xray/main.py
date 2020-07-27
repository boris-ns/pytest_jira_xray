import os
import requests
import json

from config import XRAY_CREATE_TEST_EXECUTION_URL, XRAY_AUTHENTICATION_URL

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


if __name__ == '__main__':
    main()
