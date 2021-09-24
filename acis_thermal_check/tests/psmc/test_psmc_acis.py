from ..psmc_check import model_path, PSMCCheck
from acis_thermal_check.regression_testing import \
    RegressionTester, all_loads
import pytest


@pytest.fixture(autouse=True, scope='module')
def psmc_rt(test_root):
    # ACIS state builder tests
    rt = RegressionTester(PSMCCheck, model_path, "psmc_test_spec.json",
                          test_root=test_root, sub_dir='acis')
    rt.run_models(state_builder='acis')
    return rt

# Prediction tests

@pytest.mark.parametrize('load', all_loads)
def test_prediction(psmc_rt, answer_store, load):
    psmc_rt.run_test("prediction", load, answer_store=answer_store)

# Validation tests

@pytest.mark.parametrize('load', all_loads)
def test_validation(psmc_rt, answer_store, load):
    psmc_rt.run_test("validation", load, answer_store=answer_store)
