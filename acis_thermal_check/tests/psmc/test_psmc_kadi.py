import pytest

from acis_thermal_check.apps.psmc_check import PSMCCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, all_loads


@pytest.fixture(autouse=True, scope="module")
def psmc_rt(test_root):
    # kadi state builder tests
    rt = RegressionTester(PSMCCheck, test_root=test_root, sub_dir="kadi")
    return rt


# Prediction tests


@pytest.mark.parametrize("load", all_loads)
def test_prediction(psmc_rt, answer_store, load):
    psmc_rt.run_test("prediction", load, "kadi", answer_store=answer_store)


# Validation tests


@pytest.mark.parametrize("load", all_loads)
def test_validation(psmc_rt, answer_store, load):
    psmc_rt.run_test("validation", load, "kadi", answer_store=answer_store)
