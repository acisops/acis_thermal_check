from acis_thermal_check.scripts.dpa_check import model_path, DPACheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester
import os

model_spec = os.path.join(os.path.dirname(__file__), "dpa_test_spec.json")


def test_JUL3018A_viols(answer_store, test_root):
    answer_data = os.path.join(os.path.dirname(__file__), "answers",
                               "JUL3018A_viol.json")
    dpa_rt = RegressionTester(DPACheck, model_path, model_spec,
                              test_root=test_root, sub_dir='viols')
    dpa_rt.check_violation_reporting("JUL3018A", answer_data,
                                     answer_store=answer_store)