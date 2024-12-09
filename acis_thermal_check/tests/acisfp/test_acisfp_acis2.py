import pytest

from acis_thermal_check.apps.acisfp_check import ACISFPCheck
from acis_thermal_check.tests.regression_testing import RegressionTester, hrc_loads


@pytest.fixture(autouse=True, scope="module")
def fp_rt(test_root):
    # ACIS state builder tests
    rt = RegressionTester(
        ACISFPCheck,
        test_root=test_root,
        sub_dir="acis",
        model_spec="acisfp_test_spec2.json",
    )
    rt.run_models(state_builder="acis", hrc=True)
    return rt


# Prediction tests


@pytest.mark.parametrize("load", hrc_loads["normal"])
def test_prediction(fp_rt, answer_store, load):
    fp_rt.run_test("prediction", load, answer_store=answer_store)


# Validation tests


@pytest.mark.parametrize("load", hrc_loads["normal"])
def test_validation(fp_rt, answer_store, load):
    fp_rt.run_test("validation", load, answer_store=answer_store)
