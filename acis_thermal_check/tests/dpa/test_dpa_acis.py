from acis_thermal_check.scripts.dpa_check import DPACheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester, all_loads
import pytest


@pytest.fixture(autouse=True, scope='module')
def dpa_rt(test_root):
    # ACIS state builder tests
    rt = RegressionTester(DPACheck, test_root=test_root, sub_dir='acis')
    rt.run_models(state_builder='acis')
    return rt


# Prediction tests

@pytest.mark.parametrize('load', all_loads)
def test_prediction(dpa_rt, answer_store, load):
    dpa_rt.run_test("prediction", load, answer_store=answer_store)


# Validation tests

@pytest.mark.parametrize('load', all_loads)
def test_validation(dpa_rt, answer_store, load):
    dpa_rt.run_test("validation", load, answer_store=answer_store)
