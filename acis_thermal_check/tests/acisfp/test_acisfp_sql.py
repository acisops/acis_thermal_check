from acis_thermal_check.scripts.acisfp_check import ACISFPCheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester, all_loads
import pytest


@pytest.fixture(autouse=True, scope='module')
def fp_rt(test_root):
    # SQL state builder tests
    rt = RegressionTester(ACISFPCheck, test_root=test_root, sub_dir='sql')
    rt.run_models(state_builder='sql')
    return rt

# Prediction tests

@pytest.mark.parametrize('load', all_loads)
def test_prediction(fp_rt, answer_store, load):
    if not answer_store:
        fp_rt.run_test("prediction", load)
    else:
        pass

# Validation tests


@pytest.mark.parametrize('load', all_loads)
def test_validation(fp_rt, answer_store, load):
    if not answer_store:
        fp_rt.run_test("validation", load)
    else:
        pass
