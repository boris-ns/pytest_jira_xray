from setuptools import setup, find_packages

setup(
    name='pytest_jira_xray',
    version='0.1',
    author='Boris Sulicenko',
    author_email='b.sulicenko@gmail.com',
    url='https://github.com/boris-ns/pytest_jira_xray',
    license='LICENSE',
    packages=find_packages(),
    description='Plugin for PyTest that sends test reports to Xray (Jira).',
    install_requires=[
        'requests>=2.24.0'
    ]
)