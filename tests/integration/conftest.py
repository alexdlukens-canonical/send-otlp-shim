import jubilant
import pytest


@pytest.fixture(scope="module")
def juju():
    with jubilant.temp_model() as juju:
        yield juju
