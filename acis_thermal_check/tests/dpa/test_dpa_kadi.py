import pytest

from acis_thermal_check.apps.dpa_check import DPACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, all_loads


@pytest.fixture(autouse=True, scope="module")
def dpa_rt(test_root):
    # kadi state builder tests
    rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="kadi")
    rt.run_models(state_builder="kadi")
    return rt


# Prediction tests


@pytest.mark.parametrize("load", all_loads)
def test_prediction(dpa_rt, answer_store, load):
    if not answer_store:
        dpa_rt.run_test("prediction", load)
    else:
        pass


# Validation tests


@pytest.mark.parametrize("load", all_loads)
def test_validation(dpa_rt, answer_store, load):
    if not answer_store:
        dpa_rt.run_test("validation", load)
    else:
        pass
