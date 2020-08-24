import pytest
import time

def mul(x, y):
    return x * y


@pytest.mark.xray_test_id('DIP-46')
def test_answer():
    time.sleep(2)
    assert mul(2, 2) == 5
