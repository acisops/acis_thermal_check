from acis_thermal_check.apps.cea_check import CEACheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester, hrc_loads
import pytest


@pytest.fixture(autouse=True, scope='module')
def cea_rt(test_root):
    # kadi state builder tests
    rt = RegressionTester(CEACheck, test_root=test_root, sub_dir='kadi')
    rt.run_models(state_builder='kadi', hrc=True)
    return rt


# Prediction tests

@pytest.mark.parametrize('load', hrc_loads["normal"])
def test_prediction(cea_rt, answer_store, load):
    cea_rt.run_test("prediction", load, answer_store=answer_store)


# Validation tests

@pytest.mark.parametrize('load', hrc_loads["normal"])
def test_validation(cea_rt, answer_store, load):
    cea_rt.run_test("validation", load, answer_store=answer_store)
