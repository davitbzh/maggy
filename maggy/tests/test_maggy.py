import pytest
from maggy.searchspace import Searchspace
from maggy.optimizer import RandomSearch

# this allows using the fixture in all tests in this module
pytestmark = pytest.mark.usefixtures("sc")


def test_nr_executors(sc):

    executor_instances = int(sc._conf.get("spark.executor.instances"))
    expected_number = 2
    assert executor_instances == expected_number


def test_random_search(sc):

    sp = Searchspace(argument_param=("DOUBLE", [1, 5]))

    rs = RandomSearch(5, sp, [])

    exp_result = {"argument_param": "DOUBLE"}

    assert sp.names() == exp_result
    assert rs.num_trials == 5
    assert rs.searchspace == sp
