from acis_thermal_check.apps.dpa_check import DPACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_DEC0825A_viols(answer_store, test_root):
    answer_data = tests_path / "dpa/answers/DEC0825A_viol.json"
    dpa_rt = RegressionTester(DPACheck, test_root=test_root, sub_dir="viols")
    dpa_rt.check_violation_reporting("DEC0825A", answer_data, answer_store=answer_store)
