from acis_thermal_check.scripts.dpa_check import DPACheck
from acis_thermal_check.tests.regression_testing import \
    RegressionTester, tests_path


def test_JUL3018A_viols(answer_store, test_root):
    answer_data = tests_path / "dpa/answers/JUL3018A_viol.json"
    dpa_rt = RegressionTester(DPACheck, test_root=test_root, sub_dir='viols')
    dpa_rt.check_violation_reporting("JUL3018A", answer_data,
                                     answer_store=answer_store)