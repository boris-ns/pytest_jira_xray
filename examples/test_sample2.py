import pytest

def mul(x, y):
    return x * y


@pytest.mark.xray_test_id('DIP-46')
def test_answer():
    assert mul(2, 2) == 4
