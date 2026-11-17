from acis_thermal_check.apps.dea_check import DEACheck
from acis_thermal_check.tests.regression_testing import RegressionTester, tests_path


def test_DEC0825A_viols(answer_store, test_root):
    answer_data = tests_path / "dea/answers/DEC0825A_viol.json"
    dea_rt = RegressionTester(DEACheck, test_root=test_root, sub_dir="viols")
    dea_rt.check_violation_reporting("DEC0825A", answer_data, answer_store=answer_store)
