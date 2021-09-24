from ..psmc_check import PSMCCheck, model_path
from acis_thermal_check.regression_testing import \
    RegressionTester
import os


def test_FEB1020A_viols(answer_store, test_root):
    answer_data = os.path.join(os.path.dirname(__file__), "answers",
                               "FEB1020A_viol.json")
    psmc_rt = RegressionTester(PSMCCheck, model_path, "psmc_test_spec.json",
                               test_root=test_root, sub_dir='viols')
    psmc_rt.check_violation_reporting("FEB1020A", answer_data,
                                      answer_store=answer_store)