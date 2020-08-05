# pytest_jira_xray
This plugin allows you to send testing reports to the [Jira](https://www.atlassian.com/software/jira) board by connecting it with [PyTest](https://docs.pytest.org/en/stable/index.html)

On Jira board you can create issues with ```Test``` type and you need to assign them to a ```Test plan``` issue. After the plugin is called the new issue of type ```Test execution``` will be created. That new issue will contain basic information about the test run.

Also, there is a "silent" option that won't send any information to Jira. To use it just pass ```--silent``` command line argument when calling PyTest.

# How to use

1. Install [Xray Test Management for Jira](https://marketplace.atlassian.com/apps/1211769/xray-test-management-for-jira?hosting=cloud&tab=overview) and set everything up according to the Xray documentation
2. Get API keys from Xray and set them as environment variables in your OS (XRAY_API_CLIENT_ID and XRAY_API_CLIENT_SECRET).
3. Inside your project install [PyTest](https://docs.pytest.org/en/stable/index.html)
4. Download this plugin
```
$ git clone https://github.com/boris-ns/pytest_jira_xray 
```
5. Install plugin with
```
$ pip install pytest_jira_xray
```

Now that you have installed this plugin, here is how you can use it inside Python code.

First of all, you need to add decorators (markers) to test functions. These markers need to contains ID of a ```Test``` issue for Jira board.

Here is an example of one test function
```python
@pytest.mark.xray_test_id('TEST_ID_FROM_JIRA')
def test_add():
    assert add(1, 1) == 2
```

To run this plugin, just call ```pytest``` command with command line argument ```---plan TEST_PLAN_ID```.

```
pytest --plan PLAN_ID_FROM_JIRA
```
