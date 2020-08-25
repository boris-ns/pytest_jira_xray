import pytest
import time

def inc(x):
    return x + 1


def gt5(value):
    return value > 5


def test_true():
    assert True

def test_false():
    assert True


@pytest.mark.xray_test_id('DIP-2')
def test_answer():
    assert inc(3) == 4


@pytest.mark.xray_test_id('DIP-3')
def test_answer2():
    assert inc(5) == 6


@pytest.mark.xray_test_id('DIP-35')
@pytest.mark.parametrize('value', [4, 5, 6, 7])
def test_gt5(value):
    time.sleep(1)
    assert gt5(value)


"""
Use this command to only run tests with this marker
pytest -v -m my_mark
 or 
pytest -v -m "not my_mark" to run all tests except this one
"""
# @pytest.mark.my_mark
# def test_with_marker():
#     assert True
