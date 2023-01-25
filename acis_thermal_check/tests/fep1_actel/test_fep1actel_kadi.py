import pytest

from acis_thermal_check.apps.fep1_actel_check import FEP1ActelCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, all_loads


@pytest.fixture(autouse=True, scope="module")
def fa_rt(test_root):
    # kadi state builder tests
    rt = RegressionTester(FEP1ActelCheck, test_root=test_root, sub_dir="kadi")
    rt.run_models(state_builder="kadi")
    return rt


# Prediction tests


@pytest.mark.parametrize("load", all_loads)
def test_prediction(fa_rt, answer_store, load):
    if not answer_store:
        fa_rt.run_test("prediction", load)
    else:
        pass


# Validation tests


@pytest.mark.parametrize("load", all_loads)
def test_validation(fa_rt, answer_store, load):
    if not answer_store:
        fa_rt.run_test("validation", load)
    else:
        pass
