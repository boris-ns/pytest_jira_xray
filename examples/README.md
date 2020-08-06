# pytest_jira_xray examples

This folder contains example test files.  
These files represent how this plugin is supposed to be used.  
To run these tests create a virtual environment and install the plugin
```
$ virtualenv env
$ pip install -e ../
```

Flag ```-e``` means that the plugin will be installed in development mode.
After installing, you can run the tests:
```
$ pytest --plan TEST_PLAN_JIRA_ID
```
