import pytest

from acis_thermal_check.apps.dea_check import DEACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, all_loads


@pytest.fixture(autouse=True, scope="module")
def dea_rt(test_root):
    # ACIS state builder tests
    rt = RegressionTester(DEACheck, test_root=test_root, sub_dir="acis")
    rt.run_models(state_builder="acis")
    return rt


# Prediction tests


@pytest.mark.parametrize("load", all_loads)
def test_prediction(dea_rt, answer_store, load):
    dea_rt.run_test("prediction", load, answer_store=answer_store)


# Validation tests


@pytest.mark.parametrize("load", all_loads)
def test_validation(dea_rt, answer_store, load):
    dea_rt.run_test("validation", load, answer_store=answer_store)
